import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/nft_providers.dart';
import '../widgets/nft_marketplace_item_widget.dart';
import '../widgets/nft_filter_widget.dart';

/// Screen to display NFT marketplace
class NFTMarketplaceScreen extends ConsumerStatefulWidget {
  const NFTMarketplaceScreen({super.key});

  @override
  ConsumerState<NFTMarketplaceScreen> createState() => _NFTMarketplaceScreenState();
}

class _NFTMarketplaceScreenState extends ConsumerState<NFTMarketplaceScreen> {
  final Map<String, dynamic> _filters = {
    'currency': 'stellar_shards',
    'sortBy': 'listed_at',
    'sortOrder': 'desc',
  };

  @override
  Widget build(BuildContext context) {
    final marketplaceAsync = ref.watch(nftMarketplaceProvider(_filters));

    return Scaffold(
      appBar: AppBar(
        title: const Text('NFT Marketplace'),
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: _showFilterOptions,
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.invalidate(nftMarketplaceProvider(_filters)),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(nftMarketplaceProvider(_filters));
        },
        child: marketplaceAsync.when(
          data: (items) => _buildMarketplaceContent(context, items),
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, stack) => Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.error, size: 48, color: Colors.red),
                const SizedBox(height: 16),
                Text('Error loading marketplace: $error'),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () => ref.invalidate(nftMarketplaceProvider(_filters)),
                  child: const Text('Retry'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildMarketplaceContent(BuildContext context, List<NFTMarketplaceItem> items) {
    if (items.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.storefront_outlined, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text(
              'No NFTs listed in the marketplace',
              style: TextStyle(fontSize: 18),
            ),
            SizedBox(height: 8),
            Text(
              'Check back later for new listings',
              style: TextStyle(color: Colors.grey),
            ),
          ],
        ),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Filter summary
          _buildFilterSummary(),
          
          const SizedBox(height: 16),
          
          // Marketplace items
          GridView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
              childAspectRatio: 0.8,
            ),
            itemCount: items.length,
            itemBuilder: (context, index) {
              return NFTMarketplaceItemWidget(item: items[index]);
            },
          ),
        ],
      ),
    );
  }

  Widget _buildFilterSummary() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey.shade800,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          const Icon(Icons.filter_alt, size: 20),
          const SizedBox(width: 8),
          Text(
            'Filtering by: ${_filters['currency']}',
            style: const TextStyle(fontSize: 14),
          ),
          const Spacer(),
          TextButton(
            onPressed: _clearFilters,
            child: const Text('Clear'),
          ),
        ],
      ),
    );
  }

  void _showFilterOptions() {
    showModalBottomSheet(
      context: context,
      builder: (context) {
        return NFTFilterWidget(
          initialFilters: _filters,
          onFiltersChanged: (newFilters) {
            setState(() {
              _filters.addAll(newFilters);
            });
            Navigator.pop(context);
          },
        );
      },
    );
  }

  void _clearFilters() {
    setState(() {
      _filters.clear();
      _filters.addAll({
        'currency': 'stellar_shards',
        'sortBy': 'listed_at',
        'sortOrder': 'desc',
      });
    });
  }
}