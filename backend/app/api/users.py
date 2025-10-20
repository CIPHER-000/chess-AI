from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..core.database import get_db
from ..models import User
from ..services.chesscom_api import chesscom_api, ChessComAPIError

router = APIRouter()


class UserCreate(BaseModel):
    chesscom_username: str
    email: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    chesscom_username: str
    display_name: Optional[str]
    email: Optional[str]
    is_active: bool
    current_ratings: Optional[dict] = None
    last_analysis_at: Optional[str] = None
    
    # Authentication status
    connection_type: str = "username_only"
    is_chesscom_connected: bool = False
    connection_status: str = "Public Data Only"
    can_access_private_data: bool = False
    
    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    email: Optional[str] = None
    analysis_preferences: Optional[dict] = None
    notification_preferences: Optional[dict] = None


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new user by validating their Chess.com username."""
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        User.chesscom_username == user_data.chesscom_username.lower()
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Validate Chess.com username by fetching profile
    try:
        profile_data = await chesscom_api.get_player_profile(user_data.chesscom_username)
        stats_data = await chesscom_api.get_player_stats(user_data.chesscom_username)
    except ChessComAPIError as e:
        raise HTTPException(status_code=400, detail=f"Chess.com user not found: {str(e)}")
    
    # Create user
    db_user = User(
        chesscom_username=user_data.chesscom_username.lower(),
        display_name=profile_data.get("name", user_data.chesscom_username),
        email=user_data.email,
        chesscom_profile=profile_data,
        current_ratings=stats_data
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/by-username/{username}", response_model=UserResponse)
async def get_user_by_username(username: str, db: Session = Depends(get_db)):
    """Get user by Chess.com username."""
    user = db.query(User).filter(User.chesscom_username == username.lower()).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, 
    user_update: UserProfileUpdate, 
    db: Session = Depends(get_db)
):
    """Update user profile."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user


@router.post("/{user_id}/refresh-profile")
async def refresh_user_profile(user_id: int, db: Session = Depends(get_db)):
    """Refresh user's Chess.com profile and stats."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        # Fetch updated profile and stats
        profile_data = await chesscom_api.get_player_profile(user.chesscom_username)
        stats_data = await chesscom_api.get_player_stats(user.chesscom_username)
        
        # Update user data
        user.chesscom_profile = profile_data
        user.current_ratings = stats_data
        user.display_name = profile_data.get("name", user.chesscom_username)
        
        db.commit()
        db.refresh(user)
        
        return {"message": "Profile refreshed successfully", "user": user}
        
    except ChessComAPIError as e:
        raise HTTPException(status_code=400, detail=f"Failed to refresh profile: {str(e)}")


@router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user and all associated data."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


@router.post("/{user_id}/connect-oauth")
async def connect_chesscom_oauth(user_id: int, db: Session = Depends(get_db)):
    """Placeholder for Chess.com OAuth connection (not yet available)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # This is a placeholder - Chess.com doesn't currently offer OAuth for third-party apps
    raise HTTPException(
        status_code=501, 
        detail={
            "error": "OAuth not available",
            "message": "Chess.com OAuth integration is not yet available. We're currently using public API access only.",
            "documentation": "Chess.com does not currently provide OAuth or authenticated API access for third-party applications.",
            "status": "planned",
            "alternative": "Currently using public game data via Chess.com's public API"
        }
    )


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """List all users (for admin purposes)."""
    users = db.query(User).offset(skip).limit(limit).all()
    return users
