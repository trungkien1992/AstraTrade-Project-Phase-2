import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:vibration/vibration.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/simple_trade.dart';
import '../models/simple_gamification.dart';

/// Mobile-native haptic feedback service for trading app
/// Provides contextual vibration patterns for different trading events
class MobileHapticService {
  static final _instance = MobileHapticService._internal();
  factory MobileHapticService() => _instance;
  MobileHapticService._internal();
  
  bool _isEnabled = true;
  bool _isInitialized = false;
  double _intensityMultiplier = 1.0;
  
  /// Initialize haptic service
  Future<void> initialize() async {
    if (_isInitialized) return;
    
    try {
      await _loadSettings();
      
      // Test haptic capability
      final hasVibrator = await Vibration.hasVibrator() ?? false;
      if (!hasVibrator) {
        debugPrint('📳 Device does not support vibration');
        _isEnabled = false;
      }
      
      _isInitialized = true;
      debugPrint('📳 Mobile haptic service initialized (enabled: $_isEnabled)');
      
    } catch (e) {
      debugPrint('❌ Failed to initialize haptics: $e');
      _isEnabled = false;
    }
  }

  /// Load haptic settings
  Future<void> _loadSettings() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      _isEnabled = prefs.getBool('haptics_enabled') ?? true;
      _intensityMultiplier = prefs.getDouble('haptic_intensity') ?? 1.0;
    } catch (e) {
      debugPrint('⚠️ Failed to load haptic settings: $e');
    }
  }

  /// Save haptic settings
  Future<void> _saveSettings() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool('haptics_enabled', _isEnabled);
      await prefs.setDouble('haptic_intensity', _intensityMultiplier);
    } catch (e) {
      debugPrint('⚠️ Failed to save haptic settings: $e');
    }
  }

  /// Basic tap feedback
  Future<void> lightTap() async {
    if (!_shouldVibrate()) return;
    
    try {
      await HapticFeedback.lightImpact();
    } catch (e) {
      debugPrint('❌ Light tap haptic failed: $e');
    }
  }

  /// Medium tap feedback
  Future<void> mediumTap() async {
    if (!_shouldVibrate()) return;
    
    try {
      await HapticFeedback.mediumImpact();
    } catch (e) {
      debugPrint('❌ Medium tap haptic failed: $e');
    }
  }

  /// Heavy tap feedback
  Future<void> heavyTap() async {
    if (!_shouldVibrate()) return;
    
    try {
      await HapticFeedback.heavyImpact();
    } catch (e) {
      debugPrint('❌ Heavy tap haptic failed: $e');
    }
  }

  /// Selection feedback
  Future<void> selectionClick() async {
    if (!_shouldVibrate()) return;
    
    try {
      await HapticFeedback.selectionClick();
    } catch (e) {
      debugPrint('❌ Selection click haptic failed: $e');
    }
  }

  /// Trade execution feedback
  Future<void> tradeExecuted({required bool isRealTrade}) async {
    if (!_shouldVibrate()) return;
    
    try {
      if (isRealTrade) {
        // Real trade: Strong, confident pattern
        await _customVibration([0, 100, 50, 150, 50, 200]);
      } else {
        // Practice trade: Light, quick pattern
        await _customVibration([0, 50, 30, 50]);
      }
    } catch (e) {
      debugPrint('❌ Trade execution haptic failed: $e');
    }
  }

  /// Trade completion feedback
  Future<void> tradeCompleted({
    required SimpleTrade trade,
    required bool isProfit,
  }) async {
    if (!_shouldVibrate()) return;
    
    try {
      final profit = trade.profitLoss ?? 0.0;
      
      if (isProfit) {
        if (profit > 100) {
          // Big profit: Celebration pattern
          await _customVibration([0, 200, 100, 300, 100, 400, 100, 500]);
        } else {
          // Small profit: Success pattern
          await _customVibration([0, 100, 50, 150, 50, 100]);
        }
      } else {
        if (profit < -100) {
          // Big loss: Heavy warning pattern
          await _customVibration([0, 300, 200, 300, 200, 300]);
        } else {
          // Small loss: Gentle warning pattern
          await _customVibration([0, 150, 100, 150]);
        }
      }
    } catch (e) {
      debugPrint('❌ Trade completion haptic failed: $e');
    }
  }

  /// Achievement unlock feedback
  Future<void> achievementUnlocked({required AchievementRarity rarity}) async {
    if (!_shouldVibrate()) return;
    
    try {
      switch (rarity) {
        case AchievementRarity.common:
          await _customVibration([0, 100, 50, 100]);
          break;
        case AchievementRarity.uncommon:
          await _customVibration([0, 150, 75, 150, 75, 150]);
          break;
        case AchievementRarity.rare:
          await _customVibration([0, 200, 100, 200, 100, 200, 100, 200]);
          break;
        case AchievementRarity.epic:
          await _customVibration([0, 250, 125, 300, 125, 350, 125, 400]);
          break;
        case AchievementRarity.legendary:
          await _customVibration([0, 400, 200, 500, 200, 600, 200, 700, 200, 800]);
          break;
      }
    } catch (e) {
      debugPrint('❌ Achievement haptic failed: $e');
    }
  }

  /// Level up feedback
  Future<void> levelUp({required int newLevel}) async {
    if (!_shouldVibrate()) return;
    
    try {
      // Level up: Ascending pattern
      final pattern = <int>[0];
      for (int i = 1; i <= 5; i++) {
        pattern.addAll([100 + (i * 20), 50]);
      }
      pattern.add(300); // Final strong vibration
      
      await _customVibration(pattern);
    } catch (e) {
      debugPrint('❌ Level up haptic failed: $e');
    }
  }

  /// Daily streak feedback
  Future<void> dailyStreak({required int streakDays, required bool isMilestone}) async {
    if (!_shouldVibrate()) return;
    
    try {
      if (isMilestone) {
        // Milestone: Celebration pattern
        await _customVibration([0, 200, 100, 250, 100, 300, 100, 350, 100, 400]);
      } else {
        // Regular streak: Simple positive pattern
        await _customVibration([0, 100, 50, 120, 50, 140]);
      }
    } catch (e) {
      debugPrint('❌ Daily streak haptic failed: $e');
    }
  }

  /// Error feedback
  Future<void> error({bool isSerious = false}) async {
    if (!_shouldVibrate()) return;
    
    try {
      if (isSerious) {
        // Serious error: Strong warning pattern
        await _customVibration([0, 400, 200, 400, 200, 400]);
      } else {
        // Minor error: Gentle warning
        await _customVibration([0, 200, 100, 200]);
      }
    } catch (e) {
      debugPrint('❌ Error haptic failed: $e');
    }
  }

  /// Success feedback
  Future<void> success({bool isMajor = false}) async {
    if (!_shouldVibrate()) return;
    
    try {
      if (isMajor) {
        // Major success: Celebration pattern
        await _customVibration([0, 150, 75, 200, 75, 250, 75, 300]);
      } else {
        // Minor success: Simple positive pattern
        await _customVibration([0, 100, 50, 150]);
      }
    } catch (e) {
      debugPrint('❌ Success haptic failed: $e');
    }
  }

  /// Warning feedback
  Future<void> warning() async {
    if (!_shouldVibrate()) return;
    
    try {
      await _customVibration([0, 250, 125, 250, 125, 250]);
    } catch (e) {
      debugPrint('❌ Warning haptic failed: $e');
    }
  }

  /// Button press feedback
  Future<void> buttonPress({bool isImportant = false}) async {
    if (!_shouldVibrate()) return;
    
    try {
      if (isImportant) {
        await mediumTap();
      } else {
        await lightTap();
      }
    } catch (e) {
      debugPrint('❌ Button press haptic failed: $e');
    }
  }

  /// Swipe feedback
  Future<void> swipeGesture() async {
    if (!_shouldVibrate()) return;
    
    try {
      await _customVibration([0, 50, 25, 75]);
    } catch (e) {
      debugPrint('❌ Swipe haptic failed: $e');
    }
  }

  /// Long press feedback
  Future<void> longPress() async {
    if (!_shouldVibrate()) return;
    
    try {
      await _customVibration([0, 150, 100, 200]);
    } catch (e) {
      debugPrint('❌ Long press haptic failed: $e');
    }
  }

  /// Enable/disable haptics
  Future<void> setEnabled(bool enabled) async {
    _isEnabled = enabled;
    await _saveSettings();
    debugPrint('📳 Haptics ${enabled ? 'enabled' : 'disabled'}');
  }

  /// Set haptic intensity
  Future<void> setIntensity(double intensity) async {
    _intensityMultiplier = intensity.clamp(0.1, 2.0);
    await _saveSettings();
    debugPrint('📳 Haptic intensity set to ${(_intensityMultiplier * 100).round()}%');
  }

  /// Test haptic patterns
  Future<void> testPattern(String patternName) async {
    if (!_shouldVibrate()) return;
    
    try {
      switch (patternName) {
        case 'light':
          await lightTap();
          break;
        case 'medium':
          await mediumTap();
          break;
        case 'heavy':
          await heavyTap();
          break;
        case 'success':
          await success();
          break;
        case 'error':
          await error();
          break;
        case 'achievement':
          await achievementUnlocked(rarity: AchievementRarity.rare);
          break;
        case 'levelup':
          await levelUp(newLevel: 5);
          break;
        default:
          await mediumTap();
      }
    } catch (e) {
      debugPrint('❌ Test pattern failed: $e');
    }
  }

  /// Custom vibration pattern
  Future<void> _customVibration(List<int> pattern) async {
    try {
      // Apply intensity multiplier
      final adjustedPattern = pattern.map((duration) {
        if (duration == 0) return 0; // Don't modify pauses
        return (duration * _intensityMultiplier).round();
      }).toList();
      
      await Vibration.vibrate(pattern: adjustedPattern);
    } catch (e) {
      // Fallback to basic haptic feedback
      await HapticFeedback.mediumImpact();
    }
  }

  /// Check if should vibrate
  bool _shouldVibrate() {
    return _isInitialized && _isEnabled;
  }

  /// Get haptic settings
  Map<String, dynamic> getSettings() {
    return {
      'enabled': _isEnabled,
      'intensity': _intensityMultiplier,
      'initialized': _isInitialized,
    };
  }
}