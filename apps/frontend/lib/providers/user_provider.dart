import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/user.dart';

class UserNotifier extends StateNotifier<User?> {
  UserNotifier() : super(null);

  void setUser(User user) {
    state = user;
  }

  void clearUser() {
    state = null;
  }

  void updateStellarShards(int amount) {
    if (state != null) {
      state = state!.copyWith(stellarShards: state!.stellarShards + amount);
    }
  }

  void updateLumina(int amount) {
    if (state != null) {
      state = state!.copyWith(lumina: state!.lumina + amount);
    }
  }

  void updateXP(int amount) {
    if (state != null) {
      state = state!.copyWith(xp: state!.xp + amount);
    }
  }
}

final userProvider = StateNotifierProvider<UserNotifier, User?>((ref) {
  return UserNotifier();
});
