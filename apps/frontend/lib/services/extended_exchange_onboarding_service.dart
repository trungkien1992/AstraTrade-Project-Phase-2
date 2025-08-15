import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:starknet/starknet.dart';
import 'package:astratrade_app/models/extended_exchange_onboarding_models.dart';
import 'package:astratrade_app/services/extended_exchange_l2_key_service.dart';
import 'package:astratrade_app/utils/extended_exchange_crypto_utils.dart';

/// Extended Exchange Onboarding Service
/// Implements the complete onboarding flow from x10xchange-python_sdk
class ExtendedExchangeOnboardingService {
  static const Duration _httpTimeout = Duration(seconds: 30);

  /// Complete onboarding process for Extended Exchange trading
  /// Matches the Python SDK's UserClient.onboard() method
  static Future<OnboardedAccount> onboardAccount({
    required String l1PrivateKey,
    required String l1Address,
    String? referralCode,
  }) async {
    print('🚀 Starting Extended Exchange onboarding process');
    print('   L1 Address: $l1Address');
    print('   Referral Code: ${referralCode ?? 'none'}');

    try {
      // Step 1: Derive L2 keys from L1 private key
      print('🔑 Step 1: Deriving L2 keys...');
      final l2KeyPair = await ExtendedExchangeL2KeyService.deriveL2Keys(
        l1PrivateKey: l1PrivateKey,
        l1Address: l1Address,
        accountIndex: 0,
        signingDomain: ExtendedExchangeConfig.SIGNING_DOMAIN,
      );

      // Step 2: Create onboarding payload
      print('📋 Step 2: Creating onboarding payload...');
      final onboardingPayload = await _createOnboardingPayload(
        l1PrivateKey: l1PrivateKey,
        l1Address: l1Address,
        l2KeyPair: l2KeyPair,
        referralCode: referralCode,
      );

      // Step 3: Submit onboarding request to Extended Exchange
      print('📡 Step 3: Submitting onboarding request...');
      final onboardedClient = await _submitOnboardingRequest(onboardingPayload);

      // Step 4: Create trading API key
      print('🔐 Step 4: Creating trading API key...');
      final tradingApiKey = await _createTradingApiKey(
        account: onboardedClient.defaultAccount,
        l1PrivateKey: l1PrivateKey,
        l1Address: l1Address,
      );

      // Step 5: Return complete onboarded account
      final onboardedAccount = OnboardedAccount(
        account: onboardedClient.defaultAccount,
        l2KeyPair: l2KeyPair,
        tradingApiKey: tradingApiKey,
      );

      print('✅ Onboarding completed successfully!');
      print('   Vault ID: ${onboardedAccount.l2Vault}');
      print('   Trading API Key: ${tradingApiKey.substring(0, 8)}...');

      return onboardedAccount;
    } catch (e, stackTrace) {
      print('❌ Onboarding failed: $e');
      print('Stack trace: $stackTrace');

      if (e is OnboardingException) {
        rethrow;
      } else {
        throw OnboardingException('Onboarding process failed: $e');
      }
    }
  }

  /// Create onboarding payload with signatures
  /// Matches the Python SDK's get_onboarding_payload function
  static Future<OnboardingPayload> _createOnboardingPayload({
    required String l1PrivateKey,
    required String l1Address,
    required StarkKeyPair l2KeyPair,
    String? referralCode,
  }) async {
    print('📝 Creating onboarding payload...');

    // Current timestamp for registration
    final now = DateTime.now().toUtc();
    final timeString = now
        .toIso8601String()
        .replaceAll('T', 'T')
        .replaceAll('Z', 'Z');

    // Create account registration struct
    final accountRegistration = AccountRegistration(
      accountIndex: 0,
      wallet: l1Address.toLowerCase(),
      tosAccepted: true,
      time: timeString,
      action: ExtendedExchangeConfig.REGISTER_ACTION,
      host: ExtendedExchangeConfig.STARKNET_SEPOLIA_ONBOARDING,
    );

    // Create EIP-712 registration message
    final registrationStruct =
        ExtendedExchangeCryptoUtils.createAccountRegistrationStruct(
          accountIndex: 0,
          walletAddress: l1Address,
          timeString: timeString,
          action: ExtendedExchangeConfig.REGISTER_ACTION,
          host: ExtendedExchangeConfig.STARKNET_SEPOLIA_ONBOARDING,
          signingDomain: ExtendedExchangeConfig.SIGNING_DOMAIN,
        );

    // Sign registration payload with L1 key
    final l1Signature = ExtendedExchangeCryptoUtils.signEIP712Message(
      message: registrationStruct,
      privateKey: l1PrivateKey,
    );

    print('✍️ L1 signature generated');

    // Create L2 signature using Pedersen hash
    final l1AddressInt = BigInt.parse(l1Address.substring(2), radix: 16);
    final l2Message = pedersenHash(l1AddressInt, l2KeyPair.public);

    final l2Signature = ExtendedExchangeCryptoUtils.generateStarkNetSignature(
      messageHash: l2Message,
      privateKey: l2KeyPair.private,
    );

    print('✍️ L2 signature generated');

    // Create complete onboarding payload
    final payload = OnboardingPayload(
      l1Signature: l1Signature,
      l2Key: l2KeyPair.publicHex,
      l2Signature: {
        'r': '0x${l2Signature['r']!.toRadixString(16)}',
        's': '0x${l2Signature['s']!.toRadixString(16)}',
      },
      accountRegistration: accountRegistration,
      referralCode: referralCode,
    );

    print('✅ Onboarding payload created');
    return payload;
  }

  /// Submit onboarding request to Extended Exchange
  static Future<OnboardedClientModel> _submitOnboardingRequest(
    OnboardingPayload payload,
  ) async {
    print('📡 Submitting onboarding request to Extended Exchange...');

    final url =
        '${ExtendedExchangeConfig.STARKNET_SEPOLIA_ONBOARDING}/auth/onboard';
    print('   URL: $url');

    try {
      final response = await http
          .post(
            Uri.parse(url),
            headers: {
              'Content-Type': 'application/json',
              'User-Agent': 'AstraTrade/1.0',
            },
            body: payload.toJsonString(),
          )
          .timeout(_httpTimeout);

      print('📊 Response status: ${response.statusCode}');
      print('📄 Response body length: ${response.body.length}');

      if (response.statusCode == 200 || response.statusCode == 201) {
        final responseData = json.decode(response.body);

        if (responseData['data'] != null) {
          final onboardedClient = OnboardedClientModel.fromJson(
            responseData['data'],
          );
          print('✅ Account onboarded successfully');
          print('   Account ID: ${onboardedClient.defaultAccount.id}');
          print('   Vault ID: ${onboardedClient.defaultAccount.l2Vault}');

          return onboardedClient;
        } else {
          throw OnboardingException('No account data returned from onboarding');
        }
      } else {
        print('❌ Onboarding request failed');
        print('Response body: ${response.body}');

        throw OnboardingException(
          'Onboarding request failed',
          statusCode: response.statusCode,
          response: response.body,
        );
      }
    } catch (e) {
      if (e is OnboardingException) {
        rethrow;
      } else {
        throw OnboardingException('Network error during onboarding: $e');
      }
    }
  }

  /// Create trading API key for onboarded account
  /// Matches the Python SDK's create_account_api_key method
  static Future<String> _createTradingApiKey({
    required ExtendedExchangeAccountModel account,
    required String l1PrivateKey,
    required String l1Address,
  }) async {
    print('🔐 Creating trading API key...');

    final requestPath = '/api/v1/user/account/api-key';
    final description =
        'AstraTrade Trading Key - ${DateTime.now().toIso8601String()}';

    // Create authentication headers
    final now = DateTime.now().toUtc();
    final authTimeString = now
        .toIso8601String()
        .replaceAll('T', 'T')
        .replaceAll('Z', 'Z');
    final l1Message = '$requestPath@$authTimeString';

    // Sign authentication message
    final l1MessageBytes = utf8.encode(l1Message);
    final l1Signature = ExtendedExchangeCryptoUtils.signEIP712Message(
      message: {
        'types': {
          'EIP712Domain': [
            {'name': 'name', 'type': 'string'},
          ],
          'Message': [
            {'name': 'content', 'type': 'string'},
          ],
        },
        'domain': {'name': 'Extended Exchange'},
        'primaryType': 'Message',
        'message': {'content': l1Message},
      },
      privateKey: l1PrivateKey,
    );

    final url =
        '${ExtendedExchangeConfig.STARKNET_SEPOLIA_ONBOARDING}$requestPath';

    try {
      final response = await http
          .post(
            Uri.parse(url),
            headers: {
              'Content-Type': 'application/json',
              'L1_SIGNATURE': l1Signature,
              'L1_MESSAGE_TIME': authTimeString,
              'X-X10-ACTIVE-ACCOUNT': account.id.toString(),
              'User-Agent': 'AstraTrade/1.0',
            },
            body: json.encode(
              ApiKeyRequestModel(description: description).toJson(),
            ),
          )
          .timeout(_httpTimeout);

      print('📊 API key response status: ${response.statusCode}');

      if (response.statusCode == 200 || response.statusCode == 201) {
        final responseData = json.decode(response.body);

        if (responseData['data'] != null) {
          final apiKeyResponse = ApiKeyResponseModel.fromJson(
            responseData['data'],
          );
          print('✅ Trading API key created successfully');
          print('   Key: ${apiKeyResponse.key.substring(0, 8)}...');

          return apiKeyResponse.key;
        } else {
          throw OnboardingException('No API key data returned');
        }
      } else {
        print('❌ API key creation failed');
        print('Response body: ${response.body}');

        throw OnboardingException(
          'Failed to create trading API key',
          statusCode: response.statusCode,
          response: response.body,
        );
      }
    } catch (e) {
      if (e is OnboardingException) {
        rethrow;
      } else {
        throw OnboardingException('Network error creating API key: $e');
      }
    }
  }

  /// Get existing accounts for L1 address
  static Future<List<OnboardedAccount>> getExistingAccounts({
    required String l1PrivateKey,
    required String l1Address,
  }) async {
    print('📋 Getting existing accounts...');

    final requestPath = '/api/v1/user/accounts';

    // Create authentication headers
    final now = DateTime.now().toUtc();
    final authTimeString = now
        .toIso8601String()
        .replaceAll('T', 'T')
        .replaceAll('Z', 'Z');
    final l1Message = '$requestPath@$authTimeString';

    // Sign authentication message
    final l1Signature = ExtendedExchangeCryptoUtils.signEIP712Message(
      message: {
        'types': {
          'EIP712Domain': [
            {'name': 'name', 'type': 'string'},
          ],
          'Message': [
            {'name': 'content', 'type': 'string'},
          ],
        },
        'domain': {'name': 'Extended Exchange'},
        'primaryType': 'Message',
        'message': {'content': l1Message},
      },
      privateKey: l1PrivateKey,
    );

    final url =
        '${ExtendedExchangeConfig.STARKNET_SEPOLIA_ONBOARDING}$requestPath';

    try {
      final response = await http
          .get(
            Uri.parse(url),
            headers: {
              'L1_SIGNATURE': l1Signature,
              'L1_MESSAGE_TIME': authTimeString,
              'User-Agent': 'AstraTrade/1.0',
            },
          )
          .timeout(_httpTimeout);

      if (response.statusCode == 200) {
        final responseData = json.decode(response.body);
        final accounts = <OnboardedAccount>[];

        if (responseData['data'] != null) {
          for (final accountData in responseData['data']) {
            final account = ExtendedExchangeAccountModel.fromJson(accountData);

            // Derive L2 keys for each account
            final l2KeyPair = await ExtendedExchangeL2KeyService.deriveL2Keys(
              l1PrivateKey: l1PrivateKey,
              l1Address: l1Address,
              accountIndex: account.accountIndex,
              signingDomain: ExtendedExchangeConfig.SIGNING_DOMAIN,
            );

            accounts.add(
              OnboardedAccount(account: account, l2KeyPair: l2KeyPair),
            );
          }
        }

        print('✅ Found ${accounts.length} existing accounts');
        return accounts;
      } else {
        print('❌ Failed to get existing accounts: ${response.statusCode}');
        return [];
      }
    } catch (e) {
      print('❌ Error getting existing accounts: $e');
      return [];
    }
  }

  /// Test onboarding service with demo credentials
  static Future<bool> testOnboarding() async {
    print('🧪 Testing onboarding service...');

    // Use demo credentials for testing
    const testPrivateKey =
        '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef';
    const testAddress = '0x742d35Cc6634C0532925a3b8D0C2A2b8E85b3b6b';

    try {
      // Test L2 key derivation
      final l2Keys = await ExtendedExchangeL2KeyService.deriveL2Keys(
        l1PrivateKey: testPrivateKey,
        l1Address: testAddress,
        accountIndex: 0,
        signingDomain: ExtendedExchangeConfig.SIGNING_DOMAIN,
      );

      print('✅ L2 key derivation test passed');

      // Test payload creation (without submitting)
      final payload = await _createOnboardingPayload(
        l1PrivateKey: testPrivateKey,
        l1Address: testAddress,
        l2KeyPair: l2Keys,
      );

      print('✅ Onboarding payload creation test passed');
      print('   Payload size: ${payload.toJsonString().length} bytes');

      return true;
    } catch (e) {
      print('❌ Onboarding service test failed: $e');
      return false;
    }
  }
}
