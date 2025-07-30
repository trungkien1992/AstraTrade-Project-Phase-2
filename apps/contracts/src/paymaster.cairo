#[starknet::contract]
mod AstraTradePaymaster {
    use starknet::{get_caller_address, ContractAddress};

    #[storage]
    struct Storage {
        owner: ContractAddress,
        sponsor_funds: starknet::storage::Map<ContractAddress, u256>,
    }

    #[constructor]
    fn constructor(ref self: ContractState, owner: ContractAddress) {
        self.owner.write(owner);
    }

    #[abi(embed_v0)]
    impl PaymasterImpl of PaymasterTrait<ContractState> {
        fn get_owner(self: @ContractState) -> ContractAddress {
            self.owner.read()
        }

        fn sponsor_transaction(ref self: ContractState, user: ContractAddress, amount: u256) {
            // Gasless transaction sponsorship logic
            assert(get_caller_address() == self.owner.read(), 'Unauthorized');
            let current_funds = self.sponsor_funds.read(user);
            self.sponsor_funds.write(user, current_funds + amount);
        }

        fn get_sponsor_funds(self: @ContractState, user: ContractAddress) -> u256 {
            self.sponsor_funds.read(user)
        }

        fn use_sponsor_funds(ref self: ContractState, user: ContractAddress, amount: u256) {
            let current_funds = self.sponsor_funds.read(user);
            assert(current_funds >= amount, 'Insufficient funds');
            self.sponsor_funds.write(user, current_funds - amount);
        }
    }

    #[starknet::interface]
    trait PaymasterTrait<TContractState> {
        fn get_owner(self: @TContractState) -> ContractAddress;
        fn sponsor_transaction(ref self: TContractState, user: ContractAddress, amount: u256);
        fn get_sponsor_funds(self: @TContractState, user: ContractAddress) -> u256;
        fn use_sponsor_funds(ref self: TContractState, user: ContractAddress, amount: u256);
    }
}