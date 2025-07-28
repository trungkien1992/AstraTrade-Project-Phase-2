# AstraTrade Scripts Directory

This directory contains operational scripts for AstraTrade project management, testing, deployment, and utilities.

## Directory Structure

```
scripts/
├── deployment/           # Contract deployment and production scripts
├── testing/             # Contract and API testing scripts  
├── utilities/           # Project utilities and tools
├── context-manager.sh   # Development context management
├── eaept               # Enhanced EAEPT workflow tool
├── eaept-config.yaml   # EAEPT configuration
├── enhanced-eaept-workflow.py # EAEPT workflow automation
├── health_check_requirements.txt # Health check dependencies
└── requirements.txt     # Python dependencies for scripts
```

## Script Categories

### 🚀 Deployment Scripts (`deployment/`)

#### Core Deployment
- **`deploy_contracts.py`** - Complete contract deployment automation
  - Compiles Cairo contracts using Scarb
  - Deploys to Starknet (Sepolia/Mainnet)
  - Configures contract permissions
  - Generates frontend configuration files

- **`deploy_with_starkli.sh`** - Starkli-based deployment script
  - Alternative deployment method using Starkli CLI
  - Suitable for quick deployments and testing

#### Production Deployment  
- **`deploy-production.sh`** - Production deployment script
  - Full production environment setup
  - Infrastructure configuration
  - Monitoring and logging setup

#### Security & Compliance
- **`secure_deploy.py`** - Enhanced security deployment
  - Security-first deployment approach
  - Audit trail and compliance logging
  - Multi-signature support

- **`secure_deploy.sh`** - Secure deployment shell script
  - Shell-based secure deployment
  - Environment validation
  - Security checks and balances

### 🧪 Testing Scripts (`testing/`)

#### Contract Testing
- **`test_contracts.py`** - Comprehensive contract testing framework
  - Full transaction scenario testing
  - Integration testing with Starknet
  - Automated test reporting

- **`test_contracts_simple.py`** - Simple contract compilation testing  
  - Quick compilation verification
  - Basic functionality checks
  - Development workflow testing

- **`test_deployed_contracts.py`** - Deployed contract testing
  - Tests contracts on live networks
  - Production readiness verification
  - Performance benchmarking

#### API Testing
- **`test_extended_exchange_api.py`** - Extended Exchange API testing
  - API connectivity verification
  - Trading functionality testing
  - Integration testing with backend

### 🛠️ Utility Scripts (`utilities/`)

#### Project Management
- **`cleanup_project.py`** - Project cleanup and maintenance
  - Code cleanup and optimization
  - Dependency management
  - File organization

- **`contract_health_check.py`** - Contract health monitoring
  - Contract status verification
  - Performance monitoring
  - Alert generation

#### Database & Infrastructure
- **`migrate_to_postgres.py`** - Database migration utility
  - SQLite to PostgreSQL migration
  - Data integrity verification
  - Migration rollback support

- **`prometheus_exporter.py`** - Metrics export for monitoring
  - Performance metrics collection
  - Prometheus integration
  - Custom metrics definition

#### Specialized Tools
- **`start_rag_backend.py`** - RAG backend initialization
  - Knowledge base setup
  - Vector database initialization
  - API server startup

- **`starkex_crypto.py`** - StarkEx cryptographic utilities
  - Cryptographic operations
  - Key management
  - Security utilities

- **`websocket_manager.py`** - WebSocket connection management
  - Real-time communication setup
  - Connection pooling
  - Message routing

### 🎯 Development Tools (Root Level)

- **`context-manager.sh`** - Development environment management
- **`eaept`** - Enhanced EAEPT workflow executable
- **`enhanced-eaept-workflow.py`** - Advanced development workflow automation
- **`eaept-config.yaml`** - EAEPT configuration settings

## Usage Instructions

### Prerequisites
```bash
# Install Python dependencies
pip install -r requirements.txt
pip install -r health_check_requirements.txt
```

### Contract Deployment
```bash
# Full deployment with configuration
python deployment/deploy_contracts.py --network sepolia

# Quick deployment with Starkli  
./deployment/deploy_with_starkli.sh

# Production deployment
./deployment/deploy-production.sh
```

### Testing
```bash
# Comprehensive contract testing
python testing/test_contracts.py

# Simple compilation test
python testing/test_contracts_simple.py

# Extended API testing
python testing/test_extended_exchange_api.py
```

### Utilities
```bash
# Project cleanup
python utilities/cleanup_project.py --full

# Health check
python utilities/contract_health_check.py

# Database migration
python utilities/migrate_to_postgres.py --backup
```

## Environment Variables

Required environment variables for script execution:

```bash
# Starknet Configuration
STARKNET_PRIVATE_KEY=your_private_key
STARKNET_ACCOUNT_ADDRESS=your_account_address
STARKNET_RPC_URL=https://starknet-sepolia.public.blastapi.io

# Extended Exchange API
EXTENDED_EXCHANGE_API_KEY=your_api_key
EXTENDED_EXCHANGE_SECRET=your_secret

# Database Configuration  
DATABASE_URL=postgresql://user:pass@localhost/astratrade
```

## Security Considerations

- **Private Keys**: Never commit private keys to version control
- **API Keys**: Use environment variables or secure vaults
- **Network Access**: Verify network configurations before deployment
- **Permissions**: Run scripts with minimal required permissions

## Troubleshooting

### Common Issues

1. **Compilation Errors**
   ```bash
   # Verify Scarb installation
   scarb --version
   
   # Clean and rebuild
   cd apps/contracts && scarb clean && scarb build
   ```

2. **Network Connection Issues**
   ```bash
   # Test RPC connectivity
   curl -X POST $STARKNET_RPC_URL -H "Content-Type: application/json" -d '{"method":"starknet_chainId","params":[],"id":1,"jsonrpc":"2.0"}'
   ```

3. **Deployment Failures**
   ```bash
   # Check account balance
   python -c "from starknet_py.net.full_node_client import FullNodeClient; print('Balance check needed')"
   ```

## Contributing

When adding new scripts:

1. Place in appropriate subdirectory
2. Add comprehensive docstring
3. Include error handling
4. Update this README
5. Add to requirements.txt if needed

## Support

For script-related issues:
- Check logs in respective directories
- Verify environment variables
- Ensure dependencies are installed
- Contact development team for assistance

---

*Last Updated: July 28, 2025 | Version: 2.0*