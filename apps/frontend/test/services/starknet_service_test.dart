import 'package:flutter_test/flutter_test.dart';
import 'package:astratrade_app/services/starknet_service.dart';

void main() {
  group('StarknetService', () {
    test('can create instance', () {
      final service = StarknetService();
      expect(service, isNotNull);
    });

    test('can get ETH balance', () async {
      final service = StarknetService();
      // Using a known testnet address for testing
      final balance = await service.getEthBalance(
        '0x05715B600c38f3BFA539281865Cf8d7B9fE998D79a2CF181c70eFFCb182752F7',
      );
      // Should return a numeric value (could be 0 if account has no ETH)
      expect(balance, isA<double>());
    });

    test('can check if account is deployed', () async {
      final service = StarknetService();
      final isDeployed = await service.isAccountDeployed(
        '0x05715B600c38f3BFA539281865Cf8d7B9fE998D79a2CF181c70eFFCb182752F7',
      );
      // Should return a boolean value
      expect(isDeployed, isA<bool>());
    });
  });
}
