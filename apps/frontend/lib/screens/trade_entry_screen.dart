import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/simple_trade.dart';
import '../services/simple_trading_service.dart';
import '../services/real_trading_service.dart';
import '../providers/trading_provider.dart';
import '../services/exit_intent_service.dart';
import '../services/analytics_service.dart';
import '../onboarding/paywall.dart';

class TradeEntryScreen extends ConsumerStatefulWidget {
  const TradeEntryScreen({super.key});

  @override
  ConsumerState<TradeEntryScreen> createState() => _TradeEntryScreenState();
}

class _TradeEntryScreenState extends ConsumerState<TradeEntryScreen> {
  double _selectedAmount = 100;
  String _selectedDirection = 'BUY';
  String _selectedSymbol = 'ETH-USD';
  bool _isLoading = false;

  @override
  Widget build(BuildContext context) {
    final tradingState = ref.watch(tradingProvider);
    
    // Track screen view
    AnalyticsService.trackScreenView('trade_entry_screen', properties: {
      'free_trades_remaining': tradingState.freeTrades,
      'has_subscription': tradingState.progress.hasSubscription,
      'total_trades': tradingState.progress.totalTrades,
    });
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('Place Trade'),
        backgroundColor: Colors.blue[600],
        foregroundColor: Colors.white,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            // If this is the main screen, exit or show confirmation
            Navigator.pushReplacementNamed(context, '/streak-tracker');
          },
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: 20),
            
            // Amount Selection
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Trade Amount',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Wrap(
                      spacing: 8,
                      children: RealTradingService.getAvailableAmounts()
                          .map((amount) => ChoiceChip(
                                label: Text('\$${amount.toInt()}'),
                                selected: _selectedAmount == amount,
                                onSelected: (selected) {
                                  if (selected) {
                                    setState(() {
                                      _selectedAmount = amount;
                                    });
                                  }
                                },
                              ))
                          .toList(),
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Direction Selection
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Direction',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: ChoiceChip(
                            label: const Text('BUY'),
                            selected: _selectedDirection == 'BUY',
                            selectedColor: Colors.green[200],
                            onSelected: (selected) {
                              if (selected) {
                                setState(() {
                                  _selectedDirection = 'BUY';
                                });
                              }
                            },
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: ChoiceChip(
                            label: const Text('SELL'),
                            selected: _selectedDirection == 'SELL',
                            selectedColor: Colors.red[200],
                            onSelected: (selected) {
                              if (selected) {
                                setState(() {
                                  _selectedDirection = 'SELL';
                                });
                              }
                            },
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Symbol Selection
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Token Pair',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 12),
                    DropdownButtonFormField<String>(
                      value: _selectedSymbol,
                      decoration: const InputDecoration(
                        border: OutlineInputBorder(),
                      ),
                      items: RealTradingService.getAvailableSymbols()
                          .map((symbol) => DropdownMenuItem(
                                value: symbol,
                                child: Text(symbol),
                              ))
                          .toList(),
                      onChanged: (value) {
                        if (value != null) {
                          setState(() {
                            _selectedSymbol = value;
                          });
                        }
                      },
                    ),
                  ],
                ),
              ),
            ),
            
            const Spacer(),
            
            // Trade Button
            SizedBox(
              height: 56,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _placeTrade,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue[600],
                  foregroundColor: Colors.white,
                  textStyle: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                child: _isLoading
                    ? const CircularProgressIndicator(color: Colors.white)
                    : Text('${_selectedDirection} \$${_selectedAmount.toInt()} ${_selectedSymbol}'),
              ),
            ),
            
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  void _placeTrade() async {
    final tradingState = ref.read(tradingProvider);
    
    // Track trade attempt
    await AnalyticsService.trackUserAction('trade_attempted', properties: {
      'symbol': _selectedSymbol,
      'direction': _selectedDirection,
      'amount': _selectedAmount,
      'free_trades_remaining': tradingState.freeTrades,
      'has_subscription': tradingState.progress.hasSubscription,
    });
    
    // Check if user can trade
    if (!ref.read(tradingProvider.notifier).canTrade()) {
      // Show exit intent dialog first
      final exitIntentResult = await ExitIntentService.showExitIntentDialog(context);
      
      if (exitIntentResult != true) {
        // If user didn't accept exit intent offer, show regular paywall
        final paywallResult = await Navigator.push<bool>(
          context,
          MaterialPageRoute(
            builder: (context) => const PaywallScreen(trigger: 'trade_limit_reached'),
          ),
        );
        
        if (paywallResult != true) {
          return; // User didn't subscribe
        }
      }
      
      // User has now subscribed, continue with trade
    }
    
    setState(() {
      _isLoading = true;
    });

    try {
      // 🚀 EXECUTE REAL END-TO-END TRADE
      debugPrint('🎯 Starting REAL END-TO-END TRADE execution');
      debugPrint('   Amount: \$${_selectedAmount}');
      debugPrint('   Direction: $_selectedDirection');  
      debugPrint('   Symbol: $_selectedSymbol');
      
      final trade = await RealTradingService.executeRealTrade(
        amount: _selectedAmount,
        direction: _selectedDirection,
        symbol: _selectedSymbol,
      );

      debugPrint('✅ REAL TRADE COMPLETED: ${trade.isRealTrade ? 'SUCCESS' : 'FALLBACK'}');
      
      // Track successful trade start
      await AnalyticsService.trackTradeStarted(
        symbol: _selectedSymbol,
        direction: _selectedDirection,
        amount: _selectedAmount,
      );

      // Add trade to provider
      ref.read(tradingProvider.notifier).addTrade(trade);

      // Navigate to result screen with real trade data
      if (mounted) {
        Navigator.pushReplacementNamed(
          context,
          '/trade-result',
          arguments: trade,
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error placing trade: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }
}