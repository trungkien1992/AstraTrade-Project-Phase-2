import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/simple_trade.dart';
import '../services/simple_trading_service.dart';
import '../providers/trading_provider.dart';
import '../services/rating_service.dart';
import '../services/analytics_service.dart';

class TradeResultScreen extends ConsumerStatefulWidget {
  final SimpleTrade trade;

  const TradeResultScreen({
    super.key,
    required this.trade,
  });

  @override
  ConsumerState<TradeResultScreen> createState() => _TradeResultScreenState();
}

class _TradeResultScreenState extends ConsumerState<TradeResultScreen>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;
  SimpleTrade? _completedTrade;
  bool _isProcessing = true;

  @override
  void initState() {
    super.initState();
    
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    
    _scaleAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.elasticOut,
    ));

    _processTrade();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  void _processTrade() async {
    // Simulate processing time
    await Future.delayed(const Duration(seconds: 2));
    
    final completedTrade = SimpleTradingService.completeTrade(widget.trade);
    
    // Track completed trade
    await AnalyticsService.trackTradeCompleted(
      symbol: completedTrade.symbol,
      direction: completedTrade.direction,
      amount: completedTrade.amount,
      profitLoss: completedTrade.profitLoss!,
      profitLossPercentage: completedTrade.profitLossPercentage,
      isProfit: completedTrade.profitLoss! > 0,
    );

    // Update in provider
    ref.read(tradingProvider.notifier).updateTrade(completedTrade);
    
    setState(() {
      _completedTrade = completedTrade;
      _isProcessing = false;
    });
    
    _animationController.forward();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Trade Result'),
        backgroundColor: Colors.blue[600],
        foregroundColor: Colors.white,
        automaticallyImplyLeading: false,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            const SizedBox(height: 40),
            
            if (_isProcessing) ...[
              const CircularProgressIndicator(),
              const SizedBox(height: 20),
              const Text(
                'Processing your trade...',
                style: TextStyle(fontSize: 18),
              ),
              const SizedBox(height: 10),
              Text(
                '${widget.trade.direction} \$${widget.trade.amount.toInt()} ${widget.trade.symbol}',
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ] else if (_completedTrade != null) ...[
              ScaleTransition(
                scale: _scaleAnimation,
                child: Card(
                  elevation: 8,
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Column(
                      children: [
                        Icon(
                          _completedTrade!.profitLossPercentage > 0
                              ? Icons.trending_up
                              : Icons.trending_down,
                          size: 64,
                          color: _completedTrade!.profitLossPercentage > 0
                              ? Colors.green
                              : Colors.red,
                        ),
                        const SizedBox(height: 16),
                        
                        Text(
                          SimpleTradingService.getTradeMessage(_completedTrade!),
                          style: const TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                          textAlign: TextAlign.center,
                        ),
                        
                        const SizedBox(height: 20),
                        
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceAround,
                          children: [
                            Column(
                              children: [
                                const Text(
                                  'Trade Amount',
                                  style: TextStyle(
                                    fontSize: 14,
                                    color: Colors.grey,
                                  ),
                                ),
                                Text(
                                  '\$${_completedTrade!.amount.toInt()}',
                                  style: const TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ],
                            ),
                            Column(
                              children: [
                                const Text(
                                  'Profit/Loss',
                                  style: TextStyle(
                                    fontSize: 14,
                                    color: Colors.grey,
                                  ),
                                ),
                                Text(
                                  '\$${_completedTrade!.profitLoss!.toStringAsFixed(2)}',
                                  style: TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                    color: _completedTrade!.profitLoss! > 0
                                        ? Colors.green
                                        : Colors.red,
                                  ),
                                ),
                              ],
                            ),
                            Column(
                              children: [
                                const Text(
                                  'Return',
                                  style: TextStyle(
                                    fontSize: 14,
                                    color: Colors.grey,
                                  ),
                                ),
                                Text(
                                  '${_completedTrade!.profitLossPercentage > 0 ? '+' : ''}${_completedTrade!.profitLossPercentage.toStringAsFixed(1)}%',
                                  style: TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                    color: _completedTrade!.profitLossPercentage > 0
                                        ? Colors.green
                                        : Colors.red,
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
            
            const Spacer(),
            
            if (!_isProcessing) ...[
              SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton(
                  onPressed: _handleViewProgress,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blue[600],
                    foregroundColor: Colors.white,
                  ),
                  child: const Text(
                    'View Progress',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
              
              const SizedBox(height: 12),
              
              SizedBox(
                width: double.infinity,
                height: 56,
                child: OutlinedButton(
                  onPressed: _handleTradeAgain,
                  style: OutlinedButton.styleFrom(
                    side: BorderSide(color: Colors.blue[600]!),
                  ),
                  child: Text(
                    'Trade Again',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.blue[600],
                    ),
                  ),
                ),
              ),
            ],
            
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  void _handleViewProgress() {
    _checkForRatingPrompt(() {
      Navigator.pushNamed(context, '/streak-tracker');
    });
  }

  void _handleTradeAgain() {
    _checkForRatingPrompt(() {
      Navigator.pushNamed(context, '/trade-entry');
    });
  }

  void _checkForRatingPrompt(VoidCallback onContinue) async {
    final tradingState = ref.read(tradingProvider);
    final progress = tradingState.progress;
    
    final shouldShow = await RatingService.shouldShowRatingPrompt(
      totalTrades: progress.totalTrades,
      currentStreak: progress.currentStreak,
      hasSubscription: progress.hasSubscription,
    );
    
    if (shouldShow && mounted) {
      await RatingService.markRatingPromptShown();
      
      final ratingResult = await RatingService.showRatingDialog(context);
      
      if (ratingResult == true && mounted) {
        // User interacted with rating prompt
        onContinue();
      } else if (mounted) {
        // User dismissed or skipped rating
        onContinue();
      }
    } else {
      onContinue();
    }
  }
}