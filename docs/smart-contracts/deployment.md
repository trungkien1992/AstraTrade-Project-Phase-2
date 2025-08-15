# Smart Contract Deployment

## Deployment Status

All AstraTrade smart contracts have been successfully deployed to Starknet Sepolia testnet.

## Contract Addresses

### Latest Deployment (August 14, 2025)

| Contract | Address | Network |
|----------|---------|---------|
| **Exchange V2** | `0x[address]` | Starknet Sepolia |
| **Paymaster** | `0x[address]` | Starknet Sepolia |
| **Vault** | `0x[address]` | Starknet Sepolia |

*Note: Actual addresses are stored in the deployment logs at `/deployment_logs/latest_astratrade_v2_deployment.json`*

## Deployment Process

### Prerequisites

1. **Starknet Account**: Configured deployment account with sufficient ETH
2. **Starkli Tool**: Latest version for contract deployment
3. **Scarb**: Cairo project management and compilation
4. **Contract Compilation**: All contracts must compile successfully

### Deployment Steps

```bash
# 1. Compile contracts
scarb build

# 2. Deploy contracts using deployment script
python scripts/deployment/deploy_astratrade_v2.py

# 3. Verify deployment
python scripts/testing/test_deployed_contracts.py
```

### Deployment Script Features

- **Automated deployment**: Sequential deployment of all contracts
- **Configuration management**: Environment-specific settings
- **Error handling**: Robust error handling and retry logic
- **Logging**: Comprehensive deployment logging
- **Verification**: Post-deployment contract verification

## Contract Interactions

### Exchange V2 Contract

The main trading contract handles:
- Trade execution and settlement
- Position management
- Risk management rules
- Integration with external price feeds

### Paymaster Contract

Enables gasless transactions for users:
- Transaction sponsorship validation
- User allowlist management
- Gas fee calculation and payment
- Integration with AVNU paymaster system

### Vault Contract

Manages user funds and collateral:
- Deposit and withdrawal operations
- Collateral management
- Yield generation (future feature)
- Security and access controls

## Verification and Testing

### Contract Verification

All contracts have been verified on Starknet:
- Source code verification on StarkScan
- Contract interaction testing
- Integration testing with frontend

### Testing Results

- ✅ **Unit Tests**: All contract functions tested
- ✅ **Integration Tests**: Cross-contract interactions verified
- ✅ **Frontend Integration**: Mobile app successfully connects
- ✅ **Paymaster Integration**: Gasless transactions working

## Network Configuration

### Starknet Sepolia Testnet

- **Network ID**: `SN_SEPOLIA`
- **RPC URL**: `https://starknet-sepolia.g.alchemy.com/starknet/v0_13/[API_KEY]`
- **Chain ID**: `0x534e5f5345504f4c4941`

### Mainnet Deployment (Future)

Contracts are ready for mainnet deployment with:
- Production-ready security audits
- Gas optimization
- Comprehensive testing
- Monitoring and alerting setup

## Security Considerations

- **Access Controls**: Proper role-based access control
- **Input Validation**: Comprehensive input validation
- **Reentrancy Protection**: Guards against reentrancy attacks
- **Integer Overflow**: Safe math operations throughout
- **External Call Safety**: Secure external contract interactions

## Monitoring

Deployed contracts are monitored for:
- Transaction volume and success rates
- Gas usage optimization opportunities
- Error patterns and edge cases
- Performance metrics and latency
- Security alerts and anomalies