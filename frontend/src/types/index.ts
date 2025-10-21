// User types
export interface User {
  id: number;
  chesscom_username: string;
  display_name?: string;
  email?: string;
  is_active: boolean;
  
  // Connection and authentication
  connection_type?: string;  // "username_only", "oauth", "api_key"
  is_chesscom_connected?: boolean;
  connection_status?: string;  // Property from backend: "Public Data Only", "Authenticated", etc.
  can_access_private_data?: boolean;  // Property from backend
  
  // Chess.com data
  chesscom_profile?: Record<string, any>;
  current_ratings?: Record<string, any>;
  
  // Preferences
  analysis_preferences?: Record<string, any>;
  notification_preferences?: Record<string, any>;
  
  // Metadata
  created_at?: string;
  updated_at?: string;
  last_analysis_at?: string;
}

export interface UserCreate {
  chesscom_username: string;
  email?: string;
}

// Game types
export interface Game {
  id: number;
  chesscom_game_id: string;
  chesscom_url?: string;
  time_class?: string;
  time_control?: string;
  white_username?: string;
  black_username?: string;
  white_rating?: number;
  black_rating?: number;
  white_result?: string;
  black_result?: string;
  winner?: string;
  start_time?: string;
  end_time?: string;
  is_analyzed: boolean;
}

// Analysis types
export interface Analysis {
  id: number;
  game_id: number;
  engine_version?: string;
  analysis_depth?: number;
  analysis_time?: number;
  user_color?: string;
  user_acpl?: number;
  opponent_acpl?: number;
  brilliant_moves: number;
  great_moves: number;
  best_moves: number;
  excellent_moves: number;
  good_moves: number;
  inaccuracies: number;
  mistakes: number;
  blunders: number;
  opening_acpl?: number;
  middlegame_acpl?: number;
  endgame_acpl?: number;
  opening_name?: string;
  opening_eco?: string;
  opening_moves?: number;
}

// Insight types
export interface UserInsight {
  id: number;
  user_id: number;
  period_start: string;
  period_end: string;
  analysis_type: string;
  total_games: number;
  games_analyzed: number;
  average_acpl?: number;
  performance_trend?: string;
  rating_change?: number;
  opening_performance?: Record<string, any>;
  middlegame_performance?: Record<string, any>;
  endgame_performance?: Record<string, any>;
  move_quality_stats?: Record<string, number>;
  frequent_mistakes?: Record<string, any>;
  recommendations?: Record<string, any>;
}

// API Response types
export interface ApiResponse<T> {
  data?: T;
  message?: string;
  error?: string;
}

// Fetch Games Response
export interface FetchGamesResponse {
  message: string;
  games_added: number;
  games_updated: number;
  total_games: number;
}

// Analyze Games Response
export interface AnalyzeGamesResponse {
  message: string;
  games_queued: number;
}

// Generate Insights Response
export interface GenerateInsightsResponse {
  message: string;
  period_start: string;
  period_end: string;
}

// Chart data types
export interface ChartData {
  name: string;
  value: number;
  fill?: string;
}

export interface TimeSeriesData {
  date: string;
  acpl: number;
  rating: number;
}

// Move quality types
export interface MoveQualityStats {
  brilliant_moves: number;
  great_moves: number;
  best_moves: number;
  excellent_moves: number;
  good_moves: number;
  inaccuracies: number;
  mistakes: number;
  blunders: number;
}

// Recommendation types
export interface Recommendation {
  category: string;
  priority: 'high' | 'medium' | 'low';
  description: string;
}

// Dashboard types
export interface DashboardData {
  user: User;
  recent_games: Game[];
  latest_insight?: UserInsight;
  performance_summary: {
    total_games: number;
    average_acpl: number;
    accuracy_percentage: number;
    rating_change: number;
  };
  move_quality_stats: MoveQualityStats;
  recommendations: Recommendation[];
}
