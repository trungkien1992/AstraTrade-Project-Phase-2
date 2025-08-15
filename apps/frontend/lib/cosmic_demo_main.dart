import 'package:flutter/material.dart';
import 'package:audioplayers/audioplayers.dart';
import 'cosmic_demo_screen.dart';

/// Minimal Cosmic Trading Demo
/// Showcases cosmic enhancements without complex dependencies
void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize audio system
  await AudioPlayer().setVolume(0.6);

  runApp(const CosmicDemoApp());
}

class CosmicDemoApp extends StatelessWidget {
  const CosmicDemoApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AstraTrade - Cosmic Demo',
      theme: ThemeData(
        primarySwatch: Colors.purple,
        scaffoldBackgroundColor: const Color(0xFF0A0A0A),
        textTheme: const TextTheme(
          bodyLarge: TextStyle(color: Colors.white),
          bodyMedium: TextStyle(color: Colors.white),
          titleLarge: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.purple,
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        ),
        cardTheme: CardThemeData(
          color: const Color(0xFF1A1A1A),
          elevation: 8,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: BorderSide(color: Colors.purple.withOpacity(0.3)),
          ),
        ),
      ),
      home: const CosmicDemoScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}
