import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../providers/auth_provider.dart';

/// Multi-Factor Authentication Settings Screen
/// Allows users to manage MFA settings, connected accounts, and backup options
class MFASettingsScreen extends ConsumerStatefulWidget {
  const MFASettingsScreen({super.key});

  @override
  ConsumerState<MFASettingsScreen> createState() => _MFASettingsScreenState();
}

class _MFASettingsScreenState extends ConsumerState<MFASettingsScreen> {
  bool _isLoading = false;
  bool _mfaEnabled = false;
  List<String> _connectedProviders = [];

  @override
  void initState() {
    super.initState();
    _loadMFAStatus();
  }

  Future<void> _loadMFAStatus() async {
    setState(() => _isLoading = true);

    try {
      final authService = ref.read(authServiceProvider);
      final sessionInfo = await authService.getSessionInfo();
      
      if (sessionInfo != null) {
        setState(() {
          _mfaEnabled = sessionInfo.isLoggedIn; // This would be replaced with actual MFA status
          _connectedProviders = ['Google']; // This would be dynamic based on actual connected providers
        });
      }
    } catch (e) {
      _showErrorSnackBar('Failed to load MFA status: ${e.toString()}');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _toggleMFA(bool enabled) async {
    setState(() => _isLoading = true);

    try {
      final authService = ref.read(authServiceProvider);
      
      if (enabled) {
        await authService.enableMFA();
        _showSuccessSnackBar('MFA enabled successfully');
      } else {
        // Disable MFA logic would go here
        _showInfoSnackBar('MFA disable feature coming soon');
      }
      
      setState(() => _mfaEnabled = enabled);
    } catch (e) {
      _showErrorSnackBar('Failed to toggle MFA: ${e.toString()}');
      setState(() => _mfaEnabled = !enabled); // Revert toggle
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _launchMFASetup() async {
    setState(() => _isLoading = true);

    try {
      final authService = ref.read(authServiceProvider);
      await authService.launchMFASetup();
      _showSuccessSnackBar('MFA setup launched successfully');
    } catch (e) {
      _showErrorSnackBar('Failed to launch MFA setup: ${e.toString()}');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _showSuccessSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.green[700],
        duration: const Duration(seconds: 3),
      ),
    );
  }

  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red[700],
        duration: const Duration(seconds: 4),
      ),
    );
  }

  void _showInfoSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.blue[700],
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
          'Security Settings',
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
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildMFASection(),
                  const SizedBox(height: 24),
                  _buildConnectedAccountsSection(),
                  const SizedBox(height: 24),
                  _buildSecurityOptionsSection(),
                  const SizedBox(height: 24),
                  _buildBackupSection(),
                ],
              ),
            ),
    );
  }

  Widget _buildMFASection() {
    return _buildSection(
      title: 'Multi-Factor Authentication',
      subtitle: 'Add an extra layer of security to your account',
      child: Column(
        children: [
          _buildMFAToggle(),
          if (_mfaEnabled) ...[
            const SizedBox(height: 16),
            _buildMFASetupButton(),
          ],
        ],
      ),
    );
  }

  Widget _buildMFAToggle() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[800]!),
      ),
      child: Row(
        children: [
          Icon(
            _mfaEnabled ? Icons.security : Icons.security_outlined,
            color: _mfaEnabled ? Colors.green : Colors.grey[400],
            size: 24,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Enable MFA',
                  style: GoogleFonts.rajdhani(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                Text(
                  _mfaEnabled ? 'MFA is enabled' : 'MFA is disabled',
                  style: GoogleFonts.rajdhani(
                    fontSize: 14,
                    color: _mfaEnabled ? Colors.green : Colors.grey[400],
                  ),
                ),
              ],
            ),
          ),
          Switch(
            value: _mfaEnabled,
            onChanged: _toggleMFA,
            activeColor: const Color(0xFF7B2CBF),
          ),
        ],
      ),
    );
  }

  Widget _buildMFASetupButton() {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton.icon(
        onPressed: _launchMFASetup,
        icon: const Icon(Icons.settings, size: 20),
        label: Text(
          'Configure MFA Settings',
          style: GoogleFonts.rajdhani(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        style: ElevatedButton.styleFrom(
          backgroundColor: const Color(0xFF7B2CBF),
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
        ),
      ),
    );
  }

  Widget _buildConnectedAccountsSection() {
    return _buildSection(
      title: 'Connected Accounts',
      subtitle: 'Manage your social login providers',
      child: Column(
        children: [
          ..._connectedProviders.map((provider) => _buildConnectedAccount(provider)),
          const SizedBox(height: 12),
          _buildAddAccountButton(),
        ],
      ),
    );
  }

  Widget _buildConnectedAccount(String provider) {
    IconData icon;
    Color color;
    
    switch (provider.toLowerCase()) {
      case 'google':
        icon = Icons.g_mobiledata;
        color = Colors.red;
        break;
      case 'apple':
        icon = Icons.apple;
        color = Colors.white;
        break;
      case 'discord':
        icon = Icons.discord;
        color = const Color(0xFF5865F2);
        break;
      case 'twitter':
        icon = Icons.alternate_email;
        color = const Color(0xFF1DA1F2);
        break;
      case 'github':
        icon = Icons.code;
        color = Colors.white;
        break;
      default:
        icon = Icons.account_circle;
        color = Colors.grey;
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[800]!),
      ),
      child: Row(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              provider,
              style: GoogleFonts.rajdhani(
                fontSize: 16,
                fontWeight: FontWeight.w500,
                color: Colors.white,
              ),
            ),
          ),
          Icon(
            Icons.check_circle,
            color: Colors.green,
            size: 20,
          ),
        ],
      ),
    );
  }

  Widget _buildAddAccountButton() {
    return SizedBox(
      width: double.infinity,
      child: OutlinedButton.icon(
        onPressed: () {
          _showInfoSnackBar('Add account feature coming soon');
        },
        icon: const Icon(Icons.add, size: 20),
        label: Text(
          'Add Another Account',
          style: GoogleFonts.rajdhani(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        style: OutlinedButton.styleFrom(
          foregroundColor: Colors.white,
          side: BorderSide(color: Colors.grey[600]!),
          padding: const EdgeInsets.symmetric(vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
        ),
      ),
    );
  }

  Widget _buildSecurityOptionsSection() {
    return _buildSection(
      title: 'Security Options',
      subtitle: 'Additional security features',
      child: Column(
        children: [
          _buildSecurityOption(
            icon: Icons.fingerprint,
            title: 'Biometric Authentication',
            subtitle: 'Use fingerprint or face unlock',
            trailing: Switch(
              value: false, // This would be dynamic
              onChanged: (value) {
                _showInfoSnackBar('Biometric authentication coming soon');
              },
              activeColor: const Color(0xFF7B2CBF),
            ),
          ),
          const SizedBox(height: 12),
          _buildSecurityOption(
            icon: Icons.phone_android,
            title: 'SMS Verification',
            subtitle: 'Verify with SMS code',
            trailing: const Icon(Icons.chevron_right, color: Colors.grey),
            onTap: () {
              _showInfoSnackBar('SMS verification setup coming soon');
            },
          ),
        ],
      ),
    );
  }

  Widget _buildSecurityOption({
    required IconData icon,
    required String title,
    required String subtitle,
    required Widget trailing,
    VoidCallback? onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.grey[900],
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.grey[800]!),
        ),
        child: Row(
          children: [
            Icon(icon, color: Colors.grey[300], size: 24),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: GoogleFonts.rajdhani(
                      fontSize: 16,
                      fontWeight: FontWeight.w500,
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
            trailing,
          ],
        ),
      ),
    );
  }

  Widget _buildBackupSection() {
    return _buildSection(
      title: 'Backup & Recovery',
      subtitle: 'Secure your account access',
      child: Column(
        children: [
          _buildBackupOption(
            icon: Icons.key,
            title: 'Download Backup Codes',
            subtitle: 'Emergency access codes',
            onTap: () {
              _showInfoSnackBar('Backup codes download coming soon');
            },
          ),
          const SizedBox(height: 12),
          _buildBackupOption(
            icon: Icons.cloud_download,
            title: 'Export Account Data',
            subtitle: 'Download your account information',
            onTap: () {
              _showInfoSnackBar('Account export feature coming soon');
            },
          ),
        ],
      ),
    );
  }

  Widget _buildBackupOption({
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.grey[900],
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.grey[800]!),
        ),
        child: Row(
          children: [
            Icon(icon, color: Colors.grey[300], size: 24),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: GoogleFonts.rajdhani(
                      fontSize: 16,
                      fontWeight: FontWeight.w500,
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
            const Icon(Icons.chevron_right, color: Colors.grey),
          ],
        ),
      ),
    );
  }

  Widget _buildSection({
    required String title,
    required String subtitle,
    required Widget child,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: GoogleFonts.orbitron(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          subtitle,
          style: GoogleFonts.rajdhani(
            fontSize: 14,
            color: Colors.grey[400],
          ),
        ),
        const SizedBox(height: 16),
        child,
      ],
    );
  }
}