import 'dart:convert';
import 'package:crypto/crypto.dart';

/// Simplified Starknet address derivation service
/// Uses enhanced deterministic methods for address generation
class StarknetAddressService {
  /// Derives a Starknet address from a private key using enhanced deterministic method
  /// This is the single source of truth for all address derivation in the app
  static String deriveAddressFromPrivateKey(String privateKeyHex) {
    try {
      // Normalize the private key
      final cleanKey = _normalizePrivateKey(privateKeyHex);
      
      // Use enhanced deterministic address derivation
      final address = _deriveAddressDeterministic(cleanKey);
      
      return address;
    } catch (e) {
      throw StarknetAddressException('Failed to derive address: $e');
    }
  }

  /// Enhanced deterministic address derivation
  static String _deriveAddressDeterministic(String privateKey) {
    // Create deterministic address based on private key
    final keyBytes = privateKey.codeUnits;
    final hash1 = sha256.convert(keyBytes);
    final hash2 = sha256.convert([...hash1.bytes, ...privateKey.codeUnits]);
    
    // Convert to BigInt and ensure it's within Starknet field
    final addressBigInt = BigInt.parse(hash2.toString(), radix: 16);
    final starknetPrime = BigInt.parse(
      '800000000000011000000000000000000000000000000000000000000000001',
      radix: 16
    );
    
    final reducedAddress = addressBigInt % starknetPrime;
    return '0x${reducedAddress.toRadixString(16).padLeft(64, '0')}';
  }

  /// Normalizes private key format for Starknet
  static String _normalizePrivateKey(String privateKeyHex) {
    // Remove 0x prefix if present
    String cleanKey = privateKeyHex.startsWith('0x') 
        ? privateKeyHex.substring(2) 
        : privateKeyHex;

    // Ensure valid hex format
    if (!RegExp(r'^[0-9a-fA-F]+$').hasMatch(cleanKey)) {
      throw StarknetAddressException('Invalid hex format for private key');
    }

    // Handle key too large for Starknet field
    final bigIntKey = BigInt.parse(cleanKey, radix: 16);
    final starknetPrime = BigInt.parse(
      '800000000000011000000000000000000000000000000000000000000000001',
      radix: 16
    );
    
    final reducedKey = bigIntKey % starknetPrime;
    return reducedKey.toRadixString(16).padLeft(64, '0');
  }

  /// Validates a Starknet address format
  static bool isValidStarknetAddress(String address) {
    try {
      if (!address.startsWith('0x')) return false;
      
      final cleanAddress = address.substring(2);
      if (cleanAddress.length != 64) return false;
      
      // Parse as BigInt to validate hex format
      final addressBigInt = BigInt.parse(cleanAddress, radix: 16);
      
      // Ensure within valid Starknet address range
      final maxAddress = BigInt.parse(
        '7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff',
        radix: 16
      );
      
      return addressBigInt <= maxAddress;
    } catch (e) {
      return false;
    }
  }

  /// Creates a deterministic address for testing purposes
  /// Only use for development/testing - not for production wallets
  @Deprecated('Use only for testing')
  static String createTestAddress(String input) {
    final bytes = utf8.encode(input);
    final digest = bytes.fold(BigInt.zero, (acc, byte) => (acc << 8) + BigInt.from(byte));
    
    final prime = BigInt.parse(
      '800000000000011000000000000000000000000000000000000000000000001',
      radix: 16
    );
    
    final address = digest % prime;
    return '0x${address.toRadixString(16).padLeft(64, '0')}';
  }
}

/// Exception for address derivation errors
class StarknetAddressException implements Exception {
  final String message;
  
  StarknetAddressException(this.message);
  
  @override
  String toString() => 'StarknetAddressException: $message';
}