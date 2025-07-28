import 'package:purchases_flutter/purchases_flutter.dart';
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
      await Purchases.setLogLevel(LogLevel.debug);
      
      PurchasesConfiguration configuration = PurchasesConfiguration(_apiKey);
      await Purchases.configure(configuration);
      
      _isInitialized = true;
      debugPrint('RevenueCat initialized successfully');
    } catch (e) {
      debugPrint('RevenueCat initialization failed: $e');
    }
  }

  static Future<bool> isSubscriptionActive() async {
    try {
      CustomerInfo customerInfo = await Purchases.getCustomerInfo();
      return customerInfo.entitlements.all[_entitlementId]?.isActive == true;
    } catch (e) {
      debugPrint('Error checking subscription status: $e');
      return false;
    }
  }

  static Future<List<StoreProduct>> getAvailableProducts() async {
    try {
      Offerings offerings = await Purchases.getOfferings();
      if (offerings.current != null) {
        return offerings.current!.availablePackages
            .map((package) => package.storeProduct)
            .toList();
      }
      return [];
    } catch (e) {
      debugPrint('Error fetching products: $e');
      return [];
    }
  }

  static Future<PurchaseResult> purchaseProduct(String productId) async {
    try {
      Offerings offerings = await Purchases.getOfferings();
      Package? package = offerings.current?.availablePackages
          .firstWhere((pkg) => pkg.storeProduct.identifier == productId);
      
      if (package == null) {
        return PurchaseResult(success: false, error: 'Product not found');
      }

      CustomerInfo customerInfo = await Purchases.purchasePackage(package);
      bool isPro = customerInfo.entitlements.all[_entitlementId]?.isActive == true;
      
      return PurchaseResult(success: isPro, customerInfo: customerInfo);
    } catch (e) {
      debugPrint('Purchase failed: $e');
      return PurchaseResult(success: false, error: e.toString());
    }
  }

  static Future<void> restorePurchases() async {
    try {
      await Purchases.restorePurchases();
    } catch (e) {
      debugPrint('Restore failed: $e');
    }
  }
}

class PurchaseResult {
  final bool success;
  final String? error;
  final CustomerInfo? customerInfo;

  PurchaseResult({
    required this.success,
    this.error,
    this.customerInfo,
  });
}