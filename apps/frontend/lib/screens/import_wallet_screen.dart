import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:starknet/starknet.dart';
import 'package:astratrade_app/services/secure_storage_service.dart';
import 'package:astratrade_app/services/wallet_import_service.dart';
import 'package:astratrade_app/services/extended_exchange_api_service.dart';
import 'package:astratrade_app/services/unified_wallet_setup_service.dart';
import 'package:astratrade_app/widgets/cosmic_particle_background.dart';
import 'package:astratrade_app/providers/auth_provider.dart';
import 'package:astratrade_app/models/user.dart';

class ImportWalletScreen extends ConsumerStatefulWidget {
  const ImportWalletScreen({super.key});

  @override
  ConsumerState<ImportWalletScreen> createState() => _ImportWalletScreenState();
}

class _ImportWalletScreenState extends ConsumerState<ImportWalletScreen> {
  final _formKey = GlobalKey<FormState>();
  final _seedPhraseController = TextEditingController();
  final _privateKeyController = TextEditingController();
  final _walletImportService = WalletImportService();
  final _secureStorage = SecureStorageService.instance;

  bool _obscureSeedPhrase = true;
  bool _obscurePrivateKey = true;
  bool _isValidating = false;
  String? _derivedAddress;
  String? _validationError;
  ImportType _selectedType = ImportType.seedPhrase;

  @override
  void dispose() {
    _seedPhraseController.dispose();
    _privateKeyController.dispose();
    super.dispose();
  }

  Future<void> _validateAndImport() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isValidating = true;
      _validationError = null;
    });

    try {
      String? address;
      String? privateKey;

      if (_selectedType == ImportType.seedPhrase) {
        final seedPhrase = _seedPhraseController.text.trim();
        address = await _walletImportService.deriveAddressFromSeedPhrase(
          seedPhrase,
        );
        privateKey = await _walletImportService.derivePrivateKeyFromSeedPhrase(
          seedPhrase,
        );
      } else {
        final privateKeyHex = _privateKeyController.text.trim();
        address = await _walletImportService.deriveAddressFromPrivateKey(
          privateKeyHex,
        );
        privateKey = privateKeyHex;
      }

      if (address != null && privateKey != null) {
        setState(() {
          _derivedAddress = address;
        });

        // Show confirmation dialog
        _showConfirmationDialog(address!, privateKey!);
      } else {
        setState(() {
          _validationError = 'Invalid wallet format';
        });
      }
    } catch (e) {
      setState(() {
        _validationError = 'Validation failed: ${e.toString()}';
      });
    } finally {
      setState(() {
        _isValidating = false;
      });
    }
  }

  void _showConfirmationDialog(String address, String privateKey) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1E1B4B),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Text(
          'Confirm Wallet Import',
          style: GoogleFonts.orbitron(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Starknet Address:',
              style: GoogleFonts.rajdhani(color: Colors.white70, fontSize: 14),
            ),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.black26,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                '${address.substring(0, 6)}...${address.substring(address.length - 4)}',
                style: GoogleFonts.rajdhani(color: Colors.white, fontSize: 16),
              ),
            ),
            const SizedBox(height: 16),
            Text(
              'This wallet will be securely stored on your device.',
              style: GoogleFonts.rajdhani(color: Colors.white70, fontSize: 14),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text(
              'Cancel',
              style: GoogleFonts.rajdhani(color: Colors.white70),
            ),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.of(context).pop();
              await _completeImport(address, privateKey);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF7B2CBF),
            ),
            child: Text(
              'Import Wallet',
              style: GoogleFonts.rajdhani(color: Colors.white),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _completeImport(String address, String privateKey) async {
    try {
      print('🔑 Starting wallet import with trading setup...');

      // Use unified wallet setup service for consistent Extended Exchange integration
      final user = await UnifiedWalletSetupService.setupImportedWallet(
        privateKey: privateKey,
        username: 'ImportedTrader',
        email: 'imported@astratrade.cosmic',
      );

      print('✅ Imported wallet with trading capabilities setup successfully');

      // Update auth provider with the imported user
      ref.read(authProvider.notifier).setUser(user);

      if (mounted) {
        // Show success message
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('Wallet imported successfully!'),
            backgroundColor: Colors.green[700],
            duration: const Duration(seconds: 2),
          ),
        );

        // Navigate back to login screen - auth provider will handle showing main hub
        Navigator.of(context).popUntil((route) => route.isFirst);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Import failed: ${e.toString()}'),
            backgroundColor: Colors.red[800],
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: Stack(
        children: [
          const CosmicParticleBackground(),
          SafeArea(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24.0),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildHeader(),
                    const SizedBox(height: 32),
                    _buildImportTypeSelector(),
                    const SizedBox(height: 24),
                    _selectedType == ImportType.seedPhrase
                        ? _buildSeedPhraseInput()
                        : _buildPrivateKeyInput(),
                    const SizedBox(height: 32),
                    _buildValidationStatus(),
                    const SizedBox(height: 24),
                    _buildImportButton(),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Import Your Wallet',
          style: GoogleFonts.orbitron(
            fontSize: 28,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'Securely connect your existing Starknet wallet',
          style: GoogleFonts.rajdhani(fontSize: 16, color: Colors.white70),
        ),
      ],
    );
  }

  Widget _buildImportTypeSelector() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Expanded(
            child: _ImportTypeButton(
              title: 'Seed Phrase',
              isSelected: _selectedType == ImportType.seedPhrase,
              onTap: () =>
                  setState(() => _selectedType = ImportType.seedPhrase),
            ),
          ),
          Expanded(
            child: _ImportTypeButton(
              title: 'Private Key',
              isSelected: _selectedType == ImportType.privateKey,
              onTap: () =>
                  setState(() => _selectedType = ImportType.privateKey),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSeedPhraseInput() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Seed Phrase (12 or 24 words)',
          style: GoogleFonts.rajdhani(
            fontSize: 16,
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        TextFormField(
          controller: _seedPhraseController,
          obscureText: _obscureSeedPhrase,
          maxLines: _obscureSeedPhrase ? 1 : 3,
          style: GoogleFonts.rajdhani(color: Colors.white),
          decoration: InputDecoration(
            hintText: 'Enter your 12 or 24 word seed phrase...',
            hintStyle: GoogleFonts.rajdhani(color: Colors.white54),
            filled: true,
            fillColor: Colors.white.withOpacity(0.1),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide.none,
            ),
            suffixIcon: IconButton(
              icon: Icon(
                _obscureSeedPhrase ? Icons.visibility : Icons.visibility_off,
                color: Colors.white70,
              ),
              onPressed: () =>
                  setState(() => _obscureSeedPhrase = !_obscureSeedPhrase),
            ),
          ),
          validator: (value) {
            if (value == null || value.trim().isEmpty) {
              return 'Please enter your seed phrase';
            }
            final words = value.trim().split(RegExp(r'\s+'));
            if (words.length != 12 && words.length != 24) {
              return 'Seed phrase must be 12 or 24 words';
            }
            return null;
          },
        ),
      ],
    );
  }

  Widget _buildPrivateKeyInput() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Private Key (Hex)',
          style: GoogleFonts.rajdhani(
            fontSize: 16,
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        TextFormField(
          controller: _privateKeyController,
          obscureText: _obscurePrivateKey,
          style: GoogleFonts.rajdhani(color: Colors.white),
          decoration: InputDecoration(
            hintText: '0x...',
            hintStyle: GoogleFonts.rajdhani(color: Colors.white54),
            filled: true,
            fillColor: Colors.white.withOpacity(0.1),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide.none,
            ),
            suffixIcon: IconButton(
              icon: Icon(
                _obscurePrivateKey ? Icons.visibility : Icons.visibility_off,
                color: Colors.white70,
              ),
              onPressed: () =>
                  setState(() => _obscurePrivateKey = !_obscurePrivateKey),
            ),
          ),
          validator: (value) {
            if (value == null || value.trim().isEmpty) {
              return 'Please enter your private key';
            }
            if (!value.trim().startsWith('0x')) {
              return 'Private key must start with 0x';
            }
            String cleanKey = value.trim().startsWith('0x')
                ? value.trim().substring(2)
                : value.trim();
            if (cleanKey.length < 64 || cleanKey.length > 66) {
              return 'Private key must be 64-66 hex characters (after 0x)';
            }
            if (!RegExp(r'^[0-9a-fA-F]{64,66}$').hasMatch(cleanKey)) {
              return 'Private key must contain only hex characters (0-9, a-f, A-F)';
            }
            return null;
          },
        ),
      ],
    );
  }

  Widget _buildValidationStatus() {
    if (_validationError != null) {
      return Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.red.withOpacity(0.2),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: Colors.red.withOpacity(0.5)),
        ),
        child: Text(
          _validationError!,
          style: GoogleFonts.rajdhani(color: Colors.red[300]),
        ),
      );
    }

    if (_derivedAddress != null) {
      return Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.green.withOpacity(0.2),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: Colors.green.withOpacity(0.5)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Wallet Validated',
              style: GoogleFonts.rajdhani(
                color: Colors.green[300],
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              'Address: ${_derivedAddress!.substring(0, 6)}...${_derivedAddress!.substring(_derivedAddress!.length - 4)}',
              style: GoogleFonts.rajdhani(
                color: Colors.green[300],
                fontSize: 12,
              ),
            ),
          ],
        ),
      );
    }

    return const SizedBox.shrink();
  }

  Widget _buildImportButton() {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: _isValidating ? null : _validateAndImport,
        style: ElevatedButton.styleFrom(
          backgroundColor: const Color(0xFF7B2CBF),
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        child: _isValidating
            ? const SizedBox(
                height: 20,
                width: 20,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                ),
              )
            : Text(
                'Validate & Import',
                style: GoogleFonts.rajdhani(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
      ),
    );
  }
}

class _ImportTypeButton extends StatelessWidget {
  final String title;
  final bool isSelected;
  final VoidCallback onTap;

  const _ImportTypeButton({
    required this.title,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFF7B2CBF) : Colors.transparent,
          borderRadius: BorderRadius.circular(8),
        ),
        child: Center(
          child: Text(
            title,
            style: GoogleFonts.rajdhani(
              color: isSelected ? Colors.white : Colors.white70,
              fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
            ),
          ),
        ),
      ),
    );
  }
}

enum ImportType { seedPhrase, privateKey }
