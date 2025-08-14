import 'dart:convert';

/// Transaction model representing blockchain transactions
class Transaction {
  final String hash;
  final String from;
  final String to;
  final String value; // Amount in ETH/token
  final TransactionType type;
  final TransactionStatus status;
  final DateTime timestamp;
  final int? blockNumber;
  final String? gasUsed;
  final String? gasPrice;
  final String? contractAddress;
  final String? tokenSymbol;
  final Map<String, dynamic>? metadata;

  Transaction({
    required this.hash,
    required this.from,
    required this.to,
    required this.value,
    required this.type,
    required this.status,
    required this.timestamp,
    this.blockNumber,
    this.gasUsed,
    this.gasPrice,
    this.contractAddress,
    this.tokenSymbol,
    this.metadata,
  });

  /// Create a copy of this transaction with updated fields
  Transaction copyWith({
    String? hash,
    String? from,
    String? to,
    String? value,
    TransactionType? type,
    TransactionStatus? status,
    DateTime? timestamp,
    int? blockNumber,
    String? gasUsed,
    String? gasPrice,
    String? contractAddress,
    String? tokenSymbol,
    Map<String, dynamic>? metadata,
  }) {
    return Transaction(
      hash: hash ?? this.hash,
      from: from ?? this.from,
      to: to ?? this.to,
      value: value ?? this.value,
      type: type ?? this.type,
      status: status ?? this.status,
      timestamp: timestamp ?? this.timestamp,
      blockNumber: blockNumber ?? this.blockNumber,
      gasUsed: gasUsed ?? this.gasUsed,
      gasPrice: gasPrice ?? this.gasPrice,
      contractAddress: contractAddress ?? this.contractAddress,
      tokenSymbol: tokenSymbol ?? this.tokenSymbol,
      metadata: metadata ?? this.metadata,
    );
  }

  /// Convert to JSON for storage
  String toJson() {
    return jsonEncode({
      'hash': hash,
      'from': from,
      'to': to,
      'value': value,
      'type': type.name,
      'status': status.name,
      'timestamp': timestamp.millisecondsSinceEpoch,
      'blockNumber': blockNumber,
      'gasUsed': gasUsed,
      'gasPrice': gasPrice,
      'contractAddress': contractAddress,
      'tokenSymbol': tokenSymbol,
      'metadata': metadata,
    });
  }

  /// Create from JSON
  factory Transaction.fromJson(String jsonStr) {
    final json = jsonDecode(jsonStr) as Map<String, dynamic>;
    return Transaction(
      hash: json['hash'] as String,
      from: json['from'] as String,
      to: json['to'] as String,
      value: json['value'] as String,
      type: TransactionType.values.firstWhere(
        (t) => t.name == json['type'],
        orElse: () => TransactionType.transfer,
      ),
      status: TransactionStatus.values.firstWhere(
        (s) => s.name == json['status'],
        orElse: () => TransactionStatus.pending,
      ),
      timestamp: DateTime.fromMillisecondsSinceEpoch(json['timestamp'] as int),
      blockNumber: json['blockNumber'] as int?,
      gasUsed: json['gasUsed'] as String?,
      gasPrice: json['gasPrice'] as String?,
      contractAddress: json['contractAddress'] as String?,
      tokenSymbol: json['tokenSymbol'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  /// Create from blockchain data
  factory Transaction.fromBlockchainData(Map<String, dynamic> data) {
    return Transaction(
      hash: data['transaction_hash'] ?? data['hash'] ?? '',
      from: data['sender_address'] ?? data['from'] ?? '',
      to: data['contract_address'] ?? data['to'] ?? '',
      value: data['amount'] ?? data['value'] ?? '0',
      type: _parseTransactionType(data),
      status: _parseTransactionStatus(data),
      timestamp: _parseTimestamp(data),
      blockNumber: data['block_number'] as int?,
      gasUsed: data['actual_fee']?.toString(),
      gasPrice: data['max_fee']?.toString(),
      contractAddress: data['contract_address'] as String?,
      tokenSymbol: data['token_symbol'] as String?,
      metadata: data['metadata'] as Map<String, dynamic>?,
    );
  }

  /// Check if this is an incoming transaction
  bool isIncoming(String userAddress) {
    return to.toLowerCase() == userAddress.toLowerCase();
  }

  /// Check if this is an outgoing transaction
  bool isOutgoing(String userAddress) {
    return from.toLowerCase() == userAddress.toLowerCase();
  }

  /// Get formatted value with symbol
  String getFormattedValue() {
    final symbol = tokenSymbol ?? 'ETH';
    final numValue = double.tryParse(value) ?? 0.0;
    
    if (numValue >= 1000000) {
      return '${(numValue / 1000000).toStringAsFixed(2)}M $symbol';
    } else if (numValue >= 1000) {
      return '${(numValue / 1000).toStringAsFixed(2)}K $symbol';
    } else if (numValue >= 1) {
      return '${numValue.toStringAsFixed(4)} $symbol';
    } else {
      return '${numValue.toStringAsFixed(8)} $symbol';
    }
  }

  /// Get transaction fee
  String? getTransactionFee() {
    if (gasUsed == null || gasPrice == null) return null;
    
    final gasUsedNum = double.tryParse(gasUsed!) ?? 0;
    final gasPriceNum = double.tryParse(gasPrice!) ?? 0;
    final fee = gasUsedNum * gasPriceNum;
    
    return '${fee.toStringAsFixed(8)} ETH';
  }

  /// Get short hash for display
  String getShortHash() {
    if (hash.length <= 12) return hash;
    return '${hash.substring(0, 6)}...${hash.substring(hash.length - 6)}';
  }

  /// Get short address for display
  String getShortAddress(String address) {
    if (address.length <= 12) return address;
    return '${address.substring(0, 6)}...${address.substring(address.length - 4)}';
  }

  /// Parse transaction type from blockchain data
  static TransactionType _parseTransactionType(Map<String, dynamic> data) {
    final type = data['type']?.toString().toLowerCase() ?? '';
    final contractAddress = data['contract_address']?.toString() ?? '';
    
    if (type.contains('invoke') || contractAddress.isNotEmpty) {
      return TransactionType.contract;
    } else if (type.contains('deploy')) {
      return TransactionType.deploy;
    } else {
      return TransactionType.transfer;
    }
  }

  /// Parse transaction status from blockchain data
  static TransactionStatus _parseTransactionStatus(Map<String, dynamic> data) {
    final status = data['status']?.toString().toLowerCase() ?? '';
    final executionStatus = data['execution_status']?.toString().toLowerCase() ?? '';
    
    if (status.contains('accepted') || executionStatus.contains('succeeded')) {
      return TransactionStatus.confirmed;
    } else if (status.contains('pending') || status.contains('received')) {
      return TransactionStatus.pending;
    } else if (status.contains('rejected') || status.contains('reverted') || executionStatus.contains('reverted')) {
      return TransactionStatus.failed;
    } else {
      return TransactionStatus.pending;
    }
  }

  /// Parse timestamp from blockchain data
  static DateTime _parseTimestamp(Map<String, dynamic> data) {
    final timestamp = data['timestamp'];
    
    if (timestamp is int) {
      return DateTime.fromMillisecondsSinceEpoch(timestamp * 1000);
    } else if (timestamp is String) {
      final parsed = int.tryParse(timestamp);
      if (parsed != null) {
        return DateTime.fromMillisecondsSinceEpoch(parsed * 1000);
      }
    }
    
    return DateTime.now();
  }

  @override
  String toString() {
    return 'Transaction(hash: ${getShortHash()}, from: ${getShortAddress(from)}, to: ${getShortAddress(to)}, value: $value, status: $status)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Transaction && other.hash == hash;
  }

  @override
  int get hashCode => hash.hashCode;
}

/// Transaction types
enum TransactionType {
  transfer,  // Simple ETH/token transfer
  contract,  // Contract interaction
  deploy,    // Contract deployment
  swap,      // Token swap
  stake,     // Staking transaction
  unstake,   // Unstaking transaction
}

/// Transaction status
enum TransactionStatus {
  pending,    // Transaction submitted but not confirmed
  confirmed,  // Transaction confirmed on blockchain
  failed,     // Transaction failed/reverted
  cancelled,  // Transaction cancelled
}

/// Extension methods for TransactionType
extension TransactionTypeExtension on TransactionType {
  /// Get display name for transaction type
  String get displayName {
    switch (this) {
      case TransactionType.transfer:
        return 'Transfer';
      case TransactionType.contract:
        return 'Contract';
      case TransactionType.deploy:
        return 'Deploy';
      case TransactionType.swap:
        return 'Swap';
      case TransactionType.stake:
        return 'Stake';
      case TransactionType.unstake:
        return 'Unstake';
    }
  }

  /// Get icon for transaction type
  String get icon {
    switch (this) {
      case TransactionType.transfer:
        return '💸';
      case TransactionType.contract:
        return '📄';
      case TransactionType.deploy:
        return '🚀';
      case TransactionType.swap:
        return '🔄';
      case TransactionType.stake:
        return '🔒';
      case TransactionType.unstake:
        return '🔓';
    }
  }
}

/// Extension methods for TransactionStatus
extension TransactionStatusExtension on TransactionStatus {
  /// Get display name for transaction status
  String get displayName {
    switch (this) {
      case TransactionStatus.pending:
        return 'Pending';
      case TransactionStatus.confirmed:
        return 'Confirmed';
      case TransactionStatus.failed:
        return 'Failed';
      case TransactionStatus.cancelled:
        return 'Cancelled';
    }
  }

  /// Get color for transaction status
  String get color {
    switch (this) {
      case TransactionStatus.pending:
        return '#FFA500'; // Orange
      case TransactionStatus.confirmed:
        return '#22C55E'; // Green
      case TransactionStatus.failed:
        return '#EF4444'; // Red
      case TransactionStatus.cancelled:
        return '#6B7280'; // Gray
    }
  }
}