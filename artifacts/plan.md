# Implementation Plan - MARM Notebook Integration

## Architecture Overview

### Component Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code Session Layer                │
├─────────────────────────────────────────────────────────────┤
│  session-start.md  │  session-current.md  │  session-end.md │
│       ↓                    ↓                     ↓         │
├─────────────────────────────────────────────────────────────┤
│              MARM Integration Wrapper                      │
│  • Session ID mapping     • Context compilation            │
│  • FileStorage setup      • Auto-logging coordination      │
├─────────────────────────────────────────────────────────────┤
│                   MARM Core System                         │
│  • Session management     • Notebook operations            │
│  • Context compilation    • Storage abstraction            │
├─────────────────────────────────────────────────────────────┤
│                   Storage Layer                            │
│  FileStorage(.claude/sessions/notebook-storage.json)       │
└─────────────────────────────────────────────────────────────┘
```

### Integration Strategy: Enhancement Pattern
- **Preserve:** All existing Claude Code functionality works unchanged
- **Extend:** Add MARM capabilities to existing commands
- **Add:** New `/notebook` commands for direct management
- **Integrate:** Auto-logging with workflow-comprehensive stages

## Detailed Design

### 1. Session ID Mapping Strategy
```python
def claude_to_marm_session_id(claude_session_file: str) -> str:
    """Convert Claude session filename to MARM session ID"""
    # claude_session_file: "2025-08-05-1234-integration.md"
    # marm_session_id: "claude-2025-08-05-1234-integration"
    base_name = claude_session_file.replace('.md', '')
    return f"claude-{base_name}"

def get_current_session_id() -> Optional[str]:
    """Get current MARM session ID from .current-session file"""
    current_file = read_file('.claude/sessions/.current-session')
    if current_file:
        return claude_to_marm_session_id(current_file.strip())
    return None
```

### 2. Storage Integration Design
```python
def initialize_marm_storage():
    """Initialize MARM with FileStorage pointing to Claude sessions"""
    storage_path = '.claude/sessions/notebook-storage.json'
    file_storage = create_file_storage(storage_path)
    set_storage_adapter(file_storage)
    set_persistence_enabled(True)
    
    # Configure for Claude Code environment
    set_config('no_emoji_mode', True)  # Clean terminal output
    set_config('debug_logging', False)  # Quiet by default
    set_config('compact_mode_enabled', False)  # Full context initially
```

### 3. Command Extension Architecture

#### session-start.md Enhancement
```markdown
# Enhanced Session Start Process

## Existing Functionality (Preserved)
1. Create session file: `.claude/sessions/YYYY-MM-DD-HHMM-[name].md`
2. Update `.current-session` with filename
3. Initialize session structure

## MARM Integration (Added)
4. Initialize MARM storage if not already done
5. Derive MARM session ID from filename
6. Create MARM session: `ensure_session(session_id)`
7. Auto-log session start: `/notebook add:session-start "Started [session-name] at [timestamp]"`
8. Display enhanced session info including notebook status
```

#### session-current.md Enhancement
```markdown
# Enhanced Session Current Display

## Standard Session Info (Preserved)
- Session name and duration
- Current goals and tasks
- Last updates

## MARM Integration (Added)
- Notebook entry count and usage statistics
- Recent notebook entries (last 3)
- Context compilation summary
- Available notebook commands

## Display Format
```
Current Session: integration-2025-08-05-1234
Duration: 2 hours 15 minutes
MARM Session ID: claude-2025-08-05-1234-integration

📊 Notebook: 5/30 entries, 2,147/30,000 chars

Recent Notebook Entries:
- session-start: Started integration session
- express-complete: 4W1H captured for notebook integration  
- explore-findings: Key integration points identified

Available Commands:
- /notebook show: - List all entries
- /notebook add:[key] [value] - Add new entry
```
```

#### session-end.md Enhancement
```markdown
# Enhanced Session End Process

## Standard Session Summary (Preserved)
- Duration, git summary, todo summary
- Accomplishments, problems, lessons learned

## MARM Integration (Added)
- Compile final session context
- Auto-log session summary to notebook
- Display notebook statistics and key entries
- Persist all session data
- Option to export notebook entries to session file
```

### 4. New Notebook Commands Design

#### /notebook Command Parser
```python
def parse_notebook_command(command: str) -> Tuple[str, str, str]:
    """Parse /notebook command syntax"""
    # /notebook show:
    # /notebook add:key-name value content here
    # /notebook get:key-name  
    # /notebook delete:key-name
    
    if command.startswith('/notebook '):
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
```

### 5. Workflow Auto-Logging Integration

#### Auto-Logging Hook Points
```python
def auto_log_workflow_stage(stage: str, summary: str, details: str = ""):
    """Auto-log workflow stages to current session notebook"""
    session_id = get_current_session_id()
    if not session_id:
        return  # No active session
    
    key = f"{stage.lower()}-{datetime.now().strftime('%m%d')}"
    value = f"{summary}"
    if details:
        value += f" - {details}"
    
    # Use direct add (no rate limiting for auto-logging)
    result = add_notebook_entry(session_id, key, value)
    if debug_logging_enabled():
        print(f"Auto-logged: {result}")

# Integration points:
# workflow-comprehensive Express stage → auto_log_workflow_stage('Express', '4W1H captured', scope_summary)
# workflow-comprehensive Ask stage → auto_log_workflow_stage('Ask', 'Assumptions validated', feedback_summary)  
# workflow-comprehensive Explore stage → auto_log_workflow_stage('Explore', 'Context analysis complete', key_findings)
# workflow-comprehensive Plan stage → auto_log_workflow_stage('Plan', 'Architecture designed', key_decisions)
```

### 6. Context Compilation Integration

#### Enhanced Context Generation
```python
def get_enhanced_session_context(include_marm: bool = True) -> str:
    """Generate enhanced context combining existing + MARM"""
    context_parts = []
    
    # Existing context from current-session-context.md
    existing_context = read_file('.claude/memory/current-session-context.md')
    if existing_context:
        context_parts.append("# Existing Project Context")
        context_parts.append(existing_context)
    
    # MARM session context if available and requested
    if include_marm:
        session_id = get_current_session_id()
        if session_id:
            marm_context = get_session_context(session_id, compact_mode=False)
            context_parts.append("# Session Memory Context")
            context_parts.append(marm_context)
    
    return "\n\n".join(context_parts)
```

## Implementation Sequence

### Phase 1: Core Integration (Week 1)
1. **Storage Setup** 
   - Initialize FileStorage integration
   - Create storage directory and permissions
   - Test basic MARM session operations

2. **Session ID Mapping**
   - Implement Claude-to-MARM session ID conversion
   - Update .current-session tracking
   - Test session lifecycle integration

3. **Basic Command Extensions**
   - Extend session-start with MARM initialization
   - Extend session-current with notebook display
   - Test backward compatibility

### Phase 2: Command Interface (Week 2)  
1. **Notebook Commands**
   - Implement /notebook command parser
   - Add show/add/get/delete operations
   - Integrate with existing command patterns

2. **Session End Enhancement**
   - Add context compilation to session-end
   - Implement session summary auto-logging
   - Test data persistence

3. **Error Handling**
   - Add graceful fallbacks for MARM failures
   - Implement clear error messages
   - Test failure scenarios

### Phase 3: Workflow Integration (Week 3)
1. **Auto-Logging System**
   - Implement workflow stage detection
   - Add auto-logging hook points
   - Test workflow-comprehensive integration

2. **Context Compilation**
   - Integrate MARM context with existing memory
   - Implement enhanced context generation
   - Test context quality and performance

3. **Configuration System**
   - Add user configuration options
   - Implement runtime configuration management
   - Test configuration persistence

### Phase 4: Polish and Testing (Week 4)
1. **Performance Optimization**
   - Profile and optimize file operations
   - Implement caching where beneficial
   - Test performance under load

2. **Documentation and Help**
   - Create user documentation
   - Integrate help with existing system
   - Test user experience flows

3. **Comprehensive Testing**
   - Integration testing across all components
   - Backward compatibility validation
   - User acceptance testing

## Data Schema Design

### MARM Session Structure
```json
{
  "claude-2025-08-05-1234-integration": {
    "history": [
      {"role": "user", "content": "Start integration work"},
      {"role": "assistant", "content": "Beginning MARM integration..."}
    ],
    "logs": [
      "2025-08-05 - Session started - Integration work begins",
      "2025-08-05 - Express complete - 4W1H captured"
    ],
    "notebook": {
      "session-start": "Started integration session at 2025-08-05 12:34",
      "express-complete": "4W1H captured for notebook integration",
      "key-findings": "Enhancement pattern preserves existing functionality"
    },
    "lastReasoning": "",
    "created": 1722855600000
  }
}
```

### File System Layout
```
.claude/
├── sessions/
│   ├── .current-session                    # "2025-08-05-1234-integration.md"
│   ├── 2025-08-05-1234-integration.md     # Standard session file
│   ├── notebook-storage.json              # MARM persistent storage
│   └── notebook-storage.json.backup       # Automatic backup
├── memory/
│   └── current-session-context.md         # Existing context (preserved)
└── commands/
    ├── session-*.md                        # Enhanced commands
    └── notebook-*.md                       # New notebook commands
```

## Key Design Decisions

### Decision 1: Enhancement vs Replacement Pattern
**Chosen:** Enhancement Pattern
**Rationale:** Preserves existing functionality, reduces risk, enables gradual adoption
**Trade-offs:** More complex integration, potential duplication
**Alternatives Considered:** Complete replacement (too risky), parallel systems (confusing)

### Decision 2: Storage Location and Format  
**Chosen:** Single JSON file in `.claude/sessions/`
**Rationale:** Consistent with existing session directory, atomic operations, easy inspection
**Trade-offs:** Single file bottleneck, JSON size limits
**Alternatives Considered:** Multiple files (complexity), database (overkill), existing session files (format conflicts)

### Decision 3: Session ID Mapping Strategy
**Chosen:** Derive MARM ID from Claude session filename
**Rationale:** Maintains clear relationship, enables session correlation, simple implementation
**Trade-offs:** Filename dependencies, character limitations
**Alternatives Considered:** UUID generation (no correlation), timestamp-based (collision risk)

### Decision 4: Auto-Logging Approach
**Chosen:** Configurable auto-logging at workflow stage boundaries
**Rationale:** Provides value without overwhelming users, maintains workflow continuity
**Trade-offs:** Additional complexity, potential noise
**Alternatives Considered:** Manual only (less value), everything (too noisy), AI-driven (too complex)

### Decision 5: Context Compilation Strategy
**Chosen:** Hybrid approach combining existing context + MARM context
**Rationale:** Best of both worlds, preserves existing patterns, enhances with structured data
**Trade-offs:** Potential context size growth, complexity
**Alternatives Considered:** MARM only (loses existing), existing only (no benefit), separate (confusing)

## Risk Mitigation in Design

### High-Risk Areas Addressed
1. **Backward Compatibility:** All existing commands work unchanged, MARM features are additive
2. **Data Integrity:** Atomic file operations, validation, backup rotation
3. **Performance:** Lazy loading, efficient serialization, configurable features
4. **Complexity:** Clear separation of concerns, gradual feature introduction

### Failure Handling Design
1. **MARM Unavailable:** Commands fall back to existing behavior
2. **Storage Failures:** Graceful degradation to memory-only mode  
3. **Corruption Recovery:** Validation with backup restoration
4. **Concurrency Issues:** File locking with timeout handling

## Success Metrics and Validation

### Technical Metrics
- Session startup time impact < 100ms
- Notebook operations complete < 50ms
- Zero data loss incidents in testing
- 100% backward compatibility maintained

### User Experience Metrics  
- Feature discoverability through help system
- Error message clarity and actionability
- Workflow integration smoothness
- Configuration flexibility and ease

### Integration Metrics
- Claude Code command compatibility
- Workflow-comprehensive stage integration
- Context compilation accuracy
- File system integration reliability