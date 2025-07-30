#[starknet::contract]
mod AstraTradeExchange {
    use starknet::{get_caller_address, ContractAddress};

    #[storage]
    struct Storage {
        owner: ContractAddress,
        is_paused: bool,
        // Simplified storage for demonstration
        balances: starknet::storage::Map<(ContractAddress, ContractAddress), u256>,
        orders: starknet::storage::Map<u256, Order>,
        next_order_id: u256,
    }

    #[derive(Drop, starknet::Store, Copy, Serde)]
    struct Order {
        id: u256,
        user: ContractAddress,
        market: felt252,
        side: u8, // 0 for Buy, 1 for Sell
        order_type: u8, // 0 for Market, 1 for Limit
        amount: u256,
        price: u256,
        filled: u256,
        status: u8, // 0 for Open, 1 for Partially Filled, 2 for Filled, 3 for Cancelled
    }

    #[constructor]
    fn constructor(ref self: ContractState, owner: ContractAddress) {
        self.owner.write(owner);
        self.is_paused.write(false);
        self.next_order_id.write(1_u256);
    }

    #[abi(embed_v0)]
    impl ExchangeImpl of ExchangeTrait<ContractState> {
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

        fn deposit(ref self: ContractState, token: ContractAddress, amount: u256) {
            assert(!self.is_paused.read(), 'Paused');
            // In a real implementation, this would interact with a token contract
            // For now, we'll just update internal balances
            let caller = get_caller_address();
            let current_balance = self.balances.read((caller, token));
            self.balances.write((caller, token), current_balance + amount);
        }

        fn withdraw(ref self: ContractState, token: ContractAddress, amount: u256) {
            assert(!self.is_paused.read(), 'Paused');
            let caller = get_caller_address();
            let current_balance = self.balances.read((caller, token));
            assert(current_balance >= amount, 'Insufficient');
            self.balances.write((caller, token), current_balance - amount);
        }

        fn place_order(
            ref self: ContractState,
            market: felt252,
            side: u8,  // 0 for Buy, 1 for Sell
            order_type: u8,  // 0 for Market, 1 for Limit
            amount: u256,
            price: u256
        ) -> u256 {
            assert(!self.is_paused.read(), 'Paused');
            assert(side == 0 || side == 1, 'Invalid side');
            assert(order_type == 0 || order_type == 1, 'Invalid type');
            assert(amount > 0, 'Zero amount');
            
            let caller = get_caller_address();
            let order_id = self.next_order_id.read();
            self.next_order_id.write(order_id + 1_u256);
            
            let order = Order {
                id: order_id,
                user: caller,
                market: market,
                side: side,
                order_type: order_type,
                amount: amount,
                price: price,
                filled: 0_u256,
                status: 0_u8, // Open
            };
            
            self.orders.write(order_id, order);
            order_id
        }

        fn cancel_order(ref self: ContractState, order_id: u256) {
            assert(!self.is_paused.read(), 'Paused');
            let caller = get_caller_address();
            let mut order = self.orders.read(order_id);
            assert(order.user == caller, 'Not owner');
            assert(order.status == 0 || order.status == 1, 'Not cancelable');
            
            order.status = 3_u8; // Cancelled
            self.orders.write(order_id, order);
        }

        fn get_order(self: @ContractState, order_id: u256) -> Order {
            self.orders.read(order_id)
        }
    }

    #[starknet::interface]
    trait ExchangeTrait<TContractState> {
        fn get_owner(self: @TContractState) -> ContractAddress;
        fn is_paused(self: @TContractState) -> bool;
        fn pause_contract(ref self: TContractState);
        fn unpause_contract(ref self: TContractState);
        fn get_balance(self: @TContractState, user: ContractAddress, token: ContractAddress) -> u256;
        fn deposit(ref self: TContractState, token: ContractAddress, amount: u256);
        fn withdraw(ref self: TContractState, token: ContractAddress, amount: u256);
        fn place_order(
            ref self: TContractState,
            market: felt252,
            side: u8,  // 0 for Buy, 1 for Sell
            order_type: u8,  // 0 for Market, 1 for Limit
            amount: u256,
            price: u256
        ) -> u256;
        fn cancel_order(ref self: TContractState, order_id: u256);
        fn get_order(self: @TContractState, order_id: u256) -> Order;
    }
}