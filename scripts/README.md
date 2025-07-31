# AstraTrade Scripts Directory

This directory contains operational scripts for AstraTrade project management, testing, and deployment for the StarkWare bounty submission.

## Directory Structure

```
scripts/
├── deployment/                        # Contract deployment and production scripts
│   ├── deploy-production.sh          # Production deployment automation
│   ├── deploy_contracts.py           # Complete contract deployment with Scarb
│   ├── deploy_with_starkli.sh        # Starkli-based deployment script
│   ├── secure_deploy.py              # Security-first deployment approach
│   └── secure_deploy.sh              # Secure deployment shell script
├── testing/                          # Contract and API testing scripts
│   ├── test_contracts.py             # Comprehensive contract testing framework
│   ├── test_contracts_simple.py      # Simple contract compilation testing
│   ├── test_deployed_contracts.py    # Deployed contract testing on live networks
│   ├── test_extended_exchange_api.py # Extended Exchange API connectivity testing
│   └── test_real_extended_exchange_trading.py # Live trading API integration proof
├── health_check_requirements.txt     # Health monitoring dependencies
├── requirements.txt                  # Python dependencies for all scripts
└── README.md                         # This documentation file
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
  - Integration testing with Starknet Sepolia testnet
  - Automated test reporting and validation
  - Smart contract functionality verification

- **`test_contracts_simple.py`** - Simple contract compilation testing  
  - Quick compilation verification using Scarb
  - Basic functionality checks for Cairo contracts
  - Development workflow testing

- **`test_deployed_contracts.py`** - Deployed contract testing
  - Tests contracts on live Starknet networks
  - Production readiness verification
  - Performance benchmarking and gas analysis

#### API Testing & Integration
- **`test_extended_exchange_api.py`** - Extended Exchange API testing
  - API connectivity verification
  - Trading endpoint functionality testing
  - Authentication and security testing

- **🏆 `test_real_extended_exchange_trading.py`** - **BOUNTY PROOF** Live trading integration
  - **Real trading capability demonstration**
  - Live API connectivity with Extended Exchange
  - HMAC authentication verification
  - **Judge evaluation tool for StarkWare bounty**

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

# Test deployed contracts on live network
python testing/test_deployed_contracts.py

# Extended API connectivity testing
python testing/test_extended_exchange_api.py

# 🏆 BOUNTY EVALUATION: Live trading integration proof
python testing/test_real_extended_exchange_trading.py
```

## 🏆 StarkWare Bounty Evaluation

### Quick Judge Verification (2 minutes)

For StarkWare bounty judges to quickly verify Extended Exchange API integration:

```bash
# 1. Verify contract deployment capability
python testing/test_contracts_simple.py

# 2. Test deployed contracts on Starknet Sepolia
python testing/test_deployed_contracts.py

# 3. BOUNTY REQUIREMENT: Verify live Extended Exchange API integration
python testing/test_real_extended_exchange_trading.py
```

**Expected Output for Bounty Verification:**
```
🎯 ASTRATRADE LIVE TRADING DEMONSTRATION
=======================================================
✅ Extended Exchange API integration demonstrated
✅ Authentication mechanism verified  
✅ Trading endpoints accessible
✅ Real trading capability confirmed
🏆 READY FOR STARKWARE BOUNTY EVALUATION!
```

### Bounty Evidence Files
- **Contract Deployment**: [DEPLOYMENT_VERIFICATION.md](../DEPLOYMENT_VERIFICATION.md)
- **Extended API Proof**: [bounty_evidence/EXTENDED_API_REAL_TRADING_PROOF.md](../bounty_evidence/EXTENDED_API_REAL_TRADING_PROOF.md)
- **Live Demo**: [apps/frontend/execute_real_transaction_BOUNTY_DEMO.dart](../apps/frontend/execute_real_transaction_BOUNTY_DEMO.dart)

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

1. Place in appropriate subdirectory (`deployment/` or `testing/`)
2. Add comprehensive docstring and error handling
3. Update this README with script description
4. Add dependencies to requirements.txt if needed
5. Test thoroughly before committing

## Support

For script-related issues:
- Verify environment variables are set correctly
- Ensure dependencies are installed: `pip install -r requirements.txt`
- Check network connectivity for API-dependent scripts
- Refer to bounty evidence documentation for detailed examples

---

*Last Updated: July 31, 2025 | Version: 3.0 - StarkWare Bounty Submission Ready*