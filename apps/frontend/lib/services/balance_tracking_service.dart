import 'dart:async';
import 'dart:developer';
import '../models/wallet_balance.dart';
import 'mobile_starknet_service.dart';
import 'secure_storage_service.dart';

/// Balance Tracking Service
/// Provides real-time balance updates and caching
class BalanceTrackingService {
  static BalanceTrackingService? _instance;
  static BalanceTrackingService get instance => _instance ??= BalanceTrackingService._();

  BalanceTrackingService._();

  final MobileStarknetService _starknetService = MobileStarknetService();
  final SecureStorageService _secureStorage = SecureStorageService.instance;
  
  // Current balances cache
  WalletBalance? _cachedBalance;
  DateTime? _lastUpdateTime;
  static const Duration _cacheValidDuration = Duration(minutes: 2);
  
  // Stream controller for real-time updates
  final StreamController<WalletBalance> _balanceController = StreamController<WalletBalance>.broadcast();
  Stream<WalletBalance> get balanceStream => _balanceController.stream;
  
  // Polling timer for automatic updates
  Timer? _pollingTimer;
  String? _currentAddress;
  bool _isPolling = false;

  /// Get current balance for an address
  Future<WalletBalance> getBalance({
    required String address,
    bool forceRefresh = false,
  }) async {
    try {
      // Check if we can use cached data
      if (!forceRefresh && _isCacheValid() && _cachedBalance != null) {
        log('💰 Using cached balance for ${address.substring(0, 10)}...');
        return _cachedBalance!;
      }

      log('🔍 Fetching balance for address: ${address.substring(0, 10)}...');
      
      // Fetch from blockchain
      final balance = await _fetchBalanceFromBlockchain(address);
      
      // Update cache
      _cachedBalance = balance;
      _lastUpdateTime = DateTime.now();
      
      // Emit update
      _balanceController.add(balance);
      
      // Store balance locally for offline access
      await _storeBalanceLocally(balance);
      
      log('✅ Balance fetched: ${balance.ethBalance} ETH, ${balance.stellarShards} Shards');
      return balance;
    } catch (e) {
      log('❌ Failed to fetch balance: $e');
      
      // Try to return cached or stored balance
      if (_cachedBalance != null) {
        log('⚠️ Returning cached balance due to fetch error');
        return _cachedBalance!;
      }
      
      // Try to load from local storage
      final storedBalance = await _loadBalanceFromStorage(address);
      if (storedBalance != null) {
        log('⚠️ Returning stored balance due to fetch error');
        _cachedBalance = storedBalance;
        return storedBalance;
      }
      
      throw BalanceTrackingException('Failed to fetch balance: ${e.toString()}');
    }
  }

  /// Start real-time balance polling
  void startBalancePolling({
    required String address,
    Duration interval = const Duration(seconds: 30),
  }) {
    if (_isPolling && _currentAddress == address) {
      log('⚠️ Already polling for address: ${address.substring(0, 10)}...');
      return;
    }

    stopBalancePolling();
    
    _currentAddress = address;
    _isPolling = true;
    
    log('🔄 Starting balance polling for ${address.substring(0, 10)}... (interval: ${interval.inSeconds}s)');
    
    // Initial fetch
    getBalance(address: address);
    
    // Set up periodic polling
    _pollingTimer = Timer.periodic(interval, (timer) async {
      if (!_isPolling) {
        timer.cancel();
        return;
      }
      
      try {
        await getBalance(address: address, forceRefresh: true);
      } catch (e) {
        log('⚠️ Balance polling error: $e');
      }
    });
  }

  /// Stop balance polling
  void stopBalancePolling() {
    if (_pollingTimer != null) {
      _pollingTimer!.cancel();
      _pollingTimer = null;
    }
    
    _isPolling = false;
    _currentAddress = null;
    
    log('⏹️ Balance polling stopped');
  }

  /// Update balance after a transaction
  Future<void> updateBalanceAfterTransaction({
    required String address,
    required String transactionHash,
    bool isOutgoing = true,
    double? estimatedAmount,
  }) async {
    try {
      log('🔄 Updating balance after transaction: ${transactionHash.substring(0, 10)}...');
      
      if (_cachedBalance != null && estimatedAmount != null) {
        // Optimistic update
        final updatedBalance = isOutgoing 
          ? _cachedBalance!.copyWith(
              ethBalance: _cachedBalance!.ethBalance - estimatedAmount,
            )
          : _cachedBalance!.copyWith(
              ethBalance: _cachedBalance!.ethBalance + estimatedAmount,
            );
        
        _cachedBalance = updatedBalance;
        _balanceController.add(updatedBalance);
        log('📊 Optimistic balance update applied');
      }
      
      // Fetch actual balance after a short delay
      Timer(const Duration(seconds: 5), () async {
        try {
          await getBalance(address: address, forceRefresh: true);
        } catch (e) {
          log('⚠️ Failed to refresh balance after transaction: $e');
        }
      });
      
    } catch (e) {
      log('❌ Failed to update balance after transaction: $e');
    }
  }

  /// Add to stellar shards balance (game rewards)
  Future<void> addStellarShards({
    required String address,
    required double amount,
    String? reason,
  }) async {
    try {
      log('⭐ Adding $amount Stellar Shards${reason != null ? ' for $reason' : ''}');
      
      if (_cachedBalance != null) {
        final updatedBalance = _cachedBalance!.copyWith(
          stellarShards: _cachedBalance!.stellarShards + amount,
        );
        
        _cachedBalance = updatedBalance;
        _balanceController.add(updatedBalance);
        
        await _storeBalanceLocally(updatedBalance);
        
        log('✅ Stellar Shards balance updated: ${updatedBalance.stellarShards}');
      }
    } catch (e) {
      log('❌ Failed to add Stellar Shards: $e');
      throw BalanceTrackingException('Failed to add Stellar Shards: ${e.toString()}');
    }
  }

  /// Add to lumina balance (game rewards)
  Future<void> addLumina({
    required String address,
    required double amount,
    String? reason,
  }) async {
    try {
      log('✨ Adding $amount Lumina${reason != null ? ' for $reason' : ''}');
      
      if (_cachedBalance != null) {
        final updatedBalance = _cachedBalance!.copyWith(
          lumina: _cachedBalance!.lumina + amount,
        );
        
        _cachedBalance = updatedBalance;
        _balanceController.add(updatedBalance);
        
        await _storeBalanceLocally(updatedBalance);
        
        log('✅ Lumina balance updated: ${updatedBalance.lumina}');
      }
    } catch (e) {
      log('❌ Failed to add Lumina: $e');
      throw BalanceTrackingException('Failed to add Lumina: ${e.toString()}');
    }
  }

  /// Get cached balance (sync)
  WalletBalance? getCachedBalance() {
    return _cachedBalance;
  }

  /// Clear cached balance
  void clearCache() {
    _cachedBalance = null;
    _lastUpdateTime = null;
    log('🗑️ Balance cache cleared');
  }

  /// Dispose service
  void dispose() {
    stopBalancePolling();
    _balanceController.close();
  }

  /// Check if cached data is still valid
  bool _isCacheValid() {
    if (_lastUpdateTime == null) return false;
    return DateTime.now().difference(_lastUpdateTime!) < _cacheValidDuration;
  }

  /// Fetch balance from blockchain
  Future<WalletBalance> _fetchBalanceFromBlockchain(String address) async {
    try {
      // This would integrate with Starknet node or block explorer API
      // For now, we'll simulate the API call
      
      await Future.delayed(const Duration(milliseconds: 500)); // Simulate network delay
      
      // In production, this would be something like:
      // final ethBalance = await _starknetService.getETHBalance(address);
      // final tokenBalances = await _starknetService.getTokenBalances(address);
      
      // For demo, we'll return mock data that changes slightly over time
      final random = DateTime.now().millisecondsSinceEpoch % 1000;
      final ethBalance = 0.1 + (random / 10000); // Slightly varying ETH balance
      
      // Get game balances from cache or storage (these are managed locally)
      final gameBalances = await _loadGameBalancesFromStorage(address);
      
      return WalletBalance(
        address: address,
        ethBalance: ethBalance,
        stellarShards: gameBalances['stellarShards'] ?? 100.0,
        lumina: gameBalances['lumina'] ?? 0.0,
        lastUpdated: DateTime.now(),
        tokenBalances: {
          'USDC': 50.0,
          'USDT': 25.0,
          'DAI': 10.0,
        },
      );
    } catch (e) {
      log('❌ Blockchain balance fetch error: $e');
      rethrow;
    }
  }

  /// Store balance locally for offline access
  Future<void> _storeBalanceLocally(WalletBalance balance) async {
    try {
      final key = 'balance_${balance.address}';
      final data = balance.toJson();
      await _secureStorage.storeValue(key, data);
    } catch (e) {
      log('⚠️ Failed to store balance locally: $e');
      // Don't throw, as this is not critical
    }
  }

  /// Load balance from local storage
  Future<WalletBalance?> _loadBalanceFromStorage(String address) async {
    try {
      final key = 'balance_$address';
      final data = await _secureStorage.getValue(key);
      if (data != null) {
        return WalletBalance.fromJson(data);
      }
      return null;
    } catch (e) {
      log('⚠️ Failed to load balance from storage: $e');
      return null;
    }
  }

  /// Load game balances from storage
  Future<Map<String, double>> _loadGameBalancesFromStorage(String address) async {
    try {
      final shardsKey = 'stellarShards_$address';
      final luminaKey = 'lumina_$address';
      
      final shardsData = await _secureStorage.getValue(shardsKey);
      final luminaData = await _secureStorage.getValue(luminaKey);
      
      return {
        'stellarShards': shardsData != null ? double.tryParse(shardsData) ?? 100.0 : 100.0,
        'lumina': luminaData != null ? double.tryParse(luminaData) ?? 0.0 : 0.0,
      };
    } catch (e) {
      log('⚠️ Failed to load game balances from storage: $e');
      return {'stellarShards': 100.0, 'lumina': 0.0};
    }
  }

  /// Store individual game balance
  Future<void> _storeGameBalance(String address, String currency, double amount) async {
    try {
      final key = '${currency}_$address';
      await _secureStorage.storeValue(key, amount.toString());
    } catch (e) {
      log('⚠️ Failed to store game balance: $e');
    }
  }
}

/// Custom exception for balance tracking operations
class BalanceTrackingException implements Exception {
  final String message;
  
  BalanceTrackingException(this.message);

  @override
  String toString() => 'BalanceTrackingException: $message';
}