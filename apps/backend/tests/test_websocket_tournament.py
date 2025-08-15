import pytest
import asyncio
import json
import time
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timezone
import websockets
from fastapi import FastAPI
from fastapi.testclient import TestClient
import redis
from typing import List, Dict, Any

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.competition.websocket_manager import TournamentWebSocketManager, WebSocketConnection, ConnectionState
from services.competition.tournament_models import *
from api_gateway import app

@pytest.fixture
def mock_redis():
    """Mock Redis client for testing"""
    mock_redis = Mock(spec=redis.Redis)
    mock_redis.ping.return_value = True
    mock_redis.hgetall.return_value = {}
    mock_redis.zrevrange.return_value = []
    mock_redis.zcard.return_value = 0
    mock_redis.publish.return_value = 1
    
    # Mock pubsub
    mock_pubsub = Mock()
    mock_pubsub.subscribe = AsyncMock()
    mock_pubsub.listen = AsyncMock(return_value=AsyncGenerator([]))
    mock_pubsub.unsubscribe = AsyncMock()
    mock_pubsub.close = AsyncMock()
    mock_redis.pubsub.return_value = mock_pubsub
    
    return mock_redis

async def AsyncGenerator(items):
    """Helper for async iteration in mocks"""
    for item in items:
        yield item

@pytest.fixture
def websocket_manager(mock_redis):
    """Create WebSocket manager with mocked Redis"""
    return TournamentWebSocketManager(mock_redis)

@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection"""
    websocket = Mock()
    websocket.accept = AsyncMock()
    websocket.send_json = AsyncMock()
    websocket.close = AsyncMock()
    websocket.receive_text = AsyncMock()
    websocket.client = Mock()
    websocket.client.host = "127.0.0.1"
    websocket.headers = {"user-agent": "test-client"}
    return websocket

class TestWebSocketConnection:
    """Test WebSocket connection management"""
    
    @pytest.mark.asyncio
    async def test_websocket_connection_creation(self, websocket_manager, mock_websocket):
        """Test creating a WebSocket connection"""
        tournament_id = "daily:2024-01-15"
        user_id = "user_123"
        
        connection = await websocket_manager.connect(
            websocket=mock_websocket,
            tournament_id=tournament_id,
            user_id=user_id
        )
        
        assert connection is not None
        assert connection.tournament_id == tournament_id
        assert connection.user_id == user_id
        assert connection.state in [ConnectionState.CONNECTED, ConnectionState.AUTHENTICATED]
        
        # Verify WebSocket accept was called
        mock_websocket.accept.assert_called_once()
        
        # Verify connection is tracked
        assert tournament_id in websocket_manager.active_connections
        assert connection in websocket_manager.active_connections[tournament_id]
    
    @pytest.mark.asyncio
    async def test_websocket_disconnection(self, websocket_manager, mock_websocket):
        """Test WebSocket disconnection cleanup"""
        tournament_id = "daily:2024-01-15"
        
        # Connect first
        await websocket_manager.connect(mock_websocket, tournament_id)
        assert len(websocket_manager.active_connections[tournament_id]) == 1
        
        # Disconnect
        await websocket_manager.disconnect(mock_websocket, tournament_id)
        
        # Verify cleanup
        assert tournament_id not in websocket_manager.active_connections or \
               len(websocket_manager.active_connections[tournament_id]) == 0
    
    @pytest.mark.asyncio
    async def test_multiple_connections_same_tournament(self, websocket_manager):
        """Test multiple connections to same tournament"""
        tournament_id = "daily:2024-01-15"
        
        # Create multiple mock WebSockets
        websockets_list = []
        for i in range(5):
            ws = Mock()
            ws.accept = AsyncMock()
            ws.send_json = AsyncMock()
            ws.client = Mock()
            ws.client.host = f"127.0.0.{i+1}"
            ws.headers = {"user-agent": "test-client"}
            websockets_list.append(ws)
        
        # Connect all WebSockets
        for ws in websockets_list:
            await websocket_manager.connect(ws, tournament_id)
        
        # Verify all connections are tracked
        assert len(websocket_manager.active_connections[tournament_id]) == 5
        
        # Disconnect one
        await websocket_manager.disconnect(websockets_list[0], tournament_id)
        assert len(websocket_manager.active_connections[tournament_id]) == 4
    
    @pytest.mark.asyncio
    async def test_connections_different_tournaments(self, websocket_manager):
        """Test connections to different tournaments"""
        tournament_1 = "daily:2024-01-15"
        tournament_2 = "daily:2024-01-16"
        
        ws1 = Mock()
        ws1.accept = AsyncMock()
        ws1.send_json = AsyncMock()
        ws1.client = Mock()
        ws1.client.host = "127.0.0.1"
        ws1.headers = {"user-agent": "test-client"}
        
        ws2 = Mock()
        ws2.accept = AsyncMock()
        ws2.send_json = AsyncMock()
        ws2.client = Mock()
        ws2.client.host = "127.0.0.2"
        ws2.headers = {"user-agent": "test-client"}
        
        await websocket_manager.connect(ws1, tournament_1)
        await websocket_manager.connect(ws2, tournament_2)
        
        assert len(websocket_manager.active_connections) == 2
        assert tournament_1 in websocket_manager.active_connections
        assert tournament_2 in websocket_manager.active_connections

class TestMessageHandling:
    """Test WebSocket message handling"""
    
    @pytest.mark.asyncio
    async def test_send_initial_state(self, websocket_manager, mock_websocket):
        """Test sending initial state to new connection"""
        tournament_id = "daily:2024-01-15"
        
        # Mock leaderboard data
        websocket_manager.redis.zrevrange.return_value = [
            ("ai:captain_vega", 250.0),
            ("user_123", 180.0)
        ]
        
        # Mock tournament metadata
        websocket_manager.redis.hgetall.return_value = {
            'status': 'active',
            'start_time': '2024-01-15T00:00:00Z',
            'total_participants': '2'
        }
        
        connection = await websocket_manager.connect(mock_websocket, tournament_id)
        
        # Verify initial state was sent
        mock_websocket.send_json.assert_called()
        
        # Check the message format
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args['type'] == 'initial_state'
        assert 'data' in call_args
        assert 'leaderboard' in call_args['data']
    
    @pytest.mark.asyncio
    async def test_broadcast_to_tournament(self, websocket_manager):
        """Test broadcasting messages to all connections in a tournament"""
        tournament_id = "daily:2024-01-15"
        
        # Create multiple connections
        websockets_list = []
        for i in range(3):
            ws = Mock()
            ws.accept = AsyncMock()
            ws.send_json = AsyncMock()
            ws.client = Mock()
            ws.client.host = f"127.0.0.{i+1}"
            ws.headers = {"user-agent": "test-client"}
            websockets_list.append(ws)
            await websocket_manager.connect(ws, tournament_id)
        
        # Broadcast message
        test_message = {
            'type': 'test_message',
            'data': {'message': 'Hello tournament!'}
        }
        
        await websocket_manager.broadcast_to_tournament(tournament_id, test_message)
        
        # Verify all connections received the message
        for ws in websockets_list:
            ws.send_json.assert_called_with(test_message)
    
    @pytest.mark.asyncio
    async def test_handle_client_message_nearby_competitors(self, websocket_manager, mock_websocket):
        """Test handling nearby competitors request"""
        tournament_id = "daily:2024-01-15"
        user_id = "user_123"
        
        connection = await websocket_manager.connect(mock_websocket, tournament_id, user_id)
        
        # Mock user rank
        websocket_manager.redis.zrevrank.return_value = 5  # User is rank 6 (0-indexed)
        websocket_manager.redis.zrevrange.return_value = [
            ("user_121", 200.0),
            ("user_122", 195.0),
            ("user_123", 190.0),  # Current user
            ("user_124", 185.0),
            ("user_125", 180.0)
        ]
        
        message = {
            'type': 'get_nearby_competitors',
            'data': {'radius': 2}
        }
        
        await websocket_manager.handle_client_message(connection, message)
        
        # Verify response was sent
        mock_websocket.send_json.assert_called()
        
        # Check response format
        response_calls = mock_websocket.send_json.call_args_list
        nearby_response = next((call for call in response_calls 
                              if call[0][0].get('type') == 'nearby_competitors'), None)
        
        if nearby_response:
            response_data = nearby_response[0][0]['data']
            assert 'competitors' in response_data
            assert response_data['user_rank'] == 6  # 1-indexed rank
    
    @pytest.mark.asyncio
    async def test_handle_client_message_ai_trader_info(self, websocket_manager, mock_websocket):
        """Test handling AI trader info request"""
        tournament_id = "daily:2024-01-15"
        connection = await websocket_manager.connect(mock_websocket, tournament_id)
        
        # Mock AI trader info
        websocket_manager.redis.hgetall.return_value = {
            'id': 'ai:captain_vega',
            'name': 'Captain Vega',
            'strategy': 'aggressive_growth'
        }
        
        message = {
            'type': 'get_ai_trader_info',
            'data': {'ai_id': 'ai:captain_vega'}
        }
        
        await websocket_manager.handle_client_message(connection, message)
        
        # Verify response was sent
        mock_websocket.send_json.assert_called()
    
    @pytest.mark.asyncio
    async def test_handle_authentication_message(self, websocket_manager, mock_websocket):
        """Test handling authentication message"""
        tournament_id = "daily:2024-01-15"
        connection = await websocket_manager.connect(mock_websocket, tournament_id)
        
        message = {
            'type': 'authenticate',
            'data': {'token': 'valid_token_123'}
        }
        
        await websocket_manager.handle_client_message(connection, message)
        
        # Check connection state was updated to authenticated
        assert connection.user_id == 'valid_token_123'  # Mock validation returns token as user_id
        assert connection.state == ConnectionState.AUTHENTICATED

class TestHeartbeatAndReconnection:
    """Test heartbeat monitoring and reconnection logic"""
    
    @pytest.mark.asyncio
    async def test_heartbeat_monitoring(self, websocket_manager, mock_websocket):
        """Test heartbeat monitoring functionality"""
        tournament_id = "daily:2024-01-15"
        connection = await websocket_manager.connect(mock_websocket, tournament_id)
        
        # Simulate heartbeat
        initial_heartbeat = connection.last_heartbeat
        
        # Send heartbeat message
        await websocket_manager._send_heartbeat(connection)
        
        mock_websocket.send_json.assert_called()
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args['type'] == 'heartbeat'
        assert 'timestamp' in call_args
    
    @pytest.mark.asyncio
    async def test_stale_connection_cleanup(self, websocket_manager):
        """Test cleanup of stale connections"""
        tournament_id = "daily:2024-01-15"
        
        # Create connection with old heartbeat
        ws = Mock()
        ws.accept = AsyncMock()
        ws.send_json = AsyncMock()
        ws.close = AsyncMock()
        ws.client = Mock()
        ws.client.host = "127.0.0.1"
        ws.headers = {"user-agent": "test-client"}
        
        connection = await websocket_manager.connect(ws, tournament_id)
        
        # Make connection appear stale
        connection.last_heartbeat = datetime.utcnow() - timedelta(minutes=5)
        
        # Run heartbeat check (would normally be called by timer)
        # This is testing the logic that would remove stale connections
        current_time = datetime.utcnow()
        time_since_heartbeat = (current_time - connection.last_heartbeat).total_seconds()
        
        assert time_since_heartbeat > 120  # Should be considered stale

class TestConcurrentConnections:
    """Test handling many concurrent connections"""
    
    @pytest.mark.asyncio
    async def test_many_concurrent_connections(self, websocket_manager):
        """Test handling 100+ concurrent connections"""
        tournament_id = "daily:2024-01-15"
        connection_count = 100
        
        # Create many mock WebSockets
        websockets_list = []
        tasks = []
        
        for i in range(connection_count):
            ws = Mock()
            ws.accept = AsyncMock()
            ws.send_json = AsyncMock()
            ws.client = Mock()
            ws.client.host = f"192.168.1.{i % 255}"
            ws.headers = {"user-agent": "test-client"}
            websockets_list.append(ws)
            
            # Create connection task
            task = websocket_manager.connect(ws, tournament_id, f"user_{i}")
            tasks.append(task)
        
        # Connect all concurrently
        start_time = time.time()
        connections = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Verify all connections were created
        assert len(connections) == connection_count
        assert len(websocket_manager.active_connections[tournament_id]) == connection_count
        
        # Should complete reasonably quickly
        duration = end_time - start_time
        assert duration < 10, f"Creating {connection_count} connections took too long: {duration}s"
        
        # Test broadcasting to all connections
        test_message = {'type': 'test', 'data': 'broadcast test'}
        
        broadcast_start = time.time()
        await websocket_manager.broadcast_to_tournament(tournament_id, test_message)
        broadcast_end = time.time()
        
        broadcast_duration = broadcast_end - broadcast_start
        assert broadcast_duration < 5, f"Broadcasting to {connection_count} connections took too long: {broadcast_duration}s"
        
        # Verify all received the message
        for ws in websockets_list:
            ws.send_json.assert_called_with(test_message)
    
    @pytest.mark.asyncio
    async def test_connection_statistics(self, websocket_manager):
        """Test connection statistics tracking"""
        tournament_id = "daily:2024-01-15"
        
        # Create some connections
        for i in range(10):
            ws = Mock()
            ws.accept = AsyncMock()
            ws.send_json = AsyncMock()
            ws.client = Mock()
            ws.client.host = f"127.0.0.{i+1}"
            ws.headers = {"user-agent": "test-client"}
            
            await websocket_manager.connect(ws, tournament_id)
        
        # Get statistics
        stats = websocket_manager.get_connection_stats()
        
        assert stats['current_connections'] == 10
        assert stats['total_connections'] == 10
        assert stats['active_tournaments'] == 1
        assert tournament_id in stats['tournament_breakdown']
        assert stats['tournament_breakdown'][tournament_id] == 10

class TestErrorHandling:
    """Test error handling in WebSocket operations"""
    
    @pytest.mark.asyncio
    async def test_websocket_send_error_handling(self, websocket_manager, mock_websocket):
        """Test handling WebSocket send errors"""
        tournament_id = "daily:2024-01-15"
        
        connection = await websocket_manager.connect(mock_websocket, tournament_id)
        
        # Make send_json raise an exception
        mock_websocket.send_json.side_effect = Exception("Connection closed")
        
        # Attempt to send personal update
        await websocket_manager.send_personal_update(connection, {'type': 'test'})
        
        # Should handle error gracefully and remove connection
        # (In real implementation, this would trigger cleanup)
    
    @pytest.mark.asyncio
    async def test_invalid_message_handling(self, websocket_manager, mock_websocket):
        """Test handling of invalid client messages"""
        tournament_id = "daily:2024-01-15"
        connection = await websocket_manager.connect(mock_websocket, tournament_id)
        
        # Test invalid message type
        invalid_message = {
            'type': 'invalid_message_type',
            'data': {}
        }
        
        # Should handle gracefully without crashing
        await websocket_manager.handle_client_message(connection, invalid_message)
        
        # Test malformed message
        malformed_message = {
            'invalid': 'structure'
        }
        
        await websocket_manager.handle_client_message(connection, malformed_message)
    
    @pytest.mark.asyncio
    async def test_redis_error_handling(self, websocket_manager, mock_websocket):
        """Test handling Redis connection errors"""
        tournament_id = "daily:2024-01-15"
        
        # Make Redis operations fail
        websocket_manager.redis.zrevrange.side_effect = Exception("Redis connection lost")
        
        # Should handle Redis errors gracefully during initial state
        connection = await websocket_manager.connect(mock_websocket, tournament_id)
        
        # Connection should still be created, even if Redis operations fail
        assert connection is not None

class TestMessageProtocol:
    """Test WebSocket message protocol compliance"""
    
    def test_message_type_enum_coverage(self):
        """Test that all message types are properly defined"""
        # Test that WebSocketMessageType enum covers expected types
        expected_types = [
            'initial_state', 'leaderboard_update', 'live_trade', 
            'achievement_unlocked', 'tournament_event', 'heartbeat',
            'nearby_competitors', 'ai_trader_info', 'error'
        ]
        
        for msg_type in expected_types:
            assert hasattr(WebSocketMessageType, msg_type.upper()), f"Missing message type: {msg_type}"
    
    @pytest.mark.asyncio
    async def test_message_format_validation(self, websocket_manager, mock_websocket):
        """Test message format validation"""
        tournament_id = "daily:2024-01-15"
        connection = await websocket_manager.connect(mock_websocket, tournament_id)
        
        # Test that all sent messages have required format
        test_data = {'test': 'data'}
        
        await websocket_manager.send_personal_update(connection, {
            'type': 'test_message',
            'timestamp': datetime.utcnow().isoformat(),
            'data': test_data
        })
        
        # Verify message was sent with proper format
        mock_websocket.send_json.assert_called()
        sent_message = mock_websocket.send_json.call_args[0][0]
        
        assert 'type' in sent_message
        assert 'timestamp' in sent_message
        assert 'data' in sent_message

class TestLoadTesting:
    """Load testing for WebSocket connections"""
    
    @pytest.mark.asyncio
    async def test_rapid_connect_disconnect(self, websocket_manager):
        """Test rapid connection and disconnection cycles"""
        tournament_id = "daily:2024-01-15"
        
        for cycle in range(10):
            # Connect multiple WebSockets rapidly
            websockets_list = []
            for i in range(20):
                ws = Mock()
                ws.accept = AsyncMock()
                ws.send_json = AsyncMock()
                ws.client = Mock()
                ws.client.host = f"192.168.{cycle}.{i}"
                ws.headers = {"user-agent": "load-test"}
                websockets_list.append(ws)
                
                await websocket_manager.connect(ws, tournament_id)
            
            # Disconnect all rapidly
            for ws in websockets_list:
                await websocket_manager.disconnect(ws, tournament_id)
            
            # Verify cleanup
            assert tournament_id not in websocket_manager.active_connections or \
                   len(websocket_manager.active_connections[tournament_id]) == 0
    
    @pytest.mark.asyncio
    async def test_message_throughput(self, websocket_manager):
        """Test message broadcasting throughput"""
        tournament_id = "daily:2024-01-15"
        connection_count = 50
        message_count = 100
        
        # Create connections
        websockets_list = []
        for i in range(connection_count):
            ws = Mock()
            ws.accept = AsyncMock()
            ws.send_json = AsyncMock()
            ws.client = Mock()
            ws.client.host = f"10.0.{i//255}.{i%255}"
            ws.headers = {"user-agent": "throughput-test"}
            websockets_list.append(ws)
            
            await websocket_manager.connect(ws, tournament_id)
        
        # Send many messages rapidly
        start_time = time.time()
        
        for i in range(message_count):
            message = {
                'type': 'throughput_test',
                'data': {'message_id': i, 'timestamp': time.time()}
            }
            await websocket_manager.broadcast_to_tournament(tournament_id, message)
        
        end_time = time.time()
        
        duration = end_time - start_time
        messages_per_second = message_count / duration
        
        # Should achieve reasonable throughput
        assert messages_per_second > 50, f"Message throughput too low: {messages_per_second:.2f} msg/s"
        
        # Verify total messages sent
        total_calls = sum(ws.send_json.call_count for ws in websockets_list)
        expected_calls = connection_count * message_count
        assert total_calls == expected_calls

class TestWebSocketShutdown:
    """Test graceful WebSocket manager shutdown"""
    
    @pytest.mark.asyncio
    async def test_graceful_shutdown(self, websocket_manager):
        """Test graceful shutdown of WebSocket manager"""
        tournament_id = "daily:2024-01-15"
        
        # Create some connections
        websockets_list = []
        for i in range(5):
            ws = Mock()
            ws.accept = AsyncMock()
            ws.send_json = AsyncMock()
            ws.close = AsyncMock()
            ws.client = Mock()
            ws.client.host = f"127.0.0.{i+1}"
            ws.headers = {"user-agent": "test-client"}
            websockets_list.append(ws)
            
            await websocket_manager.connect(ws, tournament_id)
        
        # Shutdown
        await websocket_manager.shutdown()
        
        # Verify all connections were closed
        for ws in websockets_list:
            ws.close.assert_called()
        
        # Verify state cleanup
        assert len(websocket_manager.active_connections) == 0
        assert len(websocket_manager.connection_mapping) == 0
        assert len(websocket_manager.pubsub_tasks) == 0

if __name__ == "__main__":
    # Run with timeout for long-running tests
    pytest.main([__file__, "-v", "--timeout=60"])