# Cairo UMAS System Startup

Start the Ultimate Multi-Agent System (UMAS) with specialized Cairo smart contract agents for enhanced development and security analysis productivity.

## Usage

```bash
@claude cairo-umas-start [OPTIONS]
```

## Options

- `--agents <number>`: Number of Cairo agents to spawn (default: 5)
- `--experts <list>`: Comma-separated list of expert types to include
- `--redis`: Enable Redis caching for improved performance
- `--websocket`: Enable WebSocket server for real-time monitoring
- `--monitoring`: Enable Prometheus metrics (default: true)
- `--config <path>`: Path to custom configuration file
- `--project-path <path>`: Path to Cairo project (default: current directory)

## Expert Types

Available expert agent types:

- `security`: Cairo security audit and vulnerability analysis
- `development`: Code generation, patterns, and best practices
- `architecture`: System design, contract composition, upgrade strategies
- `testing`: Test generation, property testing, integration strategies
- `refactoring`: Safe refactoring with impact analysis and rollback planning

## Examples

```bash
# Start with default configuration (5 agents, all expert types)
@claude cairo-umas-start

# Start with specific expert types and enhanced features
@claude cairo-umas-start --experts security,development,architecture --redis --websocket

# Start with custom configuration
@claude cairo-umas-start --config cairo_umas_config.json --agents 8

# Start for specific project
@claude cairo-umas-start --project-path /path/to/astratrade --monitoring
```

## Configuration File Format

Example `cairo_umas_config.json`:

```json
{
  "redis_enabled": true,
  "redis_host": "localhost",
  "redis_port": 6379,
  "websocket_enabled": true,
  "websocket_port": 8765,
  "monitoring_enabled": true,
  "metrics_port": 8000,
  "cache_strategy": "ADAPTIVE",
  "cache_max_size": 10000,
  "max_agents": 20,
  "task_timeout": 300,
  "max_retries": 3,
  "health_check_interval": 30,
  "cairo_specific": {
    "security_confidence_threshold": 0.95,
    "development_patterns": ["access_control", "upgradeability", "gas_optimization"],
    "audit_severity_levels": ["critical", "high", "medium", "low"],
    "gas_optimization_targets": {
      "function_calls": "< 100k gas",
      "storage_operations": "< 20k gas",
      "contract_deployment": "< 2M gas"
    }
  }
}
```

## System Architecture

When started, UMAS creates the following architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                   Cairo UMAS System                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐      ┌──────────────────┐            │
│  │  WebSocket Server │◄────►│ Prometheus Metrics│           │
│  │  :8765           │      │ :8000            │            │
│  └──────────────────┘      └──────────────────┘            │
│           ▲                          ▲                       │
│           │                          │                       │
│  ┌────────▼──────────────────────────▼─────────┐           │
│  │           Ultimate Event Bus                  │           │
│  │         (Cairo-specific routing)              │           │
│  └───────────────────┬─────────────────────────┘           │
│                      │                                       │
│  ┌───────────────────▼─────────────────────────┐           │
│  │          Cairo Coordinator                    │           │
│  │    (Workflow + Load Balancing)                │           │
│  └───────────────────┬─────────────────────────┘           │
│                      │                                       │
│  ┌───────────────────▼─────────────────────────┐           │
│  │         Specialized Cairo Agents             │           │
│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐      │           │
│  │  │Security│Dev   │Arch  │Test  │ ...      │           │
│  │  │Agent  │Agent │Agent │Agent │          │           │
│  │  └──────┘ └──────┘ └──────┘ └──────┘      │           │
│  └───────────────────┬─────────────────────────┘           │
│                      │                                       │
│  ┌───────────────────▼─────────────────────────┐           │
│  │         MARM Intelligence Layer               │           │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐    │           │
│  │  │Knowledge │ │ Pattern  │ │ Learning  │    │           │
│  │  │  Graph   │ │  Engine  │ │  Capture  │    │           │
│  │  └──────────┘ └──────────┘ └──────────┘    │           │
│  └───────────────────┬─────────────────────────┘           │
│                      │                                       │
│  ┌───────────────────▼─────────────────────────┐           │
│  │       Redis Intelligent Cache Layer          │           │
│  │    (Cairo knowledge + audit results)         │           │
│  └──────────────────────────────────────────────┘           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Startup Process

1. **System Initialization**:
   - Load configuration and validate parameters
   - Initialize Redis connection (if enabled)
   - Start Prometheus metrics server
   - Initialize WebSocket server (if enabled)

2. **Agent Creation**:
   - Spawn specialized Cairo agents based on expert types
   - Register agents with central coordinator
   - Initialize agent capabilities and knowledge bases
   - Start health monitoring for all agents

3. **Service Integration**:
   - Connect to MARM intelligence layer
   - Initialize knowledge graph with Cairo patterns
   - Load existing audit results and learning data
   - Establish event bus communication

4. **Readiness Verification**:
   - Verify all agents are responsive
   - Test core workflow execution
   - Validate external service connections
   - Report system status and readiness

## Expected Output

```bash
🚀 Starting Cairo UMAS System...

✅ Configuration loaded: cairo_umas_config.json
✅ Redis connection established: localhost:6379
✅ Prometheus metrics server started: :8000
✅ WebSocket server started: :8765

🤖 Initializing Cairo Agents...
✅ CairoSecurityAgent (cairo_security_agent): READY
✅ CairoDevelopmentAgent (cairo_development_agent): READY  
✅ CairoArchitectureAgent (cairo_architecture_agent): READY
✅ CairoTestingAgent (cairo_testing_agent): READY
✅ CairoRefactoringAgent (cairo_refactoring_agent): READY

🧠 MARM Integration...
✅ Knowledge Graph connected: 1,247 Cairo patterns loaded
✅ Learning Capture initialized: 89 previous sessions
✅ Pattern Engine ready: 156 identified patterns

📊 System Status:
   • Total Agents: 5
   • Active Workflows: 0
   • Cache Hit Rate: 0% (fresh start)
   • Memory Usage: 145 MB
   • System Health: EXCELLENT

🎯 Cairo UMAS System Ready!
   • Expert Coordination: /cairo-expert-coord
   • Security Audits: /cairo-security-audit  
   • Development Assistance: /cairo-dev-assist
   • System Status: http://localhost:8000/metrics
   • WebSocket Monitor: ws://localhost:8765

💡 Quick Start:
   @claude cairo-umas-execute security_audit --contracts exchange.cairo,vault.cairo
   @claude cairo-umas-execute expert_coordination --query "How to implement secure access control?"
```

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Redis connection failed | Ensure Redis server is running on specified host/port |
| Port already in use | Change ports in configuration or stop conflicting services |
| Agent initialization timeout | Check system resources and reduce agent count |
| MARM integration failed | Verify MARM dependencies are installed and accessible |

### Debug Commands

```bash
# Check system health
@claude cairo-umas-status --health

# View detailed logs
@claude cairo-umas-logs --level debug --tail 100

# Test agent connectivity
@claude cairo-umas-test --agents all

# Reset system state
@claude cairo-umas-reset --confirm
```

## Performance Tuning

### Recommended Settings by Use Case

**Development Environment**:
```bash
@claude cairo-umas-start --agents 3 --experts development,testing --redis
```

**Security Auditing**:
```bash
@claude cairo-umas-start --agents 5 --experts security,architecture --redis --monitoring
```

**Production Analysis**:
```bash
@claude cairo-umas-start --agents 8 --experts all --redis --websocket --monitoring --config production.json
```

### Memory and CPU Guidelines

- **Minimum**: 4 GB RAM, 2 CPU cores
- **Recommended**: 8 GB RAM, 4 CPU cores  
- **High Performance**: 16 GB RAM, 8 CPU cores
- **Memory per agent**: ~150-200 MB
- **CPU per agent**: ~15-25% under load

## Implementation

This command executes the UMAS initialization through the Cairo integration module:

```python
from Cairo_subagent.umas_integration import start_cairo_umas
import asyncio

async def start_system():
    config = {
        "redis_enabled": redis_enabled,
        "websocket_enabled": websocket_enabled,
        "monitoring_enabled": monitoring_enabled,
        "max_agents": agent_count
    }
    success = await start_cairo_umas(config)
    if success:
        print("✅ Cairo UMAS System Ready!")
    else:
        print("❌ Failed to start Cairo UMAS System")

asyncio.run(start_system())
```