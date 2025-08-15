import 'dart:convert';
import 'dart:developer';
import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:starknet_provider/starknet_provider.dart';
import 'package:bip39/bip39.dart' as bip39;
import 'package:bip32/bip32.dart' as bip32;

/// Simplified mobile Starknet service for MVP testing
/// Focuses on basic wallet functionality and signature generation
class MobileStarknetService {
  static const String _storagePrefix = 'mobile_starknet_';
  static const String _privateKeyKey = '${_storagePrefix}private_key';
  static const String _addressKey = '${_storagePrefix}address';
  static const String _mnemonicKey = '${_storagePrefix}mnemonic';
  static const String _accountTypeKey = '${_storagePrefix}account_type';

  late final JsonRpcProvider _provider;
  late final FlutterSecureStorage _secureStorage;
  bool _isInitialized = false;

  // Network configurations
  static const String _sepoliaRpcUrl =
      'https://starknet-sepolia.public.blastapi.io/rpc/v0_7';
  static const String _mainnetRpcUrl =
      'https://starknet-mainnet.public.blastapi.io/rpc/v0_7';

  MobileStarknetService() {
    _initializeSecureStorage();
  }

  void _initializeSecureStorage() {
    _secureStorage = const FlutterSecureStorage(
      aOptions: AndroidOptions(
        encryptedSharedPreferences: true,
        keyCipherAlgorithm: KeyCipherAlgorithm.RSA_ECB_PKCS1Padding,
        storageCipherAlgorithm: StorageCipherAlgorithm.AES_GCM_NoPadding,
      ),
      iOptions: IOSOptions(
        accessibility: KeychainAccessibility.first_unlock_this_device,
        synchronizable: false,
      ),
    );
  }

  /// Initialize the service
  Future<void> initialize({bool useMainnet = false}) async {
    try {
      final rpcUrl = useMainnet ? _mainnetRpcUrl : _sepoliaRpcUrl;
      _provider = JsonRpcProvider(nodeUri: Uri.parse(rpcUrl));
      _isInitialized = true;
      debugPrint('✅ Mobile Starknet service initialized');
    } catch (e) {
      log('❌ Failed to initialize Mobile Starknet service: $e');
      throw MobileStarknetException(
        'Failed to initialize Starknet service: $e',
      );
    }
  }

  /// Create a new wallet with mnemonic
  Future<MobileWalletData> createWallet({
    String? customMnemonic,
    bool enableBiometric = true,
  }) async {
    try {
      _ensureInitialized();

      // Generate mnemonic
      final mnemonic = customMnemonic ?? bip39.generateMnemonic();
      if (!bip39.validateMnemonic(mnemonic)) {
        throw MobileStarknetException('Invalid mnemonic provided');
      }

      // Generate private key from mnemonic
      final privateKey = _generatePrivateKeyFromMnemonic(mnemonic);

      // Create mock address for testing (in production this would use Starknet SDK)
      final address = _generateMockAddress(privateKey);
      final publicKey = _generateMockPublicKey(privateKey);

      // Store wallet data
      await _storeWalletData(
        privateKey: privateKey,
        address: address,
        mnemonic: mnemonic,
        accountType: AccountType.fresh,
      );

      debugPrint('✅ Mobile wallet created successfully');
      return MobileWalletData(
        address: address,
        privateKey: privateKey,
        mnemonic: mnemonic,
        accountType: AccountType.fresh,
        publicKey: publicKey,
      );
    } catch (e) {
      log('❌ Failed to create mobile wallet: $e');
      throw MobileStarknetException('Failed to create wallet: $e');
    }
  }

  /// Import wallet from private key
  Future<MobileWalletData> importFromPrivateKey({
    required String privateKey,
    bool enableBiometric = true,
  }) async {
    try {
      _ensureInitialized();

      // Validate private key format
      if (!privateKey.startsWith('0x') || privateKey.length != 66) {
        throw MobileStarknetException('Invalid private key format');
      }

      final address = _generateMockAddress(privateKey);
      final publicKey = _generateMockPublicKey(privateKey);

      await _storeWalletData(
        privateKey: privateKey,
        address: address,
        accountType: AccountType.imported,
      );

      return MobileWalletData(
        address: address,
        privateKey: privateKey,
        mnemonic: null,
        accountType: AccountType.imported,
        publicKey: publicKey,
      );
    } catch (e) {
      log('❌ Failed to import from private key: $e');
      throw MobileStarknetException('Failed to import from private key: $e');
    }
  }

  /// Import wallet from mnemonic
  Future<MobileWalletData> importFromMnemonic({
    required String mnemonic,
    bool enableBiometric = true,
  }) async {
    try {
      _ensureInitialized();

      if (!bip39.validateMnemonic(mnemonic)) {
        throw MobileStarknetException('Invalid mnemonic phrase');
      }

      final privateKey = _generatePrivateKeyFromMnemonic(mnemonic);
      final address = _generateMockAddress(privateKey);
      final publicKey = _generateMockPublicKey(privateKey);

      await _storeWalletData(
        privateKey: privateKey,
        address: address,
        mnemonic: mnemonic,
        accountType: AccountType.imported,
      );

      return MobileWalletData(
        address: address,
        privateKey: privateKey,
        mnemonic: mnemonic,
        accountType: AccountType.imported,
        publicKey: publicKey,
      );
    } catch (e) {
      log('❌ Failed to import from mnemonic: $e');
      throw MobileStarknetException('Failed to import from mnemonic: $e');
    }
  }

  /// Import from Web3Auth
  Future<MobileWalletData> importFromWeb3Auth({
    required String privateKey,
    required Map<String, dynamic> userInfo,
    bool enableBiometric = true,
  }) async {
    try {
      final walletData = await importFromPrivateKey(
        privateKey: privateKey,
        enableBiometric: enableBiometric,
      );

      // Store additional social login metadata
      await _secureStorage.write(
        key: '${_storagePrefix}social_info',
        value: jsonEncode(userInfo),
      );

      return walletData.copyWith(accountType: AccountType.social);
    } catch (e) {
      log('❌ Failed to import from Web3Auth: $e');
      throw MobileStarknetException('Failed to import from Web3Auth: $e');
    }
  }

  /// Get stored wallet data
  Future<MobileWalletData?> getStoredWallet() async {
    try {
      final privateKey = await _secureStorage.read(key: _privateKeyKey);
      final address = await _secureStorage.read(key: _addressKey);
      final mnemonic = await _secureStorage.read(key: _mnemonicKey);
      final accountTypeStr = await _secureStorage.read(key: _accountTypeKey);

      if (privateKey == null || address == null || accountTypeStr == null) {
        return null;
      }

      final accountType = AccountType.values.firstWhere(
        (type) => type.name == accountTypeStr,
        orElse: () => AccountType.fresh,
      );

      final publicKey = _generateMockPublicKey(privateKey);

      return MobileWalletData(
        address: address,
        privateKey: privateKey,
        mnemonic: mnemonic,
        accountType: accountType,
        publicKey: publicKey,
      );
    } catch (e) {
      log('❌ Failed to get stored wallet: $e');
      return null;
    }
  }

  /// Sign typed data for Extended Exchange API
  Future<List<String>> signTypedData(Map<String, dynamic> typedData) async {
    try {
      _ensureInitialized();

      // For MVP, generate a mock signature
      // In production, this would use proper Starknet signature
      final dataString = jsonEncode(typedData);
      final timestamp = DateTime.now().millisecondsSinceEpoch.toString();

      return [
        '0x${dataString.hashCode.abs().toRadixString(16)}',
        '0x${timestamp.hashCode.abs().toRadixString(16)}',
      ];
    } catch (e) {
      log('❌ Failed to sign typed data: $e');
      throw MobileStarknetException('Failed to sign typed data: $e');
    }
  }

  /// Get account balance (mock for MVP)
  Future<BigInt> getBalance([String? tokenAddress]) async {
    try {
      _ensureInitialized();
      // Return mock balance for testing
      return BigInt.from(1000000000000000000); // 1 ETH in wei
    } catch (e) {
      log('❌ Failed to get balance: $e');
      return BigInt.zero;
    }
  }

  /// Clear stored wallet data
  Future<void> clearWallet() async {
    try {
      await _secureStorage.delete(key: _privateKeyKey);
      await _secureStorage.delete(key: _addressKey);
      await _secureStorage.delete(key: _mnemonicKey);
      await _secureStorage.delete(key: _accountTypeKey);
      await _secureStorage.delete(key: '${_storagePrefix}social_info');

      debugPrint('✅ Wallet data cleared');
    } catch (e) {
      log('❌ Failed to clear wallet: $e');
    }
  }

  /// Check if service is initialized
  bool get isInitialized => _isInitialized;

  // Private helper methods

  String _generatePrivateKeyFromMnemonic(String mnemonic) {
    final seed = bip39.mnemonicToSeed(mnemonic);
    final root = bip32.BIP32.fromSeed(seed);
    final child = root.derivePath("m/44'/9004'/0'/0/0");
    final privateKeyBytes = child.privateKey!;
    final privateKeyBigInt = _bytesToBigInt(privateKeyBytes);
    return '0x${privateKeyBigInt.toRadixString(16).padLeft(64, '0')}';
  }

  String _generateMockAddress(String privateKey) {
    // Generate deterministic mock address from private key
    final hash = privateKey.hashCode.abs();
    return '0x${hash.toRadixString(16).padLeft(64, '0')}';
  }

  String _generateMockPublicKey(String privateKey) {
    // Generate deterministic mock public key from private key
    final hash = (privateKey.hashCode.abs() * 2).toRadixString(16);
    return '0x${hash.padLeft(64, '0')}';
  }

  Future<void> _storeWalletData({
    required String privateKey,
    required String address,
    String? mnemonic,
    required AccountType accountType,
  }) async {
    await _secureStorage.write(key: _privateKeyKey, value: privateKey);
    await _secureStorage.write(key: _addressKey, value: address);
    await _secureStorage.write(key: _accountTypeKey, value: accountType.name);

    if (mnemonic != null) {
      await _secureStorage.write(key: _mnemonicKey, value: mnemonic);
    }
  }

  BigInt _bytesToBigInt(Uint8List bytes) {
    BigInt result = BigInt.zero;
    for (int byte in bytes) {
      result = (result << 8) + BigInt.from(byte);
    }
    return result;
  }

  void _ensureInitialized() {
    if (!_isInitialized) {
      throw MobileStarknetException(
        'Service not initialized. Call initialize() first.',
      );
    }
  }
}

/// Wallet data model
class MobileWalletData {
  final String address;
  final String privateKey;
  final String? mnemonic;
  final AccountType accountType;
  final String publicKey;

  const MobileWalletData({
    required this.address,
    required this.privateKey,
    this.mnemonic,
    required this.accountType,
    required this.publicKey,
  });

  MobileWalletData copyWith({
    String? address,
    String? privateKey,
    String? mnemonic,
    AccountType? accountType,
    String? publicKey,
  }) {
    return MobileWalletData(
      address: address ?? this.address,
      privateKey: privateKey ?? this.privateKey,
      mnemonic: mnemonic ?? this.mnemonic,
      accountType: accountType ?? this.accountType,
      publicKey: publicKey ?? this.publicKey,
    );
  }

  Map<String, dynamic> toJson() => {
    'address': address,
    'privateKey': privateKey,
    'mnemonic': mnemonic,
    'accountType': accountType.name,
    'publicKey': publicKey,
  };

  factory MobileWalletData.fromJson(Map<String, dynamic> json) =>
      MobileWalletData(
        address: json['address'],
        privateKey: json['privateKey'],
        mnemonic: json['mnemonic'],
        accountType: AccountType.values.firstWhere(
          (type) => type.name == json['accountType'],
          orElse: () => AccountType.fresh,
        ),
        publicKey: json['publicKey'],
      );
}

/// Account creation methods
enum AccountType { fresh, imported, social }

/// Exception for mobile Starknet operations
class MobileStarknetException implements Exception {
  final String message;

  MobileStarknetException(this.message);

  @override
  String toString() => 'MobileStarknetException: $message';
}
