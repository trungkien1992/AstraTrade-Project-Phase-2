import '../config/secrets.dart';

/// Application-wide constants for AstraTrade

class AppConstants {
  // App Information
  static const String appName = 'AstraTrade';
  static const String appTagline = 'Advanced Trading Platform';
  static const String appDescription = 'Web3 Trading Revolution';
  static const String appSubtitle =
      'Seamless Social Login • Instant Starknet Wallet';

  // Version
  static const String appVersion = '1.0.0';
  static const String buildNumber = '1';

  // Web3Auth Configuration
  static const String appWeb3AuthClientId =
      web3AuthClientId; // Import from secrets.dart
  static const String web3AuthRedirectUrl = 'astratrade://auth';
  static const String web3AuthDomain = 'astratrade.io'; // Production domain

  // Theme Colors
  static const int primaryColorValue = 0xFF7B2CBF; // Purple
  static const int secondaryColorValue = 0xFF3B82F6; // Blue
  static const int accentColorValue = 0xFF06B6D4; // Cyan
  static const int backgroundColorValue = 0xFF0A0A0A; // Dark

  // Demo Mode Configuration
  static const bool enableDemoMode =
      false; // Disable demo mode for real services

  // Network Configuration
  static const String starknetNetwork =
      'sepolia-alpha'; // testnet for development (updated to Sepolia)
  static const String mainnetNetwork = 'starknet-mainnet';
  static const String starknetRpcUrl =
      'https://starknet-sepolia.public.blastapi.io';

  // API Endpoints
  static const String ragApiBaseUrl = 'http://localhost:8000';
  static const String ragSearchEndpoint = '/search';

  // Database
  static const String hiveBoxPrefix = 'astratrade_';
  static const String userBoxName = '${hiveBoxPrefix}users';
  static const String settingsBoxName = '${hiveBoxPrefix}settings';

  // Animation Durations
  static const int splashDurationSeconds = 3;
  static const int defaultAnimationMs = 300;
  static const int buttonPulseMs = 1000;
  static const Duration defaultAnimationDuration = Duration(
    milliseconds: defaultAnimationMs,
  );

  // UI Dimensions
  static const double borderRadius = 16.0;
  static const double defaultBorderRadius = 12.0;
  static const double cardElevation = 8.0;
  static const double iconSize = 24.0;
  static const double logoSize = 120.0;

  // Text Styles
  static const double titleFontSize = 32.0;
  static const double subtitleFontSize = 18.0;
  static const double bodyFontSize = 16.0;
  static const double captionFontSize = 14.0;

  // Spacing
  static const double paddingSmall = 8.0;
  static const double paddingMedium = 16.0;
  static const double defaultPadding = 16.0;
  static const double paddingLarge = 24.0;
  static const double paddingXLarge = 32.0;

  // Error Messages
  static const String genericErrorMessage =
      'An unexpected error occurred. Please try again.';
  static const String networkErrorMessage =
      'Network error. Please check your connection.';
  static const String authErrorMessage =
      'Authentication failed. Please try again.';
  static const String userCancelledMessage = 'Operation cancelled by user.';

  // Demo Mode Messages
  static const String demoModeTitle = '⚡ Cosmic Demo Mode Active';
  static const String demoModeSubtitle =
      'Risk-free trading • Unlimited practice • Full features';
  static const String simulatedDataMessage =
      'Simulated Market Data - Demo Mode';
  static const String demoPortfolioMessage = 'Demo Portfolio - Practice Mode';

  // Cosmic Login Messages
  static const String cosmicWelcomeTitle = 'Welcome to the Trading Dimension';
  static const String cosmicLoginButton = 'Initiate Cosmic Journey';
  static const String cosmicLoadingMessage = 'Preparing Stellar Navigation...';
  static const String cosmicSubtitle = 'Enter the Quantum Trading Realm';
  static const String cosmicDemoPortalMessage =
      '🌌 Demo Portal Active - Practice Mode Enabled';
  static const String cosmicBenefits =
      'Quantum Wallet Genesis • Seamless Social Authentication • Zero-Knowledge Security';

  // Success Messages
  static const String loginSuccessMessage = 'Successfully signed in!';
  static const String logoutSuccessMessage = 'Successfully signed out!';
  static const String accountCreatedMessage = 'Account created successfully!';

  // Feature Flags
  static const bool enableLogging = true;
  static const bool enableAnalytics = false; // Disabled for privacy
  static const bool enableCrashReporting = false; // Disabled for privacy
  static const bool enableGracefulFallback =
      true; // Enable graceful API fallback

  // URLs
  static const String websiteUrl = 'https://astratrade.io';
  static const String documentationUrl = 'https://docs.astratrade.io';
  static const String supportUrl = 'https://support.astratrade.io';
  static const String privacyPolicyUrl = 'https://astratrade.io/privacy';
  static const String termsOfServiceUrl = 'https://astratrade.io/terms';

  // Social Links
  static const String twitterUrl = 'https://twitter.com/astratrade';
  static const String githubUrl = 'https://github.com/astratrade';
  static const String discordUrl = 'https://discord.gg/astratrade';
}

/// Environment-specific configuration
enum Environment { development, staging, production, demo }

class EnvironmentConfig {
  static const Environment current = Environment.development;

  static bool get isDevelopment => current == Environment.development;
  static bool get isStaging => current == Environment.staging;
  static bool get isProduction => current == Environment.production;
  static bool get isDemo => current == Environment.demo;

  // Demo mode configuration
  static bool get shouldUseDemoData => isDemo || AppConstants.enableDemoMode;
  static bool get shouldShowDemoIndicators => isDemo;
  static bool get shouldUseFallbackData => AppConstants.enableGracefulFallback;

  static String get apiBaseUrl {
    switch (current) {
      case Environment.development:
        return 'http://localhost:8000';
      case Environment.staging:
        return 'https://api-staging.astratrade.io';
      case Environment.production:
        return 'https://api.astratrade.io';
      case Environment.demo:
        return 'http://localhost:8000'; // Demo backend URL
    }
  }

  static String get starknetNetwork {
    switch (current) {
      case Environment.development:
      case Environment.staging:
      case Environment.demo:
        return AppConstants.starknetNetwork; // testnet for demo
      case Environment.production:
        return AppConstants.mainnetNetwork;
    }
  }
}
