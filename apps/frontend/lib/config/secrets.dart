// secrets.dart - Configuration Template
// Copy this file to secrets_local.dart and set your actual values
// NEVER commit actual secrets to version control

// Web3Auth Configuration
// Get your client ID from: https://dashboard.web3auth.io/
const String web3AuthClientId = String.fromEnvironment(
  'WEB3AUTH_CLIENT_ID',
  defaultValue:
      'BPPbhL4egAYdv3vHFVQDhmueoOJKUeHJZe2X8LaMvMIq9go2GN72j6OwvheQkR2ofq8WveHJQtzNKaq0_o_xKuI',
);

// Extended Exchange API Configuration
// Get your API key from Extended Exchange dashboard
const String extendedExchangeApiKey = String.fromEnvironment(
  'EXTENDED_EXCHANGE_API_KEY',
  defaultValue: '', // Set via environment variable or secrets_local.dart
);

// Demo mode configuration for judges and testing
class DemoConfig {
  static const bool isDemoMode = bool.fromEnvironment(
    'DEMO_MODE',
    defaultValue: false,
  );

  // Demo credentials (safe for public use)
  static const String demoClientId = 'demo-astratrade-mobile-client-id';
  static const String demoUserId = 'demo-user-12345';

  // Use demo config when in demo mode
  static String get clientId => isDemoMode ? demoClientId : web3AuthClientId;
}
