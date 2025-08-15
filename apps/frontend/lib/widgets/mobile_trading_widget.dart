import 'package:flutter/material.dart';
import '../services/mobile_haptic_service.dart';
import '../services/mobile_notification_service.dart';
import '../models/simple_trade.dart';

/// Mobile-optimized trading widget with haptic feedback
/// Designed for touch interactions and mobile-first UX
class MobileTradingWidget extends StatefulWidget {
  final String symbol;
  final double currentPrice;
  final Function(double amount, String direction) onTrade;
  final bool isRealTrade;

  const MobileTradingWidget({
    super.key,
    required this.symbol,
    required this.currentPrice,
    required this.onTrade,
    this.isRealTrade = false,
  });

  @override
  State<MobileTradingWidget> createState() => _MobileTradingWidgetState();
}

class _MobileTradingWidgetState extends State<MobileTradingWidget>
    with TickerProviderStateMixin {
  final _hapticService = MobileHapticService();
  final _notificationService = MobileNotificationService();
  final _amountController = TextEditingController();

  late AnimationController _pulseController;
  late Animation<double> _pulseAnimation;

  String _selectedDirection = 'BUY';
  double _selectedAmount = 10.0;
  bool _isProcessing = false;

  @override
  void initState() {
    super.initState();

    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    );

    _pulseAnimation = Tween<double>(begin: 1.0, end: 1.1).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );

    _amountController.text = _selectedAmount.toString();

    // Initialize services
    _initializeServices();
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _amountController.dispose();
    super.dispose();
  }

  Future<void> _initializeServices() async {
    await _hapticService.initialize();
    await _notificationService.initialize();
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 8,
      margin: const EdgeInsets.all(16),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: widget.isRealTrade
                ? [Colors.green[50]!, Colors.green[100]!]
                : [Colors.blue[50]!, Colors.blue[100]!],
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _buildHeader(),
            const SizedBox(height: 20),
            _buildPriceDisplay(),
            const SizedBox(height: 20),
            _buildDirectionSelector(),
            const SizedBox(height: 16),
            _buildAmountSelector(),
            const SizedBox(height: 20),
            _buildTradeButton(),
            if (widget.isRealTrade) ...[
              const SizedBox(height: 12),
              _buildRealTradeWarning(),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: widget.isRealTrade ? Colors.green : Colors.blue,
            borderRadius: BorderRadius.circular(20),
          ),
          child: Text(
            widget.isRealTrade ? 'REAL TRADE' : 'PRACTICE',
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 12,
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            widget.symbol,
            style: Theme.of(
              context,
            ).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold),
          ),
        ),
        Icon(
          widget.isRealTrade ? Icons.trending_up : Icons.school,
          color: widget.isRealTrade ? Colors.green : Colors.blue,
          size: 28,
        ),
      ],
    );
  }

  Widget _buildPriceDisplay() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.8),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[300]!),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Current Price',
                style: Theme.of(
                  context,
                ).textTheme.bodyMedium?.copyWith(color: Colors.grey[600]),
              ),
              Text(
                '\$${widget.currentPrice.toStringAsFixed(2)}',
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
              ),
            ],
          ),
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.green[100],
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(Icons.trending_up, color: Colors.green[700], size: 24),
          ),
        ],
      ),
    );
  }

  Widget _buildDirectionSelector() {
    return Row(
      children: [
        Expanded(
          child: _buildDirectionButton('BUY', Colors.green, Icons.arrow_upward),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildDirectionButton(
            'SELL',
            Colors.red,
            Icons.arrow_downward,
          ),
        ),
      ],
    );
  }

  Widget _buildDirectionButton(String direction, Color color, IconData icon) {
    final isSelected = _selectedDirection == direction;

    return GestureDetector(
      onTap: () async {
        await _hapticService.selectionClick();
        setState(() {
          _selectedDirection = direction;
        });
      },
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(
          color: isSelected ? color : color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: color, width: isSelected ? 2 : 1),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: isSelected ? Colors.white : color, size: 20),
            const SizedBox(width: 8),
            Text(
              direction,
              style: TextStyle(
                color: isSelected ? Colors.white : color,
                fontWeight: FontWeight.bold,
                fontSize: 16,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAmountSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Trade Amount',
          style: Theme.of(
            context,
          ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: TextFormField(
                controller: _amountController,
                keyboardType: TextInputType.number,
                decoration: InputDecoration(
                  prefixText: '\$ ',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                  filled: true,
                  fillColor: Colors.white.withOpacity(0.8),
                ),
                onChanged: (value) {
                  _selectedAmount = double.tryParse(value) ?? 10.0;
                },
              ),
            ),
            const SizedBox(width: 12),
            Column(
              children: [
                _buildQuickAmountButton(25),
                const SizedBox(height: 4),
                _buildQuickAmountButton(100),
              ],
            ),
            const SizedBox(width: 8),
            Column(
              children: [
                _buildQuickAmountButton(50),
                const SizedBox(height: 4),
                _buildQuickAmountButton(250),
              ],
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildQuickAmountButton(double amount) {
    return GestureDetector(
      onTap: () async {
        await _hapticService.lightTap();
        setState(() {
          _selectedAmount = amount;
          _amountController.text = amount.toString();
        });
      },
      child: Container(
        width: 50,
        height: 30,
        decoration: BoxDecoration(
          color: Colors.grey[200],
          borderRadius: BorderRadius.circular(6),
          border: Border.all(color: Colors.grey[400]!),
        ),
        child: Center(
          child: Text(
            '\$${amount.round()}',
            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
          ),
        ),
      ),
    );
  }

  Widget _buildTradeButton() {
    return AnimatedBuilder(
      animation: _pulseAnimation,
      builder: (context, child) {
        return Transform.scale(
          scale: _isProcessing ? _pulseAnimation.value : 1.0,
          child: ElevatedButton(
            onPressed: _isProcessing ? null : _executeTrade,
            style: ElevatedButton.styleFrom(
              backgroundColor: widget.isRealTrade ? Colors.green : Colors.blue,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              elevation: 4,
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                if (_isProcessing) ...[
                  const SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                    ),
                  ),
                  const SizedBox(width: 12),
                  const Text('Processing...'),
                ] else ...[
                  Icon(
                    _selectedDirection == 'BUY'
                        ? Icons.arrow_upward
                        : Icons.arrow_downward,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    '${_selectedDirection} \$${_selectedAmount.toStringAsFixed(0)}',
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildRealTradeWarning() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.orange[100],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.orange[300]!),
      ),
      child: Row(
        children: [
          Icon(Icons.warning, color: Colors.orange[700], size: 20),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              'This is a real trade with real money',
              style: TextStyle(
                color: Colors.orange[700],
                fontWeight: FontWeight.w500,
                fontSize: 12,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _executeTrade() async {
    if (_isProcessing) return;

    setState(() {
      _isProcessing = true;
    });

    try {
      // Strong haptic feedback for trade execution
      await _hapticService.tradeExecuted(isRealTrade: widget.isRealTrade);

      // Start pulse animation
      _pulseController.repeat(reverse: true);

      // Simulate processing delay
      await Future.delayed(const Duration(milliseconds: 1500));

      // Execute the trade
      widget.onTrade(_selectedAmount, _selectedDirection);

      // Success haptic feedback
      await _hapticService.success(isMajor: widget.isRealTrade);

      // Show success message
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Trade executed: ${_selectedDirection} \$${_selectedAmount.toStringAsFixed(0)} ${widget.symbol}',
            ),
            backgroundColor: Colors.green,
            duration: const Duration(seconds: 2),
          ),
        );
      }
    } catch (e) {
      // Error haptic feedback
      await _hapticService.error();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Trade failed: $e'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 3),
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isProcessing = false;
        });
        _pulseController.stop();
        _pulseController.reset();
      }
    }
  }
}
