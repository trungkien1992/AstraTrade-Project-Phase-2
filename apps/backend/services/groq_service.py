"""
Groq Service for AstraTrade
Integrates Groq's fast reasoning capabilities with game mechanics
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from .groq_client import GroqClient, GroqAPIError

logger = logging.getLogger(__name__)


class GroqService:
    """
    Service layer for Groq API integration.
    Provides reasoning capabilities for trading and game mechanics.
    """
    
    def __init__(self):
        self.client = None
        self._is_available = False
        self._last_health_check = None
        self._health_check_interval = 300  # 5 minutes
    
    async def _ensure_client(self):
        """Ensure Groq client is initialized and available."""
        if self.client is None:
            self.client = GroqClient()
        
        # Check health if needed
        if (self._last_health_check is None or 
            (datetime.utcnow() - self._last_health_check).seconds > self._health_check_interval):
            self._is_available = await self.client.health_check()
            self._last_health_check = datetime.utcnow()
            
            if not self._is_available:
                logger.warning("Groq API is not available")
    
    async def get_trading_recommendation(
        self,
        user_id: int,
        market_data: Dict[str, Any],
        user_profile: Dict[str, Any],
        trading_history: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Get AI-powered trading recommendation using Groq.
        
        Args:
            user_id: User identifier
            market_data: Current market conditions
            user_profile: User's trading profile
            trading_history: Recent trading history
            
        Returns:
            Trading recommendation with reasoning
        """
        try:
            await self._ensure_client()
            
            if not self._is_available:
                logger.warning("Groq API not available, skipping trading recommendation")
                return None
            
            async with self.client:
                result = await self.client.analyze_trading_decision(
                    market_data=market_data,
                    user_profile=user_profile,
                    trading_history=trading_history
                )
                
                # Add user context
                result["user_id"] = user_id
                result["recommendation_type"] = "ai_analysis"
                
                logger.info(f"Generated trading recommendation for user {user_id}")
                return result
                
        except GroqAPIError as e:
            logger.error(f"Groq API error in trading recommendation: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in trading recommendation: {str(e)}")
            return None
    
    async def generate_viral_content(
        self,
        user_id: int,
        content_type: str,
        user_context: Dict[str, Any],
        game_state: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Generate viral content using Groq's creative capabilities.
        
        Args:
            user_id: User identifier
            content_type: Type of content (meme, story, achievement)
            user_context: User's current context
            game_state: Current game state
            
        Returns:
            Generated content with metadata
        """
        try:
            await self._ensure_client()
            
            if not self._is_available:
                logger.warning("Groq API not available, skipping content generation")
                return None
            
            async with self.client:
                result = await self.client.generate_game_content(
                    content_type=content_type,
                    user_context=user_context,
                    game_state=game_state
                )
                
                # Add user context
                result["user_id"] = user_id
                result["generated_at"] = datetime.utcnow().isoformat()
                
                logger.info(f"Generated {content_type} content for user {user_id}")
                return result
                
        except GroqAPIError as e:
            logger.error(f"Groq API error in content generation: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in content generation: {str(e)}")
            return None
    
    async def analyze_user_behavior(
        self,
        user_id: int,
        user_actions: List[Dict[str, Any]],
        game_events: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze user behavior patterns using Groq.
        
        Args:
            user_id: User identifier
            user_actions: List of user actions
            game_events: List of game events
            
        Returns:
            Behavior analysis with insights
        """
        try:
            await self._ensure_client()
            
            if not self._is_available:
                logger.warning("Groq API not available, skipping behavior analysis")
                return None
            
            messages = [
                {
                    "role": "system",
                    "content": """You are a user behavior analyst for AstraTrade. 
                    Analyze the provided user actions and game events to identify 
                    patterns, preferences, and potential improvements for the user experience."""
                },
                {
                    "role": "user",
                    "content": f"""Analyze the following user behavior data:
                    
                    User Actions: {user_actions}
                    Game Events: {game_events}
                    
                    Provide insights on:
                    1. User engagement patterns
                    2. Trading behavior trends
                    3. Feature preferences
                    4. Potential improvements
                    5. Risk assessment"""
                }
            ]
            
            async with self.client:
                response = await self.client.chat_completion(messages, temperature=0.2)
                
                analysis = {
                    "user_id": user_id,
                    "analysis": response["choices"][0]["message"]["content"],
                    "model_used": response["model"],
                    "tokens_used": response["usage"]["total_tokens"],
                    "timestamp": datetime.utcnow().isoformat(),
                    "analysis_type": "user_behavior"
                }
                
                logger.info(f"Generated behavior analysis for user {user_id}")
                return analysis
                
        except GroqAPIError as e:
            logger.error(f"Groq API error in behavior analysis: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in behavior analysis: {str(e)}")
            return None
    
    async def generate_achievement_description(
        self,
        achievement_type: str,
        user_stats: Dict[str, Any],
        game_context: Dict[str, Any]
    ) -> Optional[str]:
        """
        Generate personalized achievement descriptions using Groq.
        
        Args:
            achievement_type: Type of achievement
            user_stats: User's current statistics
            game_context: Current game context
            
        Returns:
            Personalized achievement description
        """
        try:
            await self._ensure_client()
            
            if not self._is_available:
                logger.warning("Groq API not available, using default achievement description")
                return f"Congratulations! You've earned the {achievement_type} achievement!"
            
            messages = [
                {
                    "role": "system",
                    "content": """You are an achievement system for AstraTrade. 
                    Generate engaging, cosmic-themed achievement descriptions that 
                    celebrate user accomplishments and encourage continued engagement."""
                },
                {
                    "role": "user",
                    "content": f"""Generate a personalized achievement description for:
                    
                    Achievement Type: {achievement_type}
                    User Stats: {user_stats}
                    Game Context: {game_context}
                    
                    Make it cosmic-themed, engaging, and personalized to the user's context."""
                }
            ]
            
            async with self.client:
                response = await self.client.chat_completion(messages, temperature=0.7, max_tokens=150)
                return response["choices"][0]["message"]["content"]
                
        except GroqAPIError as e:
            logger.error(f"Groq API error in achievement description: {str(e)}")
            return f"Congratulations! You've earned the {achievement_type} achievement!"
        except Exception as e:
            logger.error(f"Unexpected error in achievement description: {str(e)}")
            return f"Congratulations! You've earned the {achievement_type} achievement!"
    
    async def is_available(self) -> bool:
        """Check if Groq API is available."""
        try:
            await self._ensure_client()
            return self._is_available
        except Exception as e:
            logger.error(f"Error checking Groq availability: {str(e)}")
            return False
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        """Get Groq API usage statistics."""
        return {
            "is_available": await self.is_available(),
            "last_health_check": self._last_health_check.isoformat() if self._last_health_check else None,
            "health_check_interval": self._health_check_interval
        }


# Global service instance
groq_service = GroqService() 