# AstraTrade Configuration Guide

This guide explains how to configure AstraTrade for your environment.

## 🔧 Required Configuration

### 1. Web3Auth Setup

**Step 1: Get Web3Auth Client ID**
1. Visit [Web3Auth Dashboard](https://dashboard.web3auth.io)
2. Create a new project
3. Copy your Client ID

**Step 2: Update Configuration**
```dart
// lib/utils/constants.dart
static const String web3AuthClientId = 'YOUR_ACTUAL_CLIENT_ID_HERE';
static const String web3AuthDomain = 'your-actual-domain.com';
```

### 2. Platform Configuration

**iOS Configuration (`ios/Runner/Info.plist`):**
Add URL scheme for Web3Auth redirects:
```xml
<key>CFBundleURLTypes</key>
<array>
  <dict>
    <key>CFBundleURLName</key>
    <string>astratrade.auth</string>
    <key>CFBundleURLSchemes</key>
    <array>
      <string>astratrade</string>
    </array>
  </dict>
</array>
```

**Android Configuration (`android/app/src/main/AndroidManifest.xml`):**
Add intent filter in your MainActivity:
```xml
<activity
    android:name=".MainActivity"
    android:exported="true"
    android:launchMode="singleTop"
    android:theme="@style/LaunchTheme">
    
    <!-- Existing intent filters... -->
    
    <!-- Add this intent filter for Web3Auth -->
    <intent-filter android:autoVerify="true">
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data android:scheme="astratrade" />
    </intent-filter>
</activity>
```

### 3. Environment Configuration

Update the environment in `lib/utils/constants.dart`:

```dart
class EnvironmentConfig {
  // Change this for different environments
  static const Environment current = Environment.development; // or staging, production
}
```

**Development Environment:**
- Uses local RAG system (http://localhost:8000)
- Uses Starknet testnet
- Enables debug logging

**Production Environment:**
- Uses production APIs
- Uses Starknet mainnet
- Disables debug features

## 🎨 Customization

### Branding
Update app branding in `lib/utils/constants.dart`:
```dart
static const String appName = 'YourAppName';
static const String appTagline = 'Your Tagline';
static const String appDescription = 'Your Description';
```

### Theme Colors
Customize colors in `lib/utils/constants.dart`:
```dart
static const int primaryColorValue = 0xFF7B2CBF; // Your primary color
static const int secondaryColorValue = 0xFF3B82F6; // Your secondary color
```

### URLs and Links
Update your URLs in `lib/utils/constants.dart`:
```dart
static const String websiteUrl = 'https://yourwebsite.com';
static const String documentationUrl = 'https://docs.yourwebsite.com';
static const String supportUrl = 'https://support.yourwebsite.com';
```

## 🔒 Security Configuration

### 1. API Keys and Secrets
Never commit sensitive information to version control. Use environment variables or secure configuration files.

### 2. Network Security
- Always use HTTPS in production
- Validate all API responses
- Implement certificate pinning for critical APIs

### 3. Storage Security
- Sensitive data is encrypted using Flutter Secure Storage
- Private keys are never stored in plain text
- User sessions are managed securely

## 🧪 Testing Configuration

### Test Environment Variables
Create test-specific configurations:
```dart
// test/test_config.dart
class TestConfig {
  static const String testClientId = 'test_client_id';
  static const String testRedirectUrl = 'test://auth';
}
```

### Mock Services
For testing, create mock implementations of services:
```dart
// test/mocks/
class MockAuthService extends Mock implements AuthService {}
class MockStarknetService extends Mock implements StarknetService {}
```

## 🚀 Deployment Configuration

### iOS Deployment
1. Configure signing certificates
2. Update bundle identifier
3. Set deployment target to iOS 14.0+
4. Configure App Store Connect

### Android Deployment
1. Generate signing key
2. Update application ID
3. Set minimum SDK to API 26
4. Configure Play Console

### Web Deployment
1. Configure web-specific settings
2. Set up domain and HTTPS
3. Configure PWA settings
4. Set up analytics (if desired)

## 📱 Platform-Specific Notes

### iOS Specific
- Add camera and photo library permissions if needed
- Configure background app refresh
- Set up push notifications (if required)

### Android Specific
- Add internet permission (already included)
- Configure ProGuard rules for release builds
- Set up Android App Bundle

### Web Specific
- Configure Content Security Policy
- Set up service worker for PWA
- Configure CORS for API calls

## 🔍 Debugging

### Enable Debug Mode
```dart
// lib/utils/constants.dart
static const bool enableLogging = true; // Set to false for production
```

### Debug Tools
- Use Flutter Inspector for UI debugging
- Enable network logging for API calls
- Use Riverpod Inspector for state debugging

## 📋 Configuration Checklist

Before deploying to production:

- [ ] Web3Auth Client ID configured
- [ ] Platform-specific URL schemes set up
- [ ] Environment set to production
- [ ] Debug logging disabled
- [ ] All API endpoints updated
- [ ] App branding customized
- [ ] Security configurations verified
- [ ] Platform-specific configurations completed
- [ ] Testing configurations set up
- [ ] Deployment scripts ready

## 🆘 Troubleshooting

### Common Issues

**Web3Auth not working:**
- Verify Client ID is correct
- Check URL scheme configuration
- Ensure platform-specific setup is complete

**Build failures:**
- Run `flutter clean && flutter pub get`
- Check platform-specific configurations
- Verify all dependencies are compatible

**Network issues:**
- Check API endpoints in configuration
- Verify network permissions
- Test with different environments

For more help, check the [main README](../README.md) or create an issue in the repository.