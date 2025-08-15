import 'package:flutter/material.dart';

/// Widget for NFT marketplace filters
class NFTFilterWidget extends StatefulWidget {
  final Map<String, dynamic> initialFilters;
  final Function(Map<String, dynamic>) onFiltersChanged;

  const NFTFilterWidget({
    super.key,
    required this.initialFilters,
    required this.onFiltersChanged,
  });

  @override
  State<NFTFilterWidget> createState() => _NFTFilterWidgetState();
}

class _NFTFilterWidgetState extends State<NFTFilterWidget> {
  late Map<String, dynamic> _filters;

  @override
  void initState() {
    super.initState();
    _filters = Map<String, dynamic>.from(widget.initialFilters);
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Filter Marketplace',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 24),
          // Currency filter
          const Text('Currency', style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            children: [
              _buildFilterChip('stellar_shards', 'Stellar Shards'),
              _buildFilterChip('lumina', 'Lumina'),
            ],
          ),
          const SizedBox(height: 16),
          // Rarity filter
          const Text('Rarity', style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            children: [
              _buildRarityChip('common', 'Common'),
              _buildRarityChip('uncommon', 'Uncommon'),
              _buildRarityChip('rare', 'Rare'),
              _buildRarityChip('epic', 'Epic'),
              _buildRarityChip('legendary', 'Legendary'),
            ],
          ),
          const SizedBox(height: 16),
          // Achievement type filter
          const Text(
            'Achievement Type',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            children: [
              _buildAchievementTypeChip('first_trade', 'First Trade'),
              _buildAchievementTypeChip('level_milestone', 'Level Milestone'),
              _buildAchievementTypeChip(
                'constellation_founder',
                'Constellation Founder',
              ),
              _buildAchievementTypeChip('viral_legend', 'Viral Legend'),
              _buildAchievementTypeChip('trading_master', 'Trading Master'),
            ],
          ),
          const SizedBox(height: 24),
          // Action buttons
          Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              TextButton(
                onPressed: () {
                  Navigator.pop(context);
                },
                child: const Text('Cancel'),
              ),
              const SizedBox(width: 8),
              ElevatedButton(
                onPressed: _applyFilters,
                child: const Text('Apply Filters'),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildFilterChip(String value, String label) {
    final isSelected = _filters['currency'] == value;

    return ChoiceChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (selected) {
        setState(() {
          _filters['currency'] = selected ? value : null;
        });
      },
    );
  }

  Widget _buildRarityChip(String value, String label) {
    final isSelected = _filters['rarity'] == value;

    return ChoiceChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (selected) {
        setState(() {
          _filters['rarity'] = selected ? value : null;
        });
      },
      selectedColor: _getRarityColor(value),
    );
  }

  Widget _buildAchievementTypeChip(String value, String label) {
    final isSelected = _filters['achievementType'] == value;

    return ChoiceChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (selected) {
        setState(() {
          _filters['achievementType'] = selected ? value : null;
        });
      },
    );
  }

  void _applyFilters() {
    // Remove null values
    _filters.removeWhere((key, value) => value == null);
    widget.onFiltersChanged(_filters);
  }

  /// Get color based on rarity
  Color _getRarityColor(String rarity) {
    switch (rarity.toLowerCase()) {
      case 'common':
        return Colors.grey.shade700;
      case 'uncommon':
        return Colors.green.shade700;
      case 'rare':
        return Colors.blue.shade700;
      case 'epic':
        return Colors.purple.shade700;
      case 'legendary':
        return Colors.orange.shade700;
      default:
        return Colors.grey.shade800;
    }
  }
}
