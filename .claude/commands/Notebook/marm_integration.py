#!/usr/bin/env python3
"""
MARM Integration Module for Claude Code
Provides core integration between Claude Code session management and MARM notebook system.
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

# Add tools directory to path for MARM import
# Get absolute path to project root (go up from .claude/commands/Notebook/)
current_dir = os.path.dirname(os.path.abspath(__file__))  # .claude/commands/Notebook/
commands_dir = os.path.dirname(current_dir)              # .claude/commands/
claude_dir = os.path.dirname(commands_dir)               # .claude/
project_root = os.path.dirname(claude_dir)               # project root
tools_path = os.path.join(project_root, 'tools', 'Notebook-Context-Management')

MARM_AVAILABLE = False
try:
    # Direct import from the tools directory
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "implementation", 
        os.path.join(tools_path, "implementation.py")
    )
    implementation = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(implementation)
    
    # Extract required functions and variables
    create_file_storage = implementation.create_file_storage
    set_storage_adapter = implementation.set_storage_adapter
    set_persistence_enabled = implementation.set_persistence_enabled
    set_config = implementation.set_config
    ensure_session = implementation.ensure_session
    get_session_context = implementation.get_session_context
    manage_user_notebook = implementation.manage_user_notebook
    add_notebook_entry = implementation.add_notebook_entry
    get_session_stats = implementation.get_session_stats
    sessions = implementation.sessions
    
    MARM_AVAILABLE = True
except Exception as e:
    print(f"Warning: MARM system not available: {e}")
    MARM_AVAILABLE = False

class MarmIntegration:
    """Core MARM integration for Claude Code sessions."""
    
    def __init__(self):
        self.initialized = False
        self.current_session_id = None
        self._setup_storage()
    
    def _setup_storage(self):
        """Initialize MARM storage with Claude Code directory structure."""
        if not MARM_AVAILABLE:
            return
        
        try:
            # Ensure .claude/sessions directory exists
            sessions_dir = Path('.claude/sessions')
            sessions_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize FileStorage
            storage_path = sessions_dir / 'notebook-storage.json'
            file_storage = create_file_storage(str(storage_path))
            set_storage_adapter(file_storage)
            set_persistence_enabled(True)
            
            # Configure for Claude Code environment
            set_config('no_emoji_mode', True)  # Clean terminal output
            set_config('debug_logging', False)  # Quiet by default
            set_config('compact_mode_enabled', False)  # Full context initially
            
            self.initialized = True
            print(f"MARM storage initialized: {storage_path}")
            
        except Exception as e:
            print(f"Warning: Failed to initialize MARM storage: {e}")
            self.initialized = False
    
    def claude_to_marm_session_id(self, claude_session_file: str) -> str:
        """Convert Claude session filename to MARM session ID."""
        # claude_session_file: "2025-08-05-1234-integration.md"
        # marm_session_id: "claude-2025-08-05-1234-integration"
        base_name = claude_session_file.replace('.md', '')
        return f"claude-{base_name}"
    
    def get_current_session_id(self) -> Optional[str]:
        """Get current MARM session ID from .current-session file."""
        try:
            current_session_file = Path('.claude/sessions/.current-session')
            if current_session_file.exists():
                claude_filename = current_session_file.read_text().strip()
                if claude_filename:
                    return self.claude_to_marm_session_id(claude_filename)
        except Exception as e:
            print(f"Warning: Failed to read current session: {e}")
        return None
    
    def start_session(self, claude_session_filename: str) -> bool:
        """Initialize MARM session for new Claude session."""
        if not self.initialized:
            return False
        
        try:
            session_id = self.claude_to_marm_session_id(claude_session_filename)
            self.current_session_id = session_id
            
            # Create MARM session
            ensure_session(session_id)
            
            # Auto-log session start
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            session_name = claude_session_filename.replace('.md', '')
            result = add_notebook_entry(
                session_id, 
                'session-start', 
                f'Started {session_name} at {timestamp}'
            )
            
            print(f"MARM session started: {session_id}")
            return True
            
        except Exception as e:
            print(f"Warning: Failed to start MARM session: {e}")
            return False
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information including MARM data."""
        if not self.initialized:
            return {'marm_available': False}
        
        session_id = self.get_current_session_id()
        if not session_id:
            return {'marm_available': True, 'active_session': False}
        
        try:
            stats = get_session_stats(session_id)
            session_data = sessions.get(session_id, {})
            notebook = session_data.get('notebook', {})
            
            # Get recent notebook entries (last 3)
            recent_entries = []
            for key, value in list(notebook.items())[-3:]:
                recent_entries.append(f"- {key}: {value}")
            
            return {
                'marm_available': True,
                'active_session': True,
                'session_id': session_id,
                'notebook_count': stats.get('notebook_count', 0),
                'notebook_size': stats.get('notebook_size_bytes', 0),
                'recent_entries': recent_entries,
                'stats': stats
            }
            
        except Exception as e:
            print(f"Warning: Failed to get session info: {e}")
            return {'marm_available': True, 'error': str(e)}
    
    def end_session(self) -> Optional[str]:
        """Compile final context and prepare session summary."""
        if not self.initialized:
            return None
        
        session_id = self.get_current_session_id()
        if not session_id:
            return None
        
        try:
            # Compile final context
            final_context = get_session_context(session_id, compact_mode=False)
            
            # Auto-log session end
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            session_data = sessions.get(session_id, {})
            notebook_count = len(session_data.get('notebook', {}))
            
            add_notebook_entry(
                session_id,
                'session-end',
                f'Session ended at {timestamp} - {notebook_count} notebook entries'
            )
            
            return final_context
            
        except Exception as e:
            print(f"Warning: Failed to end MARM session: {e}")
            return None
    
    def notebook_command(self, command: str) -> str:
        """Handle /notebook commands."""
        if not self.initialized:
            return "MARM notebook system not available"
        
        session_id = self.get_current_session_id()
        if not session_id:
            return "No active session. Start a session first with /session-start"
        
        try:
            action, key, value = self._parse_notebook_command(command)
            return manage_user_notebook(session_id, action, key, value)
        except Exception as e:
            return f"Error: {e}"
    
    def _parse_notebook_command(self, command: str) -> Tuple[str, str, str]:
        """Parse /notebook command syntax."""
        if not command.startswith('/notebook '):
            return ('help', '', '')
        
        cmd_part = command[10:]  # Remove '/notebook '
        
        if cmd_part == 'show:':
            return ('show', '', '')
        elif cmd_part.startswith('add:'):
            # Split on first space after colon
            parts = cmd_part[4:].split(' ', 1)
            key = parts[0] if parts else ''
            value = parts[1] if len(parts) > 1 else ''
            return ('add', key, value)
        elif cmd_part.startswith('get:'):
            key = cmd_part[4:]
            return ('get', key, '')
        elif cmd_part.startswith('delete:'):
            key = cmd_part[7:]
            return ('delete', key, '')
        
        return ('help', '', '')
    
    def auto_log_workflow_stage(self, stage: str, summary: str, details: str = "") -> bool:
        """Auto-log workflow stages to current session notebook."""
        if not self.initialized:
            return False
        
        session_id = self.get_current_session_id()
        if not session_id:
            return False
        
        try:
            key = f"{stage.lower()}-{datetime.now().strftime('%m%d')}"
            value = summary
            if details:
                value += f" - {details}"
            
            # Use direct add (no rate limiting for auto-logging)
            result = add_notebook_entry(session_id, key, value)
            print(f"Auto-logged: {result}")
            return True
            
        except Exception as e:
            print(f"Warning: Auto-logging failed: {e}")
            return False
    
    def get_enhanced_context(self, include_existing: bool = True) -> str:
        """Generate enhanced context combining existing + MARM."""
        context_parts = []
        
        # Existing context from current-session-context.md
        if include_existing:
            try:
                existing_context_file = Path('.claude/memory/current-session-context.md')
                if existing_context_file.exists():
                    existing_context = existing_context_file.read_text()
                    context_parts.append("# Existing Project Context")
                    context_parts.append(existing_context)
            except Exception as e:
                print(f"Warning: Failed to read existing context: {e}")
        
        # MARM session context if available
        if self.initialized:
            session_id = self.get_current_session_id()
            if session_id:
                try:
                    marm_context = get_session_context(session_id, compact_mode=False)
                    context_parts.append("# Session Memory Context")
                    context_parts.append(marm_context)
                except Exception as e:
                    print(f"Warning: Failed to compile MARM context: {e}")
        
        return "\n\n".join(context_parts)

# Global integration instance
marm = MarmIntegration()

def get_marm_integration() -> MarmIntegration:
    """Get the global MARM integration instance."""
    return marm

if __name__ == "__main__":
    # Test the integration
    print("Testing MARM Integration...")
    
    # Test storage initialization
    if marm.initialized:
        print("✓ MARM storage initialized")
    else:
        print("✗ MARM storage failed to initialize")
    
    # Test session ID mapping
    test_filename = "2025-08-05-1234-test.md"
    test_id = marm.claude_to_marm_session_id(test_filename)
    expected_id = "claude-2025-08-05-1234-test"
    if test_id == expected_id:
        print(f"✓ Session ID mapping: {test_filename} → {test_id}")
    else:
        print(f"✗ Session ID mapping failed: expected {expected_id}, got {test_id}")
    
    # Test notebook command parsing
    test_commands = [
        "/notebook show:",
        "/notebook add:test-key test value here",
        "/notebook get:test-key",
        "/notebook delete:test-key"
    ]
    
    for cmd in test_commands:
        action, key, value = marm._parse_notebook_command(cmd)
        print(f"✓ Command parsing: {cmd} → ({action}, {key}, {value})")
    
    print("Integration test complete.")