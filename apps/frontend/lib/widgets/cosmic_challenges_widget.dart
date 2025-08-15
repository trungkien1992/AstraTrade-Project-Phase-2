import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../services/cosmic_challenge_service.dart';

/// Cosmic challenges display widget
/// Shows daily challenges with progress and rewards
class CosmicChallengesWidget extends StatefulWidget {
  final bool isExpanded;
  final VoidCallback? onToggle;
  final Function(ChallengeRewards)? onRewardsClaimed;

  const CosmicChallengesWidget({
    super.key,
    this.isExpanded = false,
    this.onToggle,
    this.onRewardsClaimed,
  });

  @override
  State<CosmicChallengesWidget> createState() => _CosmicChallengesWidgetState();
}

class _CosmicChallengesWidgetState extends State<CosmicChallengesWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _expandAnimation;
  late Animation<double> _rotationAnimation;

  @override
  void initState() {
    super.initState();

    _animationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );

    _expandAnimation = CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    );

    _rotationAnimation = Tween<double>(begin: 0.0, end: 0.5).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeInOut),
    );

    if (widget.isExpanded) {
      _animationController.forward();
    }
  }

  @override
  void didUpdateWidget(CosmicChallengesWidget oldWidget) {
    super.didUpdateWidget(oldWidget);

    if (widget.isExpanded != oldWidget.isExpanded) {
      if (widget.isExpanded) {
        _animationController.forward();
      } else {
        _animationController.reverse();
      }
    }
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final challenges = CosmicChallengeService.getTodaysChallenges();
    final completionRate = CosmicChallengeService.getChallengeCompletionRate();
    final completedCount =
        CosmicChallengeService.getCompletedChallenges().length;

    return Card(
      elevation: 8,
      color: Colors.deepPurple.shade900,
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          gradient: LinearGradient(
            colors: [Colors.deepPurple.shade800, Colors.indigo.shade800],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          border: Border.all(color: Colors.purple.withOpacity(0.5), width: 1),
        ),
        child: Column(
          children: [
            // Header
            InkWell(
              onTap: () {
                widget.onToggle?.call();
                HapticFeedback.lightImpact();
              },
              borderRadius: const BorderRadius.vertical(
                top: Radius.circular(12),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Colors.purple.withOpacity(0.3),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: const Icon(
                        Icons.emoji_events,
                        color: Colors.amber,
                        size: 24,
                      ),
                    ),

                    const SizedBox(width: 12),

                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              const Text(
                                'Daily Cosmic Challenges',
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.white,
                                ),
                              ),
                              const SizedBox(width: 8),
                              if (completedCount > 0)
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 6,
                                    vertical: 2,
                                  ),
                                  decoration: BoxDecoration(
                                    color: Colors.green,
                                    borderRadius: BorderRadius.circular(10),
                                  ),
                                  child: Text(
                                    '$completedCount/${challenges.length}',
                                    style: const TextStyle(
                                      fontSize: 10,
                                      fontWeight: FontWeight.bold,
                                      color: Colors.white,
                                    ),
                                  ),
                                ),
                            ],
                          ),
                          const SizedBox(height: 4),
                          Row(
                            children: [
                              Expanded(
                                child: LinearProgressIndicator(
                                  value: completionRate,
                                  backgroundColor: Colors.white24,
                                  valueColor: AlwaysStoppedAnimation<Color>(
                                    completionRate == 1.0
                                        ? Colors.amber
                                        : Colors.cyan,
                                  ),
                                ),
                              ),
                              const SizedBox(width: 8),
                              Text(
                                '${(completionRate * 100).round()}%',
                                style: const TextStyle(
                                  fontSize: 12,
                                  color: Colors.white70,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(width: 8),

                    RotationTransition(
                      turns: _rotationAnimation,
                      child: Icon(Icons.expand_more, color: Colors.white70),
                    ),
                  ],
                ),
              ),
            ),

            // Expandable content
            SizeTransition(
              sizeFactor: _expandAnimation,
              child: Column(
                children: [
                  const Divider(color: Colors.white24, height: 1),

                  // Challenge list
                  Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      children: challenges
                          .map((challenge) => _buildChallengeItem(challenge))
                          .toList(),
                    ),
                  ),

                  // Claim rewards button
                  if (completedCount > 0)
                    Padding(
                      padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                      child: _buildClaimRewardsButton(),
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Build individual challenge item
  Widget _buildChallengeItem(CosmicChallenge challenge) {
    final progress = CosmicChallengeService.getChallengeProgress(challenge.id);
    final isCompleted = CosmicChallengeService.isChallengeCompleted(challenge);
    final progressPercent = progress / challenge.targetValue;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isCompleted
            ? Colors.green.withOpacity(0.2)
            : Colors.white.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: isCompleted
              ? Colors.green.withOpacity(0.5)
              : Colors.white.withOpacity(0.3),
        ),
      ),
      child: Row(
        children: [
          // Challenge icon
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: isCompleted
                  ? Colors.green.withOpacity(0.3)
                  : Colors.purple.withOpacity(0.3),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Center(
              child: Text(challenge.icon, style: const TextStyle(fontSize: 20)),
            ),
          ),

          const SizedBox(width: 12),

          // Challenge details
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        challenge.title,
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                          color: isCompleted
                              ? Colors.green.shade300
                              : Colors.white,
                        ),
                      ),
                    ),
                    if (isCompleted)
                      const Icon(
                        Icons.check_circle,
                        color: Colors.green,
                        size: 18,
                      ),
                  ],
                ),

                const SizedBox(height: 4),

                Text(
                  challenge.description,
                  style: TextStyle(
                    fontSize: 12,
                    color: isCompleted ? Colors.green.shade200 : Colors.white70,
                  ),
                ),

                const SizedBox(height: 8),

                // Progress bar
                Row(
                  children: [
                    Expanded(
                      child: LinearProgressIndicator(
                        value: progressPercent.clamp(0.0, 1.0),
                        backgroundColor: Colors.white24,
                        valueColor: AlwaysStoppedAnimation<Color>(
                          isCompleted ? Colors.green : Colors.cyan,
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      '$progress/${challenge.targetValue}',
                      style: const TextStyle(
                        fontSize: 11,
                        color: Colors.white60,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 4),

                // Rewards
                Text(
                  'Rewards: ${challenge.rewardStellarShards} SS, ${challenge.rewardExperience} XP',
                  style: const TextStyle(
                    fontSize: 10,
                    color: Colors.amber,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Build claim rewards button
  Widget _buildClaimRewardsButton() {
    final totalRewards = CosmicChallengeService.claimCompletedRewards();

    return SizedBox(
      width: double.infinity,
      child: ElevatedButton.icon(
        onPressed: () {
          _claimRewards();
        },
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.amber,
          foregroundColor: Colors.black,
          padding: const EdgeInsets.symmetric(vertical: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        ),
        icon: const Icon(Icons.card_giftcard),
        label: Text(
          'Claim Rewards: ${totalRewards.stellarShards} SS, ${totalRewards.experience} XP',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
      ),
    );
  }

  /// Claim challenge rewards
  void _claimRewards() {
    final rewards = CosmicChallengeService.claimCompletedRewards();

    // Trigger haptic feedback
    HapticFeedback.heavyImpact();

    // Show success message
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              const Icon(Icons.celebration, color: Colors.amber),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  '🎉 Challenge rewards claimed! +${rewards.stellarShards} SS, +${rewards.experience} XP',
                  style: const TextStyle(color: Colors.white),
                ),
              ),
            ],
          ),
          backgroundColor: Colors.green.shade700,
          duration: const Duration(seconds: 3),
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        ),
      );
    }

    // Notify parent widget
    widget.onRewardsClaimed?.call(rewards);
  }
}
