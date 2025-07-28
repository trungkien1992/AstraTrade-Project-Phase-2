import 'package:flutter_test/flutter_test.dart';
import 'package:astratrade_frontend/services/paymaster_service.dart';

void main() {
  test('Complete AVNU Paymaster Mobile Integration Test', () async {
    // Initialize service
    final paymaster = PaymasterService.instance;
    await paymaster.initialize();

    // Test Data
    const testAddress = "0x123456789abcdef";
    final testCalls = [
      {"contract_address": "0xcontract1", "entrypoint": "transfer", "calldata": ["0x123", "0x456"]}
    ];

    // 1. Test Signature Generation
    final typedData = await paymaster.buildTypedData(
      userAddress: testAddress,
      calls: testCalls,
    );

    final signature = await paymaster.generateMobileNativeSignature(
      typedData: typedData,
    );
    print("✅ Generated Mobile Signature:  $signature");

    // 2. Validate Signature Format
    if (!paymaster._isValidMobileSignature(signature)) {
      throw Exception("Generated signature failed validation");
    }
    print("✅ Signature Validated" );

    // 3. Test Transaction Execution
    final sponsorship = AVNUSponsorshipResponse(
      isApproved: true,
      sponsorshipId: "test_${DateTime.now().millisecondsSinceEpoch}",
      paymasterSignature: "0xmockSig",
      maxFee: 0.01,
      validUntil: DateTime.now().add(Duration(minutes: 10)),
      paymasterCalldata: ["0x1", "0x2"],
    );

    final txHash = await paymaster.executeWithSponsorship(
      sponsorship: sponsorship,
      calls: testCalls,
      userAddress: testAddress,
      userSignature: signature,
    );
    print("✅ Transaction Executed:  $txHash");

    // 4. Verify Mock Transaction
    if (!txHash.contains("mock") && !txHash.startsWith("0x")) {
      throw Exception("Unexpected transaction hash format");
    }
    print("✅ Test Completed Successfully" );
  });
 }
