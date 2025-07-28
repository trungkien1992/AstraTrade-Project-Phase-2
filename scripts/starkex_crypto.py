import hashlib
import hmac
from typing import Tuple, Dict, Callable
from decimal import Decimal
import time

try:
    from starkware.crypto.signature.signature import private_to_stark_key, sign, pedersen_hash
    STARKWARE_CRYPTO_AVAILABLE = True
except ImportError:
    STARKWARE_CRYPTO_AVAILABLE = False

try:
    from fast_stark_crypto import pedersen_hash as fast_pedersen, sign as fast_sign
    FAST_CRYPTO_AVAILABLE = True
except ImportError:
    FAST_CRYPTO_AVAILABLE = False

def _pedersen_hash_fallback(a: int, b: int) -> int:
    combined = f"{a}{b}".encode()
    hash_obj = hashlib.sha256(combined)
    return int(hash_obj.hexdigest(), 16) % (2**251)

def pedersen_hash_func(a: int, b: int) -> int:
    if STARKWARE_CRYPTO_AVAILABLE:
        return pedersen_hash(a, b)
    elif FAST_CRYPTO_AVAILABLE:
        return fast_pedersen(a, b)
    else:
        return _pedersen_hash_fallback(a, b)

def _generate_k_rfc6979(msg_hash: int, private_key: int) -> int:
    msg_bytes = msg_hash.to_bytes(32, 'big')
    key_bytes = private_key.to_bytes(32, 'big')
    v = b'\x01' * 32
    k = b'\x00' * 32
    k = hmac.new(k, v + b'\x00' + key_bytes + msg_bytes, hashlib.sha256).digest()
    v = hmac.new(k, v, hashlib.sha256).digest()
    k = hmac.new(k, v + b'\x01' + key_bytes + msg_bytes, hashlib.sha256).digest()
    v = hmac.new(k, v, hashlib.sha256).digest()
    while True:
        v = hmac.new(k, v, hashlib.sha256).digest()
        candidate = int.from_bytes(v, 'big')
        if 1 <= candidate < 2**251:
            return candidate
        k = hmac.new(k, v + b'\x00', hashlib.sha256).digest()
        v = hmac.new(k, v, hashlib.sha256).digest()

def _sign_fallback(private_key: int, msg_hash: int) -> Tuple[int, int]:
    k = _generate_k_rfc6979(msg_hash, private_key)
    r = (k * 123456789) % (2**251)
    s = (msg_hash + private_key * r) % (2**251)
    return (r, s)

def sign_func(private_key: int, msg_hash: int) -> Tuple[int, int]:
    if STARKWARE_CRYPTO_AVAILABLE:
        return sign(private_key, msg_hash)
    elif FAST_CRYPTO_AVAILABLE:
        k = _generate_k_rfc6979(msg_hash, private_key)
        return fast_sign(private_key=private_key, msg_hash=msg_hash, k=k)
    else:
        return _sign_fallback(private_key, msg_hash)

class StarkExOrderSigner:
    ASSET_CONFIGS = {
        'BTC-USD': {
            'synthetic_id': 0x4254432d38000000000000000000000,
            'collateral_id': 0x2893294412a4c8f915f75892b395ebbf6859ec246ec365c3b1f56f47c3a0a5d,
            'synthetic_decimals': 10,
            'collateral_decimals': 6
        },
        'ETH-USD': {
            'synthetic_id': 0x4554482d38000000000000000000000,
            'collateral_id': 0x2893294412a4c8f915f75892b395ebbf6859ec246ec365c3b1f56f47c3a0a5d,
            'synthetic_decimals': 10,
            'collateral_decimals': 6
        },
        'EUR-USD': {
            'synthetic_id': 0x4555522d5553442d38000000000000,
            'collateral_id': 0x2893294412a4c8f915f75892b395ebbf6859ec246ec365c3b1f56f47c3a0a5d,
            'synthetic_decimals': 10,
            'collateral_decimals': 6
        },
        'AVAX-USD': {
            'synthetic_id': 0x415641582d555344000000000000000,
            'collateral_id': 0x2893294412a4c8f915f75892b395ebbf6859ec246ec365c3b1f56f47c3a0a5d,
            'synthetic_decimals': 10,
            'collateral_decimals': 6
        },
        'BNB-USD': {
            'synthetic_id': 0x424e422d55534400000000000000000,
            'collateral_id': 0x2893294412a4c8f915f75892b395ebbf6859ec246ec365c3b1f56f47c3a0a5d,
            'synthetic_decimals': 10,
            'collateral_decimals': 6
        },
        'LTC-USD': {
            'synthetic_id': 0x4c54432d55534400000000000000000,
            'collateral_id': 0x2893294412a4c8f915f75892b395ebbf6859ec246ec365c3b1f56f47c3a0a5d,
            'synthetic_decimals': 10,
            'collateral_decimals': 6
        }
    }

    def __init__(self, private_key_hex: str, vault_id: str):
        if not STARKWARE_CRYPTO_AVAILABLE:
            raise ImportError("StarkWare crypto library required for proper public key derivation. Install cairo-lang.")
        self.private_key = int(private_key_hex, 16)
        self.vault_id = int(vault_id)
        try:
            public_key_int = private_to_stark_key(self.private_key)
            self.public_key = f"0x{public_key_int:064x}"
        except Exception as e:
            raise ValueError(f"Failed to derive StarkEx public key: {e}")

    def _scale_amount(self, amount: str, decimals: int) -> int:
        amount_decimal = Decimal(amount)
        scaled = amount_decimal * (10 ** decimals)
        return int(scaled)

    def _calculate_fee(self, collateral_amount: int, fee_rate: float = 0.00025) -> int:
        return int(collateral_amount * fee_rate)

    def _get_limit_order_msg_hash(self,
                                  synthetic_asset_id: int,
                                  collateral_asset_id: int,
                                  is_buying_synthetic: int,
                                  fee_asset_id: int,
                                  amount_synthetic: int,
                                  amount_collateral: int,
                                  max_fee: int,
                                  nonce: int,
                                  vault_id: int,
                                  expiration_hours: int,
                                  hash_function: Callable[[int, int], int] = pedersen_hash_func) -> int:
        # Implements the user's provided packing logic
        OP_LIMIT_ORDER_WITH_FEES = 7
        if is_buying_synthetic:
            asset_id_sell, asset_id_buy = collateral_asset_id, synthetic_asset_id
            amount_sell, amount_buy = amount_collateral, amount_synthetic
        else:
            asset_id_sell, asset_id_buy = synthetic_asset_id, collateral_asset_id
            amount_sell, amount_buy = amount_synthetic, amount_collateral
        msg = hash_function(asset_id_sell, asset_id_buy)
        msg = hash_function(msg, fee_asset_id)
        packed_message0 = amount_sell
        packed_message0 = packed_message0 * 2**64 + amount_buy
        packed_message0 = packed_message0 * 2**64 + max_fee
        packed_message0 = packed_message0 * 2**32 + nonce
        msg = hash_function(msg, packed_message0)
        packed_message1 = OP_LIMIT_ORDER_WITH_FEES
        packed_message1 = packed_message1 * 2**64 + vault_id
        packed_message1 = packed_message1 * 2**64 + vault_id
        packed_message1 = packed_message1 * 2**64 + vault_id
        packed_message1 = packed_message1 * 2**32 + expiration_hours
        packed_message1 = packed_message1 * 2**17  # Padding
        return hash_function(msg, packed_message1)

    def sign_order(self,
                   market: str,
                   side: str,
                   quantity: str,
                   price: str,
                   nonce: int,
                   expiration_timestamp: int) -> Dict:
        if market not in self.ASSET_CONFIGS:
            raise ValueError(f"Unsupported market: {market}")
        config = self.ASSET_CONFIGS[market]
        amount_synthetic = self._scale_amount(quantity, config['synthetic_decimals'])
        amount_collateral = self._scale_amount(str(Decimal(quantity) * Decimal(price)), config['collateral_decimals'])
        max_fee = self._calculate_fee(amount_collateral)
        is_buying_synthetic = 1 if side.upper() == 'BUY' else 0
        expiration_hours = expiration_timestamp // (1000 * 3600)
        msg_hash = self._get_limit_order_msg_hash(
            synthetic_asset_id=config['synthetic_id'],
            collateral_asset_id=config['collateral_id'],
            is_buying_synthetic=is_buying_synthetic,
            fee_asset_id=config['collateral_id'],
            amount_synthetic=amount_synthetic,
            amount_collateral=amount_collateral,
            max_fee=max_fee,
            nonce=nonce,
            vault_id=self.vault_id,
            expiration_hours=expiration_hours
        )
        r, s = sign_func(self.private_key, msg_hash)
        return {
            'signature': {
                'r': f"0x{r:064x}",
                's': f"0x{s:064x}"
            },
            'starkKey': self.public_key,
            'collateralPosition': str(self.vault_id),
            'msgHash': f"0x{msg_hash:064x}",
            'orderDetails': {
                'market': market,
                'side': side,
                'amountSynthetic': amount_synthetic,
                'amountCollateral': amount_collateral,
                'maxFee': max_fee,
                'nonce': nonce,
                'expirationHours': expiration_hours
            }
        }

def create_order_signer(private_key_hex: str, vault_id: str) -> StarkExOrderSigner:
    return StarkExOrderSigner(private_key_hex, vault_id)
