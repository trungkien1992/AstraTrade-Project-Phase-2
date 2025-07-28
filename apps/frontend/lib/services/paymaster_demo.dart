import 'dart:developer';
import 'package:flutter/foundation.dart';
import 'paymaster_service.dart';

/// Demo integration for AVNU paymaster - tests real functionality
class PaymasterDemo {
  static final PaymasterService _paymaster = PaymasterService.instance;
  
  /// Test complete paymaster workflow for real demo
  static Future<bool> testRealDemo() async {
    try {
      debugPrint('🚀 Starting AVNU Paymaster Demo Test...');
      
      // Initialize paymaster service
      await _paymaster.initialize();
      debugPrint('✅ Paymaster initialized');
      
      // Test user address (demo address)
      const testUserAddress = '0x05f1ecb9f46b5b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b';
      
      // 1. Check user eligibility
      final eligibility = await _paymaster.checkUserEligibility(testUserAddress);
      debugPrint('✅ User eligibility: ${eligibility.isEligible}, Daily limit: ${eligibility.dailyLimit} ETH');
      
      if (!eligibility.isEligible) {
        debugPrint('❌ User not eligible for gasless transactions');
        return false;
      }
      
      // 2. Check paymaster service status  
      final status = await _paymaster.getPaymasterStatus();
      debugPrint('✅ Paymaster status: Active=${status.isActive}, Balance=${status.balance} ETH');
      
      if (!status.isActive) {
        debugPrint('❌ Paymaster service not active');
        return false;
      }
      
      // 3. Test transaction sponsorship request
      final demoTradeCalls = [
        {
          'contract_address': '0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7', // ETH
          'entrypoint': 'transfer',
          'calldata': ['0x123', '1000000000000000000'], // 1 ETH transfer
        }
      ];
      
      const estimatedGas = 0.005; // 0.005 ETH
      
      // 4. Validate transaction
      final isValid = await _paymaster.validateTransaction(
        userAddress: testUserAddress,
        calls: demoTradeCalls,
        estimatedGas: estimatedGas,
      );
      debugPrint('✅ Transaction validation: $isValid');
      
      if (!isValid) {
        debugPrint('❌ Transaction validation failed');
        return false;
      }
      
      // 5. Check sponsorship capability
      final canSponsor = await _paymaster.canSponsorTransaction(testUserAddress, estimatedGas);
      debugPrint('✅ Can sponsor transaction: $canSponsor');
      
      if (!canSponsor) {
        debugPrint('❌ Cannot sponsor transaction (limits exceeded)');
        return false;
      }
      
      // 6. Request sponsorship from AVNU
      final sponsorship = await _paymaster.requestSponsorship(
        userAddress: testUserAddress,
        calls: demoTradeCalls,
        estimatedGas: estimatedGas,
        metadata: {
          'client': 'astratrade_demo',
          'version': '1.0.0',
          'trade_type': 'spot',
        },
      );
      debugPrint('✅ Sponsorship request: Approved=${sponsorship.isApproved}, ID=${sponsorship.sponsorshipId}');
      
      if (!sponsorship.isApproved) {
        debugPrint('❌ Sponsorship request denied');
        return false;
      }
      
      // 7. Simulate transaction execution (would require real user signature in production)
      final mockUserSignature = '0xdemo_user_signature_${DateTime.now().millisecondsSinceEpoch}';
      
      final txHash = await _paymaster.executeWithSponsorship(
        sponsorship: sponsorship,
        calls: demoTradeCalls,
        userAddress: testUserAddress,
        userSignature: mockUserSignature,
      );
      debugPrint('✅ Transaction executed with sponsorship: $txHash');
      
      // 8. Verify transaction hash format
      if (!txHash.startsWith('0x') || txHash.length < 10) {
        debugPrint('❌ Invalid transaction hash format');
        return false;
      }
      
      debugPrint('🎉 AVNU Paymaster Demo Test PASSED! All functionality working.');
      debugPrint('📊 Summary:');
      debugPrint('   - User eligibility: ✅');
      debugPrint('   - Service status: ✅');
      debugPrint('   - Transaction validation: ✅');
      debugPrint('   - Sponsorship approval: ✅');
      debugPrint('   - Transaction execution: ✅');
      debugPrint('   - Transaction hash: $txHash');
      
      return true;
      
    } catch (e) {
      log('❌ Paymaster demo test failed: $e');
      return false;
    }
  }
  
  /// Test specific AVNU API endpoints for real demo readiness
  static Future<Map<String, bool>> testAPIEndpoints() async {
    final results = <String, bool>{};
    
    try {
      // Test eligibility endpoint
      try {
        await _paymaster.checkUserEligibility('0x123');
        results['eligibility'] = true;
      } catch (e) {
        results['eligibility'] = false;
        debugPrint('❌ Eligibility endpoint failed: $e');
      }
      
      // Test status endpoint
      try {
        await _paymaster.getPaymasterStatus();
        results['status'] = true;
      } catch (e) {
        results['status'] = false;
        debugPrint('❌ Status endpoint failed: $e');
      }
      
      // Test sponsorship endpoint
      try {
        await _paymaster.requestSponsorship(
          userAddress: '0x123',
          calls: [{'test': 'call'}],
          estimatedGas: 0.001,
        );
        results['sponsorship'] = true;
      } catch (e) {
        results['sponsorship'] = false;
        debugPrint('❌ Sponsorship endpoint failed: $e');
      }
      
    } catch (e) {
      log('Error testing API endpoints: $e');
    }
    
    return results;
  }
  
  /// Get demo readiness score
  static Future<DemoReadinessReport> getDemoReadiness() async {
    try {
      final apiTests = await testAPIEndpoints();
      final fullTest = await testRealDemo();
      
      final passed = apiTests.values.where((v) => v).length;
      final total = apiTests.length;
      final score = (passed / total * 100).round();
      
      return DemoReadinessReport(
        overallScore: score,
        isReady: fullTest && score >= 75,
        apiEndpoints: apiTests,
        fullWorkflowTest: fullTest,
        recommendations: _generateRecommendations(apiTests, fullTest),
      );
      
    } catch (e) {
      return DemoReadinessReport(
        overallScore: 0,
        isReady: false,
        apiEndpoints: {},
        fullWorkflowTest: false,
        recommendations: ['Critical error: ${e.toString()}'],
      );
    }
  }
  
  static List<String> _generateRecommendations(Map<String, bool> apiTests, bool fullTest) {
    final recommendations = <String>[];
    
    if (!fullTest) {
      recommendations.add('🔧 Full workflow test failed - check integration');
    }
    
    apiTests.forEach((endpoint, passed) {
      if (!passed) {
        recommendations.add('🔧 Fix $endpoint API endpoint connectivity');
      }
    });
    
    if (recommendations.isEmpty) {
      recommendations.add('🎉 Paymaster is ready for real demo!');
      recommendations.add('💡 All AVNU endpoints responding correctly');
      recommendations.add('🚀 Gasless transactions fully functional');
    }
    
    return recommendations;
  }
}

/// Report on demo readiness for paymaster
class DemoReadinessReport {
  final int overallScore;
  final bool isReady;
  final Map<String, bool> apiEndpoints;
  final bool fullWorkflowTest;
  final List<String> recommendations;
  
  DemoReadinessReport({
    required this.overallScore,
    required this.isReady,
    required this.apiEndpoints,
    required this.fullWorkflowTest,
    required this.recommendations,
  });
  
  @override
  String toString() {
    final buffer = StringBuffer();
    buffer.writeln('🎯 AVNU Paymaster Demo Readiness Report');
    buffer.writeln('════════════════════════════════════════');
    buffer.writeln('Overall Score: $overallScore/100');
    buffer.writeln('Demo Ready: ${isReady ? "✅ YES" : "❌ NO"}');
    buffer.writeln('');
    buffer.writeln('API Endpoint Tests:');
    apiEndpoints.forEach((endpoint, passed) {
      buffer.writeln('  ${passed ? "✅" : "❌"} $endpoint');
    });
    buffer.writeln('');
    buffer.writeln('Full Workflow Test: ${fullWorkflowTest ? "✅ PASS" : "❌ FAIL"}');
    buffer.writeln('');
    buffer.writeln('Recommendations:');
    for (final rec in recommendations) {
      buffer.writeln('  $rec');
    }
    buffer.writeln('════════════════════════════════════════');
    return buffer.toString();
  }
}