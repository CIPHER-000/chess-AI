from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..core.database import get_db
from ..models import User, Game, GameAnalysis
from ..services.chess_analyzer import chess_analyzer

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


async def analyze_game_background(game_id: int, db: Session):
    """Background task to analyze a single game."""
    
    # Get the game
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game or not game.pgn:
        return
    
    # Get user to determine color
    user = db.query(User).filter(User.id == game.user_id).first()
    if not user:
        return
    
    # Determine user's color
    user_color = "white" if game.white_username.lower() == user.chesscom_username else "black"
    
    # Run analysis
    analysis_result = chess_analyzer.analyze_game(
        game.pgn, 
        user_color, 
        str(game.id)
    )
    
    if not analysis_result:
        return
    
    # Check if analysis already exists
    existing_analysis = db.query(GameAnalysis).filter(GameAnalysis.game_id == game_id).first()
    
    if existing_analysis:
        # Update existing analysis
        for field, value in analysis_result.__dict__.items():
            if field not in ['game_id', 'evaluations', 'critical_positions', 'blunder_moves', 
                           'opening_phase', 'middlegame_phase', 'endgame_phase']:
                setattr(existing_analysis, field, value)
        
        # Update JSON fields
        existing_analysis.evaluations = [
            {
                'move_number': ev.move_number,
                'move': ev.move,
                'evaluation': ev.evaluation,
                'best_move': ev.best_move,
                'classification': ev.classification,
                'evaluation_change': ev.evaluation_change
            }
            for ev in analysis_result.evaluations or []
        ]
        
        existing_analysis.critical_positions = [
            {
                'move_number': ev.move_number,
                'move': ev.move,
                'evaluation_change': ev.evaluation_change
            }
            for ev in analysis_result.critical_positions or []
        ]
        
        existing_analysis.blunder_moves = [
            {
                'move_number': ev.move_number,
                'move': ev.move,
                'evaluation_change': ev.evaluation_change
            }
            for ev in analysis_result.blunder_moves or []
        ]
        
    else:
        # Create new analysis
        analysis = GameAnalysis(
            game_id=game_id,
            engine_version=analysis_result.engine_version,
            analysis_depth=chess_analyzer.analysis_depth,
            analysis_time=analysis_result.analysis_time,
            user_color=analysis_result.user_color,
            user_acpl=analysis_result.user_acpl,
            opponent_acpl=analysis_result.opponent_acpl,
            brilliant_moves=analysis_result.brilliant_moves,
            great_moves=analysis_result.great_moves,
            best_moves=analysis_result.best_moves,
            excellent_moves=analysis_result.excellent_moves,
            good_moves=analysis_result.good_moves,
            inaccuracies=analysis_result.inaccuracies,
            mistakes=analysis_result.mistakes,
            blunders=analysis_result.blunders,
            opening_acpl=analysis_result.opening_phase.acpl if analysis_result.opening_phase else None,
            middlegame_acpl=analysis_result.middlegame_phase.acpl if analysis_result.middlegame_phase else None,
            endgame_acpl=analysis_result.endgame_phase.acpl if analysis_result.endgame_phase else None,
            opening_name=analysis_result.opening_name,
            opening_eco=analysis_result.opening_eco,
            opening_moves=analysis_result.opening_moves,
            evaluations=[
                {
                    'move_number': ev.move_number,
                    'move': ev.move,
                    'evaluation': ev.evaluation,
                    'best_move': ev.best_move,
                    'classification': ev.classification,
                    'evaluation_change': ev.evaluation_change
                }
                for ev in analysis_result.evaluations or []
            ],
            critical_positions=[
                {
                    'move_number': ev.move_number,
                    'move': ev.move,
                    'evaluation_change': ev.evaluation_change
                }
                for ev in analysis_result.critical_positions or []
            ],
            blunder_moves=[
                {
                    'move_number': ev.move_number,
                    'move': ev.move,
                    'evaluation_change': ev.evaluation_change
                }
                for ev in analysis_result.blunder_moves or []
            ]
        )
        
        db.add(analysis)
    
    # Mark game as analyzed
    game.is_analyzed = True
    
    db.commit()


@router.post("/{user_id}/analyze")
async def analyze_user_games(
    user_id: int,
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Analyze games for a user."""
    
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
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
    
    # Queue analysis tasks
    for game in games_to_analyze:
        if game.pgn:  # Only analyze games with PGN data
            background_tasks.add_task(analyze_game_background, game.id, db)
    
    return {
        "message": f"Queued {len(games_to_analyze)} games for analysis",
        "games_queued": len(games_to_analyze)
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
        "accuracy_percentage": round(100 - (total_acpl / 10), 1) if total_acpl > 0 else 100
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
