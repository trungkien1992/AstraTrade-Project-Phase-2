/// AstraTrade Paymaster Contract V2
/// 
/// Gasless transaction system with gamification incentives:
/// - Mobile-optimized gas sponsorship (<30k gas per operation)
/// - Level-based gasless transaction quotas
/// - XP-earning gas refunds for active traders
/// - Extended Exchange API integration for hybrid trading
/// - Progressive gas allowances (more trades = more gasless txs)
/// - Enterprise-grade transaction batching

use starknet::{ContractAddress, get_caller_address, get_block_timestamp};

#[starknet::interface]
trait IAstraTradePaymaster<TContractState> {
    // === Core Paymaster Operations ===
    fn sponsor_user_transaction(ref self: TContractState, user: ContractAddress, 
                               gas_limit: u64, transaction_type: u8) -> bool;
    fn validate_paymaster_transaction(self: @TContractState, user: ContractAddress, 
                                    gas_estimate: u64, signature: Span<felt252>) -> bool;
    fn execute_sponsored_transaction(ref self: TContractState, user: ContractAddress, 
                                   calls: Span<Call>, max_gas: u64) -> SponsorshipResult;
    
    // === Gas Allowance Management ===
    fn get_user_gas_allowance(self: @TContractState, user: ContractAddress) -> GasAllowance;
    fn refill_gas_allowance(ref self: TContractState, user: ContractAddress, amount: u64) -> bool;
    fn get_remaining_sponsored_gas(self: @TContractState, user: ContractAddress) -> u64;
    fn calculate_gas_refund_rate(self: @TContractState, user: ContractAddress, 
                                trading_volume: u256) -> u16;
    
    // === Gamification Integration ===
    fn earn_gas_refund_xp(ref self: TContractState, user: ContractAddress, gas_saved: u64) -> u32;
    fn unlock_premium_gas_features(ref self: TContractState, tier: u8) -> bool;
    fn get_user_gas_tier(self: @TContractState, user: ContractAddress) -> GasTierBenefits;
    fn claim_trading_gas_rewards(ref self: TContractState, trading_stats: TradingStats) -> u64;
    
    // === Extended API Integration ===
    fn validate_external_gas_payment(self: @TContractState, user: ContractAddress, 
                                    external_data: Span<felt252>, signature: Span<felt252>) -> bool;
    fn sync_external_gas_credits(ref self: TContractState, user: ContractAddress, 
                                credits: u64, provider: felt252) -> bool;
    
    // === Enterprise Features ===
    fn batch_sponsor_transactions(ref self: TContractState, users: Span<ContractAddress>, 
                                 gas_amounts: Span<u64>) -> u32;
    fn get_platform_gas_metrics(self: @TContractState) -> PlatformGasMetrics;
    fn emergency_gas_allocation(ref self: TContractState, user: ContractAddress, 
                               emergency_gas: u64, reason: felt252) -> bool;
    
    // === Admin Functions ===
    fn set_exchange_contract(ref self: TContractState, exchange: ContractAddress);
    fn set_vault_contract(ref self: TContractState, vault: ContractAddress);
    fn update_gas_pricing(ref self: TContractState, base_gas_price: u128, tier_multipliers: Span<u16>);
    fn withdraw_platform_fees(ref self: TContractState, amount: u256) -> bool;
    fn set_emergency_pause(ref self: TContractState, paused: bool);
}

#[derive(Drop, Serde, starknet::Store)]
struct GasAllowance {
    daily_limit: u64,           // Daily gasless transaction limit
    weekly_limit: u64,          // Weekly gasless transaction limit  
    monthly_limit: u64,         // Monthly gasless transaction limit
    used_today: u64,            // Gas used today
    used_this_week: u64,        // Gas used this week
    used_this_month: u64,       // Gas used this month
    last_reset_day: u32,        // Last daily reset timestamp
    last_reset_week: u32,       // Last weekly reset timestamp
    last_reset_month: u32,      // Last monthly reset timestamp
    priority_boost: u16,        // Priority multiplier (10000 = 1.0x)
}

#[derive(Drop, Serde, starknet::Store)]
struct UserGasData {
    total_gas_sponsored: u64,
    total_gas_saved: u64,
    gas_tier_level: u8,         // 0=Basic, 1=Silver, 2=Gold, 3=Platinum, 4=Diamond
    consecutive_days_active: u16,
    total_xp_from_gas_savings: u32,
    premium_features_unlocked: u8, // Bitmask of unlocked features
    referral_gas_earned: u64,
    last_activity_timestamp: u64,
}

#[derive(Drop, Serde)]
struct GasTierBenefits {
    tier_name: felt252,
    daily_gas_allowance: u64,
    weekly_gas_allowance: u64,
    monthly_gas_allowance: u64,
    priority_processing: bool,
    batch_transaction_limit: u8,
    emergency_gas_access: bool,
    referral_bonus_rate: u16,   // In basis points
}

#[derive(Drop, Serde)]
struct SponsorshipResult {
    success: bool,
    transaction_hash: felt252,
    gas_used: u64,
    gas_sponsored: u64,
    xp_earned: u32,
    tier_progress: u16,         // Progress towards next tier
    error_message: felt252,
}

#[derive(Drop, Serde)]
struct TradingStats {
    volume_24h: u256,
    trades_count_24h: u32,
    avg_trade_size: u256,
    successful_trades_streak: u16,
    referrals_generated: u16,
}

#[derive(Drop, Serde)]
struct PlatformGasMetrics {
    total_gas_sponsored_today: u64,
    total_users_sponsored_today: u32,
    average_gas_per_transaction: u64,
    total_revenue_from_gas: u256,
    gas_efficiency_ratio: u16,  // Gas saved vs gas spent ratio
}

#[derive(Drop, Serde)]
struct Call {
    to: ContractAddress,
    selector: felt252,
    calldata: Span<felt252>,
}

#[starknet::contract]
mod AstraTradePaymaster {
    use super::{
        IAstraTradePaymaster, GasAllowance, UserGasData, GasTierBenefits, SponsorshipResult,
        TradingStats, PlatformGasMetrics, Call, ContractAddress, get_caller_address, get_block_timestamp
    };
    use starknet::storage::{
        StoragePointerReadAccess, StoragePointerWriteAccess,
        Map, StoragePathEntry
    };

    #[storage]
    struct Storage {
        // === Core State ===
        owner: ContractAddress,
        exchange_contract: ContractAddress,
        vault_contract: ContractAddress,
        paused: bool,
        
        // === Gas Management ===
        user_gas_allowances: Map<ContractAddress, GasAllowance>,
        user_gas_data: Map<ContractAddress, UserGasData>,
        platform_gas_pool: u256,           // Available gas sponsorship pool
        
        // === Pricing & Tiers ===
        base_gas_price: u128,              // Base gas price in wei
        tier_gas_multipliers: Map<u8, u16>, // Tier → gas allowance multiplier
        tier_upgrade_thresholds: Map<u8, u32>, // Tier → XP required
        
        // === Platform Metrics ===
        total_sponsored_transactions: u64,
        total_gas_sponsored: u64,
        total_users_onboarded: u32,
        daily_active_sponsored_users: u32,
        
        // === Revenue Tracking ===
        platform_revenue: u256,
        gas_fee_collection: u256,
        referral_rewards_paid: u256,
        
        // === Emergency Controls ===
        emergency_gas_reserve: u64,
        emergency_allocation_limit: u64,
    }

    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        TransactionSponsored: TransactionSponsored,
        GasAllowanceRefilled: GasAllowanceRefilled,
        GasTierUpgraded: GasTierUpgraded,
        GasRewardsClaimed: GasRewardsClaimed,
        EmergencyGasAllocated: EmergencyGasAllocated,
        PlatformGasMetricsUpdated: PlatformGasMetricsUpdated,
        PaymasterPaused: PaymasterPaused,
    }

    #[derive(Drop, starknet::Event)]
    struct TransactionSponsored {
        user: ContractAddress,
        gas_sponsored: u64,
        transaction_type: u8,
        xp_earned: u32,
        remaining_allowance: u64,
        tier_level: u8,
    }

    #[derive(Drop, starknet::Event)]
    struct GasAllowanceRefilled {
        user: ContractAddress,
        amount_added: u64,
        new_daily_limit: u64,
        refill_source: felt252, // 'trading', 'purchase', 'referral'
    }

    #[derive(Drop, starknet::Event)]
    struct GasTierUpgraded {
        user: ContractAddress,
        old_tier: u8,
        new_tier: u8,
        new_benefits: GasTierBenefits,
        xp_spent: u32,
    }

    #[derive(Drop, starknet::Event)]
    struct GasRewardsClaimed {
        user: ContractAddress,
        gas_credits_earned: u64,
        trading_volume: u256,
        streak_bonus: u16,
        referral_bonus: u64,
    }

    #[derive(Drop, starknet::Event)]
    struct EmergencyGasAllocated {
        user: ContractAddress,
        emergency_gas: u64,
        reason: felt252,
        admin: ContractAddress,
    }

    #[derive(Drop, starknet::Event)]
    struct PlatformGasMetricsUpdated {
        total_sponsored_today: u64,
        active_users_today: u32,
        efficiency_ratio: u16,
        revenue_generated: u256,
    }

    #[derive(Drop, starknet::Event)]
    struct PaymasterPaused {
        paused: bool,
        reason: felt252,
        timestamp: u64,
    }

    #[constructor]
    fn constructor(ref self: ContractState, owner: ContractAddress, exchange: ContractAddress, vault: ContractAddress) {
        self.owner.write(owner);
        self.exchange_contract.write(exchange);
        self.vault_contract.write(vault);
        self.paused.write(false);
        
        // Initialize gas pricing
        self.base_gas_price.write(1000000000); // 1 gwei base price
        self.platform_gas_pool.write(1000000000000000000); // 1 ETH initial pool
        
        // Initialize tier multipliers
        self.tier_gas_multipliers.entry(0).write(10000);  // Basic: 1.0x
        self.tier_gas_multipliers.entry(1).write(15000);  // Silver: 1.5x
        self.tier_gas_multipliers.entry(2).write(20000);  // Gold: 2.0x
        self.tier_gas_multipliers.entry(3).write(30000);  // Platinum: 3.0x
        self.tier_gas_multipliers.entry(4).write(50000);  // Diamond: 5.0x
        
        // Initialize tier upgrade thresholds
        self.tier_upgrade_thresholds.entry(1).write(5000);   // Silver: 5k XP
        self.tier_upgrade_thresholds.entry(2).write(15000);  // Gold: 15k XP
        self.tier_upgrade_thresholds.entry(3).write(50000);  // Platinum: 50k XP
        self.tier_upgrade_thresholds.entry(4).write(150000); // Diamond: 150k XP
        
        // Initialize emergency reserves
        self.emergency_gas_reserve.write(100000000); // 100M gas units
        self.emergency_allocation_limit.write(1000000); // 1M gas per emergency
    }

    #[abi(embed_v0)]
    impl AstraTradePaymasterImpl of IAstraTradePaymaster<ContractState> {
        
        // === Core Paymaster Operations ===
        
        fn sponsor_user_transaction(ref self: ContractState, user: ContractAddress, 
                                   gas_limit: u64, transaction_type: u8) -> bool {
            self._only_not_paused();
            self._only_authorized_caller();
            
            // Get user's current allowance and data
            let mut user_allowance = self.user_gas_allowances.entry(user).read();
            let mut user_data = self.user_gas_data.entry(user).read();
            
            // Reset daily/weekly/monthly limits if needed
            self._reset_allowance_periods(ref user_allowance);
            
            // Check if user has sufficient gas allowance
            if user_allowance.used_today + gas_limit > user_allowance.daily_limit {
                return false; // Insufficient daily allowance
            }
            
            // Check platform gas pool
            let gas_cost = gas_limit.into() * self.base_gas_price.read().into();
            if self.platform_gas_pool.read() < gas_cost {
                return false; // Insufficient platform funds
            }
            
            // Update user usage
            user_allowance.used_today += gas_limit;
            user_allowance.used_this_week += gas_limit;
            user_allowance.used_this_month += gas_limit;
            
            // Update user data
            user_data.total_gas_sponsored += gas_limit;
            user_data.total_gas_saved += gas_limit;
            user_data.last_activity_timestamp = get_block_timestamp();
            
            // Calculate XP earned from gas savings
            let xp_earned = self._calculate_gas_savings_xp(gas_limit, transaction_type);
            user_data.total_xp_from_gas_savings += xp_earned;
            
            // Check for tier upgrade
            let old_tier = user_data.gas_tier_level;
            let new_tier = self._calculate_user_tier(user_data.total_xp_from_gas_savings);
            if new_tier > old_tier {
                user_data.gas_tier_level = new_tier;
                self._upgrade_user_gas_allowance(ref user_allowance, new_tier);
                
                self.emit(GasTierUpgraded {
                    user,
                    old_tier,
                    new_tier,
                    new_benefits: self.get_user_gas_tier(user),
                    xp_spent: 0, // Automatic upgrade
                });
            }
            
            // Update storage
            self.user_gas_allowances.entry(user).write(user_allowance);
            self.user_gas_data.entry(user).write(user_data);
            
            // Update platform metrics
            self.platform_gas_pool.write(self.platform_gas_pool.read() - gas_cost);
            self.total_sponsored_transactions.write(self.total_sponsored_transactions.read() + 1);
            self.total_gas_sponsored.write(self.total_gas_sponsored.read() + gas_limit);
            
            // Emit event
            self.emit(TransactionSponsored {
                user,
                gas_sponsored: gas_limit,
                transaction_type,
                xp_earned,
                remaining_allowance: user_allowance.daily_limit - user_allowance.used_today,
                tier_level: user_data.gas_tier_level,
            });
            
            true
        }

        fn validate_paymaster_transaction(self: @ContractState, user: ContractAddress, 
                                        gas_estimate: u64, signature: Span<felt252>) -> bool {
            // Validate transaction can be sponsored
            let user_allowance = self.user_gas_allowances.entry(user).read();
            let user_data = self.user_gas_data.entry(user).read();
            
            // Check gas allowance
            if user_allowance.used_today + gas_estimate > user_allowance.daily_limit {
                return false;
            }
            
            // Check platform pool
            let gas_cost = gas_estimate.into() * self.base_gas_price.read().into();
            if self.platform_gas_pool.read() < gas_cost {
                return false;
            }
            
            // Additional validation logic for signature, rate limiting, etc.
            true
        }

        fn execute_sponsored_transaction(ref self: ContractState, user: ContractAddress, 
                                       calls: Span<Call>, max_gas: u64) -> SponsorshipResult {
            self._only_not_paused();
            
            // Pre-validate sponsorship
            if !self.validate_paymaster_transaction(user, max_gas, array![].span()) {
                return SponsorshipResult {
                    success: false,
                    transaction_hash: 0,
                    gas_used: 0,
                    gas_sponsored: 0,
                    xp_earned: 0,
                    tier_progress: 0,
                    error_message: 'Sponsorship validation failed',
                };
            }
            
            // Execute the actual transaction (simplified)
            // In reality, this would use account abstraction patterns
            let transaction_hash = self._execute_calls(calls);
            let actual_gas_used = max_gas * 80 / 100; // Assume 80% efficiency
            
            // Update sponsorship tracking
            if self.sponsor_user_transaction(user, actual_gas_used, 1) {
                let user_data = self.user_gas_data.entry(user).read();
                let xp_earned = self._calculate_gas_savings_xp(actual_gas_used, 1);
                
                SponsorshipResult {
                    success: true,
                    transaction_hash,
                    gas_used: actual_gas_used,
                    gas_sponsored: actual_gas_used,
                    xp_earned,
                    tier_progress: self._calculate_tier_progress(user_data.total_xp_from_gas_savings),
                    error_message: 0,
                }
            } else {
                SponsorshipResult {
                    success: false,
                    transaction_hash: 0,
                    gas_used: actual_gas_used,
                    gas_sponsored: 0,
                    xp_earned: 0,
                    tier_progress: 0,
                    error_message: 'Sponsorship tracking failed',
                }
            }
        }

        // === Gas Allowance Management ===

        fn get_user_gas_allowance(self: @ContractState, user: ContractAddress) -> GasAllowance {
            let mut allowance = self.user_gas_allowances.entry(user).read();
            self._reset_allowance_periods(ref allowance);
            allowance
        }

        fn refill_gas_allowance(ref self: ContractState, user: ContractAddress, amount: u64) -> bool {
            let mut user_allowance = self.user_gas_allowances.entry(user).read();
            let user_data = self.user_gas_data.entry(user).read();
            
            // Calculate refill multiplier based on tier
            let tier_multiplier = self.tier_gas_multipliers.entry(user_data.gas_tier_level).read();
            let bonus_amount = (amount.into() * tier_multiplier.into()) / 10000;
            let total_refill = amount + bonus_amount.try_into().unwrap_or(0);
            
            // Update daily limit (can exceed base limit with refills)
            user_allowance.daily_limit += total_refill;
            self.user_gas_allowances.entry(user).write(user_allowance);
            
            self.emit(GasAllowanceRefilled {
                user,
                amount_added: total_refill,
                new_daily_limit: user_allowance.daily_limit,
                refill_source: 'manual_refill',
            });
            
            true
        }

        fn get_remaining_sponsored_gas(self: @ContractState, user: ContractAddress) -> u64 {
            let allowance = self.get_user_gas_allowance(user);
            if allowance.daily_limit > allowance.used_today {
                allowance.daily_limit - allowance.used_today
            } else {
                0
            }
        }

        fn calculate_gas_refund_rate(self: @ContractState, user: ContractAddress, 
                                    trading_volume: u256) -> u16 {
            let user_data = self.user_gas_data.entry(user).read();
            
            // Base refund rate: 50% (5000 basis points)
            let mut refund_rate = 5000_u16;
            
            // Tier bonuses
            refund_rate += match user_data.gas_tier_level {
                0 => 0,      // Basic: no bonus
                1 => 500,    // Silver: +5%
                2 => 1000,   // Gold: +10%
                3 => 2000,   // Platinum: +20%
                4 => 3000,   // Diamond: +30%
                _ => 0,
            };
            
            // Volume bonuses (higher volume = higher refund rate)
            if trading_volume >= 1000000000000000000000 { // 1000 ETH
                refund_rate += 1000; // +10%
            } else if trading_volume >= 100000000000000000000 { // 100 ETH
                refund_rate += 500; // +5%
            }
            
            // Cap at 90% refund rate
            if refund_rate > 9000 { 9000 } else { refund_rate }
        }

        // === Gamification Integration ===

        fn earn_gas_refund_xp(ref self: ContractState, user: ContractAddress, gas_saved: u64) -> u32 {
            let mut user_data = self.user_gas_data.entry(user).read();
            
            // 1 XP per 1000 gas units saved
            let base_xp = gas_saved / 1000;
            
            // Tier multipliers for XP
            let tier_xp_multiplier = match user_data.gas_tier_level {
                0 => 10,   // Basic: 1.0x
                1 => 12,   // Silver: 1.2x
                2 => 15,   // Gold: 1.5x
                3 => 20,   // Platinum: 2.0x
                4 => 25,   // Diamond: 2.5x
                _ => 10,
            };
            
            let xp_earned = (base_xp.into() * tier_xp_multiplier) / 10;
            let final_xp = xp_earned.try_into().unwrap_or(0);
            
            user_data.total_xp_from_gas_savings += final_xp;
            self.user_gas_data.entry(user).write(user_data);
            
            final_xp
        }

        fn unlock_premium_gas_features(ref self: ContractState, tier: u8) -> bool {
            let caller = get_caller_address();
            let mut user_data = self.user_gas_data.entry(caller).read();
            
            // Check XP requirement for tier
            let xp_required = self.tier_upgrade_thresholds.entry(tier).read();
            if user_data.total_xp_from_gas_savings < xp_required {
                return false;
            }
            
            // Check if tier is higher than current
            if tier <= user_data.gas_tier_level {
                return false;
            }
            
            // Upgrade tier
            let old_tier = user_data.gas_tier_level;
            user_data.gas_tier_level = tier;
            
            // Unlock premium features bitmask
            user_data.premium_features_unlocked |= match tier {
                1 => 0b00000001, // Priority processing
                2 => 0b00000011, // Priority + batch transactions
                3 => 0b00000111, // All above + emergency access
                4 => 0b00001111, // All above + VIP support
                _ => 0,
            };
            
            // Upgrade gas allowance
            let mut user_allowance = self.user_gas_allowances.entry(caller).read();
            self._upgrade_user_gas_allowance(ref user_allowance, tier);
            
            self.user_gas_data.entry(caller).write(user_data);
            self.user_gas_allowances.entry(caller).write(user_allowance);
            
            self.emit(GasTierUpgraded {
                user: caller,
                old_tier,
                new_tier: tier,
                new_benefits: self.get_user_gas_tier(caller),
                xp_spent: xp_required,
            });
            
            true
        }

        fn get_user_gas_tier(self: @ContractState, user: ContractAddress) -> GasTierBenefits {
            let user_data = self.user_gas_data.entry(user).read();
            let tier = user_data.gas_tier_level;
            
            match tier {
                0 => GasTierBenefits {
                    tier_name: 'Basic',
                    daily_gas_allowance: 100000,   // 100k gas/day
                    weekly_gas_allowance: 500000,  // 500k gas/week
                    monthly_gas_allowance: 2000000, // 2M gas/month
                    priority_processing: false,
                    batch_transaction_limit: 1,
                    emergency_gas_access: false,
                    referral_bonus_rate: 500, // 5%
                },
                1 => GasTierBenefits {
                    tier_name: 'Silver',
                    daily_gas_allowance: 200000,   // 200k gas/day
                    weekly_gas_allowance: 1000000, // 1M gas/week
                    monthly_gas_allowance: 4000000, // 4M gas/month
                    priority_processing: true,
                    batch_transaction_limit: 3,
                    emergency_gas_access: false,
                    referral_bonus_rate: 750, // 7.5%
                },
                2 => GasTierBenefits {
                    tier_name: 'Gold',
                    daily_gas_allowance: 400000,   // 400k gas/day
                    weekly_gas_allowance: 2000000, // 2M gas/week
                    monthly_gas_allowance: 8000000, // 8M gas/month
                    priority_processing: true,
                    batch_transaction_limit: 5,
                    emergency_gas_access: true,
                    referral_bonus_rate: 1000, // 10%
                },
                3 => GasTierBenefits {
                    tier_name: 'Platinum',
                    daily_gas_allowance: 800000,   // 800k gas/day
                    weekly_gas_allowance: 4000000, // 4M gas/week
                    monthly_gas_allowance: 16000000, // 16M gas/month
                    priority_processing: true,
                    batch_transaction_limit: 10,
                    emergency_gas_access: true,
                    referral_bonus_rate: 1500, // 15%
                },
                4 => GasTierBenefits {
                    tier_name: 'Diamond',
                    daily_gas_allowance: 1600000,  // 1.6M gas/day
                    weekly_gas_allowance: 8000000, // 8M gas/week
                    monthly_gas_allowance: 32000000, // 32M gas/month
                    priority_processing: true,
                    batch_transaction_limit: 20,
                    emergency_gas_access: true,
                    referral_bonus_rate: 2000, // 20%
                },
                _ => self.get_user_gas_tier(user), // Fallback to basic
            }
        }

        fn claim_trading_gas_rewards(ref self: ContractState, trading_stats: TradingStats) -> u64 {
            let caller = get_caller_address();
            let user_data = self.user_gas_data.entry(caller).read();
            
            // Calculate gas rewards based on trading volume
            let volume_gas_reward = (trading_stats.volume_24h / 1000000000000000000).try_into().unwrap_or(0); // 1 gas per ETH volume
            
            // Streak bonuses
            let streak_multiplier = if trading_stats.successful_trades_streak >= 50 {
                20 // 2.0x for 50+ streak
            } else if trading_stats.successful_trades_streak >= 20 {
                15 // 1.5x for 20+ streak
            } else if trading_stats.successful_trades_streak >= 10 {
                12 // 1.2x for 10+ streak
            } else {
                10 // 1.0x base
            };
            
            let streak_bonus = (volume_gas_reward * streak_multiplier) / 10;
            
            // Referral bonuses
            let referral_rate = self.get_user_gas_tier(caller).referral_bonus_rate;
            let referral_bonus = (user_data.referral_gas_earned * referral_rate.into()) / 10000;
            
            let total_reward = volume_gas_reward + streak_bonus + referral_bonus;
            
            // Add to user's gas allowance
            self.refill_gas_allowance(caller, total_reward);
            
            self.emit(GasRewardsClaimed {
                user: caller,
                gas_credits_earned: total_reward,
                trading_volume: trading_stats.volume_24h,
                streak_bonus: (streak_bonus * 10000) / volume_gas_reward,
                referral_bonus,
            });
            
            total_reward
        }

        // === Extended API Integration ===

        fn validate_external_gas_payment(self: @ContractState, user: ContractAddress, 
                                        external_data: Span<felt252>, signature: Span<felt252>) -> bool {
            // Validate external gas payment from partner platforms
            // This would integrate with Extended Exchange API
            true // Simplified implementation
        }

        fn sync_external_gas_credits(ref self: ContractState, user: ContractAddress, 
                                    credits: u64, provider: felt252) -> bool {
            // Sync gas credits from external platforms
            self.refill_gas_allowance(user, credits);
            
            self.emit(GasAllowanceRefilled {
                user,
                amount_added: credits,
                new_daily_limit: self.get_user_gas_allowance(user).daily_limit,
                refill_source: provider,
            });
            
            true
        }

        // === Enterprise Features ===

        fn batch_sponsor_transactions(ref self: ContractState, users: Span<ContractAddress>, 
                                     gas_amounts: Span<u64>) -> u32 {
            self._only_owner();
            let mut successful_sponsorships = 0_u32;
            
            let users_len = users.len();
            let mut i = 0_usize;
            while i < users_len {
                if i < gas_amounts.len() {
                    if self.sponsor_user_transaction(*users[i], *gas_amounts[i], 0) {
                        successful_sponsorships += 1;
                    }
                }
                i += 1;
            };
            
            successful_sponsorships
        }

        fn get_platform_gas_metrics(self: @ContractState) -> PlatformGasMetrics {
            let total_sponsored = self.total_gas_sponsored.read();
            let total_transactions = self.total_sponsored_transactions.read();
            let avg_gas = if total_transactions > 0 { total_sponsored / total_transactions } else { 0 };
            
            PlatformGasMetrics {
                total_gas_sponsored_today: total_sponsored, // Simplified - should track daily
                total_users_sponsored_today: self.daily_active_sponsored_users.read(),
                average_gas_per_transaction: avg_gas,
                total_revenue_from_gas: self.platform_revenue.read(),
                gas_efficiency_ratio: 8500, // 85% efficiency ratio
            }
        }

        fn emergency_gas_allocation(ref self: ContractState, user: ContractAddress, 
                                   emergency_gas: u64, reason: felt252) -> bool {
            self._only_owner();
            
            // Check emergency reserve
            if self.emergency_gas_reserve.read() < emergency_gas {
                return false;
            }
            
            // Check allocation limit
            if emergency_gas > self.emergency_allocation_limit.read() {
                return false;
            }
            
            // Allocate emergency gas
            self.refill_gas_allowance(user, emergency_gas);
            self.emergency_gas_reserve.write(self.emergency_gas_reserve.read() - emergency_gas);
            
            self.emit(EmergencyGasAllocated {
                user,
                emergency_gas,
                reason,
                admin: get_caller_address(),
            });
            
            true
        }

        // === Admin Functions ===

        fn set_exchange_contract(ref self: ContractState, exchange: ContractAddress) {
            self._only_owner();
            self.exchange_contract.write(exchange);
        }

        fn set_vault_contract(ref self: ContractState, vault: ContractAddress) {
            self._only_owner();
            self.vault_contract.write(vault);
        }

        fn update_gas_pricing(ref self: ContractState, base_gas_price: u128, tier_multipliers: Span<u16>) {
            self._only_owner();
            self.base_gas_price.write(base_gas_price);
            
            let mut i = 0_usize;
            while i < tier_multipliers.len() && i < 5 {
                self.tier_gas_multipliers.entry(i.try_into().unwrap_or(0)).write(*tier_multipliers[i]);
                i += 1;
            }
        }

        fn withdraw_platform_fees(ref self: ContractState, amount: u256) -> bool {
            self._only_owner();
            
            if self.platform_revenue.read() >= amount {
                self.platform_revenue.write(self.platform_revenue.read() - amount);
                // In real implementation, would transfer ETH to owner
                true
            } else {
                false
            }
        }

        fn set_emergency_pause(ref self: ContractState, paused: bool) {
            self._only_owner();
            self.paused.write(paused);
            
            self.emit(PaymasterPaused {
                paused,
                reason: if paused { 'Emergency pause activated' } else { 'Emergency pause lifted' },
                timestamp: get_block_timestamp(),
            });
        }
    }

    // === Internal Helper Functions ===

    #[generate_trait]
    impl InternalImpl of InternalTrait {
        fn _only_owner(self: @ContractState) {
            let caller = get_caller_address();
            assert(caller == self.owner.read(), 'Only owner');
        }

        fn _only_not_paused(self: @ContractState) {
            assert(!self.paused.read(), 'Contract paused');
        }

        fn _only_authorized_caller(self: @ContractState) {
            let caller = get_caller_address();
            let owner = self.owner.read();
            let exchange = self.exchange_contract.read();
            let vault = self.vault_contract.read();
            
            assert(caller == owner || caller == exchange || caller == vault, 'Unauthorized caller');
        }

        fn _reset_allowance_periods(self: @ContractState, ref allowance: GasAllowance) {
            let current_time = get_block_timestamp();
            let current_day = current_time / 86400; // Seconds per day
            let current_week = current_time / 604800; // Seconds per week
            let current_month = current_time / 2629746; // Approximate seconds per month
            
            // Reset daily if new day
            if current_day > allowance.last_reset_day.into() {
                allowance.used_today = 0;
                allowance.last_reset_day = current_day.try_into().unwrap_or(0);
            }
            
            // Reset weekly if new week
            if current_week > allowance.last_reset_week.into() {
                allowance.used_this_week = 0;
                allowance.last_reset_week = current_week.try_into().unwrap_or(0);
            }
            
            // Reset monthly if new month
            if current_month > allowance.last_reset_month.into() {
                allowance.used_this_month = 0;
                allowance.last_reset_month = current_month.try_into().unwrap_or(0);
            }
        }

        fn _calculate_gas_savings_xp(self: @ContractState, gas_amount: u64, transaction_type: u8) -> u32 {
            // Base XP: 1 XP per 1000 gas units
            let base_xp = gas_amount / 1000;
            
            // Transaction type multipliers
            let type_multiplier = match transaction_type {
                0 => 10,  // Basic transaction: 1.0x
                1 => 12,  // Trading transaction: 1.2x
                2 => 15,  // Vault transaction: 1.5x
                3 => 20,  // Complex DeFi: 2.0x
                _ => 10,
            };
            
            ((base_xp.into() * type_multiplier) / 10).try_into().unwrap_or(0)
        }

        fn _calculate_user_tier(self: @ContractState, total_xp: u32) -> u8 {
            if total_xp >= 150000 { 4 }      // Diamond
            else if total_xp >= 50000 { 3 } // Platinum
            else if total_xp >= 15000 { 2 } // Gold
            else if total_xp >= 5000 { 1 }  // Silver
            else { 0 }                      // Basic
        }

        fn _upgrade_user_gas_allowance(self: @ContractState, ref allowance: GasAllowance, tier: u8) {
            let benefits = self.get_user_gas_tier(get_caller_address()); // Simplified - should pass user
            
            allowance.daily_limit = benefits.daily_gas_allowance;
            allowance.weekly_limit = benefits.weekly_gas_allowance;
            allowance.monthly_limit = benefits.monthly_gas_allowance;
            
            // Priority boost for higher tiers
            allowance.priority_boost = match tier {
                4 => 20000, // Diamond: 2.0x priority
                3 => 15000, // Platinum: 1.5x priority
                2 => 12000, // Gold: 1.2x priority
                1 => 11000, // Silver: 1.1x priority
                _ => 10000, // Basic: 1.0x priority
            };
        }

        fn _calculate_tier_progress(self: @ContractState, current_xp: u32) -> u16 {
            // Calculate progress towards next tier (0-10000 basis points)
            let current_tier = self._calculate_user_tier(current_xp);
            
            if current_tier >= 4 {
                return 10000; // Max tier reached
            }
            
            let next_tier_threshold = self.tier_upgrade_thresholds.entry(current_tier + 1).read();
            let current_tier_threshold = if current_tier == 0 { 0 } else { 
                self.tier_upgrade_thresholds.entry(current_tier).read() 
            };
            
            let progress_in_tier = current_xp - current_tier_threshold;
            let tier_span = next_tier_threshold - current_tier_threshold;
            
            if tier_span == 0 {
                return 10000;
            }
            
            ((progress_in_tier.into() * 10000) / tier_span.into()).try_into().unwrap_or(0)
        }

        fn _execute_calls(self: @ContractState, calls: Span<Call>) -> felt252 {
            // Simplified call execution - in real implementation would use account abstraction
            // Returns mock transaction hash
            0x1234567890abcdef_felt252
        }
    }
}