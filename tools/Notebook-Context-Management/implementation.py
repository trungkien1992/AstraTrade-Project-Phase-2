import json
import re
import threading
import time
import logging
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass

# ===== STORAGE ABSTRACTION =====
class Storage(ABC):
    """Abstract storage interface for different persistence backends."""
    
    @abstractmethod
    def get_item(self, key: str) -> Optional[str]:
        pass
    
    @abstractmethod
    def set_item(self, key: str, value: str) -> None:
        pass
    
    @abstractmethod
    def remove_item(self, key: str) -> None:
        pass


class MemoryStorage(Storage):
    """In-memory storage implementation."""
    
    def __init__(self):
        self._store: Dict[str, str] = {}
        self._lock = threading.Lock()

    def get_item(self, key: str) -> Optional[str]:
        with self._lock:
            return self._store.get(key)

    def set_item(self, key: str, value: str) -> None:
        with self._lock:
            self._store[key] = value

    def remove_item(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)


class FileStorage(Storage):
    """File-based storage implementation."""
    
    def __init__(self, file_path: str):
        import os
        self.file_path = file_path
        self._lock = threading.Lock()
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        # Load existing data
        self._store = self._load_from_file()
    
    def _load_from_file(self) -> Dict[str, str]:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_to_file(self) -> None:
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self._store, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.warning(f"Failed to save to file: {e}")
    
    def get_item(self, key: str) -> Optional[str]:
        with self._lock:
            return self._store.get(key)
    
    def set_item(self, key: str, value: str) -> None:
        with self._lock:
            self._store[key] = value
            self._save_to_file()
    
    def remove_item(self, key: str) -> None:
        with self._lock:
            if key in self._store:
                del self._store[key]
                self._save_to_file()


# Global storage instance - can be replaced with custom implementation
storage: Storage = MemoryStorage()
_persistence_enabled = True


def set_storage_adapter(adapter: Storage) -> None:
    """Set custom storage adapter."""
    global storage
    storage = adapter


def set_persistence_enabled(enabled: bool) -> None:
    """Toggle persistence on/off."""
    global _persistence_enabled
    _persistence_enabled = enabled

# ===== UTILITY FUNCTIONS =====
def debounce(fn: Callable, delay_ms: int) -> Callable:
    """
    Returns a debounced version of fn. If called repeatedly, only the last call
    after 'delay_ms' will execute. Thread-safe enough for simple use.
    """
    lock = threading.Lock()
    timer: Dict[str, Optional[threading.Timer]] = {"t": None}

    def debounced(*args, **kwargs):
        def call():
            fn(*args, **kwargs)
        with lock:
            if timer["t"]:
                timer["t"].cancel()
            t = threading.Timer(delay_ms / 1000.0, call)
            timer["t"] = t
            t.start()
    return debounced


def strip_html(input_str: str) -> str:
    """Strip HTML tags from input string."""
    if input_str is None:
        return ""
    return re.sub(r"<[^>]*>?", "", input_str)


def validate_notebook_entry(key: str, value: str) -> bool:
    """Validate notebook entry with configurable Unicode support."""
    if not key or not isinstance(key, str) or len(key) > 64:
        return False
    
    # Use Unicode keys if enabled, otherwise ASCII-only due to \w limitations
    if _config["enable_unicode_keys"]:
        # Allow Unicode letters, digits, dash, space
        if not re.match(r"^[\w\-\s]+$", key, re.UNICODE):
            return False
    else:
        # ASCII-only pattern (documented limitation)
        if not re.match(r"^[\w\- ]+$", key):
            return False
    
    if not value or not isinstance(value, str) or len(value) > MAX_ENTRY_SIZE:
        return False
    
    return True


def validate_log_entry(entry: str) -> bool:
    """Validate log entry format: [Date-Summary-Result]."""
    if not entry or not isinstance(entry, str):
        return False
    return re.search(r"^\s*\d{4}-\d{2}-\d{2}\s*[|-]\s*.+?\s*[|-]\s*.+\s*$", entry) is not None


def estimate_tokens(s: str) -> int:
    """Estimate token count using rough 3.5 chars per token heuristic."""
    if s is None:
        s = ""
    return int((len(s) + 3.5 - 1) // 3.5)  # ceil(len/3.5)


# ===== SESSION MANAGEMENT =====
sessions: Dict[str, Dict[str, Any]] = {}
LS_KEY = "marm-sessions-v1"
CURRENT_SESSION_KEY = "marm-current-session"
MAX_SESSIONS = 50
SESSION_EXPIRY_DAYS = 30
MAX_SESSION_SIZE = 35000
PRUNING_THRESHOLD = 5000
MAX_ENTRY_SIZE = 2048  # Explicitly defined constant

# Concurrency guard for all session mutations
_sessions_mutex = threading.RLock()  # Use RLock to allow re-entrant calls

# Configuration flags
_config = {
    "compact_mode_enabled": False,
    "max_notebook_chars_compact": 100,
    "max_conversation_tokens_compact": 1000,
    "enable_unicode_keys": False,
    "no_emoji_mode": False,
    "debug_logging": False
}


def set_config(key: str, value: Any) -> None:
    """Update configuration setting."""
    if key in _config:
        _config[key] = value


def get_config(key: str) -> Any:
    """Get configuration setting."""
    return _config.get(key)

def _now_ms() -> int:
    return int(time.time() * 1000)


def ensure_session(session_id: str) -> Dict[str, Any]:
    """Thread-safe session creation/retrieval with concurrency guard."""
    with _sessions_mutex:
        if session_id not in sessions:
            sessions[session_id] = {
                "history": [],           # List[Dict[str, str]] with {'role','content'}
                "logs": [],              # List[str]
                "notebook": {},          # Dict[str, str]
                "lastReasoning": "",
                "created": _now_ms(),
            }
        return sessions[session_id]


def prune_old_sessions() -> None:
    """Thread-safe pruning of expired and excess sessions."""
    with _sessions_mutex:
        now = _now_ms()
        expired_ms = SESSION_EXPIRY_DAYS * 86400000
        to_delete = []
        for sid, s in sessions.items():
            created = s.get("created")
            if created and (now - created) > expired_ms:
                to_delete.append(sid)
        
        pruned_count = len(to_delete)
        for sid in to_delete:
            del sessions[sid]
            if _config["debug_logging"]:
                logging.debug(f"Pruned expired session: {sid}")

        remaining_ids = list(sessions.keys())
        if len(remaining_ids) > MAX_SESSIONS:
            remaining_ids.sort(key=lambda sid: sessions[sid].get("created", 0))
            excess_sessions = remaining_ids[:len(remaining_ids) - MAX_SESSIONS]
            for sid in excess_sessions:
                del sessions[sid]
                if _config["debug_logging"]:
                    logging.debug(f"Pruned excess session: {sid}")
            pruned_count += len(excess_sessions)
        
        if _config["debug_logging"] and pruned_count > 0:
            logging.debug(f"Total sessions pruned: {pruned_count}")


def _total_size_for_trim(s: Dict[str, Any]) -> int:
    # Matches JS behavior: only history + logs considered for size trimming
    history_sz = len(json.dumps(s.get("history", []), ensure_ascii=False))
    logs_sz = len(json.dumps(s.get("logs", []), ensure_ascii=False))
    return history_sz + logs_sz


def trim_session_size(s: Dict[str, Any]) -> None:
    """Trim session with improved observability and oscillation prevention."""
    initial_total = _total_size_for_trim(s)
    total = initial_total
    
    initial_history_count = len(s.get("history", []))
    initial_logs_count = len(s.get("logs", []))
    
    # Trim history first (less aggressive threshold)
    trimmed_history = 0
    while total > PRUNING_THRESHOLD and len(s.get("history", [])) > 0:
        old_total = total
        s["history"].pop(0)
        trimmed_history += 1
        total = _total_size_for_trim(s)
        
        # Prevent oscillation if single entry is very large
        if old_total == total:
            if _config["debug_logging"]:
                logging.warning("Large history entry detected during trimming")
            break
    
    # Trim logs if still over max size
    trimmed_logs = 0
    while total > MAX_SESSION_SIZE and len(s.get("logs", [])) > 0:
        old_total = total
        s["logs"].pop(0)
        trimmed_logs += 1
        total = _total_size_for_trim(s)
        
        # Prevent oscillation if single entry is very large
        if old_total == total:
            if _config["debug_logging"]:
                logging.warning("Large log entry detected during trimming")
            break
    
    # Log trimming activity if debug enabled
    if _config["debug_logging"] and (trimmed_history > 0 or trimmed_logs > 0):
        logging.debug(f"Session trimmed: {initial_total} -> {total} bytes, "
                     f"history: {initial_history_count} -> {len(s.get('history', []))}, "
                     f"logs: {initial_logs_count} -> {len(s.get('logs', []))}")


def persist_sessions() -> None:
    """Thread-safe session persistence with improved error handling."""
    with _sessions_mutex:
        prune_old_sessions()
        if _persistence_enabled:
            try:
                storage.set_item(LS_KEY, json.dumps(sessions, ensure_ascii=False))
            except Exception as e:
                if _config["debug_logging"]:
                    logging.warning(f"Failed to persist sessions: {e}")
        else:
            if _config["debug_logging"]:
                logging.debug("Persistence disabled, skipping session save")


def persist_current_session(current_id: str) -> None:
    """Store only the current session ID, not the entire sessions object."""
    if _persistence_enabled:
        try:
            # Store just the session ID as a simple string (no JSON wrapper needed)
            storage.set_item(CURRENT_SESSION_KEY, current_id)
        except Exception as e:
            if _config["debug_logging"]:
                logging.warning(f"Failed to persist current session: {e}")
    else:
        if _config["debug_logging"]:
            logging.debug("Persistence disabled, skipping current session save")


def _validate_session_data(data: Any) -> bool:
    """Validate session data structure to prevent corruption."""
    if not isinstance(data, dict):
        return False
    
    for session_id, session_data in data.items():
        if not isinstance(session_id, str) or not isinstance(session_data, dict):
            return False
        
        # Validate required session fields
        required_fields = ["history", "logs", "notebook", "created"]
        for field in required_fields:
            if field not in session_data:
                return False
        
        # Validate field types
        if not isinstance(session_data["history"], list):
            return False
        if not isinstance(session_data["logs"], list):
            return False
        if not isinstance(session_data["notebook"], dict):
            return False
        if not isinstance(session_data["created"], (int, float)):
            return False
    
    return True


def restore_sessions() -> Optional[str]:
    """Restore sessions with validation and merge precedence (in-memory > persisted)."""
    global sessions
    current_session_id = None
    
    with _sessions_mutex:
        # Restore current session ID
        try:
            current_raw = storage.get_item(CURRENT_SESSION_KEY)
            if current_raw:
                # Current session ID is stored as plain string now
                current_session_id = current_raw
        except Exception as e:
            if _config["debug_logging"]:
                logging.warning(f"Failed to restore current session ID: {e}")

        # Restore full sessions if persistence enabled
        if _persistence_enabled:
            try:
                saved_raw = storage.get_item(LS_KEY)
                if saved_raw:
                    saved_sessions = json.loads(saved_raw)
                    
                    # Validate loaded data
                    if not _validate_session_data(saved_sessions):
                        if _config["debug_logging"]:
                            logging.warning("Invalid session data found, discarding malformed records")
                        return current_session_id
                    
                    # Merge with precedence: in-memory > persisted
                    # This preserves any sessions already in memory
                    merged_sessions = {**saved_sessions, **sessions}
                    sessions = merged_sessions
                    
                    if _config["debug_logging"]:
                        logging.debug(f"Restored {len(saved_sessions)} sessions from storage")
                        
            except (json.JSONDecodeError, TypeError) as e:
                if _config["debug_logging"]:
                    logging.warning(f"Failed to restore sessions - invalid JSON: {e}")
            except Exception as e:
                if _config["debug_logging"]:
                    logging.warning(f"Failed to restore sessions: {e}")
    
    return current_session_id


# Initialize sessions on module load
_current_session_id = restore_sessions()

# MARM protocol text constants
MARM_PROTOCOL_VERSION = "1.5.0"
MARM_PROTOCOL_TEXT = f"""MEMORY ACCURATE RESPONSE MODE v{MARM_PROTOCOL_VERSION} (MARM)

Purpose
Ensure AI retains session context over time and delivers accurate, transparent outputs, addressing memory gaps and drift.

Your Objective
You are MARM. Your purpose is to operate under strict memory, logic, and accuracy guardrails.

CORE FEATURES:
Session Memory Kernel:
- Tracks user inputs, intent, and session history
- Folder-style organization for logs
- Honest recall if memory fails
- Manual reentry option for controlled re-engagement

Session Relay Tools:
- /compile for summaries with optional filters
- Manual Reseed Option via context block
- Log Schema Enforcement: [Date-Summary-Result]
- Error Handling for invalid logs

Accuracy Guardrails:
- Self-checks for alignment with context
- Optional reasoning trail via /show reasoning

Manual Knowledge Library:
- Build personalized library with /notebook
- Reinforces user control over AI knowledge

Safe Guard Check
Review protocol before responding. Confirm responses align with MARM principles."""
RESPONSE_FORMATTING_RULES = """### Response Formatting Rules

**1. Prioritize Brevity and Clarity:**
- Paragraphs: 2-3 sentences max
- Start new paragraph for each idea
- Crisp, professional, focused responses

**2. Use Basic Markdown:**
- Bullet points (-) for lists
- Bold (**) to highlight key terms
- No headers, blockquotes, or tables

**3. Professional, Conversational Tone:**
- Write like explaining to a colleague
- If reasoning needed: "Here's my reasoning…" but keep it brief

**4. Always Follow These Formatting Rules:**
- Formatting standards remain active in longer sessions"""


def get_session_context(session_id: str, compact_mode: Optional[bool] = None) -> str:
    """Get session context with optional token-aware compact mode.
    
    Args:
        session_id: The session ID to get context for
        compact_mode: Override global compact mode setting
    
    Returns:
        Formatted session context string
    """
    s = sessions.get(session_id)
    if not s:
        return f"MARM v{MARM_PROTOCOL_VERSION}\n\n{MARM_PROTOCOL_TEXT}\n\n{RESPONSE_FORMATTING_RULES}"

    # Determine if compact mode should be used
    use_compact = compact_mode if compact_mode is not None else _config["compact_mode_enabled"]

    context = f"You are operating under MARM v{MARM_PROTOCOL_VERSION} protocol:\n\n{MARM_PROTOCOL_TEXT}\n\n{RESPONSE_FORMATTING_RULES}\n\n"
    context += f"Current Session ID: {session_id}\n\n"

    # Handle notebook contents
    nb = s.get("notebook", {})
    if nb:
        context += "Current Notebook Contents:\n"
        if use_compact:
            # Compact mode: truncate values and show only keys if budget is tight
            max_chars = _config["max_notebook_chars_compact"]
            for k, v in nb.items():
                if len(v) > max_chars:
                    truncated_value = v[:max_chars] + "..."
                    context += f"- {k}: {truncated_value}\n"
                else:
                    context += f"- {k}: {v}\n"
        else:
            # Normal mode: show full values
            for k, v in nb.items():
                context += f"- {k}: {v}\n"
        context += "\n"

    # Handle log entries
    logs = s.get("logs", [])
    if logs:
        context += "Recent Log Entries:\n"
        log_count = 3 if use_compact else 5
        for log in logs[-log_count:]:
            context += f"- {log}\n"
        context += "\n"

    # Handle conversation history with token awareness
    history = s.get("history", [])
    if history:
        if use_compact:
            # Token-aware conversation trimming
            max_tokens = _config["max_conversation_tokens_compact"]
            context += "Recent Conversation:\n"
            
            # Start from most recent and work backwards until token limit
            current_tokens = estimate_tokens(context)
            included_messages = []
            
            for msg in reversed(history):
                msg_content = f"{msg.get('role')}: {msg.get('content')}"
                msg_tokens = estimate_tokens(msg_content)
                
                if current_tokens + msg_tokens > max_tokens:
                    break
                
                included_messages.insert(0, msg_content)
                current_tokens += msg_tokens
            
            # Show truncation indicator if we didn't include all messages
            if len(included_messages) < len(history):
                context += f"[... {len(history) - len(included_messages)} earlier messages truncated for token limit ...]\n"
            
            for msg in included_messages:
                context += f"{msg}\n"
        else:
            # Normal mode: show last 20 messages
            tail_msgs = history[-20:]
            tail = "\n".join(f"{m.get('role')}: {m.get('content')}" for m in tail_msgs)
            if tail:
                context += f"Conversation History:\n{tail}"
    
    return context


# ===== NOTEBOOK FUNCTIONALITY =====
NOTEBOOK_LIMITS = {
    "MAX_ENTRIES": 30,
    "MAX_TOTAL_SIZE": 30000,
    "RATE_LIMIT_MS": 300,
    "MAX_ENTRY_SIZE": 2048,
}

# Rate limiting state with thread safety
_rate_limit_state = {
    "last_notebook_save_ms": 0,
    "lock": threading.Lock()
}

def _add_notebook_entry_internal(session_id: str, key: str, value: str) -> str:
    """Internal notebook entry addition with validation and size checks."""
    s = ensure_session(session_id)
    key = strip_html(key)
    value = strip_html(value)

    if not validate_notebook_entry(key, value):
        return 'Invalid notebook entry. Key must be 1-64 chars (letters, numbers, dash, space). Value must be 1-2048 chars.'

    current_entries = len(s["notebook"])
    if current_entries >= NOTEBOOK_LIMITS["MAX_ENTRIES"]:
        return f"⚠️ Notebook is full ({NOTEBOOK_LIMITS['MAX_ENTRIES']} entries max). Delete some entries first."

    current_size = len(json.dumps(s["notebook"], ensure_ascii=False))
    new_entry_size = len(json.dumps({key: value}, ensure_ascii=False))
    if current_size + new_entry_size > NOTEBOOK_LIMITS["MAX_TOTAL_SIZE"]:
        return f"⚠️ Notebook storage limit reached ({NOTEBOOK_LIMITS['MAX_TOTAL_SIZE']} chars max). Delete some entries first."

    # Validate entry size against MAX_ENTRY_SIZE
    if len(value) > MAX_ENTRY_SIZE:
        return f"⚠️ Entry too large ({len(value)} chars). Max allowed: {MAX_ENTRY_SIZE} chars."

    with _sessions_mutex:
        s["notebook"][key] = value
        trim_session_size(s)
    
    persist_sessions()
    return f'Stored "{key}" → "{value}"'


def _check_rate_limit() -> Optional[str]:
    """Check rate limit and return warning message if too soon, None if OK.
    
    Option A: Explicit rejection with immediate feedback to callers.
    """
    with _rate_limit_state["lock"]:
        now = _now_ms()
        time_since_last = now - _rate_limit_state["last_notebook_save_ms"]
        
        if time_since_last < NOTEBOOK_LIMITS["RATE_LIMIT_MS"]:
            remaining_ms = NOTEBOOK_LIMITS["RATE_LIMIT_MS"] - time_since_last
            return f"⚠️ Rate limit: Please wait {remaining_ms}ms before saving another notebook entry."
        
        # Update timestamp on successful check
        _rate_limit_state["last_notebook_save_ms"] = now
        return None


def _rate_limited_add_entry(session_id: str, key: str, value: str) -> str:
    """Rate-limited notebook entry addition with explicit rejection."""
    rate_limit_msg = _check_rate_limit()
    if rate_limit_msg:
        return rate_limit_msg
    
    return _add_notebook_entry_internal(session_id, key, value)


def add_notebook_entry(session_id: str, key: str, value: str) -> str:
    """Direct add without rate limit (internal use)."""
    return _add_notebook_entry_internal(session_id, key, value)


def get_notebook_entry(session_id: str, key: Optional[str]) -> str:
    """Get a specific notebook entry."""
    s = ensure_session(session_id)
    if not key or not key.strip():
        return "Usage: /notebook key:[name] [data] | /notebook get:[name] | /notebook show:"
    
    key = key.strip()
    value = s["notebook"].get(key)
    return f'"{key}": {value}' if value is not None else f'No entry for "{key}"'


def list_notebook_entries(session_id: str) -> str:
    """List notebook entries with usage statistics."""
    s = ensure_session(session_id)
    keys = list(s["notebook"].keys())
    if not keys:
        return "Notebook is empty."
    
    total_size = len(json.dumps(s["notebook"], ensure_ascii=False))
    
    # Use emoji only if not in no-emoji mode
    emoji = "" if _config["no_emoji_mode"] else "📊 "
    usage = f"{emoji}Usage: {len(keys)}/{NOTEBOOK_LIMITS['MAX_ENTRIES']} entries, {total_size}/{NOTEBOOK_LIMITS['MAX_TOTAL_SIZE']} chars"
    
    entries = "\n".join([f"• {k}: {s['notebook'][k]}" for k in keys])
    return f"{usage}\n\nNotebook entries:\n{entries}"


def delete_notebook_entry(session_id: str, key: Optional[str]) -> str:
    """Delete notebook entry with thread safety."""
    s = ensure_session(session_id)
    if not key or not key.strip():
        return "Usage: /notebook delete:[name]"
    
    key = key.strip()
    
    with _sessions_mutex:
        if key not in s["notebook"]:
            return f'No entry found for "{key}"'
        del s["notebook"][key]
    
    persist_sessions()
    return f'Deleted "{key}" from notebook'


def manage_user_notebook(session_id: str, action: str, key: str = "", value: str = "") -> str:
    """Main notebook management interface with input validation."""
    if not session_id or not isinstance(session_id, str):
        return "Error: Invalid session ID"
    
    action = (action or "").lower().strip()
    
    if action == "add":
        return _rate_limited_add_entry(session_id, key, value)
    elif action == "get":
        return get_notebook_entry(session_id, key)
    elif action in ["all", "show", "list"]:
        return list_notebook_entries(session_id)
    elif action == "delete":
        return delete_notebook_entry(session_id, key)
    else:
        return "Usage: /notebook key:[name] [data] | /notebook get:[name] | /notebook show: | /notebook delete:[name]"


# ===== HELPER FUNCTIONS FOR TESTING AND DEBUGGING =====
def get_session_stats(session_id: str) -> Dict[str, Any]:
    """Get comprehensive session statistics for debugging."""
    s = sessions.get(session_id)
    if not s:
        return {"error": "Session not found"}
    
    history_size = len(json.dumps(s.get("history", []), ensure_ascii=False))
    logs_size = len(json.dumps(s.get("logs", []), ensure_ascii=False))
    notebook_size = len(json.dumps(s.get("notebook", {}), ensure_ascii=False))
    
    return {
        "session_id": session_id,
        "created": s.get("created"),
        "history_count": len(s.get("history", [])),
        "logs_count": len(s.get("logs", [])),
        "notebook_count": len(s.get("notebook", {})),
        "history_size_bytes": history_size,
        "logs_size_bytes": logs_size,
        "notebook_size_bytes": notebook_size,
        "total_size_bytes": history_size + logs_size + notebook_size,
        "trim_threshold_exceeded": _total_size_for_trim(s) > PRUNING_THRESHOLD,
        "max_size_exceeded": _total_size_for_trim(s) > MAX_SESSION_SIZE
    }


def create_file_storage(file_path: str) -> FileStorage:
    """Factory function to create file-based storage."""
    return FileStorage(file_path)


# ===== PUBLIC API =====
__all__ = [
    # Session management
    "sessions",
    "ensure_session",
    "prune_old_sessions",
    "trim_session_size",
    "persist_sessions",
    "persist_current_session",
    "restore_sessions",
    "get_session_context",
    "get_session_stats",

    # Configuration
    "set_config",
    "get_config",
    "set_storage_adapter",
    "set_persistence_enabled",
    "create_file_storage",

    # Notebook functionality
    "manage_user_notebook",
    "add_notebook_entry",
    "get_notebook_entry",
    "list_notebook_entries",
    "delete_notebook_entry",

    # Utility functions
    "debounce",
    "strip_html",
    "validate_notebook_entry",
    "validate_log_entry",
    "estimate_tokens",
    
    # Storage classes
    "Storage",
    "MemoryStorage",
    "FileStorage",
    "storage",
    
    # Constants
    "NOTEBOOK_LIMITS",
    "MAX_ENTRY_SIZE",
    "MARM_PROTOCOL_VERSION",
]