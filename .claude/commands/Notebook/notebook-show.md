Display all notebook entries for the current session with usage statistics.

## Command Usage
This command is triggered by `/notebook show:` syntax.

## Implementation
```python
import sys
sys.path.append('.claude/commands')
from marm_integration import get_marm_integration

marm = get_marm_integration()
result = marm.notebook_command('/notebook show:')
print(result)
```

## Expected Output Format
```
📊 Usage: 5/30 entries, 2,147/30,000 chars

Notebook entries:
• session-start: Started integration session at 2025-08-05 12:34
• express-complete: 4W1H captured for notebook integration
• key-findings: Enhancement pattern preserves existing functionality
• plan-decisions: FileStorage with atomic operations chosen
• implementation-notes: Core integration module created successfully
```

If notebook is empty:
```
Notebook is empty.
```

## Error Handling
- No active session: "No active session. Start a session first with /session-start"
- MARM unavailable: "MARM notebook system not available"
- Other errors: Display specific error message with guidance