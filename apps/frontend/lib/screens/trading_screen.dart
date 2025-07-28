import 'package:flutter/material.dart';
import '../widgets/trading_chart_widget.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class TradingScreen extends StatefulWidget {
  const TradingScreen({Key? key}) : super(key: key);

  @override
  State<TradingScreen> createState() => _TradingScreenState();
}

class _TradingScreenState extends State<TradingScreen> {
  String selectedSymbol = 'BTCUSD';
  List<Map<String, dynamic>> tradingPairs = [];
  bool isLoadingPairs = true;

  @override
  void initState() {
    super.initState();
    _loadTradingPairs();
  }

  Future<void> _loadTradingPairs() async {
    try {
      final response = await http.get(
        Uri.parse('http://localhost:8002/trading/pairs'),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          tradingPairs = List<Map<String, dynamic>>.from(data['pairs']);
          isLoadingPairs = false;
        });
      }
    } catch (e) {
      setState(() {
        isLoadingPairs = false;
      });
      print('Error loading trading pairs: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: const Text(
          'AstraTrade',
          style: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
        flexibleSpace: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                Colors.purple.shade900.withOpacity(0.8),
                Colors.blue.shade900.withOpacity(0.8),
              ],
            ),
          ),
        ),
      ),
      body: Column(
        children: [
          // Trading pair selector
          Container(
            height: 100,
            padding: const EdgeInsets.symmetric(vertical: 8),
            child: isLoadingPairs
                ? const Center(
                    child: CircularProgressIndicator(color: Colors.cyan),
                  )
                : ListView.builder(
                    scrollDirection: Axis.horizontal,
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    itemCount: tradingPairs.length,
                    itemBuilder: (context, index) {
                      final pair = tradingPairs[index];
                      final isSelected = pair['symbol'] == selectedSymbol;
                      final isPositive = pair['change_percent_24h'] >= 0;

                      return GestureDetector(
                        onTap: () {
                          setState(() {
                            selectedSymbol = pair['symbol'];
                          });
                        },
                        child: Container(
                          width: 140,
                          margin: const EdgeInsets.only(right: 12),
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            gradient: LinearGradient(
                              colors: isSelected
                                  ? [
                                      Colors.cyan.withOpacity(0.8),
                                      Colors.blue.withOpacity(0.8),
                                    ]
                                  : [
                                      Colors.grey.shade900.withOpacity(0.8),
                                      Colors.grey.shade800.withOpacity(0.8),
                                    ],
                            ),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(
                              color: isSelected
                                  ? Colors.cyan
                                  : Colors.white.withOpacity(0.1),
                              width: isSelected ? 2 : 1,
                            ),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                pair['symbol'],
                                style: TextStyle(
                                  color: isSelected ? Colors.white : Colors.white70,
                                  fontSize: 14,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              Text(
                                '\$${pair['price'].toStringAsFixed(2)}',
                                style: TextStyle(
                                  color: isSelected ? Colors.white : Colors.white,
                                  fontSize: 12,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                              Text(
                                '${isPositive ? '+' : ''}${pair['change_percent_24h'].toStringAsFixed(2)}%',
                                style: TextStyle(
                                  color: isPositive ? Colors.green : Colors.red,
                                  fontSize: 11,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
          ),

          // Main trading chart
          Expanded(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: TradingChartWidget(
                key: ValueKey(selectedSymbol), // Force rebuild when symbol changes
                symbol: selectedSymbol,
                interval: '1m',
              ),
            ),
          ),

          // Market overview section
          Container(
            height: 120,
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Market Overview',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 12),
                Expanded(
                  child: Row(
                    children: [
                      Expanded(
                        child: _buildMarketCard(
                          'Total Volume',
                          '\$2.4B',
                          Colors.blue,
                          Icons.bar_chart,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _buildMarketCard(
                          'Active Pairs',
                          '${tradingPairs.length}',
                          Colors.purple,
                          Icons.currency_exchange,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _buildMarketCard(
                          'Market Cap',
                          '\$1.8T',
                          Colors.green,
                          Icons.trending_up,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMarketCard(String title, String value, Color color, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            color.withOpacity(0.2),
            color.withOpacity(0.1),
          ],
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: color.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                icon,
                color: color,
                size: 16,
              ),
              const SizedBox(width: 6),
              Expanded(
                child: Text(
                  title,
                  style: TextStyle(
                    color: Colors.white70,
                    fontSize: 11,
                    fontWeight: FontWeight.w500,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              color: color,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
}