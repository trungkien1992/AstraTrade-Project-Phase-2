"""
Extended Exchange API Client
Integrates with Extended Exchange for real trading functionality
Based on Extended Exchange API documentation and trading requirements
"""

import asyncio
import hashlib
import hmac
import time
import uuid
from typing import Dict, List, Optional, Any
import httpx
import json
from datetime import datetime, timezone
from ..core.config import settings
import logging
from starkex_crypto import StarkExOrderSigner

logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s'))
    logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class ExtendedExchangeError(Exception):
    """Custom exception for Extended Exchange API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class ExtendedExchangeClient:
    """
    Enhanced client for Extended Exchange API integration.
    Supports real trading, portfolio management, and market data.
    """
    
    def __init__(self, api_key: Optional[str] = None, secret_key: Optional[str] = None, passphrase: Optional[str] = None):
        self.api_key = api_key or settings.exchange_api_key
        self.secret_key = secret_key or settings.exchange_secret_key
        self.passphrase = passphrase or settings.exchange_passphrase
        
        self.base_url = "https://api.extended.exchange"
        self.sandbox_url = "https://sandbox-api.extended.exchange"
        
        # Use sandbox in development
        self.api_url = self.sandbox_url if settings.environment == "development" else self.base_url
        
        self.session = None
        self._rate_limits = {
            "requests_per_second": 10,
            "last_request_time": 0
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.aclose()
    
    def _generate_signature(self, timestamp: str, method: str, path: str, body: str = "") -> str:
        """Generate HMAC signature for API authentication."""
        if not self.secret_key:
            raise ExtendedExchangeError("Secret key not configured")
        
        message = timestamp + method.upper() + path + body
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def _get_headers(self, method: str, path: str, body: str = "") -> Dict[str, str]:
        """Generate authentication headers for API requests."""
        if not self.api_key or not self.secret_key or not self.passphrase:
            raise ExtendedExchangeError("API credentials not properly configured")
        
        timestamp = str(int(time.time()))
        signature = self._generate_signature(timestamp, method, path, body)
        
        return {
            "EX-ACCESS-KEY": self.api_key,
            "EX-ACCESS-SIGN": signature,
            "EX-ACCESS-TIMESTAMP": timestamp,
            "EX-ACCESS-PASSPHRASE": self.passphrase,
            "Content-Type": "application/json",
            "User-Agent": "AstraTrade/1.0"
        }
    
    async def _rate_limit(self):
        """Implement rate limiting to respect API limits."""
        current_time = time.time()
        time_since_last_request = current_time - self._rate_limits["last_request_time"]
        min_interval = 1.0 / self._rate_limits["requests_per_second"]
        
        if time_since_last_request < min_interval:
            sleep_time = min_interval - time_since_last_request
            await asyncio.sleep(sleep_time)
        
        self._rate_limits["last_request_time"] = time.time()
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None, 
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make authenticated API request with error handling."""
        if not self.session:
            raise ExtendedExchangeError("Client not initialized. Use async context manager.")
        await self._rate_limit()
        url = f"{self.api_url}{endpoint}"
        body = json.dumps(data) if data else ""
        headers = self._get_headers(method, endpoint, body)
        try:
            if method.upper() == "GET":
                response = await self.session.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = await self.session.post(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = await self.session.delete(url, headers=headers, params=params)
            else:
                raise ExtendedExchangeError(f"Unsupported HTTP method: {method}")
            response_data = response.json()
            if response.status_code != 200:
                logger.error(f"Exchange API error: {response.status_code} {response_data}")
                error_message = response_data.get("message", f"HTTP {response.status_code} error")
                raise ExtendedExchangeError(
                    error_message, 
                    status_code=response.status_code, 
                    response_data=response_data
                )
            return response_data
        except httpx.RequestError as e:
            logger.error(f"Exchange API request failed: {str(e)}")
            raise ExtendedExchangeError(f"Request failed: {str(e)}")
        except json.JSONDecodeError:
            logger.error(f"Exchange API returned invalid JSON response.")
            raise ExtendedExchangeError("Invalid JSON response from API")
    
    # Market Data Methods
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get current ticker information for a symbol."""
        return await self._make_request("GET", f"/v1/market/ticker/{symbol}")
    
    async def get_orderbook(self, symbol: str, depth: int = 20) -> Dict[str, Any]:
        """Get orderbook data for a symbol."""
        params = {"depth": depth}
        return await self._make_request("GET", f"/v1/market/orderbook/{symbol}", params=params)
    
    async def get_klines(
        self, 
        symbol: str, 
        interval: str = "1h", 
        limit: int = 100,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get candlestick/kline data."""
        params = {
            "interval": interval,
            "limit": limit
        }
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        
        return await self._make_request("GET", f"/v1/market/klines/{symbol}", params=params)
    
    # Account Methods
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information and balances."""
        return await self._make_request("GET", "/v1/account/info")
    
    async def get_balances(self) -> Dict[str, Any]:
        """Get account balances for all assets."""
        return await self._make_request("GET", "/v1/account/balances")
    
    async def get_balance(self, asset: str) -> Dict[str, Any]:
        """Get balance for a specific asset."""
        return await self._make_request("GET", f"/v1/account/balance/{asset}")
    
    # Trading Methods
    async def create_order(
        self,
        symbol: str,
        side: str,  # "buy" or "sell"
        order_type: str,  # "market", "limit", "stop_loss", "take_profit"
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        time_in_force: str = "GTC",  # GTC, IOC, FOK
        client_order_id: Optional[str] = None,
        nonce: Optional[int] = None,
        expiration_timestamp: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a new order. Now supports StarkEx signature for limit orders."""
        data = {
            "symbol": symbol,
            "side": side.lower(),
            "type": order_type.lower(),
            "quantity": str(quantity),
            "timeInForce": time_in_force
        }
        
        if price:
            data["price"] = str(price)
        if stop_price:
            data["stopPrice"] = str(stop_price)
        if client_order_id:
            data["clientOrderId"] = client_order_id
        else:
            data["clientOrderId"] = f"astratrade_{uuid.uuid4().hex[:8]}"

        # Add StarkEx signature for limit orders (or as required)
        if order_type.lower() == "limit" and settings.starknet_private_key and settings.vault_contract_address and price:
            # Use current time as nonce if not provided
            order_nonce = nonce if nonce is not None else int(time.time())
            # Use expiration_timestamp or default to 24h from now
            expiration = expiration_timestamp if expiration_timestamp is not None else int((time.time() + 24*3600) * 1000)
            signer = StarkExOrderSigner(settings.starknet_private_key, settings.vault_contract_address)
            signature_payload = signer.sign_order(
                market=symbol,
                side=side,
                quantity=str(quantity),
                price=str(price),
                nonce=order_nonce,
                expiration_timestamp=expiration
            )
            data["stark_signature"] = signature_payload["signature"]
            data["stark_key"] = signature_payload["starkKey"]
            data["collateral_position"] = signature_payload["collateralPosition"]
            data["msg_hash"] = signature_payload["msgHash"]
            data["order_details"] = signature_payload["orderDetails"]

        return await self._make_request("POST", "/v1/orders", data=data)
    
    async def cancel_order(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """Cancel an existing order."""
        params = {"symbol": symbol}
        return await self._make_request("DELETE", f"/v1/orders/{order_id}", params=params)
    
    async def get_order(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """Get order information."""
        params = {"symbol": symbol}
        return await self._make_request("GET", f"/v1/orders/{order_id}", params=params)
    
    async def get_open_orders(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Get all open orders."""
        params = {}
        if symbol:
            params["symbol"] = symbol
        return await self._make_request("GET", "/v1/orders/open", params=params)
    
    async def get_order_history(
        self, 
        symbol: Optional[str] = None, 
        limit: int = 100,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get order history."""
        params = {"limit": limit}
        if symbol:
            params["symbol"] = symbol
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        
        return await self._make_request("GET", "/v1/orders/history", params=params)
    
    # Trade History
    async def get_trades(
        self, 
        symbol: Optional[str] = None, 
        limit: int = 100,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get trade history."""
        params = {"limit": limit}
        if symbol:
            params["symbol"] = symbol
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        
        return await self._make_request("GET", "/v1/account/trades", params=params)
    
    # Portfolio and Performance
    async def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get portfolio summary with total value and performance."""
        account_info = await self.get_account_info()
        balances = await self.get_balances()
        
        # Calculate total portfolio value
        total_value_usd = 0.0
        portfolio_breakdown = {}
        
        for balance in balances.get("balances", []):
            asset = balance["asset"]
            free_balance = float(balance["free"])
            locked_balance = float(balance["locked"])
            total_balance = free_balance + locked_balance
            
            if total_balance > 0:
                # Get current price for non-USD assets
                if asset != "USD":
                    try:
                        ticker = await self.get_ticker(f"{asset}USD")
                        current_price = float(ticker["price"])
                        value_usd = total_balance * current_price
                    except:
                        # Fallback if ticker not available
                        value_usd = 0.0
                        current_price = 0.0
                else:
                    value_usd = total_balance
                    current_price = 1.0
                
                total_value_usd += value_usd
                portfolio_breakdown[asset] = {
                    "free": free_balance,
                    "locked": locked_balance,
                    "total": total_balance,
                    "current_price": current_price,
                    "value_usd": value_usd
                }
        
        return {
            "total_value_usd": total_value_usd,
            "account_status": account_info.get("accountType", "unknown"),
            "portfolio_breakdown": portfolio_breakdown,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
    
    # Market Analysis Helpers
    async def get_supported_symbols(self) -> List[str]:
        """Get list of supported trading symbols."""
        try:
            symbols_data = await self._make_request("GET", "/v1/market/symbols")
            return [symbol["symbol"] for symbol in symbols_data.get("symbols", [])]
        except:
            # Fallback to common symbols if endpoint not available
            return ["BTCUSD", "ETHUSD", "ADAUSD", "SOLUSD", "MATICUSD", "LINKUSD"]
    
    async def get_24h_stats(self, symbol: str) -> Dict[str, Any]:
        """Get 24h trading statistics."""
        ticker = await self.get_ticker(symbol)
        return {
            "symbol": symbol,
            "price_change": ticker.get("priceChange", "0"),
            "price_change_percent": ticker.get("priceChangePercent", "0"),
            "high_price": ticker.get("highPrice", "0"),
            "low_price": ticker.get("lowPrice", "0"),
            "volume": ticker.get("volume", "0"),
            "quote_volume": ticker.get("quoteVolume", "0"),
            "current_price": ticker.get("price", "0")
        }


# Singleton instance for global use
_extended_exchange_client = None

async def get_extended_exchange_client() -> ExtendedExchangeClient:
    """Get shared Extended Exchange client instance."""
    global _extended_exchange_client
    if _extended_exchange_client is None:
        _extended_exchange_client = ExtendedExchangeClient()
    return _extended_exchange_client


# Helper functions for common operations
async def execute_market_order(symbol: str, side: str, quantity: float) -> Dict[str, Any]:
    """Execute a market order with proper error handling."""
    async with ExtendedExchangeClient() as client:
        try:
            order_result = await client.create_order(
                symbol=symbol,
                side=side,
                order_type="market",
                quantity=quantity
            )
            
            logger.info(f"Market order executed: {side} {quantity} {symbol}")
            return order_result
            
        except ExtendedExchangeError as e:
            logger.error(f"Market order failed: {e.message}")
            raise

async def get_current_price(symbol: str) -> float:
    """Get current price for a symbol."""
    async with ExtendedExchangeClient() as client:
        ticker = await client.get_ticker(symbol)
        return float(ticker["price"])

async def validate_api_connection() -> bool:
    """Validate API credentials and connection."""
    try:
        async with ExtendedExchangeClient() as client:
            await client.get_account_info()
            return True
    except ExtendedExchangeError:
        return False