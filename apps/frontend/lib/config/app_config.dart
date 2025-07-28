import 'package:flutter/foundation.dart';

enum Environment {
  development,
  staging,
  production,
}

/// Production-ready application configuration
class AppConfig {
  static const Environment _environment = kDebugMode 
      ? Environment.development 
      : Environment.production;

  // App Information
  static const String appName = 'AstraTrade';
  static const String appVersion = '1.0.0';
  static const String buildNumber = '1';
  static const String apiVersion = 'v1';
  
  // Environment Detection
  static bool get isProduction => _environment == Environment.production;
  static bool get isDevelopment => _environment == Environment.development;
  static bool get isStaging => _environment == Environment.staging;
  
  // Base URL Configuration
  static String get baseUrl {
    switch (_environment) {
      case Environment.development:
        return 'http://localhost:8000';
      case Environment.staging:
        return 'https://staging-api.astratrade.app';
      case Environment.production:
        return 'https://api.astratrade.app';
    }
  }
  
  // Legacy feature flags (maintained for compatibility)
  static const bool enableClans = true;
  static const bool enableNFTs = true;
  static const bool enablePrestige = true;
  static const bool enableViral = true;
  
  // New Production Features
  static bool get enableAnalytics => isProduction || isStaging;
  static bool get enableCrashReporting => isProduction || isStaging;
  static bool get enablePerformanceMonitoring => true;
  static bool get enableABTesting => true;
  static bool get enableBetaFeatures => isDevelopment || isStaging;
  
  // API Endpoints
  static String get apiUrl => '$baseUrl/api/$apiVersion';
  static String get authUrl => '$apiUrl/auth';
  static String get leaderboardUrl => '$apiUrl/leaderboard';
  static String get clansUrl => '$apiUrl/clans';
  static String get nftUrl => '$apiUrl/nft-marketplace';
  static String get prestigeUrl => '$apiUrl/prestige';
  static String get viralUrl => '$apiUrl/viral';
  static String get healthUrl => '$apiUrl/health';
  static String get metricsUrl => '$apiUrl/metrics';
  
  // Revenue Cat Configuration
  static String get revenueCatApiKey {
    switch (_environment) {
      case Environment.development:
        return 'rcat_dev_key_placeholder';
      case Environment.staging:
        return 'rcat_staging_key_placeholder';
      case Environment.production:
        return 'rcat_prod_key_placeholder';
    }
  }
  
  // Performance Configuration
  static const int maxCacheSize = 50 * 1024 * 1024; // 50MB
  static const Duration networkTimeout = Duration(seconds: 30);
  static const int maxRetryAttempts = 3;
  static const Duration healthCheckInterval = Duration(minutes: 5);
  
  // Beta Configuration
  static const bool isBetaVersion = true;
  static const String betaTestGroup = 'beta_v1_0_0';
  static const int maxBetaUsers = 1000;
  
  // App Store Configuration
  static const String appStoreId = '6478123456'; // Placeholder
  static const String playStoreId = 'com.astratrade.app';
  
  // Support Configuration
  static const String supportEmail = 'support@astratrade.app';
  static const String feedbackEmail = 'feedback@astratrade.app';
  static const String privacyPolicyUrl = 'https://astratrade.app/privacy';
  static const String termsOfServiceUrl = 'https://astratrade.app/terms';
}
