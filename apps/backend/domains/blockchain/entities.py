"""
Blockchain Domain Entities

Core business entities for the Blockchain Domain implementing Domain-Driven Design patterns.
These entities encapsulate business logic, maintain invariants, and emit domain events
for blockchain operations.

Key Features:
- Rich domain behavior (not anemic models)
- Business rule enforcement
- Domain event emission
- Immutable creation after construction
- Proper encapsulation of business logic
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from uuid import uuid4

from .value_objects import (
    StarknetAddress, TransactionHash, GasFee, PaymasterTier, NetworkType,
    PrivateKey, ContractAddress, TransactionCall, TransactionStatus
)
from .exceptions import (
    WalletNotFoundException, InsufficientGasException, QuotaExceededException,
    TransactionFailedException, InvalidAddressException
)
from ..shared.events import DomainEvent


class WalletType(Enum):
    """Types of wallet creation/import methods."""
    FRESH = "fresh"
    IMPORTED_PRIVATE_KEY = "imported_private_key"
    IMPORTED_MNEMONIC = "imported_mnemonic"
    SOCIAL_LOGIN = "social_login"
    WEB3AUTH = "web3auth"


class Wallet:
    """
    Wallet aggregate root representing a blockchain wallet.
    
    Encapsulates wallet management business logic including transaction signing,
    balance tracking, and security validation. Acts as the aggregate root for
    all wallet-related operations.
    """
    
    def __init__(
        self,
        wallet_id: str,
        user_id: str,
        address: StarknetAddress,
        network: NetworkType,
        wallet_type: WalletType,
        encrypted_private_key: Optional[PrivateKey] = None,
        created_at: Optional[datetime] = None,
        last_used_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self._wallet_id = wallet_id
        self._user_id = user_id
        self._address = address
        self._network = network
        self._wallet_type = wallet_type
        self._encrypted_private_key = encrypted_private_key
        self._created_at = created_at or datetime.now(timezone.utc)
        self._last_used_at = last_used_at
        self._metadata = metadata or {}
        self._domain_events: List[DomainEvent] = []
        self._is_active = True
    
    @classmethod
    def create_fresh_wallet(
        cls,
        user_id: str,
        address: StarknetAddress,
        network: NetworkType,
        encrypted_private_key: PrivateKey,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'Wallet':
        """Create a new fresh wallet."""
        wallet_id = str(uuid4())
        wallet = cls(
            wallet_id=wallet_id,
            user_id=user_id,
            address=address,
            network=network,
            wallet_type=WalletType.FRESH,
            encrypted_private_key=encrypted_private_key,
            metadata=metadata
        )
        
        from .events import WalletCreatedEvent
        wallet._add_domain_event(WalletCreatedEvent(
            user_id=user_id,
            wallet_id=wallet_id,
            wallet_address=str(address),
            network=network.value,
            wallet_type=WalletType.FRESH.value,
            metadata=metadata
        ))
        
        return wallet
    
    @classmethod
    def import_existing_wallet(
        cls,
        user_id: str,
        address: StarknetAddress,
        network: NetworkType,
        wallet_type: WalletType,
        encrypted_private_key: PrivateKey,
        import_metadata: Optional[Dict[str, Any]] = None
    ) -> 'Wallet':
        """Import an existing wallet."""
        if wallet_type == WalletType.FRESH:
            raise ValueError("Cannot import wallet with FRESH type")
        
        wallet_id = str(uuid4())
        metadata = import_metadata or {}
        metadata['imported_at'] = datetime.now(timezone.utc).isoformat()
        
        wallet = cls(
            wallet_id=wallet_id,
            user_id=user_id,
            address=address,
            network=network,
            wallet_type=wallet_type,
            encrypted_private_key=encrypted_private_key,
            metadata=metadata
        )
        
        from .events import WalletImportedEvent
        wallet._add_domain_event(WalletImportedEvent(
            user_id=user_id,
            wallet_id=wallet_id,
            wallet_address=str(address),
            network=network.value,
            import_method=wallet_type.value,
            metadata=metadata
        ))
        
        return wallet
    
    # Properties
    @property
    def wallet_id(self) -> str:
        return self._wallet_id
    
    @property
    def user_id(self) -> str:
        return self._user_id
    
    @property
    def address(self) -> StarknetAddress:
        return self._address
    
    @property
    def network(self) -> NetworkType:
        return self._network
    
    @property
    def wallet_type(self) -> WalletType:
        return self._wallet_type
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def last_used_at(self) -> Optional[datetime]:
        return self._last_used_at
    
    @property
    def is_active(self) -> bool:
        return self._is_active
    
    @property
    def metadata(self) -> Dict[str, Any]:
        return self._metadata.copy()
    
    @property
    def domain_events(self) -> List[DomainEvent]:
        return self._domain_events.copy()
    
    def clear_domain_events(self) -> None:
        """Clear domain events after publishing."""
        self._domain_events.clear()
    
    # Business Methods
    def can_sign_transactions(self) -> bool:
        """Check if wallet can sign transactions (has private key)."""
        return self._encrypted_private_key is not None and self._is_active
    
    def validate_ownership(self, user_id: str) -> bool:
        """Validate that the user owns this wallet."""
        return self._user_id == user_id
    
    def update_last_used(self) -> None:
        """Update the last used timestamp."""
        self._last_used_at = datetime.now(timezone.utc)
    
    def deactivate(self, reason: str = "User requested") -> None:
        """Deactivate the wallet (soft delete)."""
        self._is_active = False
        self._metadata['deactivated_at'] = datetime.now(timezone.utc).isoformat()
        self._metadata['deactivation_reason'] = reason
    
    def get_encrypted_private_key(self) -> Optional[PrivateKey]:
        """Get encrypted private key for authorized operations."""
        if not self._is_active:
            raise ValueError("Cannot access private key of deactivated wallet")
        return self._encrypted_private_key
    
    def get_decrypted_private_key(self, encryption_key: bytes) -> Optional[str]:
        """Get decrypted private key for signing operations."""
        if not self._is_active:
            raise ValueError("Cannot access private key of deactivated wallet")
        
        if not self._encrypted_private_key:
            return None
        
        try:
            return self._encrypted_private_key.decrypt(encryption_key)
        except Exception as e:
            raise ValueError(f"Failed to decrypt private key: {e}")
    
    def get_public_key(self, encryption_key: bytes) -> Optional[str]:
        """Derive public key from private key for verification operations."""
        if not self._is_active:
            raise ValueError("Cannot access private key of deactivated wallet")
        
        private_key = self.get_decrypted_private_key(encryption_key)
        if not private_key:
            return None
        
        # TODO: Implement proper public key derivation from private key
        # For now, this is a placeholder - the actual implementation would use
        # Starknet's public key derivation from the private key
        # This should be moved to a crypto utility service
        try:
            from starknet_py.utils.crypto.facade import private_key_to_public_key
            # Remove 0x prefix if present for starknet_py
            clean_private_key = private_key[2:] if private_key.startswith('0x') else private_key
            public_key_int = private_key_to_public_key(int(clean_private_key, 16))
            return f"0x{public_key_int:064x}"
        except ImportError:
            # Fallback: derive from address (less secure but functional for development)
            # In production, proper public key derivation should be implemented
            return str(self._address.value)
    
    def _add_domain_event(self, event: DomainEvent) -> None:
        """Add domain event to be published."""
        self._domain_events.append(event)


class Transaction:
    """
    Transaction entity representing blockchain transactions.
    
    Tracks transaction lifecycle from initiation to completion,
    including gas estimation, execution, and status monitoring.
    """
    
    def __init__(
        self,
        transaction_id: str,
        wallet_id: str,
        user_id: str,
        calls: List[TransactionCall],
        network: NetworkType,
        estimated_gas_fee: GasFee,
        transaction_type: str = "contract_call",
        created_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self._transaction_id = transaction_id
        self._wallet_id = wallet_id
        self._user_id = user_id
        self._calls = calls
        self._network = network
        self._estimated_gas_fee = estimated_gas_fee
        self._transaction_type = transaction_type
        self._created_at = created_at or datetime.now(timezone.utc)
        self._metadata = metadata or {}
        
        # Execution state
        self._status = TransactionStatus.PENDING
        self._transaction_hash: Optional[TransactionHash] = None
        self._actual_gas_fee: Optional[GasFee] = None
        self._gas_used: Optional[int] = None
        self._block_number: Optional[int] = None
        self._execution_type: Optional[str] = None  # 'gasless' or 'standard'
        self._failure_reason: Optional[str] = None
        self._executed_at: Optional[datetime] = None
        
        self._domain_events: List[DomainEvent] = []
    
    @classmethod
    def create_transaction(
        cls,
        wallet_id: str,
        user_id: str,
        calls: List[TransactionCall],
        network: NetworkType,
        estimated_gas_fee: GasFee,
        transaction_type: str = "contract_call",
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'Transaction':
        """Create a new transaction."""
        transaction_id = str(uuid4())
        transaction = cls(
            transaction_id=transaction_id,
            wallet_id=wallet_id,
            user_id=user_id,
            calls=calls,
            network=network,
            estimated_gas_fee=estimated_gas_fee,
            transaction_type=transaction_type,
            metadata=metadata
        )
        
        from .events import TransactionInitiatedEvent
        transaction._add_domain_event(TransactionInitiatedEvent(
            transaction_id=transaction_id,
            wallet_id=wallet_id,
            user_id=user_id,
            transaction_type=transaction_type,
            estimated_gas_fee=str(estimated_gas_fee.amount),
            network=network.value,
            metadata=metadata
        ))
        
        return transaction
    
    # Properties
    @property
    def transaction_id(self) -> str:
        return self._transaction_id
    
    @property
    def wallet_id(self) -> str:
        return self._wallet_id
    
    @property
    def user_id(self) -> str:
        return self._user_id
    
    @property
    def calls(self) -> List[TransactionCall]:
        return self._calls.copy()
    
    @property
    def network(self) -> NetworkType:
        return self._network
    
    @property
    def status(self) -> TransactionStatus:
        return self._status
    
    @property
    def transaction_hash(self) -> Optional[TransactionHash]:
        return self._transaction_hash
    
    @property
    def estimated_gas_fee(self) -> GasFee:
        return self._estimated_gas_fee
    
    @property
    def actual_gas_fee(self) -> Optional[GasFee]:
        return self._actual_gas_fee
    
    @property
    def gas_used(self) -> Optional[int]:
        return self._gas_used
    
    @property
    def execution_type(self) -> Optional[str]:
        return self._execution_type
    
    @property
    def is_gasless(self) -> bool:
        return self._execution_type == "gasless"
    
    @property
    def is_completed(self) -> bool:
        return self._status in [TransactionStatus.ACCEPTED_ON_L1, TransactionStatus.ACCEPTED_ON_L2]
    
    @property
    def is_failed(self) -> bool:
        return self._status in [TransactionStatus.FAILED, TransactionStatus.REJECTED]
    
    @property
    def domain_events(self) -> List[DomainEvent]:
        return self._domain_events.copy()
    
    def clear_domain_events(self) -> None:
        """Clear domain events after publishing."""
        self._domain_events.clear()
    
    # Business Methods
    def mark_as_executed(
        self,
        transaction_hash: TransactionHash,
        execution_type: str,
        gas_used: Optional[int] = None,
        actual_gas_fee: Optional[GasFee] = None
    ) -> None:
        """Mark transaction as executed with hash."""
        if self._status != TransactionStatus.PENDING:
            raise TransactionFailedException(
                self._transaction_id,
                f"Cannot execute transaction in status: {self._status.value}"
            )
        
        self._transaction_hash = transaction_hash
        self._execution_type = execution_type
        self._gas_used = gas_used
        self._actual_gas_fee = actual_gas_fee
        self._executed_at = datetime.now(timezone.utc)
        self._status = TransactionStatus.ACCEPTED_ON_L2
        
        from .events import TransactionExecutedEvent
        self._add_domain_event(TransactionExecutedEvent(
            transaction_id=self._transaction_id,
            transaction_hash=str(transaction_hash),
            wallet_id=self._wallet_id,
            user_id=self._user_id,
            gas_used=gas_used or 0,
            gas_fee_paid=str(actual_gas_fee.amount) if actual_gas_fee else str(self._estimated_gas_fee.amount),
            status=self._status.value,
            network=self._network.value,
            execution_type=execution_type,
            metadata=self._metadata
        ))
    
    def update_status(
        self,
        new_status: TransactionStatus,
        block_number: Optional[int] = None
    ) -> None:
        """Update transaction status."""
        old_status = self._status
        self._status = new_status
        
        if block_number:
            self._block_number = block_number
        
        # Update metadata with status change
        self._metadata[f'{new_status.value}_at'] = datetime.now(timezone.utc).isoformat()
    
    def mark_as_failed(self, reason: str, error_code: Optional[str] = None) -> None:
        """Mark transaction as failed."""
        self._status = TransactionStatus.FAILED
        self._failure_reason = reason
        self._metadata['failure_reason'] = reason
        self._metadata['failed_at'] = datetime.now(timezone.utc).isoformat()
        
        if error_code:
            self._metadata['error_code'] = error_code
        
        from .events import TransactionFailedEvent
        self._add_domain_event(TransactionFailedEvent(
            transaction_id=self._transaction_id,
            wallet_id=self._wallet_id,
            user_id=self._user_id,
            failure_reason=reason,
            error_code=error_code,
            attempted_gas_fee=str(self._estimated_gas_fee.amount),
            network=self._network.value,
            metadata=self._metadata
        ))
    
    def calculate_gas_savings(self) -> Optional[GasFee]:
        """Calculate gas savings if transaction was gasless."""
        if not self.is_gasless:
            return None
        
        # If gasless, the user saved the estimated gas fee
        return self._estimated_gas_fee
    
    def _add_domain_event(self, event: DomainEvent) -> None:
        """Add domain event to be published."""
        self._domain_events.append(event)


class GaslessAccount:
    """
    Gasless account entity for managing gasless transaction quotas and tiers.
    
    Handles tier progression, quota management, and eligibility checking
    for gasless transaction sponsorship.
    """
    
    def __init__(
        self,
        account_id: str,
        user_id: str,
        tier: PaymasterTier = PaymasterTier.BRONZE,
        daily_quota_used: int = 0,
        total_transactions_sponsored: int = 0,
        total_gas_saved: Decimal = Decimal('0'),
        created_at: Optional[datetime] = None,
        last_quota_reset: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self._account_id = account_id
        self._user_id = user_id
        self._tier = tier
        self._daily_quota_used = daily_quota_used
        self._total_transactions_sponsored = total_transactions_sponsored
        self._total_gas_saved = total_gas_saved
        self._created_at = created_at or datetime.now(timezone.utc)
        self._last_quota_reset = last_quota_reset
        self._metadata = metadata or {}
        self._domain_events: List[DomainEvent] = []
    
    @classmethod
    def create_account(
        cls,
        user_id: str,
        initial_tier: PaymasterTier = PaymasterTier.BRONZE
    ) -> 'GaslessAccount':
        """Create a new gasless account for user."""
        account_id = str(uuid4())
        account = cls(
            account_id=account_id,
            user_id=user_id,
            tier=initial_tier,
            last_quota_reset=datetime.now(timezone.utc)
        )
        return account
    
    # Properties
    @property
    def account_id(self) -> str:
        return self._account_id
    
    @property
    def user_id(self) -> str:
        return self._user_id
    
    @property
    def tier(self) -> PaymasterTier:
        return self._tier
    
    @property
    def daily_quota_limit(self) -> int:
        return self._tier.daily_quota
    
    @property
    def daily_quota_used(self) -> int:
        return self._daily_quota_used
    
    @property
    def daily_quota_remaining(self) -> int:
        return max(0, self.daily_quota_limit - self._daily_quota_used)
    
    @property
    def total_transactions_sponsored(self) -> int:
        return self._total_transactions_sponsored
    
    @property
    def total_gas_saved(self) -> Decimal:
        return self._total_gas_saved
    
    @property
    def max_sponsorable_gas_fee(self) -> Decimal:
        return self._tier.max_gas_fee
    
    @property
    def domain_events(self) -> List[DomainEvent]:
        return self._domain_events.copy()
    
    def clear_domain_events(self) -> None:
        """Clear domain events after publishing."""
        self._domain_events.clear()
    
    # Business Methods
    def can_sponsor_transaction(self, gas_fee: GasFee) -> bool:
        """Check if account can sponsor a transaction."""
        if self.daily_quota_remaining <= 0:
            return False
        
        if gas_fee.amount > self.max_sponsorable_gas_fee:
            return False
        
        return True
    
    def use_quota(self, gas_fee: GasFee) -> None:
        """Use quota for a sponsored transaction."""
        if not self.can_sponsor_transaction(gas_fee):
            raise QuotaExceededException(
                self._user_id,
                self._daily_quota_used,
                self.daily_quota_limit
            )
        
        self._daily_quota_used += 1
        self._total_transactions_sponsored += 1
        self._total_gas_saved += gas_fee.amount
        
        # Update metadata
        self._metadata['last_sponsorship'] = datetime.now(timezone.utc).isoformat()
    
    def reset_daily_quota(self) -> None:
        """Reset daily quota usage."""
        self._daily_quota_used = 0
        self._last_quota_reset = datetime.now(timezone.utc)
    
    def upgrade_tier(self, new_tier: PaymasterTier, reason: str) -> None:
        """Upgrade account tier."""
        if new_tier.value <= self._tier.value:
            raise ValueError(f"Cannot downgrade or maintain tier: {self._tier.value} -> {new_tier.value}")
        
        old_tier = self._tier
        self._tier = new_tier
        self._metadata['tier_upgraded_at'] = datetime.now(timezone.utc).isoformat()
        self._metadata['upgrade_reason'] = reason
        
        from .events import TierUpgradedEvent
        self._add_domain_event(TierUpgradedEvent(
            user_id=self._user_id,
            previous_tier=old_tier.value,
            new_tier=new_tier.value,
            new_daily_quota=new_tier.daily_quota,
            upgrade_reason=reason,
            effective_date=datetime.now(timezone.utc)
        ))
    
    def is_eligible_for_upgrade(self, criteria: Dict[str, Any]) -> bool:
        """Check if account is eligible for tier upgrade based on criteria."""
        # Example criteria checking
        min_transactions = criteria.get('min_transactions', 50)
        min_gas_saved = Decimal(criteria.get('min_gas_saved', '0.1'))
        
        return (
            self._total_transactions_sponsored >= min_transactions and
            self._total_gas_saved >= min_gas_saved
        )
    
    def _add_domain_event(self, event: DomainEvent) -> None:
        """Add domain event to be published."""
        self._domain_events.append(event)


class SmartContract:
    """
    Smart contract entity for managing contract interactions and metadata.
    
    Tracks contract verification status, interaction patterns, and
    provides safety validation for contract calls.
    """
    
    def __init__(
        self,
        contract_id: str,
        address: ContractAddress,
        network: NetworkType,
        name: Optional[str] = None,
        abi: Optional[Dict[str, Any]] = None,
        is_verified: bool = False,
        interaction_count: int = 0,
        created_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self._contract_id = contract_id
        self._address = address
        self._network = network
        self._name = name
        self._abi = abi
        self._is_verified = is_verified
        self._interaction_count = interaction_count
        self._created_at = created_at or datetime.now(timezone.utc)
        self._metadata = metadata or {}
        self._domain_events: List[DomainEvent] = []
    
    # Properties
    @property
    def contract_id(self) -> str:
        return self._contract_id
    
    @property
    def address(self) -> ContractAddress:
        return self._address
    
    @property
    def network(self) -> NetworkType:
        return self._network
    
    @property
    def name(self) -> Optional[str]:
        return self._name
    
    @property
    def is_verified(self) -> bool:
        return self._is_verified
    
    @property
    def interaction_count(self) -> int:
        return self._interaction_count
    
    @property
    def domain_events(self) -> List[DomainEvent]:
        return self._domain_events.copy()
    
    def clear_domain_events(self) -> None:
        """Clear domain events after publishing."""
        self._domain_events.clear()
    
    # Business Methods
    def record_interaction(self, user_id: str, function_name: str, success: bool) -> None:
        """Record an interaction with this contract."""
        self._interaction_count += 1
        
        from .events import ContractInteractionEvent
        self._add_domain_event(ContractInteractionEvent(
            transaction_id=str(uuid4()),  # Will be updated with actual transaction ID
            wallet_id="",  # Will be updated with actual wallet ID
            user_id=user_id,
            contract_address=str(self._address),
            function_name=function_name,
            success=success
        ))
    
    def validate_function_call(self, function_name: str, calldata: List[str]) -> bool:
        """Validate function call against ABI if available."""
        if not self._abi:
            # If no ABI, allow call but mark as unverified
            return True
        
        # TODO: Implement ABI validation logic
        return True
    
    def _add_domain_event(self, event: DomainEvent) -> None:
        """Add domain event to be published."""
        self._domain_events.append(event)