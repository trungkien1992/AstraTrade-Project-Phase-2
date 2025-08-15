End the current development session by:

1. Check `.claude/sessions/.current-session` for the active session
2. If no active session, inform user there's nothing to end
3. If session exists, append a comprehensive summary including:
   - Session duration
   - Git summary:
     * Total files changed (added/modified/deleted)
     * List all changed files with change type
     * Number of commits made (if any)
     * Final git status
   - Todo summary:
     * Total tasks completed/remaining
     * List all completed tasks
     * List any incomplete tasks with status
   - Key accomplishments
   - All features implemented
   - Problems encountered and solutions
   - Breaking changes or important findings
   - Dependencies added/removed
   - Configuration changes
   - Deployment steps taken
   - Lessons learned
   - What wasn't completed
   - Tips for future developers

## MARM Integration (Enhanced)
Compile final session context and add MARM summary:
```python
import sys
sys.path.append('.claude/commands')
from marm_integration import get_marm_integration

marm = get_marm_integration()

# Compile final context before ending
final_context = marm.end_session()
if final_context:
    print("\n## MARM Session Summary")
    
    # Get session statistics
    session_info = marm.get_session_info()
    if session_info.get('active_session'):
        stats = session_info['stats']
        print(f"- Notebook entries: {stats.get('notebook_count', 0)}")
        print(f"- Session history: {stats.get('history_count', 0)} messages")
        print(f"- Total session size: {stats.get('total_size_bytes', 0)} bytes")
        
        # Display all notebook entries for archival
        all_entries = marm.notebook_command('/notebook show:')
        print(f"\n### Final Notebook Entries")
        print(all_entries)
        
        print(f"\n### Compiled Session Context Available")
        print("Final context has been compiled and is available for future reference.")
```

4. Empty the `.claude/sessions/.current-session` file (don't remove it, just clear its contents)
5. Inform user the session has been documented

The summary should be thorough enough that another developer (or AI) can understand everything that happened without reading the entire session.