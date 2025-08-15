class User {
  final String id;
  final String username;
  final String email;
  final String privateKey;
  final String starknetAddress;
  final String? profilePicture;
  final int stellarShards;
  final int lumina;
  final int xp;
  final DateTime createdAt;
  final DateTime lastLoginAt;
  final String?
  extendedExchangeApiKey; // User's personal Extended Exchange API key

  User({
    required this.id,
    required this.username,
    required this.email,
    required this.privateKey,
    required this.starknetAddress,
    this.profilePicture,
    this.stellarShards = 0,
    this.lumina = 0,
    this.xp = 0,
    required this.createdAt,
    required this.lastLoginAt,
    this.extendedExchangeApiKey,
  });

  User copyWith({
    String? id,
    String? username,
    String? email,
    String? privateKey,
    String? starknetAddress,
    String? profilePicture,
    int? stellarShards,
    int? lumina,
    int? xp,
    DateTime? createdAt,
    DateTime? lastLoginAt,
    String? extendedExchangeApiKey,
  }) {
    return User(
      id: id ?? this.id,
      username: username ?? this.username,
      email: email ?? this.email,
      privateKey: privateKey ?? this.privateKey,
      starknetAddress: starknetAddress ?? this.starknetAddress,
      profilePicture: profilePicture ?? this.profilePicture,
      stellarShards: stellarShards ?? this.stellarShards,
      lumina: lumina ?? this.lumina,
      xp: xp ?? this.xp,
      createdAt: createdAt ?? this.createdAt,
      lastLoginAt: lastLoginAt ?? this.lastLoginAt,
      extendedExchangeApiKey:
          extendedExchangeApiKey ?? this.extendedExchangeApiKey,
    );
  }

  /// Check if user is ready for real trading (has API key)
  bool get isReadyForTrading =>
      extendedExchangeApiKey != null && extendedExchangeApiKey!.isNotEmpty;

  /// Check if user needs API key generation for trading
  bool get needsApiKeyForTrading => !isReadyForTrading;

  /// Update user with new API key (typically after first trading setup)
  User withApiKey(String apiKey) {
    return copyWith(extendedExchangeApiKey: apiKey);
  }

  @override
  String toString() {
    // Safe toString that doesn't expose sensitive data
    return 'User(id: $id, email: $email, username: $username, '
        'address: ${starknetAddress.substring(0, 8)}...${starknetAddress.substring(starknetAddress.length - 6)}, '
        'hasApiKey: ${extendedExchangeApiKey != null}, '
        'stellarShards: $stellarShards, lumina: $lumina, xp: $xp)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is User &&
        other.id == id &&
        other.username == username &&
        other.email == email &&
        other.privateKey == privateKey &&
        other.starknetAddress == starknetAddress &&
        other.profilePicture == profilePicture &&
        other.stellarShards == stellarShards &&
        other.lumina == lumina &&
        other.xp == xp &&
        other.createdAt == createdAt &&
        other.lastLoginAt == lastLoginAt &&
        other.extendedExchangeApiKey == extendedExchangeApiKey;
  }

  @override
  int get hashCode {
    return Object.hash(
      id,
      username,
      email,
      privateKey,
      starknetAddress,
      profilePicture,
      stellarShards,
      lumina,
      xp,
      createdAt,
      lastLoginAt,
      extendedExchangeApiKey,
    );
  }

  /// Convert User to JSON for secure storage
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'email': email,
      'privateKey': privateKey,
      'starknetAddress': starknetAddress,
      'profilePicture': profilePicture,
      'stellarShards': stellarShards,
      'lumina': lumina,
      'xp': xp,
      'createdAt': createdAt.millisecondsSinceEpoch,
      'lastLoginAt': lastLoginAt.millisecondsSinceEpoch,
      'extendedExchangeApiKey': extendedExchangeApiKey,
    };
  }

  /// Create User from JSON stored data
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as String,
      username: json['username'] as String,
      email: json['email'] as String,
      privateKey: json['privateKey'] as String,
      starknetAddress: json['starknetAddress'] as String,
      profilePicture: json['profilePicture'] as String?,
      stellarShards: json['stellarShards'] as int? ?? 0,
      lumina: json['lumina'] as int? ?? 0,
      xp: json['xp'] as int? ?? 0,
      createdAt: DateTime.fromMillisecondsSinceEpoch(json['createdAt'] as int),
      lastLoginAt: DateTime.fromMillisecondsSinceEpoch(
        json['lastLoginAt'] as int,
      ),
      extendedExchangeApiKey: json['extendedExchangeApiKey'] as String?,
    );
  }
}
