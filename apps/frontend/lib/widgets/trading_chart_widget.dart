import 'package:flutter/material.dart';
import 'package:candlesticks/candlesticks.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:convert';
import 'dart:async';
import 'package:http/http.dart' as http;

class TradingChartWidget extends StatefulWidget {
  final String symbol;
  final String interval;
  
  const TradingChartWidget({
    Key? key,
    required this.symbol,
    this.interval = '1m',
  }) : super(key: key);

  @override
  State<TradingChartWidget> createState() => _TradingChartWidgetState();
}

class _TradingChartWidgetState extends State<TradingChartWidget> {
  List<Candle> candles = [];
  WebSocketChannel? _channel;
  StreamSubscription? _subscription;
  bool isLoading = true;
  String? error;
  double? currentPrice;
  double? priceChange;
  double? priceChangePercent;

  @override
  void initState() {
    super.initState();
    _loadInitialData();
    _connectWebSocket();
  }

  @override
  void dispose() {
    _subscription?.cancel();
    _channel?.sink.close();
    super.dispose();
  }

  Future<void> _loadInitialData() async {
    try {
      setState(() {
        isLoading = true;
        error = null;
      });

      // Load candlestick data
      final candleResponse = await http.get(
        Uri.parse('http://localhost:8002/trading/candles/${widget.symbol}?limit=100&interval=${widget.interval}'),
      );

      if (candleResponse.statusCode == 200) {
        final candleData = json.decode(candleResponse.body);
        final candleList = candleData['candles'] as List;
        
        setState(() {
          candles = candleList.map((item) => Candle(
            date: DateTime.fromMillisecondsSinceEpoch(item['timestamp']),
            high: item['high'].toDouble(),
            low: item['low'].toDouble(),
            open: item['open'].toDouble(),
            close: item['close'].toDouble(),
            volume: item['volume'].toDouble(),
          )).toList();
        });
      }

      // Load current ticker data
      final tickerResponse = await http.get(
        Uri.parse('http://localhost:8002/trading/ticker/${widget.symbol}'),
      );

      if (tickerResponse.statusCode == 200) {
        final tickerData = json.decode(tickerResponse.body);
        setState(() {
          currentPrice = tickerData['price'].toDouble();
          priceChange = tickerData['change_24h'].toDouble();
          priceChangePercent = tickerData['change_percent_24h'].toDouble();
          isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        error = 'Failed to load data: $e';
        isLoading = false;
      });
    }
  }

  void _connectWebSocket() {
    try {
      _channel = WebSocketChannel.connect(
        Uri.parse('ws://localhost:8002/ws/trading'),
      );

      _subscription = _channel!.stream.listen(
        (data) {
          try {
            final message = json.decode(data);
            if (message['type'] == 'ticker' && message['data']['symbol'] == widget.symbol) {
              final tickerData = message['data'];
              setState(() {
                currentPrice = tickerData['price'].toDouble();
                priceChange = tickerData['change_24h'].toDouble();
                priceChangePercent = tickerData['change_percent_24h'].toDouble();
              });
            }
          } catch (e) {
            print('Error parsing WebSocket message: $e');
          }
        },
        onError: (error) {
          print('WebSocket error: $error');
        },
        onDone: () {
          print('WebSocket connection closed');
          // Attempt to reconnect after a delay
          Timer(const Duration(seconds: 5), () {
            if (mounted) {
              _connectWebSocket();
            }
          });
        },
      );
    } catch (e) {
      print('Failed to connect to WebSocket: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Colors.grey.shade900.withOpacity(0.8),
            Colors.black.withOpacity(0.9),
          ],
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Colors.cyan.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Column(
        children: [
          // Header with symbol and price info
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(16),
                topRight: Radius.circular(16),
              ),
              gradient: LinearGradient(
                colors: [
                  Colors.purple.shade900.withOpacity(0.8),
                  Colors.blue.shade900.withOpacity(0.8),
                ],
              ),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      widget.symbol,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    if (currentPrice != null)
                      Text(
                        '\$${currentPrice!.toStringAsFixed(2)}',
                        style: const TextStyle(
                          color: Colors.cyan,
                          fontSize: 20,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                  ],
                ),
                if (priceChange != null && priceChangePercent != null)
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(
                        '${priceChange! >= 0 ? '+' : ''}${priceChange!.toStringAsFixed(2)}',
                        style: TextStyle(
                          color: priceChange! >= 0 ? Colors.green : Colors.red,
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      Text(
                        '${priceChangePercent! >= 0 ? '+' : ''}${priceChangePercent!.toStringAsFixed(2)}%',
                        style: TextStyle(
                          color: priceChangePercent! >= 0 ? Colors.green : Colors.red,
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
              ],
            ),
          ),
          
          // Chart area
          Expanded(
            child: Container(
              padding: const EdgeInsets.all(8),
              child: isLoading
                  ? const Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          CircularProgressIndicator(color: Colors.cyan),
                          SizedBox(height: 16),
                          Text(
                            'Loading chart data...',
                            style: TextStyle(color: Colors.white70),
                          ),
                        ],
                      ),
                    )
                  : error != null
                      ? Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              const Icon(
                                Icons.error_outline,
                                color: Colors.red,
                                size: 48,
                              ),
                              const SizedBox(height: 16),
                              Text(
                                error!,
                                style: const TextStyle(color: Colors.red),
                                textAlign: TextAlign.center,
                              ),
                              const SizedBox(height: 16),
                              ElevatedButton(
                                onPressed: _loadInitialData,
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: Colors.cyan,
                                  foregroundColor: Colors.white,
                                ),
                                child: const Text('Retry'),
                              ),
                            ],
                          ),
                        )
                      : candles.isEmpty
                          ? const Center(
                              child: Text(
                                'No chart data available',
                                style: TextStyle(color: Colors.white70),
                              ),
                            )
                          : Candlesticks(
                              candles: candles,
                              onLoadMoreCandles: () async {
                                // Could implement pagination here
                                return null;
                              },
                            ),
            ),
          ),
          
          // Trading controls
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              borderRadius: const BorderRadius.only(
                bottomLeft: Radius.circular(16),
                bottomRight: Radius.circular(16),
              ),
              color: Colors.grey.shade900.withOpacity(0.8),
            ),
            child: Row(
              children: [
                Expanded(
                  child: ElevatedButton(
                    onPressed: () {
                      // Implement buy functionality
                      _showTradeDialog('BUY');
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                    child: const Text(
                      'BUY',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton(
                    onPressed: () {
                      // Implement sell functionality
                      _showTradeDialog('SELL');
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                    child: const Text(
                      'SELL',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
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

  void _showTradeDialog(String action) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          backgroundColor: Colors.grey.shade900,
          title: Text(
            '$action ${widget.symbol}',
            style: const TextStyle(color: Colors.white),
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'Current Price: \$${currentPrice?.toStringAsFixed(2) ?? 'N/A'}',
                style: const TextStyle(color: Colors.cyan),
              ),
              const SizedBox(height: 16),
              const Text(
                'Trade execution coming soon!',
                style: TextStyle(color: Colors.white70),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.of(context).pop();
                // Show a more informative message about trading implementation
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('Trading functionality is being implemented. $action order for ${widget.symbol} would be placed in a future update.'),
                    backgroundColor: action == 'BUY' ? Colors.green : Colors.red,
                  ),
                );
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: action == 'BUY' ? Colors.green : Colors.red,
              ),
              child: Text(action),
            ),
          ],
        );
      },
    );
  }
}