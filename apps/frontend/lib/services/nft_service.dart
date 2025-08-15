import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../config/app_config.dart';
import '../models/nft_models.dart';

/// Service for managing NFT functionality
class NFTService {
  static final NFTService _instance = NFTService._internal();
  factory NFTService() => _instance;
  NFTService._internal();

  final String _baseUrl = '${AppConfig.apiUrl}/nft';

  /// Mint a Genesis NFT for an achievement
  Future<GenesisNFT> mintGenesisNFT({
    required String achievementType,
    required Map<String, dynamic> milestoneData,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/genesis/mint'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'achievement_type': achievementType,
          'milestone_data': milestoneData,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return GenesisNFT.fromJson(data);
      } else {
        throw Exception('Failed to mint NFT: ${response.body}');
      }
    } catch (e) {
      if (kDebugMode) {
        print('Error minting NFT: $e');
      }
      rethrow;
    }
  }

  /// Get user's NFT collection
  Future<NFTCollection> getUserNFTCollection(int userId) async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/genesis/collection/$userId'),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return NFTCollection.fromJson(data);
      } else {
        throw Exception('Failed to get NFT collection: ${response.body}');
      }
    } catch (e) {
      if (kDebugMode) {
        print('Error getting NFT collection: $e');
      }
      rethrow;
    }
  }

  /// Get eligible achievements for Genesis NFT minting
  Future<List<EligibleAchievement>> getEligibleAchievements() async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/genesis/eligible-achievements'),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final achievements = (data['eligible_achievements'] as List)
            .map((item) => EligibleAchievement.fromJson(item))
            .toList();
        return achievements;
      } else {
        throw Exception(
          'Failed to get eligible achievements: ${response.body}',
        );
      }
    } catch (e) {
      if (kDebugMode) {
        print('Error getting eligible achievements: $e');
      }
      rethrow;
    }
  }

  /// Get NFT marketplace listings
  Future<List<NFTMarketplaceItem>> getMarketplaceListings({
    String? rarity,
    String? achievementType,
    double? minPrice,
    double? maxPrice,
    String currency = 'stellar_shards',
    String sortBy = 'listed_at',
    String sortOrder = 'desc',
    int limit = 20,
  }) async {
    try {
      final queryParams = {
        'limit': limit.toString(),
        'currency': currency,
        'sort_by': sortBy,
        'sort_order': sortOrder,
        if (rarity != null) 'rarity': rarity,
        if (achievementType != null) 'achievement_type': achievementType,
        if (minPrice != null) 'min_price': minPrice.toString(),
        if (maxPrice != null) 'max_price': maxPrice.toString(),
      };

      final uri = Uri.parse(
        '$_baseUrl/marketplace',
      ).replace(queryParameters: queryParams);
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as List;
        return data.map((item) => NFTMarketplaceItem.fromJson(item)).toList();
      } else {
        throw Exception('Failed to get marketplace listings: ${response.body}');
      }
    } catch (e) {
      if (kDebugMode) {
        print('Error getting marketplace listings: $e');
      }
      rethrow;
    }
  }

  /// List an NFT for sale
  Future<Map<String, dynamic>> listNFTForSale({
    required String nftId,
    required double price,
    required String currency,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/marketplace/list/$nftId'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'price': price, 'currency': currency}),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to list NFT: ${response.body}');
      }
    } catch (e) {
      if (kDebugMode) {
        print('Error listing NFT: $e');
      }
      rethrow;
    }
  }

  /// Buy an NFT from the marketplace
  Future<Map<String, dynamic>> buyNFTFromMarketplace(String listingId) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/marketplace/buy/$listingId'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to buy NFT: ${response.body}');
      }
    } catch (e) {
      if (kDebugMode) {
        print('Error buying NFT: $e');
      }
      rethrow;
    }
  }

  /// Create shareable content for an NFT
  Future<Map<String, dynamic>> createShareableNFTContent({
    required String nftId,
    required List<String> sharePlatforms,
    String? customMessage,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/share/$nftId'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'nft_id': nftId,
          'share_platforms': sharePlatforms,
          'custom_message': customMessage,
        }),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to create shareable content: ${response.body}');
      }
    } catch (e) {
      if (kDebugMode) {
        print('Error creating shareable content: $e');
      }
      rethrow;
    }
  }

  /// Get global NFT statistics
  Future<Map<String, dynamic>> getGlobalNFTStats() async {
    try {
      final response = await http.get(Uri.parse('$_baseUrl/stats/global'));

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to get global NFT stats: ${response.body}');
      }
    } catch (e) {
      if (kDebugMode) {
        print('Error getting global NFT stats: $e');
      }
      rethrow;
    }
  }
}
