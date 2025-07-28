import 'dart:convert';
import 'package:http/http.dart' as http;

/// Response from the RAG search endpoint
class RagSearchResponse {
  final List<RagSearchResult> results;
  final String query;
  final double maxSimilarity;
  final int resultCount;
  final int processingTimeMs;

  RagSearchResponse({
    required this.results,
    required this.query,
    required this.maxSimilarity,
    required this.resultCount,
    required this.processingTimeMs,
  });

  factory RagSearchResponse.fromJson(Map<String, dynamic> json) {
    return RagSearchResponse(
      results: (json['results'] as List)
          .map((item) => RagSearchResult.fromJson(item))
          .toList(),
      query: json['query'] ?? '',
      maxSimilarity: (json['max_similarity'] ?? 0.0).toDouble(),
      resultCount: json['result_count'] ?? 0,
      processingTimeMs: json['processing_time_ms'] ?? 0,
    );
  }
}

/// Individual search result from RAG backend
class RagSearchResult {
  final String content;
  final String filename;
  final double similarity;
  final Map<String, dynamic> metadata;

  RagSearchResult({
    required this.content,
    required this.filename,
    required this.similarity,
    required this.metadata,
  });

  factory RagSearchResult.fromJson(Map<String, dynamic> json) {
    return RagSearchResult(
      content: json['content'] ?? '',
      filename: json['filename'] ?? '',
      similarity: (json['similarity'] ?? 0.0).toDouble(),
      metadata: json['metadata'] ?? {},
    );
  }
}

/// Exception thrown when RAG API calls fail
class RagApiException implements Exception {
  final String message;
  final int? statusCode;
  final String? details;

  RagApiException(this.message, {this.statusCode, this.details});

  @override
  String toString() {
    return 'RagApiException: $message ${statusCode != null ? '(Status: $statusCode)' : ''}${details != null ? ' - $details' : ''}';
  }
}

/// API client for communicating with AstraTrade RAG backend
class RagApiClient {
  static const String baseUrl = 'http://localhost:8000';
  static const String apiKey = String.fromEnvironment(
    'RAG_API_KEY',
    defaultValue: 'astra_rag_secret_key_2024',
  );
  static const Duration defaultTimeout = Duration(seconds: 10);

  final http.Client _httpClient;

  RagApiClient({http.Client? httpClient}) 
      : _httpClient = httpClient ?? http.Client();

  /// Search the RAG knowledge base with a query
  /// 
  /// Sends a POST request to /search endpoint with the query and returns
  /// relevant documents from the AstraTrade knowledge base.
  Future<RagSearchResponse> search(
    String query, {
    int maxResults = 3,
    double minSimilarity = 0.25,
  }) async {
    final uri = Uri.parse('$baseUrl/search');
    
    final requestBody = {
      'query': query,
      'max_results': maxResults,
      'min_similarity': minSimilarity,
    };

    try {
      final response = await _httpClient
          .post(
            uri,
            headers: {
              'Content-Type': 'application/json',
              'X-API-Key': apiKey,
              'User-Agent': 'AstraTrade-Flutter/1.0.0',
            },
            body: json.encode(requestBody),
          )
          .timeout(defaultTimeout);

      if (response.statusCode == 200) {
        final Map<String, dynamic> responseData = json.decode(response.body);
        return RagSearchResponse.fromJson(responseData);
      } else {
        throw RagApiException(
          'RAG search failed',
          statusCode: response.statusCode,
          details: response.body,
        );
      }
    } catch (e) {
      if (e is RagApiException) rethrow;
      throw RagApiException('Network error during RAG search: ${e.toString()}');
    }
  }

  /// Perform a Claude-optimized search for trading scenarios
  /// 
  /// This method constructs queries specifically for trading simulations
  /// and game mechanics, using the RAG backend to provide realistic
  /// trading scenarios and outcomes.
  Future<RagSearchResponse> searchTradingScenario(
    String tradeType, {
    String asset = 'ETH',
    String direction = 'long',
    double amount = 100.0,
  }) async {
    final query = 'Simulate $tradeType $direction position on $asset with \$${amount.toStringAsFixed(2)} - provide realistic trading outcome with profit/loss percentage and cosmic-themed result message';
    
    return await search(
      query,
      maxResults: 2,
      minSimilarity: 0.15, // Lower threshold for trading scenarios
    );
  }

  /// Get market sentiment and cosmic forecast
  /// 
  /// Queries the RAG for current market analysis and translates
  /// it into cosmic-themed forecasts for the game UI.
  Future<RagSearchResponse> getCosmicForecast() async {
    final query = 'Current crypto market sentiment analysis and price prediction for major assets like ETH BTC SOL - translate to cosmic gaming metaphors';
    
    return await search(
      query,
      maxResults: 1,
      minSimilarity: 0.20,
    );
  }

  /// Health check to verify RAG backend connectivity
  Future<bool> healthCheck() async {
    try {
      final uri = Uri.parse('$baseUrl/health');
      final response = await _httpClient
          .get(uri)
          .timeout(const Duration(seconds: 2)); // Reduced timeout
      
      return response.statusCode == 200;
    } catch (e) {
      // Silently fail without logging to reduce console noise
      return false;
    }
  }

  /// Close the HTTP client
  void dispose() {
    _httpClient.close();
  }
}