import 'dart:developer';
import '../models/transaction.dart';
import 'secure_storage_service.dart';
import 'mobile_starknet_service.dart';

/// Transaction History Service
/// Manages transaction history, caching, and real-time updates
class TransactionHistoryService {
  static TransactionHistoryService? _instance;
  static TransactionHistoryService get instance => _instance ??= TransactionHistoryService._();

  TransactionHistoryService._();

  final SecureStorageService _secureStorage = SecureStorageService.instance;
  final MobileStarknetService _starknetService = MobileStarknetService();
  
  List<Transaction> _cachedTransactions = [];
  DateTime? _lastFetchTime;
  static const Duration _cacheValidDuration = Duration(minutes: 5);
  
  // Stream controller for real-time updates
  final List<Function(List<Transaction>)> _listeners = [];

  /// Get transaction history for a wallet address
  Future<List<Transaction>> getTransactionHistory({
    required String address,
    int limit = 50,
    int offset = 0,
    bool forceRefresh = false,
  }) async {
    try {
      // Check if we can use cached data
      if (!forceRefresh && _isCacheValid() && _cachedTransactions.isNotEmpty) {
        log('📋 Using cached transaction history (${_cachedTransactions.length} transactions)');
        return _cachedTransactions.skip(offset).take(limit).toList();
      }

      log('🔍 Fetching transaction history for address: ${address.substring(0, 10)}...');
      
      // Fetch from blockchain
      final transactions = await _fetchTransactionsFromBlockchain(address, limit, offset);
      
      // Update cache
      _cachedTransactions = transactions;
      _lastFetchTime = DateTime.now();
      
      // Notify listeners
      _notifyListeners(transactions);
      
      log('✅ Fetched ${transactions.length} transactions');
      return transactions;
    } catch (e) {
      log('❌ Failed to fetch transaction history: $e');
      
      // Return cached data if available
      if (_cachedTransactions.isNotEmpty) {
        log('⚠️ Returning cached transactions due to fetch error');
        return _cachedTransactions.skip(offset).take(limit).toList();
      }
      
      throw TransactionHistoryException('Failed to fetch transaction history: ${e.toString()}');
    }
  }

  /// Get pending transactions
  Future<List<Transaction>> getPendingTransactions(String address) async {
    try {
      log('⏳ Fetching pending transactions for address: ${address.substring(0, 10)}...');
      
      // In a real implementation, this would fetch from mempool or pending transaction pool
      // For now, we'll return a filtered list from cached transactions
      final pendingTransactions = _cachedTransactions
          .where((tx) => tx.status == TransactionStatus.pending)
          .toList();
      
      log('📋 Found ${pendingTransactions.length} pending transactions');
      return pendingTransactions;
    } catch (e) {
      log('❌ Failed to fetch pending transactions: $e');
      return [];
    }
  }

  /// Add a new transaction (for tracking sent transactions)
  Future<void> addTransaction(Transaction transaction) async {
    try {
      log('➕ Adding new transaction: ${transaction.hash}');
      
      // Add to cache
      _cachedTransactions.insert(0, transaction);
      
      // Store in local storage for persistence
      await _storeTransactionLocally(transaction);
      
      // Notify listeners
      _notifyListeners(_cachedTransactions);
      
      log('✅ Transaction added successfully');
    } catch (e) {
      log('❌ Failed to add transaction: $e');
      throw TransactionHistoryException('Failed to add transaction: ${e.toString()}');
    }
  }

  /// Update transaction status (when confirmation is received)
  Future<void> updateTransactionStatus(String hash, TransactionStatus status) async {
    try {
      log('🔄 Updating transaction status: $hash -> $status');
      
      final index = _cachedTransactions.indexWhere((tx) => tx.hash == hash);
      if (index != -1) {
        _cachedTransactions[index] = _cachedTransactions[index].copyWith(
          status: status,
          timestamp: status == TransactionStatus.confirmed ? DateTime.now() : _cachedTransactions[index].timestamp,
        );
        
        // Notify listeners
        _notifyListeners(_cachedTransactions);
        
        log('✅ Transaction status updated successfully');
      } else {
        log('⚠️ Transaction not found in cache: $hash');
      }
    } catch (e) {
      log('❌ Failed to update transaction status: $e');
    }
  }

  /// Get transaction by hash
  Future<Transaction?> getTransaction(String hash) async {
    try {
      // Check cache first
      final cachedTransaction = _cachedTransactions
          .where((tx) => tx.hash == hash)
          .firstOrNull;
      
      if (cachedTransaction != null) {
        return cachedTransaction;
      }
      
      // Fetch from blockchain
      log('🔍 Fetching transaction from blockchain: $hash');
      final transaction = await _fetchTransactionFromBlockchain(hash);
      
      if (transaction != null) {
        // Add to cache
        _cachedTransactions.add(transaction);
        _notifyListeners(_cachedTransactions);
      }
      
      return transaction;
    } catch (e) {
      log('❌ Failed to get transaction: $e');
      return null;
    }
  }

  /// Subscribe to transaction updates
  void addListener(Function(List<Transaction>) listener) {
    _listeners.add(listener);
  }

  /// Unsubscribe from transaction updates
  void removeListener(Function(List<Transaction>) listener) {
    _listeners.remove(listener);
  }

  /// Clear cached transactions
  void clearCache() {
    _cachedTransactions.clear();
    _lastFetchTime = null;
    log('🗑️ Transaction cache cleared');
  }

  /// Check if cached data is still valid
  bool _isCacheValid() {
    if (_lastFetchTime == null) return false;
    return DateTime.now().difference(_lastFetchTime!) < _cacheValidDuration;
  }

  /// Notify all listeners of transaction updates
  void _notifyListeners(List<Transaction> transactions) {
    for (final listener in _listeners) {
      try {
        listener(transactions);
      } catch (e) {
        log('⚠️ Error notifying transaction listener: $e');
      }
    }
  }

  /// Fetch transactions from blockchain
  Future<List<Transaction>> _fetchTransactionsFromBlockchain(
    String address,
    int limit,
    int offset,
  ) async {
    try {
      // This would integrate with a Starknet block explorer API or node
      // For now, we'll return mock data that looks realistic
      
      // In production, you would call something like:
      // final response = await _starknetService.getTransactionHistory(address, limit, offset);
      // return response.map((tx) => Transaction.fromBlockchainData(tx)).toList();
      
      await Future.delayed(const Duration(seconds: 1)); // Simulate network delay
      
      // Return mock transactions for demo
      return _generateMockTransactions(address, limit);
    } catch (e) {
      log('❌ Blockchain fetch error: $e');
      rethrow;
    }
  }

  /// Fetch single transaction from blockchain
  Future<Transaction?> _fetchTransactionFromBlockchain(String hash) async {
    try {
      // This would integrate with a Starknet block explorer API or node
      // For now, we'll return null or a mock transaction
      
      await Future.delayed(const Duration(milliseconds: 500)); // Simulate network delay
      
      // Return mock transaction if hash matches a pattern
      if (hash.startsWith('0x')) {
        return Transaction(
          hash: hash,
          from: '0x1234567890abcdef1234567890abcdef12345678',
          to: '0xabcdef1234567890abcdef1234567890abcdef12',
          value: '0.1',
          type: TransactionType.transfer,
          status: TransactionStatus.confirmed,
          timestamp: DateTime.now(),
          blockNumber: 12345,
          gasUsed: '21000',
          gasPrice: '0.000000001',
        );
      }
      
      return null;
    } catch (e) {
      log('❌ Failed to fetch transaction from blockchain: $e');
      return null;
    }
  }

  /// Store transaction locally for persistence
  Future<void> _storeTransactionLocally(Transaction transaction) async {
    try {
      // Store in secure storage with a transaction key
      final key = 'tx_${transaction.hash}';
      final data = transaction.toJson();
      await _secureStorage.storeValue(key, data);
    } catch (e) {
      log('⚠️ Failed to store transaction locally: $e');
      // Don't throw, as this is not critical
    }
  }

  /// Generate mock transactions for demo purposes
  List<Transaction> _generateMockTransactions(String address, int limit) {
    final transactions = <Transaction>[];
    final now = DateTime.now();
    
    final mockHashes = [
      '0xa1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456',
      '0xb2c3d4e5f67890123456789012345678901abcdef234567890abcdef1234567',
      '0xc3d4e5f678901234567890123456789012abcdef34567890abcdef12345678',
      '0xd4e5f6789012345678901234567890123abcdef4567890abcdef123456789',
      '0xe5f678901234567890123456789012346abcdef567890abcdef1234567890',
    ];
    
    for (int i = 0; i < limit && i < mockHashes.length; i++) {
      transactions.add(Transaction(
        hash: mockHashes[i],
        from: i % 2 == 0 ? address : '0x1234567890abcdef1234567890abcdef12345678',
        to: i % 2 == 0 ? '0x1234567890abcdef1234567890abcdef12345678' : address,
        value: (0.01 * (i + 1)).toString(),
        type: i % 3 == 0 ? TransactionType.contract : TransactionType.transfer,
        status: i == 0 ? TransactionStatus.pending : TransactionStatus.confirmed,
        timestamp: now.subtract(Duration(hours: i)),
        blockNumber: 12345 - i,
        gasUsed: (21000 + i * 1000).toString(),
        gasPrice: '0.000000001',
      ));
    }
    
    return transactions;
  }
}

/// Custom exception for transaction history operations
class TransactionHistoryException implements Exception {
  final String message;
  
  TransactionHistoryException(this.message);

  @override
  String toString() => 'TransactionHistoryException: $message';
}