# ♟️ **Chess Game Analysis - Official Implementation Plan**

**Date**: October 23, 2025  
**Based on**: Official documentation research  
**Status**: Ready for implementation

---

## 📚 **Research Summary**

### **1. Chess.com API** ✅
**Source**: https://www.chess.com/news/view/published-data-api

**Key Findings**:
- ✅ Chess.com API is **READ-ONLY**
- ✅ Provides: Player profiles, game data (PGN format), stats
- ❌ **Does NOT provide game analysis** - no engine evaluations
- ✅ Rate limit: ~100 requests/minute
- ✅ Game data includes: PGN, FEN, moves, timestamps, results

**Conclusion**: We must **analyze games locally using Stockfish**.

---

### **2. Python-Chess Library** ✅
**Source**: https://python-chess.readthedocs.io/en/latest/engine.html

**Key Findings**:
- ✅ **python-chess 1.11.2** - Latest stable version
- ✅ Supports both **UCI (Stockfish)** and **XBoard** engines
- ✅ Two patterns available:
  - **AsyncEngine** - For async/await (recommended)
  - **SimpleEngine** - Synchronous wrapper (easier)
  
**Official Analysis Pattern**:
```python
import chess
import chess.engine

# Modern async pattern (python-chess 1.11.2)
async def analyze_game(pgn_text: str):
    engine = await chess.engine.popen_uci("/usr/games/stockfish")
    board = chess.Board()
    
    # Parse PGN and analyze each position
    game = chess.pgn.read_game(io.StringIO(pgn_text))
    
    analyses = []
    for move in game.mainline_moves():
        board.push(move)
        
        # Analyze position
        info = await engine.analyse(
            board, 
            chess.engine.Limit(time=1.0, depth=15)
        )
        
        analyses.append({
            "fen": board.fen(),
            "score": info.get("score"),
            "best_move": info.get("pv")[0] if "pv" in info else None,
        })
    
    await engine.quit()
    return analyses
```

**Synchronous pattern** (if needed):
```python
from chess.engine import SimpleEngine

engine = SimpleEngine.popen_uci("/usr/games/stockfish")
info = engine.analyse(board, chess.engine.Limit(time=1.0))
engine.quit()
```

---

### **3. FastAPI Background Tasks** ✅
**Source**: https://fastapi.tiangolo.com/tutorial/background-tasks/

**Key Findings**:
- ✅ **BackgroundTasks** - Built-in FastAPI feature
- ✅ Good for: Simple tasks, quick operations, email notifications
- ⚠️ **NOT recommended for heavy computations** (like chess analysis)

**FastAPI Official Caveat**:
> *"If you need to perform **heavy background computation** and you don't necessarily need it to be run by the same process, you might benefit from using other bigger tools like **Celery**."*

**Recommendation**: Use **Celery for chess analysis** (CPU-intensive).

---

### **4. Celery + FastAPI** ⚠️
**Source**: https://docs.celeryq.dev

**Key Findings**:
- ✅ Celery is the **standard** for heavy background jobs
- ✅ Runs in separate worker processes
- ✅ Supports: Job queues, retries, scheduling, monitoring
- ⚠️ **More complex setup**: Requires Redis/RabbitMQ
- ✅ Already have Redis running in Docker!

---

## 🎯 **Recommended Approach**

### **Option 1: Simplified (FastAPI BackgroundTasks)** - Quick Fix ⚡
**For immediate fix** (get analysis working now):

**Pros**:
- ✅ Simple to implement
- ✅ No additional setup needed
- ✅ Works for limited concurrent users
- ✅ User gets immediate feedback

**Cons**:
- ❌ Blocks API worker during analysis
- ❌ Not scalable for multiple users
- ❌ Long analysis = slow response

**Implementation**:
```python
@router.post("/{user_id}/analyze")
async def analyze_user_games(
    user_id: int,
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Queue analysis as background task
    background_tasks.add_task(analyze_games_task, user_id, game_ids, db)
    
    return {
        "message": "Analysis started",
        "games_queued": len(game_ids)
    }
```

---

### **Option 2: Production-Ready (Celery)** - Best Practice ⭐
**For scalable production deployment**:

**Pros**:
- ✅ Handles heavy computation properly
- ✅ Scalable across multiple workers
- ✅ Supports retries and error handling
- ✅ Can monitor job progress
- ✅ Production-grade solution

**Cons**:
- ⚠️ More complex setup
- ⚠️ Requires worker management

**Implementation**:
```python
# tasks.py
from celery import Celery
from chess_analysis import analyze_game_with_stockfish

celery_app = Celery('chess_insight', broker='redis://redis:6379/0')

@celery_app.task
def analyze_game_task(game_id: int):
    # Heavy computation here
    result = analyze_game_with_stockfish(game_id)
    return result

# api endpoint
@router.post("/{user_id}/analyze")
async def analyze_user_games(...):
    # Queue Celery task
    for game_id in game_ids:
        analyze_game_task.delay(game_id)
    
    return {"message": "Analysis queued", "games_queued": len(game_ids)}
```

---

## ✅ **My Recommendation**

**Start with Option 1 (FastAPI BackgroundTasks)** then migrate to Option 2:

### **Phase 1: Quick Fix (Now)** 
- ✅ Use FastAPI BackgroundTasks
- ✅ Get analysis working immediately
- ✅ Good for single-user testing
- ✅ Simple implementation

### **Phase 2: Production (Later)**
- ✅ Migrate to Celery when scaling
- ✅ Add job progress tracking
- ✅ Add retry logic
- ✅ Add monitoring

---

## 🔧 **Implementation Details**

### **1. Chess Analysis Service** (New)
```python
# backend/app/services/chess_analysis.py

import chess
import chess.engine
import chess.pgn
import io
from typing import Dict, List, Optional
from loguru import logger

class ChessAnalysisService:
    """Service for analyzing chess games using Stockfish."""
    
    def __init__(self, stockfish_path: str = "/usr/games/stockfish"):
        self.stockfish_path = stockfish_path
    
    async def analyze_game(
        self, 
        pgn_text: str,
        depth: int = 15,
        time_limit: float = 1.0
    ) -> Dict:
        """
        Analyze a chess game and return detailed insights.
        
        Args:
            pgn_text: PGN string of the game
            depth: Stockfish search depth
            time_limit: Time limit per position in seconds
        
        Returns:
            Dictionary with analysis results including:
            - accuracy_percentage
            - average_centipawn_loss
            - move_classifications (brilliant, good, inaccuracy, mistake, blunder)
            - best_moves per position
            - critical_moments
        """
        try:
            # Initialize engine
            engine = await chess.engine.popen_uci(self.stockfish_path)
            
            # Parse PGN
            game = chess.pgn.read_game(io.StringIO(pgn_text))
            if not game:
                raise ValueError("Invalid PGN")
            
            board = game.board()
            
            # Analyze each position
            move_data = []
            total_centipawn_loss = 0
            move_count = 0
            
            for node in game.mainline():
                move = node.move
                
                # Get position BEFORE move
                position_before = board.copy()
                
                # Analyze best move in current position
                info_before = await engine.analyse(
                    position_before,
                    chess.engine.Limit(depth=depth, time=time_limit)
                )
                
                # Make the played move
                board.push(move)
                
                # Analyze position AFTER move
                info_after = await engine.analyse(
                    board,
                    chess.engine.Limit(depth=depth, time=time_limit)
                )
                
                # Calculate centipawn loss
                score_before = info_before.get("score")
                score_after = info_after.get("score")
                
                if score_before and score_after:
                    # Convert scores to centipawns
                    cp_before = self._score_to_centipawns(score_before, position_before.turn)
                    cp_after = self._score_to_centipawns(score_after, board.turn)
                    
                    # Centipawn loss (from player's perspective)
                    cp_loss = max(0, cp_before - cp_after)
                    total_centipawn_loss += cp_loss
                    move_count += 1
                    
                    # Classify move
                    classification = self._classify_move(cp_loss)
                    
                    move_data.append({
                        "move": move.uci(),
                        "move_san": board.san(move),
                        "ply": board.ply(),
                        "centipawn_loss": cp_loss,
                        "classification": classification,
                        "best_move": info_before.get("pv")[0].uci() if info_before.get("pv") else None,
                        "evaluation": cp_after,
                    })
            
            # Close engine
            await engine.quit()
            
            # Calculate metrics
            average_cp_loss = total_centipawn_loss / move_count if move_count > 0 else 0
            accuracy_percentage = max(0, 100 - (average_cp_loss / 10))  # Rough formula
            
            # Count move classifications
            move_classifications = {
                "brilliant": sum(1 for m in move_data if m["classification"] == "brilliant"),
                "great": sum(1 for m in move_data if m["classification"] == "great"),
                "best": sum(1 for m in move_data if m["classification"] == "best"),
                "excellent": sum(1 for m in move_data if m["classification"] == "excellent"),
                "good": sum(1 for m in move_data if m["classification"] == "good"),
                "inaccuracy": sum(1 for m in move_data if m["classification"] == "inaccuracy"),
                "mistake": sum(1 for m in move_data if m["classification"] == "mistake"),
                "blunder": sum(1 for m in move_data if m["classification"] == "blunder"),
            }
            
            return {
                "accuracy_percentage": round(accuracy_percentage, 2),
                "average_centipawn_loss": round(average_cp_loss, 2),
                "move_classifications": move_classifications,
                "moves": move_data,
                "total_moves": move_count,
            }
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise
    
    def _score_to_centipawns(self, score, turn: bool) -> float:
        """Convert chess.engine.Score to centipawns from player's perspective."""
        if score.is_mate():
            # Mate score: very high/low value
            mate_in = score.relative.mate()
            return 10000 if mate_in > 0 else -10000
        else:
            # Centipawn score
            cp = score.relative.score()
            return cp if turn == chess.WHITE else -cp
    
    def _classify_move(self, centipawn_loss: float) -> str:
        """Classify move based on centipawn loss."""
        if centipawn_loss <= 10:
            return "best"
        elif centipawn_loss <= 25:
            return "excellent"
        elif centipawn_loss <= 50:
            return "good"
        elif centipawn_loss <= 100:
            return "inaccuracy"
        elif centipawn_loss <= 300:
            return "mistake"
        else:
            return "blunder"
```

---

### **2. Background Task Handler** (Phase 1)
```python
# backend/app/api/analysis.py

from fastapi import BackgroundTasks
from ..services.chess_analysis import ChessAnalysisService
from ..core.config import settings

chess_analyzer = ChessAnalysisService(settings.STOCKFISH_PATH)

async def analyze_games_task(
    user_id: int, 
    game_ids: List[int],
    db_session_factory
):
    """Background task to analyze games."""
    db = db_session_factory()
    
    try:
        for game_id in game_ids:
            game = db.query(Game).filter(Game.id == game_id).first()
            if not game or not game.pgn:
                continue
            
            # Run analysis
            analysis_result = await chess_analyzer.analyze_game(game.pgn)
            
            # Save to database
            analysis = Analysis(
                game_id=game.id,
                user_id=user_id,
                accuracy_percentage=analysis_result["accuracy_percentage"],
                average_centipawn_loss=analysis_result["average_centipawn_loss"],
                move_data=analysis_result["moves"],
                **analysis_result["move_classifications"]
            )
            
            db.add(analysis)
            game.is_analyzed = True
        
        db.commit()
        logger.info(f"Analyzed {len(game_ids)} games for user {user_id}")
        
    except Exception as e:
        logger.error(f"Analysis task failed: {e}")
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
    """Analyze games for a user (Phase 1: BackgroundTasks)."""
    
    # Get games to analyze
    games_to_analyze = get_games_for_analysis(user_id, request, db)
    
    if not games_to_analyze:
        return {"message": "No games to analyze", "games_queued": 0}
    
    # Queue background task
    from ..core.database import SessionLocal
    background_tasks.add_task(
        analyze_games_task,
        user_id,
        [g.id for g in games_to_analyze],
        SessionLocal
    )
    
    return {
        "message": "Analysis started",
        "games_queued": len(games_to_analyze)
    }
```

---

## 📊 **Frontend Updates Needed**

1. **Add polling** to check analysis status
2. **Show progress indicator** while analyzing
3. **Refresh dashboard** when analysis completes
4. **Toast notification** when done

---

## 🧪 **Testing Plan**

1. ✅ Test Stockfish is installed in Docker
2. ✅ Test single game analysis
3. ✅ Test multiple games (batch)
4. ✅ Test error handling (invalid PGN)
5. ✅ Test analysis results storage
6. ✅ Test frontend updates after completion

---

## 🚀 **Next Steps**

1. ✅ Implement `ChessAnalysisService`
2. ✅ Update analysis endpoint with BackgroundTasks
3. ✅ Test with your 10 games
4. ✅ Add frontend polling
5. ✅ Verify results on dashboard
6. 🔄 (Later) Migrate to Celery for scaling

---

**Ready to implement?** This is based on official documentation and best practices! 🎯
