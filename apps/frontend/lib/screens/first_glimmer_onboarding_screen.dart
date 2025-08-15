import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lottie/lottie.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../providers/auth_provider.dart';
import '../providers/xp_provider.dart';
import '../services/auth_service.dart';
import '../services/haptic_service.dart';
// import '../services/cosmic_animation_service.dart';
// import '../models/planet_biome.dart';
// import '../widgets/enhanced_cosmic_planet_3d.dart';
// import '../widgets/cosmic_particles.dart';
import 'dart:math' as math;

/// First Glimmer Onboarding Screen - Gamified cosmic quest introduction
/// Implements the "First Glimmer" onboarding flow as specified in the implementation plan
class FirstGlimmerOnboardingScreen extends ConsumerStatefulWidget {
  const FirstGlimmerOnboardingScreen({super.key});

  @override
  ConsumerState<FirstGlimmerOnboardingScreen> createState() =>
      _FirstGlimmerOnboardingScreenState();
}

class _FirstGlimmerOnboardingScreenState
    extends ConsumerState<FirstGlimmerOnboardingScreen>
    with TickerProviderStateMixin {
  late AnimationController _cosmicGlowController;
  late AnimationController _particleController;
  late AnimationController _transitionController;
  late AnimationController _planetBirthController;
  late AnimationController _textAnimationController;

  OnboardingStep _currentStep = OnboardingStep.cosmicAwakening;
  // PlanetBiome _selectedCosmicSeed = PlanetBiome.verdant;
  bool _isProcessing = false;

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
    _startCosmicAwakening();
  }

  void _initializeAnimations() {
    _cosmicGlowController = AnimationController(
      duration: const Duration(seconds: 4),
      vsync: this,
    )..repeat(reverse: true);

    _particleController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    );

    _transitionController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );

    _planetBirthController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );

    _textAnimationController = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );
  }

  @override
  void dispose() {
    _cosmicGlowController.dispose();
    _particleController.dispose();
    _transitionController.dispose();
    _planetBirthController.dispose();
    _textAnimationController.dispose();
    super.dispose();
  }

  /// Start the cosmic awakening animation
  void _startCosmicAwakening() {
    Future.delayed(const Duration(seconds: 1), () {
      _particleController.forward();
      HapticService.triggerEvolutionFeedback();
    });
  }

  /// Proceed to next onboarding step
  Future<void> _nextStep() async {
    if (_isProcessing) return;

    setState(() {
      _isProcessing = true;
    });

    // Trigger transition animation
    await _transitionController.forward();

    switch (_currentStep) {
      case OnboardingStep.cosmicAwakening:
        await _proceedToCosmicSeedSelection();
        break;
      case OnboardingStep.cosmicSeedSelection:
        await _proceedToWebAuthLogin();
        break;
      case OnboardingStep.webAuthLogin:
        await _proceedToMockTradeTutorial();
        break;
      case OnboardingStep.mockTradeTutorial:
        await _proceedToFirstNFTReward();
        break;
      case OnboardingStep.firstNFTReward:
        await _proceedToPlanetCustomization();
        break;
      case OnboardingStep.planetCustomization:
        await _proceedToQuantumCoreIntroduction();
        break;
      case OnboardingStep.quantumCoreIntroduction:
        await _completeOnboarding();
        break;
    }

    _transitionController.reset();
    setState(() {
      _isProcessing = false;
    });
  }

  /// Proceed to cosmic seed selection
  Future<void> _proceedToCosmicSeedSelection() async {
    setState(() {
      _currentStep = OnboardingStep.cosmicSeedSelection;
    });

    await _textAnimationController.forward();
  }

  /// Proceed to Web3Auth login
  Future<void> _proceedToWebAuthLogin() async {
    setState(() {
      _currentStep = OnboardingStep.webAuthLogin;
    });

    await _textAnimationController.forward();
  }

  /// Proceed to mock trade tutorial
  Future<void> _proceedToMockTradeTutorial() async {
    setState(() {
      _currentStep = OnboardingStep.mockTradeTutorial;
    });

    await _textAnimationController.forward();
  }

  /// Proceed to first NFT reward
  Future<void> _proceedToFirstNFTReward() async {
    setState(() {
      _currentStep = OnboardingStep.firstNFTReward;
    });

    await _textAnimationController.forward();

    // Trigger NFT mint animation
    await _planetBirthController.forward();
  }

  /// Proceed to planet customization
  Future<void> _proceedToPlanetCustomization() async {
    setState(() {
      _currentStep = OnboardingStep.planetCustomization;
    });

    await _textAnimationController.forward();
  }

  /// Proceed to quantum core introduction
  Future<void> _proceedToQuantumCoreIntroduction() async {
    setState(() {
      _currentStep = OnboardingStep.quantumCoreIntroduction;
    });

    await _textAnimationController.forward();
  }

  /// Complete onboarding and navigate to main app
  Future<void> _completeOnboarding() async {
    // Initialize user with selected cosmic seed
    await _initializeUserWithCosmicSeed();

    // Navigate to main hub
    if (mounted) {
      Navigator.of(context).pushReplacementNamed('/main_hub');
    }
  }

  /// Initialize user with selected cosmic seed
  Future<void> _initializeUserWithCosmicSeed() async {
    final user = ref.read(authProvider).value;
    if (user != null) {
      // Initialize XP system with cosmic seed bonus
      // await ref.read(playerXPProvider.notifier).initializePlayer(
      //   user.id,
      //   cosmicSeed: _selectedCosmicSeed,
      // );

      // Grant initial rewards
      // await ref.read(playerXPProvider.notifier).grantWelcomeRewards(user.id);
    }
  }

  /// Handle Web3Auth login
  Future<void> _handleWeb3AuthLogin() async {
    try {
      setState(() {
        _isProcessing = true;
      });

      final authService = AuthService();
      final user = await authService.signInWithWeb3Auth();

      if (user != null) {
        // Trigger success animation
        await HapticService.triggerTradeSuccessFeedback();
        await Future.delayed(const Duration(seconds: 1));
        await _nextStep();
      }
    } catch (e) {
      // Handle login error
      HapticService.triggerErrorFeedback();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Cosmic connection failed: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() {
        _isProcessing = false;
      });
    }
  }

  /// Execute mock trade tutorial
  Future<void> _executeMockTrade() async {
    try {
      setState(() {
        _isProcessing = true;
      });

      // Simulate trade execution
      await Future.delayed(const Duration(seconds: 2));

      // Trigger success effects
      await HapticService.triggerTradeSuccessFeedback();
      await _particleController.forward();

      // Grant tutorial rewards
      final user = ref.read(authProvider).value;
      if (user != null) {
        // await ref.read(playerXPProvider.notifier).grantTutorialRewards(user.id);
      }

      await Future.delayed(const Duration(seconds: 1));
      await _nextStep();
    } catch (e) {
      HapticService.triggerErrorFeedback();
    } finally {
      setState(() {
        _isProcessing = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        children: [
          // Background cosmic effects
          _buildCosmicBackground(),

          // Main content
          SafeArea(child: _buildStepContent()),

          // Particle effects overlay
          // CosmicParticles(
          //   animationController: _particleController,
          //   isActive: _currentStep == OnboardingStep.cosmicAwakening ||
          //             _currentStep == OnboardingStep.firstNFTReward,
          // ),

          // Loading overlay
          if (_isProcessing) _buildLoadingOverlay(),
        ],
      ),
    );
  }

  /// Build cosmic background with animated effects
  Widget _buildCosmicBackground() {
    return AnimatedBuilder(
      animation: _cosmicGlowController,
      builder: (context, child) {
        return Container(
          decoration: BoxDecoration(
            gradient: RadialGradient(
              center: Alignment.center,
              colors: [
                Colors.purple.withOpacity(
                  0.1 + _cosmicGlowController.value * 0.2,
                ),
                Colors.blue.withOpacity(
                  0.05 + _cosmicGlowController.value * 0.1,
                ),
                Colors.black,
              ],
              stops: const [0.0, 0.5, 1.0],
            ),
          ),
          child: Stack(
            children: [
              // Floating cosmic particles
              ...List.generate(20, (index) {
                final angle =
                    (index * 2 * math.pi / 20) +
                    (_cosmicGlowController.value * 2 * math.pi);
                final radius = 100 + (index * 20);
                final x =
                    MediaQuery.of(context).size.width / 2 +
                    math.cos(angle) * radius;
                final y =
                    MediaQuery.of(context).size.height / 2 +
                    math.sin(angle) * radius;

                return Positioned(
                  left: x,
                  top: y,
                  child: Container(
                    width: 4,
                    height: 4,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: Colors.white.withOpacity(
                        0.3 + _cosmicGlowController.value * 0.4,
                      ),
                    ),
                  ),
                );
              }),
            ],
          ),
        );
      },
    );
  }

  /// Build step-specific content
  Widget _buildStepContent() {
    switch (_currentStep) {
      case OnboardingStep.cosmicAwakening:
        return _buildCosmicAwakeningStep();
      case OnboardingStep.cosmicSeedSelection:
        return _buildCosmicSeedSelectionStep();
      case OnboardingStep.webAuthLogin:
        return _buildWebAuthLoginStep();
      case OnboardingStep.mockTradeTutorial:
        return _buildMockTradeTutorialStep();
      case OnboardingStep.firstNFTReward:
        return _buildFirstNFTRewardStep();
      case OnboardingStep.planetCustomization:
        return _buildPlanetCustomizationStep();
      case OnboardingStep.quantumCoreIntroduction:
        return _buildQuantumCoreIntroductionStep();
    }
  }

  /// Build cosmic awakening step
  Widget _buildCosmicAwakeningStep() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // Cosmic awakening animation
        Lottie.asset(
              'assets/animations/cosmic_awakening.json',
              width: 300,
              height: 300,
              repeat: true,
            )
            .animate()
            .fadeIn(duration: 1000.ms)
            .scale(
              begin: const Offset(0.5, 0.5),
              end: const Offset(1.0, 1.0),
              duration: 1000.ms,
            ),

        const SizedBox(height: 40),

        // Welcome text
        Text(
              'The First Glimmer',
              style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
              textAlign: TextAlign.center,
            )
            .animate()
            .fadeIn(delay: 1500.ms)
            .slideY(begin: 0.5, end: 0, duration: 800.ms),

        const SizedBox(height: 20),

        Text(
              'In the vast cosmic expanse, a new consciousness awakens...\n\nYour journey through the Stellar Realm begins now.',
              style: Theme.of(
                context,
              ).textTheme.bodyLarge?.copyWith(color: Colors.white70),
              textAlign: TextAlign.center,
            )
            .animate()
            .fadeIn(delay: 2000.ms)
            .slideY(begin: 0.5, end: 0, duration: 800.ms),

        const SizedBox(height: 60),

        // Continue button
        _buildCosmicButton(
          text: 'Begin Your Cosmic Journey',
          onPressed: _nextStep,
          delay: 2500.ms,
        ),
      ],
    );
  }

  /// Build cosmic seed selection step
  Widget _buildCosmicSeedSelectionStep() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text(
          'Choose Your Cosmic Seed',
          style: Theme.of(context).textTheme.headlineLarge?.copyWith(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
          textAlign: TextAlign.center,
        ).animate().fadeIn().slideY(begin: 0.5, end: 0, duration: 800.ms),

        const SizedBox(height: 20),

        Text(
          'Select the cosmic essence that resonates with your soul.\nThis will determine your planet\'s initial biome.',
          style: Theme.of(
            context,
          ).textTheme.bodyLarge?.copyWith(color: Colors.white70),
          textAlign: TextAlign.center,
        ).animate().fadeIn(delay: 300.ms),

        const SizedBox(height: 40),

        // Cosmic seed selection
        // Row(
        //   mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        //   children: [
        //     _buildCosmicSeedOption(PlanetBiome.verdant),
        //     _buildCosmicSeedOption(PlanetBiome.volcanic),
        //     _buildCosmicSeedOption(PlanetBiome.crystalline),
        //   ],
        // ).animate().fadeIn(delay: 500.ms).scale(
        //   begin: const Offset(0.8, 0.8),
        //   end: const Offset(1.0, 1.0),
        //   duration: 600.ms,
        // ),
        const SizedBox(height: 60),

        _buildCosmicButton(
          text: 'Embrace Your Cosmic Seed',
          onPressed: _nextStep,
          delay: 800.ms,
        ),
      ],
    );
  }

  /// Build cosmic seed option
  // Widget _buildCosmicSeedOption(PlanetBiome biome) {
  //   final isSelected = _selectedCosmicSeed == biome;

  //   return GestureDetector(
  //     onTap: () {
  //       setState(() {
  //         _selectedCosmicSeed = biome;
  //       });
  //       HapticService.triggerTapFeedback();
  //     },
  //     child: Container(
  //       width: 80,
  //       height: 80,
  //       decoration: BoxDecoration(
  //         shape: BoxShape.circle,
  //         gradient: RadialGradient(
  //           colors: [
  //             _getBiomeColor(biome).withOpacity(0.8),
  //             _getBiomeColor(biome).withOpacity(0.3),
  //           ],
  //         ),
  //         border: Border.all(
  //           color: isSelected ? Colors.white : Colors.transparent,
  //           width: 3,
  //         ),
  //         boxShadow: [
  //           BoxShadow(
  //             color: _getBiomeColor(biome).withOpacity(0.5),
  //             blurRadius: isSelected ? 20 : 10,
  //             spreadRadius: isSelected ? 5 : 2,
  //           ),
  //         ],
  //       ),
  //       child: Column(
  //         mainAxisAlignment: MainAxisAlignment.center,
  //         children: [
  //           Icon(
  //             _getBiomeIcon(biome),
  //             color: Colors.white,
  //             size: isSelected ? 30 : 25,
  //           ),
  //           const SizedBox(height: 4),
  //           Text(
  //             biome.displayName.split(' ').first,
  //             style: TextStyle(
  //               color: Colors.white,
  //               fontSize: isSelected ? 10 : 8,
  //               fontWeight: FontWeight.bold,
  //             ),
  //           ),
  //         ],
  //       ),
  //     ),
  //   );
  // }

  /// Build Web3Auth login step
  Widget _buildWebAuthLoginStep() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(
          Icons.security,
          color: Colors.cyan,
          size: 100,
        ).animate().fadeIn().rotate(begin: 0, end: 1, duration: 2000.ms),

        const SizedBox(height: 40),

        Text(
          'Secure Cosmic Connection',
          style: Theme.of(context).textTheme.headlineLarge?.copyWith(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
          textAlign: TextAlign.center,
        ).animate().fadeIn(delay: 500.ms),

        const SizedBox(height: 20),

        Text(
          'Connect your digital identity to the cosmic realm.\nYour journey will be secured across the multiverse.',
          style: Theme.of(
            context,
          ).textTheme.bodyLarge?.copyWith(color: Colors.white70),
          textAlign: TextAlign.center,
        ).animate().fadeIn(delay: 700.ms),

        const SizedBox(height: 60),

        _buildCosmicButton(
          text: 'Connect with Web3Auth',
          onPressed: _handleWeb3AuthLogin,
          delay: 1000.ms,
        ),
      ],
    );
  }

  /// Build mock trade tutorial step
  Widget _buildMockTradeTutorialStep() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // Mock trading interface
        Container(
          width: 300,
          height: 200,
          decoration: BoxDecoration(
            color: Colors.grey.shade900,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: Colors.cyan.withOpacity(0.5)),
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                'Practice Cosmic Forge',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  color: Colors.cyan,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 20),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _buildMockTradeButton('Orbital Ascent', Colors.green),
                  _buildMockTradeButton('Gravitational Descent', Colors.red),
                ],
              ),
            ],
          ),
        ).animate().fadeIn().scale(
          begin: const Offset(0.8, 0.8),
          end: const Offset(1.0, 1.0),
          duration: 800.ms,
        ),

        const SizedBox(height: 40),

        Text(
          'Your First Cosmic Trade',
          style: Theme.of(context).textTheme.headlineLarge?.copyWith(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
          textAlign: TextAlign.center,
        ).animate().fadeIn(delay: 300.ms),

        const SizedBox(height: 20),

        Text(
          'Practice with cosmic energy flows.\nNo real risk, only cosmic rewards await.',
          style: Theme.of(
            context,
          ).textTheme.bodyLarge?.copyWith(color: Colors.white70),
          textAlign: TextAlign.center,
        ).animate().fadeIn(delay: 500.ms),

        const SizedBox(height: 60),

        _buildCosmicButton(
          text: 'Execute Mock Trade',
          onPressed: _executeMockTrade,
          delay: 700.ms,
        ),
      ],
    );
  }

  /// Build mock trade button
  Widget _buildMockTradeButton(String text, Color color) {
    return ElevatedButton(
      onPressed: () {
        HapticService.triggerTapFeedback();
        // Visual feedback only, actual trade happens on main button
      },
      style: ElevatedButton.styleFrom(
        backgroundColor: color.withOpacity(0.2),
        foregroundColor: color,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
      child: Text(text, style: const TextStyle(fontSize: 12)),
    );
  }

  /// Build first NFT reward step
  Widget _buildFirstNFTRewardStep() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // NFT animation
        AnimatedBuilder(
          animation: _planetBirthController,
          builder: (context, child) {
            return Transform.scale(
              scale: 0.5 + _planetBirthController.value * 0.5,
              child: Container(
                width: 200,
                height: 200,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: RadialGradient(
                    colors: [
                      Colors.purple.withOpacity(0.8),
                      Colors.blue.withOpacity(0.4),
                      Colors.transparent,
                    ],
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.purple.withOpacity(0.5),
                      blurRadius: 30,
                      spreadRadius: 10,
                    ),
                  ],
                ),
                child: const Icon(
                  Icons.auto_awesome,
                  color: Colors.white,
                  size: 80,
                ),
              ),
            );
          },
        ),

        const SizedBox(height: 40),

        Text(
          'Genesis NFT Acquired!',
          style: Theme.of(context).textTheme.headlineLarge?.copyWith(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
          textAlign: TextAlign.center,
        ).animate().fadeIn(delay: 500.ms),

        const SizedBox(height: 20),

        Text(
          'You have been granted the "First Glimmer" NFT.\nThis marks your entry into the cosmic realm.',
          style: Theme.of(
            context,
          ).textTheme.bodyLarge?.copyWith(color: Colors.white70),
          textAlign: TextAlign.center,
        ).animate().fadeIn(delay: 700.ms),

        const SizedBox(height: 60),

        _buildCosmicButton(
          text: 'Claim Your Genesis NFT',
          onPressed: _nextStep,
          delay: 1000.ms,
        ),
      ],
    );
  }

  /// Build planet customization step
  Widget _buildPlanetCustomizationStep() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // 3D Planet preview
        // EnhancedCosmicPlanet3D(
        //   size: 200,
        //   enableTapping: true,
        //   enableBiomeEvolution: false,
        //   onPlanetTap: () {
        //     HapticService.triggerTapFeedback();
        //   },
        // ).animate().fadeIn().scale(
        //   begin: const Offset(0.5, 0.5),
        //   end: const Offset(1.0, 1.0),
        //   duration: 1000.ms,
        // ),
        const SizedBox(height: 40),

        Text(
          'Your Cosmic Planet',
          style: Theme.of(context).textTheme.headlineLarge?.copyWith(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
          textAlign: TextAlign.center,
        ).animate().fadeIn(delay: 500.ms),

        const SizedBox(height: 20),

        // Text(
        //   'Behold your cosmic realm, born from the ${_selectedCosmicSeed.displayName} seed.\nTap to generate your first Stellar Shards.',
        //   style: Theme.of(context).textTheme.bodyLarge?.copyWith(
        //     color: Colors.white70,
        //   ),
        //   textAlign: TextAlign.center,
        // ).animate().fadeIn(delay: 700.ms),
        const SizedBox(height: 60),

        _buildCosmicButton(
          text: 'Enter the Quantum Core',
          onPressed: _nextStep,
          delay: 1000.ms,
        ),
      ],
    );
  }

  /// Build quantum core introduction step
  Widget _buildQuantumCoreIntroductionStep() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // Quantum core animation
        Lottie.asset(
          'assets/animations/quantum_core.json',
          width: 300,
          height: 300,
          repeat: true,
        ).animate().fadeIn().rotate(begin: 0, end: 1, duration: 3000.ms),

        const SizedBox(height: 40),

        Text(
          'The Quantum Core',
          style: Theme.of(context).textTheme.headlineLarge?.copyWith(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
          textAlign: TextAlign.center,
        ).animate().fadeIn(delay: 500.ms),

        const SizedBox(height: 20),

        Text(
          'Your cosmic journey headquarters.\nHere you can:\n\n• Tap your planet for Stellar Shards\n• Upgrade your Astro-Forgers\n• Track your cosmic progress\n• Access the Cosmic Forge for real trading',
          style: Theme.of(
            context,
          ).textTheme.bodyLarge?.copyWith(color: Colors.white70),
          textAlign: TextAlign.center,
        ).animate().fadeIn(delay: 700.ms),

        const SizedBox(height: 60),

        _buildCosmicButton(
          text: 'Begin Your Cosmic Adventure',
          onPressed: _nextStep,
          delay: 1000.ms,
        ),
      ],
    );
  }

  /// Build cosmic button
  Widget _buildCosmicButton({
    required String text,
    required VoidCallback onPressed,
    required Duration delay,
  }) {
    return Container(
          width: 300,
          height: 60,
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Colors.purple, Colors.blue],
            ),
            borderRadius: BorderRadius.circular(30),
            boxShadow: [
              BoxShadow(
                color: Colors.purple.withOpacity(0.5),
                blurRadius: 20,
                spreadRadius: 2,
              ),
            ],
          ),
          child: ElevatedButton(
            onPressed: onPressed,
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.transparent,
              shadowColor: Colors.transparent,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(30),
              ),
            ),
            child: Text(
              text,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        )
        .animate()
        .fadeIn(delay: delay)
        .slideY(begin: 0.5, end: 0, duration: 600.ms);
  }

  /// Build loading overlay
  Widget _buildLoadingOverlay() {
    return Container(
      color: Colors.black.withOpacity(0.7),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Lottie.asset(
              'assets/animations/cosmic_loading.json',
              width: 100,
              height: 100,
              repeat: true,
            ),
            const SizedBox(height: 20),
            Text(
              'Channeling cosmic energy...',
              style: Theme.of(
                context,
              ).textTheme.bodyLarge?.copyWith(color: Colors.white),
            ),
          ],
        ),
      ),
    );
  }

  // Helper methods

  // Color _getBiomeColor(PlanetBiome biome) {
  //   switch (biome) {
  //     case PlanetBiome.verdant:
  //       return Colors.green;
  //     case PlanetBiome.volcanic:
  //       return Colors.red;
  //     case PlanetBiome.crystalline:
  //       return Colors.blue;
  //     default:
  //       return Colors.grey;
  //   }
  // }

  // IconData _getBiomeIcon(PlanetBiome biome) {
  //   switch (biome) {
  //     case PlanetBiome.verdant:
  //       return Icons.eco;
  //     case PlanetBiome.volcanic:
  //       return Icons.whatshot;
  //     case PlanetBiome.crystalline:
  //       return Icons.diamond;
  //     default:
  //       return Icons.landscape;
  //   }
  // }
}

/// Onboarding step enumeration
enum OnboardingStep {
  cosmicAwakening,
  cosmicSeedSelection,
  webAuthLogin,
  mockTradeTutorial,
  firstNFTReward,
  planetCustomization,
  quantumCoreIntroduction,
}
