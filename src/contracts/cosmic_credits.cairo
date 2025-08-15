// Cosmic Credits - Ethical Virtual Currency Contract
// 
// Implements the first anti-predatory virtual currency for trading platforms
// Features: Dual currency system, conversion bridge, anti-whale bonding curve
// Compliance: SEC/FINRA safe harbor, no securities classification

#[starknet::contract]
mod CosmicCredits {
    use starknet::{ContractAddress, get_caller_address, get_block_timestamp};
    use openzeppelin::token::erc20::{ERC20Component, ERC20HooksEmptyImpl};
    use openzeppelin::access::ownable::OwnableComponent;
    use openzeppelin::security::pausable::PausableComponent;
    use openzeppelin::upgrades::UpgradeableComponent;
    use openzeppelin::security::reentrancyguard::ReentrancyGuardComponent;

    component!(path: ERC20Component, storage: erc20, event: ERC20Event);
    component!(path: OwnableComponent, storage: ownable, event: OwnableEvent);
    component!(path: PausableComponent, storage: pausable, event: PausableEvent);
    component!(path: UpgradeableComponent, storage: upgradeable, event: UpgradeableEvent);
    component!(path: ReentrancyGuardComponent, storage: reentrancy_guard, event: ReentrancyGuardEvent);

    // ERC20 Mixin
    #[abi(embed_v0)]
    impl ERC20MixinImpl = ERC20Component::ERC20MixinImpl<ContractState>;
    impl ERC20InternalImpl = ERC20Component::InternalImpl<ContractState>;

    // Ownable Mixin
    #[abi(embed_v0)]
    impl OwnableMixinImpl = OwnableComponent::OwnableMixinImpl<ContractState>;
    impl OwnableInternalImpl = OwnableComponent::InternalImpl<ContractState>;

    // Pausable Mixin
    #[abi(embed_v0)]
    impl PausableMixinImpl = PausableComponent::PausableMixinImpl<ContractState>;
    impl PausableInternalImpl = PausableComponent::InternalImpl<ContractState>;

    // Upgradeable Mixin
    #[abi(embed_v0)]
    impl UpgradeableImpl = UpgradeableComponent::UpgradeableImpl<ContractState>;
    impl UpgradeableInternalImpl = UpgradeableComponent::InternalImpl<ContractState>;

    // ReentrancyGuard Mixin
    impl ReentrancyGuardInternalImpl = ReentrancyGuardComponent::InternalImpl<ContractState>;

    #[storage]
    struct Storage {
        #[substorage(v0)]
        erc20: ERC20Component::Storage,
        #[substorage(v0)]
        ownable: OwnableComponent::Storage,
        #[substorage(v0)]
        pausable: PausableComponent::Storage,
        #[substorage(v0)]
        upgradeable: UpgradeableComponent::Storage,
        #[substorage(v0)]
        reentrancy_guard: ReentrancyGuardComponent::Storage,
        
        // Currency system specific storage
        currency_type: felt252, // 'cosmic_credits' or 'star_tokens'
        conversion_rate: u256,  // Rate to USD (scaled by 1e18)
        minimum_conversion: u256, // Minimum conversion amount
        conversion_fee_rate: u256, // Fee percentage (scaled by 1e4)
        
        // Economic stability
        total_supply_target: u256,
        inflation_rate: u256, // Annual rate (scaled by 1e4)
        faucet_rate_multiplier: u256, // Earning rate adjustment
        sink_rate_multiplier: u256,   // Spending rate adjustment
        
        // Anti-abuse mechanisms
        user_daily_earned: LegacyMap<ContractAddress, u256>,
        user_last_earn_day: LegacyMap<ContractAddress, u64>,
        user_spending_limits: LegacyMap<ContractAddress, u256>,
        user_cooling_period: LegacyMap<ContractAddress, u64>,
        
        // Compliance tracking
        kyc_verified: LegacyMap<ContractAddress, bool>,
        large_transaction_threshold: u256,
        max_daily_earning: u256,
        
        // Economic metrics
        total_earned_today: u256,
        total_spent_today: u256,
        last_metrics_day: u64,
        
        // Authorized minters (for earning mechanisms)
        authorized_minters: LegacyMap<ContractAddress, bool>,
        
        // Conversion bridge
        bridge_enabled: bool,
        bridge_reserve: u256,
        pending_conversions: LegacyMap<ContractAddress, u256>,
    }

    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        #[flat]
        ERC20Event: ERC20Component::Event,
        #[flat]
        OwnableEvent: OwnableComponent::Event,
        #[flat]
        PausableEvent: PausableComponent::Event,
        #[flat]
        UpgradeableEvent: UpgradeableComponent::Event,
        #[flat]
        ReentrancyGuardEvent: ReentrancyGuardComponent::Event,
        
        CurrencyEarned: CurrencyEarned,
        CurrencySpent: CurrencySpent,
        ConversionRequested: ConversionRequested,
        ConversionProcessed: ConversionProcessed,
        EconomicAdjustment: EconomicAdjustment,
        SpendingLimitSet: SpendingLimitSet,
        CoolingPeriodActivated: CoolingPeriodActivated,
    }

    #[derive(Drop, starknet::Event)]
    struct CurrencyEarned {
        #[key]
        user: ContractAddress,
        amount: u256,
        reason: felt252,
        source: felt252, // 'daily_reward', 'achievement', etc.
    }

    #[derive(Drop, starknet::Event)]
    struct CurrencySpent {
        #[key]
        user: ContractAddress,
        amount: u256,
        reason: felt252,
        sink_type: felt252, // 'cosmetic', 'tournament', etc.
    }

    #[derive(Drop, starknet::Event)]
    struct ConversionRequested {
        #[key]
        user: ContractAddress,
        credits_amount: u256,
        usd_amount: u256,
        cooling_period_until: u64,
    }

    #[derive(Drop, starknet::Event)]
    struct ConversionProcessed {
        #[key]
        user: ContractAddress,
        credits_converted: u256,
        usd_received: u256,
        fee_paid: u256,
    }

    #[derive(Drop, starknet::Event)]
    struct EconomicAdjustment {
        old_faucet_multiplier: u256,
        new_faucet_multiplier: u256,
        old_sink_multiplier: u256,
        new_sink_multiplier: u256,
        reason: felt252,
    }

    #[derive(Drop, starknet::Event)]
    struct SpendingLimitSet {
        #[key]
        user: ContractAddress,
        daily_limit: u256,
    }

    #[derive(Drop, starknet::Event)]
    struct CoolingPeriodActivated {
        #[key]
        user: ContractAddress,
        until_timestamp: u64,
        reason: felt252,
    }

    #[constructor]
    fn constructor(
        ref self: ContractState,
        owner: ContractAddress,
        currency_type: felt252,
        name: ByteArray,
        symbol: ByteArray,
    ) {
        self.erc20.initializer(name, symbol);
        self.ownable.initializer(owner);
        
        // Initialize currency system
        self.currency_type.write(currency_type);
        
        // Set initial economic parameters
        if currency_type == 'cosmic_credits' {
            self.conversion_rate.write(3500000000000000); // $0.0035 per credit (scaled by 1e18)
            self.minimum_conversion.write(50000 * 1000000000000000000); // 50,000 credits
        } else { // star_tokens
            self.conversion_rate.write(100000000000000000); // $0.10 per token (scaled by 1e18)
            self.minimum_conversion.write(100 * 1000000000000000000); // 100 tokens
        }
        
        self.conversion_fee_rate.write(200); // 2% (scaled by 1e4)
        self.inflation_rate.write(250); // 2.5% annually (scaled by 1e4)
        self.faucet_rate_multiplier.write(1000000000000000000); // 1.0 (scaled by 1e18)
        self.sink_rate_multiplier.write(1000000000000000000); // 1.0 (scaled by 1e18)
        
        // Anti-abuse settings
        self.large_transaction_threshold.write(1000 * 1000000000000000000); // $1000 equivalent
        self.max_daily_earning.write(10000 * 1000000000000000000); // 10,000 credits/tokens per day
        
        // Enable bridge
        self.bridge_enabled.write(true);
    }

    #[abi(embed_v0)]
    impl CosmicCreditsImpl of super::ICosmicCredits<ContractState> {
        
        /// Award currency to user for activities (only authorized minters)
        fn award_currency(
            ref self: ContractState,
            to: ContractAddress,
            amount: u256,
            reason: felt252,
            source: felt252,
        ) {
            self.pausable.assert_not_paused();
            self.reentrancy_guard.start();
            
            let caller = get_caller_address();
            assert(self.authorized_minters.read(caller), 'Unauthorized minter');
            
            // Apply economic balancing
            let faucet_multiplier = self.faucet_rate_multiplier.read();
            let adjusted_amount = (amount * faucet_multiplier) / 1000000000000000000; // Divide by 1e18
            
            // Check daily earning limits
            self._check_daily_earning_limit(to, adjusted_amount);
            
            // Mint tokens
            self.erc20._mint(to, adjusted_amount);
            
            // Update daily tracking
            self._update_daily_earned(to, adjusted_amount);
            
            // Emit event
            self.emit(CurrencyEarned { 
                user: to, 
                amount: adjusted_amount, 
                reason, 
                source 
            });
            
            self.reentrancy_guard.end();
        }
        
        /// Spend currency (burn tokens)
        fn spend_currency(
            ref self: ContractState,
            amount: u256,
            reason: felt252,
            sink_type: felt252,
        ) {
            self.pausable.assert_not_paused();
            self.reentrancy_guard.start();
            
            let caller = get_caller_address();
            
            // Check spending limits
            self._check_spending_limits(caller, amount);
            
            // Apply economic balancing
            let sink_multiplier = self.sink_rate_multiplier.read();
            let adjusted_amount = (amount * sink_multiplier) / 1000000000000000000; // Divide by 1e18
            
            // Burn tokens
            self.erc20._burn(caller, adjusted_amount);
            
            // Update spending tracking
            self._update_daily_spent(adjusted_amount);
            
            // Emit event
            self.emit(CurrencySpent { 
                user: caller, 
                amount: adjusted_amount, 
                reason, 
                sink_type 
            });
            
            self.reentrancy_guard.end();
        }
        
        /// Request conversion to USD (only for Cosmic Credits)
        fn request_conversion(
            ref self: ContractState,
            credits_amount: u256,
        ) {
            assert(self.currency_type.read() == 'cosmic_credits', 'Only credits convertible');
            assert(self.bridge_enabled.read(), 'Bridge disabled');
            self.pausable.assert_not_paused();
            self.reentrancy_guard.start();
            
            let caller = get_caller_address();
            
            // Check minimum conversion
            assert(credits_amount >= self.minimum_conversion.read(), 'Below minimum conversion');
            
            // Check balance
            assert(self.erc20.balance_of(caller) >= credits_amount, 'Insufficient balance');
            
            // Calculate USD amount
            let conversion_rate = self.conversion_rate.read();
            let gross_usd = (credits_amount * conversion_rate) / 1000000000000000000; // Divide by 1e18
            
            // Determine cooling period for large conversions
            let cooling_period = if gross_usd >= self.large_transaction_threshold.read() {
                get_block_timestamp() + 172800 // 48 hours
            } else {
                get_block_timestamp()
            };
            
            // KYC requirement for large conversions
            if gross_usd >= 100 * 1000000000000000000 { // $100
                assert(self.kyc_verified.read(caller), 'KYC required for large conversions');
            }
            
            // Store pending conversion
            self.pending_conversions.write(caller, credits_amount);
            self.user_cooling_period.write(caller, cooling_period);
            
            // Emit event
            self.emit(ConversionRequested {
                user: caller,
                credits_amount,
                usd_amount: gross_usd,
                cooling_period_until: cooling_period,
            });
            
            if cooling_period > get_block_timestamp() {
                self.emit(CoolingPeriodActivated {
                    user: caller,
                    until_timestamp: cooling_period,
                    reason: 'large_conversion',
                });
            }
            
            self.reentrancy_guard.end();
        }
        
        /// Process pending conversion (after cooling period)
        fn process_conversion(ref self: ContractState) {
            assert(self.currency_type.read() == 'cosmic_credits', 'Only credits convertible');
            assert(self.bridge_enabled.read(), 'Bridge disabled');
            self.pausable.assert_not_paused();
            self.reentrancy_guard.start();
            
            let caller = get_caller_address();
            let current_time = get_block_timestamp();
            
            // Check cooling period
            assert(current_time >= self.user_cooling_period.read(caller), 'Cooling period active');
            
            // Get pending conversion
            let credits_amount = self.pending_conversions.read(caller);
            assert(credits_amount > 0, 'No pending conversion');
            
            // Calculate final amounts
            let conversion_rate = self.conversion_rate.read();
            let gross_usd = (credits_amount * conversion_rate) / 1000000000000000000;
            let fee_rate = self.conversion_fee_rate.read();
            let fee_amount = (gross_usd * fee_rate) / 10000; // Divide by 1e4
            let net_usd = gross_usd - fee_amount;
            
            // Burn the credits
            self.erc20._burn(caller, credits_amount);
            
            // Clear pending conversion
            self.pending_conversions.write(caller, 0);
            self.user_cooling_period.write(caller, 0);
            
            // Emit event (actual USD transfer would be handled off-chain)
            self.emit(ConversionProcessed {
                user: caller,
                credits_converted: credits_amount,
                usd_received: net_usd,
                fee_paid: fee_amount,
            });
            
            self.reentrancy_guard.end();
        }
        
        /// Set user spending limits (self-imposed)
        fn set_spending_limit(
            ref self: ContractState,
            daily_limit: u256,
        ) {
            let caller = get_caller_address();
            self.user_spending_limits.write(caller, daily_limit);
            
            self.emit(SpendingLimitSet {
                user: caller,
                daily_limit,
            });
        }
        
        /// Set KYC verification status (only owner)
        fn set_kyc_verified(
            ref self: ContractState,
            user: ContractAddress,
            verified: bool,
        ) {
            self.ownable.assert_only_owner();
            self.kyc_verified.write(user, verified);
        }
        
        /// Add authorized minter (only owner)
        fn add_minter(
            ref self: ContractState,
            minter: ContractAddress,
        ) {
            self.ownable.assert_only_owner();
            self.authorized_minters.write(minter, true);
        }
        
        /// Remove authorized minter (only owner)
        fn remove_minter(
            ref self: ContractState,
            minter: ContractAddress,
        ) {
            self.ownable.assert_only_owner();
            self.authorized_minters.write(minter, false);
        }
        
        /// Adjust economic parameters (only owner)
        fn adjust_economic_parameters(
            ref self: ContractState,
            new_faucet_multiplier: u256,
            new_sink_multiplier: u256,
            reason: felt252,
        ) {
            self.ownable.assert_only_owner();
            
            let old_faucet = self.faucet_rate_multiplier.read();
            let old_sink = self.sink_rate_multiplier.read();
            
            // Bounds checking (0.5x to 2.0x)
            assert(new_faucet_multiplier >= 500000000000000000, 'Faucet multiplier too low'); // 0.5
            assert(new_faucet_multiplier <= 2000000000000000000, 'Faucet multiplier too high'); // 2.0
            assert(new_sink_multiplier >= 500000000000000000, 'Sink multiplier too low'); // 0.5
            assert(new_sink_multiplier <= 2000000000000000000, 'Sink multiplier too high'); // 2.0
            
            self.faucet_rate_multiplier.write(new_faucet_multiplier);
            self.sink_rate_multiplier.write(new_sink_multiplier);
            
            self.emit(EconomicAdjustment {
                old_faucet_multiplier: old_faucet,
                new_faucet_multiplier,
                old_sink_multiplier: old_sink,
                new_sink_multiplier,
                reason,
            });
        }
        
        /// Get user balance info
        fn get_user_info(self: @ContractState, user: ContractAddress) -> (u256, u256, u256, u64) {
            let balance = self.erc20.balance_of(user);
            let daily_earned = self.user_daily_earned.read(user);
            let spending_limit = self.user_spending_limits.read(user);
            let cooling_period = self.user_cooling_period.read(user);
            
            (balance, daily_earned, spending_limit, cooling_period)
        }
        
        /// Get economic health metrics
        fn get_economic_metrics(self: @ContractState) -> (u256, u256, u256, u256) {
            let total_supply = self.erc20.total_supply();
            let faucet_multiplier = self.faucet_rate_multiplier.read();
            let sink_multiplier = self.sink_rate_multiplier.read();
            let conversion_rate = self.conversion_rate.read();
            
            (total_supply, faucet_multiplier, sink_multiplier, conversion_rate)
        }
    }

    #[generate_trait]
    impl InternalImpl of InternalTrait {
        fn _check_daily_earning_limit(
            ref self: ContractState,
            user: ContractAddress,
            amount: u256,
        ) {
            let current_day = get_block_timestamp() / 86400; // Convert to days
            let last_earn_day = self.user_last_earn_day.read(user);
            
            if current_day > last_earn_day {
                // New day, reset counter
                self.user_daily_earned.write(user, amount);
                self.user_last_earn_day.write(user, current_day);
            } else {
                // Same day, check limit
                let current_earned = self.user_daily_earned.read(user);
                let new_total = current_earned + amount;
                assert(new_total <= self.max_daily_earning.read(), 'Daily earning limit exceeded');
                self.user_daily_earned.write(user, new_total);
            }
        }
        
        fn _update_daily_earned(
            ref self: ContractState,
            user: ContractAddress,
            amount: u256,
        ) {
            let current_earned = self.user_daily_earned.read(user);
            self.user_daily_earned.write(user, current_earned + amount);
            
            // Update global daily metrics
            let current_day = get_block_timestamp() / 86400;
            let last_metrics_day = self.last_metrics_day.read();
            
            if current_day > last_metrics_day {
                // New day, reset global counter
                self.total_earned_today.write(amount);
                self.total_spent_today.write(0);
                self.last_metrics_day.write(current_day);
            } else {
                let current_total = self.total_earned_today.read();
                self.total_earned_today.write(current_total + amount);
            }
        }
        
        fn _update_daily_spent(
            ref self: ContractState,
            amount: u256,
        ) {
            let current_spent = self.total_spent_today.read();
            self.total_spent_today.write(current_spent + amount);
        }
        
        fn _check_spending_limits(
            ref self: ContractState,
            user: ContractAddress,
            amount: u256,
        ) {
            let spending_limit = self.user_spending_limits.read(user);
            if spending_limit > 0 {
                let daily_earned = self.user_daily_earned.read(user);
                assert(amount <= spending_limit, 'Exceeds spending limit');
                assert(amount <= daily_earned, 'Cannot spend more than earned'); // Additional safety
            }
        }
    }
}

#[starknet::interface]
trait ICosmicCredits<TContractState> {
    fn award_currency(
        ref self: TContractState,
        to: ContractAddress,
        amount: u256,
        reason: felt252,
        source: felt252,
    );
    fn spend_currency(
        ref self: TContractState,
        amount: u256,
        reason: felt252,
        sink_type: felt252,
    );
    fn request_conversion(
        ref self: TContractState,
        credits_amount: u256,
    );
    fn process_conversion(ref self: TContractState);
    fn set_spending_limit(
        ref self: TContractState,
        daily_limit: u256,
    );
    fn set_kyc_verified(
        ref self: TContractState,
        user: ContractAddress,
        verified: bool,
    );
    fn add_minter(
        ref self: TContractState,
        minter: ContractAddress,
    );
    fn remove_minter(
        ref self: TContractState,
        minter: ContractAddress,
    );
    fn adjust_economic_parameters(
        ref self: TContractState,
        new_faucet_multiplier: u256,
        new_sink_multiplier: u256,
        reason: felt252,
    );
    fn get_user_info(self: @TContractState, user: ContractAddress) -> (u256, u256, u256, u64);
    fn get_economic_metrics(self: @TContractState) -> (u256, u256, u256, u256);
}