Delete a specific entry from the current session's notebook.

## Command Usage
This command is triggered by `/notebook delete:[key]` syntax.

## Implementation
```python
import sys
sys.path.append('.claude/commands')
from marm_integration import get_marm_integration

# Extract key from command
# Example: "/notebook delete:old-entry"
command = "[full command string]"  # Provided by user input
marm = get_marm_integration()
result = marm.notebook_command(command)
print(result)
```

## Expected Output Examples

**Successful Deletion:**
```
Deleted "old-entry" from notebook
```

**Entry Not Found:**
```
No entry found for "nonexistent-key"
```

**Missing Key:**
```
Usage: /notebook delete:[name]
```

## Usage Examples
- `/notebook delete:temp-notes` - Delete temporary notes entry
- `/notebook delete:old-findings` - Delete outdated findings
- `/notebook delete:duplicate-entry` - Remove duplicate entries

## Important Notes
- **Deletion is permanent** - entries cannot be recovered once deleted
- **No confirmation prompt** - deletion happens immediately
- **Storage space freed** - deleted entries free up space for new ones
- **Automatic persistence** - changes are saved immediately to storage

## Error Handling
- No active session: "No active session. Start a session first with /session-start"
- MARM unavailable: "MARM notebook system not available"
- Invalid syntax: Display usage help with correct format

## Best Practices
- Verify entry name with `/notebook get:[key]` before deletion
- Use `/notebook show:` to see all entries before bulk cleanup
- Consider archiving important entries to session files before deletion