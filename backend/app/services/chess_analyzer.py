import io
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

import chess
import chess.pgn
import chess.engine
from stockfish import Stockfish
from loguru import logger

from ..core.config import settings


@dataclass
class MoveEvaluation:
    """Represents the evaluation of a single move."""
    move_number: int
    move: str
    position_fen: str
    evaluation: float  # In centipawns
    best_move: Optional[str]
    mate_in: Optional[int]
    classification: str  # brilliant, great, best, excellent, good, inaccuracy, mistake, blunder
    evaluation_change: Optional[float]  # Change from previous position


@dataclass
class GamePhase:
    """Represents statistics for a game phase."""
    name: str
    move_start: int
    move_end: int
    acpl: float
    moves: List[MoveEvaluation]
    key_positions: List[MoveEvaluation]


@dataclass
class AnalysisResult:
    """Complete analysis result for a game."""
    game_id: str
    user_color: str
    total_moves: int
    
    # Overall metrics
    user_acpl: float
    opponent_acpl: float
    
    # Move classifications
    brilliant_moves: int = 0
    great_moves: int = 0
    best_moves: int = 0
    excellent_moves: int = 0
    good_moves: int = 0
    inaccuracies: int = 0
    mistakes: int = 0
    blunders: int = 0
    
    # Game phases
    opening_phase: Optional[GamePhase] = None
    middlegame_phase: Optional[GamePhase] = None
    endgame_phase: Optional[GamePhase] = None
    
    # Opening information
    opening_name: Optional[str] = None
    opening_eco: Optional[str] = None
    opening_moves: int = 0
    
    # Detailed evaluations
    evaluations: List[MoveEvaluation] = None
    critical_positions: List[MoveEvaluation] = None
    blunder_moves: List[MoveEvaluation] = None
    
    # Metadata
    analysis_time: float = 0.0
    engine_version: str = ""


class ChessAnalyzer:
    """Chess game analyzer using Stockfish engine."""
    
    def __init__(self):
        self.stockfish_path = settings.STOCKFISH_PATH
        self.analysis_depth = settings.STOCKFISH_DEPTH
        self.analysis_time = settings.STOCKFISH_TIME
        
        # Move classification thresholds (in centipawns)
        self.thresholds = {
            'brilliant': -50,    # Sacrifice or spectacular move
            'great': -25,        # Very good move
            'best': 0,           # Engine's top choice
            'excellent': 25,     # Almost best
            'good': 50,          # Reasonable move
            'inaccuracy': 100,   # Minor mistake
            'mistake': 200,      # Significant error
            'blunder': 300       # Major blunder
        }
    
    def _get_stockfish_engine(self) -> Stockfish:
        """Initialize Stockfish engine."""
        try:
            stockfish = Stockfish(
                path=self.stockfish_path,
                depth=self.analysis_depth,
                parameters={
                    "Hash": 512,
                    "Threads": 2,
                    "Minimum Thinking Time": int(self.analysis_time * 1000),
                }
            )
            return stockfish
        except Exception as e:
            logger.error(f"Failed to initialize Stockfish: {e}")
            raise RuntimeError(f"Stockfish initialization failed: {e}")
    
    def parse_pgn(self, pgn_string: str) -> Optional[chess.pgn.Game]:
        """Parse PGN string into chess.pgn.Game object."""
        try:
            pgn_io = io.StringIO(pgn_string)
            game = chess.pgn.read_game(pgn_io)
            return game
        except Exception as e:
            logger.error(f"Failed to parse PGN: {e}")
            return None
    
    def extract_opening_info(self, game: chess.pgn.Game) -> Tuple[Optional[str], Optional[str], int]:
        """Extract opening name, ECO code, and number of opening moves."""
        
        # Try to get opening info from PGN headers
        opening_name = game.headers.get("Opening")
        eco_code = game.headers.get("ECO")
        
        # Count opening moves (typically first 10-15 moves)
        opening_moves = 0
        node = game
        while node.variations and opening_moves < 20:
            node = node.variations[0]
            opening_moves += 1
            
            # Simple heuristic: opening ends when pieces start getting traded
            # or when we reach move 15
            if opening_moves >= 10:
                board = node.board()
                if len(board.piece_map()) < 30:  # Pieces have been traded
                    break
        
        return opening_name, eco_code, min(opening_moves, 15)
    
    def classify_move(self, evaluation_change: float, is_best_move: bool = False) -> str:
        """Classify a move based on evaluation change."""
        
        if is_best_move or evaluation_change >= self.thresholds['best']:
            return 'best'
        elif evaluation_change >= self.thresholds['excellent']:
            return 'excellent'
        elif evaluation_change >= self.thresholds['good']:
            return 'good'
        elif evaluation_change >= self.thresholds['inaccuracy']:
            return 'inaccuracy'
        elif evaluation_change >= self.thresholds['mistake']:
            return 'mistake'
        else:
            return 'blunder'
    
    def determine_game_phases(self, total_moves: int, evaluations: List[MoveEvaluation]) -> Tuple[GamePhase, GamePhase, GamePhase]:
        """Determine game phase boundaries and calculate phase statistics."""
        
        # Simple heuristic for game phases
        opening_end = min(20, total_moves // 3)
        endgame_start = max(opening_end + 10, total_moves * 2 // 3)
        
        def create_phase(name: str, start: int, end: int) -> GamePhase:
            phase_moves = [ev for ev in evaluations if start <= ev.move_number < end]
            acpl = sum(abs(ev.evaluation_change or 0) for ev in phase_moves) / max(len(phase_moves), 1)
            
            # Identify key positions (large evaluation swings)
            key_positions = [ev for ev in phase_moves if abs(ev.evaluation_change or 0) > 100]
            
            return GamePhase(
                name=name,
                move_start=start,
                move_end=end,
                acpl=acpl,
                moves=phase_moves,
                key_positions=key_positions
            )
        
        opening = create_phase("opening", 1, opening_end)
        middlegame = create_phase("middlegame", opening_end, endgame_start)
        endgame = create_phase("endgame", endgame_start, total_moves + 1)
        
        return opening, middlegame, endgame
    
    def analyze_game(self, pgn_string: str, user_color: str, game_id: str = "") -> Optional[AnalysisResult]:
        """Analyze a complete chess game."""
        
        start_time = datetime.now()
        
        # Parse PGN
        game = self.parse_pgn(pgn_string)
        if not game:
            logger.error("Failed to parse PGN")
            return None
        
        # Initialize Stockfish
        try:
            stockfish = self._get_stockfish_engine()
        except RuntimeError as e:
            logger.error(f"Stockfish initialization failed: {e}")
            return None
        
        # Extract opening information
        opening_name, opening_eco, opening_moves = self.extract_opening_info(game)
        
        # Analyze each position
        evaluations = []
        board = game.board()
        stockfish.set_fen_position(board.fen())
        
        # Get initial position evaluation
        prev_eval = stockfish.get_evaluation()
        prev_eval_cp = prev_eval.get('value', 0) if prev_eval.get('type') == 'cp' else 0
        
        move_number = 0
        
        for node in game.mainline():
            move_number += 1
            move = node.move
            board.push(move)
            
            # Set position in Stockfish
            stockfish.set_fen_position(board.fen())
            
            # Get current evaluation
            current_eval = stockfish.get_evaluation()
            current_eval_cp = current_eval.get('value', 0) if current_eval.get('type') == 'cp' else 0
            
            # Adjust evaluation for player perspective
            if board.turn == chess.BLACK:  # After move, it's the other player's turn
                current_eval_cp = -current_eval_cp
                prev_eval_cp = -prev_eval_cp
            
            # Calculate evaluation change
            eval_change = current_eval_cp - prev_eval_cp
            
            # For the player who just moved, a negative change is bad
            if (user_color == 'white' and move_number % 2 == 1) or \
               (user_color == 'black' and move_number % 2 == 0):
                eval_change = -eval_change
            
            # Get best move
            best_move_info = stockfish.get_best_move()
            best_move = best_move_info if best_move_info else None
            
            # Classify move
            is_best = str(move) == best_move if best_move else False
            classification = self.classify_move(eval_change, is_best)
            
            # Create move evaluation
            move_eval = MoveEvaluation(
                move_number=move_number,
                move=str(move),
                position_fen=board.fen(),
                evaluation=current_eval_cp,
                best_move=best_move,
                mate_in=current_eval.get('value') if current_eval.get('type') == 'mate' else None,
                classification=classification,
                evaluation_change=eval_change
            )
            
            evaluations.append(move_eval)
            prev_eval_cp = current_eval_cp
        
        # Filter evaluations for user's moves only
        if user_color == 'white':
            user_moves = [ev for ev in evaluations if ev.move_number % 2 == 1]
        else:
            user_moves = [ev for ev in evaluations if ev.move_number % 2 == 0]
        
        # Calculate statistics
        user_acpl = sum(abs(ev.evaluation_change or 0) for ev in user_moves) / max(len(user_moves), 1)
        
        opponent_moves = [ev for ev in evaluations if ev not in user_moves]
        opponent_acpl = sum(abs(ev.evaluation_change or 0) for ev in opponent_moves) / max(len(opponent_moves), 1)
        
        # Count move classifications for user
        move_counts = {
            'brilliant_moves': len([m for m in user_moves if m.classification == 'brilliant']),
            'great_moves': len([m for m in user_moves if m.classification == 'great']),
            'best_moves': len([m for m in user_moves if m.classification == 'best']),
            'excellent_moves': len([m for m in user_moves if m.classification == 'excellent']),
            'good_moves': len([m for m in user_moves if m.classification == 'good']),
            'inaccuracies': len([m for m in user_moves if m.classification == 'inaccuracy']),
            'mistakes': len([m for m in user_moves if m.classification == 'mistake']),
            'blunders': len([m for m in user_moves if m.classification == 'blunder']),
        }
        
        # Determine game phases
        opening, middlegame, endgame = self.determine_game_phases(len(evaluations), user_moves)
        
        # Find critical positions and blunders
        critical_positions = [ev for ev in user_moves if abs(ev.evaluation_change or 0) > 150]
        blunder_moves = [ev for ev in user_moves if ev.classification == 'blunder']
        
        # Calculate analysis time
        analysis_duration = (datetime.now() - start_time).total_seconds()
        
        # Create result
        result = AnalysisResult(
            game_id=game_id,
            user_color=user_color,
            total_moves=len(user_moves),
            user_acpl=user_acpl,
            opponent_acpl=opponent_acpl,
            opening_name=opening_name,
            opening_eco=opening_eco,
            opening_moves=opening_moves,
            evaluations=user_moves,
            critical_positions=critical_positions,
            blunder_moves=blunder_moves,
            opening_phase=opening,
            middlegame_phase=middlegame,
            endgame_phase=endgame,
            analysis_time=analysis_duration,
            engine_version=f"Stockfish {stockfish.get_stockfish_major_version()}",
            **move_counts
        )
        
        logger.info(f"Analysis completed for game {game_id}: {user_acpl:.1f} ACPL, {len(blunder_moves)} blunders")
        
        return result


# Global analyzer instance
chess_analyzer = ChessAnalyzer()
