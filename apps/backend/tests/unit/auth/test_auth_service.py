import sys
sys.path.append("/Users/admin/AstraTrade-Project")
from apps.backend.auth.auth_service import AuthService
import pytest

class TestAuthService:
    def test_token_generation(self):
        service = AuthService()
        token = service.generate_token(user_id=123)
        assert isinstance(token, str)
        assert len(token) > 30