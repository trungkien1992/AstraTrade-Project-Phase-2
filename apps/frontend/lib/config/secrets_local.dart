// secrets_local.dart - Local Configuration File
// NEVER commit this file to version control
// Copy secrets.dart to secrets_local.dart and set your actual values

// Web3Auth Configuration
// Get your client ID from: https://dashboard.web3auth.io/
const String web3AuthClientId = 'YOUR_WEB3AUTH_CLIENT_ID_HERE';

// Extended Exchange API Configuration
// Get your API key from Extended Exchange dashboard
const String extendedExchangeApiKey = 'YOUR_EXTENDED_EXCHANGE_API_KEY_HERE';

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
