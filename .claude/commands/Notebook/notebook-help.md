Display help information for all notebook commands and features.

## Notebook Command Reference

### Basic Commands
- **`/notebook show:`** - List all entries with usage statistics
- **`/notebook add:[key] [value]`** - Add new entry (rate limited)
- **`/notebook get:[key]`** - Retrieve specific entry
- **`/notebook delete:[key]`** - Delete entry (permanent)

### Usage Examples
```bash
# View all entries
/notebook show:

# Add new entries
/notebook add:session-goal "Integrate MARM with Claude Code"
/notebook add:key-insight "Enhancement pattern preserves compatibility"
/notebook add:next-steps "Implement workflow auto-logging"

# Retrieve entries
/notebook get:session-goal
/notebook get:key-insight

# Delete entries
/notebook delete:temp-notes
/notebook delete:old-findings
```

### Entry Validation Rules
- **Key requirements:** 1-64 characters, letters/numbers/dash/space only
- **Value requirements:** 1-2048 characters maximum
- **Rate limiting:** 300ms cooldown between additions
- **Storage limits:** 30 entries max, 30,000 characters total

### Session Integration
- **Auto-logging:** Major workflow stages automatically logged
- **Session start:** Creates initial "session-start" entry
- **Session end:** Creates final "session-end" entry with summary
- **Context compilation:** Notebook entries included in AI context

### Storage and Persistence
- **Location:** `.claude/sessions/notebook-storage.json`
- **Format:** JSON with atomic file operations
- **Backup:** Automatic backup rotation for data safety
- **Persistence:** Survives Claude Code restarts

### Best Practices
1. **Descriptive keys:** Use clear, consistent naming conventions
2. **Concise values:** Keep entries focused and actionable
3. **Regular cleanup:** Delete outdated or duplicate entries
4. **Strategic use:** Capture insights, decisions, and key findings
5. **Context awareness:** Remember entries enhance AI understanding

### Error Messages
- **No session:** "No active session. Start a session first with /session-start"
- **Rate limit:** "⚠️ Rate limit: Please wait Xms before saving another entry"
- **Storage full:** "⚠️ Notebook is full (30 entries max). Delete some entries first"
- **Size limit:** "⚠️ Notebook storage limit reached (30,000 chars max)"
- **Invalid entry:** "Invalid notebook entry. Key must be 1-64 chars..."
- **Not found:** "No entry for '[key]'"

### Integration with Claude Code
- **Enhanced sessions:** All session commands now include notebook features
- **Workflow logging:** Express/Ask/Explore/Plan stages auto-logged
- **Context compilation:** Enhanced AI prompts with notebook history
- **Backward compatibility:** All existing commands work unchanged

## Need More Help?
- Use `/notebook show:` to see current notebook status
- Check session files in `.claude/sessions/` for persistent records
- Review `.claude/sessions/notebook-storage.json` for raw data
- All notebook features are optional - existing workflows unaffected