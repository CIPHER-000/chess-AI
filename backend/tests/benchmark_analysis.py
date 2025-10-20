"""
Benchmarking suite for chess analysis performance.

Run with: pytest benchmark_analysis.py -v --benchmark
"""
import time
import statistics
from typing import List, Dict
from fixtures.sample_pgns import get_all_sample_pgns
import chess.pgn
import io


class AnalysisBenchmark:
    """Benchmark chess analysis operations."""
    
    def __init__(self):
        self.results: Dict[str, List[float]] = {}
    
    def benchmark_pgn_parsing(self, iterations: int = 100) -> Dict:
        """
        Benchmark PGN parsing speed.
        
        Args:
            iterations: Number of iterations to run
        
        Returns:
            Dict with timing statistics
        """
        samples = get_all_sample_pgns()
        timings = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            
            for pgn in samples.values():
                game = chess.pgn.read_game(io.StringIO(pgn))
                assert game is not None
            
            elapsed = time.perf_counter() - start
            timings.append(elapsed)
        
        return {
            "operation": "pgn_parsing",
            "iterations": iterations,
            "games_per_iteration": len(samples),
            "mean_time": statistics.mean(timings),
            "median_time": statistics.median(timings),
            "min_time": min(timings),
            "max_time": max(timings),
            "stddev": statistics.stdev(timings) if len(timings) > 1 else 0
        }
    
    def benchmark_move_iteration(self, iterations: int = 100) -> Dict:
        """
        Benchmark move iteration speed.
        
        Args:
            iterations: Number of iterations
        
        Returns:
            Dict with timing statistics
        """
        samples = get_all_sample_pgns()
        timings = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            
            for pgn in samples.values():
                game = chess.pgn.read_game(io.StringIO(pgn))
                board = game.board()
                
                for move in game.mainline_moves():
                    board.push(move)
            
            elapsed = time.perf_counter() - start
            timings.append(elapsed)
        
        return {
            "operation": "move_iteration",
            "iterations": iterations,
            "games_per_iteration": len(samples),
            "mean_time": statistics.mean(timings),
            "median_time": statistics.median(timings),
            "min_time": min(timings),
            "max_time": max(timings),
            "stddev": statistics.stdev(timings) if len(timings) > 1 else 0
        }
    
    def benchmark_position_evaluation(self, iterations: int = 50) -> Dict:
        """
        Benchmark position evaluation (requires Stockfish).
        
        Args:
            iterations: Number of positions to evaluate
        
        Returns:
            Dict with timing statistics
        """
        try:
            from stockfish import Stockfish
            import os
            
            stockfish_path = os.getenv("STOCKFISH_PATH", "/usr/games/stockfish")
            stockfish = Stockfish(path=stockfish_path, depth=10)
            
            # Test positions
            positions = [
                "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",  # Starting
                "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4",  # Italian
                "rnbqkb1r/ppp2ppp/4pn2/3p4/2PP4/2N5/PP2PPPP/R1BQKBNR w KQkq - 0 4",  # Queen's Gambit
            ]
            
            timings = []
            
            for _ in range(iterations):
                start = time.perf_counter()
                
                for fen in positions:
                    stockfish.set_fen_position(fen)
                    stockfish.get_evaluation()
                
                elapsed = time.perf_counter() - start
                timings.append(elapsed)
            
            return {
                "operation": "position_evaluation",
                "iterations": iterations,
                "positions_per_iteration": len(positions),
                "mean_time": statistics.mean(timings),
                "median_time": statistics.median(timings),
                "min_time": min(timings),
                "max_time": max(timings),
                "stddev": statistics.stdev(timings) if len(timings) > 1 else 0,
                "stockfish_available": True
            }
        
        except Exception as e:
            return {
                "operation": "position_evaluation",
                "error": str(e),
                "stockfish_available": False
            }
    
    def run_all_benchmarks(self, verbose: bool = True) -> Dict:
        """
        Run all benchmarks and return results.
        
        Args:
            verbose: Print results to console
        
        Returns:
            Dict with all benchmark results
        """
        results = {}
        
        # PGN Parsing
        if verbose:
            print("\n🔄 Benchmarking PGN parsing...")
        results["pgn_parsing"] = self.benchmark_pgn_parsing()
        
        # Move Iteration
        if verbose:
            print("🔄 Benchmarking move iteration...")
        results["move_iteration"] = self.benchmark_move_iteration()
        
        # Position Evaluation (optional - requires Stockfish)
        if verbose:
            print("🔄 Benchmarking position evaluation (Stockfish)...")
        results["position_evaluation"] = self.benchmark_position_evaluation()
        
        if verbose:
            self.print_results(results)
        
        return results
    
    def print_results(self, results: Dict):
        """Print benchmark results in readable format."""
        print("\n" + "="*60)
        print("📊 CHESS ANALYSIS BENCHMARK RESULTS")
        print("="*60)
        
        for operation, data in results.items():
            print(f"\n🎯 {operation.replace('_', ' ').title()}")
            print("-" * 60)
            
            if "error" in data:
                print(f"  ❌ Error: {data['error']}")
                continue
            
            if "iterations" in data:
                print(f"  Iterations: {data['iterations']}")
            
            if "games_per_iteration" in data:
                print(f"  Games per iteration: {data['games_per_iteration']}")
            
            if "positions_per_iteration" in data:
                print(f"  Positions per iteration: {data['positions_per_iteration']}")
            
            print(f"\n  ⏱️  Timing Statistics:")
            print(f"    Mean:   {data.get('mean_time', 0)*1000:.2f} ms")
            print(f"    Median: {data.get('median_time', 0)*1000:.2f} ms")
            print(f"    Min:    {data.get('min_time', 0)*1000:.2f} ms")
            print(f"    Max:    {data.get('max_time', 0)*1000:.2f} ms")
            print(f"    StdDev: {data.get('stddev', 0)*1000:.2f} ms")
            
            # Calculate throughput
            if "mean_time" in data and data["mean_time"] > 0:
                if "games_per_iteration" in data:
                    throughput = data["games_per_iteration"] / data["mean_time"]
                    print(f"\n  📈 Throughput: {throughput:.2f} games/second")
                elif "positions_per_iteration" in data:
                    throughput = data["positions_per_iteration"] / data["mean_time"]
                    print(f"\n  📈 Throughput: {throughput:.2f} positions/second")
        
        print("\n" + "="*60)
        print("✅ Benchmark complete!")
        print("="*60 + "\n")


def test_run_benchmarks():
    """Pytest-compatible benchmark runner."""
    benchmark = AnalysisBenchmark()
    results = benchmark.run_all_benchmarks(verbose=True)
    
    # Assertions for performance targets
    assert results["pgn_parsing"]["mean_time"] < 0.1, "PGN parsing too slow"
    assert results["move_iteration"]["mean_time"] < 0.2, "Move iteration too slow"


if __name__ == "__main__":
    # Run benchmarks directly
    benchmark = AnalysisBenchmark()
    results = benchmark.run_all_benchmarks(verbose=True)
    
    # Save results to file
    import json
    from datetime import datetime
    
    output = {
        "timestamp": datetime.now().isoformat(),
        "results": results
    }
    
    with open("benchmark_results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"📝 Results saved to benchmark_results.json")
