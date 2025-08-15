import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:developer';

import '../models/user.dart';
import '../services/auth_service.dart';
import '../config/starknet_config.dart';

// Re-enabled: Starknet service integration
final authServiceProvider = Provider(
  (ref) => AuthService(ref.watch(dynamicStarknetServiceProvider)),
);

class AuthNotifier extends StateNotifier<AsyncValue<User?>> {
  final AuthService _authService;

  AuthNotifier(this._authService) : super(const AsyncValue.data(null)) {
    // Re-enabled: Check existing session on startup
    _checkExistingSession();
  }

  /// Check if user has an existing session on app startup
  Future<void> _checkExistingSession() async {
    try {
      log('🔍 Starting authentication check...');
      state = const AsyncValue.loading();

      final hasWalletData = await _authService.hasStoredWalletData();
      log('📱 Has stored wallet data: $hasWalletData');

      if (hasWalletData) {
        // User has stored wallet data, recreate User object without triggering Web3Auth
        final user = await _authService.restoreUserFromStoredData();
        if (user != null) {
          state = AsyncValue.data(user);
          log('✅ Existing session restored for user: ${user.email}');
        } else {
          state = const AsyncValue.data(null);
          log('❌ Failed to restore user from stored data');
        }
      } else {
        state = const AsyncValue.data(null);
        log('🚪 No existing session found - should show login screen');
      }
    } catch (e) {
      log('💥 Error checking existing session: $e');
      state = const AsyncValue.data(null);
    }
  }

  /// Sign in with Google using Web3Auth
  Future<void> signInWithGoogle() async {
    try {
      state = const AsyncValue.loading();

      final user = await _authService.signInWithGoogle();
      state = AsyncValue.data(user);

      log('User signed in successfully: ${user.email}');
    } catch (e) {
      log('Google sign-in failed: $e');
      state = AsyncValue.error(e, StackTrace.current);
      rethrow;
    }
  }

  /// Sign in with Apple using Web3Auth
  Future<void> signInWithApple() async {
    try {
      state = const AsyncValue.loading();

      final user = await _authService.signInWithApple();
      state = AsyncValue.data(user);

      log('Apple user signed in successfully: ${user.email}');
    } catch (e) {
      log('Apple sign-in failed: $e');
      state = AsyncValue.error(e, StackTrace.current);
      rethrow;
    }
  }

  /// Sign in with Discord using Web3Auth
  Future<void> signInWithDiscord() async {
    try {
      state = const AsyncValue.loading();

      final user = await _authService.signInWithDiscord();
      state = AsyncValue.data(user);

      log('Discord user signed in successfully: ${user.email}');
    } catch (e) {
      log('Discord sign-in failed: $e');
      state = AsyncValue.error(e, StackTrace.current);
      rethrow;
    }
  }

  /// Sign in with Twitter using Web3Auth
  Future<void> signInWithTwitter() async {
    try {
      state = const AsyncValue.loading();

      final user = await _authService.signInWithTwitter();
      state = AsyncValue.data(user);

      log('Twitter user signed in successfully: ${user.email}');
    } catch (e) {
      log('Twitter sign-in failed: $e');
      state = AsyncValue.error(e, StackTrace.current);
      rethrow;
    }
  }

  /// Sign in with GitHub using Web3Auth
  Future<void> signInWithGitHub() async {
    try {
      state = const AsyncValue.loading();

      final user = await _authService.signInWithGitHub();
      state = AsyncValue.data(user);

      log('GitHub user signed in successfully: ${user.email}');
    } catch (e) {
      log('GitHub sign-in failed: $e');
      state = AsyncValue.error(e, StackTrace.current);
      rethrow;
    }
  }

  /// Sign in with Email/Password using Web3Auth
  Future<void> signInWithEmail(String email, String password) async {
    try {
      state = const AsyncValue.loading();

      final user = await _authService.signInWithEmail(email, password);
      state = AsyncValue.data(user);

      log('Email user signed in successfully: ${user.email}');
    } catch (e) {
      log('Email sign-in failed: $e');
      state = AsyncValue.error(e, StackTrace.current);
      rethrow;
    }
  }

  /// Sign out the current user
  Future<void> signOut() async {
    log('🚪 Starting sign out process from auth provider...');

    try {
      await _authService.signOut();
      log('✅ Auth service sign out completed');
    } catch (e) {
      log('⚠️ Auth service sign out failed: $e');
      // Don't throw - continue with state cleanup
    }

    // Always clear the state regardless of auth service result
    try {
      state = const AsyncValue.data(null);
      log('✅ Auth provider state cleared');
    } catch (e) {
      log('⚠️ Failed to clear auth state: $e');
    }

    log('✅ Sign out process completed successfully');
    // Never throw exceptions from signOut
  }

  /// Get the current user (null if not authenticated)
  User? get currentUser {
    return state.value;
  }

  /// Check if user is currently authenticated
  bool get isAuthenticated {
    return state.value != null;
  }

  /// Check if authentication is in progress
  bool get isLoading {
    return state.isLoading;
  }

  /// Get authentication error if any
  Object? get error {
    return state.hasError ? state.error : null;
  }

  /// Refresh user session
  Future<void> refreshSession() async {
    await _checkExistingSession();
  }

  /// Set user directly (used after wallet import)
  void setUser(User user) {
    state = AsyncValue.data(user);
    log('✅ User set directly: ${user.email}');
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, AsyncValue<User?>>((
  ref,
) {
  return AuthNotifier(ref.watch(authServiceProvider));
});

/// Convenience provider to get current user
final currentUserProvider = Provider<User?>((ref) {
  return ref.watch(authProvider).value;
});

/// Convenience provider to check if user is authenticated
final isAuthenticatedProvider = Provider<bool>((ref) {
  return ref.watch(authProvider).value != null;
});
