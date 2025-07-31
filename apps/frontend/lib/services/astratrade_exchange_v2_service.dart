/// AstraTrade Exchange V2 Service - Flutter Integration
/// 
/// This service provides seamless integration with the new Cairo 2.x exchange contract
/// Features:
/// - Mobile-optimized gas patterns
/// - Real-time gamification events
/// - Extended Exchange API validation
/// - Comprehensive error handling
/// - Event streaming for live updates

import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:starknet/starknet.dart';
import '../config/starknet_config.dart';
import '../models/trade_result.dart';
import '../models/user_progression.dart';
import '../models/trading_position.dart';
import '../models/trading_pair.dart';

class AstraTradeExchangeV2Service {
  static const String CONTRACT_ADDRESS = 'YOUR_DEPLOYED_CONTRACT_ADDRESS_HERE'; // Will be updated after deployment
  
  final StarknetProvider _provider;
  final Account _account;
  final StreamController<ExchangeEvent> _eventController = StreamController<ExchangeEvent>.broadcast();
  
  // Event stream for real-time updates
  Stream<ExchangeEvent> get eventStream => _eventController.stream;
  
  AstraTradeExchangeV2Service({
    required StarknetProvider provider,
    required Account account,
  }) : _provider = provider, _account = account {
    _initializeEventListening();
  }

  // ============================================================================
  // USER MANAGEMENT
  // ============================================================================

  /// Register a new user in the exchange
  Future<TransactionResult> registerUser() async {
    try {
      final call = FunctionCall(
        contractAddress: CONTRACT_ADDRESS,
        entrypoint: 'register_user',
        calldata: [],
      );

      final response = await _account.execute([call]);
      
      if (response.transactionHash.isNotEmpty) {
        return TransactionResult(
          success: true,
          transactionHash: response.transactionHash,
          message: 'User registered successfully',
        );
      } else {
        return TransactionResult(
          success: false,
          error: 'Failed to register user',
        );
      }
    } catch (e) {
      debugPrint('Error registering user: $e');
      return TransactionResult(
        success: false,
        error: e.toString(),
      );
    }
  }

  /// Get user information and progression
  Future<UserProgression?> getUserProgression(String userAddress) async {
    try {
      final call = FunctionCall(
        contractAddress: CONTRACT_ADDRESS,
        entrypoint: 'get_user',
        calldata: [userAddress],
      );

      final response = await _provider.call(call);
      
      if (response.isNotEmpty) {
        return UserProgression.fromContractResponse(response);
      }
      return null;
    } catch (e) {
      debugPrint('Error getting user progression: $e');
      return null;
    }
  }

  // ============================================================================
  // POSITION MANAGEMENT - Mobile Optimized
  // ============================================================================

  /// Open a practice position with mobile-optimized gas usage
  Future<PositionResult> openPracticePosition({
    required int pairId,
    required bool isLong,
    required int leverage,
    required BigInt collateralAmount,
  }) async {
    try {
      // Validate inputs before sending transaction
      if (leverage <= 0 || leverage > 100) {
        return PositionResult(
          success: false,
          error: 'Invalid leverage. Must be between 1 and 100.',
        );
      }

      if (collateralAmount <= BigInt.zero) {
        return PositionResult(
          success: false,
          error: 'Collateral amount must be greater than zero.',
        );
      }

      final call = FunctionCall(
        contractAddress: CONTRACT_ADDRESS,
        entrypoint: 'open_practice_position',
        calldata: [
          pairId.toString(),
          isLong ? '1' : '0',
          leverage.toString(),
          collateralAmount.toString(),
        ],
      );

      final response = await _account.execute([call]);
      
      if (response.transactionHash.isNotEmpty) {
        // Wait for transaction confirmation
        final receipt = await _waitForTransaction(response.transactionHash);
        
        if (receipt != null && receipt.status == TransactionStatus.ACCEPTED_ON_L2) {
          final positionId = _parsePositionIdFromEvents(receipt.events);
          
          return PositionResult(
            success: true,
            positionId: positionId,
            transactionHash: response.transactionHash,
            message: 'Position opened successfully',
          );
        } else {
          return PositionResult(
            success: false,
            error: 'Transaction failed or reverted',
          );
        }
      } else {
        return PositionResult(
          success: false,
          error: 'Failed to submit transaction',
        );
      }
    } catch (e) {
      debugPrint('Error opening practice position: $e');
      return PositionResult(
        success: false,
        error: _parseErrorMessage(e.toString()),
      );
    }
  }

  /// Close an existing position
  Future<ClosePositionResult> closePosition(int positionId) async {
    try {
      final call = FunctionCall(
        contractAddress: CONTRACT_ADDRESS,
        entrypoint: 'close_position',
        calldata: [positionId.toString()],
      );

      final response = await _account.execute([call]);
      
      if (response.transactionHash.isNotEmpty) {
        final receipt = await _waitForTransaction(response.transactionHash);
        
        if (receipt != null && receipt.status == TransactionStatus.ACCEPTED_ON_L2) {
          final (pnl, isProfit) = _parsePnlFromEvents(receipt.events);
          
          return ClosePositionResult(
            success: true,
            positionId: positionId,
            pnl: pnl,
            isProfit: isProfit,
            transactionHash: response.transactionHash,
            message: isProfit ? 'Position closed with profit!' : 'Position closed',
          );
        } else {
          return ClosePositionResult(
            success: false,
            error: 'Transaction failed or reverted',
          );
        }
      } else {
        return ClosePositionResult(
          success: false,
          error: 'Failed to submit transaction',
        );
      }
    } catch (e) {
      debugPrint('Error closing position: $e');
      return ClosePositionResult(
        success: false,
        error: _parseErrorMessage(e.toString()),
      );
    }
  }

  /// Get all active positions for a user
  Future<List<TradingPosition>> getUserPositions(String userAddress) async {
    try {
      final call = FunctionCall(
        contractAddress: CONTRACT_ADDRESS,
        entrypoint: 'get_user_positions',
        calldata: [userAddress],
      );

      final response = await _provider.call(call);
      
      if (response.isNotEmpty) {
        return _parsePositionsFromResponse(response);
      }
      return [];
    } catch (e) {
      debugPrint('Error getting user positions: $e');
      return [];
    }
  }

  // ============================================================================
  // EXTENDED EXCHANGE API INTEGRATION
  // ============================================================================

  /// Register Extended Exchange API key for live trading
  Future<ApiKeyResult> registerExtendedExchangeKey({
    required String keyHash,
    required int permissions,
  }) async {
    try {
      final call = FunctionCall(
        contractAddress: CONTRACT_ADDRESS,
        entrypoint: 'register_extended_exchange_key',
        calldata: [keyHash, permissions.toString()],
      );

      final response = await _account.execute([call]);
      
      if (response.transactionHash.isNotEmpty) {
        final receipt = await _waitForTransaction(response.transactionHash);
        
        if (receipt != null && receipt.status == TransactionStatus.ACCEPTED_ON_L2) {
          final keyId = _parseKeyIdFromEvents(receipt.events);
          
          return ApiKeyResult(
            success: true,
            keyId: keyId,
            transactionHash: response.transactionHash,
            message: 'API key registered successfully',
          );
        } else {
          return ApiKeyResult(
            success: false,
            error: 'Transaction failed or reverted',
          );
        }
      } else {
        return ApiKeyResult(
          success: false,
          error: 'Failed to submit transaction',
        );
      }
    } catch (e) {
      debugPrint('Error registering Extended Exchange key: $e');
      return ApiKeyResult(
        success: false,
        error: _parseErrorMessage(e.toString()),
      );
    }
  }

  /// Validate a trade executed through Extended Exchange API
  Future<ValidationResult> validateExtendedExchangeTrade({
    required int keyId,
    required String externalTradeId,
    required String tradeDataHash,
    required List<String> signature,
  }) async {
    try {
      final call = FunctionCall(
        contractAddress: CONTRACT_ADDRESS,
        entrypoint: 'validate_extended_exchange_trade',
        calldata: [
          keyId.toString(),
          externalTradeId,
          tradeDataHash,
          signature.length.toString(),
          ...signature,
        ],
      );

      final response = await _account.execute([call]);
      
      if (response.transactionHash.isNotEmpty) {
        final receipt = await _waitForTransaction(response.transactionHash);
        
        if (receipt != null && receipt.status == TransactionStatus.ACCEPTED_ON_L2) {
          final validationHash = _parseValidationHashFromEvents(receipt.events);
          
          return ValidationResult(
            success: true,
            validationHash: validationHash,
            transactionHash: response.transactionHash,
            message: 'Trade validated successfully',
          );
        } else {
          return ValidationResult(
            success: false,
            error: 'Transaction failed or reverted',
          );
        }
      } else {
        return ValidationResult(
          success: false,
          error: 'Failed to submit transaction',
        );
      }
    } catch (e) {
      debugPrint('Error validating Extended Exchange trade: $e');
      return ValidationResult(
        success: false,
        error: _parseErrorMessage(e.toString()),
      );
    }
  }

  // ============================================================================
  // TRADING PAIRS
  // ============================================================================

  /// Get trading pair information
  Future<TradingPair?> getTradingPair(int pairId) async {
    try {
      final call = FunctionCall(
        contractAddress: CONTRACT_ADDRESS,
        entrypoint: 'get_trading_pair',
        calldata: [pairId.toString()],
      );

      final response = await _provider.call(call);
      
      if (response.isNotEmpty) {
        return TradingPair.fromContractResponse(response);
      }
      return null;
    } catch (e) {
      debugPrint('Error getting trading pair: $e');
      return null;
    }
  }

  /// Get all available trading pairs
  Future<List<TradingPair>> getAllTradingPairs() async {
    try {
      // Get active pairs count first
      final countCall = FunctionCall(
        contractAddress: CONTRACT_ADDRESS,
        entrypoint: 'get_system_status', // This returns system info including pair count
        calldata: [],
      );

      final countResponse = await _provider.call(countCall);
      // Parse active pairs count from response
      
      List<TradingPair> pairs = [];
      
      // Fetch each trading pair (assuming we know there are at least BTC/USD and ETH/USD)
      for (int i = 1; i <= 2; i++) {
        final pair = await getTradingPair(i);
        if (pair != null && pair.isActive) {
          pairs.add(pair);
        }
      }
      
      return pairs;
    } catch (e) {
      debugPrint('Error getting all trading pairs: $e');
      return [];
    }
  }

  // ============================================================================
  // SYSTEM STATUS
  // ============================================================================

  /// Get system status (paused, emergency mode)
  Future<SystemStatus> getSystemStatus() async {
    try {
      final call = FunctionCall(
        contractAddress: CONTRACT_ADDRESS,
        entrypoint: 'get_system_status',
        calldata: [],
      );

      final response = await _provider.call(call);
      
      if (response.length >= 2) {
        return SystemStatus(
          isPaused: response[0] == '1',
          isEmergencyMode: response[1] == '1',
        );
      }
      
      return SystemStatus(isPaused: false, isEmergencyMode: false);
    } catch (e) {
      debugPrint('Error getting system status: $e');
      return SystemStatus(isPaused: true, isEmergencyMode: true); // Fail safe
    }
  }

  /// Get daily trading volume
  Future<BigInt> getDailyVolume() async {
    try {
      final call = FunctionCall(
        contractAddress: CONTRACT_ADDRESS,
        entrypoint: 'get_daily_volume',
        calldata: [],
      );

      final response = await _provider.call(call);
      
      if (response.isNotEmpty) {
        return BigInt.parse(response[0]);
      }
      return BigInt.zero;
    } catch (e) {
      debugPrint('Error getting daily volume: $e');
      return BigInt.zero;
    }
  }

  // ============================================================================
  // PRIVATE HELPER METHODS
  // ============================================================================

  void _initializeEventListening() {
    // Initialize event listening for real-time updates
    // This would typically involve WebSocket connections or polling
    // For now, we'll set up the basic structure
    
    Timer.periodic(const Duration(seconds: 10), (timer) {
      _pollForEvents();
    });
  }

  Future<void> _pollForEvents() async {
    try {
      // Poll for recent events from the contract
      // This is a simplified implementation - in production, you'd use
      // proper event filtering and websockets
      
      // Implementation would go here based on Starknet event polling patterns
    } catch (e) {
      debugPrint('Error polling for events: $e');
    }
  }

  Future<TransactionReceipt?> _waitForTransaction(String transactionHash) async {
    try {
      // Wait for transaction confirmation with timeout
      int attempts = 0;
      const maxAttempts = 30; // 5 minutes with 10-second intervals
      
      while (attempts < maxAttempts) {
        try {
          final receipt = await _provider.getTransactionReceipt(transactionHash);
          
          if (receipt.status == TransactionStatus.ACCEPTED_ON_L2 ||
              receipt.status == TransactionStatus.REJECTED) {
            return receipt;
          }
        } catch (e) {
          // Transaction might not be available yet
        }
        
        await Future.delayed(const Duration(seconds: 10));
        attempts++;
      }
      
      return null; // Timeout
    } catch (e) {
      debugPrint('Error waiting for transaction: $e');
      return null;
    }
  }

  int _parsePositionIdFromEvents(List<Event> events) {
    try {
      for (final event in events) {
        if (event.keys.isNotEmpty && event.keys[0] == 'PositionOpened') {
          // Parse position ID from event data
          return int.parse(event.data[1]); // position_id is second data field
        }
      }
      return 0;
    } catch (e) {
      debugPrint('Error parsing position ID from events: $e');
      return 0;
    }
  }

  (BigInt, bool) _parsePnlFromEvents(List<Event> events) {
    try {
      for (final event in events) {
        if (event.keys.isNotEmpty && event.keys[0] == 'PositionClosed') {
          final pnl = BigInt.parse(event.data[2]); // pnl field
          final isProfit = event.data[3] == '1'; // is_profit field
          return (pnl, isProfit);
        }
      }
      return (BigInt.zero, false);
    } catch (e) {
      debugPrint('Error parsing PnL from events: $e');
      return (BigInt.zero, false);
    }
  }

  int _parseKeyIdFromEvents(List<Event> events) {
    try {
      for (final event in events) {
        if (event.keys.isNotEmpty && event.keys[0] == 'ExtendedExchangeKeyRegistered') {
          return int.parse(event.data[1]); // key_id field
        }
      }
      return 0;
    } catch (e) {
      debugPrint('Error parsing key ID from events: $e');
      return 0;
    }
  }

  String _parseValidationHashFromEvents(List<Event> events) {
    try {
      for (final event in events) {
        if (event.keys.isNotEmpty && event.keys[0] == 'ExtendedExchangeTradeValidated') {
          return event.data[3]; // validation_hash field
        }
      }
      return '';
    } catch (e) {
      debugPrint('Error parsing validation hash from events: $e');
      return '';
    }
  }

  List<TradingPosition> _parsePositionsFromResponse(List<String> response) {
    try {
      List<TradingPosition> positions = [];
      
      // Parse array of positions from contract response
      // This would need to match the exact format returned by the contract
      
      // Simplified parsing - in reality, this would be more complex
      for (int i = 0; i < response.length; i += 12) { // 12 fields per position
        if (i + 11 < response.length) {
          positions.add(TradingPosition.fromContractData(
            response.sublist(i, i + 12)
          ));
        }
      }
      
      return positions;
    } catch (e) {
      debugPrint('Error parsing positions from response: $e');
      return [];
    }
  }

  String _parseErrorMessage(String error) {
    // Parse common contract error messages into user-friendly text
    if (error.contains('User not registered')) {
      return 'Please register your account first';
    } else if (error.contains('Insufficient balance')) {
      return 'Insufficient balance for this trade';
    } else if (error.contains('System paused')) {
      return 'Trading is temporarily paused';
    } else if (error.contains('Invalid leverage')) {
      return 'Leverage amount is invalid';
    } else if (error.contains('Exceeds user limit')) {
      return 'Trade exceeds your leverage limit';
    } else {
      return 'An error occurred: ${error.length > 100 ? error.substring(0, 100) + '...' : error}';
    }
  }

  void dispose() {
    _eventController.close();
  }
}

// ============================================================================
// DATA MODELS
// ============================================================================

class TransactionResult {
  final bool success;
  final String? transactionHash;
  final String? error;
  final String? message;

  TransactionResult({
    required this.success,
    this.transactionHash,
    this.error,
    this.message,
  });
}

class PositionResult extends TransactionResult {
  final int? positionId;

  PositionResult({
    required bool success,
    this.positionId,
    String? transactionHash,
    String? error,
    String? message,
  }) : super(
    success: success,
    transactionHash: transactionHash,
    error: error,
    message: message,
  );
}

class ClosePositionResult extends TransactionResult {
  final int? positionId;
  final BigInt? pnl;
  final bool? isProfit;

  ClosePositionResult({
    required bool success,
    this.positionId,
    this.pnl,
    this.isProfit,
    String? transactionHash,
    String? error,
    String? message,
  }) : super(
    success: success,
    transactionHash: transactionHash,
    error: error,
    message: message,
  );
}

class ApiKeyResult extends TransactionResult {
  final int? keyId;

  ApiKeyResult({
    required bool success,
    this.keyId,
    String? transactionHash,
    String? error,
    String? message,
  }) : super(
    success: success,
    transactionHash: transactionHash,
    error: error,
    message: message,
  );
}

class ValidationResult extends TransactionResult {
  final String? validationHash;

  ValidationResult({
    required bool success,
    this.validationHash,
    String? transactionHash,
    String? error,
    String? message,
  }) : super(
    success: success,
    transactionHash: transactionHash,
    error: error,
    message: message,
  );
}

class SystemStatus {
  final bool isPaused;
  final bool isEmergencyMode;

  SystemStatus({
    required this.isPaused,
    required this.isEmergencyMode,
  });
}

abstract class ExchangeEvent {
  final String type;
  final DateTime timestamp;

  ExchangeEvent({
    required this.type,
    required this.timestamp,
  });
}

class PositionOpenedEvent extends ExchangeEvent {
  final String userAddress;
  final int positionId;
  final int pairId;
  final bool isLong;
  final int leverage;
  final BigInt collateral;
  final int xpEarned;

  PositionOpenedEvent({
    required this.userAddress,
    required this.positionId,
    required this.pairId,
    required this.isLong,
    required this.leverage,
    required this.collateral,
    required this.xpEarned,
    required DateTime timestamp,
  }) : super(type: 'PositionOpened', timestamp: timestamp);
}

class XPAwardedEvent extends ExchangeEvent {
  final String userAddress;
  final int xpAmount;
  final String activityType;
  final int multiplier;
  final BigInt totalXp;

  XPAwardedEvent({
    required this.userAddress,
    required this.xpAmount,
    required this.activityType,
    required this.multiplier,
    required this.totalXp,
    required DateTime timestamp,
  }) : super(type: 'XPAwarded', timestamp: timestamp);
}

class LevelUpEvent extends ExchangeEvent {
  final String userAddress;
  final int oldLevel;
  final int newLevel;
  final BigInt totalXp;
  final int newMaxLeverage;

  LevelUpEvent({
    required this.userAddress,
    required this.oldLevel,
    required this.newLevel,
    required this.totalXp,
    required this.newMaxLeverage,
    required DateTime timestamp,
  }) : super(type: 'LevelUp', timestamp: timestamp);
}