-- Add tier management fields to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS tier VARCHAR DEFAULT 'free';
ALTER TABLE users ADD COLUMN IF NOT EXISTS ai_analyses_used INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS ai_analyses_limit INTEGER DEFAULT 5;
ALTER TABLE users ADD COLUMN IF NOT EXISTS trial_exhausted_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS total_games INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS analyzed_games INTEGER DEFAULT 0;

-- Update existing users to have default values
UPDATE users SET tier = 'free' WHERE tier IS NULL;
UPDATE users SET ai_analyses_used = 0 WHERE ai_analyses_used IS NULL;
UPDATE users SET ai_analyses_limit = 5 WHERE ai_analyses_limit IS NULL;
UPDATE users SET total_games = 0 WHERE total_games IS NULL;
UPDATE users SET analyzed_games = 0 WHERE analyzed_games IS NULL;
