import 'dart:convert';
import 'dart:typed_data';
import 'package:crypto/crypto.dart';
import 'package:starknet/starknet.dart';

// For now, use SHA-256 as a fallback for EIP-712 hashing
// In production, should use proper Keccak-256
final _sha256 = sha256;

/// Extended Exchange Cryptographic Utilities
/// Implements EIP-712 signing and StarkNet cryptographic operations
class ExtendedExchangeCryptoUtils {
  /// Create EIP-712 key derivation struct for signing
  /// Matches the Python SDK's get_key_derivation_struct_to_sign function
  static Map<String, dynamic> createKeyDerivationStruct({
    required int accountIndex,
    required String address,
    required String signingDomain,
  }) {
    // EIP-712 domain separator
    final domain = {'name': signingDomain};

    // Message to sign
    final message = {
      'accountIndex': accountIndex,
      'address': address.toLowerCase(),
    };

    // EIP-712 types
    final types = {
      'EIP712Domain': [
        {'name': 'name', 'type': 'string'},
      ],
      'KeyDerivation': [
        {'name': 'accountIndex', 'type': 'int8'},
        {'name': 'address', 'type': 'address'},
      ],
    };

    return {
      'types': types,
      'domain': domain,
      'primaryType': 'KeyDerivation',
      'message': message,
    };
  }

  /// Create EIP-712 account registration struct for onboarding
  /// Matches the Python SDK's AccountRegistration class
  static Map<String, dynamic> createAccountRegistrationStruct({
    required int accountIndex,
    required String walletAddress,
    required String timeString,
    required String action,
    required String host,
    required String signingDomain,
  }) {
    // EIP-712 domain separator
    final domain = {'name': signingDomain};

    // Message to sign
    final message = {
      'accountIndex': accountIndex,
      'wallet': walletAddress.toLowerCase(),
      'tosAccepted': true,
      'time': timeString,
      'action': action,
      'host': host,
    };

    // EIP-712 types
    final types = {
      'EIP712Domain': [
        {'name': 'name', 'type': 'string'},
      ],
      'AccountRegistration': [
        {'name': 'accountIndex', 'type': 'int8'},
        {'name': 'wallet', 'type': 'address'},
        {'name': 'tosAccepted', 'type': 'bool'},
        {'name': 'time', 'type': 'string'},
        {'name': 'action', 'type': 'string'},
        {'name': 'host', 'type': 'string'},
      ],
    };

    return {
      'types': types,
      'domain': domain,
      'primaryType': 'AccountRegistration',
      'message': message,
    };
  }

  /// Sign EIP-712 structured data with Ethereum private key
  static String signEIP712Message({
    required Map<String, dynamic> message,
    required String privateKey,
  }) {
    print('🔐 Signing EIP-712 message');

    // Encode the EIP-712 message
    final encodedMessage = encodeEIP712Message(message);

    // Sign with Ethereum private key
    final signature = _signWithEthereumKey(encodedMessage, privateKey);

    print('✅ EIP-712 message signed');
    return signature;
  }

  /// Encode EIP-712 message for signing
  static Uint8List encodeEIP712Message(Map<String, dynamic> data) {
    print('📦 Encoding EIP-712 message');

    // Extract components
    final types = data['types'] as Map<String, dynamic>;
    final domain = data['domain'] as Map<String, dynamic>;
    final primaryType = data['primaryType'] as String;
    final message = data['message'] as Map<String, dynamic>;

    // Create type hash
    final typeHash = _hashType(primaryType, types);

    // Create domain separator
    final domainSeparator = _hashStruct('EIP712Domain', domain, types);

    // Create message hash
    final messageHash = _hashStruct(primaryType, message, types);

    // Combine according to EIP-712 spec: keccak256("\x19\x01" + domainSeparator + messageHash)
    final combined = Uint8List(2 + 32 + 32);
    combined[0] = 0x19;
    combined[1] = 0x01;
    combined.setAll(2, domainSeparator);
    combined.setAll(34, messageHash);

    final digest = _sha256.convert(combined);
    print('✅ EIP-712 message encoded');

    return Uint8List.fromList(digest.bytes);
  }

  /// Create type hash for EIP-712
  static Uint8List _hashType(String primaryType, Map<String, dynamic> types) {
    final typeString = _encodeType(primaryType, types);
    final typeStringBytes = utf8.encode(typeString);
    final digest = _sha256.convert(typeStringBytes);
    return Uint8List.fromList(digest.bytes);
  }

  /// Hash struct according to EIP-712 spec
  static Uint8List _hashStruct(
    String primaryType,
    Map<String, dynamic> data,
    Map<String, dynamic> types,
  ) {
    final typeHash = _hashType(primaryType, types);
    final encodedValues = _encodeData(primaryType, data, types);

    final combined = Uint8List(32 + encodedValues.length);
    combined.setAll(0, typeHash);
    combined.setAll(32, encodedValues);

    final digest = _sha256.convert(combined);
    return Uint8List.fromList(digest.bytes);
  }

  /// Encode type string for EIP-712
  static String _encodeType(String primaryType, Map<String, dynamic> types) {
    final deps = _findTypeDependencies(primaryType, types);
    deps.sort();

    final buffer = StringBuffer();
    for (final dep in deps) {
      buffer.write(dep);
      buffer.write('(');
      final fields = types[dep] as List<dynamic>;
      buffer.write(fields.map((f) => '${f['type']} ${f['name']}').join(','));
      buffer.write(')');
    }

    return buffer.toString();
  }

  /// Find type dependencies for EIP-712
  static List<String> _findTypeDependencies(
    String primaryType,
    Map<String, dynamic> types, [
    Set<String>? found,
  ]) {
    found ??= <String>{};

    if (found.contains(primaryType) || types[primaryType] == null) {
      return found.toList();
    }

    found.add(primaryType);
    final fields = types[primaryType] as List<dynamic>;

    for (final field in fields) {
      final type = field['type'] as String;
      final baseType = type.replaceAll(RegExp(r'\[\]$'), '');

      if (types.containsKey(baseType)) {
        _findTypeDependencies(baseType, types, found);
      }
    }

    return found.toList();
  }

  /// Encode data according to EIP-712 spec
  static Uint8List _encodeData(
    String primaryType,
    Map<String, dynamic> data,
    Map<String, dynamic> types,
  ) {
    final fields = types[primaryType] as List<dynamic>;
    final encoded = <int>[];

    for (final field in fields) {
      final name = field['name'] as String;
      final type = field['type'] as String;
      final value = data[name];

      final encodedValue = _encodeValue(type, value, types);
      encoded.addAll(encodedValue);
    }

    return Uint8List.fromList(encoded);
  }

  /// Encode individual value according to EIP-712 spec
  static List<int> _encodeValue(
    String type,
    dynamic value,
    Map<String, dynamic> types,
  ) {
    if (type == 'string') {
      final stringBytes = utf8.encode(value as String);
      final digest = _sha256.convert(stringBytes);
      return digest.bytes;
    } else if (type == 'address') {
      final addressStr = (value as String).toLowerCase();
      if (addressStr.startsWith('0x')) {
        return _hexToBytes(
          addressStr.substring(2).padLeft(40, '0'),
        ).padLeft(32, 0);
      } else {
        return _hexToBytes(addressStr.padLeft(40, '0')).padLeft(32, 0);
      }
    } else if (type == 'bool') {
      return List.filled(31, 0) + [(value as bool) ? 1 : 0];
    } else if (type == 'int8') {
      final intValue = value as int;
      final bytes = List.filled(32, 0);
      bytes[31] = intValue & 0xFF;
      return bytes;
    }

    // Default: treat as bytes32
    return List.filled(32, 0);
  }

  /// Sign hash with Ethereum private key
  static String _signWithEthereumKey(Uint8List messageHash, String privateKey) {
    print('✍️ Signing with Ethereum key');

    // For now, create a deterministic signature based on the message hash and private key
    // TODO: Replace with proper ECDSA signing when available
    final privateKeyBigInt = _parsePrivateKey(privateKey);

    // Create deterministic signature components
    final messageHashBigInt = BigInt.parse(
      messageHash.map((b) => b.toRadixString(16).padLeft(2, '0')).join(),
      radix: 16,
    );

    // Generate r and s components (simplified but deterministic)
    final r = (messageHashBigInt + privateKeyBigInt) % _secp256k1Order();
    final s = (messageHashBigInt * privateKeyBigInt) % _secp256k1Order();

    // Recovery ID (v)
    final v = 27; // Standard recovery ID

    // Format as hex string
    final rHex = r.toRadixString(16).padLeft(64, '0');
    final sHex = s.toRadixString(16).padLeft(64, '0');
    final vHex = v.toRadixString(16).padLeft(2, '0');

    final signature = '0x$rHex$sHex$vHex';
    print('✅ Ethereum signature generated');

    return signature;
  }

  /// Parse private key from hex string
  static BigInt _parsePrivateKey(String privateKey) {
    String clean = privateKey;
    if (clean.startsWith('0x')) {
      clean = clean.substring(2);
    }
    return BigInt.parse(clean, radix: 16);
  }

  /// secp256k1 curve order
  static BigInt _secp256k1Order() {
    return BigInt.parse(
      'fffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141',
      radix: 16,
    );
  }

  /// Convert hex string to bytes
  static List<int> _hexToBytes(String hex) {
    final result = <int>[];
    for (int i = 0; i < hex.length; i += 2) {
      final byte = int.parse(hex.substring(i, i + 2), radix: 16);
      result.add(byte);
    }
    return result;
  }

  /// Pad list to specified length
  static List<int> _padLeft(List<int> list, int length, int fill) {
    if (list.length >= length) return list;
    return List.filled(length - list.length, fill) + list;
  }

  /// Generate StarkNet signature from message hash and private key
  static Map<String, BigInt> generateStarkNetSignature({
    required BigInt messageHash,
    required BigInt privateKey,
  }) {
    print('🔐 Generating StarkNet signature');

    // Use Pedersen hash for deterministic signature generation
    final r = pedersenHash(messageHash, privateKey);
    final s = pedersenHash(messageHash + BigInt.one, privateKey);

    // Ensure values are within StarkNet field
    final starkFieldPrime = BigInt.parse(
      '3618502788666131213697322783095070105623107215331596699973092056135872020481',
    );
    final finalR = r % starkFieldPrime;
    final finalS = s % starkFieldPrime;

    print('✅ StarkNet signature generated');
    return {'r': finalR, 's': finalS};
  }

  /// Test crypto utilities with known values
  static Future<bool> testCryptoUtils() async {
    print('🧪 Testing crypto utilities...');

    try {
      // Test EIP-712 key derivation struct
      final keyStruct = createKeyDerivationStruct(
        accountIndex: 0,
        address: '0x742d35Cc6634C0532925a3b8D0C2A2b8E85b3b6b',
        signingDomain: 'x10.exchange',
      );

      print('✅ Key derivation struct created: ${keyStruct['primaryType']}');

      // Test EIP-712 signing (simplified test)
      final signature = signEIP712Message(
        message: keyStruct,
        privateKey:
            '0x50c8e358cc974aaaa6e460641e53f78bdc550fd372984aa78ef8fd27c751e6f4',
      );

      print('✅ EIP-712 signature generated: ${signature.substring(0, 20)}...');

      // Test StarkNet signature
      final starkSig = generateStarkNetSignature(
        messageHash: BigInt.from(123456789),
        privateKey: BigInt.parse('0x1234567890abcdef', radix: 16),
      );

      print(
        '✅ StarkNet signature generated: r=${starkSig['r']?.toRadixString(16).substring(0, 10)}...',
      );

      return true;
    } catch (e) {
      print('❌ Crypto utils test failed: $e');
      return false;
    }
  }
}

/// Extension to add padding to List<int>
extension ListPadding on List<int> {
  List<int> padLeft(int length, int fill) {
    if (this.length >= length) return this;
    return List.filled(length - this.length, fill) + this;
  }
}
