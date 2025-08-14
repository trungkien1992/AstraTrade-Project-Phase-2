import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/unified_wallet_onboarding_service.dart';
import '../providers/auth_provider.dart';

/// Wallet Creation Flow Screen
/// Provides a step-by-step wallet creation experience with recovery options
class WalletCreationFlowScreen extends ConsumerStatefulWidget {
  const WalletCreationFlowScreen({super.key});

  @override
  ConsumerState<WalletCreationFlowScreen> createState() => _WalletCreationFlowScreenState();
}

class _WalletCreationFlowScreenState extends ConsumerState<WalletCreationFlowScreen> {
  final PageController _pageController = PageController();
  int _currentStep = 0;
  bool _isLoading = false;
  
  // User input data
  final TextEditingController _usernameController = TextEditingController();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _privateKeyController = TextEditingController();
  final TextEditingController _mnemonicController = TextEditingController();
  
  // Wallet creation result
  WalletOnboardingResult? _creationResult;
  bool _generateMnemonic = true;
  WalletCreationType _selectedType = WalletCreationType.fresh;

  @override
  void dispose() {
    _pageController.dispose();
    _usernameController.dispose();
    _emailController.dispose();
    _privateKeyController.dispose();
    _mnemonicController.dispose();
    super.dispose();
  }

  void _nextStep() {
    if (_currentStep < 4) {
      setState(() => _currentStep++);
      _pageController.nextPage(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
      );
    }
  }

  void _previousStep() {
    if (_currentStep > 0) {
      setState(() => _currentStep--);
      _pageController.previousPage(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
      );
    }
  }

  Future<void> _createWallet() async {
    if (!_validateInputs()) return;

    setState(() => _isLoading = true);

    try {
      WalletOnboardingResult result;
      
      switch (_selectedType) {
        case WalletCreationType.fresh:
          result = await UnifiedWalletOnboardingService.onboardWithFreshWallet(
            username: _usernameController.text.trim(),
            email: _emailController.text.trim(),
            generateMnemonic: _generateMnemonic,
          );
          break;
        case WalletCreationType.privateKey:
          result = await UnifiedWalletOnboardingService.onboardWithPrivateKey(
            privateKey: _privateKeyController.text.trim(),
            username: _usernameController.text.trim(),
            email: _emailController.text.trim(),
          );
          break;
        case WalletCreationType.mnemonic:
          result = await UnifiedWalletOnboardingService.onboardWithMnemonic(
            mnemonic: _mnemonicController.text.trim(),
            username: _usernameController.text.trim(),
            email: _emailController.text.trim(),
          );
          break;
      }

      setState(() {
        _creationResult = result;
        _isLoading = false;
      });

      if (result.isSuccess) {
        // Set user in auth provider
        ref.read(authProvider.notifier).setUser(result.user!);
        _nextStep();
      } else {
        _showError(result.error ?? 'Unknown error occurred');
      }
    } catch (e) {
      setState(() => _isLoading = false);
      _showError('Wallet creation failed: ${e.toString()}');
    }
  }

  bool _validateInputs() {
    if (_usernameController.text.trim().isEmpty) {
      _showError('Please enter a username');
      return false;
    }
    if (_emailController.text.trim().isEmpty) {
      _showError('Please enter an email');
      return false;
    }
    if (_selectedType == WalletCreationType.privateKey && 
        _privateKeyController.text.trim().isEmpty) {
      _showError('Please enter a private key');
      return false;
    }
    if (_selectedType == WalletCreationType.mnemonic && 
        _mnemonicController.text.trim().isEmpty) {
      _showError('Please enter a mnemonic phrase');
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
          'Create Wallet',
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
      body: Column(
        children: [
          // Progress indicator
          _buildProgressIndicator(),
          const SizedBox(height: 20),
          
          // Main content
          Expanded(
            child: PageView(
              controller: _pageController,
              physics: const NeverScrollableScrollPhysics(),
              children: [
                _buildWalletTypeSelection(),
                _buildUserDetailsStep(),
                _buildWalletCredentialsStep(),
                _buildConfirmationStep(),
                _buildSuccessStep(),
              ],
            ),
          ),
          
          // Navigation buttons
          if (_currentStep < 4) _buildNavigationButtons(),
        ],
      ),
    );
  }

  Widget _buildProgressIndicator() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Row(
        children: List.generate(5, (index) {
          final isActive = index <= _currentStep;
          final isCompleted = index < _currentStep;
          
          return Expanded(
            child: Container(
              margin: EdgeInsets.only(right: index < 4 ? 8 : 0),
              height: 4,
              decoration: BoxDecoration(
                color: isActive 
                  ? const Color(0xFF7B2CBF)
                  : Colors.grey[800],
                borderRadius: BorderRadius.circular(2),
              ),
              child: isCompleted
                ? Container(
                    decoration: BoxDecoration(
                      color: const Color(0xFF7B2CBF),
                      borderRadius: BorderRadius.circular(2),
                    ),
                  )
                : null,
            ),
          );
        }),
      ),
    );
  }

  Widget _buildWalletTypeSelection() {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Choose Wallet Type',
            style: GoogleFonts.orbitron(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Select how you want to create or import your wallet',
            style: GoogleFonts.rajdhani(
              fontSize: 16,
              color: Colors.grey[400],
            ),
          ),
          const SizedBox(height: 30),
          
          _buildWalletTypeCard(
            type: WalletCreationType.fresh,
            title: 'Create New Wallet',
            subtitle: 'Generate a brand new wallet with recovery phrase',
            icon: Icons.add_circle_outline,
            color: const Color(0xFF7B2CBF),
          ),
          const SizedBox(height: 16),
          
          _buildWalletTypeCard(
            type: WalletCreationType.privateKey,
            title: 'Import Private Key',
            subtitle: 'Import wallet using existing private key',
            icon: Icons.vpn_key,
            color: const Color(0xFF06B6D4),
          ),
          const SizedBox(height: 16),
          
          _buildWalletTypeCard(
            type: WalletCreationType.mnemonic,
            title: 'Recover from Phrase',
            subtitle: 'Recover wallet using 12-word recovery phrase',
            icon: Icons.restore,
            color: const Color(0xFF10B981),
          ),
          
          if (_selectedType == WalletCreationType.fresh) ...[
            const SizedBox(height: 20),
            _buildMnemonicOption(),
          ],
        ],
      ),
    );
  }

  Widget _buildWalletTypeCard({
    required WalletCreationType type,
    required String title,
    required String subtitle,
    required IconData icon,
    required Color color,
  }) {
    final isSelected = _selectedType == type;
    
    return GestureDetector(
      onTap: () => setState(() => _selectedType = type),
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
            Icon(icon, color: color, size: 28),
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

  Widget _buildMnemonicOption() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[800]!),
      ),
      child: Row(
        children: [
          Expanded(
            child: Text(
              'Generate recovery phrase',
              style: GoogleFonts.rajdhani(
                fontSize: 16,
                fontWeight: FontWeight.w500,
                color: Colors.white,
              ),
            ),
          ),
          Switch(
            value: _generateMnemonic,
            onChanged: (value) => setState(() => _generateMnemonic = value),
            activeColor: const Color(0xFF7B2CBF),
          ),
        ],
      ),
    );
  }

  Widget _buildUserDetailsStep() {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'User Details',
            style: GoogleFonts.orbitron(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Enter your details to create your account',
            style: GoogleFonts.rajdhani(
              fontSize: 16,
              color: Colors.grey[400],
            ),
          ),
          const SizedBox(height: 30),
          
          _buildTextField(
            controller: _usernameController,
            label: 'Username',
            hint: 'Enter your username',
            icon: Icons.person,
          ),
          const SizedBox(height: 20),
          
          _buildTextField(
            controller: _emailController,
            label: 'Email',
            hint: 'Enter your email address',
            icon: Icons.email,
            keyboardType: TextInputType.emailAddress,
          ),
        ],
      ),
    );
  }

  Widget _buildWalletCredentialsStep() {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            _selectedType == WalletCreationType.privateKey 
              ? 'Import Private Key'
              : 'Recovery Phrase',
            style: GoogleFonts.orbitron(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            _selectedType == WalletCreationType.privateKey
              ? 'Enter your private key to import wallet'
              : 'Enter your 12-word recovery phrase',
            style: GoogleFonts.rajdhani(
              fontSize: 16,
              color: Colors.grey[400],
            ),
          ),
          const SizedBox(height: 30),
          
          if (_selectedType == WalletCreationType.privateKey)
            _buildTextField(
              controller: _privateKeyController,
              label: 'Private Key',
              hint: '0x...',
              icon: Icons.vpn_key,
              obscureText: true,
              maxLines: 3,
            ),
          
          if (_selectedType == WalletCreationType.mnemonic)
            _buildTextField(
              controller: _mnemonicController,
              label: 'Recovery Phrase',
              hint: 'word1 word2 word3 ...',
              icon: Icons.restore,
              maxLines: 4,
            ),
        ],
      ),
    );
  }

  Widget _buildConfirmationStep() {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Confirm Details',
            style: GoogleFonts.orbitron(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Review your information before creating wallet',
            style: GoogleFonts.rajdhani(
              fontSize: 16,
              color: Colors.grey[400],
            ),
          ),
          const SizedBox(height: 30),
          
          _buildDetailRow('Wallet Type', _getWalletTypeString()),
          _buildDetailRow('Username', _usernameController.text),
          _buildDetailRow('Email', _emailController.text),
          
          if (_selectedType == WalletCreationType.fresh && _generateMnemonic)
            _buildDetailRow('Recovery Phrase', 'Will be generated'),
          
          const Spacer(),
          
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _isLoading ? null : _createWallet,
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
                    'Create Wallet',
                    style: GoogleFonts.rajdhani(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSuccessStep() {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        children: [
          const SizedBox(height: 60),
          Container(
            width: 100,
            height: 100,
            decoration: BoxDecoration(
              color: const Color(0xFF7B2CBF),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.check,
              color: Colors.white,
              size: 50,
            ),
          ),
          const SizedBox(height: 30),
          
          Text(
            'Wallet Created Successfully!',
            style: GoogleFonts.orbitron(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          
          Text(
            'Your wallet has been created and is ready to use',
            style: GoogleFonts.rajdhani(
              fontSize: 16,
              color: Colors.grey[400],
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 30),
          
          if (_creationResult?.user != null) ...[
            _buildDetailRow('Address', _creationResult!.user!.starknetAddress),
            if (_creationResult!.mnemonic != null) ...[
              const SizedBox(height: 20),
              _buildMnemonicBackup(_creationResult!.mnemonic!),
            ],
          ],
          
          const Spacer(),
          
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () => Navigator.of(context).pop(),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF7B2CBF),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: Text(
                'Continue to App',
                style: GoogleFonts.rajdhani(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    required String hint,
    required IconData icon,
    bool obscureText = false,
    int maxLines = 1,
    TextInputType? keyboardType,
  }) {
    return TextField(
      controller: controller,
      obscureText: obscureText,
      maxLines: maxLines,
      keyboardType: keyboardType,
      style: GoogleFonts.rajdhani(color: Colors.white, fontSize: 16),
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        prefixIcon: Icon(icon, color: const Color(0xFF7B2CBF)),
        labelStyle: GoogleFonts.rajdhani(color: Colors.grey[400]),
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
          borderSide: const BorderSide(color: Color(0xFF7B2CBF)),
        ),
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[800]!),
      ),
      child: Row(
        children: [
          Text(
            '$label:',
            style: GoogleFonts.rajdhani(
              fontSize: 16,
              fontWeight: FontWeight.w500,
              color: Colors.grey[400],
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              value,
              style: GoogleFonts.rajdhani(
                fontSize: 16,
                color: Colors.white,
              ),
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMnemonicBackup(String mnemonic) {
    final words = mnemonic.split(' ');
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.red[900]?.withOpacity(0.2),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.red[800]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.warning, color: Colors.red[400], size: 20),
              const SizedBox(width: 8),
              Text(
                'IMPORTANT: Save Your Recovery Phrase',
                style: GoogleFonts.rajdhani(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: Colors.red[400],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: words.asMap().entries.map((entry) {
              return Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.grey[800],
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  '${entry.key + 1}. ${entry.value}',
                  style: GoogleFonts.rajdhani(
                    fontSize: 12,
                    color: Colors.white,
                  ),
                ),
              );
            }).toList(),
          ),
          const SizedBox(height: 12),
          
          Row(
            children: [
              Expanded(
                child: Text(
                  'Write down these words in order. You\'ll need them to recover your wallet.',
                  style: GoogleFonts.rajdhani(
                    fontSize: 12,
                    color: Colors.grey[400],
                  ),
                ),
              ),
              IconButton(
                onPressed: () {
                  Clipboard.setData(ClipboardData(text: mnemonic));
                  _showSuccess('Recovery phrase copied to clipboard');
                },
                icon: Icon(Icons.copy, color: Colors.grey[400], size: 20),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildNavigationButtons() {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Row(
        children: [
          if (_currentStep > 0)
            Expanded(
              child: OutlinedButton(
                onPressed: _previousStep,
                style: OutlinedButton.styleFrom(
                  foregroundColor: Colors.white,
                  side: BorderSide(color: Colors.grey[600]!),
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: Text(
                  'Previous',
                  style: GoogleFonts.rajdhani(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          
          if (_currentStep > 0) const SizedBox(width: 12),
          
          Expanded(
            child: ElevatedButton(
              onPressed: _currentStep == 3 ? null : _nextStep,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF7B2CBF),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 12),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: Text(
                _currentStep < 3 ? 'Next' : 'Create',
                style: GoogleFonts.rajdhani(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  String _getWalletTypeString() {
    switch (_selectedType) {
      case WalletCreationType.fresh:
        return 'Create New Wallet';
      case WalletCreationType.privateKey:
        return 'Import Private Key';
      case WalletCreationType.mnemonic:
        return 'Recover from Phrase';
    }
  }
}

enum WalletCreationType {
  fresh,
  privateKey,
  mnemonic,
}