from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..core.database import get_db, SessionLocal
from ..models import User, Game, GameAnalysis
from ..services.chess_analysis import ChessAnalysisService
from ..services.tier_service import get_tier_service
from ..core.config import settings
from loguru import logger
import asyncio

router = APIRouter()


class AnalysisResponse(BaseModel):
    id: int
    game_id: int
    engine_version: Optional[str]
    analysis_depth: Optional[int]
    analysis_time: Optional[float]
    user_color: Optional[str]
    user_acpl: Optional[float]
    opponent_acpl: Optional[float]
    brilliant_moves: int = 0
    great_moves: int = 0
    best_moves: int = 0
    excellent_moves: int = 0
    good_moves: int = 0
    inaccuracies: int = 0
    mistakes: int = 0
    blunders: int = 0
    opening_acpl: Optional[float]
    middlegame_acpl: Optional[float]
    endgame_acpl: Optional[float]
    opening_name: Optional[str]
    opening_eco: Optional[str]
    opening_moves: Optional[int]
    
    class Config:
        from_attributes = True


class AnalysisRequest(BaseModel):
    game_ids: Optional[List[int]] = None  # Specific games to analyze
    days: int = 7  # Analyze games from last N days
    time_classes: Optional[List[str]] = None  # Filter by time classes
    force_reanalysis: bool = False  # Re-analyze already analyzed games
    mode: str = "auto"  # "auto", "stockfish-only", or "ai-enhanced"


def analyze_game_background_wrapper(game_id: int, user_id: int):
    """Wrapper to run async analysis in background task."""
    asyncio.run(analyze_game_background(game_id, user_id))


async def analyze_game_background(game_id: int, user_id: int):
    """Background task to analyze a single game with Stockfish."""
    
    # Create new database session for background task
    db = SessionLocal()
    
    try:
        logger.info(f"Starting analysis for game {game_id}")
        
        # Get the game
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game or not game.pgn:
            logger.warning(f"Game {game_id} not found or has no PGN")
            return
        
        # Get user to determine color
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"User {user_id} not found")
            return
        
        # Determine user's color
        user_color = "white" if game.white_username and game.white_username.lower() == user.chesscom_username else "black"
        
        # Initialize analysis service
        analyzer = ChessAnalysisService(stockfish_path=settings.STOCKFISH_PATH)
        
        # Run analysis
        logger.info(f"Analyzing game {game_id} with Stockfish...")
        analysis_result = await analyzer.analyze_game(
            game.pgn,
            depth=settings.STOCKFISH_DEPTH,
            time_limit=settings.STOCKFISH_TIME
        )
        
        if not analysis_result:
            logger.warning(f"Analysis failed for game {game_id}")
            return
        
        # Check if analysis already exists
        existing_analysis = db.query(GameAnalysis).filter(GameAnalysis.game_id == game_id).first()
        
        if existing_analysis:
            # Update existing analysis
            existing_analysis.analysis_depth = settings.STOCKFISH_DEPTH
            existing_analysis.user_color = user_color
            existing_analysis.user_acpl = analysis_result["average_centipawn_loss"]
            existing_analysis.brilliant_moves = analysis_result["move_classifications"]["brilliant"]
            existing_analysis.great_moves = analysis_result["move_classifications"]["great"]
            existing_analysis.best_moves = analysis_result["move_classifications"]["best"]
            existing_analysis.excellent_moves = analysis_result["move_classifications"]["excellent"]
            existing_analysis.good_moves = analysis_result["move_classifications"]["good"]
            existing_analysis.inaccuracies = analysis_result["move_classifications"]["inaccuracy"]
            existing_analysis.mistakes = analysis_result["move_classifications"]["mistake"]
            existing_analysis.blunders = analysis_result["move_classifications"]["blunder"]
            existing_analysis.evaluations = analysis_result["moves"]
            
            logger.info(f"Updated existing analysis for game {game_id}")
        else:
            # Create new analysis
            analysis = GameAnalysis(
                game_id=game_id,
                engine_version="Stockfish",
                analysis_depth=settings.STOCKFISH_DEPTH,
                user_color=user_color,
                user_acpl=analysis_result["average_centipawn_loss"],
                brilliant_moves=analysis_result["move_classifications"]["brilliant"],
                great_moves=analysis_result["move_classifications"]["great"],
                best_moves=analysis_result["move_classifications"]["best"],
                excellent_moves=analysis_result["move_classifications"]["excellent"],
                good_moves=analysis_result["move_classifications"]["good"],
                inaccuracies=analysis_result["move_classifications"]["inaccuracy"],
                mistakes=analysis_result["move_classifications"]["mistake"],
                blunders=analysis_result["move_classifications"]["blunder"],
                evaluations=analysis_result["moves"]
            )
            
            db.add(analysis)
            logger.info(f"Created new analysis for game {game_id}")
        
        # Mark game as analyzed
        game.is_analyzed = True
        
        db.commit()
        logger.info(f"Successfully completed analysis for game {game_id}")
        
    except Exception as e:
        logger.error(f"Error analyzing game {game_id}: {e}")
        db.rollback()
    finally:
        db.close()


@router.post("/{user_id}/analyze")
async def analyze_user_games(
    user_id: int,
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Analyze games for a user with tier-aware logic."""
    
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check tier status
    tier_service = get_tier_service(db)
    
    # Determine analysis mode based on tier and request
    analysis_mode = request.mode
    uses_ai = False
    
    if analysis_mode == "auto":
        # Auto mode: use AI if user can, otherwise Stockfish-only
        if tier_service.can_use_ai_analysis(user):
            analysis_mode = "ai-enhanced"
            uses_ai = True
        else:
            analysis_mode = "stockfish-only"
    elif analysis_mode == "ai-enhanced":
        # Explicit AI request: check if user has access
        if not tier_service.can_use_ai_analysis(user):
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "AI analysis limit reached",
                    "message": tier_service.get_upgrade_message(user),
                    "tier": user.tier,
                    "remaining_analyses": user.remaining_ai_analyses,
                    "upgrade_required": True
                }
            )
        uses_ai = True
    
    # Build query for games to analyze
    if request.game_ids:
        # Analyze specific games
        games_query = db.query(Game).filter(
            Game.user_id == user_id,
            Game.id.in_(request.game_ids)
        )
    else:
        # Analyze recent games
        from datetime import datetime, timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=request.days)
        
        games_query = db.query(Game).filter(
            Game.user_id == user_id,
            Game.end_time >= cutoff_date
        )
        
        if request.time_classes:
            games_query = games_query.filter(Game.time_class.in_(request.time_classes))
    
    # Filter out already analyzed games if not forcing re-analysis
    if not request.force_reanalysis:
        games_query = games_query.filter(Game.is_analyzed == False)
    
    games_to_analyze = games_query.all()
    
    if not games_to_analyze:
        return {
            "message": "No games to analyze",
            "games_queued": 0
        }
    
    # Increment AI usage if using AI-enhanced mode
    if uses_ai:
        if not tier_service.increment_ai_usage(user):
            raise HTTPException(
                status_code=403,
                detail="AI analysis limit reached"
            )
    
    # Queue analysis tasks
    for game in games_to_analyze:
        if game.pgn:  # Only analyze games with PGN data
            background_tasks.add_task(analyze_game_background_wrapper, game.id, user_id)
    
    # Update user's analyzed_games count
    user.analyzed_games = db.query(Game).filter(
        Game.user_id == user_id,
        Game.is_analyzed == True
    ).count() + len(games_to_analyze)
    db.commit()
    
    return {
        "message": f"Queued {len(games_to_analyze)} games for analysis",
        "games_queued": len(games_to_analyze),
        "analysis_mode": analysis_mode,
        "uses_ai": uses_ai,
        "tier_info": {
            "tier": user.tier,
            "remaining_ai_analyses": user.remaining_ai_analyses if not user.is_pro else "unlimited"
        }
    }


@router.get("/{user_id}/analyses", response_model=List[AnalysisResponse])
async def get_user_analyses(
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get analysis results for a user's games."""
    
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get analyses for user's games
    analyses = db.query(GameAnalysis).join(Game).filter(
        Game.user_id == user_id
    ).order_by(GameAnalysis.created_at.desc()).offset(skip).limit(limit).all()
    
    return analyses


@router.get("/game/{game_id}", response_model=AnalysisResponse)
async def get_game_analysis(game_id: int, db: Session = Depends(get_db)):
    """Get analysis for a specific game."""
    
    analysis = db.query(GameAnalysis).filter(GameAnalysis.game_id == game_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis


@router.get("/{user_id}/summary")
async def get_analysis_summary(user_id: int, days: int = 7, db: Session = Depends(get_db)):
    """Get analysis summary for a user."""
    
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get recent analyses
    from datetime import datetime, timedelta
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    analyses = db.query(GameAnalysis).join(Game).filter(
        Game.user_id == user_id,
        Game.end_time >= cutoff_date,
        Game.is_analyzed == True
    ).all()
    
    if not analyses:
        return {
            "period_days": days,
            "total_games_analyzed": 0,
            "message": "No analyzed games found for this period"
        }
    
    # Calculate summary statistics
    total_games = len(analyses)
    total_acpl = sum(a.user_acpl for a in analyses if a.user_acpl) / total_games if total_games > 0 else 0
    
    # Aggregate move counts
    move_totals = {
        'brilliant_moves': sum(a.brilliant_moves for a in analyses),
        'great_moves': sum(a.great_moves for a in analyses),
        'best_moves': sum(a.best_moves for a in analyses),
        'excellent_moves': sum(a.excellent_moves for a in analyses),
        'good_moves': sum(a.good_moves for a in analyses),
        'inaccuracies': sum(a.inaccuracies for a in analyses),
        'mistakes': sum(a.mistakes for a in analyses),
        'blunders': sum(a.blunders for a in analyses),
    }
    
    # Phase performance
    opening_acpl = sum(a.opening_acpl for a in analyses if a.opening_acpl) / len([a for a in analyses if a.opening_acpl]) if any(a.opening_acpl for a in analyses) else 0
    middlegame_acpl = sum(a.middlegame_acpl for a in analyses if a.middlegame_acpl) / len([a for a in analyses if a.middlegame_acpl]) if any(a.middlegame_acpl for a in analyses) else 0
    endgame_acpl = sum(a.endgame_acpl for a in analyses if a.endgame_acpl) / len([a for a in analyses if a.endgame_acpl]) if any(a.endgame_acpl for a in analyses) else 0
    
    # Common openings
    opening_counts = {}
    for analysis in analyses:
        if analysis.opening_name:
            opening_counts[analysis.opening_name] = opening_counts.get(analysis.opening_name, 0) + 1
    
    most_played_openings = sorted(opening_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Get tier info
    tier_service = get_tier_service(db)
    tier_status = tier_service.get_tier_status(user)
    
    return {
        "period_days": days,
        "total_games_analyzed": total_games,
        "average_acpl": round(total_acpl, 1),
        "move_quality_breakdown": move_totals,
        "phase_performance": {
            "opening_acpl": round(opening_acpl, 1),
            "middlegame_acpl": round(middlegame_acpl, 1),
            "endgame_acpl": round(endgame_acpl, 1)
        },
        "most_played_openings": most_played_openings,
        "accuracy_percentage": round(max(0, min(100, 100 - (total_acpl / 10))), 1),
        "tier_status": tier_status,
        "analysis_note": "Stockfish metrics only" if not tier_status["can_use_ai"] and user.tier == "free" else "Full AI insights"
    }


@router.delete("/game/{game_id}")
async def delete_game_analysis(game_id: int, db: Session = Depends(get_db)):
    """Delete analysis for a specific game."""
    
    analysis = db.query(GameAnalysis).filter(GameAnalysis.game_id == game_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Also mark the game as not analyzed
    game = db.query(Game).filter(Game.id == game_id).first()
    if game:
        game.is_analyzed = False
    
    db.delete(analysis)
    db.commit()
    
    return {"message": "Analysis deleted successfully"}
