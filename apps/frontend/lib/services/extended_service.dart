import 'package:http/http.dart' as http;
import 'dart:convert';

class ExtendedService {
  static const String baseUrl = 'https://starknet.sepolia.extended.exchange/perp';  // Starknet Sepolia testnet
  static bool isMock = false;  // Enable real Extended Exchange trading

  static Future<Map<String, dynamic>> getOrderBook() async {
    if (isMock) {
      return {'bids': [[100.0, 1.0]], 'asks': [[101.0, 1.0]]};  // Mock data
    }
    // Real API call
    final response = await http.get(Uri.parse('$baseUrl/orderbook'));
    if (response.statusCode == 200) return json.decode(response.body);
    throw Exception('Failed to load order book');
  }

  static Future<String> placeTrade(String type, double amount) async {
    if (isMock) {
      return 'Mock trade placed: $type $amount';  // Mock success
    }
    // Real trade logic
    throw Exception('Trade failed');
  }
}
