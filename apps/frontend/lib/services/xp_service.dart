import 'dart:developer';
import 'dart:math' as math;
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/xp_system.dart';
import '../models/user.dart';
import '../api/astratrade_backend_client.dart';

/// XP Service - Manages Stellar Shards (SS) and Lumina (LM) progression
/// Implements the core gamification loop for AstraTrade
class XPService {
  static const String _storageKey = 'player_xp_data';
  
  PlayerXP? _currentPlayerXP;
  final List<XPGainEvent> _recentEvents = [];
  final _backendClient = AstraTradeBackendClient();
  
  /// Get current player XP data
  PlayerXP? get currentPlayerXP => _currentPlayerXP;
  
  /// Initialize XP system for player
  Future<PlayerXP> initializePlayer(String playerId) async {
    try {
      // Try to load existing data first
      final existingXP = await _loadPlayerXP(playerId);
      if (existingXP != null) {
        _currentPlayerXP = existingXP;
        return existingXP;
      }
      
      // Create new player XP
      final newPlayerXP = PlayerXP.newPlayer(playerId);
      _currentPlayerXP = newPlayerXP;
      
      await _savePlayerXP(newPlayerXP);
      
      debugPrint('🌟 Initialized XP system for player: $playerId');
      return newPlayerXP;
      
    } catch (e) {
      log('Error initializing player XP: $e');
      throw XPServiceException('Failed to initialize XP system');
    }
  }
  
  /// Generate Stellar Shards from orbital forging (idle tapping)
  Future<XPGainEvent> generateStellarShards({
    required String playerId,
    required double baseAmount,
    bool isCriticalForge = false,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      if (_currentPlayerXP == null) {
        throw XPServiceException('Player XP not initialized');
      }
      
      // Calculate final amount with multipliers
      double finalAmount = baseAmount;
      
      // Apply streak multiplier
      finalAmount *= _currentPlayerXP!.streakMultiplier;
      
      // Apply critical forge bonus (random chance for 2-5x)
      if (isCriticalForge) {
        final critMultiplier = 2.0 + (math.Random().nextDouble() * 3.0);
        finalAmount *= critMultiplier;
      }
      
      // Apply level bonus
      finalAmount *= (1.0 + (_currentPlayerXP!.level * 0.05));
      
      // Create XP gain event
      final event = XPGainEvent(
        eventId: _generateEventId(),
        playerId: playerId,
        type: XPGainType.orbitalForging,
        stellarShardsGained: finalAmount,
        luminaGained: 0.0,
        description: isCriticalForge 
            ? 'Critical Orbital Forge! ⚡️ +${finalAmount.toStringAsFixed(1)} SS'
            : 'Orbital Forging ⭐ +${finalAmount.toStringAsFixed(1)} SS',
        timestamp: DateTime.now(),
        metadata: metadata ?? {},
      );
      
      // Update player XP
      await _applyXPGain(event);
      
      debugPrint('🔨 Stellar Shards generated: ${finalAmount.toStringAsFixed(2)}');
      return event;
      
    } catch (e) {
      log('Error generating Stellar Shards: $e');
      throw XPServiceException('Failed to generate Stellar Shards');
    }
  }
  
  /// Generate Stellar Shards from mock trading
  Future<XPGainEvent> generateStellarShardsFromMockTrade({
    required String playerId,
    required double tradeAmount,
    required bool wasSuccessful,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      // Base reward calculation
      double baseReward = tradeAmount * 0.1; // 10% of trade amount as SS
      
      // Success bonus
      if (wasSuccessful) {
        baseReward *= 1.5; // 50% bonus for successful trades
      } else {
        baseReward *= 0.3; // Consolation reward for failed trades
      }
      
      final event = XPGainEvent(
        eventId: _generateEventId(),
        playerId: playerId,
        type: XPGainType.mockTrade,
        stellarShardsGained: baseReward,
        luminaGained: 0.0,
        description: wasSuccessful
            ? 'Successful Mock Trade! 📈 +${baseReward.toStringAsFixed(1)} SS'
            : 'Mock Trade Learning 📊 +${baseReward.toStringAsFixed(1)} SS',
        timestamp: DateTime.now(),
        metadata: {
          'trade_amount': tradeAmount,
          'was_successful': wasSuccessful,
          ...?metadata,
        },
      );
      
      await _applyXPGain(event);
      return event;
      
    } catch (e) {
      log('Error generating SS from mock trade: $e');
      throw XPServiceException('Failed to process mock trade rewards');
    }
  }
  
  /// Harvest Lumina from real trading (Quantum Harvest)
  Future<XPGainEvent> harvestLumina({
    required String playerId,
    required double tradeAmount,
    required bool wasSuccessful,
    required String transactionHash,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      if (_currentPlayerXP == null) {
        throw XPServiceException('Player XP not initialized');
      }
      
      // Only successful real trades generate Lumina
      if (!wasSuccessful) {
        // Failed real trades still give small SS consolation
        return await generateStellarShardsFromMockTrade(
          playerId: playerId,
          tradeAmount: tradeAmount,
          wasSuccessful: false,
          metadata: metadata,
        );
      }
      
      // Calculate Lumina harvest
      // Formula: Base Lumina = (Trade Amount / 100) * Efficiency Multiplier
      double baseLumina = tradeAmount / 100.0;
      
      // Apply efficiency multiplier based on recent trading success
      final efficiencyMultiplier = await _calculateTradingEfficiency(playerId);
      baseLumina *= efficiencyMultiplier;
      
      // Apply level bonus for experienced traders
      baseLumina *= (1.0 + (_currentPlayerXP!.level * 0.02)); // 2% per level
      
      // Bonus Stellar Shards for real trading
      final bonusStellaSahards = baseLumina * 5.0; // 5 SS per 1 LM
      
      final event = XPGainEvent(
        eventId: _generateEventId(),
        playerId: playerId,
        type: XPGainType.quantumHarvest,
        stellarShardsGained: bonusStellaSahards,
        luminaGained: baseLumina,
        description: 'Quantum Harvest Complete! 🌌 +${baseLumina.toStringAsFixed(2)} LM',
        timestamp: DateTime.now(),
        metadata: {
          'trade_amount': tradeAmount,
          'transaction_hash': transactionHash,
          'efficiency_multiplier': efficiencyMultiplier,
          ...?metadata,
        },
      );
      
      // Update last Lumina harvest timestamp
      _currentPlayerXP = _currentPlayerXP!.copyWith(
        lastLuminaHarvest: DateTime.now(),
      );
      
      await _applyXPGain(event);
      
      debugPrint('🌌 Lumina harvested: ${baseLumina.toStringAsFixed(3)}');
      return event;
      
    } catch (e) {
      log('Error harvesting Lumina: $e');
      throw XPServiceException('Failed to harvest Lumina');
    }
  }
  
  /// Process daily login and streak rewards
  Future<XPGainEvent?> processDailyLogin({
    required String playerId,
  }) async {
    try {
      if (_currentPlayerXP == null) {
        throw XPServiceException('Player XP not initialized');
      }
      
      final now = DateTime.now();
      final today = DateTime(now.year, now.month, now.day);
      final lastActiveDay = DateTime(
        _currentPlayerXP!.lastActiveDate.year,
        _currentPlayerXP!.lastActiveDate.month,
        _currentPlayerXP!.lastActiveDate.day,
      );
      
      // Check if already claimed today
      if (lastActiveDay.isAtSameMomentAs(today)) {
        return null; // Already claimed today
      }
      
      // Calculate new streak
      int newStreakDays;
      final yesterday = today.subtract(const Duration(days: 1));
      
      if (lastActiveDay.isAtSameMomentAs(yesterday)) {
        // Consecutive day
        newStreakDays = _currentPlayerXP!.consecutiveDays + 1;
      } else {
        // Streak broken, restart
        newStreakDays = 1;
      }
      
      // Generate daily reward
      final dailyReward = DailyStreakReward.calculateReward(newStreakDays);
      
      final event = XPGainEvent(
        eventId: _generateEventId(),
        playerId: playerId,
        type: XPGainType.dailyReward,
        stellarShardsGained: dailyReward.stellarShardsReward,
        luminaGained: dailyReward.luminaReward,
        description: dailyReward.description,
        timestamp: now,
        metadata: {
          'streak_days': newStreakDays,
          'is_milestone': dailyReward.isMilestone,
          'special_rewards': dailyReward.specialRewards,
        },
      );
      
      // Update player data
      _currentPlayerXP = _currentPlayerXP!.copyWith(
        consecutiveDays: newStreakDays,
        lastActiveDate: now,
      );
      
      await _applyXPGain(event);
      
      debugPrint('🎁 Daily reward claimed: Streak ${newStreakDays} days');
      return event;
      
    } catch (e) {
      log('Error processing daily login: $e');
      throw XPServiceException('Failed to process daily login');
    }
  }
  
  /// Upgrade Cosmic Genesis Node with Lumina
  Future<bool> upgradeCosmicGenesisNode({
    required String playerId,
    required String nodeId,
  }) async {
    try {
      if (_currentPlayerXP == null) {
        throw XPServiceException('Player XP not initialized');
      }
      
      final currentGrid = Map<String, dynamic>.from(_currentPlayerXP!.cosmicGenesisGrid);
      final nodeData = currentGrid[nodeId];
      
      if (nodeData == null) {
        throw XPServiceException('Invalid node ID: $nodeId');
      }
      
      final currentLevel = nodeData['level'] as int;
      final maxLevel = nodeData['max_level'] as int;
      final costMultiplier = nodeData['cost_multiplier'] as double;
      
      if (currentLevel >= maxLevel) {
        return false; // Already at max level
      }
      
      // Calculate cost
      final baseCost = _getNodeBaseCost(nodeId);
      final upgradeCost = baseCost * math.pow(costMultiplier, currentLevel);
      
      if (_currentPlayerXP!.lumina < upgradeCost) {
        return false; // Insufficient Lumina
      }
      
      // Perform upgrade
      nodeData['level'] = currentLevel + 1;
      currentGrid[nodeId] = nodeData;
      
      // Deduct Lumina
      _currentPlayerXP = _currentPlayerXP!.copyWith(
        lumina: _currentPlayerXP!.lumina - upgradeCost,
        cosmicGenesisGrid: currentGrid,
      );
      
      // Create upgrade event
      final event = XPGainEvent(
        eventId: _generateEventId(),
        playerId: playerId,
        type: XPGainType.genesisActivation,
        stellarShardsGained: 0.0,
        luminaGained: -upgradeCost,
        description: 'Cosmic Node Upgraded! 🔮 ${_getNodeDisplayName(nodeId)} Level ${currentLevel + 1}',
        timestamp: DateTime.now(),
        metadata: {
          'node_id': nodeId,
          'new_level': currentLevel + 1,
          'lumina_cost': upgradeCost,
        },
      );
      
      _recentEvents.add(event);
      await _savePlayerXP(_currentPlayerXP!);
      
      debugPrint('🔮 Upgraded $nodeId to level ${currentLevel + 1}');
      return true;
      
    } catch (e) {
      log('Error upgrading cosmic node: $e');
      throw XPServiceException('Failed to upgrade cosmic node');
    }
  }
  
  /// Get recent XP events for display
  List<XPGainEvent> getRecentEvents({int limit = 10}) {
    return _recentEvents.take(limit).toList();
  }
  
  /// Calculate idle Stellar Shards generation per hour
  double calculateIdleGeneration() {
    if (_currentPlayerXP == null) return 0.0;
    return _currentPlayerXP!.stellarShardsPerHour;
  }
  
  /// Process idle time when app returns from background
  Future<double> processIdleTime(Duration idleTime) async {
    if (_currentPlayerXP == null) return 0.0;
    
    final hoursIdle = idleTime.inMilliseconds / (1000 * 60 * 60);
    final generatedShards = calculateIdleGeneration() * hoursIdle;
    
    // Cap idle generation to prevent exploitation
    final cappedShards = math.min(generatedShards, calculateIdleGeneration() * 8); // Max 8 hours
    
    if (cappedShards > 0) {
      await generateStellarShards(
        playerId: _currentPlayerXP!.playerId,
        baseAmount: cappedShards,
        metadata: {
          'idle_hours': hoursIdle,
          'generation_rate': calculateIdleGeneration(),
        },
      );
    }
    
    return cappedShards;
  }
  
  /// Add XP to user via backend and update local state
  Future<void> addXpToUser({required int userId, required int amount}) async {
    await _backendClient.addXp(userId, amount);
    // Optionally fetch updated user data
    final users = await _backendClient.getUsers();
    final backendUser = users.firstWhere((u) => u.id == userId);
    // Update local XP model if needed
    _currentPlayerXP = PlayerXP(
      playerId: userId.toString(),
      stellarShards: backendUser.xp.toDouble(), // Assuming backendUser.xp maps to stellarShards
      lumina: 0.0, // Assuming lumina is not directly from backendUser.xp
      level: backendUser.level,
      xpToNextLevel: PlayerXP.xpRequiredForLevel(backendUser.level + 1), // Recalculate
      consecutiveDays: 0, // Assuming streak is not directly from backendUser
      lastActiveDate: DateTime.now(),
      createdAt: DateTime.now(),
      lastLuminaHarvest: DateTime.now(),
      cosmicGenesisGrid: PlayerXP.initializeCosmicGrid(), // Initialize default grid
    );
  }
  
  // Private helper methods
  
  String _generateEventId() {
    return 'xp_${DateTime.now().millisecondsSinceEpoch}_${math.Random().nextInt(9999)}';
  }
  
  Future<void> _applyXPGain(XPGainEvent event) async {
    if (_currentPlayerXP == null) return;
    
    // Update XP values
    _currentPlayerXP = _currentPlayerXP!.copyWith(
      stellarShards: _currentPlayerXP!.stellarShards + event.stellarShardsGained,
      lumina: _currentPlayerXP!.lumina + event.luminaGained,
    );
    
    // Check for level up
    final newLevel = _currentPlayerXP!.calculatedLevel;
    if (newLevel > _currentPlayerXP!.level) {
      _currentPlayerXP = _currentPlayerXP!.copyWith(level: newLevel);
      
      // Create level up event
      final levelUpEvent = XPGainEvent(
        eventId: _generateEventId(),
        playerId: _currentPlayerXP!.playerId,
        type: XPGainType.levelUp,
        stellarShardsGained: newLevel * 10.0, // Bonus SS for leveling
        luminaGained: newLevel >= 10 ? 1.0 : 0.0, // Lumina bonus for higher levels
        description: 'Level Up! ⬆️ Cosmic Level $newLevel Achieved',
        timestamp: DateTime.now(),
        metadata: {'new_level': newLevel, 'previous_level': _currentPlayerXP!.level},
      );
      
      _recentEvents.add(levelUpEvent);
    }
    
    // Add event to recent events
    _recentEvents.insert(0, event);
    if (_recentEvents.length > 50) {
      _recentEvents.removeLast();
    }
    
    await _savePlayerXP(_currentPlayerXP!);
  }
  
  Future<double> _calculateTradingEfficiency(String playerId) async {
    // Calculate efficiency based on recent trading success rate
    // This would integrate with trading history in a real implementation
    // For now, return base efficiency with small random variation
    return 0.8 + (math.Random().nextDouble() * 0.4); // 0.8 to 1.2 multiplier
  }
  
  double _getNodeBaseCost(String nodeId) {
    switch (nodeId) {
      case 'graviton_amplifier': return 10.0;
      case 'chrono_accelerator': return 8.0;
      case 'bio_synthesis_nexus': return 12.0;
      case 'quantum_resonator': return 15.0;
      case 'stellar_flux_harmonizer': return 20.0;
      default: return 10.0;
    }
  }
  
  String _getNodeDisplayName(String nodeId) {
    switch (nodeId) {
      case 'graviton_amplifier': return 'Graviton Amplifier';
      case 'chrono_accelerator': return 'Chrono Accelerator';
      case 'bio_synthesis_nexus': return 'Bio-Synthesis Nexus';
      case 'quantum_resonator': return 'Quantum Resonator';
      case 'stellar_flux_harmonizer': return 'Stellar Flux Harmonizer';
      default: return nodeId.replaceAll('_', ' ').titleCase;
    }
  }
  
  Future<PlayerXP?> _loadPlayerXP(String playerId) async {
    // Load player XP data from shared preferences
    try {
      final prefs = await SharedPreferences.getInstance();
      final jsonString = prefs.getString('$_storageKey:$playerId');
      if (jsonString != null) {
        final jsonMap = json.decode(jsonString);
        return PlayerXP.fromJson(jsonMap);
      }
      return null;
    } catch (e) {
      log('Error loading player XP: $e');
      return null;
    }
  }
  
  Future<void> _savePlayerXP(PlayerXP playerXP) async {
    // Save player XP data to shared preferences
    try {
      final prefs = await SharedPreferences.getInstance();
      final jsonString = jsonEncode(playerXP.toJson());
      await prefs.setString('$_storageKey:${playerXP.playerId}', jsonString);
      debugPrint('💾 Saved XP data for player: ${playerXP.playerId}');
    } catch (e) {
      log('Error saving player XP: $e');
    }
  }
}

/// Custom extension for string formatting
extension StringExtension on String {
  String get titleCase {
    return split(' ').map((word) => 
      word.isNotEmpty ? word[0].toUpperCase() + word.substring(1).toLowerCase() : ''
    ).join(' ');
  }
}

/// Exception thrown by XP Service
class XPServiceException implements Exception {
  final String message;
  final String? code;
  
  XPServiceException(this.message, {this.code});
  
  @override
  String toString() {
    return 'XPServiceException: $message${code != null ? ' (Code: $code)' : ''}';
  }
}