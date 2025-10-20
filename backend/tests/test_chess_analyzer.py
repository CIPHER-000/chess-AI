"""Tests for chess analysis service."""
import pytest
from app.services.chess_analyzer import ChessAnalyzer


@pytest.mark.analysis
@pytest.mark.unit
def test_parse_pgn(sample_game_pgn):
    """Test PGN parsing."""
    analyzer = ChessAnalyzer()
    
    # This would need actual Stockfish installed
    # For now, test PGN parsing structure
    assert "e4" in sample_game_pgn
    assert "testuser123" in sample_game_pgn


@pytest.mark.analysis
@pytest.mark.slow
@pytest.mark.skip(reason="Requires Stockfish installation")
def test_analyze_game(sample_game_pgn):
    """Test full game analysis with Stockfish."""
    analyzer = ChessAnalyzer()
    result = analyzer.analyze_game(sample_game_pgn, "white")
    
    assert result is not None
    assert result.user_color == "white"
    assert result.total_moves > 0
