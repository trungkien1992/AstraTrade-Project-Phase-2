# Test Plan - MARM Notebook Integration

## Test Strategy Overview

### Testing Approach
- **Unit Tests:** Individual component functionality
- **Integration Tests:** Component interaction and data flow
- **Compatibility Tests:** Backward compatibility and existing workflow preservation
- **Performance Tests:** Response times and resource usage
- **User Acceptance Tests:** End-to-end workflow validation

### Test Environment Setup
```bash
# Test directory structure
test-environment/
├── .claude/
│   ├── sessions/
│   ├── memory/
│   └── commands/
├── tools/
│   └── Notebook-Context-Management/
└── test-data/
    ├── existing-sessions/
    ├── mock-workflows/
    └── performance-data/
```

## Unit Test Coverage

### UT-1: MARM Core Integration
**Scope:** Basic MARM functionality integration with Claude Code

**Test Cases:**
```python
def test_storage_initialization():
    """Test FileStorage setup with Claude Code directories"""
    # Given: .claude/sessions/ directory exists
    # When: initialize_marm_storage() called
    # Then: FileStorage configured, persistence enabled
    
def test_session_id_mapping():
    """Test Claude session filename to MARM ID conversion"""
    # Given: Claude session file "2025-08-05-1234-integration.md"
    # When: claude_to_marm_session_id() called
    # Then: Returns "claude-2025-08-05-1234-integration"
    
def test_current_session_tracking():
    """Test .current-session file integration"""
    # Given: .current-session contains "2025-08-05-1234-test.md"
    # When: get_current_session_id() called
    # Then: Returns "claude-2025-08-05-1234-test"
```

**Coverage Target:** 100% of MARM integration wrapper functions
**Test Data:** Various session filename formats, edge cases, invalid inputs

### UT-2: Notebook Command Parsing
**Scope:** /notebook command syntax parsing and validation

**Test Cases:**
```python
def test_notebook_command_parsing():
    """Test all /notebook command variants"""
    test_cases = [
        ("/notebook show:", ("show", "", "")),
        ("/notebook add:key value here", ("add", "key", "value here")),
        ("/notebook get:test-key", ("get", "test-key", "")),
        ("/notebook delete:old-key", ("delete", "old-key", "")),
        ("/notebook invalid", ("help", "", ""))
    ]
    
def test_notebook_operations():
    """Test notebook CRUD operations"""
    # Test add, get, list, delete operations
    # Validate rate limiting behavior
    # Test entry size and count limits
```

**Coverage Target:** 100% of command parsing logic
**Test Data:** Valid commands, malformed input, edge cases, boundary conditions

### UT-3: Auto-Logging System
**Scope:** Workflow stage detection and auto-logging functionality

**Test Cases:**
```python
def test_workflow_stage_detection():
    """Test detection of workflow-comprehensive stages"""
    # Mock workflow command execution
    # Verify stage detection accuracy
    # Test auto-logging trigger conditions
    
def test_auto_log_formatting():
    """Test auto-log entry format and content"""
    # Verify timestamp inclusion
    # Test stage name formatting
    # Validate entry content structure
```

**Coverage Target:** 90% of auto-logging logic
**Test Data:** Mock workflow executions, various stage types, timing scenarios

## Integration Test Coverage

### IT-1: Session Lifecycle Integration  
**Scope:** End-to-end session management with MARM integration

**Test Scenario 1: New Session Creation**
```bash
# Test Steps:
1. Execute: /session-start integration-test
2. Verify: Standard session file created
3. Verify: MARM session initialized
4. Verify: .current-session updated
5. Verify: Auto-log entry created
6. Verify: Session-current shows MARM status

# Expected Results:
- Session file: .claude/sessions/2025-08-05-HHMM-integration-test.md
- MARM session: claude-2025-08-05-HHMM-integration-test exists
- Notebook entry: "session-start" with timestamp
- No errors or failures in any step
```

**Test Scenario 2: Session Continuation**  
```bash
# Test Steps:
1. Create existing session with MARM data
2. Execute: /session-current
3. Verify: Standard session info displayed
4. Verify: MARM notebook entries shown
5. Verify: Context compilation available

# Expected Results:
- Both standard and MARM info displayed
- Notebook statistics accurate
- Recent entries shown correctly
```

**Test Scenario 3: Session Termination**
```bash
# Test Steps:
1. Active session with notebook entries
2. Execute: /session-end
3. Verify: Standard session summary generated
4. Verify: MARM context compiled and saved
5. Verify: Session data persisted
6. Verify: .current-session cleared

# Expected Results:
- Complete session summary with MARM data
- All notebook entries preserved
- Storage file updated atomically
```

### IT-2: Workflow Integration
**Scope:** workflow-comprehensive integration with auto-logging

**Test Scenario 1: Express Stage Integration**
```bash
# Test Steps:
1. Start session: /session-start workflow-test
2. Execute: /workflow-comprehensive "Express stage test"
3. Complete Express stage artifacts
4. Verify: Auto-log entry created
5. Check: /notebook show: includes express entry

# Expected Results:
- Express completion auto-logged
- Entry key: "express-MMDD"
- Entry value: Contains 4W1H summary
```

**Test Scenario 2: Multi-Stage Workflow**
```bash
# Test Steps:
1. Execute complete workflow: Express → Ask → Explore → Plan
2. Verify auto-logging at each stage
3. Check notebook accumulates workflow history
4. Verify context compilation includes all stages

# Expected Results:
- 4 auto-log entries (one per stage)
- Chronological workflow history
- Context compilation shows progression
```

### IT-3: Context Compilation Integration
**Scope:** Enhanced context generation combining existing + MARM

**Test Scenario 1: Hybrid Context Generation**
```bash
# Test Steps:
1. Create session with existing context file
2. Add notebook entries via MARM
3. Generate enhanced context
4. Verify both sources included
5. Test context quality and completeness

# Expected Results:
- Both existing and MARM context present
- Proper section separation and formatting
- No data loss or corruption
```

## Compatibility Test Coverage

### CT-1: Backward Compatibility
**Scope:** Ensure existing Claude Code functionality unchanged

**Test Matrix:**
| Existing Command | Test Type | Expected Behavior |
|------------------|-----------|-------------------|
| /session-start   | Basic     | Works unchanged + MARM features |
| /session-current | Basic     | Works unchanged + MARM info |
| /session-end     | Basic     | Works unchanged + MARM summary |
| /session-update  | Basic     | Works unchanged |
| /session-list    | Basic     | Works unchanged |
| /workflow-comprehensive | Integration | Works unchanged + auto-logging |

**Test Cases:**
```python
def test_existing_session_commands():
    """Test all existing session commands work unchanged"""
    # Execute each command in isolation
    # Verify original functionality preserved
    # Confirm no breaking changes introduced
    
def test_existing_session_files():
    """Test compatibility with existing session files"""
    # Load pre-existing session files
    # Verify they open and display correctly
    # Confirm no data corruption or loss
```

### CT-2: Multi-Project Compatibility
**Scope:** Ensure integration works across different project contexts

**Test Scenarios:**
1. **Project Switching:** Test session isolation between projects
2. **Concurrent Projects:** Multiple .claude directories with separate MARM storage
3. **Nested Projects:** Project-in-project scenarios

### CT-3: File System Compatibility
**Scope:** Cross-platform file system behavior

**Test Matrix:**
| Platform | File System | Test Focus |
|----------|-------------|------------|
| macOS    | APFS/HFS+   | Unicode handling, permissions |
| Linux    | ext4/btrfs  | Case sensitivity, permissions |
| Windows  | NTFS        | Path length, reserved names |

## Performance Test Coverage

### PT-1: Session Operation Performance
**Scope:** Measure performance impact of MARM integration

**Baseline Measurements:**
```bash
# Without MARM integration
session-start: ~50ms
session-current: ~20ms  
session-end: ~100ms
```

**Target Performance:**
```bash
# With MARM integration (maximum acceptable impact)
session-start: <150ms (100ms increase)
session-current: <70ms (50ms increase)
session-end: <150ms (50ms increase)
```

**Test Methodology:**
```python
def performance_test_session_operations():
    """Measure session operation performance"""
    times = []
    for i in range(100):
        start_time = time.time()
        execute_session_start(f"perf-test-{i}")
        end_time = time.time()
        times.append(end_time - start_time)
    
    avg_time = sum(times) / len(times)
    p95_time = percentile(times, 95)
    
    assert avg_time < 0.150, f"Average time {avg_time} exceeds 150ms"
    assert p95_time < 0.200, f"P95 time {p95_time} exceeds 200ms"
```

### PT-2: Storage Performance
**Scope:** File I/O operation performance under various conditions

**Test Scenarios:**
1. **Small Sessions:** 1-10 notebook entries, minimal history
2. **Medium Sessions:** 15-25 entries, moderate history  
3. **Large Sessions:** Near-limit sessions (30 entries, max size)
4. **Multiple Sessions:** 10-50 concurrent sessions

**Metrics:**
- File read/write latency
- JSON serialization/deserialization time  
- Memory usage during operations
- Disk space utilization

### PT-3: Context Compilation Performance
**Scope:** Context generation performance with various session sizes

**Test Matrix:**
| Session Size | Notebook Entries | History Items | Target Time |
|--------------|------------------|---------------|-------------|
| Small        | 1-5              | 1-10          | <50ms       |
| Medium       | 10-20            | 50-100        | <100ms      |
| Large        | 25-30            | 150-200       | <200ms      |

## User Acceptance Test Coverage

### UAT-1: New User Experience
**Scope:** First-time user discovery and adoption of notebook features

**Test Scenario:**
```
User Story: As a new Claude Code user, I want to discover and start using notebook features without disrupting my existing workflow.

Acceptance Criteria:
- Existing session workflows work exactly as before
- New notebook features are discoverable through help
- Error messages are clear and actionable
- Learning curve is minimal and gradual
```

**Test Steps:**
1. New user starts standard session
2. User discovers /notebook commands through help
3. User attempts basic notebook operations
4. User integrates notebook into workflow over time

### UAT-2: Power User Experience  
**Scope:** Advanced user adoption of full notebook feature set

**Test Scenario:**
```
User Story: As an experienced Claude Code user, I want to leverage advanced notebook features to enhance my development workflow continuity.

Acceptance Criteria:
- Auto-logging provides value without noise
- Context compilation improves AI interactions
- Workflow integration feels natural
- Advanced features are accessible when needed
```

**Test Steps:**
1. Experienced user adopts auto-logging
2. User leverages context compilation
3. User customizes configuration options
4. User integrates with complex workflows

### UAT-3: Error Recovery Experience
**Scope:** User experience during error conditions and recovery

**Test Scenarios:**
1. **Storage Corruption:** File corruption recovery flow
2. **Disk Full:** Storage space exhaustion handling
3. **Permission Issues:** File access problem resolution
4. **Concurrent Access:** Multiple instance conflict resolution

## Test Data Management

### Test Data Sets
```
test-data/
├── sessions/
│   ├── minimal-session.md
│   ├── standard-session.md  
│   ├── complex-session.md
│   └── corrupted-session.json
├── notebooks/
│   ├── empty-notebook.json
│   ├── sample-entries.json
│   ├── large-notebook.json
│   └── invalid-notebook.json
└── workflows/
    ├── express-artifacts/
    ├── complete-workflow/
    └── interrupted-workflow/
```

### Test Environment Management
```python
class TestEnvironment:
    def setup(self):
        """Create isolated test environment"""
        # Create temporary .claude directory
        # Copy test data files
        # Initialize MARM with test storage
        
    def teardown(self):
        """Clean up test environment"""
        # Remove temporary files
        # Reset MARM state
        # Capture test artifacts
```

## Coverage Targets and Success Criteria

### Code Coverage Targets
- **Unit Tests:** ≥90% line coverage for integration code
- **Integration Tests:** ≥80% feature coverage  
- **Compatibility Tests:** 100% existing command coverage
- **Performance Tests:** All operations within target thresholds

### Success Criteria
1. **Functionality:** All test cases pass
2. **Performance:** No operation exceeds target thresholds
3. **Compatibility:** Zero breaking changes to existing functionality
4. **Reliability:** Zero data loss incidents in testing
5. **Usability:** User acceptance criteria met

### Test Automation
```bash
# Automated test suite execution
./run-tests.sh unit        # Unit tests only
./run-tests.sh integration # Integration tests
./run-tests.sh performance # Performance benchmarks  
./run-tests.sh all         # Complete test suite

# Continuous testing during development
./watch-tests.sh           # Run tests on file changes
```

### Test Reporting
- **Coverage Reports:** HTML coverage reports with line-by-line analysis
- **Performance Reports:** Timing charts and threshold compliance
- **Compatibility Reports:** Existing functionality validation results
- **User Acceptance Reports:** UAT scenario completion status

## Risk-Based Testing Priorities

### High Priority (Must Pass)
1. Backward compatibility tests
2. Data integrity and corruption recovery
3. Basic session lifecycle integration
4. File system operation reliability

### Medium Priority (Should Pass)  
1. Performance threshold compliance
2. Auto-logging accuracy and timing
3. Context compilation correctness
4. Error handling and user experience

### Low Priority (Nice to Have)
1. Advanced configuration options
2. Edge case handling
3. Cross-platform optimization
4. Advanced user workflow scenarios

This comprehensive test plan ensures reliable delivery of MARM notebook integration while maintaining Claude Code's existing functionality and user experience.