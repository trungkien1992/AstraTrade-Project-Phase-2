import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/unified_wallet_onboarding_service.dart';
import '../providers/auth_provider.dart';

/// Wallet Recovery Screen
/// Provides options to recover existing wallets through various methods
class WalletRecoveryScreen extends ConsumerStatefulWidget {
  const WalletRecoveryScreen({super.key});

  @override
  ConsumerState<WalletRecoveryScreen> createState() => _WalletRecoveryScreenState();
}

class _WalletRecoveryScreenState extends ConsumerState<WalletRecoveryScreen> {
  WalletRecoveryInfo? _recoveryInfo;
  bool _isLoading = false;
  RecoveryMethod _selectedMethod = RecoveryMethod.none;
  
  // Controllers for recovery inputs
  final TextEditingController _mnemonicController = TextEditingController();
  final TextEditingController _privateKeyController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadRecoveryInfo();
  }

  @override
  void dispose() {
    _mnemonicController.dispose();
    _privateKeyController.dispose();
    super.dispose();
  }

  Future<void> _loadRecoveryInfo() async {
    setState(() => _isLoading = true);
    
    try {
      final info = await UnifiedWalletOnboardingService.getRecoveryInfo();
      setState(() {
        _recoveryInfo = info;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      _showError('Failed to load recovery information: ${e.toString()}');
    }
  }

  Future<void> _recoverWallet() async {
    if (!_validateRecoveryInputs()) return;

    setState(() => _isLoading = true);

    try {
      WalletOnboardingResult result;
      
      switch (_selectedMethod) {
        case RecoveryMethod.mnemonic:
          result = await UnifiedWalletOnboardingService.onboardWithMnemonic(
            mnemonic: _mnemonicController.text.trim(),
            username: 'RecoveredUser',
            email: 'recovered@astratrade.cosmic',
          );
          break;
        case RecoveryMethod.privateKey:
          result = await UnifiedWalletOnboardingService.onboardWithPrivateKey(
            privateKey: _privateKeyController.text.trim(),
            username: 'RecoveredUser',
            email: 'recovered@astratrade.cosmic',
          );
          break;
        case RecoveryMethod.none:
          throw Exception('No recovery method selected');
      }

      setState(() => _isLoading = false);

      if (result.isSuccess) {
        // Set user in auth provider
        ref.read(authProvider.notifier).setUser(result.user!);
        
        _showSuccess('Wallet recovered successfully!');
        Navigator.of(context).pop();
      } else {
        _showError(result.error ?? 'Recovery failed');
      }
    } catch (e) {
      setState(() => _isLoading = false);
      _showError('Wallet recovery failed: ${e.toString()}');
    }
  }

  bool _validateRecoveryInputs() {
    if (_selectedMethod == RecoveryMethod.mnemonic && 
        _mnemonicController.text.trim().isEmpty) {
      _showError('Please enter your recovery phrase');
      return false;
    }
    if (_selectedMethod == RecoveryMethod.privateKey && 
        _privateKeyController.text.trim().isEmpty) {
      _showError('Please enter your private key');
      return false;
    }
    return true;
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red[700],
        duration: const Duration(seconds: 4),
      ),
    );
  }

  void _showSuccess(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.green[700],
        duration: const Duration(seconds: 3),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0A),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: Text(
          'Recover Wallet',
          style: GoogleFonts.orbitron(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(color: Color(0xFF7B2CBF)),
            )
          : SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildHeaderSection(),
                  const SizedBox(height: 30),
                  
                  if (_recoveryInfo != null) ...[
                    _buildAvailableRecoveryMethods(),
                    const SizedBox(height: 30),
                  ],
                  
                  _buildManualRecoverySection(),
                  const SizedBox(height: 40),
                  
                  if (_selectedMethod != RecoveryMethod.none)
                    _buildRecoverButton(),
                ],
              ),
            ),
    );
  }

  Widget _buildHeaderSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Recover Your Wallet',
          style: GoogleFonts.orbitron(
            fontSize: 28,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'Use your recovery phrase, private key, or stored credentials to restore your wallet',
          style: GoogleFonts.rajdhani(
            fontSize: 16,
            color: Colors.grey[400],
          ),
        ),
      ],
    );
  }

  Widget _buildAvailableRecoveryMethods() {
    if (_recoveryInfo == null || !_recoveryInfo!.hasAnyRecoveryMethod) {
      return Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.grey[900],
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.grey[800]!),
        ),
        child: Row(
          children: [
            Icon(Icons.info, color: Colors.blue[400], size: 24),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                'No stored recovery methods found. Use manual recovery below.',
                style: GoogleFonts.rajdhani(
                  fontSize: 16,
                  color: Colors.grey[300],
                ),
              ),
            ),
          ],
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Stored Recovery Methods',
          style: GoogleFonts.orbitron(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        const SizedBox(height: 16),
        
        if (_recoveryInfo!.hasMnemonic)
          _buildStoredRecoveryCard(
            icon: Icons.restore,
            title: 'Recovery Phrase',
            subtitle: 'Stored securely on this device',
            color: const Color(0xFF10B981),
            onTap: () => _recoverFromStored('mnemonic'),
          ),
        
        if (_recoveryInfo!.hasPrivateKey)
          _buildStoredRecoveryCard(
            icon: Icons.vpn_key,
            title: 'Private Key',
            subtitle: 'Stored securely on this device',
            color: const Color(0xFF06B6D4),
            onTap: () => _recoverFromStored('private_key'),
          ),
        
        if (_recoveryInfo!.hasSocialLogin)
          _buildStoredRecoveryCard(
            icon: Icons.account_circle,
            title: 'Social Login',
            subtitle: 'Recover via ${_recoveryInfo!.socialProvider ?? 'social account'}',
            color: const Color(0xFF7B2CBF),
            onTap: () => _recoverFromStored('social'),
          ),
      ],
    );
  }

  Widget _buildStoredRecoveryCard({
    required IconData icon,
    required String title,
    required String subtitle,
    required Color color,
    required VoidCallback onTap,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(12),
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: color.withOpacity(0.3)),
            ),
            child: Row(
              children: [
                Icon(icon, color: color, size: 24),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: GoogleFonts.rajdhani(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      Text(
                        subtitle,
                        style: GoogleFonts.rajdhani(
                          fontSize: 14,
                          color: Colors.grey[400],
                        ),
                      ),
                    ],
                  ),
                ),
                Icon(Icons.arrow_forward_ios, color: color, size: 16),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildManualRecoverySection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Manual Recovery',
          style: GoogleFonts.orbitron(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        const SizedBox(height: 16),
        
        _buildRecoveryMethodCard(
          method: RecoveryMethod.mnemonic,
          icon: Icons.restore,
          title: 'Recovery Phrase',
          subtitle: 'Enter your 12-word recovery phrase',
          color: const Color(0xFF10B981),
        ),
        const SizedBox(height: 12),
        
        _buildRecoveryMethodCard(
          method: RecoveryMethod.privateKey,
          icon: Icons.vpn_key,
          title: 'Private Key',
          subtitle: 'Enter your wallet private key',
          color: const Color(0xFF06B6D4),
        ),
        
        if (_selectedMethod == RecoveryMethod.mnemonic) ...[
          const SizedBox(height: 20),
          _buildMnemonicInput(),
        ],
        
        if (_selectedMethod == RecoveryMethod.privateKey) ...[
          const SizedBox(height: 20),
          _buildPrivateKeyInput(),
        ],
      ],
    );
  }

  Widget _buildRecoveryMethodCard({
    required RecoveryMethod method,
    required IconData icon,
    required String title,
    required String subtitle,
    required Color color,
  }) {
    final isSelected = _selectedMethod == method;
    
    return GestureDetector(
      onTap: () => setState(() => _selectedMethod = method),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: isSelected ? color.withOpacity(0.2) : Colors.grey[900],
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isSelected ? color : Colors.grey[800]!,
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Row(
          children: [
            Icon(icon, color: color, size: 24),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: GoogleFonts.rajdhani(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  Text(
                    subtitle,
                    style: GoogleFonts.rajdhani(
                      fontSize: 14,
                      color: Colors.grey[400],
                    ),
                  ),
                ],
              ),
            ),
            if (isSelected)
              Icon(Icons.check_circle, color: color, size: 24)
            else
              Icon(Icons.radio_button_unchecked, color: Colors.grey[600], size: 24),
          ],
        ),
      ),
    );
  }

  Widget _buildMnemonicInput() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Enter Recovery Phrase',
          style: GoogleFonts.rajdhani(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        const SizedBox(height: 8),
        TextField(
          controller: _mnemonicController,
          maxLines: 4,
          style: GoogleFonts.rajdhani(color: Colors.white, fontSize: 16),
          decoration: InputDecoration(
            hintText: 'word1 word2 word3 word4 word5 word6...',
            hintStyle: GoogleFonts.rajdhani(color: Colors.grey[600]),
            filled: true,
            fillColor: Colors.grey[900],
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey[800]!),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey[800]!),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFF10B981)),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildPrivateKeyInput() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Enter Private Key',
          style: GoogleFonts.rajdhani(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        const SizedBox(height: 8),
        TextField(
          controller: _privateKeyController,
          maxLines: 3,
          obscureText: true,
          style: GoogleFonts.rajdhani(color: Colors.white, fontSize: 16),
          decoration: InputDecoration(
            hintText: '0x...',
            hintStyle: GoogleFonts.rajdhani(color: Colors.grey[600]),
            filled: true,
            fillColor: Colors.grey[900],
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey[800]!),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey[800]!),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFF06B6D4)),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildRecoverButton() {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: _isLoading ? null : _recoverWallet,
        style: ElevatedButton.styleFrom(
          backgroundColor: const Color(0xFF7B2CBF),
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        child: _isLoading
            ? const CircularProgressIndicator(color: Colors.white)
            : Text(
                'Recover Wallet',
                style: GoogleFonts.rajdhani(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
      ),
    );
  }

  Future<void> _recoverFromStored(String method) async {
    setState(() => _isLoading = true);
    
    try {
      // For stored recovery methods, we would implement the actual recovery logic here
      // For now, show a placeholder message
      _showSuccess('Stored recovery methods not yet implemented');
      
      // TODO: Implement actual recovery from stored credentials
      // This would involve reading the stored data and reconstructing the wallet
      
    } catch (e) {
      _showError('Failed to recover from stored method: ${e.toString()}');
    } finally {
      setState(() => _isLoading = false);
    }
  }
}

enum RecoveryMethod {
  none,
  mnemonic,
  privateKey,
}