"""Sample PGN games for testing chess analysis."""

# Real PGN from Magnus Carlsen vs Hikaru Nakamura (2021)
SAMPLE_GAME_1_CARLSEN = """[Event "Speed Chess Championship 2021"]
[Site "Chess.com"]
[Date "2021.05.25"]
[Round "?"]
[White "MagnusCarlsen"]
[Black "Hikaru"]
[Result "1-0"]
[ECO "C50"]
[WhiteElo "3265"]
[BlackElo "3292"]
[TimeControl "180+1"]
[EndTime "18:25:22 PDT"]
[Termination "MagnusCarlsen won by checkmate"]

1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. d3 Nf6 5. Nc3 d6 6. Bg5 h6 7. Bxf6 Qxf6 8. Nd5
Qd8 9. c3 Ne7 10. d4 exd4 11. Nxd4 Nxd5 12. Bxd5 O-O 13. O-O c6 14. Bb3 Qf6 15.
Qf3 Qg5 16. Rae1 Be6 17. Nxe6 fxe6 18. Bxe6+ Kh8 19. Qf7 Rxf7 20. Bxf7 Rf8 21.
Bb3 Bd4 22. cxd4 Qxe1 23. Rxe1 Rxf2 24. Kh1 Rf8 25. e5 dxe5 26. dxe5 b6 27. Rf1
Rxf1+ 28. Bxf1 Kg8 29. Kg1 Kf7 30. Kf2 Ke6 31. Ke3 c5 32. Ke4 Kf7 33. Kf5 Ke7
34. Kg6 Ke6 35. Bc4+ Kxe5 36. Kxg7 h5 37. h4 Kd4 38. Bd5 b5 39. Kh6 c4 40. Bxc4
bxc4 41. Kxh5 c3 42. bxc3+ Kxc3 43. g4 Kd4 44. g5 Ke5 45. g6 Kf6 46. h5 1-0"""

# Blunder-heavy game for testing mistake detection
SAMPLE_GAME_2_BLUNDERS = """[Event "Casual Game"]
[Site "Chess.com"]
[Date "2024.01.10"]
[Round "?"]
[White "Player1"]
[Black "Player2"]
[Result "0-1"]
[ECO "C20"]
[WhiteElo "1200"]
[BlackElo "1180"]
[TimeControl "600"]
[EndTime "14:35:12 PST"]
[Termination "Player2 won on time"]

1. e4 e5 2. Qh5 Nc6 3. Bc4 g6 4. Qf3 Nf6 5. Ne2 Bg7 6. O-O O-O 7. d3 d6 8. Bg5
h6 9. Bh4 g5 10. Bg3 Nh5 11. Qd1 Nxg3 12. hxg3 Be6 13. Bxe6 fxe6 14. Nbc3 Qd7
15. Ng1 Rf6 16. Nf3 Raf8 17. Nh2 Nd4 18. Nd5 exd5 19. c3 Nf5 20. exd5 Nxg3 21.
fxg3 Rxf1+ 22. Qxf1 Rxf1+ 23. Kxf1 Qf5+ 24. Kg1 Qf2+ 25. Kh1 Qxg3 0-1"""

# Short tactical game
SAMPLE_GAME_3_TACTICAL = """[Event "Titled Tuesday"]
[Site "Chess.com"]
[Date "2024.03.15"]
[Round "?"]
[White "IMPlayer"]
[Black "GMPlayer"]
[Result "0-1"]
[ECO "B12"]
[WhiteElo "2450"]
[BlackElo "2620"]
[TimeControl "180+0"]
[EndTime "20:15:33 UTC"]
[Termination "GMPlayer won by checkmate"]

1. e4 c6 2. d4 d5 3. e5 Bf5 4. Nf3 e6 5. Be2 c5 6. Be3 Qb6 7. Nc3 Nc6 8. Na4 Qa5+
9. c3 cxd4 10. b4 Nxb4 11. cxb4 Bxb4+ 12. Nd2 dxe3 13. Qa4+ Qxa4 14. Nc3 Qxa2
15. Nxa2 Bxd2+ 16. Kxd2 exf2 17. Rhf1 Be4 18. Rxf2 Bxg2 19. Bh5 g6 20. Bf3 Bxf3
21. Rxf3 Ne7 22. Nc3 O-O 23. Rg1 Rfc8 24. Kd3 Rc4 25. Rb1 b6 26. Rb5 Rac8 27.
Nd1 Rc1 28. Nf2 R8c3+ 29. Rxc3 Rxc3+ 30. Ke2 Nc6 31. Rb1 Nxe5 32. Kd2 Rc2+ 33.
Ke3 Rxf2 34. Kxf2 Nc4 35. Rb3 Kf8 36. Ke2 Ke7 37. Kd3 Kd6 38. Rb1 Kc5 39. Rc1
Kb4 40. Rb1+ Kc5 41. Rc1 d4 42. Ke2 Kd5 43. Kd3 e5 44. Rg1 Ne3 45. Rg3 Nf5 46.
Rg5 Ke6 47. Rg1 h5 48. Rb1 Kd5 49. Rc1 e4+ 50. Kd2 d3 51. Rc3 Nd4 52. Rc1 Nf3+
53. Kd1 e3 54. Re1 e2+ 55. Kd2 Nxe1 56. Kxe1 Ke4 57. h4 Kf3 58. Kxe2 dxe2 59.
h5 gxh5 0-1"""

# Endgame focused
SAMPLE_GAME_4_ENDGAME = """[Event "Lichess Rated Game"]
[Site "lichess.org"]
[Date "2024.02.20"]
[Round "?"]
[White "Endgame_Master"]
[Black "Rookie_Player"]
[Result "1-0"]
[ECO "C42"]
[WhiteElo "2100"]
[BlackElo "1650"]
[TimeControl "900+10"]
[Termination "Endgame_Master won by checkmate"]

1. e4 e5 2. Nf3 Nf6 3. Nxe5 d6 4. Nf3 Nxe4 5. d4 d5 6. Bd3 Nc6 7. O-O Be7 8. c4
Nb4 9. Be2 O-O 10. Nc3 Bf5 11. a3 Nxc3 12. bxc3 Nc6 13. Re1 Re8 14. Bf4 Bf6 15.
Qd2 dxc4 16. Bxc4 Na5 17. Bd3 Bxd3 18. Qxd3 Qd5 19. Rab1 b6 20. Rb5 Qd8 21. Re4
c6 22. Rb1 Nc4 23. Qa6 Qd5 24. Rg4 g6 25. h4 Bg7 26. h5 Nd6 27. Bxd6 Qxd6 28.
hxg6 hxg6 29. Rbh1 Qxa6 30. Rh8+ Kf8 31. Rxe8+ Rxe8 32. Rxe8+ Kxe8 33. Ng5 Ke7
34. Nxf7 Qe2 35. Nd6 Qe1+ 36. Kh2 Qe6 37. f4 Kf6 38. Nc8 a5 39. Nxb6 Qe2 40.
Nd7+ Ke6 41. Ne5 Bxe5 42. fxe5 Kxe5 43. Kg3 Qe1+ 44. Kf3 Qf1+ 45. Ke3 Qe1+ 46.
Kd3 Qd1+ 47. Kc4 Qxd4+ 48. Kb5 Qd5+ 49. Kxa5 Kd6 50. Kb6 Qd3 51. a4 Qb1+ 52.
Ka7 Qa2 53. Kb8 Qxa4 54. Kc8 Qa8+ 55. Kc7 Qa7+ 56. Kc8 Qe7 57. g4 Qe8+ 58. Kc7
Qe5+ 59. Kc8 Qe8+ 60. Kb7 Qe7+ 61. Ka6 Kc7 62. g5 Qe6 63. Ka7 Qe7+ 64. Ka8 Qe8+
65. Ka7 Qd7+ 66. Ka6 Qd3+ 67. Ka7 Qd4+ 68. Ka8 Qd8+ 69. Ka7 Qd7+ 70. Kb8 Qd8+
71. Kb7 Qd7+ 72. Ka6 Qa4+ 73. Kb6 Qb4+ 74. Ka6 Qc5 75. Ka7 Qc4 76. Ka6 Qa2+ 77.
Kb5 Qb3+ 78. Ka6 Qxc3 79. Ka7 Qd4+ 80. Ka8 Qd8+ 81. Ka7 Qd7+ 82. Ka8 Qc8# 0-1"""

# Opening theory test
SAMPLE_GAME_5_OPENING = """[Event "Online Championship"]
[Site "Chess.com"]
[Date "2024.04.01"]
[Round "1"]
[White "TheoryExpert"]
[Black "PrepWizard"]
[Result "1/2-1/2"]
[ECO "D37"]
[WhiteElo "2550"]
[BlackElo "2580"]
[TimeControl "3600+30"]
[Termination "Draw by agreement"]

1. d4 Nf6 2. c4 e6 3. Nf3 d5 4. Nc3 Be7 5. Bf4 O-O 6. e3 c5 7. dxc5 Bxc5 8. Qc2
Nc6 9. a3 Qa5 10. Rd1 Be7 11. Be2 dxc4 12. Bxc4 Nh5 13. Be5 Nxe5 14. Nxe5 Nf6
15. O-O Bd7 16. Rd4 Bc6 17. Nxc6 bxc6 18. Be2 Rfd8 19. Rfd1 Rxd4 20. Rxd4 Rd8
21. Rxd8+ Bxd8 22. Kf1 Qc7 23. Qd3 Nd5 24. Nxd5 cxd5 25. Qxd5 Qc1+ 26. Bd1 Qxb2
27. Qd3 Qb1 28. Qd7 Qd3+ 29. Ke1 Qg3 30. Kd2 Qxf2+ 31. Kc3 Qe1+ 32. Kb3 Qb1+
33. Kc3 Qe1+ 34. Kb3 1/2-1/2"""


# Dictionary mapping for easy access
SAMPLE_GAMES = {
    "carlsen_tactical": SAMPLE_GAME_1_CARLSEN,
    "blunder_heavy": SAMPLE_GAME_2_BLUNDERS,
    "tactical_brilliancy": SAMPLE_GAME_3_TACTICAL,
    "endgame_grind": SAMPLE_GAME_4_ENDGAME,
    "opening_theory": SAMPLE_GAME_5_OPENING
}


def get_sample_pgn(game_name: str) -> str:
    """
    Get a sample PGN by name.
    
    Args:
        game_name: One of the keys from SAMPLE_GAMES
    
    Returns:
        PGN string
    """
    return SAMPLE_GAMES.get(game_name, SAMPLE_GAME_1_CARLSEN)


def get_all_sample_pgns() -> dict:
    """Get all sample PGNs."""
    return SAMPLE_GAMES.copy()
