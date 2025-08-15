# Cairo UMAS System Status

Monitor the Ultimate Multi-Agent System (UMAS) status, agent performance, workflow execution, and system health for Cairo smart contract operations.

## Usage

```bash
@claude cairo-umas-status [OPTIONS]
```

## Options

- `--detailed`: Show detailed agent performance metrics
- `--agents`: Show agent-specific status and capabilities
- `--workflows`: Show active and completed workflow status
- `--health`: Show system health and resource usage
- `--cache`: Show cache performance and statistics
- `--monitoring`: Show monitoring and alerting status
- `--json`: Output in JSON format for integration
- `--watch`: Continuously monitor status (refresh every 5 seconds)

## Examples

```bash
# Basic system status
@claude cairo-umas-status

# Detailed agent performance
@claude cairo-umas-status --detailed --agents

# System health overview
@claude cairo-umas-status --health

# Watch system status in real-time
@claude cairo-umas-status --watch

# Export status as JSON
@claude cairo-umas-status --json > status.json

# Complete system overview
@claude cairo-umas-status --detailed --agents --workflows --health --cache
```

## Status Information

### Basic Status Display

```bash
🤖 Cairo UMAS System Status - 2024-01-15 14:30:25
===============================================

📊 System Overview:
   Status: RUNNING ✅
   Uptime: 2h 15m 33s
   Active Agents: 5/5
   Active Workflows: 2
   Queue Depth: 0
   System Health: EXCELLENT

🎯 Quick Metrics:
   • Tasks Completed: 847 (success rate: 94.2%)
   • Average Response Time: 1.8s
   • Cache Hit Rate: 73%
   • Memory Usage: 892 MB / 2.1 GB
   • CPU Usage: 23%

🚀 Recent Activity:
   • 14:28 - Security audit completed for exchange.cairo
   • 14:25 - Code generation completed for vault functions
   • 14:23 - Expert coordination resolved architecture query
   • 14:20 - Performance optimization suggestions generated

🌐 Services:
   • Prometheus Metrics: http://localhost:8000/metrics ✅
   • WebSocket Monitor: ws://localhost:8765 ✅
   • Redis Cache: localhost:6379 ✅
```

### Detailed Agent Status

```bash
🤖 Cairo Agent Performance Details
=================================

🛡️  CairoSecurityAgent (cairo_security_agent)
    Status: IDLE ✅                Role: SECURITY
    Capabilities: 4               Specialization: Vulnerability Analysis
    Tasks Completed: 23          Success Rate: 100%
    Avg Response Time: 3.2s      Last Active: 2 minutes ago
    Current Load: 0%             Health Score: 98/100
    
    Recent Tasks:
    • 14:28 - Security audit: exchange.cairo (COMPLETED)
    • 14:15 - Access control analysis (COMPLETED)  
    • 14:05 - Reentrancy detection (COMPLETED)

💻 CairoDevelopmentAgent (cairo_development_agent)  
    Status: WORKING 🔄           Role: DEVELOPER
    Capabilities: 3               Specialization: Code Generation
    Tasks Completed: 156         Success Rate: 92.3%
    Avg Response Time: 2.1s      Last Active: Active now
    Current Load: 45%            Health Score: 95/100
    
    Current Task: Code generation for trading position management
    Progress: 78% (estimated 30s remaining)
    
    Recent Tasks:
    • 14:25 - Code generation: vault functions (COMPLETED)
    • 14:18 - Storage optimization analysis (COMPLETED)
    • 14:12 - Function design assistance (COMPLETED)

🏗️  CairoArchitectureAgent (cairo_architecture_agent)
    Status: IDLE ✅             Role: ARCHITECT  
    Capabilities: 5              Specialization: System Design
    Tasks Completed: 45          Success Rate: 97.8%
    Avg Response Time: 4.1s      Last Active: 7 minutes ago
    Current Load: 0%             Health Score: 99/100
    
    Recent Tasks:
    • 14:23 - Architecture review: contract composition (COMPLETED)
    • 14:10 - Upgrade strategy design (COMPLETED)
    • 13:58 - Integration patterns analysis (COMPLETED)

🧪 CairoTestingAgent (cairo_testing_agent)
    Status: IDLE ✅             Role: TESTER
    Capabilities: 5              Specialization: Test Generation
    Tasks Completed: 67          Success Rate: 96.4%
    Avg Response Time: 2.8s      Last Active: 12 minutes ago  
    Current Load: 0%             Health Score: 97/100
    
    Recent Tasks:
    • 14:18 - Integration test generation (COMPLETED)
    • 14:08 - Property testing strategy (COMPLETED)
    • 13:55 - Security test case generation (COMPLETED)

🔧 CairoRefactoringAgent (cairo_refactoring_agent)
    Status: IDLE ✅             Role: OPTIMIZER
    Capabilities: 5              Specialization: Safe Refactoring  
    Tasks Completed: 34          Success Rate: 94.1%
    Avg Response Time: 5.2s      Last Active: 18 minutes ago
    Current Load: 0%             Health Score: 96/100
    
    Recent Tasks:
    • 13:52 - Code smell detection (COMPLETED)
    • 13:41 - Refactoring impact analysis (COMPLETED)
    • 13:28 - Dependency analysis (COMPLETED)
```

### Workflow Status

```bash
📋 Active Workflows
==================

🔍 cairo_expert_coordination_20240115_143025
    Status: IN_PROGRESS 🔄       Priority: HIGH
    Started: 14:30:25            Estimated Completion: 14:31:15
    Progress: 60%                Current Phase: Expert Consultation
    Query: "How to implement secure cross-contract communication?"
    Experts: Security, Architecture, Development
    
    Phase Progress:
    ✅ Query Analysis (completed in 2.3s)
    ✅ Expert Routing (completed in 0.8s)  
    🔄 Multi-Expert Analysis (in progress - 45s elapsed)
    ⏳ Consensus Building (pending)
    ⏳ Final Recommendation (pending)

🔒 cairo_security_audit_20240115_142820
    Status: COMPLETED ✅         Priority: HIGH
    Started: 14:28:20           Completed: 14:28:47
    Duration: 27s                Success: YES
    Contracts: exchange.cairo, vault.cairo
    Results: 3 medium issues found, 0 critical issues
    
    Phase Results:
    ✅ Contract Discovery (2.1s)
    ✅ Security Analysis (18.4s) 
    ✅ Vulnerability Assessment (3.2s)
    ✅ Remediation Planning (3.1s)

📊 Recent Workflows (Last 24h)
=============================
    Total Executed: 89          Success Rate: 96.6%
    Average Duration: 23.4s     Fastest: 1.2s (simple query)
    Failed Workflows: 3         Longest: 2m 15s (complex refactoring)
    
    By Type:
    • Expert Coordination: 34 (94.1% success)
    • Security Audits: 28 (100% success)  
    • Development Cycle: 15 (93.3% success)
    • Safe Refactoring: 8 (87.5% success)
    • Code Reviews: 4 (100% success)
```

### System Health

```bash
🏥 System Health Dashboard
=========================

💚 Overall Health: EXCELLENT (96/100)

🖥️  Resource Usage:
    CPU: 23% (4 cores available)      Load Average: 1.2, 1.0, 0.8
    Memory: 892 MB / 2.1 GB (42%)     Swap: 0 MB used
    Disk I/O: Low (12 MB/s read, 3 MB/s write)
    Network: Moderate (156 KB/s in, 89 KB/s out)

📊 Performance Metrics:
    Request Queue: 0 pending          Max Queue Depth: 3 (last hour)
    Response Times: P50: 1.2s, P95: 4.8s, P99: 12.3s
    Error Rate: 2.1% (last hour)      Throughput: 45 tasks/hour
    Cache Hit Rate: 73%               Cache Size: 2,847 entries

🔧 Agent Health:
    Security Agent:     ✅ 98/100     Last Health Check: 30s ago
    Development Agent:  ✅ 95/100     Last Health Check: 35s ago  
    Architecture Agent: ✅ 99/100     Last Health Check: 25s ago
    Testing Agent:      ✅ 97/100     Last Health Check: 40s ago
    Refactoring Agent:  ✅ 96/100     Last Health Check: 28s ago

🌐 External Services:
    Redis Cache:        ✅ Connected  Latency: 0.8ms
    Prometheus:         ✅ Active     Last Scrape: 15s ago
    WebSocket Server:   ✅ Running    Connected Clients: 2
    MARM Knowledge:     ✅ Synced     Last Update: 2m ago

⚠️  Alerts & Warnings:
    • None active ✅

📈 Trends (Last 6 hours):
    Task Success Rate: ↗️ Improving (92% → 94%)
    Response Time: ↘️ Decreasing (2.1s → 1.8s)  
    Memory Usage: ↗️ Increasing (750MB → 892MB)
    Cache Efficiency: ↗️ Improving (68% → 73%)
```

### Cache Performance

```bash
💾 Cache Performance Statistics
==============================

📊 Overall Cache Stats:
    Hit Rate: 73.4%               Miss Rate: 26.6%
    Total Entries: 2,847         Cache Size: 145 MB
    Evictions: 23 (last hour)    Max Size: 10,000 entries
    Average Lookup Time: 0.3ms   Cache Strategy: ADAPTIVE

🔍 Cache Breakdown by Type:
    
    Security Audits:
    • Entries: 892 (31%)          Hit Rate: 81%
    • Average Size: 23 KB         TTL: 1 hour
    • Most Cached: Access control patterns
    
    Code Generation:  
    • Entries: 1,234 (43%)        Hit Rate: 69%
    • Average Size: 15 KB         TTL: 30 minutes
    • Most Cached: Function templates
    
    Architecture Analysis:
    • Entries: 456 (16%)          Hit Rate: 78%
    • Average Size: 31 KB         TTL: 2 hours
    • Most Cached: Design patterns
    
    Expert Queries:
    • Entries: 265 (10%)          Hit Rate: 62%
    • Average Size: 8 KB          TTL: 15 minutes
    • Most Cached: Common questions

🎯 Cache Efficiency Trends:
    Hour 14: 73% hit rate (current)
    Hour 13: 71% hit rate          
    Hour 12: 68% hit rate
    Hour 11: 70% hit rate
    
📈 Performance Impact:
    Cache Hits: 2.1s avg saved per request
    Cache Misses: Full analysis required
    Total Time Saved: 47.3 minutes (today)
    Cost Reduction: 68% fewer redundant computations
```

## JSON Output Format

When using `--json` flag, status is returned in structured format:

```json
{
  "timestamp": "2024-01-15T14:30:25Z",
  "system": {
    "status": "running",
    "uptime_seconds": 8133,
    "health_score": 96,
    "version": "2.0.0"
  },
  "agents": [
    {
      "id": "cairo_security_agent",
      "type": "CairoSecurityAgent", 
      "status": "idle",
      "role": "SECURITY",
      "capabilities": 4,
      "tasks_completed": 23,
      "success_rate": 1.0,
      "avg_response_time": 3.2,
      "current_load": 0.0,
      "health_score": 98,
      "last_active": "2024-01-15T14:28:15Z"
    }
  ],
  "workflows": {
    "active": 2,
    "completed_today": 89,
    "success_rate": 0.966,
    "avg_duration": 23.4
  },
  "resources": {
    "cpu_percent": 23,
    "memory_mb": 892,
    "memory_total_mb": 2048,
    "cache_hit_rate": 0.734
  },
  "services": {
    "redis": {"status": "connected", "latency_ms": 0.8},
    "prometheus": {"status": "active"},
    "websocket": {"status": "running", "clients": 2}
  }
}
```

## Monitoring Integration

### Prometheus Metrics

Available at `http://localhost:8000/metrics`:

```prometheus
# Agent task metrics
cairo_agent_tasks_total{agent_type="security", status="completed"} 23
cairo_agent_task_duration_seconds{agent_type="security"} 3.2
cairo_agent_errors_total{agent_type="security", error_type="timeout"} 0

# Workflow metrics  
cairo_workflow_executions_total{workflow_type="security_audit"} 28
cairo_workflow_duration_seconds{workflow_type="security_audit"} 27.3
cairo_workflow_success_rate{workflow_type="security_audit"} 1.0

# System metrics
cairo_system_memory_bytes 935329792
cairo_cache_hit_rate 0.734
cairo_active_agents 5
```

### WebSocket Real-time Updates

Connect to `ws://localhost:8765` for live status updates:

```javascript
const ws = new WebSocket('ws://localhost:8765');

ws.onmessage = (event) => {
    const update = JSON.parse(event.data);
    console.log('Status update:', update);
};

// Request status updates
ws.send(JSON.stringify({
    type: 'subscribe',
    channels: ['agent_status', 'workflow_progress', 'system_health']
}));
```

## Alerts and Notifications

### Health Check Alerts

System automatically monitors:

- Agent response times > 10 seconds
- Memory usage > 80%  
- Cache hit rate < 50%
- Workflow failure rate > 10%
- External service downtime

### Custom Alert Configuration

```bash
# Set custom alert thresholds
@claude cairo-umas-config --alerts '{"response_time_ms": 5000, "memory_percent": 75}'

# Enable alert notifications
@claude cairo-umas-config --notifications webhook,email,slack
```

## Implementation

This command queries the UMAS system status through the integration layer:

```python
from Cairo_subagent.umas_integration import get_cairo_umas_status
import asyncio

async def show_status():
    status = await get_cairo_umas_status()
    print(f"System Status: {status['status']}")
    print(f"Active Agents: {len(status['agents'])}")
    for agent_name, agent_info in status['agents'].items():
        print(f"  {agent_name}: {agent_info['status']}")

asyncio.run(show_status())
```