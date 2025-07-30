import 'package:flutter/foundation.dart';
import '../api/production_extended_exchange_client.dart';
import '../models/trade_request.dart';
import '../models/trade_result.dart';

/// Production Live Trading Service
/// Handles REAL trading operations with Extended Exchange API
class LiveTradingService {
  static const String _apiKey = String.fromEnvironment('EXTENDED_EXCHANGE_API_KEY');
  static const String _apiSecret = String.fromEnvironment('EXTENDED_EXCHANGE_API_SECRET');
  
  late final ProductionExtendedExchangeClient _client;
  
  LiveTradingService() {
    _client = ProductionExtendedExchangeClient(
      apiKey: _apiKey.isNotEmpty ? _apiKey : 'demo_key_for_testing',
      apiSecret: _apiSecret.isNotEmpty ? _apiSecret : 'demo_secret_for_testing',
    );
  }
  
  /// Execute a real trading order on Extended Exchange
  Future<TradeResult> executeRealTrade(TradeRequest request) async {
    try {
      if (kDebugMode) {
        print('🚀 Executing LIVE trade: ${request.symbol} ${request.side} ${request.amount}');
      }
      
      // Execute the live trade
      final liveResult = await _client.executeLiveTrade(
        symbol: request.symbol,
        side: request.side,
        amount: request.amount,
        orderType: request.orderType ?? 'MARKET',
        limitPrice: request.limitPrice,
      );
      
      // Convert to our internal format
      return TradeResult(
        success: liveResult.success,
        tradeId: liveResult.orderId ?? 'unknown',
        symbol: request.symbol,
        side: request.side,
        requestedAmount: request.amount,
        executedAmount: liveResult.executedAmount,
        executedPrice: liveResult.executedPrice,
        status: liveResult.status ?? 'UNKNOWN',
        timestamp: liveResult.timestamp,
        isLive: true, // Mark as live trade
        exchangeResponse: liveResult.rawResponse,
        error: liveResult.error,
      );
      
    } catch (e) {
      if (kDebugMode) {
        print('❌ Live trade execution failed: $e');
      }
      
      return TradeResult(
        success: false,
        tradeId: 'failed_${DateTime.now().millisecondsSinceEpoch}',
        symbol: request.symbol,
        side: request.side,
        requestedAmount: request.amount,
        executedAmount: 0,
        executedPrice: 0,
        status: 'FAILED',
        timestamp: DateTime.now(),
        isLive: true,
        error: 'Live trading failed: ${e.toString()}',
      );
    }
  }
  
  /// Get live market data for a symbol
  Future<MarketData> getLiveMarketData(String symbol) async {
    return await _client.getLiveMarketData(symbol);
  }
  
  /// Get current account information
  Future<AccountInfo> getAccountInfo() async {
    return await _client.getAccountInfo();
  }
  
  /// Check if live trading is available
  bool get isLiveTradingEnabled => _apiKey.isNotEmpty && _apiSecret.isNotEmpty;
  
  /// Dispose resources
  void dispose() {
    _client.dispose();
  }
}