"""
Chess game analysis service using Stockfish engine.
Based on python-chess official documentation.
"""

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
            depth: Stockfish search depth (default: 15)
            time_limit: Time limit per position in seconds (default: 1.0)
        
        Returns:
            Dictionary with analysis results including:
            - accuracy_percentage: Overall accuracy (0-100)
            - average_centipawn_loss: Average centipawn loss per move
            - move_classifications: Count of each move type
            - moves: Detailed analysis per move
            - total_moves: Total number of moves analyzed
        """
        try:
            logger.info(f"Starting game analysis with depth={depth}, time={time_limit}")
            
            # Initialize Stockfish engine
            engine = await chess.engine.popen_uci(self.stockfish_path)
            
            # Parse PGN
            game = chess.pgn.read_game(io.StringIO(pgn_text))
            if not game:
                raise ValueError("Invalid PGN - could not parse game")
            
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
                    # Convert scores to centipawns from player's perspective
                    cp_before = self._score_to_centipawns(score_before, position_before.turn)
                    cp_after = self._score_to_centipawns(score_after, board.turn)
                    
                    # Centipawn loss (always positive - how much worse the position got)
                    cp_loss = max(0, cp_before - cp_after)
                    total_centipawn_loss += cp_loss
                    move_count += 1
                    
                    # Classify move based on centipawn loss
                    classification = self._classify_move(cp_loss)
                    
                    # Get best move suggestion
                    best_move_uci = None
                    if info_before.get("pv"):
                        best_move_uci = info_before["pv"][0].uci()
                    
                    move_data.append({
                        "move": move.uci(),
                        "move_san": position_before.san(move),
                        "ply": board.ply(),
                        "centipawn_loss": round(cp_loss, 2),
                        "classification": classification,
                        "best_move": best_move_uci,
                        "evaluation": round(cp_after, 2),
                    })
            
            # Close engine
            await engine.quit()
            logger.info(f"Analysis complete: {move_count} moves analyzed")
            
            # Calculate overall metrics
            average_cp_loss = total_centipawn_loss / move_count if move_count > 0 else 0
            
            # Accuracy formula: Higher CP loss = lower accuracy
            # Perfect play (0 CP loss) = 100%, 100 CP loss = ~0%
            accuracy_percentage = max(0, min(100, 100 - (average_cp_loss / 10)))
            
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
            
        except FileNotFoundError:
            logger.error(f"Stockfish not found at {self.stockfish_path}")
            raise ValueError(f"Stockfish engine not found at {self.stockfish_path}")
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise
    
    def _score_to_centipawns(self, score: chess.engine.Score, turn: bool) -> float:
        """
        Convert chess.engine.Score to centipawns from current player's perspective.
        
        Args:
            score: Score object from engine analysis
            turn: Current turn (chess.WHITE or chess.BLACK)
        
        Returns:
            Centipawn value (positive = advantage, negative = disadvantage)
        """
        if score.is_mate():
            # Mate score: assign very high/low value
            mate_in = score.relative.mate()
            return 10000 if mate_in > 0 else -10000
        else:
            # Regular centipawn score
            cp = score.relative.score()
            # Ensure score is from current player's perspective
            return cp if cp is not None else 0
    
    def _classify_move(self, centipawn_loss: float) -> str:
        """
        Classify move quality based on centipawn loss.
        Based on common chess analysis standards.
        
        Args:
            centipawn_loss: How many centipawns were lost by this move
        
        Returns:
            Move classification string
        """
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
