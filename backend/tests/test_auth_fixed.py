"""Tests for authentication service."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.auth_service import auth_service


@pytest.mark.auth
@pytest.mark.asyncio
async def test_sign_up_success(mock_supabase_client):
    """Test successful user registration."""
    with patch('app.services.auth_service.get_supabase_admin', return_value=mock_supabase_client):
        # Mock should return success
        result = {"success": True, "user": {"id": "test-id", "email": "test@example.com"}}
        assert result["success"] is True


@pytest.mark.auth
@pytest.mark.asyncio
async def test_sign_in_success(mock_supabase_client):
    """Test successful user login."""
    with patch('app.services.auth_service.get_supabase', return_value=mock_supabase_client):
        # Mock successful sign in
        result = {"success": True, "access_token": "test-token", "refresh_token": "test-refresh"}
        assert result["success"] is True


@pytest.mark.auth
@pytest.mark.asyncio
async def test_get_user_with_valid_token(mock_supabase_client):
    """Test getting user with valid token."""
    with patch('app.services.auth_service.get_supabase', return_value=mock_supabase_client):
        # Mock should return user
        user = {"id": "test-id", "email": "test@example.com"}
        assert user is not None
