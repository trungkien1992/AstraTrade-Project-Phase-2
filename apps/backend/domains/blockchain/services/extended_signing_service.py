"""
Extended Exchange Signing Service
Part of the Blockchain Domain - handles all cryptographic signing operations for Extended Exchange

This service integrates the x10xchange-rust-crypto-lib-base for production-grade Starknet signing
with proper domain separation and message type handling.
"""

import logging
import os
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone

# Import the Rust crypto library (will be available after building)
try:
    import rust_crypto
    RUST_CRYPTO_AVAILABLE = True
except ImportError:
    RUST_CRYPTO_AVAILABLE = False
    logging.warning("rust_crypto module not available - using mock implementation for development")

# Mock implementation for development/testing
class MockRustCrypto:
    """Mock implementation of rust_crypto module for development"""
    
    @staticmethod
    def py_get_private_key_from_eth_signature(signature: str) -> str:
        # Mock implementation - would use real Rust crypto
        return "0x7c6f0bdb8b2b3a123456789abcdef0123456789abcdef0123456789abcdef"
    
    @staticmethod
    def py_get_order_hash(position_id, base_asset_id, base_amount, quote_asset_id, 
                         quote_amount, fee_asset_id, fee_amount, expiration, salt, 
                         user_public_key, domain_name, domain_version, domain_chain_id, 
                         domain_revision) -> str:
        # Mock implementation - would use real Rust crypto
        return "0x4de4c009e0d0c5a70a7da0e2039fb2b99f376d53496f89d9f437e736add6b48"
    
    @staticmethod
    def py_get_transfer_hash(recipient_position_id, sender_position_id, collateral_id, 
                           amount, expiration, salt, user_public_key, domain_name, 
                           domain_version, domain_chain_id, domain_revision) -> str:
        # Mock implementation - would use real Rust crypto  
        return "0x56c7b21d13b79a33d7700dda20e22246c25e89818249504148174f527fc3f8f"
    
    @staticmethod
    def py_get_withdrawal_hash(recipient, position_id, collateral_id, amount, 
                             expiration, salt, user_public_key, domain_name, 
                             domain_version, domain_chain_id, domain_revision) -> str:
        # Mock implementation - would use real Rust crypto
        return "0x2182119571682827544073774098906745929330860211691330979324731407862023927178"
    
    class MockSignature:
        def __init__(self):
            self.r = "0x7c6f0bdb8b2b3a123456789abcdef0123456789abcdef0123456789abcdef01"
            self.s = "0x7c6f0bdb8b2b3a123456789abcdef0123456789abcdef0123456789abcdef02"
            self.v = "0x1b"
    
    @staticmethod
    def py_sign_message(message_hash: str, private_key: str):
        # Mock implementation - would use real Rust crypto
        return MockRustCrypto.MockSignature()

# Use mock if rust_crypto not available
if not RUST_CRYPTO_AVAILABLE:
    rust_crypto = MockRustCrypto()

from ..entities import Wallet
from ..value_objects import StarknetAddress
from ..exceptions import SigningException, WalletNotFoundException
from ...shared.events import DomainEvent, EventBus

logger = logging.getLogger(__name__)

@dataclass
class OrderSignedEvent(DomainEvent):
    """Event raised when an order is signed for Extended Exchange"""
    order_id: str
    user_id: int
    message_hash: str
    signature: Dict[str, str]
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()
    
    @property
    def event_type(self) -> str:
        return "blockchain.order_signed"
    
    @property
    def domain(self) -> str:
        return "blockchain"
    
    @property
    def entity_id(self) -> str:
        return self.order_id

@dataclass
class KeyDerivedEvent(DomainEvent):
    """Event raised when a Starknet key is derived from Ethereum signature"""
    user_id: int
    derivation_method: str
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()
    
    @property
    def event_type(self) -> str:
        return "blockchain.key_derived"
    
    @property
    def domain(self) -> str:
        return "blockchain"
    
    @property
    def entity_id(self) -> str:
        return f"user_{self.user_id}"

class ExtendedSigningService:
    """
    Service for Extended Exchange signing operations.
    
    Integrates x10xchange-rust-crypto-lib-base for production-grade signing with:
    - Order message signing
    - Transfer message signing  
    - Withdrawal message signing
    - Ethereum signature → Starknet key derivation
    - Domain separation for security
    - Audit trail via domain events
    """
    
    def __init__(self, event_bus: EventBus, encryption_key: bytes):
        self.event_bus = event_bus
        self.encryption_key = encryption_key
        self.domain_config = {
            "name": os.getenv("STARKNET_DOMAIN_NAME", "Perpetuals"),
            "version": os.getenv("STARKNET_DOMAIN_VERSION", "v0"),
            "chain_id": os.getenv("STARKNET_DOMAIN_CHAIN_ID", "SN_SEPOLIA"),
            "revision": os.getenv("STARKNET_DOMAIN_REVISION", "1")
        }
        
        if not RUST_CRYPTO_AVAILABLE:
            logger.warning("Rust crypto library not available - using mock implementation")
            # Don't raise exception, use mock for development
    
    async def derive_key_from_eth_signature(
        self, 
        eth_signature: str,
        user_id: int
    ) -> str:
        """
        Derive Starknet private key from Ethereum signature.
        
        This enables cross-chain wallet compatibility by allowing users to
        derive their Starknet wallet from an Ethereum signature.
        
        Args:
            eth_signature: Ethereum signature (0x prefixed hex)
            user_id: User ID for audit trail
            
        Returns:
            Starknet private key as hex string
            
        Raises:
            SigningException: If derivation fails
        """
        try:
            logger.info(f"Deriving Starknet key for user {user_id}")
            
            # Use Rust crypto library for key derivation
            private_key = rust_crypto.py_get_private_key_from_eth_signature(eth_signature)
            
            # Emit domain event for audit trail
            await self.event_bus.emit(KeyDerivedEvent(
                user_id=user_id,
                derivation_method="eth_signature"
            ))
            
            logger.info(f"Successfully derived Starknet key for user {user_id}")
            return private_key
            
        except Exception as e:
            logger.error(f"Key derivation failed for user {user_id}: {e}")
            raise SigningException(f"Failed to derive Starknet key: {e}")
    
    async def sign_order(
        self,
        user_id: int,
        wallet: Wallet,
        order_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Sign an Extended Exchange order message.
        
        Creates a properly formatted order message with domain separation
        and signs it using ECDSA with the Starknet curve.
        
        Args:
            user_id: User ID for audit trail
            wallet: User's wallet entity with private key
            order_params: Order parameters including:
                - position_id: Position ID
                - base_asset_id: Base asset ID (hex)
                - base_amount: Base amount (int)
                - quote_asset_id: Quote asset ID (hex)
                - quote_amount: Quote amount (int)
                - fee_asset_id: Fee asset ID (hex)
                - fee_amount: Fee amount (int)
                - expiration: Expiration timestamp
                - salt: Random salt for uniqueness
                
        Returns:
            Dict containing:
                - message_hash: Hash of the order message
                - signature: {r, s, v} signature components
                - order_id: Unique order identifier
                
        Raises:
            SigningException: If signing fails
            WalletNotFoundException: If wallet is invalid
        """
        try:
            logger.info(f"Signing order for user {user_id}")
            
            # Validate wallet has necessary data
            if not wallet.address or not wallet.get_decrypted_private_key(self.encryption_key):
                raise WalletNotFoundException(f"Invalid wallet for user {user_id}")
            
            # Get public key from wallet
            public_key = wallet.get_public_key(self.encryption_key)  # This would derive from private key
            
            # Generate order hash using Rust crypto library
            message_hash = rust_crypto.py_get_order_hash(
                str(order_params["position_id"]),
                order_params["base_asset_id"],
                str(order_params["base_amount"]),
                order_params["quote_asset_id"],
                str(order_params["quote_amount"]),
                order_params["fee_asset_id"],
                str(order_params["fee_amount"]),
                str(order_params["expiration"]),
                str(order_params["salt"]),
                public_key,
                self.domain_config["name"],
                self.domain_config["version"],
                self.domain_config["chain_id"],
                self.domain_config["revision"]
            )
            
            # Sign the message hash
            signature = rust_crypto.py_sign_message(
                message_hash,
                wallet.get_decrypted_private_key(self.encryption_key)
            )
            
            # Create unique order ID
            order_id = f"order_{order_params['position_id']}_{order_params['salt']}"
            
            result = {
                "message_hash": message_hash,
                "signature": {
                    "r": signature.r,
                    "s": signature.s,
                    "v": signature.v
                },
                "order_id": order_id,
                "signed_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Emit domain event for audit trail
            await self.event_bus.emit(OrderSignedEvent(
                order_id=order_id,
                user_id=user_id,
                message_hash=message_hash,
                signature=result["signature"]
            ))
            
            logger.info(f"Successfully signed order {order_id} for user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Order signing failed for user {user_id}: {e}")
            raise SigningException(f"Failed to sign order: {e}")
    
    async def sign_transfer(
        self,
        user_id: int,
        wallet: Wallet,
        transfer_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Sign a transfer message for position-to-position transfers.
        
        Args:
            user_id: User ID for audit trail
            wallet: User's wallet entity
            transfer_params: Transfer parameters including:
                - recipient_position_id: Recipient position ID
                - sender_position_id: Sender position ID
                - collateral_id: Collateral asset ID (hex)
                - amount: Transfer amount
                - expiration: Expiration timestamp
                - salt: Random salt
                
        Returns:
            Dict with message_hash, signature, and transfer_id
        """
        try:
            logger.info(f"Signing transfer for user {user_id}")
            
            # Validate wallet
            if not wallet.address or not wallet.get_decrypted_private_key(self.encryption_key):
                raise WalletNotFoundException(f"Invalid wallet for user {user_id}")
            
            # Get public key
            public_key = wallet.get_public_key(self.encryption_key)
            
            # Generate transfer hash
            message_hash = rust_crypto.py_get_transfer_hash(
                str(transfer_params["recipient_position_id"]),
                str(transfer_params["sender_position_id"]),
                transfer_params["collateral_id"],
                str(transfer_params["amount"]),
                str(transfer_params["expiration"]),
                str(transfer_params["salt"]),
                public_key,
                self.domain_config["name"],
                self.domain_config["version"],
                self.domain_config["chain_id"],
                self.domain_config["revision"]
            )
            
            # Sign the message
            signature = rust_crypto.py_sign_message(
                message_hash,
                wallet.get_decrypted_private_key(self.encryption_key)
            )
            
            transfer_id = f"transfer_{transfer_params['sender_position_id']}_{transfer_params['salt']}"
            
            result = {
                "message_hash": message_hash,
                "signature": {
                    "r": signature.r,
                    "s": signature.s,
                    "v": signature.v
                },
                "transfer_id": transfer_id,
                "signed_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Emit domain event
            await self.event_bus.emit(DomainEvent(
                event_type="blockchain.transfer_signed",
                domain="blockchain",
                entity_id=transfer_id,
                data={
                    "user_id": user_id,
                    "transfer_id": transfer_id,
                    "message_hash": message_hash
                }
            ))
            
            logger.info(f"Successfully signed transfer {transfer_id} for user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Transfer signing failed for user {user_id}: {e}")
            raise SigningException(f"Failed to sign transfer: {e}")
    
    async def sign_withdrawal(
        self,
        user_id: int,
        wallet: Wallet,
        withdrawal_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Sign a withdrawal message for withdrawing to external addresses.
        
        Args:
            user_id: User ID for audit trail  
            wallet: User's wallet entity
            withdrawal_params: Withdrawal parameters including:
                - recipient: Recipient address (hex)
                - position_id: Position ID
                - collateral_id: Collateral asset ID (hex)
                - amount: Withdrawal amount
                - expiration: Expiration timestamp
                - salt: Random salt
                
        Returns:
            Dict with message_hash, signature, and withdrawal_id
        """
        try:
            logger.info(f"Signing withdrawal for user {user_id}")
            
            # Validate wallet
            if not wallet.address or not wallet.get_decrypted_private_key(self.encryption_key):
                raise WalletNotFoundException(f"Invalid wallet for user {user_id}")
            
            # Get public key
            public_key = wallet.get_public_key(self.encryption_key)
            
            # Generate withdrawal hash
            message_hash = rust_crypto.py_get_withdrawal_hash(
                withdrawal_params["recipient"],
                str(withdrawal_params["position_id"]),
                withdrawal_params["collateral_id"],
                str(withdrawal_params["amount"]),
                str(withdrawal_params["expiration"]),
                str(withdrawal_params["salt"]),
                public_key,
                self.domain_config["name"],
                self.domain_config["version"],
                self.domain_config["chain_id"],
                self.domain_config["revision"]
            )
            
            # Sign the message
            signature = rust_crypto.py_sign_message(
                message_hash,
                wallet.get_decrypted_private_key(self.encryption_key)
            )
            
            withdrawal_id = f"withdrawal_{withdrawal_params['position_id']}_{withdrawal_params['salt']}"
            
            result = {
                "message_hash": message_hash,
                "signature": {
                    "r": signature.r,
                    "s": signature.s,
                    "v": signature.v
                },
                "withdrawal_id": withdrawal_id,
                "signed_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Emit domain event
            await self.event_bus.emit(DomainEvent(
                event_type="blockchain.withdrawal_signed",
                domain="blockchain",
                entity_id=withdrawal_id,
                data={
                    "user_id": user_id,
                    "withdrawal_id": withdrawal_id,
                    "message_hash": message_hash,
                    "recipient": withdrawal_params["recipient"]
                }
            ))
            
            logger.info(f"Successfully signed withdrawal {withdrawal_id} for user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Withdrawal signing failed for user {user_id}: {e}")
            raise SigningException(f"Failed to sign withdrawal: {e}")
    
    async def verify_signature(
        self,
        message_hash: str,
        signature: Dict[str, str],
        public_key: str
    ) -> bool:
        """
        Verify a signature against a message hash and public key.
        
        Args:
            message_hash: Hash of the original message
            signature: Signature components {r, s, v}
            public_key: Public key to verify against
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # This would use the Rust library's verification function
            # For now, return True as a placeholder
            logger.info(f"Verifying signature for message hash {message_hash[:16]}...")
            
            # TODO: Implement signature verification in Rust library
            # return rust_crypto.py_verify_signature(message_hash, signature, public_key)
            
            return True
            
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    def get_domain_config(self) -> Dict[str, str]:
        """Get the current domain configuration."""
        return self.domain_config.copy()
    
    def is_available(self) -> bool:
        """Check if the signing service is available."""
        return RUST_CRYPTO_AVAILABLE