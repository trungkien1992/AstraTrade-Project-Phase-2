import 'package:flutter/material.dart';
import 'package:share_plus/share_plus.dart';
// import 'package:screenshot/screenshot.dart'; // COMMENTED OUT - package removed
import 'package:path_provider/path_provider.dart';
import 'package:flutter_image_compress/flutter_image_compress.dart';
import 'dart:io';
import 'dart:typed_data';
import 'dart:ui' as ui;
import 'package:image/image.dart' as img;

/// Service for handling social sharing and meme generation
class SocialSharingService {
  static final SocialSharingService _instance =
      SocialSharingService._internal();
  factory SocialSharingService() => _instance;
  SocialSharingService._internal();

  // final ScreenshotController _screenshotController = ScreenshotController(); // COMMENTED OUT - package removed

  /// Share trading achievement with cosmic-themed message
  Future<void> shareTradingAchievement({
    required String achievement,
    required double stellarShards,
    required double lumina,
    required int level,
    Widget? customWidget,
  }) async {
    final message = _generateCosmicMessage(
      achievement: achievement,
      stellarShards: stellarShards,
      lumina: lumina,
      level: level,
    );

    if (customWidget != null) {
      final imageFile = await _captureWidget(customWidget);
      await Share.shareXFiles(
        [XFile(imageFile.path)],
        text: message,
        subject: 'AstraTrade Cosmic Achievement! 🚀',
      );
    } else {
      await Share.share(message, subject: 'AstraTrade Cosmic Achievement! 🚀');
    }
  }

  /// Share level up achievement with enhanced visuals
  Future<void> shareLevelUp({
    required int newLevel,
    required double totalShards,
    required String specialUnlock,
    Widget? levelUpWidget,
  }) async {
    final message =
        '''
🚀 COSMIC LEVEL UP! 🚀

Level: $newLevel
Total Stellar Shards: ${totalShards.toStringAsFixed(1)} ⭐
Special Unlock: $specialUnlock

Join the cosmic trading adventure!
#AstraTrade #CosmicTrading #LevelUp #Blockchain
''';

    if (levelUpWidget != null) {
      final imageFile = await _captureWidget(levelUpWidget);
      await Share.shareXFiles(
        [XFile(imageFile.path)],
        text: message,
        subject: 'Level Up in AstraTrade! 🌌',
      );
    } else {
      await Share.share(message, subject: 'Level Up in AstraTrade! 🌌');
    }
  }

  /// Share streak achievement
  Future<void> shareStreak({
    required int streakDays,
    required double bonusMultiplier,
    Widget? streakWidget,
  }) async {
    final message =
        '''
🔥 COSMIC STREAK FIRE! 🔥

${streakDays} Day Trading Streak!
Bonus Multiplier: ${((bonusMultiplier - 1.0) * 100).toStringAsFixed(0)}%

The stellar currents are flowing through me! ✨
#AstraTrade #TradingStreak #CosmicPower
''';

    if (streakWidget != null) {
      final imageFile = await _captureWidget(streakWidget);
      await Share.shareXFiles(
        [XFile(imageFile.path)],
        text: message,
        subject: 'Epic Trading Streak! 🔥',
      );
    } else {
      await Share.share(message, subject: 'Epic Trading Streak! 🔥');
    }
  }

  /// Share rare artifact discovery
  Future<void> shareArtifactDiscovery({
    required String artifactName,
    required String rarity,
    required String effect,
    Widget? artifactWidget,
  }) async {
    final rarityEmoji = _getRarityEmoji(rarity);
    final message =
        '''
$rarityEmoji COSMIC ARTIFACT DISCOVERED! $rarityEmoji

Artifact: $artifactName
Rarity: ${rarity.toUpperCase()}
Effect: $effect

The universe has blessed my trading journey! 🌌
#AstraTrade #CosmicArtifact #$rarity #Trading
''';

    if (artifactWidget != null) {
      final imageFile = await _captureWidget(artifactWidget);
      await Share.shareXFiles(
        [XFile(imageFile.path)],
        text: message,
        subject: 'Rare Cosmic Artifact! $rarityEmoji',
      );
    } else {
      await Share.share(message, subject: 'Rare Cosmic Artifact! $rarityEmoji');
    }
  }

  /// Generate and share a trading meme
  Future<void> shareCosmicMeme({
    required String memeType,
    required Map<String, dynamic> memeData,
  }) async {
    final memeWidget = _generateMemeWidget(memeType, memeData);
    final imageFile = await _captureWidget(memeWidget);

    final memeMessage = _generateMemeMessage(memeType, memeData);

    await Share.shareXFiles(
      [XFile(imageFile.path)],
      text: memeMessage,
      subject: 'AstraTrade Cosmic Meme! 😂',
    );
  }

  /// Capture a widget as an image file (simplified version)
  Future<File> _captureWidget(Widget widget) async {
    final directory = await getTemporaryDirectory();
    final imagePath =
        '${directory.path}/cosmic_share_${DateTime.now().millisecondsSinceEpoch}.png';

    // For now, create a placeholder file
    // In a real implementation, this would use screenshot or render techniques
    final file = File(imagePath);
    await file.writeAsBytes(
      Uint8List.fromList([0x89, 0x50, 0x4E, 0x47]),
    ); // PNG header

    return file;
  }

  /// Generate cosmic-themed message
  String _generateCosmicMessage({
    required String achievement,
    required double stellarShards,
    required double lumina,
    required int level,
  }) {
    final cosmicPhrases = [
      'The stellar currents flow through me!',
      'Harnessing the power of the cosmos!',
      'Trading through the quantum void!',
      'Channeling cosmic energy into profits!',
      'The universe aligns with my trades!',
    ];

    final randomPhrase =
        cosmicPhrases[DateTime.now().millisecondsSinceEpoch %
            cosmicPhrases.length];

    return '''
🌌 COSMIC TRADING ACHIEVEMENT! 🌌

$achievement

Level: $level
Stellar Shards: ${stellarShards.toStringAsFixed(1)} ⭐
Lumina: ${lumina.toStringAsFixed(2)} 🌟

$randomPhrase

Join the cosmic trading revolution!
#AstraTrade #CosmicTrading #Blockchain #DeFi
''';
  }

  /// Generate meme widget based on type
  Widget _generateMemeWidget(String memeType, Map<String, dynamic> data) {
    switch (memeType) {
      case 'profit_explosion':
        return _buildProfitExplosionMeme(data);
      case 'loss_protection':
        return _buildLossProtectionMeme(data);
      case 'streak_fire':
        return _buildStreakFireMeme(data);
      case 'artifact_discovery':
        return _buildArtifactDiscoveryMeme(data);
      default:
        return _buildGenericCosmicMeme(data);
    }
  }

  /// Build profit explosion meme
  Widget _buildProfitExplosionMeme(Map<String, dynamic> data) {
    return Container(
      width: 400,
      height: 600,
      decoration: const BoxDecoration(
        gradient: RadialGradient(
          colors: [Color(0xFF1a0033), Color(0xFF000000)],
        ),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Text(
            '🚀 PROFIT EXPLOSION! 🚀',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Colors.cyan,
            ),
          ),
          const SizedBox(height: 20),
          Text(
            'Stellar Shards: +${data['shards']?.toStringAsFixed(1) ?? '0.0'}',
            style: const TextStyle(fontSize: 18, color: Colors.white),
          ),
          const SizedBox(height: 10),
          Text(
            'Lumina: +${data['lumina']?.toStringAsFixed(2) ?? '0.0'}',
            style: const TextStyle(fontSize: 18, color: Colors.purple),
          ),
          const SizedBox(height: 30),
          const Text(
            'The cosmos rewards\nthe bold traders!',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey,
              fontStyle: FontStyle.italic,
            ),
          ),
          const SizedBox(height: 20),
          const Text(
            'Join AstraTrade',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
        ],
      ),
    );
  }

  /// Build loss protection meme
  Widget _buildLossProtectionMeme(Map<String, dynamic> data) {
    return Container(
      width: 400,
      height: 600,
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          colors: [Color(0xFF330011), Color(0xFF000000)],
        ),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Text(
            '🛡️ COSMIC PROTECTION! 🛡️',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Colors.orange,
            ),
          ),
          const SizedBox(height: 20),
          Text(
            'Trade Amount: \$${data['amount']?.toStringAsFixed(2) ?? '0.0'}',
            style: const TextStyle(fontSize: 18, color: Colors.white),
          ),
          const SizedBox(height: 10),
          Text(
            'Consolation Shards: +${data['consolation']?.toStringAsFixed(1) ?? '0.0'}',
            style: const TextStyle(fontSize: 18, color: Colors.cyan),
          ),
          const SizedBox(height: 30),
          const Text(
            'Even the cosmos teaches\nthrough challenges!',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey,
              fontStyle: FontStyle.italic,
            ),
          ),
          const SizedBox(height: 20),
          const Text(
            'AstraTrade - Learn & Earn',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
        ],
      ),
    );
  }

  /// Build streak fire meme
  Widget _buildStreakFireMeme(Map<String, dynamic> data) {
    return Container(
      width: 400,
      height: 600,
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          colors: [Color(0xFF331100), Color(0xFF000000)],
        ),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Text(
            '🔥 STREAK ON FIRE! 🔥',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Colors.orange,
            ),
          ),
          const SizedBox(height: 20),
          Text(
            '${data['days']} Day Streak!',
            style: const TextStyle(
              fontSize: 32,
              fontWeight: FontWeight.bold,
              color: Colors.red,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            'Bonus: ${data['bonus']?.toStringAsFixed(0) ?? '0'}%',
            style: const TextStyle(fontSize: 18, color: Colors.yellow),
          ),
          const SizedBox(height: 30),
          const Text(
            'Consistency is the path\nto cosmic mastery!',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey,
              fontStyle: FontStyle.italic,
            ),
          ),
          const SizedBox(height: 20),
          const Text(
            'Keep the fire burning!',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
        ],
      ),
    );
  }

  /// Build artifact discovery meme
  Widget _buildArtifactDiscoveryMeme(Map<String, dynamic> data) {
    final rarity = data['rarity'] ?? 'common';
    final rarityColor = _getRarityColor(rarity);
    final rarityEmoji = _getRarityEmoji(rarity);

    return Container(
      width: 400,
      height: 600,
      decoration: BoxDecoration(
        gradient: RadialGradient(
          colors: [rarityColor.withOpacity(0.3), const Color(0xFF000000)],
        ),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            '$rarityEmoji ARTIFACT FOUND! $rarityEmoji',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: rarityColor,
            ),
          ),
          const SizedBox(height: 20),
          Text(
            data['name'] ?? 'Unknown Artifact',
            style: TextStyle(
              fontSize: 22,
              fontWeight: FontWeight.bold,
              color: rarityColor,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            rarity.toUpperCase(),
            style: TextStyle(fontSize: 18, color: rarityColor),
          ),
          const SizedBox(height: 20),
          Text(
            data['effect'] ?? 'Mystical cosmic power',
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 16, color: Colors.white),
          ),
          const SizedBox(height: 30),
          const Text(
            'The universe reveals\nits secrets to worthy traders!',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey,
              fontStyle: FontStyle.italic,
            ),
          ),
          const SizedBox(height: 20),
          const Text(
            'Collect them all in AstraTrade!',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
        ],
      ),
    );
  }

  /// Build generic cosmic meme
  Widget _buildGenericCosmicMeme(Map<String, dynamic> data) {
    return Container(
      width: 400,
      height: 600,
      decoration: const BoxDecoration(
        gradient: RadialGradient(
          colors: [Color(0xFF1a0033), Color(0xFF000000)],
        ),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Text(
            '🌌 COSMIC TRADING 🌌',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Colors.cyan,
            ),
          ),
          const SizedBox(height: 20),
          Text(
            data['message'] ?? 'Trading through the stars!',
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 18, color: Colors.white),
          ),
          const SizedBox(height: 30),
          const Text(
            'Join the cosmic revolution!',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
        ],
      ),
    );
  }

  /// Generate meme message based on type
  String _generateMemeMessage(String memeType, Map<String, dynamic> data) {
    switch (memeType) {
      case 'profit_explosion':
        return '''
🚀 PROFIT EXPLOSION MEME! 🚀

When the stellar currents align perfectly! ✨
Stellar Shards: +${data['shards']?.toStringAsFixed(1) ?? '0.0'}
Lumina: +${data['lumina']?.toStringAsFixed(2) ?? '0.0'}

#AstraTrade #CosmicMeme #ProfitExplosion
''';
      case 'loss_protection':
        return '''
🛡️ COSMIC PROTECTION MEME! 🛡️

Even failed trades teach us wisdom! 📚
Consolation Shards: +${data['consolation']?.toStringAsFixed(1) ?? '0.0'}

#AstraTrade #CosmicMeme #LearningExperience
''';
      case 'streak_fire':
        return '''
🔥 STREAK FIRE MEME! 🔥

${data['days']} days of cosmic consistency! 
Bonus: ${data['bonus']?.toStringAsFixed(0) ?? '0'}%

#AstraTrade #CosmicMeme #StreakFire
''';
      case 'artifact_discovery':
        return '''
${_getRarityEmoji(data['rarity'])} ARTIFACT MEME! ${_getRarityEmoji(data['rarity'])}

Found: ${data['name']}
Rarity: ${data['rarity']?.toUpperCase()}

#AstraTrade #CosmicMeme #ArtifactDiscovery
''';
      default:
        return '''
🌌 COSMIC TRADING MEME! 🌌

${data['message'] ?? 'Trading through the stars!'}

#AstraTrade #CosmicMeme #Trading
''';
    }
  }

  /// Get rarity emoji
  String _getRarityEmoji(String rarity) {
    switch (rarity.toLowerCase()) {
      case 'legendary':
        return '🌟';
      case 'epic':
        return '⭐';
      case 'rare':
        return '💎';
      case 'common':
        return '✨';
      default:
        return '⚡';
    }
  }

  /// Get rarity color
  Color _getRarityColor(String rarity) {
    switch (rarity.toLowerCase()) {
      case 'legendary':
        return Colors.orange;
      case 'epic':
        return Colors.purple;
      case 'rare':
        return Colors.blue;
      case 'common':
        return Colors.green;
      default:
        return Colors.grey;
    }
  }
}
