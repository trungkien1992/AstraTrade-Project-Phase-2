# Extended Exchange API Key Management

This document explains how AstraTrade manages Extended Exchange API keys for real trading functionality.

## Overview

AstraTrade allows users to connect their Extended Exchange accounts to enable real trading capabilities. Since Extended Exchange does not provide automated user registration through their API, users must manually obtain their API keys from the Extended Exchange platform and enter them into the AstraTrade application.

## User Flow

1. User creates or imports a wallet in AstraTrade
2. User navigates to the main hub screen
3. User clicks the "API Key" button in the user controls section
4. User is presented with the API Key management screen
5. User enters their Extended Exchange API key
6. AstraTrade validates the API key by making an authenticated request to Extended Exchange
7. If valid, the API key is securely stored on the device
8. User can now access real trading features

## Security

API keys are stored securely using Flutter Secure Storage with hardware-backed encryption:
- Android: Encrypted SharedPreferences with Android Keystore
- iOS: iOS Keychain with hardware-backed encryption

## API Key Validation

AstraTrade validates API keys by making a request to the Extended Exchange account balance endpoint:
```
GET /api/v1/account/balance
Authorization: Bearer {api_key}
```

A key is considered valid if the response status is either:
- 200 (OK) - Valid key with account access
- 403 (Forbidden) - Valid key but insufficient permissions

A key is considered invalid if the response status is:
- 401 (Unauthorized) - Invalid or expired key

## Error Handling

If an API key is found to be invalid during validation:
1. User is prompted to re-enter their API key
2. Previous key is cleared from secure storage
3. User must enter a new, valid API key to continue

## UI Components

### Main Hub Screen
- Added "API Key" button to user controls section
- Button opens the API Key management screen

### API Key Management Screen
- Form for entering Extended Exchange API key
- Validation and secure storage of API key
- Instructions for obtaining API key from Extended Exchange
- Security information about key storage

## Technical Implementation

### Services
- `ExtendedExchangeApiService` - Handles API key management and validation
- `SecureStorageService` - Securely stores API keys using hardware-backed encryption

### Screens
- `ExtendedExchangeApiKeyScreen` - UI for entering and managing API keys
- `MainHubScreen` - Updated to include API key management button

### Routes
- Added `/extended-exchange-api-key` route to main application router

## Future Improvements

1. Automatic API key refresh when keys expire
2. Support for multiple API keys for different accounts
3. Integration with Extended Exchange OAuth for streamlined key management
4. Enhanced key usage monitoring and analytics