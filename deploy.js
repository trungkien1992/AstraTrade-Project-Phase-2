import { Account, Provider, Contract, json, stark, RpcProvider, CallData } from 'starknet';
import fs from 'fs';

// Configuration
const STARKNET_RPC_URL = 'https://free-rpc.nethermind.io/sepolia-juno/';
const ACCOUNT_ADDRESS = '0x05715B600c38f3BFA539281865Cf8d7B9fE998D79a2CF181c70eFFCb182752F7';
const PRIVATE_KEY = '0x06f2d72ab60a23f96e6a1ed1c1d368f706ab699e3ead50b7ae51b1ad766f308e';

async function main() {
    console.log('🚀 Starting AstraTrade contract deployment...\n');

    try {
        // Initialize provider
        const provider = new RpcProvider({ 
            nodeUrl: STARKNET_RPC_URL 
        });

        // Initialize account
        const account = new Account(provider, ACCOUNT_ADDRESS, PRIVATE_KEY);
        
        console.log('📋 Account address:', ACCOUNT_ADDRESS);
        
        // Get account nonce
        const nonce = await account.getNonce();
        console.log('🔢 Account nonce:', nonce);

        // Load and deploy Paymaster contract
        console.log('\n📄 Loading Paymaster contract...');
        const paymasterClassJson = JSON.parse(
            fs.readFileSync('./target/dev/astratrade_contracts_AstraTradePaymaster.contract_class.json', 'utf8')
        );

        console.log('📤 Declaring Paymaster contract...');
        const paymasterDeclareResponse = await account.declare({
            contract: paymasterClassJson,
            compiledClassHash: '0x038bef691b82a484e837be0130dd925b48bb477146ecc5381ced986f46cba64d' // Manually computed from starkli
        });

        console.log('⏳ Waiting for Paymaster declaration confirmation...');
        await provider.waitForTransaction(paymasterDeclareResponse.transaction_hash);
        
        const paymasterClassHash = paymasterDeclareResponse.class_hash;
        console.log('✅ Paymaster declared with class hash:', paymasterClassHash);

        console.log('🚀 Deploying Paymaster contract...');
        const paymasterConstructorCalldata = CallData.compile([ACCOUNT_ADDRESS]);
        const paymasterDeployResponse = await account.deployContract({
            classHash: paymasterClassHash,
            constructorCalldata: paymasterConstructorCalldata,
        });

        console.log('⏳ Waiting for Paymaster deployment confirmation...');
        await provider.waitForTransaction(paymasterDeployResponse.transaction_hash);

        const paymasterAddress = paymasterDeployResponse.contract_address;
        console.log('✅ Paymaster deployed at address:', paymasterAddress);

        // Load and deploy Vault contract
        console.log('\n📄 Loading Vault contract...');
        const vaultClassJson = JSON.parse(
            fs.readFileSync('./target/dev/astratrade_contracts_AstraTradeVault.contract_class.json', 'utf8')
        );

        console.log('📤 Declaring Vault contract...');
        const vaultDeclareResponse = await account.declare({
            contract: vaultClassJson,
            compiledClassHash: '0x01a5b64701fa97b88aa5390c19ed6b531ca4cd9459d17870deeeb17a8b8415fe' // Manually computed from starkli
        });

        console.log('⏳ Waiting for Vault declaration confirmation...');
        await provider.waitForTransaction(vaultDeclareResponse.transaction_hash);
        
        const vaultClassHash = vaultDeclareResponse.class_hash;
        console.log('✅ Vault declared with class hash:', vaultClassHash);

        console.log('🚀 Deploying Vault contract...');
        const vaultConstructorCalldata = CallData.compile([ACCOUNT_ADDRESS]);
        const vaultDeployResponse = await account.deployContract({
            classHash: vaultClassHash,
            constructorCalldata: vaultConstructorCalldata,
        });

        console.log('⏳ Waiting for Vault deployment confirmation...');
        await provider.waitForTransaction(vaultDeployResponse.transaction_hash);

        const vaultAddress = vaultDeployResponse.contract_address;
        console.log('✅ Vault deployed at address:', vaultAddress);

        // Save deployment results
        const deploymentResults = {
            network: 'starknet-sepolia',
            deployed_at: new Date().toISOString(),
            account_address: ACCOUNT_ADDRESS,
            contracts: {
                AstraTradePaymaster: {
                    class_hash: paymasterClassHash,
                    contract_address: paymasterAddress,
                    declaration_tx: paymasterDeclareResponse.transaction_hash,
                    deployment_tx: paymasterDeployResponse.transaction_hash,
                    starkscan_url: `https://sepolia.starkscan.co/contract/${paymasterAddress}`
                },
                AstraTradeVault: {
                    class_hash: vaultClassHash,
                    contract_address: vaultAddress,
                    declaration_tx: vaultDeclareResponse.transaction_hash,
                    deployment_tx: vaultDeployResponse.transaction_hash,
                    starkscan_url: `https://sepolia.starkscan.co/contract/${vaultAddress}`
                }
            }
        };

        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const deploymentFile = `deployment_results_${timestamp}.json`;
        
        fs.writeFileSync(deploymentFile, JSON.stringify(deploymentResults, null, 2));

        console.log('\n🎉 DEPLOYMENT SUCCESSFUL! 🎉');
        console.log('\n📊 DEPLOYMENT SUMMARY:');
        console.log('='.repeat(50));
        console.log(`📅 Deployed on: ${deploymentResults.deployed_at}`);
        console.log(`🌐 Network: Starknet Sepolia Testnet`);
        console.log(`👤 Deployer: ${ACCOUNT_ADDRESS}`);
        console.log('');
        console.log('📋 PAYMASTER CONTRACT:');
        console.log(`   🆔 Class Hash: ${paymasterClassHash}`);
        console.log(`   📍 Address: ${paymasterAddress}`);
        console.log(`   🔗 StarkScan: https://sepolia.starkscan.co/contract/${paymasterAddress}`);
        console.log('');
        console.log('📋 VAULT CONTRACT:');
        console.log(`   🆔 Class Hash: ${vaultClassHash}`);
        console.log(`   📍 Address: ${vaultAddress}`);
        console.log(`   🔗 StarkScan: https://sepolia.starkscan.co/contract/${vaultAddress}`);
        console.log('');
        console.log(`💾 Results saved to: ${deploymentFile}`);
        console.log('='.repeat(50));

        // Test the deployed contracts
        console.log('\n🧪 Testing deployed contracts...');
        
        // Test Paymaster
        const paymasterContract = new Contract(paymasterClassJson.abi, paymasterAddress, provider);
        try {
            const dummyValue = await paymasterContract.get_dummy();
            console.log('✅ Paymaster test successful - dummy value:', dummyValue);
        } catch (error) {
            console.log('❌ Paymaster test failed:', error.message);
        }

        // Test Vault
        const vaultContract = new Contract(vaultClassJson.abi, vaultAddress, provider);
        try {
            const owner = await vaultContract.get_owner();
            console.log('✅ Vault test successful - owner:', owner);
        } catch (error) {
            console.log('❌ Vault test failed:', error.message);
        }

        console.log('\n🏁 All operations completed!');
        
    } catch (error) {
        console.error('💥 Deployment failed:', error);
        process.exit(1);
    }
}

main().catch(console.error);