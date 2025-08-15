import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:lottie/lottie.dart';

class LearnMoreModal extends StatelessWidget {
  const LearnMoreModal({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.85,
      decoration: const BoxDecoration(
        color: Color(0xFF1E1B4B),
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      child: Column(
        children: [
          // Handle bar
          Container(
            width: 40,
            height: 4,
            margin: const EdgeInsets.symmetric(vertical: 12),
            decoration: BoxDecoration(
              color: Colors.white24,
              borderRadius: BorderRadius.circular(2),
            ),
          ),

          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildHeader(),
                  const SizedBox(height: 32),
                  _buildEducationalSections(),
                  const SizedBox(height: 32),
                  _buildClosingSection(context),
                ],
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
          'Welcome to the Cosmos',
          style: GoogleFonts.orbitron(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'Understanding Starknet Wallets in AstraTrade',
          style: GoogleFonts.rajdhani(fontSize: 16, color: Colors.white70),
        ),
      ],
    );
  }

  Widget _buildEducationalSections() {
    return Column(
      children: [
        _buildEducationCard(
          title: 'Self-Custody',
          description: 'You truly own your assets',
          icon: Icons.security,
          color: const Color(0xFF7B2CBF),
          animation: 'assets/animations/lock.json',
          content: [
            'Your wallet is yours alone - no one can freeze or control your funds',
            'Private keys are encrypted and stored only on your device',
            'You have complete sovereignty over your digital assets',
            'No intermediaries, no custodians - pure decentralized finance',
          ],
        ),
        const SizedBox(height: 24),

        _buildEducationCard(
          title: 'Starknet Power',
          description: 'Access fast, low-cost trades',
          icon: Icons.speed,
          color: const Color(0xFF06B6D4),
          animation: 'assets/animations/speed.json',
          content: [
            'Trade with lightning-fast transaction speeds',
            'Ultra-low fees compared to traditional blockchains',
            'Advanced cryptographic security with STARK proofs',
            'Seamless bridging to Ethereum and other networks',
          ],
        ),
        const SizedBox(height: 24),

        _buildEducationCard(
          title: 'Seamless Experience',
          description: 'Your single key to the AstraTrade universe',
          icon: Icons.auto_awesome,
          color: const Color(0xFFFF9800),
          animation: 'assets/animations/universe.json',
          content: [
            'One wallet unlocks the entire cosmic trading experience',
            'Seamless integration with all AstraTrade features',
            'Cross-device synchronization with secure backup',
            'Future-proof: ready for new galaxies and dimensions',
          ],
        ),
      ],
    );
  }

  Widget _buildEducationCard({
    required String title,
    required String description,
    required IconData icon,
    required Color color,
    required String animation,
    required List<String> content,
  }) {
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [color.withOpacity(0.2), color.withOpacity(0.1)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: color.withOpacity(0.2),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(icon, color: color, size: 28),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: GoogleFonts.orbitron(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      Text(
                        description,
                        style: GoogleFonts.rajdhani(
                          fontSize: 14,
                          color: Colors.white70,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ...content
                .map(
                  (item) => Padding(
                    padding: const EdgeInsets.only(bottom: 8.0),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Padding(
                          padding: EdgeInsets.only(top: 4.0),
                          child: Icon(
                            Icons.star,
                            size: 12,
                            color: Colors.white54,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            item,
                            style: GoogleFonts.rajdhani(
                              fontSize: 14,
                              color: Colors.white70,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                )
                .toList(),
          ],
        ),
      ),
    );
  }

  Widget _buildClosingSection(BuildContext context) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.05),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.white.withOpacity(0.1)),
          ),
          child: Column(
            children: [
              Text(
                'Ready to Begin?',
                style: GoogleFonts.orbitron(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                'Your Starknet wallet is your passport to the cosmic trading universe. Choose your path and start your journey today.',
                textAlign: TextAlign.center,
                style: GoogleFonts.rajdhani(
                  fontSize: 16,
                  color: Colors.white70,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 24),
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
              'Got it! Ready to connect',
              style: GoogleFonts.rajdhani(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
      ],
    );
  }
}

// Fallback widget for missing animations
class _PlaceholderAnimation extends StatelessWidget {
  final IconData icon;
  final Color color;

  const _PlaceholderAnimation({required this.icon, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 80,
      height: 80,
      decoration: BoxDecoration(
        color: color.withOpacity(0.2),
        shape: BoxShape.circle,
      ),
      child: Icon(icon, size: 40, color: color),
    );
  }
}
