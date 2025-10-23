from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator

from ..core.database import get_db
from ..models import User, Game
from ..services.chesscom_api import chesscom_api, ChessComAPIError

router = APIRouter()


class GameResponse(BaseModel):
    id: int
    chesscom_game_id: str
    chesscom_url: Optional[str]
    time_class: Optional[str]
    time_control: Optional[str]
    white_username: Optional[str]
    black_username: Optional[str]
    white_rating: Optional[int]
    black_rating: Optional[int]
    white_result: Optional[str]
    black_result: Optional[str]
    winner: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    is_analyzed: bool
    
    class Config:
        from_attributes = True


class GameFetchRequest(BaseModel):
    """Request model for fetching games from Chess.com."""
    
    days: Optional[int] = None  # Fetch games from last N days
    count: Optional[int] = None  # Fetch last N games
    time_classes: Optional[List[str]] = None  # e.g., ["rapid", "blitz"]
    
    @validator('count')
    def validate_mutually_exclusive(cls, v, values):
        """Ensure only one of days/count is specified."""
        if v is not None and values.get('days') is not None:
            raise ValueError("Specify either 'days' or 'count', not both")
        return v
    
    @validator('days', 'count', pre=True, always=True)
    def set_default(cls, v, values, field):
        """Set default to days=10 if neither specified."""
        if field.name == 'days' and v is None and values.get('count') is None:
            return 10  # Default to last 10 days
        return v


@router.post("/{user_id}/fetch")
async def fetch_recent_games(
    user_id: int,
    fetch_request: GameFetchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Fetch recent games for a user from Chess.com."""
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        # Fetch recent games from Chess.com
        raw_games = await chesscom_api.get_recent_games(
            user.chesscom_username, 
            days=fetch_request.days,
            count=fetch_request.count
        )
        
        # Determine fetch method used
        fetch_method = "count" if fetch_request.count else "days"
        fetch_value = fetch_request.count if fetch_request.count else fetch_request.days
        
        if not raw_games:
            return {"message": "No recent games found", "games_fetched": 0}
        
        games_added = 0
        games_updated = 0
        
        for raw_game in raw_games:
            # Parse game data
            game_data = chesscom_api.parse_game_data(raw_game, user.chesscom_username)
            
            # Filter by time class if specified
            if fetch_request.time_classes and game_data["time_class"] not in fetch_request.time_classes:
                continue
            
            # Check if game already exists
            existing_game = db.query(Game).filter(
                Game.chesscom_game_id == game_data["chesscom_game_id"]
            ).first()
            
            if existing_game:
                # Update existing game if needed
                games_updated += 1
                continue
            
            # Determine winner
            winner = None
            if game_data["white_result"] == "win":
                winner = "white"
            elif game_data["black_result"] == "win":
                winner = "black"
            elif game_data["white_result"] in ["agreed", "stalemate", "repetition", "insufficient"]:
                winner = "draw"
            
            # Create new game record
            game = Game(
                user_id=user.id,
                chesscom_game_id=game_data["chesscom_game_id"],
                chesscom_url=game_data["chesscom_url"],
                time_class=game_data["time_class"],
                time_control=game_data["time_control"],
                rules=game_data["rules"],
                white_username=game_data["white_username"],
                black_username=game_data["black_username"],
                white_rating=game_data["white_rating"],
                black_rating=game_data["black_rating"],
                white_result=game_data["white_result"],
                black_result=game_data["black_result"],
                winner=winner,
                pgn=game_data["pgn"],
                fen=game_data["fen"],
                start_time=game_data["start_time"],
                end_time=game_data["end_time"]
            )
            
            db.add(game)
            games_added += 1
        
        db.commit()
        
        # Count existing games for this user
        existing_games_count = db.query(Game).filter(Game.user_id == user.id).count()
        
        return {
            "message": f"Successfully fetched games",
            "games_added": games_added,
            "games_updated": games_updated,
            "total_games": games_added + games_updated,
            "existing_games": existing_games_count,
            "fetch_method": fetch_method,
            "fetch_value": fetch_value
        }
        
    except ChessComAPIError as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch games: {str(e)}")


@router.get("/{user_id}", response_model=List[GameResponse])
async def get_user_games(
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    time_class: Optional[str] = None,
    analyzed_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get games for a user."""
    
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Build query
    query = db.query(Game).filter(Game.user_id == user_id)
    
    if time_class:
        query = query.filter(Game.time_class == time_class)
    
    if analyzed_only:
        query = query.filter(Game.is_analyzed == True)
    
    # Order by most recent first
    games = query.order_by(Game.end_time.desc()).offset(skip).limit(limit).all()
    
    return games


@router.get("/{user_id}/recent", response_model=List[GameResponse])
async def get_recent_games(
    user_id: int,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get recent games for a user."""
    
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Calculate cutoff date
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Get recent games
    games = db.query(Game).filter(
        Game.user_id == user_id,
        Game.end_time >= cutoff_date
    ).order_by(Game.end_time.desc()).all()
    
    return games


@router.get("/game/{game_id}", response_model=GameResponse)
async def get_game(game_id: int, db: Session = Depends(get_db)):
    """Get a specific game by ID."""
    
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    return game


@router.get("/{user_id}/stats")
async def get_user_game_stats(user_id: int, db: Session = Depends(get_db)):
    """Get game statistics for a user."""
    
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get all games for user
    games = db.query(Game).filter(Game.user_id == user_id).all()
    
    if not games:
        return {"total_games": 0}
    
    # Calculate statistics
    total_games = len(games)
    analyzed_games = len([g for g in games if g.is_analyzed])
    
    # Count by time class
    time_class_counts = {}
    wins = 0
    draws = 0
    losses = 0
    
    for game in games:
        # Time class stats
        tc = game.time_class or "unknown"
        time_class_counts[tc] = time_class_counts.get(tc, 0) + 1
        
        # Result stats
        user_color = "white" if game.white_username.lower() == user.chesscom_username else "black"
        user_result = game.white_result if user_color == "white" else game.black_result
        
        if user_result == "win":
            wins += 1
        elif user_result in ["checkmated", "timeout", "resigned", "abandoned"]:
            losses += 1
        else:
            draws += 1
    
    return {
        "total_games": total_games,
        "analyzed_games": analyzed_games,
        "analysis_percentage": (analyzed_games / total_games * 100) if total_games > 0 else 0,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "win_percentage": (wins / total_games * 100) if total_games > 0 else 0,
        "time_class_breakdown": time_class_counts,
        "most_recent_game": max(games, key=lambda g: g.end_time or datetime.min).end_time if games else None
    }


@router.delete("/{user_id}/games")
async def delete_user_games(
    user_id: int, 
    older_than_days: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Delete games for a user. Optionally only delete games older than specified days."""
    
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Build delete query
    query = db.query(Game).filter(Game.user_id == user_id)
    
    if older_than_days:
        cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
        query = query.filter(Game.end_time < cutoff_date)
    
    # Count games to be deleted
    games_to_delete = query.count()
    
    # Delete games
    query.delete()
    db.commit()
    
    return {
        "message": f"Deleted {games_to_delete} games",
        "games_deleted": games_to_delete
    }
