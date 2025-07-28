import 'dart:developer';
import 'package:flutter/foundation.dart';
import '../models/simple_trade.dart';
import 'simple_trading_service.dart';
import 'extended_trading_service.dart';
import 'secure_storage_service.dart';
import 'gamification_integration.dart';

/// Trading modes for progressive onboarding
enum TradingMode {
  practice,     // Simulation only
  micro,        // Real trades $1-$10
  intermediate, // Real trades $10-$100
  advanced,     // Real trades $100+
}

/// Advanced trading service that seamlessly switches between simulation and real trading
/// Maintains SimpleTradingService compatibility while adding real Extended API integration
class RealTradingService extends SimpleTradingService {
  static const String _tradingModeKey = 'trading_mode';
  static const String _userLevelKey = 'user_level';
  static const String _tradeCountKey = 'total_trade_count';
  
  /// Get current trading mode
  static Future<TradingMode> getTradingMode() async {
    try {
      final modeString = await SecureStorageService.instance.getValue(_tradingModeKey);
      if (modeString != null) {
        return TradingMode.values.firstWhere(
          (mode) => mode.name == modeString,
          orElse: () => TradingMode.practice,
        );
      }
    } catch (e) {
      log('❌ Failed to get trading mode: $e');
    }
    return TradingMode.practice;
  }
  
  /// Set trading mode
  static Future<void> setTradingMode(TradingMode mode) async {
    try {
      await SecureStorageService.instance.storeValue(_tradingModeKey, mode.name);
      debugPrint('✅ Trading mode set to: ${mode.name}');
    } catch (e) {
      log('❌ Failed to set trading mode: $e');
    }
  }
  
  /// Create trade with automatic mode detection
  static Future<SimpleTrade> createTrade({
    required double amount,
    required String direction,
    String? symbol,
  }) async {
    try {
      final mode = await getTradingMode();
      final shouldUseRealTrading = await _shouldUseRealTrading(mode, amount);
      
      if (shouldUseRealTrading) {
        debugPrint('🚀 Creating REAL trade: $amount $direction ${symbol ?? 'BTC-USD'}');
        return await _createRealTrade(
          amount: amount,
          direction: direction,
          symbol: symbol,
        );
      } else {
        debugPrint('🎮 Creating PRACTICE trade: $amount $direction ${symbol ?? 'BTC-USD'}');
        return SimpleTradingService.createTrade(
          amount: amount,
          direction: direction,
          symbol: symbol,
        );
      }
    } catch (e) {
      log('❌ Failed to create trade: $e');
      // Fallback to simulation if real trading fails
      return SimpleTradingService.createTrade(
        amount: amount,
        direction: direction,
        symbol: symbol,
      );
    }
  }
  
  /// Complete trade with real position tracking
  static Future<SimpleTrade> completeTradeDelayed(SimpleTrade trade) async {
    try {
      SimpleTrade completedTrade;
      
      if (trade.isRealTrade) {
        debugPrint('📊 Updating REAL trade with position data: ${trade.id}');
        completedTrade = await _completeRealTrade(trade);
      } else {
        debugPrint('🎯 Completing PRACTICE trade: ${trade.id}');
        completedTrade = await SimpleTradingService.completeTradeDelayed(trade);
      }
      
      // Award gamification XP after trade completion
      try {
        // Get user ID from secure storage or generate one
        final userId = 'user_${DateTime.now().millisecondsSinceEpoch}'; // Simplified for now
        await GamificationIntegration.awardTradeXP(
          playerId: userId,
          trade: completedTrade,
          isRealTrade: completedTrade.isRealTrade,
        );
      } catch (e) {
        log('Warning: Failed to award gamification XP: $e');
        // Don't fail the trade completion due to gamification errors
      }
      
      return completedTrade;
    } catch (e) {
      log('❌ Failed to complete trade: $e');
      // Fallback to simulation completion
      return await SimpleTradingService.completeTradeDelayed(trade);
    }
  }
  
  /// Get trading mode limits and recommendations
  static Map<String, dynamic> getTradingLimits(TradingMode mode) {
    switch (mode) {
      case TradingMode.practice:
        return {
          'min_amount': 1.0,
          'max_amount': 1000.0,
          'max_daily_trades': 20,
          'is_real_money': false,
          'description': 'Practice trading with simulation',
        };
      case TradingMode.micro:
        return {
          'min_amount': 1.0,
          'max_amount': 10.0,
          'max_daily_trades': 5,
          'is_real_money': true,
          'description': 'Real micro-trades for learning',
        };
      case TradingMode.intermediate:
        return {
          'min_amount': 5.0,
          'max_amount': 100.0,
          'max_daily_trades': 10,
          'is_real_money': true,
          'description': 'Real intermediate trading',
        };
      case TradingMode.advanced:
        return {
          'min_amount': 10.0,
          'max_amount': 1000.0,
          'max_daily_trades': 50,
          'is_real_money': true,
          'description': 'Full real trading capabilities',
        };
    }
  }
  
  /// Progress user to next trading level
  static Future<Map<String, dynamic>> progressUserLevel() async {
    try {
      final currentMode = await getTradingMode();
      final tradeCount = await _getTotalTradeCount();
      
      TradingMode? nextMode;
      String? unlockReason;
      
      switch (currentMode) {
        case TradingMode.practice:
          if (tradeCount >= 5) {
            nextMode = TradingMode.micro;
            unlockReason = 'Completed 5+ practice trades';
          }
          break;
        case TradingMode.micro:
          if (tradeCount >= 15) {
            nextMode = TradingMode.intermediate;
            unlockReason = 'Completed 10+ micro trades';
          }
          break;
        case TradingMode.intermediate:
          if (tradeCount >= 35) {
            nextMode = TradingMode.advanced;
            unlockReason = 'Completed 20+ intermediate trades';
          }
          break;
        case TradingMode.advanced:
          // Already at max level
          break;
      }
      
      if (nextMode != null) {
        await setTradingMode(nextMode);
        debugPrint('🎉 User progressed to ${nextMode.name}: $unlockReason');
        
        return {
          'progressed': true,
          'new_mode': nextMode.name,
          'reason': unlockReason,
          'limits': getTradingLimits(nextMode),
        };
      }
      
      return {
        'progressed': false,
        'current_mode': currentMode.name,
        'trades_needed': _getTradesNeededForNext(currentMode, tradeCount),
      };
    } catch (e) {
      log('❌ Failed to progress user level: $e');
      return {
        'progressed': false,
        'error': e.toString(),
      };
    }
  }
  
  /// Setup user for real trading (onboarding)
  static Future<Map<String, dynamic>> setupRealTrading() async {
    try {
      debugPrint('🔧 Setting up user for real trading...');
      
      // Setup Extended API trading
      final setup = await ExtendedTradingService.setupUserForTrading();
      
      if (setup['success'] == true) {
        // User is ready for micro trading
        await setTradingMode(TradingMode.micro);
        
        return {
          'success': true,
          'mode': TradingMode.micro.name,
          'message': 'Ready for real micro-trading!',
          'limits': getTradingLimits(TradingMode.micro),
        };
      } else {
        return {
          'success': false,
          'error': setup['error'] ?? 'Setup failed',
          'message': 'Real trading setup failed, staying in practice mode',
        };
      }
    } catch (e) {
      log('❌ Failed to setup real trading: $e');
      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }
  
  /// Get comprehensive trading status
  static Future<Map<String, dynamic>> getTradingStatus() async {
    try {
      final mode = await getTradingMode();
      final tradeCount = await _getTotalTradeCount();
      final limits = getTradingLimits(mode);
      
      // Check Extended API status if in real trading mode
      Map<String, dynamic> extendedStatus = {};
      if (mode != TradingMode.practice) {
        extendedStatus = await ExtendedTradingService.getTradingStatus();
      }
      
      return {
        'trading_mode': mode.name,
        'total_trades': tradeCount,
        'limits': limits,
        'can_progress': await _canProgressToNext(mode, tradeCount),
        'trades_needed_for_next': _getTradesNeededForNext(mode, tradeCount),
        'extended_api_status': extendedStatus,
      };
    } catch (e) {
      log('❌ Failed to get trading status: $e');
      return {
        'trading_mode': TradingMode.practice.name,
        'error': e.toString(),
      };
    }
  }
  
  // ========================================
  // PRIVATE HELPER METHODS
  // ========================================
  
  /// Determine if real trading should be used
  static Future<bool> _shouldUseRealTrading(TradingMode mode, double amount) async {
    if (mode == TradingMode.practice) {
      return false;
    }
    
    final limits = getTradingLimits(mode);
    final maxAmount = limits['max_amount'] as double;
    
    // Check if amount is within limits for real trading
    if (amount > maxAmount) {
      debugPrint('⚠️ Amount $amount exceeds limit $maxAmount, using simulation');
      return false;
    }
    
    // Check if Extended API is available
    final isServiceAvailable = await ExtendedTradingService.isServiceAvailable();
    if (!isServiceAvailable) {
      debugPrint('⚠️ Extended API unavailable, using simulation');
      return false;
    }
    
    return true;
  }
  
  /// Create real trade via Extended API
  static Future<SimpleTrade> _createRealTrade({
    required double amount,
    required String direction,
    String? symbol,
  }) async {
    try {
      final trade = await ExtendedTradingService.placePerpetualTrade(
        amount: amount,
        direction: direction,
        symbol: symbol,
      );
      
      // Increment trade count
      await _incrementTradeCount();
      
      return trade;
    } catch (e) {
      log('❌ Real trade creation failed: $e');
      rethrow;
    }
  }
  
  /// Complete real trade with Extended API position data
  static Future<SimpleTrade> _completeRealTrade(SimpleTrade trade) async {
    try {
      // Wait a bit for position to settle
      await Future.delayed(const Duration(seconds: 3));
      
      // Update with real position data
      final updatedTrade = await ExtendedTradingService.updateTradeWithPosition(trade);
      
      return updatedTrade;
    } catch (e) {
      log('❌ Real trade completion failed: $e');
      // Return trade as-is if update fails
      return trade.copyWith(isCompleted: true);
    }
  }
  
  /// Get total trade count
  static Future<int> _getTotalTradeCount() async {
    try {
      final countString = await SecureStorageService.instance.getValue(_tradeCountKey);
      return int.tryParse(countString ?? '0') ?? 0;
    } catch (e) {
      return 0;
    }
  }
  
  /// Increment trade count
  static Future<void> _incrementTradeCount() async {
    try {
      final currentCount = await _getTotalTradeCount();
      await SecureStorageService.instance.storeValue(_tradeCountKey, (currentCount + 1).toString());
    } catch (e) {
      log('❌ Failed to increment trade count: $e');
    }
  }
  
  /// Check if user can progress to next level
  static Future<bool> _canProgressToNext(TradingMode mode, int tradeCount) async {
    switch (mode) {
      case TradingMode.practice:
        return tradeCount >= 5;
      case TradingMode.micro:
        return tradeCount >= 15;
      case TradingMode.intermediate:
        return tradeCount >= 35;
      case TradingMode.advanced:
        return false; // Already at max
    }
  }
  
  /// Get number of trades needed for next level
  static int _getTradesNeededForNext(TradingMode mode, int tradeCount) {
    switch (mode) {
      case TradingMode.practice:
        return (5 - tradeCount).clamp(0, 5);
      case TradingMode.micro:
        return (15 - tradeCount).clamp(0, 10);
      case TradingMode.intermediate:
        return (35 - tradeCount).clamp(0, 20);
      case TradingMode.advanced:
        return 0; // Already at max
    }
  }
}

/// Risk management service for real trading
class TradingRiskManager {
  /// Validate trade against risk limits
  static Map<String, dynamic> validateTrade({
    required double amount,
    required TradingMode mode,
    required int dailyTradeCount,
  }) {
    final limits = RealTradingService.getTradingLimits(mode);
    final maxAmount = limits['max_amount'] as double;
    final maxDailyTrades = limits['max_daily_trades'] as int;
    
    List<String> warnings = [];
    List<String> errors = [];
    
    // Amount validation
    if (amount > maxAmount) {
      errors.add('Amount \$${amount.toStringAsFixed(2)} exceeds limit \$${maxAmount.toStringAsFixed(2)}');
    }
    
    if (amount < 1.0 && mode != TradingMode.practice) {
      warnings.add('Minimum real trade amount is \$1.00');
    }
    
    // Daily trade limit validation
    if (dailyTradeCount >= maxDailyTrades) {
      errors.add('Daily trade limit reached ($dailyTradeCount/$maxDailyTrades)');
    }
    
    return {
      'is_valid': errors.isEmpty,
      'warnings': warnings,
      'errors': errors,
      'suggested_amount': errors.isNotEmpty ? maxAmount : amount,
    };
  }
  
  /// Get risk assessment for user
  static Map<String, dynamic> getRiskAssessment(TradingMode mode) {
    switch (mode) {
      case TradingMode.practice:
        return {
          'risk_level': 'None',
          'description': 'No real money at risk',
          'max_loss': 0.0,
        };
      case TradingMode.micro:
        return {
          'risk_level': 'Very Low',
          'description': 'Maximum \$10 per trade',
          'max_loss': 50.0, // 5 trades x $10
        };
      case TradingMode.intermediate:
        return {
          'risk_level': 'Low',
          'description': 'Maximum \$100 per trade',
          'max_loss': 1000.0, // 10 trades x $100
        };
      case TradingMode.advanced:
        return {
          'risk_level': 'Moderate',
          'description': 'Maximum \$1000 per trade',
          'max_loss': 50000.0, // 50 trades x $1000
        };
    }
  }
}