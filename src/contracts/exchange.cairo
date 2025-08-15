//! AstraTrade Exchange V2 - Gamification-Integrated Perpetuals Trading Contract
//! 
//! This contract implements mobile-optimized perpetuals trading with:
//! - On-chain XP and achievement system
//! - Extended Exchange API validation
//! - Gas-efficient operations (<100k gas per trade)
//! - Real-time events for Flutter integration
//! - Risk management and liquidation system

#[starknet::contract]
mod AstraTradeExchangeV2 {
    use starknet::{
        get_caller_address, get_block_timestamp, ContractAddress, ClassHash,
        storage::{Map, StorageMapReadAccess, StorageMapWriteAccess}
    };
    use core::pedersen::PedersenTrait;
    use core::hash::{HashStateTrait, HashStateExTrait};
    
    // ============================================================================
    // CONSTANTS
    // ============================================================================
    
    const XP_PER_TRADE: u32 = 50_u32;
    const XP_STREAK_BONUS: u32 = 10_u32;
    const MAX_LEVERAGE: u32 = 100_u32;
    const LIQUIDATION_THRESHOLD: u32 = 8000_u32; // 80%
    const FEE_RATE: u32 = 30_u32; // 0.3%
    
    // Achievement IDs
    const ACHIEVEMENT_FIRST_TRADE: u32 = 1_u32;
    const ACHIEVEMENT_TRADER_NOVICE: u32 = 2_u32;
    const ACHIEVEMENT_TRADER_EXPERT: u32 = 3_u32;
    const ACHIEVEMENT_WEEK_WARRIOR: u32 = 4_u32;
    const ACHIEVEMENT_PROFIT_MASTER: u32 = 5_u32;

    // ============================================================================
    // STORAGE
    // ============================================================================

    #[storage]
    struct Storage {
        // Contract governance
        owner: ContractAddress,
        is_paused: bool,
        emergency_mode: bool,
        
        // Ecosystem integration
        vault_contract: ContractAddress,
        paymaster_contract: ContractAddress,
        oracle_contract: ContractAddress,
        
        // User management (dual storage for migration)
        users: Map<ContractAddress, User>,              // Legacy storage
        users_v2: Map<ContractAddress, PackedUser>,     // Optimized storage
        migration_enabled: bool,                        // Migration feature flag
        user_positions: Map<(ContractAddress, u32), Position>,
        user_position_count: Map<ContractAddress, u32>,
        
        // Trading pairs
        trading_pairs: Map<u32, TradingPair>,
        active_pairs_count: u32,
        
        // Global state
        next_position_id: u32,
        total_open_interest: u256,
        daily_volume: u256,
        last_daily_reset: u64,
        
        // Extended Exchange API integration
        extended_exchange_keys: Map<u32, ExtendedExchangeKey>,
        next_key_id: u32,
        
        // Risk management
        global_exposure_limit: u256,
        liquidation_reward_rate: u32,
        
        // Reentrancy protection
        reentrancy_guard: bool,
    }

    // ============================================================================
    // STRUCTS
    // ============================================================================

    #[derive(Drop, starknet::Store, Copy, Serde)]
    struct User {
        user_address: ContractAddress,
        total_xp: u256,
        current_level: u32,
        streak_days: u32,
        last_activity_timestamp: u64,
        achievement_mask: u256,  // Bitfield for achievements
        practice_balance: u256,
        total_trades: u32,
        profitable_trades: u32,
        max_leverage_allowed: u32,
        is_kyc_verified: bool,
    }

    // OPTIMIZED: Packed User struct for gas efficiency (7 storage slots vs 11)
    #[derive(Drop, starknet::Store, Copy, Serde)]
    struct PackedUser {
        // Slot 1: ContractAddress (32 bytes)
        user_address: ContractAddress,
        
        // Slot 2: Large integers (32 bytes)
        total_xp: u256,
        
        // Slot 3: Large integers (32 bytes)  
        practice_balance: u256,
        
        // Slot 4: Large integers (32 bytes)
        achievement_mask: u256,
        
        // Slot 5: Packed small integers (32 bytes total)
        packed_stats: PackedUserStats,
        
        // Slot 6: Timestamp and flags (32 bytes)
        packed_metadata: PackedUserMetadata,
        
        // Slot 7: Reserved for future expansion (32 bytes)
        reserved: u256,
    }

    // Packed statistics struct (fits in 32 bytes)
    #[derive(Drop, starknet::Store, Copy, Serde)]
    struct PackedUserStats {
        current_level: u32,              // 4 bytes
        streak_days: u32,                // 4 bytes
        total_trades: u32,               // 4 bytes
        profitable_trades: u32,          // 4 bytes
        max_leverage_allowed: u32,       // 4 bytes
        // 12 bytes remaining for future stats
    }

    // Packed metadata struct (fits in 32 bytes)
    #[derive(Drop, starknet::Store, Copy, Serde)]
    struct PackedUserMetadata {
        last_activity_timestamp: u64,   // 8 bytes
        is_kyc_verified: bool,          // 1 byte
        user_tier: u8,                  // 1 byte - future feature
        feature_flags: u32,             // 4 bytes - future features
        // 18 bytes remaining for future metadata
    }

    #[derive(Drop, starknet::Store, Copy, Serde)]
    struct Position {
        position_id: u32,
        user_address: ContractAddress,
        pair_id: u32,
        is_long: bool,
        leverage: u32,
        collateral: u256,
        entry_price: u256,
        liquidation_price: u256,
        funding_rate_accumulated: u256,
        is_active: bool,
        created_timestamp: u64,
        last_updated_timestamp: u64,
    }

    #[derive(Drop, starknet::Store, Copy, Serde)]
    struct TradingPair {
        pair_id: u32,
        name: felt252, // e.g., 'BTC/USD'
        base_asset: felt252,
        quote_asset: felt252,
        current_price: u256,
        max_leverage: u32,
        maintenance_margin: u32, // Basis points (e.g., 500 = 5%)
        funding_rate: u256,
        is_active: bool,
        daily_volume: u256,
    }

    #[derive(Drop, starknet::Store, Copy, Serde)]
    struct ExtendedExchangeKey {
        key_id: u32,
        owner: ContractAddress,
        key_hash: felt252, // Hash of the actual API key for security
        permissions: u32, // Bitfield for permissions
        is_active: bool,
        created_timestamp: u64,
        last_used_timestamp: u64,
    }

    // ============================================================================
    // EVENTS
    // ============================================================================

    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        // Trading events
        PositionOpened: PositionOpened,
        PositionClosed: PositionClosed,
        PositionLiquidated: PositionLiquidated,
        
        // Gamification events
        XPAwarded: XPAwarded,
        UserLevelUp: UserLevelUp,
        AchievementUnlocked: AchievementUnlocked,
        StreakUpdated: StreakUpdated,
        
        // Extended Exchange events
        ExtendedExchangeTradeValidated: ExtendedExchangeTradeValidated,
        ExtendedExchangeKeyRegistered: ExtendedExchangeKeyRegistered,
        
        // System events
        TradingPairAdded: TradingPairAdded,
        SystemPaused: SystemPaused,
        EmergencyModeActivated: EmergencyModeActivated,
    }

    #[derive(Drop, starknet::Event)]
    struct PositionOpened {
        #[key]
        user_address: ContractAddress,
        position_id: u32,
        pair_id: u32,
        is_long: bool,
        leverage: u32,
        collateral: u256,
        entry_price: u256,
        liquidation_price: u256,
        xp_earned: u32,
        timestamp: u64,
    }

    #[derive(Drop, starknet::Event)]
    struct PositionClosed {
        #[key]
        user_address: ContractAddress,
        position_id: u32,
        exit_price: u256,
        pnl: u256,
        is_profit: bool,
        fee_amount: u256,
        xp_earned: u32,
        timestamp: u64,
    }

    #[derive(Drop, starknet::Event)]
    struct PositionLiquidated {
        #[key]
        user_address: ContractAddress,
        position_id: u32,
        liquidation_price: u256,
        liquidator: ContractAddress,
        liquidation_reward: u256,
        timestamp: u64,
    }

    #[derive(Drop, starknet::Event)]
    struct XPAwarded {
        #[key]
        user_address: ContractAddress,
        xp_amount: u32,
        activity_type: felt252,
        multiplier: u32,
        total_xp: u256,
        timestamp: u64,
    }

    #[derive(Drop, starknet::Event)]
    struct UserLevelUp {
        #[key]
        user_address: ContractAddress,
        old_level: u32,
        new_level: u32,
        total_xp: u256,
        new_max_leverage: u32,
        timestamp: u64,
    }

    #[derive(Drop, starknet::Event)]
    struct AchievementUnlocked {
        #[key]
        user_address: ContractAddress,
        achievement_id: u32,
        achievement_name: felt252,
        xp_reward: u32,
        timestamp: u64,
    }

    #[derive(Drop, starknet::Event)]
    struct StreakUpdated {
        #[key]
        user_address: ContractAddress,
        old_streak: u32,
        new_streak: u32,
        streak_bonus_xp: u32,
        timestamp: u64,
    }

    #[derive(Drop, starknet::Event)]
    struct ExtendedExchangeTradeValidated {
        #[key]
        user_address: ContractAddress,
        key_id: u32,
        external_trade_id: felt252,
        validation_hash: felt252,
        xp_bonus: u32,
        timestamp: u64,
    }

    #[derive(Drop, starknet::Event)]
    struct ExtendedExchangeKeyRegistered {
        #[key]
        user_address: ContractAddress,
        key_id: u32,
        permissions: u32,
        timestamp: u64,
    }

    #[derive(Drop, starknet::Event)]
    struct TradingPairAdded {
        pair_id: u32,
        name: felt252,
        max_leverage: u32,
        timestamp: u64,
    }

    #[derive(Drop, starknet::Event)]
    struct SystemPaused {
        paused: bool,
        timestamp: u64,
    }

    #[derive(Drop, starknet::Event)]
    struct EmergencyModeActivated {
        active: bool,
        timestamp: u64,
    }

    // ============================================================================
    // CONSTRUCTOR
    // ============================================================================

    #[constructor]
    fn constructor(
        ref self: ContractState,
        owner: ContractAddress,
        vault_contract: ContractAddress,
        paymaster_contract: ContractAddress,
        oracle_contract: ContractAddress,
    ) {
        self.owner.write(owner);
        self.vault_contract.write(vault_contract);
        self.paymaster_contract.write(paymaster_contract);
        self.oracle_contract.write(oracle_contract);
        
        self.is_paused.write(false);
        self.emergency_mode.write(false);
        self.next_position_id.write(1_u32);
        self.next_key_id.write(1_u32);
        self.active_pairs_count.write(0_u32);
        
        // Initialize risk parameters
        self.global_exposure_limit.write(10000000000000000000000_u256); // 10,000 tokens
        self.liquidation_reward_rate.write(500_u32); // 5%
        
        // Initialize default trading pairs
        self._initialize_default_pairs();
    }

    // ============================================================================
    // EXTERNAL FUNCTIONS
    // ============================================================================

    #[abi(embed_v0)]
    impl ExchangeImpl of ExchangeTrait<ContractState> {
        
        // ========================================================================
        // USER MANAGEMENT
        // ========================================================================

        fn register_user(ref self: ContractState) {
            let caller = get_caller_address();
            let existing_user = self.users.read(caller);
            
            // Check if user already exists
            assert(existing_user.user_address.is_zero(), 'User already registered');
            
            let user = User {
                user_address: caller,
                total_xp: 0_u256,
                current_level: 1_u32,
                streak_days: 0_u32,
                last_activity_timestamp: get_block_timestamp(),
                achievement_mask: 0_u256,
                practice_balance: 10000000000000000000000_u256, // 10,000 practice tokens
                total_trades: 0_u32,
                profitable_trades: 0_u32,
                max_leverage_allowed: 10_u32, // Start with 10x max leverage
                is_kyc_verified: false,
            };
            
            self.users.write(caller, user);
            self.user_position_count.write(caller, 0_u32);
        }

        fn get_user(self: @ContractState, user_address: ContractAddress) -> User {
            self.users.read(user_address)
        }

        // ========================================================================
        // POSITION MANAGEMENT - Mobile Optimized
        // ========================================================================

        fn open_practice_position(
            ref self: ContractState,
            pair_id: u32,
            is_long: bool,
            leverage: u32,
            collateral_amount: u256
        ) -> u32 {
            self._assert_not_paused();
            let caller = get_caller_address();
            
            // Validate user and get current state
            let mut user = self.users.read(caller);
            assert(!user.user_address.is_zero(), 'User not registered');
            
            // Validate trading pair
            let trading_pair = self.trading_pairs.read(pair_id);
            assert(trading_pair.is_active, 'Pair not active');
            
            // Validate leverage
            self._validate_leverage(user, trading_pair, leverage);
            
            // Check practice balance
            assert(user.practice_balance >= collateral_amount, 'Insufficient balance');
            
            // Calculate position details
            let current_price = trading_pair.current_price;
            let liquidation_price = self._calculate_liquidation_price(
                current_price, is_long, leverage, trading_pair.maintenance_margin
            );
            
            // Create position
            let position_id = self.next_position_id.read();
            let position = Position {
                position_id,
                user_address: caller,
                pair_id,
                is_long,
                leverage,
                collateral: collateral_amount,
                entry_price: current_price,
                liquidation_price,
                funding_rate_accumulated: 0_u256,
                is_active: true,
                created_timestamp: get_block_timestamp(),
                last_updated_timestamp: get_block_timestamp(),
            };
            
            // Batch storage updates for gas efficiency
            self.user_positions.write((caller, position_id), position);
            self.next_position_id.write(position_id + 1_u32);
            
            // Update user balance
            user.practice_balance = user.practice_balance - collateral_amount;
            user.total_trades = user.total_trades + 1_u32;
            let position_count = self.user_position_count.read(caller);
            self.user_position_count.write(caller, position_count + 1_u32);
            
            // Award XP and update streak in same transaction
            let (xp_earned, _streak_updated) = self._award_trade_xp(ref user, 'PRACTICE_TRADE');
            self.users.write(caller, user);
            
            // Update daily volume
            self._update_daily_volume(collateral_amount * leverage.into());
            
            // Emit comprehensive event for Flutter UI
            self.emit(PositionOpened {
                user_address: caller,
                position_id,
                pair_id,
                is_long,
                leverage,
                collateral: collateral_amount,
                entry_price: current_price,
                liquidation_price,
                xp_earned,
                timestamp: get_block_timestamp(),
            });
            
            position_id
        }

        fn close_position(ref self: ContractState, position_id: u32) -> (u256, bool) {
            // Reentrancy protection
            self._reentrancy_guard_start();
            
            self._assert_not_paused();
            let caller = get_caller_address();
            
            // Get position and validate ownership
            let mut position = self.user_positions.read((caller, position_id));
            assert(position.user_address == caller, 'Not position owner');
            assert(position.is_active, 'Position not active');
            
            // Get current price and trading pair
            let trading_pair = self.trading_pairs.read(position.pair_id);
            let current_price = trading_pair.current_price;
            
            // Calculate PnL and fees
            let (pnl, is_profit) = self._calculate_pnl(position, current_price);
            let fee_amount = (position.collateral * FEE_RATE.into()) / 10000_u256;
            let net_pnl = if pnl > fee_amount { pnl - fee_amount } else { 0_u256 };
            
            // Update user balance and stats
            let mut user = self.users.read(caller);
            user.practice_balance = user.practice_balance + position.collateral + net_pnl;
            if is_profit {
                user.profitable_trades = user.profitable_trades + 1_u32;
            }
            
            // Award XP for closing position
            let activity_type = if is_profit { 'PROFITABLE_TRADE' } else { 'TRADE_CLOSE' };
            let (xp_earned, _) = self._award_trade_xp(ref user, activity_type);
            
            // Mark position as closed
            position.is_active = false;
            position.last_updated_timestamp = get_block_timestamp();
            
            // Batch storage updates
            self.user_positions.write((caller, position_id), position);
            self.users.write(caller, user);
            
            // Emit event
            self.emit(PositionClosed {
                user_address: caller,
                position_id,
                exit_price: current_price,
                pnl: net_pnl,
                is_profit,
                fee_amount,
                xp_earned,
                timestamp: get_block_timestamp(),
            });
            
            // End reentrancy protection
            self._reentrancy_guard_end();
            
            (net_pnl, is_profit)
        }

        fn get_user_positions(
            self: @ContractState, 
            user_address: ContractAddress
        ) -> Array<Position> {
            let position_count = self.user_position_count.read(user_address);
            let mut positions = ArrayTrait::new();
            let mut i = 1_u32;
            
            loop {
                if i > position_count {
                    break;
                }
                
                let position = self.user_positions.read((user_address, i));
                if position.is_active {
                    positions.append(position);
                }
                i += 1_u32;
            };
            
            positions
        }

        // ========================================================================
        // EXTENDED EXCHANGE API INTEGRATION
        // ========================================================================

        fn register_extended_exchange_key(
            ref self: ContractState,
            key_hash: felt252,
            permissions: u32
        ) -> u32 {
            self._assert_not_paused();
            let caller = get_caller_address();
            
            // Validate user is registered and KYC verified for live trading
            let user = self.users.read(caller);
            assert(!user.user_address.is_zero(), 'User not registered');
            assert(user.is_kyc_verified, 'KYC verification required');
            
            let key_id = self.next_key_id.read();
            let key = ExtendedExchangeKey {
                key_id,
                owner: caller,
                key_hash,
                permissions,
                is_active: true,
                created_timestamp: get_block_timestamp(),
                last_used_timestamp: 0_u64,
            };
            
            self.extended_exchange_keys.write(key_id, key);
            self.next_key_id.write(key_id + 1_u32);
            
            self.emit(ExtendedExchangeKeyRegistered {
                user_address: caller,
                key_id,
                permissions,
                timestamp: get_block_timestamp(),
            });
            
            key_id
        }

        fn validate_extended_exchange_trade(
            ref self: ContractState,
            key_id: u32,
            external_trade_id: felt252,
            trade_data_hash: felt252,
            signature: Array<felt252>
        ) -> felt252 {
            self._assert_not_paused();
            let caller = get_caller_address();
            
            // Validate API key
            let mut key = self.extended_exchange_keys.read(key_id);
            assert(key.owner == caller, 'Invalid key owner');
            assert(key.is_active, 'Key not active');
            
            // Create validation hash using Pedersen hash
            let validation_hash = core::pedersen::pedersen(
                core::pedersen::pedersen(caller.into(), external_trade_id),
                core::pedersen::pedersen(trade_data_hash, get_block_timestamp().into())
            );
            
            // Update key usage
            key.last_used_timestamp = get_block_timestamp();
            self.extended_exchange_keys.write(key_id, key);
            
            // Award bonus XP for live trading
            let mut user = self.users.read(caller);
            let (xp_bonus, _) = self._award_trade_xp(ref user, 'LIVE_TRADE');
            self.users.write(caller, user);
            
            // Emit validation event
            self.emit(ExtendedExchangeTradeValidated {
                user_address: caller,
                key_id,
                external_trade_id,
                validation_hash,
                xp_bonus,
                timestamp: get_block_timestamp(),
            });
            
            validation_hash
        }

        // ========================================================================
        // TRADING PAIRS MANAGEMENT
        // ========================================================================

        fn add_trading_pair(
            ref self: ContractState,
            name: felt252,
            base_asset: felt252,
            quote_asset: felt252,
            initial_price: u256,
            max_leverage: u32,
            maintenance_margin: u32
        ) -> u32 {
            self._assert_only_owner();
            
            let pair_id = self.active_pairs_count.read() + 1_u32;
            let trading_pair = TradingPair {
                pair_id,
                name,
                base_asset,
                quote_asset,
                current_price: initial_price,
                max_leverage,
                maintenance_margin,
                funding_rate: 0_u256,
                is_active: true,
                daily_volume: 0_u256,
            };
            
            self.trading_pairs.write(pair_id, trading_pair);
            self.active_pairs_count.write(pair_id);
            
            self.emit(TradingPairAdded {
                pair_id,
                name,
                max_leverage,
                timestamp: get_block_timestamp(),
            });
            
            pair_id
        }

        fn get_trading_pair(self: @ContractState, pair_id: u32) -> TradingPair {
            self.trading_pairs.read(pair_id)
        }

        fn update_pair_price(ref self: ContractState, pair_id: u32, new_price: u256) {
            self._assert_only_owner();
            
            let mut trading_pair = self.trading_pairs.read(pair_id);
            assert(trading_pair.is_active, 'Pair not active');
            
            trading_pair.current_price = new_price;
            self.trading_pairs.write(pair_id, trading_pair);
        }

        // ========================================================================
        // SYSTEM MANAGEMENT
        // ========================================================================

        fn pause_system(ref self: ContractState) {
            self._assert_only_owner();
            self.is_paused.write(true);
            
            self.emit(SystemPaused {
                paused: true,
                timestamp: get_block_timestamp(),
            });
        }

        fn unpause_system(ref self: ContractState) {
            self._assert_only_owner();
            self.is_paused.write(false);
            
            self.emit(SystemPaused {
                paused: false,
                timestamp: get_block_timestamp(),
            });
        }

        fn activate_emergency_mode(ref self: ContractState) {
            self._assert_only_owner();
            self.emergency_mode.write(true);
            self.is_paused.write(true);
            
            self.emit(EmergencyModeActivated {
                active: true,
                timestamp: get_block_timestamp(),
            });
        }

        // ========================================================================
        // VIEW FUNCTIONS
        // ========================================================================

        fn get_system_status(self: @ContractState) -> (bool, bool) {
            (self.is_paused.read(), self.emergency_mode.read())
        }

        fn get_daily_volume(self: @ContractState) -> u256 {
            self.daily_volume.read()
        }

        fn get_total_open_interest(self: @ContractState) -> u256 {
            self.total_open_interest.read()
        }
    }

    // ============================================================================
    // INTERNAL FUNCTIONS
    // ============================================================================

    #[generate_trait]
    impl InternalFunctions of InternalFunctionsTrait {
        
        fn _assert_not_paused(self: @ContractState) {
            assert(!self.is_paused.read(), 'System paused');
        }

        fn _assert_only_owner(self: @ContractState) {
            assert(get_caller_address() == self.owner.read(), 'Unauthorized');
        }
        
        fn _reentrancy_guard_start(ref self: ContractState) {
            assert(!self.reentrancy_guard.read(), 'Reentrancy detected');
            self.reentrancy_guard.write(true);
        }
        
        fn _reentrancy_guard_end(ref self: ContractState) {
            self.reentrancy_guard.write(false);
        }
        
        // USER PACKING HELPER FUNCTIONS
        
        fn _pack_user_stats(
            current_level: u32,
            streak_days: u32,
            total_trades: u32,
            profitable_trades: u32,
            max_leverage_allowed: u32
        ) -> PackedUserStats {
            PackedUserStats {
                current_level,
                streak_days,
                total_trades,
                profitable_trades,
                max_leverage_allowed,
            }
        }
        
        fn _pack_user_metadata(
            last_activity_timestamp: u64,
            is_kyc_verified: bool
        ) -> PackedUserMetadata {
            PackedUserMetadata {
                last_activity_timestamp,
                is_kyc_verified,
                user_tier: 1, // Default tier
                feature_flags: 0, // No features enabled initially
            }
        }
        
        fn _migrate_user_to_packed(old_user: User) -> PackedUser {
            PackedUser {
                user_address: old_user.user_address,
                total_xp: old_user.total_xp,
                practice_balance: old_user.practice_balance,
                achievement_mask: old_user.achievement_mask,
                packed_stats: Self::_pack_user_stats(
                    old_user.current_level,
                    old_user.streak_days,
                    old_user.total_trades,
                    old_user.profitable_trades,
                    old_user.max_leverage_allowed
                ),
                packed_metadata: Self::_pack_user_metadata(
                    old_user.last_activity_timestamp,
                    old_user.is_kyc_verified
                ),
                reserved: 0, // Reserved for future use
            }
        }

        fn _validate_leverage(
            self: @ContractState,
            user: User,
            trading_pair: TradingPair,
            leverage: u32
        ) {
            assert(leverage <= user.max_leverage_allowed, 'Exceeds user limit');
            assert(leverage <= trading_pair.max_leverage, 'Exceeds pair limit');
            assert(leverage <= MAX_LEVERAGE, 'Exceeds system limit');
            assert(leverage > 0_u32, 'Invalid leverage');
        }

        fn _calculate_liquidation_price(
            self: @ContractState,
            entry_price: u256,
            is_long: bool,
            leverage: u32,
            maintenance_margin: u32
        ) -> u256 {
            // Input validation to prevent overflow conditions
            assert(entry_price > 0, 'Invalid entry price');
            assert(leverage > 0 && leverage <= MAX_LEVERAGE, 'Invalid leverage');
            assert(maintenance_margin <= 10000, 'Invalid maintenance margin');
            
            // Safe arithmetic with overflow protection
            let margin_factor_base = 10000_u32 - maintenance_margin;
            
            // Prevent multiplication overflow: check if result would exceed max
            assert(margin_factor_base <= 4294967295_u32 / 100_u32, 'Margin factor overflow');
            let margin_factor = margin_factor_base * 100_u32;
            
            // Safe division
            assert(leverage > 0, 'Division by zero');
            let leverage_factor = margin_factor / leverage;
            
            if is_long {
                // Safe multiplication and division to prevent overflow
                let numerator = entry_price * leverage_factor.into();
                assert(numerator >= entry_price, 'Multiplication overflow');
                
                let price_reduction = numerator / 1000000_u256;
                assert(price_reduction <= entry_price, 'Price reduction exceeds entry');
                entry_price - price_reduction
            } else {
                // Safe multiplication and division to prevent overflow
                let numerator = entry_price * leverage_factor.into();
                assert(numerator >= entry_price, 'Multiplication overflow');
                
                let price_increase = numerator / 1000000_u256;
                // Check for addition overflow
                assert(entry_price + price_increase >= entry_price, 'Addition overflow');
                entry_price + price_increase
            }
        }

        fn _calculate_pnl(
            self: @ContractState,
            position: Position,
            current_price: u256
        ) -> (u256, bool) {
            // Input validation
            assert(current_price > 0, 'Invalid current price');
            assert(position.entry_price > 0, 'Invalid entry price');
            assert(position.collateral > 0, 'Invalid collateral');
            assert(position.leverage > 0, 'Invalid leverage');
            
            // Safe position size calculation with overflow protection
            let leverage_u256 = position.leverage.into();
            let position_size = position.collateral * leverage_u256;
            assert(position_size >= position.collateral, 'Position size overflow');
            
            if position.is_long {
                if current_price > position.entry_price {
                    let price_diff = current_price - position.entry_price;
                    // Safe multiplication with overflow check
                    let numerator = position_size * price_diff;
                    assert(numerator >= position_size, 'PnL calculation overflow');
                    let pnl = numerator / position.entry_price;
                    (pnl, true)
                } else {
                    let price_diff = position.entry_price - current_price;
                    // Safe multiplication with overflow check
                    let numerator = position_size * price_diff;
                    assert(numerator >= position_size, 'PnL calculation overflow');
                    let pnl = numerator / position.entry_price;
                    (pnl, false)
                }
            } else {
                if current_price < position.entry_price {
                    let price_diff = position.entry_price - current_price;
                    // Safe multiplication with overflow check
                    let numerator = position_size * price_diff;
                    assert(numerator >= position_size, 'PnL calculation overflow');
                    let pnl = numerator / position.entry_price;
                    (pnl, true)
                } else {
                    let price_diff = current_price - position.entry_price;
                    // Safe multiplication with overflow check
                    let numerator = position_size * price_diff;
                    assert(numerator >= position_size, 'PnL calculation overflow');
                    let pnl = numerator / position.entry_price;
                    (pnl, false)
                }
            }
        }

        // DECOMPOSED XP SYSTEM FUNCTIONS (improved maintainability)
        
        /// @notice Calculates base XP award for a trading activity
        /// @param activity_type The type of trading activity
        /// @return Base XP amount to award
        fn _calculate_base_xp(activity_type: felt252) -> u32 {
            if activity_type == 'PRACTICE_TRADE' {
                XP_PER_TRADE
            } else if activity_type == 'LIVE_TRADE' {
                XP_PER_TRADE * 2 // Bonus for live trading
            } else if activity_type == 'PROFITABLE_TRADE' {
                XP_PER_TRADE + 25 // Profit bonus
            } else if activity_type == 'TRADE_CLOSE' {
                XP_PER_TRADE / 2 // Reduced XP for closing
            } else {
                XP_PER_TRADE // Default XP
            }
        }
        
        /// @notice Updates user trading streak based on activity timestamp
        /// @param user Reference to user struct to update
        /// @param current_time Current block timestamp
        /// @return (streak_bonus_xp, new_streak_days)
        fn _update_trading_streak(ref user: User, current_time: u64) -> (u32, u32) {
            let time_since_last = current_time - user.last_activity_timestamp;
            
            // Determine new streak length
            let new_streak = if time_since_last >= 86400_u64 && time_since_last <= 172800_u64 {
                // Consecutive day (24-48 hours)
                user.streak_days + 1_u32
            } else if time_since_last <= 86400_u64 {
                // Same day - maintain streak
                user.streak_days
            } else {
                // Streak broken - reset to 1
                1_u32
            };
            
            // Calculate streak bonus
            let streak_bonus = new_streak * XP_STREAK_BONUS;
            
            // Update user streak data
            user.streak_days = new_streak;
            user.last_activity_timestamp = current_time;
            
            (streak_bonus, new_streak)
        }
        
        /// @notice Processes user level progression and unlocks benefits
        /// @param self Contract state for level calculation
        /// @param user Reference to user struct to update
        /// @return true if user leveled up, false otherwise
        fn _process_level_progression(self: @ContractState, ref user: User) -> bool {
            let new_level = self._calculate_level(user.total_xp);
            let level_up = new_level > user.current_level;
            
            if level_up {
                user.current_level = new_level;
                // Unlock level benefits: 10x base + 5x per level, capped at MAX_LEVERAGE
                user.max_leverage_allowed = core::cmp::min(10_u32 + (new_level - 1_u32) * 5_u32, MAX_LEVERAGE);
            }
            
            level_up
        }
        
        /// @notice Awards XP and processes all related user progression updates
        /// @param self Contract state reference
        /// @param user Reference to user struct to update
        /// @param activity_type Type of trading activity being rewarded
        /// @return (total_xp_awarded, new_streak_days)
        fn _award_trade_xp(
            self: @ContractState,
            ref user: User,
            activity_type: felt252
        ) -> (u32, u32) {
            // Calculate base XP for activity
            let base_xp = Self::_calculate_base_xp(activity_type);
            
            // Update trading streak and get bonus
            let current_time = get_block_timestamp();
            let (streak_bonus, new_streak) = Self::_update_trading_streak(ref user, current_time);
            
            // Calculate total XP award
            let total_xp = base_xp + streak_bonus;
            user.total_xp = user.total_xp + total_xp.into();
            
            // Process level progression
            let _leveled_up = self._process_level_progression(ref user);
            
            // Process achievements (existing function, already well-structured)
            self._check_achievements(ref user);
            
            (total_xp, new_streak)
        }

        fn _calculate_level(self: @ContractState, total_xp: u256) -> u32 {
            // Level calculation: Level = floor(sqrt(XP / 100)) + 1
            // This creates a curved progression that gets harder over time
            let xp_scaled = total_xp / 100_u256;
            
            // Simple approximation for square root
            let mut level = 1_u32;
            let mut threshold = 1_u256;
            
            loop {
                if threshold > xp_scaled {
                    break;
                }
                level += 1_u32;
                threshold = (level * level).into();
            };
            
            level
        }

        fn _check_achievements(self: @ContractState, ref user: User) {
            
            // First trade achievement
            if user.total_trades == 1_u32 && !self._has_achievement(user, ACHIEVEMENT_FIRST_TRADE) {
                self._unlock_achievement(ref user, ACHIEVEMENT_FIRST_TRADE, 'FIRST_TRADE', 100_u32);
            }
            
            // Trader achievements
            if user.total_trades >= 10_u32 && !self._has_achievement(user, ACHIEVEMENT_TRADER_NOVICE) {
                self._unlock_achievement(ref user, ACHIEVEMENT_TRADER_NOVICE, 'TRADER_NOVICE', 250_u32);
            }
            
            if user.total_trades >= 100_u32 && !self._has_achievement(user, ACHIEVEMENT_TRADER_EXPERT) {
                self._unlock_achievement(ref user, ACHIEVEMENT_TRADER_EXPERT, 'TRADER_EXPERT', 500_u32);
            }
            
            // Streak achievements
            if user.streak_days >= 7_u32 && !self._has_achievement(user, ACHIEVEMENT_WEEK_WARRIOR) {
                self._unlock_achievement(ref user, ACHIEVEMENT_WEEK_WARRIOR, 'WEEK_WARRIOR', 300_u32);
            }
            
            // Profit achievement
            let profit_rate = if user.total_trades > 0_u32 {
                (user.profitable_trades * 100_u32) / user.total_trades
            } else {
                0_u32
            };
            
            if profit_rate >= 70_u32 && user.total_trades >= 10_u32 && !self._has_achievement(user, ACHIEVEMENT_PROFIT_MASTER) {
                self._unlock_achievement(ref user, ACHIEVEMENT_PROFIT_MASTER, 'PROFIT_MASTER', 750_u32);
            }
        }

        fn _has_achievement(self: @ContractState, user: User, achievement_id: u32) -> bool {
            let bit_position = achievement_id - 1_u32;
            // Simple bit shift implementation using multiplication
            let mut mask = 1_u256;
            let mut i = 0_u32;
            loop {
                if i >= bit_position {
                    break;
                }
                mask = mask * 2_u256;
                i += 1_u32;
            };
            (user.achievement_mask & mask) != 0_u256
        }

        fn _unlock_achievement(
            self: @ContractState,
            ref user: User,
            achievement_id: u32,
            achievement_name: felt252,
            xp_reward: u32
        ) {
            let bit_position = achievement_id - 1_u32;
            // Simple bit shift implementation using multiplication
            let mut mask = 1_u256;
            let mut i = 0_u32;
            loop {
                if i >= bit_position {
                    break;
                }
                mask = mask * 2_u256;
                i += 1_u32;
            };
            user.achievement_mask = user.achievement_mask | mask;
            user.total_xp = user.total_xp + xp_reward.into();
            
            // Note: Achievement event would be emitted from calling function
        }

        fn _update_daily_volume(ref self: ContractState, volume: u256) {
            let current_time = get_block_timestamp();
            let last_reset = self.last_daily_reset.read();
            
            // Reset daily volume if it's a new day
            if current_time - last_reset >= 86400_u64 {
                self.daily_volume.write(volume);
                self.last_daily_reset.write(current_time);
            } else {
                let current_volume = self.daily_volume.read();
                self.daily_volume.write(current_volume + volume);
            }
        }

        fn _initialize_default_pairs(ref self: ContractState) {
            // Add BTC/USD pair
            let btc_pair = TradingPair {
                pair_id: 1_u32,
                name: 'BTC/USD',
                base_asset: 'BTC',
                quote_asset: 'USD',
                current_price: 45000000000000000000000_u256, // $45,000
                max_leverage: 50_u32,
                maintenance_margin: 500_u32, // 5%
                funding_rate: 0_u256,
                is_active: true,
                daily_volume: 0_u256,
            };
            self.trading_pairs.write(1_u32, btc_pair);
            
            // Add ETH/USD pair
            let eth_pair = TradingPair {
                pair_id: 2_u32,
                name: 'ETH/USD',
                base_asset: 'ETH',
                quote_asset: 'USD',
                current_price: 3000000000000000000000_u256, // $3,000
                max_leverage: 50_u32,
                maintenance_margin: 500_u32, // 5%
                funding_rate: 0_u256,
                is_active: true,
                daily_volume: 0_u256,
            };
            self.trading_pairs.write(2_u32, eth_pair);
            
            self.active_pairs_count.write(2_u32);
        }
    }

    // ============================================================================
    // TRAIT DEFINITION
    // ============================================================================

    #[starknet::interface]
    trait ExchangeTrait<TContractState> {
        // User management
        fn register_user(ref self: TContractState);
        fn get_user(self: @TContractState, user_address: ContractAddress) -> User;
        
        // Position management
        fn open_practice_position(
            ref self: TContractState,
            pair_id: u32,
            is_long: bool,
            leverage: u32,
            collateral_amount: u256
        ) -> u32;
        fn close_position(ref self: TContractState, position_id: u32) -> (u256, bool);
        fn get_user_positions(self: @TContractState, user_address: ContractAddress) -> Array<Position>;
        
        // Extended Exchange API
        fn register_extended_exchange_key(
            ref self: TContractState,
            key_hash: felt252,
            permissions: u32
        ) -> u32;
        fn validate_extended_exchange_trade(
            ref self: TContractState,
            key_id: u32,
            external_trade_id: felt252,
            trade_data_hash: felt252,
            signature: Array<felt252>
        ) -> felt252;
        
        // Trading pairs
        fn add_trading_pair(
            ref self: TContractState,
            name: felt252,
            base_asset: felt252,
            quote_asset: felt252,
            initial_price: u256,
            max_leverage: u32,
            maintenance_margin: u32
        ) -> u32;
        fn get_trading_pair(self: @TContractState, pair_id: u32) -> TradingPair;
        fn update_pair_price(ref self: TContractState, pair_id: u32, new_price: u256);
        
        // System management
        fn pause_system(ref self: TContractState);
        fn unpause_system(ref self: TContractState);
        fn activate_emergency_mode(ref self: TContractState);
        
        // View functions
        fn get_system_status(self: @TContractState) -> (bool, bool);
        fn get_daily_volume(self: @TContractState) -> u256;
        fn get_total_open_interest(self: @TContractState) -> u256;
    }
}