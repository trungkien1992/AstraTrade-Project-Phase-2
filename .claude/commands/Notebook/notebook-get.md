Retrieve a specific entry from the current session's notebook.

## Command Usage
This command is triggered by `/notebook get:[key]` syntax.

## Implementation
```python
import sys
sys.path.append('.claude/commands')
from marm_integration import get_marm_integration

# Extract key from command
# Example: "/notebook get:session-start"
command = "[full command string]"  # Provided by user input
marm = get_marm_integration()
result = marm.notebook_command(command)
print(result)
```

## Expected Output Examples

**Entry Found:**
```
"session-start": Started integration session at 2025-08-05 12:34
```

**Entry Not Found:**
```
No entry for "nonexistent-key"
```

**Missing Key:**
```
Usage: /notebook key:[name] [data] | /notebook get:[name] | /notebook show:
```

## Usage Examples
- `/notebook get:session-start` - Get the session start entry
- `/notebook get:key-findings` - Get a specific findings entry
- `/notebook get:implementation-notes` - Get implementation notes

## Error Handling
- No active session: "No active session. Start a session first with /session-start"
- MARM unavailable: "MARM notebook system not available"
- Invalid syntax: Display usage help with available commands