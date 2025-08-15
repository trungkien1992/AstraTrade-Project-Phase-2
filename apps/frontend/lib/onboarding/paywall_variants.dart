import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/subscription_service.dart';
import '../providers/trading_provider.dart';
import '../services/analytics_service.dart';
import '../services/ab_testing_service.dart';

// Advanced paywall variants for conversion optimization
enum PaywallVariantType {
  urgency_focused, // Variant D: Scarcity and urgency
  value_proposition, // Variant E: Feature comparison
  money_back_guarantee, // Variant F: Risk reversal
  free_trial_extended, // Variant G: Extended trial
}

class AdvancedPaywallScreen extends ConsumerStatefulWidget {
  final PaywallVariantType variantType;
  final String trigger;
  final bool showDiscount;

  const AdvancedPaywallScreen({
    super.key,
    required this.variantType,
    this.trigger = 'unknown',
    this.showDiscount = false,
  });

  @override
  ConsumerState<AdvancedPaywallScreen> createState() =>
      _AdvancedPaywallScreenState();
}

class _AdvancedPaywallScreenState extends ConsumerState<AdvancedPaywallScreen>
    with TickerProviderStateMixin {
  bool _isLoading = false;
  late AnimationController _urgencyAnimationController;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
    _trackPaywallShown();
  }

  void _initializeAnimations() {
    _urgencyAnimationController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    );

    _pulseAnimation = Tween<double>(begin: 1.0, end: 1.1).animate(
      CurvedAnimation(
        parent: _urgencyAnimationController,
        curve: Curves.easeInOut,
      ),
    );

    if (widget.variantType == PaywallVariantType.urgency_focused) {
      _urgencyAnimationController.repeat(reverse: true);
    }
  }

  @override
  void dispose() {
    _urgencyAnimationController.dispose();
    super.dispose();
  }

  Future<void> _trackPaywallShown() async {
    await AnalyticsService.trackPaywallShown(
      trigger: widget.trigger,
      variant: 'advanced_${widget.variantType.name}',
    );

    await AnalyticsService.trackScreenView(
      'advanced_paywall_screen',
      properties: {
        'variant_type': widget.variantType.name,
        'trigger': widget.trigger,
        'show_discount': widget.showDiscount,
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _getBackgroundColor(),
      appBar: AppBar(
        title: Text(_getAppBarTitle()),
        backgroundColor: _getPrimaryColor(),
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          if (widget.variantType == PaywallVariantType.urgency_focused)
            Padding(
              padding: const EdgeInsets.only(right: 16),
              child: AnimatedBuilder(
                animation: _pulseAnimation,
                builder: (context, child) {
                  return Transform.scale(
                    scale: _pulseAnimation.value,
                    child: const Icon(Icons.access_time, color: Colors.orange),
                  );
                },
              ),
            ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            _buildHeroSection(),
            const SizedBox(height: 32),
            _buildContentSection(),
            const SizedBox(height: 32),
            _buildPricingSection(),
            const SizedBox(height: 32),
            _buildCallToAction(),
            const SizedBox(height: 16),
            _buildSecondaryActions(),
            const SizedBox(height: 16),
            _buildTrustSignals(),
          ],
        ),
      ),
    );
  }

  Widget _buildHeroSection() {
    switch (widget.variantType) {
      case PaywallVariantType.urgency_focused:
        return _buildUrgencyHero();
      case PaywallVariantType.value_proposition:
        return _buildValuePropositionHero();
      case PaywallVariantType.money_back_guarantee:
        return _buildGuaranteeHero();
      case PaywallVariantType.free_trial_extended:
        return _buildExtendedTrialHero();
    }
  }

  Widget _buildUrgencyHero() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.red[600]!, Colors.orange[500]!],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.red.withOpacity(0.3),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        children: [
          AnimatedBuilder(
            animation: _pulseAnimation,
            builder: (context, child) {
              return Transform.scale(
                scale: _pulseAnimation.value,
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 8,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    '⚡ FLASH SALE ENDING SOON',
                    style: TextStyle(
                      color: Colors.red[700],
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                ),
              );
            },
          ),
          const SizedBox(height: 16),
          const Icon(
            Icons.local_fire_department,
            size: 64,
            color: Colors.white,
          ),
          const SizedBox(height: 16),
          const Text(
            'Last Chance: 80% OFF!',
            style: TextStyle(
              fontSize: 32,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          const Text(
            'Only 47 spots left at this price',
            style: TextStyle(fontSize: 16, color: Colors.white70),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          _buildCountdownTimer(),
        ],
      ),
    );
  }

  Widget _buildValuePropositionHero() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.blue[600]!, Colors.purple[500]!],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        children: [
          const Icon(Icons.trending_up, size: 64, color: Colors.white),
          const SizedBox(height: 16),
          const Text(
            'Join Elite Traders',
            style: TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          const Text(
            'Everything you need to trade like a professional',
            style: TextStyle(fontSize: 16, color: Colors.white70),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          _buildValueMetrics(),
        ],
      ),
    );
  }

  Widget _buildGuaranteeHero() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.green[600]!, Colors.teal[500]!],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              shape: BoxShape.circle,
            ),
            child: Icon(
              Icons.shield_outlined,
              size: 48,
              color: Colors.green[600],
            ),
          ),
          const SizedBox(height: 16),
          const Text(
            '100% Risk-Free Trading',
            style: TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          const Text(
            '30-day money-back guarantee. No questions asked.',
            style: TextStyle(fontSize: 16, color: Colors.white70),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildExtendedTrialHero() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.indigo[600]!, Colors.blue[500]!],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        children: [
          const Icon(Icons.access_time, size: 64, color: Colors.white),
          const SizedBox(height: 16),
          const Text(
            'Extended 14-Day Trial',
            style: TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          const Text(
            'Double the time to explore all Pro features',
            style: TextStyle(fontSize: 16, color: Colors.white70),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Text(
              'Usually 7 days • Today only: 14 days',
              style: TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildContentSection() {
    switch (widget.variantType) {
      case PaywallVariantType.urgency_focused:
        return _buildUrgencyContent();
      case PaywallVariantType.value_proposition:
        return _buildValueComparisonTable();
      case PaywallVariantType.money_back_guarantee:
        return _buildGuaranteeContent();
      case PaywallVariantType.free_trial_extended:
        return _buildTrialContent();
    }
  }

  Widget _buildUrgencyContent() {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.red[50],
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.red[200]!),
          ),
          child: Row(
            children: [
              Icon(Icons.people, color: Colors.red[600]),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '1,247 people viewing this offer',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Colors.red[700],
                      ),
                    ),
                    Text(
                      '53 spots left at this price',
                      style: TextStyle(color: Colors.red[600]),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 24),
        _buildQuickFeatures(),
      ],
    );
  }

  Widget _buildValueComparisonTable() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Free vs Pro Comparison',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _buildComparisonRow(
              'Virtual Trading Funds',
              'Limited',
              'Unlimited',
            ),
            _buildComparisonRow('Real Market Data', '❌', '✅'),
            _buildComparisonRow('Advanced Analytics', '❌', '✅'),
            _buildComparisonRow('Pro Trading Lessons', '❌', '✅'),
            _buildComparisonRow('Priority Support', '❌', '✅'),
            _buildComparisonRow('Exclusive Strategies', '❌', '✅'),
          ],
        ),
      ),
    );
  }

  Widget _buildGuaranteeContent() {
    return Column(
      children: [
        _buildGuaranteeItem(
          Icons.thumb_up,
          'Try Risk-Free',
          'Full access for 30 days with money-back guarantee',
        ),
        _buildGuaranteeItem(
          Icons.support_agent,
          '24/7 Support',
          'Get help anytime from our expert trading team',
        ),
        _buildGuaranteeItem(
          Icons.security,
          'Secure & Safe',
          'Bank-level security protecting your data',
        ),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.green[50],
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(
            children: [
              Text(
                '💰 Money-Back Promise',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.green[700],
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'If you\'re not completely satisfied within 30 days, we\'ll refund every penny. No questions, no hassle.',
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.green[600]),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildTrialContent() {
    return Column(
      children: [
        _buildTrialFeature(
          Icons.access_time,
          '14 Full Days',
          'Double the standard trial period',
        ),
        _buildTrialFeature(
          Icons.all_inclusive,
          'Everything Included',
          'Access to all Pro features and content',
        ),
        _buildTrialFeature(
          Icons.cancel,
          'Cancel Anytime',
          'No commitment, cancel before trial ends',
        ),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.blue[50],
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            '⏰ This extended trial is only available today. Starting tomorrow, new users get the standard 7-day trial.',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: Colors.blue[700],
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildPricingSection() {
    final regularPrice = 9.99;
    final discountPrice =
        widget.variantType == PaywallVariantType.urgency_focused ? 1.99 : 2.99;

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          if (widget.variantType == PaywallVariantType.urgency_focused) ...[
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  '\$${regularPrice.toStringAsFixed(2)}',
                  style: const TextStyle(
                    fontSize: 24,
                    decoration: TextDecoration.lineThrough,
                    color: Colors.grey,
                  ),
                ),
                const SizedBox(width: 12),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.red,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: const Text(
                    '80% OFF',
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
          ],
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                '\$${_getPrice().toStringAsFixed(2)}',
                style: TextStyle(
                  fontSize: 48,
                  fontWeight: FontWeight.bold,
                  color: _getPrimaryColor(),
                ),
              ),
              const Text(
                '/month',
                style: TextStyle(fontSize: 16, color: Colors.grey),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            _getPricingSubtext(),
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 14, color: Colors.grey[600]),
          ),
        ],
      ),
    );
  }

  Widget _buildCallToAction() {
    return SizedBox(
      width: double.infinity,
      height: 56,
      child: ElevatedButton(
        onPressed: _isLoading ? null : _handleUpgrade,
        style: ElevatedButton.styleFrom(
          backgroundColor: _getPrimaryColor(),
          foregroundColor: Colors.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(28),
          ),
          elevation: 4,
        ),
        child: _isLoading
            ? const CircularProgressIndicator(color: Colors.white)
            : Text(
                _getCallToActionText(),
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
      ),
    );
  }

  Widget _buildSecondaryActions() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        TextButton(
          onPressed: () async {
            await SubscriptionService.restorePurchases();
          },
          child: const Text('Restore Purchases'),
        ),
        TextButton(
          onPressed: () async {
            await AnalyticsService.trackPaywallDismissed(
              variant: 'advanced_${widget.variantType.name}',
              reason: 'maybe_later',
            );
            Navigator.pop(context);
          },
          child: const Text('Maybe Later'),
        ),
      ],
    );
  }

  Widget _buildTrustSignals() {
    return Column(
      children: [
        const Text(
          '⭐⭐⭐⭐⭐ 4.8/5 from 12,000+ reviews',
          style: TextStyle(fontSize: 14, color: Colors.grey),
        ),
        const SizedBox(height: 8),
        const Text(
          'Secure payment • Powered by App Store',
          style: TextStyle(fontSize: 12, color: Colors.grey),
        ),
        if (widget.variantType == PaywallVariantType.money_back_guarantee) ...[
          const SizedBox(height: 8),
          Text(
            '🛡️ 30-Day Money-Back Guarantee',
            style: TextStyle(
              fontSize: 12,
              color: Colors.green[600],
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ],
    );
  }

  // Helper widgets
  Widget _buildCountdownTimer() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.3),
        borderRadius: BorderRadius.circular(8),
      ),
      child: const Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.timer, color: Colors.white, size: 16),
          SizedBox(width: 8),
          Text(
            'Ends in: 23:47:12',
            style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }

  Widget _buildValueMetrics() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceAround,
      children: [
        _buildMetric('50K+', 'Active Traders'),
        _buildMetric('98%', 'Success Rate'),
        _buildMetric('4.8★', 'Rating'),
      ],
    );
  }

  Widget _buildMetric(String value, String label) {
    return Column(
      children: [
        Text(
          value,
          style: const TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        Text(
          label,
          style: const TextStyle(fontSize: 12, color: Colors.white70),
        ),
      ],
    );
  }

  Widget _buildQuickFeatures() {
    final features = [
      'Unlimited virtual funds',
      'Real-time market data',
      'Advanced trading tools',
      'Expert strategies',
    ];

    return Column(
      children: features
          .map(
            (feature) => Padding(
              padding: const EdgeInsets.symmetric(vertical: 4),
              child: Row(
                children: [
                  Icon(Icons.check_circle, color: Colors.green[600], size: 20),
                  const SizedBox(width: 12),
                  Text(feature, style: const TextStyle(fontSize: 16)),
                ],
              ),
            ),
          )
          .toList(),
    );
  }

  Widget _buildComparisonRow(String feature, String free, String pro) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Expanded(
            flex: 2,
            child: Text(
              feature,
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
          Expanded(child: Text(free, textAlign: TextAlign.center)),
          Expanded(
            child: Text(
              pro,
              textAlign: TextAlign.center,
              style: TextStyle(
                color: Colors.green[600],
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildGuaranteeItem(IconData icon, String title, String description) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.green[50],
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: Colors.green[600]),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                Text(description, style: const TextStyle(color: Colors.grey)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTrialFeature(IconData icon, String title, String description) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.blue[50],
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: Colors.blue[600]),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                Text(description, style: const TextStyle(color: Colors.grey)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // Helper methods
  Color _getBackgroundColor() {
    switch (widget.variantType) {
      case PaywallVariantType.urgency_focused:
        return Colors.red[50]!;
      case PaywallVariantType.value_proposition:
        return Colors.blue[50]!;
      case PaywallVariantType.money_back_guarantee:
        return Colors.green[50]!;
      case PaywallVariantType.free_trial_extended:
        return Colors.indigo[50]!;
    }
  }

  Color _getPrimaryColor() {
    switch (widget.variantType) {
      case PaywallVariantType.urgency_focused:
        return Colors.red[600]!;
      case PaywallVariantType.value_proposition:
        return Colors.blue[600]!;
      case PaywallVariantType.money_back_guarantee:
        return Colors.green[600]!;
      case PaywallVariantType.free_trial_extended:
        return Colors.indigo[600]!;
    }
  }

  String _getAppBarTitle() {
    switch (widget.variantType) {
      case PaywallVariantType.urgency_focused:
        return 'Flash Sale';
      case PaywallVariantType.value_proposition:
        return 'Upgrade to Pro';
      case PaywallVariantType.money_back_guarantee:
        return 'Risk-Free Trial';
      case PaywallVariantType.free_trial_extended:
        return 'Extended Trial';
    }
  }

  double _getPrice() {
    switch (widget.variantType) {
      case PaywallVariantType.urgency_focused:
        return 1.99;
      case PaywallVariantType.value_proposition:
        return 9.99;
      case PaywallVariantType.money_back_guarantee:
        return 9.99;
      case PaywallVariantType.free_trial_extended:
        return 9.99;
    }
  }

  String _getPricingSubtext() {
    switch (widget.variantType) {
      case PaywallVariantType.urgency_focused:
        return 'Flash sale price • Limited time only';
      case PaywallVariantType.value_proposition:
        return 'Cancel anytime • Full feature access';
      case PaywallVariantType.money_back_guarantee:
        return '30-day money-back guarantee';
      case PaywallVariantType.free_trial_extended:
        return 'Free for 14 days, then \$9.99/month';
    }
  }

  String _getCallToActionText() {
    switch (widget.variantType) {
      case PaywallVariantType.urgency_focused:
        return 'Claim Flash Sale Now';
      case PaywallVariantType.value_proposition:
        return 'Upgrade to Pro';
      case PaywallVariantType.money_back_guarantee:
        return 'Start Risk-Free Trial';
      case PaywallVariantType.free_trial_extended:
        return 'Start 14-Day Free Trial';
    }
  }

  Future<void> _handleUpgrade() async {
    setState(() => _isLoading = true);

    try {
      // Track conversion attempt
      await AnalyticsService.trackPaywallConversion(
        variant: 'advanced_${widget.variantType.name}',
        plan: 'pro_monthly',
        price: _getPrice(),
      );

      await ABTestingService.trackConversion(
        'paywall_presentation',
        'purchase',
        {
          'variant_type': widget.variantType.name,
          'plan': 'pro_monthly',
          'price': _getPrice(),
        },
      );

      // Simulate successful upgrade for demo
      ref.read(tradingProvider.notifier).updateSubscription(true);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('Welcome to Trading Practice Pro! 🎉'),
            backgroundColor: Colors.green[600],
            duration: const Duration(seconds: 3),
          ),
        );

        Navigator.pop(context, true);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Upgrade failed: $e'),
            backgroundColor: Colors.red[600],
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }
}
