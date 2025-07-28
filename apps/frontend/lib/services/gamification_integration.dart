import 'dart:developer';
import 'package:flutter/foundation.dart';
import '../services/simple_gamification_service.dart';
import '../models/simple_trade.dart';

/// Helper service to integrate gamification with trading
/// Awards XP and achievements for trading activities
class GamificationIntegration {
  static final SimpleGamificationService _gamificationService = SimpleGamificationService();
  
  /// Award XP for a completed trade
  static Future<void> awardTradeXP({
    required String playerId,
    required SimpleTrade trade,
    required bool isRealTrade,
  }) async {
    try {
      final profit = trade.profitLoss ?? 0.0;
      final isProfitable = profit > 0;
      final amount = trade.amount;
      
      final metadata = {
        'trade_id': trade.id,
        'symbol': trade.symbol,
        'direction': trade.direction,
        'amount': amount,
        'profit': profit,
        'is_real_trade': isRealTrade,
        'timestamp': trade.timestamp.toIso8601String(),
      };
      
      if (isRealTrade) {
        await _gamificationService.awardRealTradeXP(
          playerId: playerId,
          isProfitable: isProfitable,
          amount: amount,
          profit: profit,
          metadata: metadata,
        );
        
        debugPrint('💰 Real trade XP awarded for trade ${trade.id}');
      } else {
        await _gamificationService.awardPracticeTradeXP(
          playerId: playerId,
          isProfitable: isProfitable,
          amount: amount,
          metadata: metadata,
        );
        
        debugPrint('🎯 Practice trade XP awarded for trade ${trade.id}');
      }
      
    } catch (e) {
      log('Error awarding trade XP: $e');
      // Don't throw - gamification should not break trading
    }
  }
  
  /// Award daily login bonus
  static Future<bool> awardDailyLoginBonus(String playerId) async {
    try {
      final event = await _gamificationService.awardDailyLogin(playerId);
      
      if (event != null) {
        debugPrint('📅 Daily login bonus awarded: ${event.xpGained}XP');
        return true;
      }
      
      return false; // Already claimed today
      
    } catch (e) {
      log('Error awarding daily login bonus: $e');
      return false;
    }
  }
  
  /// Initialize gamification for a new player
  static Future<void> initializeNewPlayer(String playerId) async {
    try {
      await _gamificationService.initializePlayer(playerId);
      debugPrint('🎮 Gamification initialized for new player: $playerId');
    } catch (e) {
      log('Error initializing gamification for new player: $e');
      // Don't throw - player creation should not fail due to gamification
    }
  }
  
  /// Get current gamification service instance
  static SimpleGamificationService get service => _gamificationService;
}