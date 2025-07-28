import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'dart:async';

import '../models/user.dart';
// TEMPORARILY DISABLED: Starknet service has API compatibility issues
// import '../services/starknet_service.dart';
import '../providers/auth_provider.dart';

/// Starknet wallet balance data
class WalletBalance {
  final String eth;
  final String strk;
  final bool isLoading;
  final String? error;

  const WalletBalance({
    required this.eth,
    required this.strk,
    this.isLoading = false,
    this.error,
  });
}

/// Provider for wallet balance
final walletBalanceProvider = StateNotifierProvider<WalletBalanceNotifier, WalletBalance>((ref) {
  return WalletBalanceNotifier(ref);
});

class WalletBalanceNotifier extends StateNotifier<WalletBalance> {
  final Ref ref;
  Timer? _refreshTimer;

  WalletBalanceNotifier(this.ref) : super(const WalletBalance(eth: '0.0', strk: '0.0', isLoading: true)) {
    _loadBalance();
    _startPeriodicRefresh();
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }

  void _startPeriodicRefresh() {
    _refreshTimer = Timer.periodic(const Duration(minutes: 1), (_) {
      _loadBalance();
    });
  }

  Future<void> _loadBalance() async {
    final user = ref.read(currentUserProvider);
    if (user == null) return;

    state = state.copyWith(isLoading: true, error: null);

    try {
      // TEMPORARILY DISABLED: Starknet service has API compatibility issues
      // TODO: Fix Starknet API compatibility
      /*
      final starknetService = StarknetService(useMainnet: false);
      final ethBalance = await starknetService.getEthBalance(user.starknetAddress);
      final strkBalance = await starknetService.getStrkBalance(user.starknetAddress);
      */
      
      // Mock balances for now
      final ethBalance = 0.5;
      final strkBalance = 100.0;

      state = WalletBalance(
        eth: ethBalance.toStringAsFixed(4),
        strk: strkBalance.toStringAsFixed(2),
        isLoading: false,
      );
    } catch (e) {
      state = WalletBalance(
        eth: '0.0',
        strk: '0.0',
        isLoading: false,
        error: 'Failed to load balance: $e',
      );
    }
  }

  void refresh() {
    _loadBalance();
  }
}

extension WalletBalanceCopyWith on WalletBalance {
  WalletBalance copyWith({
    String? eth,
    String? strk,
    bool? isLoading,
    String? error,
  }) {
    return WalletBalance(
      eth: eth ?? this.eth,
      strk: strk ?? this.strk,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

/// Starknet Wallet Widget for Main Hub
class StarknetWalletWidget extends ConsumerWidget {
  const StarknetWalletWidget({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(currentUserProvider);
    final walletBalance = ref.watch(walletBalanceProvider);

    if (user == null) {
      return const SizedBox.shrink();
    }

    return Container(
      margin: const EdgeInsets.symmetric(vertical: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            const Color(0xFF1A1A2E).withOpacity(0.9),
            const Color(0xFF16213E).withOpacity(0.9),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Colors.cyan.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header with wallet icon and status
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.cyan.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  Icons.account_balance_wallet,
                  color: Colors.cyan,
                  size: 24,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Starknet Wallet',
                      style: GoogleFonts.orbitron(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    Row(
                      children: [
                        Container(
                          width: 8,
                          height: 8,
                          decoration: BoxDecoration(
                            color: Colors.green,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 4),
                        Text(
                          'Connected',
                          style: GoogleFonts.rajdhani(
                            fontSize: 12,
                            color: Colors.green,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              IconButton(
                icon: Icon(Icons.refresh, color: Colors.cyan, size: 20),
                onPressed: () => ref.read(walletBalanceProvider.notifier).refresh(),
                tooltip: 'Refresh Balance',
              ),
            ],
          ),
          const SizedBox(height: 16),

          // Wallet Address
          _buildAddressSection(context, user.starknetAddress),
          const SizedBox(height: 16),

          // Balance Section
          _buildBalanceSection(context, walletBalance),

          // Actions Row
          const SizedBox(height: 16),
          _buildActionsRow(context, user),
        ],
      ),
    );
  }

  Widget _buildAddressSection(BuildContext context, String address) {
    final displayAddress = '${address.substring(0, 6)}...${address.substring(address.length - 4)}';

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.2),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          Icon(Icons.fingerprint, color: Colors.grey, size: 18),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Wallet Address',
                  style: GoogleFonts.rajdhani(
                    fontSize: 12,
                    color: Colors.grey,
                  ),
                ),
                Text(
                  displayAddress,
                  style: GoogleFonts.rajdhani(
                    fontSize: 16,
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          IconButton(
            icon: Icon(Icons.copy, color: Colors.cyan, size: 18),
            onPressed: () => _copyAddress(context, address),
            tooltip: 'Copy Address',
          ),
        ],
      ),
    );
  }

  Widget _buildBalanceSection(BuildContext context, WalletBalance balance) {
    if (balance.isLoading) {
      return Container(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            SizedBox(
              width: 20,
              height: 20,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                valueColor: AlwaysStoppedAnimation<Color>(Colors.cyan),
              ),
            ),
            const SizedBox(width: 12),
            Text(
              'Loading balance...',
              style: GoogleFonts.rajdhani(color: Colors.grey),
            ),
          ],
        ),
      );
    }

    if (balance.error != null) {
      return Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.red.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          children: [
            Icon(Icons.error, color: Colors.red, size: 18),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                balance.error!,
                style: GoogleFonts.rajdhani(
                  color: Colors.red,
                  fontSize: 12,
                ),
              ),
            ),
          ],
        ),
      );
    }

    return Row(
      children: [
        Expanded(
          child: _buildBalanceCard('ETH', balance.eth, Colors.blue),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildBalanceCard('STRK', balance.strk, Colors.purple),
        ),
      ],
    );
  }

  Widget _buildBalanceCard(String symbol, String amount, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            symbol,
            style: GoogleFonts.orbitron(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            amount,
            style: GoogleFonts.rajdhani(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionsRow(BuildContext context, User user) {
    return Row(
      children: [
        Expanded(
          child: OutlinedButton.icon(
            onPressed: () => _showReceiveDialog(context, user.starknetAddress),
            icon: Icon(Icons.arrow_downward, size: 16),
            label: Text('Receive'),
            style: OutlinedButton.styleFrom(
              foregroundColor: Colors.cyan,
              side: BorderSide(color: Colors.cyan.withOpacity(0.5)),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: OutlinedButton.icon(
            onPressed: () => _showSendDialog(context),
            icon: Icon(Icons.arrow_upward, size: 16),
            label: Text('Send'),
            style: OutlinedButton.styleFrom(
              foregroundColor: Colors.orange,
              side: BorderSide(color: Colors.orange.withOpacity(0.5)),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: OutlinedButton.icon(
            onPressed: () => _showTransactionHistory(context),
            icon: Icon(Icons.history, size: 16),
            label: Text('History'),
            style: OutlinedButton.styleFrom(
              foregroundColor: Colors.purple,
              side: BorderSide(color: Colors.purple.withOpacity(0.5)),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
          ),
        ),
      ],
    );
  }

  void _copyAddress(BuildContext context, String address) {
    Clipboard.setData(ClipboardData(text: address));
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Wallet address copied to clipboard!'),
        backgroundColor: Colors.green[700],
        duration: const Duration(seconds: 2),
      ),
    );
  }

  void _showReceiveDialog(BuildContext context, String address) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1A1A2E),
        title: Text(
          'Receive Funds',
          style: GoogleFonts.orbitron(color: Colors.white),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'Share this address to receive ETH or STRK tokens:',
              style: GoogleFonts.rajdhani(color: Colors.grey),
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.black.withOpacity(0.3),
                borderRadius: BorderRadius.circular(8),
              ),
              child: SelectableText(
                address,
                style: GoogleFonts.rajdhani(
                  color: Colors.white,
                  fontSize: 14,
                ),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text('Close', style: GoogleFonts.rajdhani(color: Colors.grey)),
          ),
          ElevatedButton(
            onPressed: () {
              _copyAddress(context, address);
              Navigator.of(context).pop();
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.cyan),
            child: Text('Copy Address', style: GoogleFonts.rajdhani(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  void _showSendDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1A1A2E),
        title: Text(
          'Send Funds',
          style: GoogleFonts.orbitron(color: Colors.white),
        ),
        content: Text(
          'Send functionality will be available in a future update. This will allow you to send ETH and STRK tokens to other Starknet addresses.',
          style: GoogleFonts.rajdhani(color: Colors.grey),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text('OK', style: GoogleFonts.rajdhani(color: Colors.cyan)),
          ),
        ],
      ),
    );
  }

  void _showTransactionHistory(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1A1A2E),
        title: Text(
          'Transaction History',
          style: GoogleFonts.orbitron(color: Colors.white),
        ),
        content: Text(
          'Transaction history will be available in a future update. This will show your recent Starknet transactions.',
          style: GoogleFonts.rajdhani(color: Colors.grey),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text('OK', style: GoogleFonts.rajdhani(color: Colors.cyan)),
          ),
        ],
      ),
    );
  }
}