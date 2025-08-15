import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class RatingService {
  static const String _ratingShownKey = 'rating_prompt_shown';
  static const String _ratingCountKey = 'rating_prompt_count';
  static const String _lastRatingPromptKey = 'last_rating_prompt';
  static const String _userRatedKey = 'user_rated_app';
  static const String _userOptedOutKey = 'user_opted_out_rating';

  // Conditions for showing rating prompt
  static const int _minTradesForRating = 5;
  static const int _minStreakForRating = 3;
  static const int _daysBetweenPrompts = 7;

  static Future<bool> shouldShowRatingPrompt({
    required int totalTrades,
    required int currentStreak,
    required bool hasSubscription,
  }) async {
    final prefs = await SharedPreferences.getInstance();

    // Never show if user already rated or opted out
    if (prefs.getBool(_userRatedKey) == true ||
        prefs.getBool(_userOptedOutKey) == true) {
      return false;
    }

    // Check minimum requirements
    if (totalTrades < _minTradesForRating ||
        currentStreak < _minStreakForRating) {
      return false;
    }

    // Check cooldown period
    final lastPrompt = prefs.getInt(_lastRatingPromptKey) ?? 0;
    final now = DateTime.now().millisecondsSinceEpoch;
    final daysSinceLastPrompt = (now - lastPrompt) / (1000 * 60 * 60 * 24);

    if (daysSinceLastPrompt < _daysBetweenPrompts) {
      return false;
    }

    // Higher chance for subscribers and high-streak users
    if (hasSubscription || currentStreak >= 7) {
      return true;
    }

    // Limit prompt frequency for free users
    final promptCount = prefs.getInt(_ratingCountKey) ?? 0;
    return promptCount < 3; // Max 3 prompts for free users
  }

  static Future<void> markRatingPromptShown() async {
    final prefs = await SharedPreferences.getInstance();
    final promptCount = prefs.getInt(_ratingCountKey) ?? 0;

    await prefs.setBool(_ratingShownKey, true);
    await prefs.setInt(_ratingCountKey, promptCount + 1);
    await prefs.setInt(
      _lastRatingPromptKey,
      DateTime.now().millisecondsSinceEpoch,
    );
  }

  static Future<void> markUserRated() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_userRatedKey, true);
  }

  static Future<void> markUserOptedOut() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_userOptedOutKey, true);
  }

  static Future<bool?> showRatingDialog(BuildContext context) async {
    return showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (context) => const RatingDialog(),
    );
  }
}

class RatingDialog extends StatefulWidget {
  const RatingDialog({super.key});

  @override
  State<RatingDialog> createState() => _RatingDialogState();
}

class _RatingDialogState extends State<RatingDialog> {
  int _selectedRating = 0;

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      title: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.blue[50],
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(Icons.star, size: 32, color: Colors.blue[600]),
          ),
          const SizedBox(height: 16),
          const Text(
            'Enjoying Trading Practice?',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
        ],
      ),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Text(
            'Your feedback helps us improve the app for everyone.',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 16),
          ),
          const SizedBox(height: 24),

          // Star Rating
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: List.generate(5, (index) {
              final starNumber = index + 1;
              return GestureDetector(
                onTap: () {
                  setState(() {
                    _selectedRating = starNumber;
                  });
                },
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4),
                  child: Icon(
                    _selectedRating >= starNumber
                        ? Icons.star
                        : Icons.star_border,
                    size: 36,
                    color: _selectedRating >= starNumber
                        ? Colors.amber[600]
                        : Colors.grey[400],
                  ),
                ),
              );
            }),
          ),

          const SizedBox(height: 8),

          if (_selectedRating > 0)
            Text(
              _getRatingText(_selectedRating),
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey[600],
                fontWeight: FontWeight.w500,
              ),
            ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () {
            RatingService.markUserOptedOut();
            Navigator.pop(context, false);
          },
          child: const Text('Not Now'),
        ),
        if (_selectedRating >= 4)
          ElevatedButton(
            onPressed: () {
              RatingService.markUserRated();
              Navigator.pop(context, true);
              _openAppStore();
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.blue[600],
              foregroundColor: Colors.white,
            ),
            child: const Text('Rate on App Store'),
          )
        else if (_selectedRating > 0)
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context, true);
              _showFeedbackDialog();
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.orange[600],
              foregroundColor: Colors.white,
            ),
            child: const Text('Send Feedback'),
          ),
      ],
    );
  }

  String _getRatingText(int rating) {
    switch (rating) {
      case 1:
        return 'We can do better 😔';
      case 2:
        return 'Needs improvement 🤔';
      case 3:
        return 'It\'s okay 😐';
      case 4:
        return 'Pretty good! 😊';
      case 5:
        return 'Amazing! 🤩';
      default:
        return '';
    }
  }

  void _openAppStore() {
    // In a real app, you'd use url_launcher to open the app store
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Thank you for your rating! 🙏'),
        backgroundColor: Colors.green,
      ),
    );
  }

  void _showFeedbackDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Send Feedback'),
        content: const Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('We\'d love to hear how we can improve!'),
            SizedBox(height: 16),
            TextField(
              maxLines: 3,
              decoration: InputDecoration(
                hintText: 'Tell us what we can do better...',
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Feedback sent! Thank you 🙏'),
                  backgroundColor: Colors.blue,
                ),
              );
            },
            child: const Text('Send'),
          ),
        ],
      ),
    );
  }
}
