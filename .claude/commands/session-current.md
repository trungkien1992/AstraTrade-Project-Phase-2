Show the current session status by:

1. Check if `.claude/sessions/.current-session` exists
2. If no active session, inform user and suggest starting one
3. If active session exists:
   - Show session name and filename
   - Calculate and show duration since start
   - Show last few updates
   - Show current goals/tasks
   - Remind user of available commands

## MARM Integration (Enhanced)
Display MARM notebook information alongside standard session info:
```python
import sys
sys.path.append('.claude/commands')
from marm_integration import get_marm_integration

marm = get_marm_integration()
session_info = marm.get_session_info()

if session_info['marm_available'] and session_info.get('active_session'):
    print(f"MARM Session ID: {session_info['session_id']}")
    print(f"📊 Notebook: {session_info['notebook_count']}/30 entries, {session_info['notebook_size']}/30,000 chars")
    
    if session_info['recent_entries']:
        print("\nRecent Notebook Entries:")
        for entry in session_info['recent_entries']:
            print(entry)
    
    print("\nAvailable Notebook Commands:")
    print("- /notebook show: - List all entries")
    print("- /notebook add:[key] [value] - Add new entry")
    print("- /notebook get:[key] - Get specific entry")
    print("- /notebook delete:[key] - Delete entry")
```

Keep the output concise and informative.