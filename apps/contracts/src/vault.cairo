#[starknet::contract]
mod AstraTradeVault {
    use starknet::{get_caller_address, ContractAddress};

    #[storage]
    struct Storage {
        owner: ContractAddress,
        is_paused: bool,
        // Simplified storage for demonstration
        balances: starknet::storage::Map<(ContractAddress, ContractAddress), u256>,
        total_deposits: starknet::storage::Map<ContractAddress, u256>,
    }

    #[constructor]
    fn constructor(ref self: ContractState, owner: ContractAddress) {
        self.owner.write(owner);
        self.is_paused.write(false);
    }

    #[abi(embed_v0)]
    impl VaultImpl of VaultTrait<ContractState> {
        fn get_owner(self: @ContractState) -> ContractAddress {
            self.owner.read()
        }

        fn is_paused(self: @ContractState) -> bool {
            self.is_paused.read()
        }

        fn pause_contract(ref self: ContractState) {
            assert(get_caller_address() == self.owner.read(), 'Unauthorized');
            self.is_paused.write(true);
        }

        fn unpause_contract(ref self: ContractState) {
            assert(get_caller_address() == self.owner.read(), 'Unauthorized');
            self.is_paused.write(false);
        }

        fn get_balance(self: @ContractState, user: ContractAddress, token: ContractAddress) -> u256 {
            self.balances.read((user, token))
        }

        fn get_total_deposits(self: @ContractState, token: ContractAddress) -> u256 {
            self.total_deposits.read(token)
        }

        fn deposit(ref self: ContractState, token: ContractAddress, amount: u256) {
            assert(!self.is_paused.read(), 'Paused');
            
            // In a real implementation, this would interact with a token contract
            // For now, we'll just update internal balances
            let caller = get_caller_address();
            let current_balance = self.balances.read((caller, token));
            self.balances.write((caller, token), current_balance + amount);
            
            let current_total = self.total_deposits.read(token);
            self.total_deposits.write(token, current_total + amount);
        }

        fn withdraw(ref self: ContractState, token: ContractAddress, amount: u256) {
            assert(!self.is_paused.read(), 'Paused');
            
            let caller = get_caller_address();
            let current_balance = self.balances.read((caller, token));
            assert(current_balance >= amount, 'Insufficient');
            
            // Update balances
            self.balances.write((caller, token), current_balance - amount);
            
            let current_total = self.total_deposits.read(token);
            self.total_deposits.write(token, current_total - amount);
        }
    }

    #[starknet::interface]
    trait VaultTrait<TContractState> {
        fn get_owner(self: @TContractState) -> ContractAddress;
        fn is_paused(self: @TContractState) -> bool;
        fn pause_contract(ref self: TContractState);
        fn unpause_contract(ref self: TContractState);
        fn get_balance(self: @TContractState, user: ContractAddress, token: ContractAddress) -> u256;
        fn get_total_deposits(self: @TContractState, token: ContractAddress) -> u256;
        fn deposit(ref self: TContractState, token: ContractAddress, amount: u256);
        fn withdraw(ref self: TContractState, token: ContractAddress, amount: u256);
    }
}