import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../utils/constants.dart';

/// Cosmic Theme System for AstraTrade
/// Transforms the entire app with cosmic aesthetic while preserving functionality
class CosmicTheme {
  // Cosmic Color Palette from Constants
  static const Color primaryPurple = Color(
    AppConstants.primaryColorValue,
  ); // 0xFF7B2CBF
  static const Color accentBlue = Color(
    AppConstants.secondaryColorValue,
  ); // 0xFF3B82F6
  static const Color accentCyan = Color(
    AppConstants.accentColorValue,
  ); // 0xFF06B6D4
  static const Color cosmicBackground = Color(
    AppConstants.backgroundColorValue,
  ); // 0xFF0A0A0A

  // Extended Cosmic Palette
  static const Color deepPurple = Color(0xFF5B21B6);
  static const Color cosmicGold = Color(0xFFFBBF24);
  static const Color nebulaViolet = Color(0xFF8B5CF6);
  static const Color starWhite = Color(0xFFF8FAFC);
  static const Color cosmicGray = Color(0xFF1F2937);
  static const Color cosmicDarkGray = Color(0xFF111827);

  // Gradient Definitions
  static const LinearGradient cosmicGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [primaryPurple, deepPurple, accentBlue],
  );

  static const LinearGradient nebulaGradient = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [nebulaViolet, primaryPurple, cosmicBackground],
  );

  static const LinearGradient goldGradient = LinearGradient(
    colors: [cosmicGold, Color(0xFFEAB308), Color(0xFFF59E0B)],
  );

  /// Main Cosmic Theme
  static ThemeData get theme {
    return ThemeData(
      // Core Material 3 theming
      useMaterial3: true,
      brightness: Brightness.dark,

      // Primary color scheme
      primarySwatch: _createMaterialColor(primaryPurple),
      primaryColor: primaryPurple,

      // Color Scheme for Material 3
      colorScheme: const ColorScheme.dark(
        primary: primaryPurple,
        secondary: accentCyan,
        tertiary: cosmicGold,
        surface: cosmicDarkGray,
        background: cosmicBackground,
        onPrimary: starWhite,
        onSecondary: cosmicBackground,
        onSurface: starWhite,
        onBackground: starWhite,
        error: Color(0xFFEF4444),
        onError: starWhite,
      ),

      // Scaffold background
      scaffoldBackgroundColor: cosmicBackground,

      // App Bar Theme
      appBarTheme: AppBarTheme(
        backgroundColor: primaryPurple,
        foregroundColor: starWhite,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: GoogleFonts.orbitron(
          fontSize: 20,
          fontWeight: FontWeight.bold,
          color: starWhite,
        ),
        iconTheme: const IconThemeData(color: starWhite),
      ),

      // Card Theme
      cardTheme: CardThemeData(
        color: cosmicDarkGray,
        elevation: AppConstants.cardElevation,
        shadowColor: primaryPurple.withOpacity(0.3),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppConstants.borderRadius),
          side: BorderSide(color: primaryPurple.withOpacity(0.2), width: 1),
        ),
      ),

      // Button Themes
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryPurple,
          foregroundColor: starWhite,
          elevation: 8,
          shadowColor: primaryPurple.withOpacity(0.5),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(
              AppConstants.defaultBorderRadius,
            ),
          ),
          padding: const EdgeInsets.symmetric(
            horizontal: AppConstants.paddingLarge,
            vertical: AppConstants.paddingMedium,
          ),
          textStyle: GoogleFonts.orbitron(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),

      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: primaryPurple,
          side: const BorderSide(color: primaryPurple, width: 2),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(
              AppConstants.defaultBorderRadius,
            ),
          ),
          padding: const EdgeInsets.symmetric(
            horizontal: AppConstants.paddingLarge,
            vertical: AppConstants.paddingMedium,
          ),
          textStyle: GoogleFonts.orbitron(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),

      // Text Button Theme
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: accentCyan,
          textStyle: GoogleFonts.rajdhani(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),

      // Input Decoration Theme
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: cosmicGray,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppConstants.defaultBorderRadius),
          borderSide: BorderSide(color: primaryPurple.withOpacity(0.3)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppConstants.defaultBorderRadius),
          borderSide: BorderSide(color: primaryPurple.withOpacity(0.3)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppConstants.defaultBorderRadius),
          borderSide: const BorderSide(color: primaryPurple, width: 2),
        ),
        labelStyle: GoogleFonts.rajdhani(
          color: starWhite.withOpacity(0.8),
          fontSize: 16,
        ),
        hintStyle: GoogleFonts.rajdhani(
          color: starWhite.withOpacity(0.6),
          fontSize: 14,
        ),
      ),

      // Chip Theme
      chipTheme: ChipThemeData(
        backgroundColor: cosmicGray,
        selectedColor: primaryPurple,
        labelStyle: GoogleFonts.rajdhani(
          color: starWhite,
          fontWeight: FontWeight.w500,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppConstants.defaultBorderRadius),
        ),
      ),

      // Typography - Cosmic Font System
      textTheme: TextTheme(
        displayLarge: GoogleFonts.orbitron(
          fontSize: 32,
          fontWeight: FontWeight.bold,
          color: starWhite,
        ),
        displayMedium: GoogleFonts.orbitron(
          fontSize: 28,
          fontWeight: FontWeight.bold,
          color: starWhite,
        ),
        displaySmall: GoogleFonts.orbitron(
          fontSize: 24,
          fontWeight: FontWeight.w600,
          color: starWhite,
        ),
        headlineLarge: GoogleFonts.orbitron(
          fontSize: 22,
          fontWeight: FontWeight.w600,
          color: starWhite,
        ),
        headlineMedium: GoogleFonts.orbitron(
          fontSize: 20,
          fontWeight: FontWeight.w500,
          color: starWhite,
        ),
        headlineSmall: GoogleFonts.orbitron(
          fontSize: 18,
          fontWeight: FontWeight.w500,
          color: starWhite,
        ),
        titleLarge: GoogleFonts.rajdhani(
          fontSize: 18,
          fontWeight: FontWeight.w600,
          color: starWhite,
        ),
        titleMedium: GoogleFonts.rajdhani(
          fontSize: 16,
          fontWeight: FontWeight.w600,
          color: starWhite,
        ),
        titleSmall: GoogleFonts.rajdhani(
          fontSize: 14,
          fontWeight: FontWeight.w600,
          color: starWhite,
        ),
        bodyLarge: GoogleFonts.rajdhani(
          fontSize: 16,
          fontWeight: FontWeight.normal,
          color: starWhite,
        ),
        bodyMedium: GoogleFonts.rajdhani(
          fontSize: 14,
          fontWeight: FontWeight.normal,
          color: starWhite,
        ),
        bodySmall: GoogleFonts.rajdhani(
          fontSize: 12,
          fontWeight: FontWeight.normal,
          color: starWhite.withOpacity(0.8),
        ),
        labelLarge: GoogleFonts.rajdhani(
          fontSize: 14,
          fontWeight: FontWeight.w500,
          color: starWhite,
        ),
        labelMedium: GoogleFonts.rajdhani(
          fontSize: 12,
          fontWeight: FontWeight.w500,
          color: starWhite,
        ),
        labelSmall: GoogleFonts.rajdhani(
          fontSize: 10,
          fontWeight: FontWeight.w500,
          color: starWhite.withOpacity(0.8),
        ),
      ),

      // Icon Theme
      iconTheme: const IconThemeData(
        color: starWhite,
        size: AppConstants.iconSize,
      ),

      // Divider Theme
      dividerTheme: DividerThemeData(
        color: primaryPurple.withOpacity(0.3),
        thickness: 1,
      ),

      // Progress Indicator Theme
      progressIndicatorTheme: const ProgressIndicatorThemeData(
        color: accentCyan,
      ),

      // Dialog Theme
      dialogTheme: DialogThemeData(
        backgroundColor: cosmicDarkGray,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppConstants.borderRadius),
        ),
        titleTextStyle: GoogleFonts.orbitron(
          fontSize: 20,
          fontWeight: FontWeight.bold,
          color: starWhite,
        ),
        contentTextStyle: GoogleFonts.rajdhani(fontSize: 16, color: starWhite),
      ),

      // Snackbar Theme
      snackBarTheme: SnackBarThemeData(
        backgroundColor: cosmicDarkGray,
        contentTextStyle: GoogleFonts.rajdhani(color: starWhite, fontSize: 14),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppConstants.defaultBorderRadius),
        ),
      ),
    );
  }

  /// Create MaterialColor from Color for primarySwatch
  static MaterialColor _createMaterialColor(Color color) {
    List strengths = <double>[.05];
    final swatch = <int, Color>{};
    final int r = color.red, g = color.green, b = color.blue;

    for (int i = 1; i < 10; i++) {
      strengths.add(0.1 * i);
    }
    for (var strength in strengths) {
      final double ds = 0.5 - strength;
      swatch[(strength * 1000).round()] = Color.fromRGBO(
        r + ((ds < 0 ? r : (255 - r)) * ds).round(),
        g + ((ds < 0 ? g : (255 - g)) * ds).round(),
        b + ((ds < 0 ? b : (255 - b)) * ds).round(),
        1,
      );
    }
    return MaterialColor(color.value, swatch);
  }
}

/// Cosmic-specific widget styles for advanced components
class CosmicStyles {
  /// Cosmic Container with gradient background
  static BoxDecoration get cosmicContainer => BoxDecoration(
    gradient: CosmicTheme.cosmicGradient,
    borderRadius: BorderRadius.circular(AppConstants.borderRadius),
    boxShadow: [
      BoxShadow(
        color: CosmicTheme.primaryPurple.withOpacity(0.3),
        blurRadius: 10,
        offset: const Offset(0, 4),
      ),
    ],
  );

  /// Nebula background for special containers
  static BoxDecoration get nebulaContainer => BoxDecoration(
    gradient: CosmicTheme.nebulaGradient,
    borderRadius: BorderRadius.circular(AppConstants.borderRadius),
    border: Border.all(
      color: CosmicTheme.primaryPurple.withOpacity(0.5),
      width: 1,
    ),
  );

  /// Gold accent container for premium elements
  static BoxDecoration get goldContainer => BoxDecoration(
    gradient: CosmicTheme.goldGradient,
    borderRadius: BorderRadius.circular(AppConstants.borderRadius),
    boxShadow: [
      BoxShadow(
        color: CosmicTheme.cosmicGold.withOpacity(0.3),
        blurRadius: 8,
        offset: const Offset(0, 2),
      ),
    ],
  );
}

/// Cosmic Animation Durations
class CosmicAnimations {
  static const Duration fast = Duration(milliseconds: 200);
  static const Duration normal = Duration(
    milliseconds: AppConstants.defaultAnimationMs,
  );
  static const Duration slow = Duration(milliseconds: 500);
  static const Duration pulse = Duration(
    milliseconds: AppConstants.buttonPulseMs,
  );
}
