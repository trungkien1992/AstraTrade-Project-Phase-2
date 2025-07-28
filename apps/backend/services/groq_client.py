"""
Groq API Client for Fast Reasoning Models
Integrates with Groq's ultra-fast inference API for reasoning tasks
Based on Groq API documentation and AstraTrade requirements
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Union
import httpx
from datetime import datetime
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s'))
    logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class GroqAPIError(Exception):
    """Custom exception for Groq API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class GroqClient:
    """
    Client for Groq API integration.
    Provides ultra-fast inference for reasoning models.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.groq_api_key
        if not self.api_key:
            logger.warning("Groq API key not configured. Some features may be limited.")
        
        self.base_url = settings.groq_base_url
        self.model = settings.groq_model
        self.max_tokens = settings.groq_max_tokens
        self.temperature = settings.groq_temperature
        self.timeout = settings.groq_timeout
        
        self.session = None
        self._rate_limits = {
            "requests_per_second": 50,  # Groq allows high throughput
            "last_request_time": 0
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.aclose()
    
    async def _rate_limit(self):
        """Implement rate limiting for API requests."""
        current_time = time.time()
        time_since_last = current_time - self._rate_limits["last_request_time"]
        
        if time_since_last < (1.0 / self._rate_limits["requests_per_second"]):
            await asyncio.sleep((1.0 / self._rate_limits["requests_per_second"]) - time_since_last)
        
        self._rate_limits["last_request_time"] = time.time()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "AstraTrade-Groq-Client/1.0.0"
        }
        return headers
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make authenticated API request with error handling."""
        if not self.session:
            raise GroqAPIError("Client not initialized. Use async context manager.")
        
        if not self.api_key:
            raise GroqAPIError("Groq API key not configured")
        
        await self._rate_limit()
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        try:
            if method.upper() == "POST":
                response = await self.session.post(url, headers=headers, json=data)
            elif method.upper() == "GET":
                response = await self.session.get(url, headers=headers)
            else:
                raise GroqAPIError(f"Unsupported HTTP method: {method}")
            
            response_data = response.json()
            
            if response.status_code != 200:
                logger.error(f"Groq API error: {response.status_code} {response_data}")
                error_message = response_data.get("error", {}).get("message", f"HTTP {response.status_code} error")
                raise GroqAPIError(
                    error_message, 
                    status_code=response.status_code, 
                    response_data=response_data
                )
            
            return response_data
            
        except httpx.RequestError as e:
            logger.error(f"Groq API request failed: {str(e)}")
            raise GroqAPIError(f"Request failed: {str(e)}")
        except json.JSONDecodeError:
            logger.error(f"Groq API returned invalid JSON response.")
            raise GroqAPIError("Invalid JSON response from API")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Send a chat completion request to Groq API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use (defaults to configured model)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 2.0)
            stream: Whether to stream the response
            
        Returns:
            API response dictionary
        """
        payload = {
            "model": model or self.model,
            "messages": messages,
            "max_tokens": max_tokens or self.max_tokens,
            "temperature": temperature or self.temperature,
            "stream": stream
        }
        
        logger.info(f"Sending chat completion request to Groq API with model: {payload['model']}")
        start_time = time.time()
        
        try:
            response = await self._make_request("POST", "/openai/v1/chat/completions", payload)
            
            duration = time.time() - start_time
            logger.info(f"Groq API response received in {duration:.2f}s")
            
            return response
            
        except Exception as e:
            logger.error(f"Chat completion failed: {str(e)}")
            raise
    
    async def analyze_trading_decision(
        self,
        market_data: Dict[str, Any],
        user_profile: Dict[str, Any],
        trading_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze trading decision using Groq's reasoning capabilities.
        
        Args:
            market_data: Current market conditions
            user_profile: User's trading profile and preferences
            trading_history: Recent trading history
            
        Returns:
            Analysis result with recommendations
        """
        messages = [
            {
                "role": "system",
                "content": """You are an expert trading analyst for AstraTrade. 
                Analyze the provided market data, user profile, and trading history 
                to provide reasoned trading recommendations. Focus on risk management 
                and user-specific preferences."""
            },
            {
                "role": "user",
                "content": f"""Please analyze the following trading scenario:
                
                Market Data: {json.dumps(market_data, indent=2)}
                User Profile: {json.dumps(user_profile, indent=2)}
                Trading History: {json.dumps(trading_history, indent=2)}
                
                Provide a reasoned analysis with:
                1. Market assessment
                2. Risk evaluation
                3. Recommended action
                4. Confidence level
                5. Reasoning behind the recommendation"""
            }
        ]
        
        try:
            response = await self.chat_completion(messages, temperature=0.3)
            return {
                "analysis": response["choices"][0]["message"]["content"],
                "model_used": response["model"],
                "tokens_used": response["usage"]["total_tokens"],
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Trading analysis failed: {str(e)}")
            raise
    
    async def generate_game_content(
        self,
        content_type: str,
        user_context: Dict[str, Any],
        game_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate game content using Groq's creative capabilities.
        
        Args:
            content_type: Type of content to generate (meme, story, achievement)
            user_context: User's current context and preferences
            game_state: Current game state and mechanics
            
        Returns:
            Generated content with metadata
        """
        messages = [
            {
                "role": "system",
                "content": f"""You are a creative content generator for AstraTrade, 
                a cosmic-themed trading game. Generate engaging {content_type} content 
                that fits the cosmic theme and user's context."""
            },
            {
                "role": "user",
                "content": f"""Generate {content_type} content for:
                
                User Context: {json.dumps(user_context, indent=2)}
                Game State: {json.dumps(game_state, indent=2)}
                
                Make it engaging, cosmic-themed, and personalized to the user's context."""
            }
        ]
        
        try:
            response = await self.chat_completion(messages, temperature=0.8)
            return {
                "content": response["choices"][0]["message"]["content"],
                "content_type": content_type,
                "model_used": response["model"],
                "tokens_used": response["usage"]["total_tokens"],
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Content generation failed: {str(e)}")
            raise
    
    async def health_check(self) -> bool:
        """Check if Groq API is accessible."""
        try:
            # Try a simple completion to test connectivity
            messages = [{"role": "user", "content": "Hello"}]
            await self.chat_completion(messages, max_tokens=10)
            return True
        except Exception as e:
            logger.error(f"Groq API health check failed: {str(e)}")
            return False 