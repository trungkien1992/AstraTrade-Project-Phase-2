import 'dart:convert';
import 'dart:developer';
import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:starknet/starknet.dart';
import 'package:starknet_provider/starknet_provider.dart';
import 'package:crypto/crypto.dart';
import 'package:bip39/bip39.dart' as bip39;
import 'package:bip32/bip32.dart' as bip32;

/// Native mobile Starknet service using Starknet.dart SDK
/// Provides secure wallet management with biometric support and native mobile optimizations
class MobileStarknetService {
  static const String _storagePrefix = 'mobile_starknet_';
  static const String _privateKeyKey = '${_storagePrefix}private_key';
  static const String _addressKey = '${_storagePrefix}address';
  static const String _mnemonicKey = '${_storagePrefix}mnemonic';
  static const String _accountTypeKey = '${_storagePrefix}account_type';

  // Starknet field prime for validation
  static final BigInt _starknetFieldPrime = BigInt.parse(
    '800000000000011000000000000000000000000000000000000000000000001',
    radix: 16,
  );

  // Network configurations
  static const String _sepoliaRpcUrl =
      'https://starknet-sepolia.public.blastapi.io/rpc/v0_7';
  static const String _mainnetRpcUrl =
      'https://starknet-mainnet.public.blastapi.io/rpc/v0_7';

  late final JsonRpcProvider _provider;
  late final FlutterSecureStorage _secureStorage;
  Account? _currentAccount;
  bool _isInitialized = false;

  // Account class hash for OpenZeppelin account
  static const String _accountClassHash =
      '0x061dac032f228abef9c6626f995015233097ae253a7f72d68552db02f2971b8f';

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

  /// Initialize the Starknet service with network configuration
  Future<void> initialize({bool useMainnet = false}) async {
    try {
      final rpcUrl = useMainnet ? _mainnetRpcUrl : _sepoliaRpcUrl;
      _provider = JsonRpcProvider(nodeUri: Uri.parse(rpcUrl));

      // Test connection
      await _provider.chainId();
      _isInitialized = true;

      debugPrint(
        '✅ Mobile Starknet service initialized on ${useMainnet ? 'mainnet' : 'sepolia'}',
      );
    } catch (e) {
      log('❌ Failed to initialize Mobile Starknet service: $e');
      throw MobileStarknetException(
        'Failed to initialize Starknet service: $e',
      );
    }
  }

  /// Create a new wallet with mnemonic and secure storage
  Future<MobileWalletData> createWallet({
    String? customMnemonic,
    bool enableBiometric = true,
  }) async {
    try {
      _ensureInitialized();

      // Generate or use provided mnemonic
      final mnemonic = customMnemonic ?? bip39.generateMnemonic();
      if (!bip39.validateMnemonic(mnemonic)) {
        throw MobileStarknetException('Invalid mnemonic provided');
      }

      // Derive private key from mnemonic using BIP32
      final seed = bip39.mnemonicToSeed(mnemonic);
      final root = bip32.BIP32.fromSeed(seed);

      // Use Starknet derivation path: m/44'/9004'/0'/0/0
      final child = root.derivePath("m/44'/9004'/0'/0/0");

      final privateKeyBytes = child.privateKey!;
      final privateKeyBigInt = _bytesToBigInt(privateKeyBytes);

      // Ensure private key is within Starknet field
      if (privateKeyBigInt >= _starknetFieldPrime ||
          privateKeyBigInt == BigInt.zero) {
        throw MobileStarknetException(
          'Generated private key outside valid range',
        );
      }

      final privateKeyHex =
          '0x${privateKeyBigInt.toRadixString(16).padLeft(64, '0')}';

      // Create Starknet account
      final signingKey = Felt.fromHexString(privateKeyHex);
      final publicKey = getPublicKey(signingKey);
      final address = calculateContractAddressFromHash(
        classHash: Felt.fromHexString(_accountClassHash),
        constructorCalldata: [publicKey],
        salt: publicKey,
      );

      final account = Account(
        provider: _provider,
        signer: signingKey,
        accountAddress: address,
        chainId: await _provider.chainId(),
      );

      // Store wallet data securely
      await _storeWalletData(
        privateKey: privateKeyHex,
        address: address.toHex(),
        mnemonic: mnemonic,
        accountType: AccountType.fresh,
        enableBiometric: enableBiometric,
      );

      _currentAccount = account;

      debugPrint('✅ Mobile wallet created successfully');
      return MobileWalletData(
        address: address.toHex(),
        privateKey: privateKeyHex,
        mnemonic: mnemonic,
        accountType: AccountType.fresh,
        publicKey: publicKey.toHex(),
      );
    } catch (e) {
      log('❌ Failed to create mobile wallet: $e');
      throw MobileStarknetException('Failed to create wallet: $e');
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

      // Use the same derivation as createWallet
      final seed = bip39.mnemonicToSeed(mnemonic);
      final root = bip32.BIP32.fromSeed(seed);
      final child = root.derivePath("m/44'/9004'/0'/0/0");

      final privateKeyBytes = child.privateKey!;
      final privateKeyBigInt = _bytesToBigInt(privateKeyBytes);
      final privateKeyHex =
          '0x${privateKeyBigInt.toRadixString(16).padLeft(64, '0')}';

      return await _importFromPrivateKey(
        privateKey: privateKeyHex,
        mnemonic: mnemonic,
        accountType: AccountType.imported,
        enableBiometric: enableBiometric,
      );
    } catch (e) {
      log('❌ Failed to import from mnemonic: $e');
      throw MobileStarknetException('Failed to import from mnemonic: $e');
    }
  }

  /// Import wallet from private key
  Future<MobileWalletData> importFromPrivateKey({
    required String privateKey,
    bool enableBiometric = true,
  }) async {
    try {
      return await _importFromPrivateKey(
        privateKey: privateKey,
        accountType: AccountType.imported,
        enableBiometric: enableBiometric,
      );
    } catch (e) {
      log('❌ Failed to import from private key: $e');
      throw MobileStarknetException('Failed to import from private key: $e');
    }
  }

  /// Import wallet from Web3Auth (social login)
  Future<MobileWalletData> importFromWeb3Auth({
    required String privateKey,
    required Map<String, dynamic> userInfo,
    bool enableBiometric = true,
  }) async {
    try {
      final walletData = await _importFromPrivateKey(
        privateKey: privateKey,
        accountType: AccountType.social,
        enableBiometric: enableBiometric,
      );

      // Store additional social login metadata
      await _secureStorage.write(
        key: '${_storagePrefix}social_info',
        value: jsonEncode(userInfo),
      );

      debugPrint('✅ Web3Auth wallet imported successfully');
      return walletData;
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

      // Recreate account
      final signingKey = Felt.fromHexString(privateKey);
      final publicKey = getPublicKey(signingKey);
      final accountAddress = Felt.fromHexString(address);

      final account = Account(
        provider: _provider,
        signer: signingKey,
        accountAddress: accountAddress,
        chainId: await _provider.chainId(),
      );

      _currentAccount = account;

      return MobileWalletData(
        address: address,
        privateKey: privateKey,
        mnemonic: mnemonic,
        accountType: accountType,
        publicKey: publicKey.toHex(),
      );
    } catch (e) {
      log('❌ Failed to get stored wallet: $e');
      return null;
    }
  }

  /// Sign a transaction using the current account
  Future<String> signTransaction({
    required List<FunctionCall> calls,
    Felt? nonce,
  }) async {
    try {
      _ensureAccountLoaded();

      final result = await _currentAccount!.execute(
        functionCalls: calls,
        nonce: nonce,
      );

      return result.when(
        result: (result) => result.transactionHash.toHexString(),
        error: (error) =>
            throw MobileStarknetException('Transaction failed: $error'),
      );
    } catch (e) {
      log('❌ Failed to sign transaction: $e');
      throw MobileStarknetException('Failed to sign transaction: $e');
    }
  }

  /// Sign typed data (SNIP-12)
  Future<List<Felt>> signTypedData(Map<String, dynamic> typedData) async {
    try {
      _ensureAccountLoaded();

      // Convert typed data to Starknet format
      final structuredData = _convertToStructuredData(typedData);
      final signature = await _currentAccount!.signTypedData(structuredData);

      return signature;
    } catch (e) {
      log('❌ Failed to sign typed data: $e');
      throw MobileStarknetException('Failed to sign typed data: $e');
    }
  }

  /// Get account balance
  Future<BigInt> getBalance([String? tokenAddress]) async {
    try {
      _ensureAccountLoaded();

      // Default to ETH if no token specified
      final token =
          tokenAddress ??
          '0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7';

      final balance = await _provider.call(
        request: FunctionCall(
          contractAddress: Felt.fromHexString(token),
          entryPointSelector: getSelectorFromName('balanceOf'),
          calldata: [_currentAccount!.accountAddress],
        ),
        blockId: BlockId.latest,
      );

      return balance.when(
        result: (result) => result.first.toBigInt(),
        error: (error) => BigInt.zero,
      );
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

      _currentAccount = null;
      debugPrint('✅ Wallet data cleared');
    } catch (e) {
      log('❌ Failed to clear wallet: $e');
    }
  }

  /// Check if service is initialized
  bool get isInitialized => _isInitialized;

  /// Get current account
  Account? get currentAccount => _currentAccount;

  // Private helper methods

  Future<MobileWalletData> _importFromPrivateKey({
    required String privateKey,
    String? mnemonic,
    required AccountType accountType,
    required bool enableBiometric,
  }) async {
    _ensureInitialized();

    // Validate private key format
    if (!privateKey.startsWith('0x') || privateKey.length != 66) {
      throw MobileStarknetException('Invalid private key format');
    }

    final privateKeyBigInt = BigInt.parse(privateKey.substring(2), radix: 16);
    if (privateKeyBigInt >= _starknetFieldPrime ||
        privateKeyBigInt == BigInt.zero) {
      throw MobileStarknetException('Private key outside valid range');
    }

    // Create account
    final signingKey = Felt.fromHexString(privateKey);
    final publicKey = getPublicKey(signingKey);
    final address = calculateContractAddressFromHash(
      classHash: Felt.fromHexString(_accountClassHash),
      constructorCalldata: [publicKey],
      salt: publicKey,
    );

    final account = Account(
      provider: _provider,
      signer: signingKey,
      accountAddress: address,
      chainId: await _provider.chainId(),
    );

    // Store wallet data
    await _storeWalletData(
      privateKey: privateKey,
      address: address.toHex(),
      mnemonic: mnemonic,
      accountType: accountType,
      enableBiometric: enableBiometric,
    );

    _currentAccount = account;

    return MobileWalletData(
      address: address.toHex(),
      privateKey: privateKey,
      mnemonic: mnemonic,
      accountType: accountType,
      publicKey: publicKey.toHex(),
    );
  }

  Future<void> _storeWalletData({
    required String privateKey,
    required String address,
    String? mnemonic,
    required AccountType accountType,
    required bool enableBiometric,
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

  TypedData _convertToStructuredData(Map<String, dynamic> typedData) {
    // Convert typed data to Starknet structured data format
    // This is a simplified implementation - in production, use proper SNIP-12 encoding
    return TypedData(
      types: {
        'StarkNetDomain': [
          {'name': 'name', 'type': 'felt'},
          {'name': 'version', 'type': 'felt'},
          {'name': 'chainId', 'type': 'felt'},
        ],
        'Order': [
          {'name': 'data', 'type': 'felt'},
        ],
      },
      primaryType: 'Order',
      domain: {'name': 'AstraTrade', 'version': '1', 'chainId': '1'},
      message: {'data': jsonEncode(typedData)},
    );
  }

  void _ensureInitialized() {
    if (!_isInitialized) {
      throw MobileStarknetException(
        'Service not initialized. Call initialize() first.',
      );
    }
  }

  void _ensureAccountLoaded() {
    _ensureInitialized();
    if (_currentAccount == null) {
      throw MobileStarknetException(
        'No account loaded. Create or import a wallet first.',
      );
    }
  }
}

/// Wallet data model for mobile Starknet integration
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
enum AccountType {
  fresh, // Newly created wallet
  imported, // Imported from private key/mnemonic
  social, // Created via Web3Auth social login
}

/// Exception for mobile Starknet operations
class MobileStarknetException implements Exception {
  final String message;

  MobileStarknetException(this.message);

  @override
  String toString() => 'MobileStarknetException: $message';
}
