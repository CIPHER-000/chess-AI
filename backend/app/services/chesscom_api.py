import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin

import httpx
from loguru import logger

from ..core.config import settings


class ChessComAPIError(Exception):
    """Exception for Chess.com API errors."""
    pass


class ChessComAPI:
    """Chess.com API client with rate limiting and caching."""
    
    def __init__(self):
        self.base_url = settings.CHESSCOM_API_BASE_URL
        self.rate_limit_delay = 60.0 / settings.CHESSCOM_API_RATE_LIMIT  # Delay between requests
        self.last_request_time = 0.0
        
        # HTTP client configuration
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            headers={
                "User-Agent": f"{settings.PROJECT_NAME}/{settings.VERSION}",
                "Accept": "application/json"
            }
        )
    
    async def _make_request(self, endpoint: str, headers: Optional[Dict] = None) -> Tuple[Dict, Dict]:
        """Make rate-limited request to Chess.com API."""
        
        # Rate limiting
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        
        self.last_request_time = asyncio.get_event_loop().time()
        
        url = urljoin(self.base_url, endpoint)
        request_headers = headers or {}
        
        try:
            logger.debug(f"Making request to {url}")
            response = await self.client.get(url, headers=request_headers)
            response.raise_for_status()
            
            # Return data and response headers for caching
            return response.json(), dict(response.headers)
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ChessComAPIError(f"User or resource not found: {endpoint}")
            elif e.response.status_code == 429:
                raise ChessComAPIError("Rate limit exceeded")
            else:
                raise ChessComAPIError(f"API request failed: {e.response.status_code}")
        except httpx.RequestError as e:
            raise ChessComAPIError(f"Request error: {str(e)}")
    
    async def get_player_profile(self, username: str) -> Dict:
        """Get player profile information."""
        endpoint = f"/player/{username.lower()}"
        data, headers = await self._make_request(endpoint)
        return data
    
    async def get_player_stats(self, username: str) -> Dict:
        """Get player statistics including ratings."""
        endpoint = f"/player/{username.lower()}/stats"
        data, headers = await self._make_request(endpoint)
        return data
    
    async def get_player_games_archive_list(self, username: str) -> List[str]:
        """Get list of available game archives for a player."""
        endpoint = f"/player/{username.lower()}/games/archives"
        data, headers = await self._make_request(endpoint)
        return data.get("archives", [])
    
    async def get_player_games_by_month(self, username: str, year: int, month: int, 
                                       etag: Optional[str] = None) -> Tuple[Dict, Dict]:
        """Get player games for a specific month with caching support."""
        endpoint = f"/player/{username.lower()}/games/{year:04d}/{month:02d}"
        
        headers = {}
        if etag:
            headers["If-None-Match"] = etag
        
        try:
            data, response_headers = await self._make_request(endpoint, headers)
            return data, response_headers
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 304:  # Not Modified
                return None, dict(e.response.headers)
            raise
    
    async def get_recent_games(self, username: str, days: int = 7) -> List[Dict]:
        """Get recent games for a player within the specified number of days."""
        
        # Get available archives
        archives = await self.get_player_games_archive_list(username)
        
        if not archives:
            return []
        
        # Sort archives by date (most recent first)
        archives.sort(reverse=True)
        
        # Calculate target date
        target_date = datetime.now(timezone.utc).timestamp() - (days * 24 * 3600)
        
        all_games = []
        
        # Fetch games from most recent archives until we have enough
        for archive_url in archives[:3]:  # Limit to last 3 months
            try:
                # Extract year and month from archive URL
                parts = archive_url.split('/')
                year, month = int(parts[-2]), int(parts[-1])
                
                games_data, _ = await self.get_player_games_by_month(username, year, month)
                
                if games_data and "games" in games_data:
                    games = games_data["games"]
                    
                    # Filter games by date
                    recent_games = [
                        game for game in games 
                        if game.get("end_time", 0) >= target_date
                    ]
                    
                    all_games.extend(recent_games)
                    
                    # If we found games older than our target, we can stop
                    if games and min(game.get("end_time", 0) for game in games) < target_date:
                        break
                        
            except ChessComAPIError as e:
                logger.warning(f"Failed to fetch archive {archive_url}: {e}")
                continue
        
        # Sort by end_time (most recent first) and limit
        all_games.sort(key=lambda x: x.get("end_time", 0), reverse=True)
        
        # Limit to reasonable number of games
        return all_games[:settings.MAX_GAMES_PER_ANALYSIS]
    
    async def get_player_current_daily_chess(self, username: str) -> Dict:
        """Get current daily chess games."""
        endpoint = f"/player/{username.lower()}/games/to-move"
        data, headers = await self._make_request(endpoint)
        return data
    
    def parse_game_data(self, game: Dict, username: str) -> Dict:
        """Parse and normalize game data from Chess.com API."""
        
        # Determine user's color and opponent
        white_player = game.get("white", {})
        black_player = game.get("black", {})
        
        user_color = None
        opponent_username = None
        user_rating = None
        opponent_rating = None
        
        if white_player.get("username", "").lower() == username.lower():
            user_color = "white"
            opponent_username = black_player.get("username")
            user_rating = white_player.get("rating")
            opponent_rating = black_player.get("rating")
        elif black_player.get("username", "").lower() == username.lower():
            user_color = "black"
            opponent_username = white_player.get("username")
            user_rating = black_player.get("rating")
            opponent_rating = white_player.get("rating")
        
        # Determine game result for user
        user_result = None
        if user_color == "white":
            user_result = white_player.get("result")
        elif user_color == "black":
            user_result = black_player.get("result")
        
        # Parse time control
        time_control = game.get("time_control", "")
        time_class = game.get("time_class", "")
        
        return {
            "chesscom_game_id": str(game.get("uuid", "")),
            "chesscom_url": game.get("url", ""),
            "time_class": time_class,
            "time_control": time_control,
            "rules": game.get("rules", "chess"),
            "white_username": white_player.get("username"),
            "black_username": black_player.get("username"),
            "white_rating": white_player.get("rating"),
            "black_rating": black_player.get("rating"),
            "white_result": white_player.get("result"),
            "black_result": black_player.get("result"),
            "pgn": game.get("pgn", ""),
            "fen": game.get("fen", ""),
            "start_time": datetime.fromtimestamp(game.get("start_time", 0), tz=timezone.utc) if game.get("start_time") else None,
            "end_time": datetime.fromtimestamp(game.get("end_time", 0), tz=timezone.utc) if game.get("end_time") else None,
            "user_color": user_color,
            "opponent_username": opponent_username,
            "user_rating": user_rating,
            "opponent_rating": opponent_rating,
            "user_result": user_result,
            "raw_data": game  # Store original data for reference
        }
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Global API client instance
chesscom_api = ChessComAPI()
