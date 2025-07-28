import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
// import 'package:screenshot/screenshot.dart'; // COMMENTED OUT - package removed
import '../services/social_sharing_service.dart';
import '../services/viral_engagement_service.dart' as viral_service;
import '../services/viral_content_service.dart';
import '../models/viral_content.dart';
import '../widgets/cosmic_haptic_button.dart';
import '../core/haptic_feedback.dart' as core_haptic;
import 'package:google_fonts/google_fonts.dart';

/// Widget for social sharing functionality
class SocialSharingWidget extends StatefulWidget {
  final String contentType;
  final Map<String, dynamic> contentData;
  final Widget? customWidget;
  final bool showMemeOptions;

  const SocialSharingWidget({
    super.key,
    required this.contentType,
    required this.contentData,
    this.customWidget,
    this.showMemeOptions = true,
  });

  @override
  State<SocialSharingWidget> createState() => _SocialSharingWidgetState();
}

class _SocialSharingWidgetState extends State<SocialSharingWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;
  late Animation<double> _opacityAnimation;
  
  final SocialSharingService _sharingService = SocialSharingService();
  final viral_service.ViralEngagementService _viralService = viral_service.ViralEngagementService();
  final ViralContentService _viralContentService = ViralContentService();
  // final ScreenshotController _screenshotController = ScreenshotController(); // COMMENTED OUT - package removed
  
  bool _isExpanded = false;
  bool _showMemeGenerator = false;
  bool _showFOMOEvents = false;
  bool _isGeneratingMeme = false;
  bool _isCreatingSnapshot = false;
  String _selectedMemeType = 'trading_win';
  String? _authToken;
  
  List<MemeTemplate> _memeTemplates = [];
  List<FOMOEvent> _activeFOMOEvents = [];
  List<ViralContent> _userContent = [];
  Map<String, dynamic> _socialProofData = {};

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    
    _scaleAnimation = Tween<double>(
      begin: 0.8,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.elasticOut,
    ));
    
    _opacityAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));
    
    _loadViralData();
  }

  /// Load viral content data
  Future<void> _loadViralData() async {
    try {
      final results = await Future.wait([
        _viralContentService.getMemeTemplates(),
        _viralContentService.getActiveFOMOEvents(),
        _viralContentService.getSocialProofData(token: _authToken),
      ]);

      final templatesData = results[0] as Map<String, dynamic>;
      final fomoEvents = results[1] as List<FOMOEvent>;
      final socialProof = results[2] as Map<String, dynamic>;

      if (mounted) {
        setState(() {
          _memeTemplates = _parseMemeTemplates(templatesData);
          _activeFOMOEvents = fomoEvents;
          _socialProofData = socialProof;
        });
      }
    } catch (e) {
      // Silently handle errors for now
      debugPrint('Failed to load viral data: $e');
    }
  }

  /// Parse meme templates from API response
  List<MemeTemplate> _parseMemeTemplates(Map<String, dynamic> data) {
    final templates = <MemeTemplate>[];
    
    for (final category in data.keys) {
      final categoryTemplates = data[category] as List<dynamic>;
      for (final templateData in categoryTemplates) {
        templates.add(MemeTemplate.fromJson(templateData));
      }
    }
    
    return templates;
  }

  @override
  void dispose() {
    _animationController.dispose();
    _viralContentService.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animationController,
      builder: (context, child) {
        return Transform.scale(
          scale: _scaleAnimation.value,
          child: Opacity(
            opacity: _opacityAnimation.value,
            child: _buildSharingInterface(),
          ),
        );
      },
    );
  }

  Widget _buildSharingInterface() {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.8),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.cyan.withOpacity(0.3)),
        boxShadow: [
          BoxShadow(
            color: Colors.cyan.withOpacity(0.1),
            blurRadius: 10,
            spreadRadius: 2,
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Share Header
          _buildShareHeader(),
          
          if (_isExpanded) ...[
            const SizedBox(height: 16),
            // Quick Share Options
            _buildQuickShareOptions(),
            
            if (widget.showMemeOptions) ...[
              const SizedBox(height: 16),
              // Enhanced Meme Generator Toggle
              _buildMemeGeneratorToggle(),
            ],
            
            if (_showMemeGenerator) ...[
              const SizedBox(height: 16),
              // Enhanced Meme Generator
              _buildEnhancedMemeGenerator(),
            ],

            const SizedBox(height: 16),
            // Ecosystem Snapshot Option
            _buildEcosystemSnapshotOption(),

            if (_activeFOMOEvents.isNotEmpty) ...[
              const SizedBox(height: 16),
              // FOMO Events Section
              _buildFOMOEventsSection(),
            ],
            
            const SizedBox(height: 16),
            // Enhanced Viral Stats
            _buildEnhancedViralStats(),

            if (_socialProofData.isNotEmpty) ...[
              const SizedBox(height: 16),
              // Social Proof Display
              _buildSocialProofSection(),
            ],
          ],
        ],
      ),
    );
  }

  Widget _buildShareHeader() {
    return Row(
      children: [
        Icon(
          Icons.share,
          color: Colors.cyan,
          size: 24,
        ),
        const SizedBox(width: 8),
        const Text(
          'Share Your Cosmic Achievement!',
          style: TextStyle(
            color: Colors.white,
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const Spacer(),
        CosmicHapticButton(
          onPressed: () {
            setState(() {
              _isExpanded = !_isExpanded;
            });
            if (_isExpanded) {
              _animationController.forward();
            } else {
              _animationController.reverse();
            }
          },
          hapticPattern: CosmicHapticPattern.light,
          primaryColor: Colors.cyan,
          padding: const EdgeInsets.all(8),
          child: Icon(
            _isExpanded ? Icons.keyboard_arrow_up : Icons.keyboard_arrow_down,
            color: Colors.white,
          ),
        ),
      ],
    );
  }

  Widget _buildQuickShareOptions() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Quick Share Options',
          style: TextStyle(
            color: Colors.white,
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            _buildQuickShareButton(
              icon: Icons.message,
              label: 'Text',
              onPressed: () => _shareContent('text'),
            ),
            _buildQuickShareButton(
              icon: Icons.image,
              label: 'Image',
              onPressed: () => _shareContent('image'),
            ),
            _buildQuickShareButton(
              icon: Icons.link,
              label: 'Link',
              onPressed: () => _shareContent('link'),
            ),
            _buildQuickShareButton(
              icon: Icons.emoji_emotions,
              label: 'Meme',
              onPressed: () => _shareContent('meme'),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildQuickShareButton({
    required IconData icon,
    required String label,
    required VoidCallback onPressed,
  }) {
    return CosmicHapticButton(
      onPressed: onPressed,
      hapticPattern: CosmicHapticPattern.medium,
      primaryColor: Colors.purple,
      padding: const EdgeInsets.all(12),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: Colors.white, size: 24),
          const SizedBox(height: 4),
          Text(
            label,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMemeGeneratorToggle() {
    return Row(
      children: [
        Icon(
          Icons.auto_awesome,
          color: Colors.orange,
          size: 20,
        ),
        const SizedBox(width: 8),
        const Text(
          'Meme Generator',
          style: TextStyle(
            color: Colors.white,
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        const Spacer(),
        Switch(
          value: _showMemeGenerator,
          onChanged: (value) {
            setState(() {
              _showMemeGenerator = value;
            });
          },
          activeColor: Colors.orange,
        ),
      ],
    );
  }

  /// Enhanced meme generator with templates from API
  Widget _buildEnhancedMemeGenerator() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.orange.withOpacity(0.2), Colors.red.withOpacity(0.1)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.orange.withOpacity(0.5)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.auto_awesome, color: Colors.orange, size: 20),
              const SizedBox(width: 8),
              Text(
                'AI Meme Generator',
                style: GoogleFonts.orbitron(
                  color: Colors.orange,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const Spacer(),
              if (_memeTemplates.isNotEmpty)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.orange.withOpacity(0.3),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    '${_memeTemplates.length} templates',
                    style: GoogleFonts.orbitron(
                      color: Colors.orange,
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
            ],
          ),
          
          const SizedBox(height: 16),
          
          // Meme type selection
          Text(
            'Choose Your Vibe',
            style: GoogleFonts.orbitron(
              color: Colors.white,
              fontSize: 14,
              fontWeight: FontWeight.w600,
            ),
          ),
          
          const SizedBox(height: 8),
          
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _buildMemeTypeChip('trading_win', 'Epic Win', Icons.trending_up, Colors.green),
              _buildMemeTypeChip('trading_loss', 'Learning Exp', Icons.school, Colors.blue),
              _buildMemeTypeChip('milestone', 'Achievement', Icons.star, Colors.yellow),
              _buildMemeTypeChip('streak', 'On Fire', Icons.local_fire_department, Colors.red),
              _buildMemeTypeChip('constellation', 'Clan Victory', Icons.groups, Colors.purple),
              _buildMemeTypeChip('nft', 'NFT Flex', Icons.diamond, Colors.cyan),
            ],
          ),
          
          const SizedBox(height: 16),
          
          // Generate button with loading state
          SizedBox(
            width: double.infinity,
            child: CosmicHapticButton(
              onPressed: _isGeneratingMeme ? null : _generateViralMeme,
              hapticPattern: CosmicHapticPattern.success,
              primaryColor: Colors.orange,
              child: _isGeneratingMeme
                  ? Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'Creating Magic...',
                          style: GoogleFonts.orbitron(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    )
                  : Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.auto_awesome, color: Colors.white),
                        const SizedBox(width: 8),
                        Text(
                          'Generate Viral Meme',
                          style: GoogleFonts.orbitron(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
            ),
          ),
          
          // Optimal timing suggestion
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.black.withOpacity(0.3),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                Icon(Icons.schedule, color: Colors.cyan, size: 16),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    ViralContentService.getOptimalSharingTime(),
                    style: const TextStyle(
                      color: Colors.cyan,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Build meme type selection chip
  Widget _buildMemeTypeChip(String type, String label, IconData icon, Color color) {
    final isSelected = _selectedMemeType == type;
    
    return GestureDetector(
      onTap: () {
        core_haptic.HapticFeedback.triggerHaptic(core_haptic.HapticType.selection);
        setState(() {
          _selectedMemeType = type;
        });
      },
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: isSelected ? color.withOpacity(0.3) : Colors.grey.withOpacity(0.2),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected ? color : Colors.grey.withOpacity(0.5),
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              color: isSelected ? color : Colors.grey,
              size: 16,
            ),
            const SizedBox(width: 6),
            Text(
              label,
              style: GoogleFonts.orbitron(
                color: isSelected ? color : Colors.grey,
                fontSize: 12,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildViralStats() {
    return FutureBuilder<Map<String, dynamic>>(
      future: _getViralStats(),
      builder: (context, snapshot) {
        if (!snapshot.hasData) {
          return const SizedBox.shrink();
        }

        final stats = snapshot.data!;
        return Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.purple.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.purple.withOpacity(0.3)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Your Viral Stats',
                style: TextStyle(
                  color: Colors.purple,
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _buildStatItem(
                    'Shares',
                    stats['shares'].toString(),
                    Icons.share,
                    Colors.cyan,
                  ),
                  _buildStatItem(
                    'Viral Score',
                    stats['viralScore'].toStringAsFixed(0),
                    Icons.trending_up,
                    Colors.orange,
                  ),
                  _buildStatItem(
                    'Rank',
                    stats['rank'],
                    Icons.star,
                    Colors.yellow,
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildStatItem(String label, String value, IconData icon, Color color) {
    return Column(
      children: [
        Icon(icon, color: color, size: 20),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            color: color,
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: const TextStyle(
            color: Colors.grey,
            fontSize: 12,
          ),
        ),
      ],
    );
  }

  Future<void> _shareContent(String shareType) async {
    try {
      switch (shareType) {
        case 'text':
          await _shareText();
          break;
        case 'image':
          await _shareImage();
          break;
        case 'link':
          await _shareLink();
          break;
        case 'meme':
          await _generateAndShareMeme();
          break;
      }
      
      // Track the share for viral engagement
      await _viralService.trackShare(
        contentType: widget.contentType,
        platform: 'general',
        metadata: widget.contentData,
      );
      
      // Show success feedback
      _showShareSuccess();
      
    } catch (e) {
      _showShareError(e.toString());
    }
  }

  Future<void> _shareText() async {
    switch (widget.contentType) {
      case 'achievement':
        await _sharingService.shareTradingAchievement(
          achievement: widget.contentData['achievement'] ?? 'Cosmic Achievement',
          stellarShards: widget.contentData['stellarShards'] ?? 0.0,
          lumina: widget.contentData['lumina'] ?? 0.0,
          level: widget.contentData['level'] ?? 1,
        );
        break;
      case 'levelup':
        await _sharingService.shareLevelUp(
          newLevel: widget.contentData['newLevel'] ?? 1,
          totalShards: widget.contentData['totalShards'] ?? 0.0,
          specialUnlock: widget.contentData['specialUnlock'] ?? 'New Powers',
        );
        break;
      case 'streak':
        await _sharingService.shareStreak(
          streakDays: widget.contentData['streakDays'] ?? 1,
          bonusMultiplier: widget.contentData['bonusMultiplier'] ?? 1.0,
        );
        break;
      case 'artifact':
        await _sharingService.shareArtifactDiscovery(
          artifactName: widget.contentData['artifactName'] ?? 'Cosmic Artifact',
          rarity: widget.contentData['rarity'] ?? 'common',
          effect: widget.contentData['effect'] ?? 'Mystical power',
        );
        break;
    }
  }

  Future<void> _shareImage() async {
    if (widget.customWidget != null) {
      await _shareText(); // This will use the custom widget
    } else {
      await _shareText(); // Fallback to text sharing
    }
  }

  Future<void> _shareLink() async {
    // Generate referral link
    final referralCode = 'COSMIC_${DateTime.now().millisecondsSinceEpoch}';
    const baseUrl = 'https://astratrade.app';
    final referralLink = '$baseUrl/join?ref=$referralCode';
    
    await _sharingService.shareTradingAchievement(
      achievement: '${widget.contentData['achievement'] ?? 'Join AstraTrade'}\n\nJoin me: $referralLink',
      stellarShards: widget.contentData['stellarShards'] ?? 0.0,
      lumina: widget.contentData['lumina'] ?? 0.0,
      level: widget.contentData['level'] ?? 1,
    );
  }

  Future<void> _generateAndShareMeme() async {
    await _sharingService.shareCosmicMeme(
      memeType: _selectedMemeType,
      memeData: widget.contentData,
    );
  }

  Future<Map<String, dynamic>> _getViralStats() async {
    return {
      'shares': _viralService.shareCount,
      'viralScore': _viralService.viralScore,
      'rank': _viralService.getViralRank(),
    };
  }

  void _showShareSuccess() {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: const Row(
          children: [
            Icon(Icons.check_circle, color: Colors.green),
            SizedBox(width: 8),
            Text('Cosmic achievement shared! ✨'),
          ],
        ),
        backgroundColor: Colors.green.withOpacity(0.2),
        duration: const Duration(seconds: 2),
      ),
    );
  }

  void _showShareError(String error) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const Icon(Icons.error, color: Colors.red),
            const SizedBox(width: 8),
            Text('Share failed: $error'),
          ],
        ),
        backgroundColor: Colors.red.withOpacity(0.2),
        duration: const Duration(seconds: 3),
      ),
    );
  }

  /// Build ecosystem snapshot option
  Widget _buildEcosystemSnapshotOption() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.blue.withOpacity(0.2), Colors.purple.withOpacity(0.1)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.blue.withOpacity(0.5)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.dashboard, color: Colors.blue, size: 20),
              const SizedBox(width: 8),
              Text(
                'Performance Snapshot',
                style: GoogleFonts.orbitron(
                  color: Colors.blue,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 8),
          
          const Text(
            'Create a beautiful snapshot of your cosmic trading performance',
            style: TextStyle(
              color: Colors.white70,
              fontSize: 14,
            ),
          ),
          
          const SizedBox(height: 12),
          
          SizedBox(
            width: double.infinity,
            child: CosmicHapticButton(
              onPressed: _isCreatingSnapshot ? null : _createEcosystemSnapshot,
              hapticPattern: CosmicHapticPattern.medium,
              primaryColor: Colors.blue,
              child: _isCreatingSnapshot
                  ? Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'Creating Snapshot...',
                          style: GoogleFonts.orbitron(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    )
                  : Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.dashboard, color: Colors.white),
                        const SizedBox(width: 8),
                        Text(
                          'Create Performance Snapshot',
                          style: GoogleFonts.orbitron(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
            ),
          ),
        ],
      ),
    );
  }

  /// Build FOMO events section
  Widget _buildFOMOEventsSection() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.red.withOpacity(0.2), Colors.orange.withOpacity(0.1)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.red.withOpacity(0.5)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.bolt, color: Colors.red, size: 20),
              const SizedBox(width: 8),
              Text(
                'FOMO Events',
                style: GoogleFonts.orbitron(
                  color: Colors.red,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.red.withOpacity(0.3),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  '${_activeFOMOEvents.where((e) => e.isCurrentlyActive).length} LIVE',
                  style: GoogleFonts.orbitron(
                    color: Colors.red,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 12),
          
          ...(_activeFOMOEvents.take(2).map((event) => _buildFOMOEventCard(event))),
          
          if (_activeFOMOEvents.length > 2) ...[
            const SizedBox(height: 8),
            Center(
              child: TextButton(
                onPressed: () {
                  // Show all FOMO events
                },
                child: Text(
                  'View ${_activeFOMOEvents.length - 2} more events',
                  style: GoogleFonts.orbitron(
                    color: Colors.red,
                    fontSize: 12,
                  ),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  /// Build FOMO event card
  Widget _buildFOMOEventCard(FOMOEvent event) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.3),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Color(int.parse('0xFF${event.urgencyLevelColor.substring(1)}')),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  event.eventName,
                  style: GoogleFonts.orbitron(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: Color(int.parse('0xFF${event.urgencyLevelColor.substring(1)}')),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  event.urgencyLevelName,
                  style: GoogleFonts.orbitron(
                    color: Colors.black,
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 4),
          
          Text(
            event.description,
            style: const TextStyle(
              color: Colors.white70,
              fontSize: 12,
            ),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          
          const SizedBox(height: 8),
          
          Row(
            children: [
              Icon(Icons.timer, color: Colors.orange, size: 16),
              const SizedBox(width: 4),
              Text(
                event.timeRemainingDisplay,
                style: const TextStyle(
                  color: Colors.orange,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const Spacer(),
              if (event.maxParticipants != null)
                Text(
                  '${event.currentParticipants}/${event.maxParticipants}',
                  style: const TextStyle(
                    color: Colors.white60,
                    fontSize: 12,
                  ),
                ),
            ],
          ),
        ],
      ),
    );
  }

  /// Build enhanced viral stats
  Widget _buildEnhancedViralStats() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.purple.withOpacity(0.2), Colors.pink.withOpacity(0.1)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.purple.withOpacity(0.5)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.trending_up, color: Colors.purple, size: 20),
              const SizedBox(width: 8),
              Text(
                'Your Viral Impact',
                style: GoogleFonts.orbitron(
                  color: Colors.purple,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 16),
          
          FutureBuilder<Map<String, dynamic>>(
            future: _getEnhancedViralStats(),
            builder: (context, snapshot) {
              if (!snapshot.hasData) {
                return const Center(
                  child: CircularProgressIndicator(
                    valueColor: AlwaysStoppedAnimation<Color>(Colors.purple),
                  ),
                );
              }

              final stats = snapshot.data!;
              return Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _buildStatItem(
                    'Content',
                    stats['totalContent'].toString(),
                    Icons.library_add,
                    Colors.cyan,
                  ),
                  _buildStatItem(
                    'Viral Score',
                    stats['viralScore'].toStringAsFixed(0),
                    Icons.whatshot,
                    Colors.orange,
                  ),
                  _buildStatItem(
                    'Shares',
                    stats['totalShares'].toString(),
                    Icons.share,
                    Colors.green,
                  ),
                  _buildStatItem(
                    'Rank',
                    stats['viralRank'],
                    Icons.star,
                    Colors.yellow,
                  ),
                ],
              );
            },
          ),
        ],
      ),
    );
  }

  /// Build social proof section
  Widget _buildSocialProofSection() {
    final trendingContent = _socialProofData['trending_content'] as List<dynamic>? ?? [];
    final viralMomentum = _socialProofData['viral_momentum'] as double? ?? 0.0;
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.green.withOpacity(0.2), Colors.blue.withOpacity(0.1)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.green.withOpacity(0.5)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.insights, color: Colors.green, size: 20),
              const SizedBox(width: 8),
              Text(
                'Community Buzz',
                style: GoogleFonts.orbitron(
                  color: Colors.green,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.green.withOpacity(0.3),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  '${viralMomentum.toStringAsFixed(1)}% momentum',
                  style: GoogleFonts.orbitron(
                    color: Colors.green,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 12),
          
          if (trendingContent.isNotEmpty) ...[
            Text(
              'Trending Now',
              style: GoogleFonts.orbitron(
                color: Colors.white,
                fontSize: 14,
                fontWeight: FontWeight.w600,
              ),
            ),
            
            const SizedBox(height: 8),
            
            ...trendingContent.take(3).map((content) {
              return Container(
                margin: const EdgeInsets.only(bottom: 4),
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.black.withOpacity(0.3),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Icon(
                      _getContentTypeIcon(content['content_type']),
                      color: Colors.green,
                      size: 16,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        content['title'] ?? 'Trending Content',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 12,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    Text(
                      '🔥 ${content['viral_score']}',
                      style: const TextStyle(
                        color: Colors.orange,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              );
            }).toList(),
          ],
        ],
      ),
    );
  }

  /// Generate viral meme using enhanced API
  Future<void> _generateViralMeme() async {
    if (_authToken == null) {
      _showShareError('Please log in to generate memes');
      return;
    }

    setState(() {
      _isGeneratingMeme = true;
    });

    try {
      core_haptic.HapticFeedback.triggerHaptic(core_haptic.HapticType.heavy);
      
      final meme = await _viralContentService.generateMeme(
        token: _authToken!,
        memeType: _selectedMemeType,
        tradingData: widget.contentData,
        customText: widget.contentData['customText'],
      );

      // Share the generated meme
      await _shareMemeToSocial(meme);
      
      core_haptic.HapticFeedback.triggerHaptic(core_haptic.HapticType.success);
      _showMemeSuccess(meme);
      
    } catch (e) {
      _showShareError('Failed to generate meme: $e');
    } finally {
      setState(() {
        _isGeneratingMeme = false;
      });
    }
  }

  /// Create ecosystem snapshot
  Future<void> _createEcosystemSnapshot() async {
    if (_authToken == null) {
      _showShareError('Please log in to create snapshots');
      return;
    }

    setState(() {
      _isCreatingSnapshot = true;
    });

    try {
      core_haptic.HapticFeedback.triggerHaptic(core_haptic.HapticType.medium);
      
      final snapshot = await _viralContentService.createEcosystemSnapshot(
        token: _authToken!,
      );

      // Share the snapshot
      await _shareSnapshotToSocial(snapshot);
      
      core_haptic.HapticFeedback.triggerHaptic(core_haptic.HapticType.success);
      _showSnapshotSuccess(snapshot);
      
    } catch (e) {
      _showShareError('Failed to create snapshot: $e');
    } finally {
      setState(() {
        _isCreatingSnapshot = false;
      });
    }
  }

  /// Share meme to social platforms
  Future<void> _shareMemeToSocial(ViralContent meme) async {
    await _viralContentService.shareMeme(
      token: _authToken!,
      memeId: meme.id,
      platforms: ['twitter', 'instagram', 'discord'],
      customMessage: 'Check out my cosmic trading meme! 🚀',
    );
  }

  /// Share snapshot to social platforms
  Future<void> _shareSnapshotToSocial(ViralContent snapshot) async {
    // Use existing social sharing service for snapshot
    await _sharingService.shareTradingAchievement(
      achievement: snapshot.contentTitle,
      stellarShards: widget.contentData['stellarShards'] ?? 0.0,
      lumina: widget.contentData['lumina'] ?? 0.0,
      level: widget.contentData['level'] ?? 1,
    );
  }

  /// Get enhanced viral stats
  Future<Map<String, dynamic>> _getEnhancedViralStats() async {
    try {
      if (_authToken != null) {
        final userContent = await _viralContentService.getUserViralContent(
          token: _authToken!,
          limit: 100,
        );
        
        final totalShares = userContent.fold<int>(0, (sum, content) => sum + content.shareCount);
        final totalViralScore = userContent.fold<double>(0, (sum, content) => sum + content.viralScore);
        
        return {
          'totalContent': userContent.length,
          'totalShares': totalShares,
          'viralScore': totalViralScore,
          'viralRank': _calculateViralRank(totalViralScore),
        };
      }
    } catch (e) {
      debugPrint('Failed to get enhanced viral stats: $e');
    }
    
    // Fallback to basic stats
    return {
      'totalContent': 0,
      'totalShares': 0,
      'viralScore': 0.0,
      'viralRank': 'Rookie',
    };
  }

  /// Calculate viral rank based on score
  String _calculateViralRank(double viralScore) {
    if (viralScore >= 10000) return 'Cosmic Legend';
    if (viralScore >= 5000) return 'Viral Master';
    if (viralScore >= 2000) return 'Trending Star';
    if (viralScore >= 500) return 'Rising Creator';
    if (viralScore >= 100) return 'Active Sharer';
    return 'Cosmic Rookie';
  }

  /// Get content type icon
  IconData _getContentTypeIcon(String contentType) {
    switch (contentType) {
      case 'meme':
        return Icons.emoji_emotions;
      case 'snapshot':
        return Icons.dashboard;
      case 'achievement':
        return Icons.star;
      case 'nft':
        return Icons.diamond;
      default:
        return Icons.share;
    }
  }

  /// Show meme generation success
  void _showMemeSuccess(ViralContent meme) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(Icons.auto_awesome, color: Colors.orange),
            const SizedBox(width: 8),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    'Meme created successfully! 🎉',
                    style: GoogleFonts.orbitron(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    'Viral score: ${meme.viralScore}',
                    style: const TextStyle(fontSize: 12),
                  ),
                ],
              ),
            ),
          ],
        ),
        backgroundColor: Colors.orange.withOpacity(0.2),
        duration: const Duration(seconds: 3),
      ),
    );
  }

  /// Show snapshot creation success
  void _showSnapshotSuccess(ViralContent snapshot) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(Icons.dashboard, color: Colors.blue),
            const SizedBox(width: 8),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    'Performance snapshot created! 📊',
                    style: GoogleFonts.orbitron(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    'Share your cosmic progress!',
                    style: const TextStyle(fontSize: 12),
                  ),
                ],
              ),
            ),
          ],
        ),
        backgroundColor: Colors.blue.withOpacity(0.2),
        duration: const Duration(seconds: 3),
      ),
    );
  }
}