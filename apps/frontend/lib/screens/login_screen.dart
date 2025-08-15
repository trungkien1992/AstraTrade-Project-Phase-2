import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:lottie/lottie.dart';
import 'package:astratrade_app/services/auth_service.dart';
import 'package:astratrade_app/providers/auth_provider.dart';
import 'package:astratrade_app/screens/import_wallet_screen.dart';
import 'package:astratrade_app/screens/learn_more_modal.dart';
import 'package:astratrade_app/widgets/enhanced_cosmic_background.dart';
import 'package:astratrade_app/widgets/cosmic_logo.dart';
import 'package:astratrade_app/models/user.dart';
import 'package:astratrade_app/services/wallet_import_service.dart';
import 'package:astratrade_app/services/secure_storage_service.dart';
import 'package:astratrade_app/services/unified_wallet_setup_service.dart';
import 'package:astratrade_app/services/biometric_auth_service.dart';
import 'package:astratrade_app/main.dart';
import 'dart:math' as math;

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;
  
  final BiometricAuthService _biometricService = BiometricAuthService.instance;
  bool _biometricAvailable = false;
  bool _showEmailLogin = false;
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );

    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(parent: _controller, curve: Curves.easeInOut));

    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.3),
      end: Offset.zero,
    ).animate(CurvedAnimation(parent: _controller, curve: Curves.easeOutBack));

    _controller.forward();
    _checkBiometricAvailability();
  }

  Future<void> _checkBiometricAvailability() async {
    try {
      final available = await _biometricService.isBiometricAvailable();
      if (mounted) {
        setState(() {
          _biometricAvailable = available;
        });
      }
    } catch (e) {
      // Biometric check failed, continue without biometric option
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _handleGoogleSignIn() async {
    final authService = ref.read(authServiceProvider);
    final authNotifier = ref.read(authProvider.notifier);

    try {
      await authNotifier.signInWithGoogle();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Sign-in failed: ${e.toString()}'),
            backgroundColor: Colors.red[800],
          ),
        );
      }
    }
  }

  Future<void> _handleAppleSignIn() async {
    final authNotifier = ref.read(authProvider.notifier);

    try {
      await authNotifier.signInWithApple();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Apple sign-in failed: ${e.toString()}'),
            backgroundColor: Colors.red[800],
          ),
        );
      }
    }
  }

  Future<void> _handleDiscordSignIn() async {
    final authNotifier = ref.read(authProvider.notifier);

    try {
      await authNotifier.signInWithDiscord();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Discord sign-in failed: ${e.toString()}'),
            backgroundColor: Colors.red[800],
          ),
        );
      }
    }
  }

  Future<void> _handleTwitterSignIn() async {
    final authNotifier = ref.read(authProvider.notifier);

    try {
      await authNotifier.signInWithTwitter();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Twitter sign-in failed: ${e.toString()}'),
            backgroundColor: Colors.red[800],
          ),
        );
      }
    }
  }

  Future<void> _handleGitHubSignIn() async {
    final authNotifier = ref.read(authProvider.notifier);

    try {
      await authNotifier.signInWithGitHub();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('GitHub sign-in failed: ${e.toString()}'),
            backgroundColor: Colors.red[800],
          ),
        );
      }
    }
  }

  Future<void> _handleEmailSignIn() async {
    if (_emailController.text.trim().isEmpty || _passwordController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please enter both email and password'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    final authNotifier = ref.read(authProvider.notifier);

    try {
      await authNotifier.signInWithEmail(_emailController.text.trim(), _passwordController.text);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Email sign-in failed: ${e.toString()}'),
            backgroundColor: Colors.red[800],
          ),
        );
      }
    }
  }

  Future<void> _handleBiometricSignIn() async {
    try {
      final result = await _biometricService.authenticate(
        reason: 'Please authenticate to access AstraTrade',
      );

      if (result.isSuccess) {
        // Try to restore user from stored data after biometric success
        final authService = ref.read(authServiceProvider);
        final user = await authService.restoreUserFromStoredData();
        
        if (user != null) {
          ref.read(authProvider.notifier).setUser(user);
        } else {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('No stored user data found. Please sign in with a provider.'),
                backgroundColor: Colors.orange,
              ),
            );
          }
        }
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Biometric authentication failed: ${result.message}'),
              backgroundColor: Colors.red[800],
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Biometric sign-in failed: ${e.toString()}'),
            backgroundColor: Colors.red[800],
          ),
        );
      }
    }
  }

  void _navigateToImportWallet() {
    Navigator.of(context).push(
      PageRouteBuilder(
        pageBuilder: (context, animation, secondaryAnimation) =>
            const ImportWalletScreen(),
        transitionsBuilder: (context, animation, secondaryAnimation, child) {
          return SlideTransition(
            position:
                Tween<Offset>(
                  begin: const Offset(1.0, 0.0),
                  end: Offset.zero,
                ).animate(
                  CurvedAnimation(parent: animation, curve: Curves.easeInOut),
                ),
            child: child,
          );
        },
      ),
    );
  }

  void _showLearnMoreModal() {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      builder: (context) => const LearnMoreModal(),
    );
  }

  Future<void> _createFreshWallet() async {
    try {
      print('🚀 Starting fresh wallet creation with trading setup...');

      // Use unified wallet setup service for consistent integration
      final newUser = await UnifiedWalletSetupService.setupFreshWallet(
        username: 'CosmicTrader',
        email: 'fresh-wallet@astratrade.app',
      );

      print('✅ Fresh wallet with trading capabilities created successfully');

      // Debug the user object
      print('📋 User created: ${newUser.toString()}');
      print('🔑 User ID: ${newUser.id}');
      print('📧 User Email: ${newUser.email}');
      print('🏠 User Address: ${newUser.starknetAddress}');

      // Sign in with the new wallet
      print('🔄 Setting user in auth provider...');
      ref.read(authProvider.notifier).setUser(newUser);
      print('✅ User set in auth provider successfully');

      // Navigate directly to main hub screen
      // if (mounted) {
      //   Navigator.of(context).pushReplacement(
      //     MaterialPageRoute(
      //       builder: (context) => DirectMainHubNavigation(user: newUser),
      //     ),
      //   );
      // }

      // Note: Removed page reload workaround - now using proper state management fixes

      // Check auth state after setting user
      final authState = ref.read(authProvider);
      print('🔍 Auth state after setUser: ${authState.toString()}');
      print('🔍 Auth state has value: ${authState.hasValue}');
      print('🔍 Auth state value: ${authState.value?.toString() ?? 'null'}');

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              '🎉 Fresh wallet created with trading! \nAddress: ${newUser.starknetAddress.substring(0, 6)}...${newUser.starknetAddress.substring(newUser.starknetAddress.length - 4)}',
            ),
            backgroundColor: Colors.green[700],
            duration: const Duration(seconds: 4),
          ),
        );
      }
    } catch (e, stack) {
      print('💥 Wallet creation failed: $e');
      print('📍 Error type: ${e.runtimeType}');
      print('📍 Stack trace: $stack');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ Failed to create wallet: ${e.toString()}'),
            backgroundColor: Colors.red[800],
            duration: const Duration(seconds: 5),
          ),
        );
      }
    }
  }

  String _generateFreshPrivateKey() {
    try {
      // Generate cryptographically secure random bytes
      final random = math.Random.secure();
      final bytes = List<int>.generate(32, (_) => random.nextInt(256));

      // Convert to hex string
      final hexString = bytes
          .map((b) => b.toRadixString(16).padLeft(2, '0'))
          .join();

      // Ensure it's exactly 64 characters (32 bytes)
      final privateKey = '0x$hexString';

      print(
        'Generated private key: ${privateKey.substring(0, 10)}...${privateKey.substring(privateKey.length - 8)}',
      );
      return privateKey;
    } catch (e) {
      print('Error generating private key: $e');
      throw Exception('Failed to generate private key: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);

    return Scaffold(
      body: Stack(
        children: [
          // const EnhancedCosmicParticleBackground(),
          SafeArea(
            child: Center(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: FadeTransition(
                  opacity: _fadeAnimation,
                  child: SlideTransition(
                    position: _slideAnimation,
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        // Logo and Title
                        _buildCosmicLogo(),
                        const SizedBox(height: 20),

                        // Welcome Text
                        _buildWelcomeText(),
                        const SizedBox(height: 20),

                        // Authentication Cards
                        _buildAuthCards(authState),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),

          if (authState.isLoading)
            Container(
              color: Colors.black54,
              child: const Center(
                child: CircularProgressIndicator(color: Color(0xFF7B2CBF)),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildCosmicLogo() {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        // const CosmicLogo(
        //   size: 100,
        //   animate: true,
        // ),
        const SizedBox(height: 8),
        Text(
          'AstraTrade',
          style: GoogleFonts.orbitron(
            fontSize: 28,
            fontWeight: FontWeight.bold,
            color: Colors.white,
            letterSpacing: 1.5,
          ),
        ),
        Text(
          'Cosmic Perpetuals Trading',
          style: GoogleFonts.rajdhani(
            fontSize: 14,
            color: Colors.cyan.withOpacity(0.8),
          ),
        ),
      ],
    );
  }

  Widget _buildWelcomeText() {
    return Text(
      'Choose your path',
      style: GoogleFonts.orbitron(
        fontSize: 20,
        fontWeight: FontWeight.bold,
        color: Colors.white,
      ),
    );
  }

  Widget _buildAuthCards(AsyncValue<User?> authState) {
    return Column(
      children: [
        // Primary CTA - Fresh Wallet Creation
        _buildCreateWalletCard(),
        const SizedBox(height: 12),

        // Secondary - Import Existing Wallet
        _buildImportWalletCard(),
        const SizedBox(height: 12),

        // Tertiary - Social Login (inconvenient placement)
        _buildSocialLoginCard(),

        // Learn More as subtle text link
        const SizedBox(height: 8),
        _buildLearnMoreLink(),
      ],
    );
  }

  Widget _buildCreateWalletCard() {
    return _CosmicAuthCard(
      gradient: const LinearGradient(
        colors: [Color(0xFF7B2CBF), Color(0xFF9D4EDD)],
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
      ),
      icon: Icons.add_circle_outline,
      title: 'Create Fresh Wallet',
      subtitle: 'Generate a new Starknet wallet instantly',
      primaryAction: 'Create Wallet',
      secondaryAction: 'Quick Setup',
      onPrimaryTap: _createFreshWallet,
      onSecondaryTap: _createFreshWallet,
      isPrimary: true,
    );
  }

  Widget _buildImportWalletCard() {
    return _CosmicAuthCard(
      gradient: const LinearGradient(
        colors: [Color(0xFF06B6D4), Color(0xFF0891B2)],
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
      ),
      icon: Icons.vpn_key,
      title: 'Import Existing Wallet',
      subtitle: 'Already have a Starknet wallet? Import it here',
      primaryAction: 'Import Wallet',
      onPrimaryTap: _navigateToImportWallet,
    );
  }

  Widget _buildSocialLoginCard() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 8.0),
      child: Column(
        children: [
          const SizedBox(height: 12),
          Text(
            'Or connect with social accounts',
            style: GoogleFonts.rajdhani(fontSize: 12, color: Colors.white54),
          ),
          const SizedBox(height: 12),
          // Row 1: Google, Apple, Discord
          Row(
            children: [
              Expanded(
                child: _buildSocialButton(
                  'Google',
                  Icons.g_mobiledata,
                  Colors.red,
                  _handleGoogleSignIn,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _buildSocialButton(
                  'Apple',
                  Icons.apple,
                  Colors.white,
                  _handleAppleSignIn,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _buildSocialButton(
                  'Discord',
                  Icons.discord,
                  const Color(0xFF5865F2),
                  _handleDiscordSignIn,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          // Row 2: Twitter, GitHub, Email
          Row(
            children: [
              Expanded(
                child: _buildSocialButton(
                  'Twitter',
                  Icons.alternate_email,
                  const Color(0xFF1DA1F2),
                  _handleTwitterSignIn,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _buildSocialButton(
                  'GitHub',
                  Icons.code,
                  Colors.white,
                  _handleGitHubSignIn,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _buildSocialButton(
                  'Email',
                  Icons.email,
                  Colors.cyan,
                  () {
                    setState(() {
                      _showEmailLogin = !_showEmailLogin;
                    });
                  },
                ),
              ),
            ],
          ),
          // Email login form
          if (_showEmailLogin) ...[
            const SizedBox(height: 16),
            _buildEmailLoginForm(),
          ],
          // Biometric login option
          if (_biometricAvailable) ...[
            const SizedBox(height: 12),
            _buildBiometricButton(),
          ],
        ],
      ),
    );
  }

  Widget _buildSocialButton(
    String label,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return OutlinedButton(
      onPressed: onTap,
      style: OutlinedButton.styleFrom(
        foregroundColor: Colors.white,
        side: BorderSide(color: color.withOpacity(0.5)),
        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
        minimumSize: const Size(0, 32),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 16, color: color),
          const SizedBox(width: 4),
          Text(
            label,
            style: GoogleFonts.rajdhani(
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmailLoginForm() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[800]!),
      ),
      child: Column(
        children: [
          TextField(
            controller: _emailController,
            decoration: InputDecoration(
              labelText: 'Email',
              labelStyle: GoogleFonts.rajdhani(color: Colors.grey[400]),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: BorderSide(color: Colors.grey[600]!),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: BorderSide(color: Colors.grey[600]!),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: const BorderSide(color: Color(0xFF7B2CBF)),
              ),
              filled: true,
              fillColor: Colors.grey[800],
            ),
            style: GoogleFonts.rajdhani(color: Colors.white),
            keyboardType: TextInputType.emailAddress,
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _passwordController,
            decoration: InputDecoration(
              labelText: 'Password',
              labelStyle: GoogleFonts.rajdhani(color: Colors.grey[400]),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: BorderSide(color: Colors.grey[600]!),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: BorderSide(color: Colors.grey[600]!),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: const BorderSide(color: Color(0xFF7B2CBF)),
              ),
              filled: true,
              fillColor: Colors.grey[800],
            ),
            style: GoogleFonts.rajdhani(color: Colors.white),
            obscureText: true,
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _handleEmailSignIn,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF7B2CBF),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 12),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: Text(
                'Sign In',
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

  Widget _buildBiometricButton() {
    return SizedBox(
      width: double.infinity,
      child: OutlinedButton.icon(
        onPressed: _handleBiometricSignIn,
        icon: const Icon(Icons.fingerprint, size: 20),
        label: Text(
          'Use Biometric Login',
          style: GoogleFonts.rajdhani(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        style: OutlinedButton.styleFrom(
          foregroundColor: Colors.cyan,
          side: const BorderSide(color: Colors.cyan),
          padding: const EdgeInsets.symmetric(vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
        ),
      ),
    );
  }

  Widget _buildLearnMoreLink() {
    return TextButton(
      onPressed: _showLearnMoreModal,
      child: Text(
        'Learn about Starknet & self-custody →',
        style: GoogleFonts.rajdhani(
          fontSize: 14,
          color: Colors.cyan.withOpacity(0.8),
          decoration: TextDecoration.underline,
        ),
      ),
    );
  }
}

class _CosmicAuthCard extends StatelessWidget {
  final Gradient gradient;
  final IconData icon;
  final String title;
  final String subtitle;
  final String primaryAction;
  final String? secondaryAction;
  final VoidCallback onPrimaryTap;
  final VoidCallback? onSecondaryTap;
  final bool isPrimary;

  const _CosmicAuthCard({
    required this.gradient,
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.primaryAction,
    this.secondaryAction,
    required this.onPrimaryTap,
    this.onSecondaryTap,
    this.isPrimary = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.symmetric(horizontal: 8.0),
      decoration: BoxDecoration(
        gradient: gradient,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color:
                (isPrimary ? const Color(0xFF7B2CBF) : const Color(0xFF06B6D4))
                    .withOpacity(0.3),
            blurRadius: 20,
            spreadRadius: 2,
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              children: [
                Icon(icon, size: 24, color: Colors.white),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    title,
                    style: GoogleFonts.orbitron(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              subtitle,
              style: GoogleFonts.rajdhani(fontSize: 12, color: Colors.white70),
            ),
            const SizedBox(height: 12),
            _buildActionButtons(),
          ],
        ),
      ),
    );
  }

  Widget _buildActionButtons() {
    return Column(
      children: [
        SizedBox(
          width: double.infinity,
          child: ElevatedButton(
            onPressed: onPrimaryTap,
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.white.withOpacity(0.2),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 12),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
              elevation: 0,
            ),
            child: Text(
              primaryAction,
              style: GoogleFonts.rajdhani(
                fontSize: 14,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
        if (secondaryAction != null) ...[
          const SizedBox(height: 8),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton(
              onPressed: onSecondaryTap,
              style: OutlinedButton.styleFrom(
                foregroundColor: Colors.white,
                side: BorderSide(color: Colors.white.withOpacity(0.3)),
                padding: const EdgeInsets.symmetric(vertical: 12),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: Text(
                secondaryAction!,
                style: GoogleFonts.rajdhani(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
        ],
      ],
    );
  }
}
