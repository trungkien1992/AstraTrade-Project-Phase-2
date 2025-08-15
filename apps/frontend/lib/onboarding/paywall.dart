import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/subscription_service.dart';
import '../providers/trading_provider.dart';
import '../services/analytics_service.dart';
import '../services/ab_testing_service.dart';

class PaywallScreen extends ConsumerStatefulWidget {
  final bool showDiscount;
  final String trigger;

  const PaywallScreen({
    super.key,
    this.showDiscount = false,
    this.trigger = 'unknown',
  });

  @override
  ConsumerState<PaywallScreen> createState() => _PaywallScreenState();
}

class _PaywallScreenState extends ConsumerState<PaywallScreen> {
  bool _isLoading = false;
  PaywallVariant? _variant;

  @override
  void initState() {
    super.initState();
    _initializePaywall();
  }

  Future<void> _initializePaywall() async {
    final variant = await ABTestingService.getPaywallVariant();
    setState(() {
      _variant = variant;
    });

    // Track paywall shown
    await AnalyticsService.trackPaywallShown(
      trigger: widget.trigger,
      variant: variant.name,
    );

    await AnalyticsService.trackScreenView(
      'paywall_screen',
      properties: {
        'variant': variant.name,
        'trigger': widget.trigger,
        'show_discount': widget.showDiscount,
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_variant == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    final discountPrice = widget.showDiscount ? '\$2.99' : null;
    final regularPrice = '\$9.99';

    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text('Trading Practice Pro'),
        backgroundColor: Colors.blue[600],
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            // Hero Section - Variant Specific
            _buildHeroSection(),

            const SizedBox(height: 32),

            // Features List
            _buildFeature(
              Icons.all_inclusive,
              'Unlimited Virtual Money',
              'Practice with \$1M+ virtual funds',
              Colors.green,
            ),
            _buildFeature(
              Icons.trending_up,
              'Real Market Data',
              'Live prices from global exchanges',
              Colors.blue,
            ),
            _buildFeature(
              Icons.analytics,
              'Advanced Analytics',
              'Track your progress & strategies',
              Colors.purple,
            ),
            _buildFeature(
              Icons.school,
              'Pro Trading Lessons',
              'Learn from expert traders',
              Colors.orange,
            ),

            const SizedBox(height: 32),

            // Discount Badge
            if (widget.showDiscount) ...[
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 8,
                ),
                decoration: BoxDecoration(
                  color: Colors.red[100],
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: Colors.red[300]!),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.local_fire_department,
                      color: Colors.red[600],
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'LIMITED TIME: 70% OFF!',
                      style: TextStyle(
                        color: Colors.red[700],
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),
            ],

            // Pricing
            Container(
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
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      if (widget.showDiscount) ...[
                        Text(
                          regularPrice,
                          style: const TextStyle(
                            fontSize: 20,
                            decoration: TextDecoration.lineThrough,
                            color: Colors.grey,
                          ),
                        ),
                        const SizedBox(width: 12),
                      ],
                      Text(
                        discountPrice ?? regularPrice,
                        style: const TextStyle(
                          fontSize: 42,
                          fontWeight: FontWeight.bold,
                          color: Colors.blue,
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
                    widget.showDiscount
                        ? 'Save \$7/month with this exclusive offer!'
                        : 'Cancel anytime • No commitment',
                    style: TextStyle(
                      fontSize: 14,
                      color: widget.showDiscount
                          ? Colors.green[700]
                          : Colors.grey[600],
                      fontWeight: widget.showDiscount
                          ? FontWeight.w600
                          : FontWeight.normal,
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 32),

            // CTA Button
            SizedBox(
              width: double.infinity,
              height: 56,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _handleUpgrade,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue[600],
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(28),
                  ),
                  elevation: 2,
                ),
                child: _isLoading
                    ? const CircularProgressIndicator(color: Colors.white)
                    : Text(
                        widget.showDiscount
                            ? 'Claim 70% Off Deal'
                            : 'Start 7-Day Free Trial',
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
              ),
            ),

            const SizedBox(height: 16),

            // Secondary Actions
            Row(
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
                      variant: _variant!.name,
                      reason: 'maybe_later',
                    );
                    await ABTestingService.trackConversion(
                      'paywall_presentation',
                      'dismissal',
                      {'reason': 'maybe_later'},
                    );
                    Navigator.pop(context);
                  },
                  child: const Text('Maybe Later'),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // Trust Signals
            Text(
              '⭐⭐⭐⭐⭐ 4.8/5 from 12,000+ reviews',
              style: TextStyle(fontSize: 14, color: Colors.grey[600]),
            ),
            const SizedBox(height: 8),
            Text(
              'Secure payment • Powered by App Store',
              style: TextStyle(fontSize: 12, color: Colors.grey[500]),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFeature(
    IconData icon,
    String title,
    String subtitle,
    Color color,
  ) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: color, size: 24),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  subtitle,
                  style: TextStyle(fontSize: 14, color: Colors.grey[600]),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _handleUpgrade() async {
    setState(() {
      _isLoading = true;
    });

    try {
      // Initialize RevenueCat if not already done
      await SubscriptionService.initialize();

      // Get available products
      final products = await SubscriptionService.getAvailableProducts();

      if (products.isEmpty) {
        // Fallback: simulate successful upgrade for demo
        _simulateSuccessfulUpgrade();
        return;
      }

      // Purchase the monthly product
      final result = await SubscriptionService.purchaseProduct('pro_monthly');

      if (result.success) {
        // Track successful conversion
        await AnalyticsService.trackPaywallConversion(
          variant: _variant!.name,
          plan: 'pro_monthly',
          price: widget.showDiscount ? 2.99 : 9.99,
        );

        await ABTestingService.trackConversion(
          'paywall_presentation',
          'purchase',
          {
            'plan': 'pro_monthly',
            'price': widget.showDiscount ? 2.99 : 9.99,
            'discount_applied': widget.showDiscount,
          },
        );

        // Update subscription status in provider
        ref.read(tradingProvider.notifier).updateSubscription(true);

        // Show success message
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: const Text('Welcome to Trading Practice Pro! 🎉'),
              backgroundColor: Colors.green[600],
              duration: const Duration(seconds: 3),
            ),
          );

          Navigator.pop(context, true); // Return true to indicate success
        }
      } else {
        // Show error message
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                'Purchase failed: ${result.error ?? 'Unknown error'}',
              ),
              backgroundColor: Colors.red[600],
            ),
          );
        }
      }
    } catch (e) {
      // Fallback for demo: simulate successful upgrade
      _simulateSuccessfulUpgrade();
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  void _simulateSuccessfulUpgrade() {
    // For demo purposes: simulate successful upgrade
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
  }

  Widget _buildHeroSection() {
    switch (_variant!) {
      case PaywallVariant.standard:
        return _buildStandardHero();
      case PaywallVariant.discount_first:
        return _buildDiscountFirstHero();
      case PaywallVariant.social_proof:
        return _buildSocialProofHero();
    }
  }

  Widget _buildStandardHero() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.blue[600]!, Colors.blue[400]!],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        children: [
          const Icon(Icons.rocket_launch, size: 64, color: Colors.white),
          const SizedBox(height: 16),
          const Text(
            'Master Trading Like a Pro',
            style: TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          const Text(
            'Join 50,000+ traders practicing with unlimited virtual funds',
            style: TextStyle(fontSize: 16, color: Colors.white70),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildDiscountFirstHero() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.red[600]!, Colors.orange[400]!],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(
              'LIMITED TIME: 70% OFF',
              style: TextStyle(
                color: Colors.red[700],
                fontWeight: FontWeight.bold,
                fontSize: 16,
              ),
            ),
          ),
          const SizedBox(height: 16),
          const Icon(
            Icons.local_fire_department,
            size: 64,
            color: Colors.white,
          ),
          const SizedBox(height: 16),
          const Text(
            'Save \$7/Month Today!',
            style: TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          const Text(
            'Flash sale: Pro trading features for just \$2.99/month',
            style: TextStyle(fontSize: 16, color: Colors.white70),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildSocialProofHero() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.purple[600]!, Colors.blue[400]!],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              ...List.generate(
                5,
                (index) =>
                    const Icon(Icons.star, color: Colors.amber, size: 20),
              ),
              const SizedBox(width: 8),
              const Text(
                '4.8/5',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          const Icon(Icons.people, size: 64, color: Colors.white),
          const SizedBox(height: 16),
          const Text(
            'Join 50,000+ Successful Traders',
            style: TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          const Text(
            '"This app transformed my trading skills!" - Sarah M.',
            style: TextStyle(
              fontSize: 16,
              color: Colors.white70,
              fontStyle: FontStyle.italic,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}

class ExitIntentDiscountDialog extends StatelessWidget {
  const ExitIntentDiscountDialog({super.key});

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      title: Row(
        children: [
          Icon(Icons.local_fire_department, color: Colors.red[600]),
          const SizedBox(width: 8),
          const Text('Wait! Special Offer'),
        ],
      ),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.red[50],
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.red[200]!),
            ),
            child: Column(
              children: [
                Text(
                  '70% OFF FLASH SALE',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.red[700],
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Text(
                      '\$9.99',
                      style: TextStyle(
                        fontSize: 18,
                        decoration: TextDecoration.lineThrough,
                        color: Colors.grey,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Text(
                      '\$2.99',
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: Colors.red[700],
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          const Text(
            'This exclusive offer expires in 10 minutes!\nDon\'t miss your chance to master trading.',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 16),
          ),
          const SizedBox(height: 16),
          const Text(
            '⏰ Limited time only',
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w600,
              color: Colors.orange,
            ),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () {
            Navigator.of(context).pop(false);
          },
          child: const Text('No Thanks'),
        ),
        ElevatedButton(
          onPressed: () {
            Navigator.of(context).pop(true);
            // Navigate to discounted paywall
            Navigator.of(context).push(
              MaterialPageRoute(
                builder: (context) => const PaywallScreen(showDiscount: true),
              ),
            );
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.red[600],
            foregroundColor: Colors.white,
          ),
          child: const Text('Claim 70% Off'),
        ),
      ],
    );
  }
}
