import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';

/// Wallet Info Widget
/// Displays wallet address, balance, and quick actions
class WalletInfoWidget extends StatelessWidget {
  final String address;
  final double ethBalance;
  final double stellarShards;
  final double lumina;
  final VoidCallback? onCopyAddress;
  final VoidCallback? onViewTransactions;
  final VoidCallback? onSend;
  final VoidCallback? onReceive;

  const WalletInfoWidget({
    super.key,
    required this.address,
    required this.ethBalance,
    required this.stellarShards,
    required this.lumina,
    this.onCopyAddress,
    this.onViewTransactions,
    this.onSend,
    this.onReceive,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF7B2CBF), Color(0xFF9D4EDD)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF7B2CBF).withOpacity(0.3),
            blurRadius: 20,
            spreadRadius: 2,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(),
          const SizedBox(height: 20),
          _buildBalanceSection(),
          const SizedBox(height: 20),
          _buildActionButtons(context),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.2),
            borderRadius: BorderRadius.circular(8),
          ),
          child: const Icon(
            Icons.account_balance_wallet,
            color: Colors.white,
            size: 20,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Wallet Address',
                style: GoogleFonts.rajdhani(
                  fontSize: 12,
                  color: Colors.white.withOpacity(0.8),
                  fontWeight: FontWeight.w500,
                ),
              ),
              Row(
                children: [
                  Expanded(
                    child: Text(
                      _formatAddress(address),
                      style: GoogleFonts.rajdhani(
                        fontSize: 14,
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  IconButton(
                    onPressed: () {
                      Clipboard.setData(ClipboardData(text: address));
                      onCopyAddress?.call();
                    },
                    icon: const Icon(
                      Icons.copy,
                      color: Colors.white,
                      size: 16,
                    ),
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(),
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildBalanceSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Balances',
          style: GoogleFonts.orbitron(
            fontSize: 16,
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        
        // ETH Balance
        _buildBalanceRow(
          icon: Icons.currency_bitcoin,
          label: 'ETH',
          balance: ethBalance.toStringAsFixed(4),
          color: Colors.white,
        ),
        const SizedBox(height: 8),
        
        // Stellar Shards
        _buildBalanceRow(
          icon: Icons.stars,
          label: 'Stellar Shards',
          balance: stellarShards.toStringAsFixed(0),
          color: const Color(0xFFFFD700),
        ),
        const SizedBox(height: 8),
        
        // Lumina
        _buildBalanceRow(
          icon: Icons.wb_sunny,
          label: 'Lumina',
          balance: lumina.toStringAsFixed(0),
          color: const Color(0xFF00FFFF),
        ),
      ],
    );
  }

  Widget _buildBalanceRow({
    required IconData icon,
    required String label,
    required String balance,
    required Color color,
  }) {
    return Row(
      children: [
        Icon(icon, color: color, size: 16),
        const SizedBox(width: 8),
        Text(
          label,
          style: GoogleFonts.rajdhani(
            fontSize: 14,
            color: Colors.white.withOpacity(0.8),
          ),
        ),
        const Spacer(),
        Text(
          balance,
          style: GoogleFonts.rajdhani(
            fontSize: 14,
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildActionButtons(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: _buildActionButton(
            icon: Icons.send,
            label: 'Send',
            onPressed: onSend,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildActionButton(
            icon: Icons.call_received,
            label: 'Receive',
            onPressed: onReceive,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildActionButton(
            icon: Icons.history,
            label: 'History',
            onPressed: onViewTransactions,
          ),
        ),
      ],
    );
  }

  Widget _buildActionButton({
    required IconData icon,
    required String label,
    VoidCallback? onPressed,
  }) {
    return Material(
      color: Colors.white.withOpacity(0.2),
      borderRadius: BorderRadius.circular(10),
      child: InkWell(
        onTap: onPressed,
        borderRadius: BorderRadius.circular(10),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 10),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(10),
            border: Border.all(
              color: Colors.white.withOpacity(0.3),
            ),
          ),
          child: Column(
            children: [
              Icon(icon, color: Colors.white, size: 20),
              const SizedBox(height: 4),
              Text(
                label,
                style: GoogleFonts.rajdhani(
                  fontSize: 12,
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _formatAddress(String address) {
    if (address.length <= 10) return address;
    return '${address.substring(0, 6)}...${address.substring(address.length - 4)}';
  }
}

/// Compact Wallet Balance Widget
/// Shows just the essential balance information
class WalletBalanceWidget extends StatelessWidget {
  final double ethBalance;
  final double stellarShards;
  final bool showDetails;

  const WalletBalanceWidget({
    super.key,
    required this.ethBalance,
    required this.stellarShards,
    this.showDetails = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[800]!),
      ),
      child: showDetails ? _buildDetailedView() : _buildCompactView(),
    );
  }

  Widget _buildCompactView() {
    return Row(
      children: [
        const Icon(
          Icons.account_balance_wallet,
          color: Color(0xFF7B2CBF),
          size: 20,
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Wallet Balance',
                style: GoogleFonts.rajdhani(
                  fontSize: 12,
                  color: Colors.grey[400],
                ),
              ),
              Text(
                '${ethBalance.toStringAsFixed(4)} ETH',
                style: GoogleFonts.rajdhani(
                  fontSize: 16,
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
        Text(
          '${stellarShards.toStringAsFixed(0)}',
          style: GoogleFonts.rajdhani(
            fontSize: 14,
            color: const Color(0xFFFFD700),
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(width: 4),
        const Icon(
          Icons.stars,
          color: Color(0xFFFFD700),
          size: 14,
        ),
      ],
    );
  }

  Widget _buildDetailedView() {
    return Column(
      children: [
        Row(
          children: [
            const Icon(
              Icons.account_balance_wallet,
              color: Color(0xFF7B2CBF),
              size: 20,
            ),
            const SizedBox(width: 12),
            Text(
              'Wallet Balance',
              style: GoogleFonts.orbitron(
                fontSize: 16,
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        
        Row(
          children: [
            Expanded(
              child: _buildBalanceItem(
                icon: Icons.currency_bitcoin,
                label: 'ETH',
                value: ethBalance.toStringAsFixed(4),
                color: Colors.white,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildBalanceItem(
                icon: Icons.stars,
                label: 'Shards',
                value: stellarShards.toStringAsFixed(0),
                color: const Color(0xFFFFD700),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildBalanceItem({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(height: 4),
          Text(
            label,
            style: GoogleFonts.rajdhani(
              fontSize: 12,
              color: Colors.grey[400],
            ),
          ),
          Text(
            value,
            style: GoogleFonts.rajdhani(
              fontSize: 16,
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
}

/// Wallet Address Widget
/// Standalone widget for displaying and copying wallet address
class WalletAddressWidget extends StatelessWidget {
  final String address;
  final String? label;
  final VoidCallback? onCopy;

  const WalletAddressWidget({
    super.key,
    required this.address,
    this.label,
    this.onCopy,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[800]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (label != null) ...[
            Text(
              label!,
              style: GoogleFonts.rajdhani(
                fontSize: 14,
                color: Colors.grey[400],
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 8),
          ],
          
          Row(
            children: [
              Expanded(
                child: Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.grey[800],
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    address,
                    style: const TextStyle(
                      fontSize: 14,
                      color: Colors.white,
                      fontFamily: 'monospace',
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              IconButton(
                onPressed: () {
                  Clipboard.setData(ClipboardData(text: address));
                  onCopy?.call();
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Address copied to clipboard'),
                      duration: Duration(seconds: 2),
                    ),
                  );
                },
                icon: const Icon(Icons.copy, color: Color(0xFF7B2CBF)),
                tooltip: 'Copy address',
              ),
            ],
          ),
        ],
      ),
    );
  }
}