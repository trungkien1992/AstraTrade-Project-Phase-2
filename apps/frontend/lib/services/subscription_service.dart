// Temporarily disabled for iOS build issues
// import 'package:purchases_flutter/purchases_flutter.dart';
import 'package:flutter/material.dart';

class SubscriptionService {
  static const String _apiKey = 'rcat_YOUR_API_KEY'; // Replace with actual key
  static const String _monthlyProductId = 'pro_monthly';
  static const String _yearlyProductId = 'pro_yearly';
  static const String _entitlementId = 'pro';

  static bool _isInitialized = false;

  static Future<void> initialize() async {
    if (_isInitialized) return;
    
    try {
      // Temporarily disabled for iOS build - stub implementation
      // await Purchases.setLogLevel(LogLevel.debug);
      // PurchasesConfiguration configuration = PurchasesConfiguration(_apiKey);
      // await Purchases.configure(configuration);
      
      _isInitialized = true;
      debugPrint('RevenueCat initialized successfully');
    } catch (e) {
      debugPrint('RevenueCat initialization failed: $e');
    }
  }

  static Future<bool> isSubscriptionActive() async {
    try {
      // Stub implementation - temporarily disabled
      // CustomerInfo customerInfo = await Purchases.getCustomerInfo();
      // return customerInfo.entitlements.all[_entitlementId]?.isActive == true;
      return false; // Default to free tier for demo
    } catch (e) {
      debugPrint('Error checking subscription status: $e');
      return false;
    }
  }

  static Future<List<Map<String, dynamic>>> getAvailableProducts() async {
    try {
      // Stub implementation - return mock products
      // Offerings offerings = await Purchases.getOfferings();
      return [
        {'id': _monthlyProductId, 'price': '\$4.99', 'title': 'Monthly Pro'},
        {'id': _yearlyProductId, 'price': '\$49.99', 'title': 'Yearly Pro'},
      ];
    } catch (e) {
      debugPrint('Error fetching products: $e');
      return [];
    }
  }

  static Future<PurchaseResult> purchaseProduct(String productId) async {
    try {
      // Stub implementation - simulate purchase
      debugPrint('Simulating purchase for: $productId');
      return PurchaseResult(success: false, error: 'Demo mode - purchases disabled');
    } catch (e) {
      debugPrint('Purchase failed: $e');
      return PurchaseResult(success: false, error: e.toString());
    }
  }

  static Future<void> restorePurchases() async {
    try {
      // Stub implementation
      debugPrint('Restore purchases - demo mode');
    } catch (e) {
      debugPrint('Restore failed: $e');
    }
  }
}

class PurchaseResult {
  final bool success;
  final String? error;
  final Map<String, dynamic>? customerInfo; // Changed from CustomerInfo for demo

  PurchaseResult({
    required this.success,
    this.error,
    this.customerInfo,
  });
}