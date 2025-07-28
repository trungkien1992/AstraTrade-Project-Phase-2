#[starknet::contract]
mod AstraTradePaymaster {
    use starknet::ContractAddress;

    #[storage]
    struct Storage {
        owner: ContractAddress,
        dummy_value: u256,
    }

    #[constructor]
    fn constructor(ref self: ContractState, owner: ContractAddress) {
        self.owner.write(owner);
        self.dummy_value.write(42_u256);
    }

    #[abi(embed_v0)]
    impl PaymasterImpl of PaymasterTrait<ContractState> {
        fn get_dummy(self: @ContractState) -> u256 {
            self.dummy_value.read()
        }

        fn test_emit(ref self: ContractState, user: ContractAddress, value: u256) {
            // Emit event for testing
            self.emit(TestEvent { user, value });
        }
    }

    #[starknet::interface]
    trait PaymasterTrait<TContractState> {
        fn get_dummy(self: @TContractState) -> u256;
        fn test_emit(ref self: TContractState, user: ContractAddress, value: u256);
    }

    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        TestEvent: TestEvent,
    }

    #[derive(Drop, starknet::Event)]
    struct TestEvent {
        user: ContractAddress,
        value: u256,
    }
}