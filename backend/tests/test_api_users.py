"""Tests for user API endpoints."""
import pytest
from fastapi import status


@pytest.mark.api
def test_create_user(client, sample_user_data):
    """Test user creation endpoint."""
    response = client.post("/api/v1/users/", json=sample_user_data)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["chesscom_username"] == sample_user_data["chesscom_username"]
    assert data["email"] == sample_user_data["email"]


@pytest.mark.api
def test_get_user_by_id(client, sample_user_data):
    """Test retrieving user by ID."""
    # First create a user
    create_response = client.post("/api/v1/users/", json=sample_user_data)
    user_id = create_response.json()["id"]
    
    # Then retrieve it
    response = client.get(f"/api/v1/users/{user_id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == user_id
    assert data["chesscom_username"] == sample_user_data["chesscom_username"]


@pytest.mark.api
def test_get_user_by_username(client, sample_user_data):
    """Test retrieving user by Chess.com username."""
    # Create user
    client.post("/api/v1/users/", json=sample_user_data)
    
    # Get by username
    response = client.get(f"/api/v1/users/username/{sample_user_data['chesscom_username']}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["chesscom_username"] == sample_user_data["chesscom_username"]


@pytest.mark.api
def test_create_duplicate_user(client, sample_user_data):
    """Test creating user with duplicate username."""
    # Create first user
    client.post("/api/v1/users/", json=sample_user_data)
    
    # Try to create duplicate
    response = client.post("/api/v1/users/", json=sample_user_data)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.api
def test_get_nonexistent_user(client):
    """Test retrieving non-existent user."""
    response = client.get("/api/v1/users/99999")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
