import 'dart:convert';

/// Account Registration Model for EIP-712 signing
/// Matches the Python SDK's AccountRegistration class
class AccountRegistration {
  final int accountIndex;
  final String wallet;
  final bool tosAccepted;
  final String time;
  final String action;
  final String host;

  AccountRegistration({
    required this.accountIndex,
    required this.wallet,
    required this.tosAccepted,
    required this.time,
    required this.action,
    required this.host,
  });

  Map<String, dynamic> toJson() {
    return {
      'accountIndex': accountIndex,
      'wallet': wallet,
      'tosAccepted': tosAccepted,
      'time': time,
      'action': action,
      'host': host,
    };
  }

  @override
  String toString() => 'AccountRegistration(wallet: $wallet, action: $action)';
}

/// Onboarding Payload for Extended Exchange registration
/// Matches the Python SDK's OnboardingPayLoad class
class OnboardingPayload {
  final String l1Signature;
  final String l2Key;
  final Map<String, String> l2Signature;
  final AccountRegistration accountRegistration;
  final String? referralCode;

  OnboardingPayload({
    required this.l1Signature,
    required this.l2Key,
    required this.l2Signature,
    required this.accountRegistration,
    this.referralCode,
  });

  Map<String, dynamic> toJson() {
    return {
      'l1Signature': l1Signature,
      'l2Key': l2Key,
      'l2Signature': l2Signature,
      'accountCreation': accountRegistration.toJson(),
      'referralCode': referralCode,
    };
  }

  String toJsonString() => json.encode(toJson());

  @override
  String toString() => 'OnboardingPayload(l2Key: ${l2Key.substring(0, 10)}...)';
}

/// Onboarded Client Model from Extended Exchange response
/// Matches the Python SDK's OnboardedClientModel class
class OnboardedClientModel {
  final ExtendedExchangeAccountModel defaultAccount;

  OnboardedClientModel({required this.defaultAccount});

  factory OnboardedClientModel.fromJson(Map<String, dynamic> json) {
    return OnboardedClientModel(
      defaultAccount: ExtendedExchangeAccountModel.fromJson(
        json['defaultAccount'],
      ),
    );
  }

  @override
  String toString() => 'OnboardedClientModel(account: ${defaultAccount.id})';
}

/// Extended Exchange Account Model
/// Matches the Python SDK's AccountModel class
class ExtendedExchangeAccountModel {
  final int id;
  final int accountIndex;
  final int l2Vault;
  final String status;
  final String createdAt;
  final String updatedAt;

  ExtendedExchangeAccountModel({
    required this.id,
    required this.accountIndex,
    required this.l2Vault,
    required this.status,
    required this.createdAt,
    required this.updatedAt,
  });

  factory ExtendedExchangeAccountModel.fromJson(Map<String, dynamic> json) {
    return ExtendedExchangeAccountModel(
      id: json['id'],
      accountIndex: json['accountIndex'],
      l2Vault: json['l2Vault'],
      status: json['status'],
      createdAt: json['createdAt'],
      updatedAt: json['updatedAt'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'accountIndex': accountIndex,
      'l2Vault': l2Vault,
      'status': status,
      'createdAt': createdAt,
      'updatedAt': updatedAt,
    };
  }

  @override
  String toString() => 'ExtendedExchangeAccount(id: $id, vault: $l2Vault)';
}

/// Complete Onboarded Account with L2 credentials
/// Matches the Python SDK's OnBoardedAccount class
class OnboardedAccount {
  final ExtendedExchangeAccountModel account;
  final StarkKeyPair l2KeyPair;
  final String? tradingApiKey;

  OnboardedAccount({
    required this.account,
    required this.l2KeyPair,
    this.tradingApiKey,
  });

  // Convenience getters
  int get l2Vault => account.l2Vault;
  String get l2PrivateKey => l2KeyPair.privateHex;
  String get l2PublicKey => l2KeyPair.publicHex;

  Map<String, dynamic> toJson() {
    return {
      'account': account.toJson(),
      'l2KeyPair': {
        'private': l2KeyPair.privateHex,
        'public': l2KeyPair.publicHex,
      },
      'tradingApiKey': tradingApiKey,
    };
  }

  factory OnboardedAccount.fromJson(Map<String, dynamic> json) {
    return OnboardedAccount(
      account: ExtendedExchangeAccountModel.fromJson(json['account']),
      l2KeyPair: StarkKeyPair(
        private: BigInt.parse(
          json['l2KeyPair']['private'].substring(2),
          radix: 16,
        ),
        public: BigInt.parse(
          json['l2KeyPair']['public'].substring(2),
          radix: 16,
        ),
      ),
      tradingApiKey: json['tradingApiKey'],
    );
  }

  @override
  String toString() =>
      'OnboardedAccount(vault: $l2Vault, apiKey: ${tradingApiKey?.substring(0, 8) ?? 'none'}...)';
}

/// StarkNet Key Pair for L2 operations
class StarkKeyPair {
  final BigInt private;
  final BigInt public;

  StarkKeyPair({required this.private, required this.public});

  String get privateHex => '0x${private.toRadixString(16).padLeft(64, '0')}';
  String get publicHex => '0x${public.toRadixString(16).padLeft(64, '0')}';

  Map<String, dynamic> toJson() {
    return {'private': privateHex, 'public': publicHex};
  }

  @override
  String toString() =>
      'StarkKeyPair(private: ${privateHex.substring(0, 10)}..., public: $publicHex)';
}

/// API Key Request Model for trading key generation
class ApiKeyRequestModel {
  final String description;

  ApiKeyRequestModel({required this.description});

  Map<String, dynamic> toJson() {
    return {'description': description};
  }
}

/// API Key Response Model from Extended Exchange
class ApiKeyResponseModel {
  final String key;
  final String description;
  final String createdAt;

  ApiKeyResponseModel({
    required this.key,
    required this.description,
    required this.createdAt,
  });

  factory ApiKeyResponseModel.fromJson(Map<String, dynamic> json) {
    return ApiKeyResponseModel(
      key: json['key'],
      description: json['description'],
      createdAt: json['createdAt'],
    );
  }

  @override
  String toString() =>
      'ApiKeyResponse(key: ${key.substring(0, 8)}..., desc: $description)';
}

/// Extended Exchange Configuration Constants
class ExtendedExchangeConfig {
  // StarkNet Sepolia Extended Exchange endpoints
  static const String STARKNET_SEPOLIA_API =
      'https://api.starknet.sepolia.extended.exchange/api/v1';
  static const String STARKNET_SEPOLIA_ONBOARDING =
      'https://api.starknet.sepolia.extended.exchange';
  static const String STARKNET_SEPOLIA_STREAM =
      'wss://starknet.sepolia.extended.exchange/stream.extended.exchange/v1';
  static const String SIGNING_DOMAIN = 'starknet.sepolia.extended.exchange';

  // Actions for account registration
  static const String REGISTER_ACTION = 'REGISTER';
  static const String CREATE_SUB_ACCOUNT_ACTION = 'CREATE_SUB_ACCOUNT';

  // Collateral configuration
  static const int COLLATERAL_DECIMALS = 6;

  /// Full StarkNet Sepolia configuration
  static const Map<String, dynamic> STARKNET_SEPOLIA_CONFIG = {
    'api_base_url': STARKNET_SEPOLIA_API,
    'stream_url': STARKNET_SEPOLIA_STREAM,
    'onboarding_url': STARKNET_SEPOLIA_ONBOARDING,
    'signing_domain': SIGNING_DOMAIN,
    'collateral_asset_contract': '',
    'asset_operations_contract': '',
    'collateral_asset_on_chain_id': '',
    'collateral_decimals': COLLATERAL_DECIMALS,
  };
}

/// Onboarding Exception for error handling
class OnboardingException implements Exception {
  final String message;
  final int? statusCode;
  final String? response;

  OnboardingException(this.message, {this.statusCode, this.response});

  @override
  String toString() =>
      'OnboardingException: $message${statusCode != null ? ' (Status: $statusCode)' : ''}';
}

/// Sub-account creation exception
class SubAccountExistsException extends OnboardingException {
  SubAccountExistsException(String message) : super(message);
}
