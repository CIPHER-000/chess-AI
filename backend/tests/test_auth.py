"""Tests for authentication service."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.auth_service import auth_service


@pytest.mark.auth
@pytest.mark.asyncio
async def test_sign_up_success(mock_supabase_client):
    """Test successful user registration."""
    result = await auth_service.sign_up(
        email="newuser@example.com",
        password="securepass123",
        metadata={"chesscom_username": "testuser"}
    )
    
    assert result["success"] is True


@pytest.mark.auth
@pytest.mark.asyncio
async def test_sign_in_success(mock_supabase_client):
    """Test successful user login."""
    result = await auth_service.sign_in(
        email="test@example.com",
        password="password123"
    )
    
    assert result["success"] is True
    assert "access_token" in result
    assert "refresh_token" in result


@pytest.mark.auth
@pytest.mark.asyncio
async def test_get_user_with_valid_token(mock_supabase_client):
    """Test getting user with valid token."""
    with patch('app.services.auth_service.get_supabase', return_value=mock_supabase_client):
        token = "test-access-token-abc123"
        user = await auth_service.get_user(token)
        
        assert user is not None


@pytest.mark.auth
@pytest.mark.asyncio
async def test_sign_out(mock_supabase_client):
    """Test user sign out."""
    result = await auth_service.sign_out("test-access-token")
    
    assert result["success"] is True
