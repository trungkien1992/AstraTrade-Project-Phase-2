from fastapi import WebSocket, WebSocketDisconnect, Query
from typing import Dict, Set, Optional, List
import asyncio
import json
import redis
from datetime import datetime
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ConnectionState(Enum):
    CONNECTING = "connecting"
    CONNECTED = "connected"
    AUTHENTICATED = "authenticated"
    DISCONNECTED = "disconnected"

@dataclass
class WebSocketConnection:
    """Represents a WebSocket connection with metadata"""
    websocket: WebSocket
    user_id: Optional[str]
    tournament_id: str
    connection_time: datetime
    last_heartbeat: datetime
    state: ConnectionState
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class TournamentWebSocketManager:
    """Manages WebSocket connections for tournament live updates"""
    
    def __init__(self, redis_client: redis.Redis):
        # tournament_id -> set of connections
        self.active_connections: Dict[str, Set[WebSocketConnection]] = {}
        # websocket -> connection mapping for quick lookup
        self.connection_mapping: Dict[WebSocket, WebSocketConnection] = {}
        # Redis pub/sub tasks
        self.pubsub_tasks: Dict[str, asyncio.Task] = {}
        # Redis client for pub/sub
        self.redis_client = redis_client
        # Connection statistics
        self.connection_stats = {
            'total_connections': 0,
            'peak_concurrent': 0,
            'messages_sent': 0,
            'messages_received': 0,
            'reconnections': 0
        }
        
        # Heartbeat task
        self.heartbeat_task = None
        self.start_heartbeat_monitor()
        
    def start_heartbeat_monitor(self):
        """Start the heartbeat monitoring task"""
        if self.heartbeat_task is None or self.heartbeat_task.done():
            self.heartbeat_task = asyncio.create_task(self._heartbeat_monitor())
    
    async def _heartbeat_monitor(self):
        """Monitor connections and send heartbeats"""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                current_time = datetime.utcnow()
                dead_connections = []
                
                # Check all active connections
                for tournament_id, connections in self.active_connections.items():
                    for conn in list(connections):
                        # Check if connection is stale (no heartbeat in 2 minutes)
                        if (current_time - conn.last_heartbeat).total_seconds() > 120:
                            dead_connections.append((conn, tournament_id))
                        else:
                            # Send heartbeat ping
                            try:
                                await self._send_heartbeat(conn)
                            except:
                                dead_connections.append((conn, tournament_id))
                
                # Clean up dead connections
                for conn, tournament_id in dead_connections:
                    await self.disconnect(conn.websocket, tournament_id)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat monitor: {e}")
                await asyncio.sleep(5)
    
    async def _send_heartbeat(self, connection: WebSocketConnection):
        """Send heartbeat ping to connection"""
        heartbeat_message = {
            'type': 'heartbeat',
            'timestamp': datetime.utcnow().isoformat(),
            'server_time': datetime.utcnow().timestamp()
        }
        await connection.websocket.send_json(heartbeat_message)
    
    async def connect(self, websocket: WebSocket, tournament_id: str, user_id: Optional[str] = None, 
                     ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        """Accept new WebSocket connection"""
        try:
            await websocket.accept()
            
            # Create connection object
            connection = WebSocketConnection(
                websocket=websocket,
                user_id=user_id,
                tournament_id=tournament_id,
                connection_time=datetime.utcnow(),
                last_heartbeat=datetime.utcnow(),
                state=ConnectionState.CONNECTED if user_id else ConnectionState.CONNECTING,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Add to connection pool
            if tournament_id not in self.active_connections:
                self.active_connections[tournament_id] = set()
                # Start pubsub listener for this tournament
                self.pubsub_tasks[tournament_id] = asyncio.create_task(
                    self._pubsub_listener(tournament_id)
                )
                
            self.active_connections[tournament_id].add(connection)
            self.connection_mapping[websocket] = connection
            
            # Update statistics
            self.connection_stats['total_connections'] += 1
            current_concurrent = sum(len(conns) for conns in self.active_connections.values())
            if current_concurrent > self.connection_stats['peak_concurrent']:
                self.connection_stats['peak_concurrent'] = current_concurrent
            
            # Send initial tournament state
            await self._send_initial_state(connection)
            
            # Log connection
            logger.info(f"WebSocket connected: tournament={tournament_id}, user={user_id}, "
                       f"ip={ip_address}, total_active={current_concurrent}")
            
            return connection
            
        except Exception as e:
            logger.error(f"Error accepting WebSocket connection: {e}")
            await websocket.close()
            raise
        
    async def disconnect(self, websocket: WebSocket, tournament_id: str = None):
        """Handle WebSocket disconnection"""
        try:
            connection = self.connection_mapping.get(websocket)
            if not connection:
                return
                
            # Determine tournament ID
            if not tournament_id:
                tournament_id = connection.tournament_id
            
            # Remove from connection pool
            if tournament_id in self.active_connections:
                self.active_connections[tournament_id].discard(connection)
                
                # Clean up if no more connections
                if not self.active_connections[tournament_id]:
                    del self.active_connections[tournament_id]
                    # Cancel pubsub task
                    if tournament_id in self.pubsub_tasks:
                        self.pubsub_tasks[tournament_id].cancel()
                        del self.pubsub_tasks[tournament_id]
                        
            # Remove from mapping
            self.connection_mapping.pop(websocket, None)
            
            # Update connection state
            connection.state = ConnectionState.DISCONNECTED
            
            # Log disconnection
            logger.info(f"WebSocket disconnected: tournament={tournament_id}, user={connection.user_id}")
            
        except Exception as e:
            logger.error(f"Error handling WebSocket disconnection: {e}")
        
    async def broadcast_to_tournament(self, tournament_id: str, message: dict, exclude_user: Optional[str] = None):
        """Send message to all connections in a tournament"""
        if tournament_id not in self.active_connections:
            return
            
        connections = list(self.active_connections[tournament_id])  # Copy to avoid modification during iteration
        dead_connections = []
        sent_count = 0
        
        for connection in connections:
            # Skip excluded user
            if exclude_user and connection.user_id == exclude_user:
                continue
                
            try:
                await connection.websocket.send_json(message)
                sent_count += 1
                self.connection_stats['messages_sent'] += 1
            except Exception as e:
                logger.warning(f"Failed to send message to connection: {e}")
                dead_connections.append(connection)
                
        # Clean up dead connections
        for dead_conn in dead_connections:
            await self.disconnect(dead_conn.websocket, tournament_id)
        
        logger.debug(f"Broadcast to {sent_count} connections in tournament {tournament_id}")
            
    async def send_personal_update(self, connection: WebSocketConnection, message: dict):
        """Send personalized update to specific connection"""
        try:
            await connection.websocket.send_json(message)
            connection.last_heartbeat = datetime.utcnow()
            self.connection_stats['messages_sent'] += 1
        except Exception as e:
            logger.warning(f"Failed to send personal update: {e}")
            await self.disconnect(connection.websocket)
            
    async def _send_initial_state(self, connection: WebSocketConnection):
        """Send initial tournament state to new connection"""
        try:
            tournament_id = connection.tournament_id
            
            # Get current leaderboard (top 20)
            leaderboard_key = f"tournament:{tournament_id}:leaderboard"
            raw_leaderboard = self.redis_client.zrevrange(leaderboard_key, 0, 19, withscores=True)
            
            leaderboard = []
            for rank, (user_id, score) in enumerate(raw_leaderboard, 1):
                # Basic user info (would integrate with user service in production)
                is_ai = user_id.startswith('ai:')
                username = self._get_display_name(user_id, is_ai)
                
                leaderboard.append({
                    'rank': rank,
                    'user_id': user_id,
                    'username': username,
                    'score': score,
                    'is_ai': is_ai
                })
            
            # Get user's current rank if authenticated
            user_rank = None
            user_score = None
            if connection.user_id:
                user_score = self.redis_client.zscore(leaderboard_key, connection.user_id)
                if user_score is not None:
                    user_rank = self.redis_client.zrevrank(leaderboard_key, connection.user_id)
                    if user_rank is not None:
                        user_rank += 1  # Convert to 1-based ranking
            
            # Get tournament metadata
            tournament_meta = self.redis_client.hgetall(f"tournament:{tournament_id}:meta")
            
            # Get active connection count
            active_connections = len(self.active_connections.get(tournament_id, set()))
            
            initial_state = {
                'type': 'initial_state',
                'timestamp': datetime.utcnow().isoformat(),
                'data': {
                    'tournament_id': tournament_id,
                    'leaderboard': leaderboard,
                    'user_rank': user_rank,
                    'user_score': user_score,
                    'active_connections': active_connections,
                    'tournament_meta': tournament_meta,
                    'server_time': datetime.utcnow().timestamp()
                }
            }
            
            await self.send_personal_update(connection, initial_state)
            
        except Exception as e:
            logger.error(f"Error sending initial state: {e}")
            
    def _get_display_name(self, user_id: str, is_ai: bool) -> str:
        """Get display name for user"""
        if is_ai:
            # Extract AI name from ID
            return user_id.replace('ai:', '').replace('_', ' ').title()
        else:
            # Generate display name for human user
            return f"Trader_{user_id[-6:]}"
        
    async def _pubsub_listener(self, tournament_id: str):
        """Listen to Redis pub/sub for tournament updates"""
        pubsub = self.redis_client.pubsub()
        
        try:
            # Subscribe to tournament channels
            await pubsub.subscribe(
                f'tournament:{tournament_id}:leaderboard',
                f'tournament:{tournament_id}:trades',
                f'tournament:{tournament_id}:achievements',
                f'tournament:{tournament_id}:events'
            )
            
            logger.info(f"Started pubsub listener for tournament {tournament_id}")
            
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        channel = message['channel'].decode('utf-8')
                        
                        # Format message based on channel
                        formatted_message = None
                        
                        if 'leaderboard' in channel:
                            formatted_message = {
                                'type': 'leaderboard_update',
                                'timestamp': datetime.utcnow().isoformat(),
                                'data': data
                            }
                        elif 'trades' in channel:
                            formatted_message = {
                                'type': 'live_trade',
                                'timestamp': datetime.utcnow().isoformat(),
                                'data': data
                            }
                        elif 'achievements' in channel:
                            formatted_message = {
                                'type': 'achievement_unlocked',
                                'timestamp': datetime.utcnow().isoformat(),
                                'data': data
                            }
                        elif 'events' in channel:
                            formatted_message = {
                                'type': 'tournament_event',
                                'timestamp': datetime.utcnow().isoformat(),
                                'data': data
                            }
                        
                        if formatted_message:
                            await self.broadcast_to_tournament(tournament_id, formatted_message)
                            
                    except Exception as e:
                        logger.error(f"Error processing pubsub message: {e}")
                        
        except asyncio.CancelledError:
            logger.info(f"Pubsub listener cancelled for tournament {tournament_id}")
        except Exception as e:
            logger.error(f"Error in pubsub listener for tournament {tournament_id}: {e}")
        finally:
            try:
                await pubsub.unsubscribe()
                await pubsub.close()
            except:
                pass
                
    async def handle_client_message(self, connection: WebSocketConnection, message: dict):
        """Process messages from WebSocket clients"""
        try:
            msg_type = message.get('type')
            self.connection_stats['messages_received'] += 1
            
            # Update last heartbeat
            connection.last_heartbeat = datetime.utcnow()
            
            if msg_type == 'heartbeat_response':
                # Client responding to heartbeat - already updated last_heartbeat above
                pass
                
            elif msg_type == 'get_nearby_competitors':
                await self._handle_nearby_competitors_request(connection, message)
                
            elif msg_type == 'get_ai_trader_info':
                await self._handle_ai_trader_info_request(connection, message)
                
            elif msg_type == 'get_detailed_leaderboard':
                await self._handle_detailed_leaderboard_request(connection, message)
                
            elif msg_type == 'authenticate':
                await self._handle_authentication(connection, message)
                
            else:
                logger.warning(f"Unknown message type from client: {msg_type}")
                
        except Exception as e:
            logger.error(f"Error handling client message: {e}")
    
    async def _handle_nearby_competitors_request(self, connection: WebSocketConnection, message: dict):
        """Handle request for nearby competitors"""
        if not connection.user_id:
            return
            
        try:
            tournament_id = connection.tournament_id
            user_id = connection.user_id
            radius = message.get('radius', 5)
            
            # Get user's current rank
            leaderboard_key = f"tournament:{tournament_id}:leaderboard"
            user_rank = self.redis_client.zrevrank(leaderboard_key, user_id)
            
            if user_rank is None:
                return
                
            # Calculate range
            start = max(0, user_rank - radius)
            end = user_rank + radius
            
            # Get nearby competitors
            raw_leaderboard = self.redis_client.zrevrange(leaderboard_key, start, end, withscores=True)
            
            nearby_competitors = []
            for idx, (competitor_id, score) in enumerate(raw_leaderboard):
                is_ai = competitor_id.startswith('ai:')
                nearby_competitors.append({
                    'rank': start + idx + 1,
                    'user_id': competitor_id,
                    'username': self._get_display_name(competitor_id, is_ai),
                    'score': score,
                    'is_ai': is_ai,
                    'is_current_user': competitor_id == user_id
                })
            
            response = {
                'type': 'nearby_competitors',
                'timestamp': datetime.utcnow().isoformat(),
                'data': {
                    'competitors': nearby_competitors,
                    'user_rank': user_rank + 1,
                    'radius': radius
                }
            }
            
            await self.send_personal_update(connection, response)
            
        except Exception as e:
            logger.error(f"Error handling nearby competitors request: {e}")
    
    async def _handle_ai_trader_info_request(self, connection: WebSocketConnection, message: dict):
        """Handle request for AI trader information"""
        try:
            ai_id = message.get('ai_id')
            if not ai_id:
                return
            
            # Get AI trader info from Redis or competition service
            # This would integrate with the competition service's get_ai_trader_info method
            ai_info_key = f"ai_trader_info:{ai_id}"
            ai_info = self.redis_client.hgetall(ai_info_key)
            
            if ai_info:
                response = {
                    'type': 'ai_trader_info',
                    'timestamp': datetime.utcnow().isoformat(),
                    'data': ai_info
                }
                
                await self.send_personal_update(connection, response)
                
        except Exception as e:
            logger.error(f"Error handling AI trader info request: {e}")
    
    async def _handle_detailed_leaderboard_request(self, connection: WebSocketConnection, message: dict):
        """Handle request for detailed leaderboard"""
        try:
            start = message.get('start', 0)
            limit = message.get('limit', 50)
            end = start + limit - 1
            
            tournament_id = connection.tournament_id
            leaderboard_key = f"tournament:{tournament_id}:leaderboard"
            
            raw_leaderboard = self.redis_client.zrevrange(leaderboard_key, start, end, withscores=True)
            
            detailed_leaderboard = []
            for idx, (user_id, score) in enumerate(raw_leaderboard):
                is_ai = user_id.startswith('ai:')
                
                # Get additional stats
                stats_key = f"tournament:{tournament_id}:stats:{user_id}"
                user_stats = self.redis_client.hgetall(stats_key)
                
                detailed_leaderboard.append({
                    'rank': start + idx + 1,
                    'user_id': user_id,
                    'username': self._get_display_name(user_id, is_ai),
                    'score': score,
                    'is_ai': is_ai,
                    'stats': user_stats
                })
            
            response = {
                'type': 'detailed_leaderboard',
                'timestamp': datetime.utcnow().isoformat(),
                'data': {
                    'leaderboard': detailed_leaderboard,
                    'start': start,
                    'limit': limit,
                    'total_participants': self.redis_client.zcard(leaderboard_key)
                }
            }
            
            await self.send_personal_update(connection, response)
            
        except Exception as e:
            logger.error(f"Error handling detailed leaderboard request: {e}")
    
    async def _handle_authentication(self, connection: WebSocketConnection, message: dict):
        """Handle user authentication"""
        try:
            token = message.get('token')
            if not token:
                return
            
            # Validate token (would integrate with auth service)
            # For now, mock validation
            user_id = self._validate_auth_token(token)
            
            if user_id:
                connection.user_id = user_id
                connection.state = ConnectionState.AUTHENTICATED
                
                # Send updated initial state with user-specific data
                await self._send_initial_state(connection)
                
                # Send authentication success
                auth_response = {
                    'type': 'authentication_success',
                    'timestamp': datetime.utcnow().isoformat(),
                    'data': {
                        'user_id': user_id,
                        'authenticated': True
                    }
                }
                
                await self.send_personal_update(connection, auth_response)
                
        except Exception as e:
            logger.error(f"Error handling authentication: {e}")
    
    def _validate_auth_token(self, token: str) -> Optional[str]:
        """Validate authentication token and return user ID"""
        # Mock implementation - would integrate with real auth service
        if token.startswith('user_'):
            return token
        return None
    
    def get_connection_stats(self) -> Dict:
        """Get connection statistics"""
        current_connections = sum(len(conns) for conns in self.active_connections.values())
        tournament_stats = {
            tournament_id: len(connections) 
            for tournament_id, connections in self.active_connections.items()
        }
        
        return {
            **self.connection_stats,
            'current_connections': current_connections,
            'active_tournaments': len(self.active_connections),
            'tournament_breakdown': tournament_stats
        }
    
    async def shutdown(self):
        """Gracefully shutdown the WebSocket manager"""
        logger.info("Shutting down WebSocket manager...")
        
        # Cancel heartbeat monitor
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # Cancel all pubsub tasks
        for task in self.pubsub_tasks.values():
            task.cancel()
            
        await asyncio.gather(*self.pubsub_tasks.values(), return_exceptions=True)
        
        # Close all connections
        all_connections = []
        for connections in self.active_connections.values():
            all_connections.extend(connections)
            
        for connection in all_connections:
            try:
                await connection.websocket.close()
            except:
                pass
        
        # Clear state
        self.active_connections.clear()
        self.connection_mapping.clear()
        self.pubsub_tasks.clear()
        
        logger.info("WebSocket manager shutdown complete")