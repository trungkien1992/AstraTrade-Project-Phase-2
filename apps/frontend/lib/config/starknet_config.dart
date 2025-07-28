import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/starknet_service.dart';

/// Configuration for Starknet network settings
class StarknetConfig {
  static const bool _defaultUseMainnet = false; // Default to testnet for safety
  
  /// Whether to use mainnet (true) or testnet (false)
  static bool get useMainnet => _defaultUseMainnet;
  
  /// Network name for display purposes
  static String get networkName => useMainnet ? 'Mainnet' : 'Sepolia Testnet';
  
  /// Chain ID for the current network
  static String get chainId => useMainnet ? '0x534e5f4d41494e' : '0x534e5f5345504f4c4941';
  
  /// Block explorer URL for the current network
  static String get blockExplorerUrl => useMainnet 
    ? 'https://starkscan.co'
    : 'https://sepolia.starkscan.co';
    
  /// Default token contracts for the current network
  static Map<String, String> get tokenContracts => useMainnet ? {
    'ETH': '0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7',
    'USDC': '0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8',
    'USDT': '0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8',
    'STRK': '0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d',
  } : {
    'ETH': '0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7',
    'USDC': '0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8', // Testnet USDC
    'USDT': '0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8', // Testnet USDT
    'STRK': '0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d', // Testnet STRK
  };
}

final environmentStarknetServiceProvider = Provider((ref) {
  final useMainnet = const bool.fromEnvironment('USE_MAINNET', defaultValue: false);
  return StarknetService(useMainnet: useMainnet);
});

final networkModeProvider = StateProvider<bool>((ref) => StarknetConfig.useMainnet);

final dynamicStarknetServiceProvider = Provider((ref) {
  final useMainnet = ref.watch(networkModeProvider);
  return StarknetService(useMainnet: useMainnet);
});