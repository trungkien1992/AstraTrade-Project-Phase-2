import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:developer';

import '../services/extended_exchange_api_service.dart';
import '../services/secure_storage_service.dart';

/// Screen for entering Extended Exchange API key
class ExtendedExchangeApiKeyScreen extends ConsumerStatefulWidget {
  const ExtendedExchangeApiKeyScreen({super.key});

  @override
  ConsumerState<ExtendedExchangeApiKeyScreen> createState() => _ExtendedExchangeApiKeyScreenState();
}

class _ExtendedExchangeApiKeyScreenState extends ConsumerState<ExtendedExchangeApiKeyScreen> {
  final _formKey = GlobalKey<FormState>();
  final _apiKeyController = TextEditingController();
  bool _isSaving = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadExistingApiKey();
  }

  /// Load existing API key if available
  Future<void> _loadExistingApiKey() async {
    try {
      final credentials = await SecureStorageService.instance.getTradingCredentials();
      if (credentials != null && credentials['api_key'] != null) {
        setState(() {
          _apiKeyController.text = credentials['api_key'];
        });
      }
    } catch (e) {
      log('Failed to load existing API key: $e');
    }
  }

  /// Save API key
  Future<void> _saveApiKey() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isSaving = true;
      _errorMessage = null;
    });

    try {
      // Validate the API key by making a real API call
      final isValid = await ExtendedExchangeApiService.validateApiKey(_apiKeyController.text);
      
      if (!isValid) {
        setState(() {
          _errorMessage = 'Invalid API key. Please check and try again.';
          _isSaving = false;
        });
        return;
      }

      // Save the API key
      await ExtendedExchangeApiService.saveUserApiKey(_apiKeyController.text);
      
      if (!mounted) return;
      
      // Show success message
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('API key saved successfully!')),
      );
      
      // Navigate back or to the main screen
      Navigator.of(context).pop();
    } catch (e) {
      log('Failed to save API key: $e');
      setState(() {
        _errorMessage = 'Failed to save API key: ${e.toString()}';
        _isSaving = false;
      });
    }
  }

  @override
  void dispose() {
    _apiKeyController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Extended Exchange API Key'),
        backgroundColor: Colors.blue[600],
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Enter your Extended Exchange API Key',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'To enable real trading, please enter your Extended Exchange API key. '
                'You can obtain this from your Extended Exchange account dashboard.',
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey,
                ),
              ),
              const SizedBox(height: 24),
              TextFormField(
                controller: _apiKeyController,
                decoration: const InputDecoration(
                  labelText: 'API Key',
                  hintText: 'Enter your Extended Exchange API key',
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter your API key';
                  }
                  if (value.length < 20) {
                    return 'API key seems too short';
                  }
                  return null;
                },
                obscureText: true,
              ),
              if (_errorMessage != null) ...[
                const SizedBox(height: 16),
                Text(
                  _errorMessage!,
                  style: const TextStyle(
                    color: Colors.red,
                    fontSize: 14,
                  ),
                ),
              ],
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _isSaving ? null : _saveApiKey,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blue[600],
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  child: Text(_isSaving ? 'Saving...' : 'Save API Key'),
                ),
              ),
              const SizedBox(height: 24),
              const Text(
                'How to get your API key:',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                '1. Visit the Extended Exchange website\n'
                '2. Log in to your account\n'
                '3. Go to Account Settings > API Keys\n'
                '4. Create a new API key with trading permissions\n'
                '5. Copy the API key and paste it here',
                style: TextStyle(
                  fontSize: 14,
                  height: 1.5,
                ),
              ),
              const SizedBox(height: 16),
              const Text(
                'Security Note:',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'Your API key is stored securely on your device using hardware-backed encryption. '
                'Never share your API key with anyone.',
                style: TextStyle(
                  fontSize: 14,
                  height: 1.5,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}