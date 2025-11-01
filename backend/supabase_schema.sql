-- ============================================
-- Chess Insight AI - Complete Schema Migration for Supabase
-- ============================================
-- This creates the full database schema including:
-- 1. users table (with tier management)
-- 2. games table
-- 3. game_analyses table
-- 4. user_insights table
-- ============================================

-- Drop tables if they exist (be careful!)
DROP TABLE IF EXISTS game_analyses CASCADE;
DROP TABLE IF EXISTS user_insights CASCADE;
DROP TABLE IF EXISTS games CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ============================================
-- TABLE 1: users
-- ============================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    chesscom_username VARCHAR NOT NULL UNIQUE,
    display_name VARCHAR,
    email VARCHAR UNIQUE,
    
    -- Authentication and connection
    connection_type VARCHAR DEFAULT 'username_only',
    is_chesscom_connected BOOLEAN DEFAULT FALSE,
    chesscom_user_id VARCHAR,
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Chess.com profile data
    chesscom_profile JSONB,
    current_ratings JSONB,
    
    -- User preferences
    analysis_preferences JSONB DEFAULT '{}'::jsonb,
    notification_preferences JSONB DEFAULT '{}'::jsonb,
    
    -- Tier management (NEW)
    tier VARCHAR DEFAULT 'free',
    ai_analyses_used INTEGER DEFAULT 0,
    ai_analyses_limit INTEGER DEFAULT 5,
    trial_exhausted_at TIMESTAMP WITH TIME ZONE,
    
    -- Game statistics (NEW)
    total_games INTEGER DEFAULT 0,
    analyzed_games INTEGER DEFAULT 0,
    
    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_analysis_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for users table
CREATE INDEX idx_users_chesscom_username ON users(chesscom_username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_tier ON users(tier);

-- ============================================
-- TABLE 2: games
-- ============================================
CREATE TABLE games (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chesscom_game_id VARCHAR NOT NULL UNIQUE,
    chesscom_url VARCHAR,
    
    -- Game metadata
    time_class VARCHAR,
    time_control VARCHAR,
    rules VARCHAR DEFAULT 'chess',
    
    -- Players
    white_username VARCHAR,
    black_username VARCHAR,
    white_rating INTEGER,
    black_rating INTEGER,
    white_result VARCHAR,
    black_result VARCHAR,
    winner VARCHAR,
    
    -- Game data
    pgn TEXT,
    fen VARCHAR,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    
    -- Analysis status
    is_analyzed BOOLEAN DEFAULT FALSE,
    analysis_data JSONB,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for games table
CREATE INDEX idx_games_user_id ON games(user_id);
CREATE INDEX idx_games_chesscom_game_id ON games(chesscom_game_id);
CREATE INDEX idx_games_end_time ON games(end_time);
CREATE INDEX idx_games_time_class ON games(time_class);
CREATE INDEX idx_games_is_analyzed ON games(is_analyzed);

-- ============================================
-- TABLE 3: game_analyses
-- ============================================
CREATE TABLE game_analyses (
    id SERIAL PRIMARY KEY,
    game_id INTEGER NOT NULL UNIQUE REFERENCES games(id) ON DELETE CASCADE,
    
    -- Analysis metadata
    engine_version VARCHAR,
    analysis_depth INTEGER,
    analysis_time FLOAT,
    
    -- User-specific metrics
    user_color VARCHAR,
    user_acpl FLOAT,
    opponent_acpl FLOAT,
    
    -- Move classifications
    brilliant_moves INTEGER DEFAULT 0,
    great_moves INTEGER DEFAULT 0,
    best_moves INTEGER DEFAULT 0,
    excellent_moves INTEGER DEFAULT 0,
    good_moves INTEGER DEFAULT 0,
    inaccuracies INTEGER DEFAULT 0,
    mistakes INTEGER DEFAULT 0,
    blunders INTEGER DEFAULT 0,
    
    -- Game phase analysis
    opening_acpl FLOAT,
    middlegame_acpl FLOAT,
    endgame_acpl FLOAT,
    
    -- Opening analysis
    opening_name VARCHAR,
    opening_eco VARCHAR,
    opening_moves INTEGER,
    
    -- Detailed data
    evaluations JSONB,
    critical_positions JSONB,
    blunder_moves JSONB,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for game_analyses table
CREATE INDEX idx_game_analyses_game_id ON game_analyses(game_id);

-- ============================================
-- TABLE 4: user_insights
-- ============================================
CREATE TABLE user_insights (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Insight details
    insight_type VARCHAR NOT NULL,
    insight_data JSONB,
    priority VARCHAR,
    category VARCHAR,
    description VARCHAR,
    recommendation VARCHAR,
    confidence_score FLOAT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for user_insights table
CREATE INDEX idx_user_insights_user_id ON user_insights(user_id);
CREATE INDEX idx_user_insights_created_at ON user_insights(created_at);

-- ============================================
-- Enable Row Level Security (RLS) for Supabase
-- ============================================
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE games ENABLE ROW LEVEL SECURITY;
ALTER TABLE game_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_insights ENABLE ROW LEVEL SECURITY;

-- ============================================
-- RLS Policies (Basic - adjust as needed)
-- ============================================

-- Users: Allow users to read/update their own data
CREATE POLICY "Users can view their own data" ON users
    FOR SELECT USING (true);  -- Public read for now

CREATE POLICY "Users can update their own data" ON users
    FOR UPDATE USING (true);

-- Games: Allow users to view their own games
CREATE POLICY "Users can view games" ON games
    FOR SELECT USING (true);

-- Game analyses: Allow users to view analyses
CREATE POLICY "Users can view analyses" ON game_analyses
    FOR SELECT USING (true);

-- User insights: Allow users to view insights
CREATE POLICY "Users can view insights" ON user_insights
    FOR SELECT USING (true);

-- ============================================
-- Triggers for updated_at timestamps
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_games_updated_at BEFORE UPDATE ON games
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_insights_updated_at BEFORE UPDATE ON user_insights
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Success message
-- ============================================
SELECT 'Schema migration completed successfully!' AS message;
SELECT 'Tables created: users, games, game_analyses, user_insights' AS tables;
SELECT 'Tier management fields added to users table' AS features;
