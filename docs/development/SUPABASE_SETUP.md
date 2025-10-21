# 🚀 Supabase Setup Guide for Chess Insight AI

This guide walks you through setting up Supabase for Chess Insight AI, replacing the local PostgreSQL instance.

## 📋 Prerequisites

- Supabase account (free tier available at https://supabase.com)
- Basic understanding of PostgreSQL and REST APIs

---

## 🏗️ Step 1: Create Supabase Project

1. **Go to Supabase Dashboard:**
   - Visit: https://app.supabase.com
   - Click "New Project"

2. **Configure Project:**
   - **Name**: `chess-insight-ai`
   - **Database Password**: Generate a strong password (save this!)
   - **Region**: Choose closest to your users
   - **Pricing Plan**: Free tier is sufficient for development

3. **Wait for Project Setup** (1-2 minutes)

---

## 🔑 Step 2: Get API Keys

Once your project is ready:

1. **Navigate to Project Settings:**
   - Settings → API

2. **Copy the following:**
   - **Project URL**: `https://your-project-ref.supabase.co`
   - **anon/public key**: For client-side requests
   - **service_role key**: For server-side admin operations (keep secret!)

3. **Copy Database Password:**
   - Settings → Database
   - You'll need this for direct PostgreSQL connections

---

## 🗄️ Step 3: Set Up Database Tables

### Option A: Using Supabase SQL Editor (Recommended)

1. Go to **SQL Editor** in Supabase dashboard
2. Create a new query
3. Paste and run the following SQL:

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    chesscom_username VARCHAR UNIQUE NOT NULL,
    display_name VARCHAR,
    email VARCHAR UNIQUE,
    
    -- Supabase auth integration
    supabase_user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Chess.com profile data
    chesscom_profile JSONB,
    current_ratings JSONB,
    
    -- User preferences
    analysis_preferences JSONB DEFAULT '{}',
    notification_preferences JSONB DEFAULT '{}',
    
    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_analysis_at TIMESTAMPTZ,
    
    -- Indexes
    CONSTRAINT users_chesscom_username_key UNIQUE (chesscom_username),
    CONSTRAINT users_email_key UNIQUE (email)
);

-- Games table
CREATE TABLE games (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    -- Chess.com game data
    chesscom_game_id VARCHAR UNIQUE NOT NULL,
    url VARCHAR NOT NULL,
    pgn TEXT NOT NULL,
    
    -- Game metadata
    time_control VARCHAR NOT NULL,
    time_class VARCHAR NOT NULL,
    rules VARCHAR NOT NULL,
    rated BOOLEAN DEFAULT TRUE,
    
    -- Players
    white_username VARCHAR NOT NULL,
    white_rating INTEGER NOT NULL,
    black_username VARCHAR NOT NULL,
    black_rating INTEGER NOT NULL,
    
    -- Results
    white_result VARCHAR NOT NULL,
    black_result VARCHAR NOT NULL,
    
    -- Opening
    eco VARCHAR,
    opening_name VARCHAR,
    
    -- Timestamps
    end_time TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    analyzed_at TIMESTAMPTZ,
    
    -- Analysis status
    is_analyzed BOOLEAN DEFAULT FALSE,
    
    CONSTRAINT games_chesscom_game_id_key UNIQUE (chesscom_game_id)
);

-- User insights table
CREATE TABLE user_insights (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    -- Time period
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    
    -- Metrics
    total_games INTEGER NOT NULL,
    total_moves INTEGER NOT NULL,
    user_acpl FLOAT NOT NULL,
    opponent_acpl FLOAT NOT NULL,
    
    -- Move quality distribution
    brilliant_moves INTEGER DEFAULT 0,
    great_moves INTEGER DEFAULT 0,
    best_moves INTEGER DEFAULT 0,
    excellent_moves INTEGER DEFAULT 0,
    good_moves INTEGER DEFAULT 0,
    inaccuracies INTEGER DEFAULT 0,
    mistakes INTEGER DEFAULT 0,
    blunders INTEGER DEFAULT 0,
    
    -- Phase performance
    opening_acpl FLOAT,
    middlegame_acpl FLOAT,
    endgame_acpl FLOAT,
    
    -- Opening analysis
    opening_eco_distribution JSONB,
    best_openings JSONB,
    worst_openings JSONB,
    
    -- Recommendations
    recommendations JSONB,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_users_supabase_user_id ON users(supabase_user_id);
CREATE INDEX idx_users_chesscom_username ON users(chesscom_username);
CREATE INDEX idx_games_user_id ON games(user_id);
CREATE INDEX idx_games_end_time ON games(end_time);
CREATE INDEX idx_games_is_analyzed ON games(is_analyzed);
CREATE INDEX idx_insights_user_id ON user_insights(user_id);
CREATE INDEX idx_insights_period ON user_insights(period_start, period_end);

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_insights_updated_at BEFORE UPDATE ON user_insights
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### Option B: Using Alembic Migrations

The existing Alembic migrations will work, but you'll need to update the connection string (see Step 4).

---

## 🔐 Step 4: Configure Row Level Security (RLS)

Enable RLS for data protection:

```sql
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE games ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_insights ENABLE ROW LEVEL SECURITY;

-- Users table policies
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (auth.uid() = supabase_user_id);

CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (auth.uid() = supabase_user_id);

-- Games table policies
CREATE POLICY "Users can view own games" ON games
    FOR SELECT USING (
        user_id IN (SELECT id FROM users WHERE supabase_user_id = auth.uid())
    );

CREATE POLICY "Users can insert own games" ON games
    FOR INSERT WITH CHECK (
        user_id IN (SELECT id FROM users WHERE supabase_user_id = auth.uid())
    );

-- Insights table policies
CREATE POLICY "Users can view own insights" ON user_insights
    FOR SELECT USING (
        user_id IN (SELECT id FROM users WHERE supabase_user_id = auth.uid())
    );

-- Service role bypass (for backend operations)
-- The service role key automatically bypasses RLS
```

---

## 📁 Step 5: Set Up Storage Bucket

For storing game reports and uploaded files:

1. **Go to Storage** in Supabase dashboard
2. **Create new bucket:**
   - Name: `chess-insight-files`
   - Public: `No` (private bucket)
   - File size limit: `10 MB`
   - Allowed MIME types: `application/pdf, image/*`

3. **Set up storage policies:**

```sql
-- Allow authenticated users to upload their own files
CREATE POLICY "Users can upload own files" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'chess-insight-files' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Allow users to view their own files
CREATE POLICY "Users can view own files" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'chess-insight-files' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );
```

---

## ⚙️ Step 6: Update Local Environment

1. **Copy the updated `.env.example` to `.env`:**
   ```powershell
   cp .env.example .env
   ```

2. **Edit `.env` with your Supabase credentials:**
   ```env
   # Supabase Configuration
   SUPABASE_URL=https://your-project-ref.supabase.co
   SUPABASE_ANON_KEY=your-anon-key-here
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
   SUPABASE_DB_PASSWORD=your-database-password
   SUPABASE_STORAGE_BUCKET=chess-insight-files
   
   # OpenAI API (rotate the exposed key!)
   OPENAI_API_KEY=your-new-openai-key-here
   
   # Redis (keep for caching)
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_DB=0
   
   # Other settings...
   ```

---

## 🧪 Step 7: Test the Connection

1. **Install updated dependencies:**
   ```powershell
   cd backend
   pip install -r requirements.txt
   ```

2. **Test Supabase connection:**
   ```python
   # Run in Python console or create test script
   from app.core.supabase_client import get_supabase
   
   supabase = get_supabase()
   print("✅ Supabase connected successfully!")
   
   # Test query
   result = supabase.table('users').select('*').limit(1).execute()
   print(f"Query result: {result}")
   ```

---

## 🔄 Step 8: Migrate Existing Data (If Applicable)

If you have existing PostgreSQL data to migrate:

1. **Export from PostgreSQL:**
   ```powershell
   pg_dump -U chessai -d chessai -F c -f backup.dump
   ```

2. **Import to Supabase:**
   - Use Supabase CLI or direct PostgreSQL connection
   - Supabase provides PostgreSQL connection string in Settings → Database

---

## 🚀 Step 9: Update Docker Compose

The updated `docker-compose.yml` removes PostgreSQL and keeps only Redis:

```yaml
services:
  # Redis Cache (keep for Celery)
  redis:
    image: redis:7-alpine
    container_name: chess-insight-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  # Backend API (now using Supabase)
  backend:
    build: ./backend
    container_name: chess-insight-backend
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    env_file:
      - .env
    depends_on:
      - redis
    restart: unless-stopped

volumes:
  redis_data:
```

---

## ✅ Verification Checklist

- [ ] Supabase project created
- [ ] API keys copied to `.env`
- [ ] Database tables created
- [ ] RLS policies enabled
- [ ] Storage bucket configured
- [ ] Backend connects successfully
- [ ] Test user can register/login
- [ ] Docker Compose starts without errors

---

## 🔮 Next Steps

1. **Test authentication flow** - Register and login
2. **Import Chess.com games** - Test game fetching
3. **Run analysis** - Verify Stockfish integration
4. **Deploy to production** - Update Render.com config

---

## 🆘 Troubleshooting

### Connection Issues
**Error**: `Unable to connect to Supabase`
- Verify URL format: `https://your-project.supabase.co`
- Check API keys are correct
- Ensure project is active (not paused on free tier)

### RLS Blocking Queries
**Error**: `Row-level security policy violation`
- Use `service_role` key for backend operations
- Check policies match your use case
- Verify user authentication tokens

### Storage Upload Fails
**Error**: `Storage upload denied`
- Check bucket name matches `SUPABASE_STORAGE_BUCKET`
- Verify storage policies are created
- Ensure user is authenticated

---

**🎉 You're now ready to use Supabase with Chess Insight AI!**
