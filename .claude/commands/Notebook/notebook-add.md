Add a new entry to the current session's notebook with validation and rate limiting.

## Command Usage
This command is triggered by `/notebook add:[key] [value]` syntax.

## Implementation
```python
import sys
sys.path.append('.claude/commands')
from marm_integration import get_marm_integration

# Extract key and value from command
# Example: "/notebook add:key-name This is the value content"
command = "[full command string]"  # Provided by user input
marm = get_marm_integration()
result = marm.notebook_command(command)
print(result)
```

## Expected Output Examples

**Success:**
```
Stored "key-name" → "This is the value content"
```

**Rate Limited:**
```
⚠️ Rate limit: Please wait 127ms before saving another notebook entry.
```

**Validation Errors:**
```
Invalid notebook entry. Key must be 1-64 chars (letters, numbers, dash, space). Value must be 1-2048 chars.
```

**Storage Limits:**
```
⚠️ Notebook is full (30 entries max). Delete some entries first.
```
```
⚠️ Notebook storage limit reached (30,000 chars max). Delete some entries first.
```

## Validation Rules
- **Key:** 1-64 characters, letters/numbers/dash/space only
- **Value:** 1-2048 characters
- **Rate limit:** 300ms cooldown between additions
- **Entry limit:** Maximum 30 entries per session
- **Size limit:** Maximum 30,000 total characters

## Error Handling
- No active session: "No active session. Start a session first with /session-start"
- MARM unavailable: "MARM notebook system not available"
- Invalid syntax: Display usage help and examples