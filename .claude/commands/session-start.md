Start a new development session by creating a session file in `.claude/sessions/` with the format `YYYY-MM-DD-HHMM-$ARGUMENTS.md` (or just `YYYY-MM-DD-HHMM.md` if no name provided).

The session file should begin with:
1. Session name and timestamp as the title
2. Session overview section with start time
3. Goals section (ask user for goals if not clear)
4. Empty progress section ready for updates

After creating the file, create or update `.claude/sessions/.current-session` to track the active session filename.

## MARM Integration (Enhanced)
Initialize MARM notebook session alongside standard session:
```python
import sys
sys.path.append('.claude/commands')
from marm_integration import get_marm_integration

marm = get_marm_integration()
session_filename = "[created session filename]"  # e.g., "2025-08-05-1234-integration.md"
marm.start_session(session_filename)
```

Confirm the session has started and remind the user they can:
- Update it with `/project:session-update`
- End it with `/project:session-end`
- **NEW:** Use notebook features with `/notebook show:`, `/notebook add:[key] [value]`