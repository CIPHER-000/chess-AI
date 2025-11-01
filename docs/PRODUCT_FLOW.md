# 🎯 Chess Insight AI - Product Flow & Architecture

**Last Updated**: November 1, 2025  
**Version**: 2.0 (Post-Refactoring)

---

## 📊 Table of Contents

1. [Overview](#overview)
2. [User Journey](#user-journey)
3. [Feature Gating (Free vs Pro)](#feature-gating-free-vs-pro)
4. [Technical Architecture](#technical-architecture)
5. [Chess.com API Integration](#chesscom-api-integration)
6. [Analysis Pipeline](#analysis-pipeline)
7. [Caching Strategy](#caching-strategy)
8. [Database Schema](#database-schema)
9. [Extension Points](#extension-points)

---

## 🌐 Overview

Chess Insight AI is a chess improvement platform that:
1. Fetches games from Chess.com's public API
2. Analyzes them using Stockfish chess engine
3. Generates AI-powered coaching insights
4. Recommends personalized YouTube training videos

### **Core Value Proposition**
- **For Free Users**: Get Stockfish-based metrics (ACPL, blunders, etc.) + 5 full AI analyses
- **For Pro Users**: Unlimited AI coaching, YouTube recommendations, advanced filters

---

## 🚀 User Journey

### **Step 1: Landing / Sign-In Page** (`/`)

**Purpose**: User enters their Chess.com username and optionally configures filters.

**User Actions**:
1. Enter Chess.com username (required)
2. Enter email (optional, for future features)
3. **Configure filters** (optional):
   - Game count: "Last 10 games", "Last 25 games", "Last 50 games", "All games"
   - Date range: Custom start/end dates
   - Time control: "Bullet", "Blitz", "Rapid", "Daily", "All"
   - Game type: "Rated", "Unrated", "All"

4. Click **"Get Started"**

**Backend Actions**:
- Check if user exists in database
  - **If exists**: Load user and redirect to dashboard
  - **If new**: Create user → Trigger game fetching background task
- Fetch games from Chess.com API with applied filters
- Store games in PostgreSQL
- Redirect to dashboard

**Technical Flow**:
```typescript
// Frontend (index.tsx)
onSubmit() → 
  api.users.create({ username, filters }) → 
    Background job: FetchGamesTask →
      Chess.com API → 
        Parse & store games →
          Return user with games_count

// Polling (frontend)
pollUserData() → 
  Check every 3 seconds →
    If games_count > 0 → Redirect to dashboard
```

---

### **Step 2: Dashboard Page** (`/dashboard?username={username}`)

**Purpose**: Display fetched games, allow re-filtering, and trigger analysis.

**Sections**:
1. **User Stats Card**
   - Total games fetched
   - Games analyzed
   - Current tier (Free/Pro)
   - Trial analyses remaining (if Free)

2. **Action Buttons**
   - **"Sync Recent Games"**: Fetch new games from Chess.com
   - **"Analyze with AI"** (Pro) / **"Analyze with Stockfish"** (Free after trial)
   - **"Force Re-analyze"**: Re-run analysis on already-analyzed games

3. **Filter Panel** (Re-filterable on dashboard)
   - Same filters as landing page
   - Apply button refreshes game list

4. **Games Table**
   - Opponent, Result, Rating, Time Control, Date
   - "View Analysis" button (if analyzed)

5. **Insights Section** (Visible only if games are analyzed)
   - **Stockfish Metrics** (Always visible):
     - Average ACPL
     - Blunders, Mistakes, Inaccuracies count
     - Opening performance
     - Phase performance (Opening/Middlegame/Endgame)
   
   - **AI Coaching** (Pro only or Free trial):
     - Behavioral patterns detected
     - Personalized recommendations
     - YouTube video suggestions

---

## 🔒 Feature Gating (Free vs Pro)

### **Free Tier**
- ✅ Unlimited game fetching
- ✅ Stockfish analysis (ACPL, blunders, phase performance)
- ✅ **5 full AI analyses** (includes coaching + YouTube videos)
- ⏸️ After trial: Stockfish-only mode (metrics but no AI insights)
- ❌ Advanced filters (date range, time control)
- ❌ Force re-analysis

**Trial Counter**:
```sql
-- User model
ai_analyses_used INT DEFAULT 0,
ai_analyses_limit INT DEFAULT 5,
tier VARCHAR DEFAULT 'free'
```

**Logic**:
```python
if user.tier == 'free' and user.ai_analyses_used >= user.ai_analyses_limit:
    # Run Stockfish only, skip AI layer
    return stockfish_only_analysis()
else:
    # Run full pipeline
    return full_ai_analysis()
```

### **Pro Tier**
- ✅ Everything in Free
- ✅ Unlimited AI analyses
- ✅ YouTube video recommendations
- ✅ Advanced filtering
- ✅ Force re-analysis
- ✅ Priority support

**Upgrade CTA**:
When free trial exhausted, show banner:
```
🎯 You're viewing Stockfish-only insights.
Upgrade to Pro for AI coaching and video recommendations.
[Upgrade to Pro →]
```

---

## 🏗️ Technical Architecture

### **System Components**

```
┌─────────────────────────────────────────────┐
│           Frontend (Next.js)                │
│                                             │
│  Landing Page → Dashboard → Analysis View   │
└─────────────────┬───────────────────────────┘
                  │
                  ├─► API Gateway (FastAPI)
                  │
┌─────────────────▼───────────────────────────┐
│               Backend Services              │
│                                             │
│  ┌────────────────────────────────────┐    │
│  │  ChessComService                   │    │
│  │  - Fetch games                     │    │
│  │  - Validate usernames              │    │
│  │  - Apply filters                   │    │
│  └────────────────────────────────────┘    │
│                                             │
│  ┌────────────────────────────────────┐    │
│  │  ChessAnalysisService              │    │
│  │  - Stockfish evaluation            │    │
│  │  - ACPL calculation                │    │
│  │  - Move classification             │    │
│  └────────────────────────────────────┘    │
│                                             │
│  ┌────────────────────────────────────┐    │
│  │  AIInsightsService                 │    │
│  │  - Pattern detection               │    │
│  │  - Coaching generation             │    │
│  │  - YouTube recommendations         │    │
│  └────────────────────────────────────┘    │
│                                             │
│  ┌────────────────────────────────────┐    │
│  │  TierManagementService             │    │
│  │  - Check trial status              │    │
│  │  - Enforce limits                  │    │
│  └────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
                  │
                  ├─► PostgreSQL (Users, Games, Analyses)
                  ├─► Redis (Caching, Background Jobs)
                  └─► Stockfish Engine
```

---

## 🌐 Chess.com API Integration

### **Endpoints Used**

1. **Get Player Profile**
   ```
   GET https://api.chess.com/pub/player/{username}
   ```
   Returns: Player info, ratings, profile

2. **Get Player Game Archives**
   ```
   GET https://api.chess.com/pub/player/{username}/games/archives
   ```
   Returns: Array of monthly archive URLs
   ```json
   {
     "archives": [
       "https://api.chess.com/pub/player/{username}/games/2025/10",
       "https://api.chess.com/pub/player/{username}/games/2025/09"
     ]
   }
   ```

3. **Get Games from Monthly Archive**
   ```
   GET https://api.chess.com/pub/player/{username}/games/{YYYY}/{MM}
   ```
   Returns: Array of games with PGN, results, ratings

### **Filtering Parameters**

Chess.com API doesn't support native filtering, so we filter **post-fetch**:

**Client-Side Filters**:
- **Game Count**: Slice array after sorting by date
- **Date Range**: Filter by `end_time` field
- **Time Control**: Parse `time_class` field (`bullet`, `blitz`, `rapid`, `daily`)
- **Rated/Unrated**: Filter by `rated` boolean field

**Example Flow**:
```python
# Fetch all recent games
all_games = await fetch_games_from_api(username)

# Apply filters
filtered_games = [
    game for game in all_games
    if game.end_time >= start_date
    and game.end_time <= end_date
    and game.time_class in selected_time_controls
    and (not rated_only or game.rated)
][:game_limit]
```

### **Rate Limiting**
- Chess.com: **300 requests per minute** per IP
- Our caching: Store games for **24 hours** to minimize API calls
- ETag/Last-Modified headers: Check for new games without re-fetching

---

## ⚙️ Analysis Pipeline

### **Phase 1: Stockfish Analysis** (Always runs)

**Input**: PGN string

**Process**:
1. Parse PGN with `python-chess`
2. Iterate through each move
3. Evaluate position before and after each move
4. Calculate centipawn loss (CP before - CP after)
5. Classify moves: Brilliant, Great, Best, Excellent, Good, Inaccuracy, Mistake, Blunder

**Output**:
```json
{
  "game_id": 123,
  "user_acpl": 45.2,
  "brilliant_moves": 2,
  "great_moves": 5,
  "best_moves": 12,
  "excellent_moves": 8,
  "good_moves": 10,
  "inaccuracies": 4,
  "mistakes": 2,
  "blunders": 1,
  "opening_acpl": 35.0,
  "middlegame_acpl": 50.5,
  "endgame_acpl": 48.0,
  "opening_name": "Sicilian Defense: Najdorf Variation"
}
```

### **Phase 2: AI Insights** (Pro or Free trial only)

**Input**: Stockfish analysis + User game history

**Process**:
1. Detect patterns across multiple games:
   - Time trouble (low time in critical positions)
   - Opening repertoire weaknesses
   - Tactical blind spots (missed forks, pins, etc.)
   - Endgame deficiencies

2. Generate coaching text:
   ```
   "You tend to blunder in time trouble during the middlegame. 
   Consider practicing rapid time controls to build speed."
   ```

3. Recommend YouTube videos:
   - Query based on detected weaknesses
   - Match to relevant chess channels (GothamChess, Naroditsky, etc.)

**Output**:
```json
{
  "insights": [
    {
      "category": "time_management",
      "severity": "high",
      "description": "You blundered 3 times in positions with <10 seconds left"
    },
    {
      "category": "opening",
      "severity": "medium",
      "description": "Your Sicilian Defense scores 35% worse than other openings"
    }
  ],
  "recommendations": [
    "Practice bullet games to improve time management",
    "Study the Najdorf Variation systematically"
  ],
  "youtube_videos": [
    {
      "title": "Time Management in Chess | GothamChess",
      "url": "https://youtube.com/watch?v=...",
      "relevance_score": 0.95
    }
  ]
}
```

---

## 💾 Caching Strategy

### **Game Data**
- **Cache Key**: `games:{username}:{filters_hash}`
- **TTL**: 24 hours
- **Invalidation**: Manual "Sync Recent Games" button

### **Analysis Results**
- **Cache Key**: `analysis:{game_id}`
- **TTL**: Permanent (until re-analysis requested)
- **Storage**: PostgreSQL `game_analyses` table

### **AI Insights**
- **Cache Key**: `insights:{user_id}`
- **TTL**: 7 days
- **Regeneration**: Triggered when new games are analyzed

---

## 🗃️ Database Schema

### **Users Table**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    chesscom_username VARCHAR UNIQUE NOT NULL,
    display_name VARCHAR,
    email VARCHAR,
    tier VARCHAR DEFAULT 'free', -- 'free' or 'pro'
    ai_analyses_used INT DEFAULT 0,
    ai_analyses_limit INT DEFAULT 5,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### **Games Table**
```sql
CREATE TABLE games (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    chesscom_game_id VARCHAR UNIQUE,
    pgn TEXT,
    result VARCHAR, -- 'win', 'loss', 'draw'
    time_class VARCHAR, -- 'bullet', 'blitz', 'rapid', 'daily'
    time_control VARCHAR,
    rated BOOLEAN,
    user_rating INT,
    opponent_rating INT,
    opponent_username VARCHAR,
    end_time TIMESTAMP,
    is_analyzed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### **Game Analyses Table**
```sql
CREATE TABLE game_analyses (
    id SERIAL PRIMARY KEY,
    game_id INT REFERENCES games(id) UNIQUE,
    user_acpl FLOAT,
    brilliant_moves INT,
    great_moves INT,
    best_moves INT,
    excellent_moves INT,
    good_moves INT,
    inaccuracies INT,
    mistakes INT,
    blunders INT,
    opening_acpl FLOAT,
    middlegame_acpl FLOAT,
    endgame_acpl FLOAT,
    opening_name VARCHAR,
    move_data JSONB, -- Detailed move-by-move analysis
    created_at TIMESTAMP DEFAULT NOW()
);
```

### **AI Insights Table**
```sql
CREATE TABLE ai_insights (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    insights JSONB, -- Detected patterns
    recommendations JSONB, -- Coaching advice
    youtube_videos JSONB, -- Video suggestions
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP -- Auto-regenerate after expiry
);
```

---

## 🔧 Extension Points

### **Adding New Filters**
1. Update `FilterOptions` type in `frontend/src/types/index.ts`
2. Add filter UI in `index.tsx` and `dashboard.tsx`
3. Update `apply_filters()` logic in `backend/app/services/chesscom_service.py`

### **Adding New Chess Metrics**
1. Extend `ChessAnalysisService` in `backend/app/services/chess_analysis.py`
2. Add new columns to `game_analyses` table (migration)
3. Update frontend dashboard to display new metrics

### **Adding New AI Insights**
1. Extend `AIInsightsService` pattern detection logic
2. Train or fine-tune AI model on new patterns
3. Update `ai_insights` JSONB schema
4. Update dashboard insights section

### **Adding Payment Integration**
1. Create `subscriptions` table
2. Integrate Stripe/Paddle
3. Add `SubscriptionService` to manage tier upgrades
4. Update `TierManagementService` to check subscription status

---

## 📈 Performance Considerations

- **Game Fetching**: Background job (Celery) to avoid blocking sign-in
- **Analysis**: Async queue (Redis) to handle multiple games concurrently
- **Caching**: Redis for frequently accessed data (game lists, user stats)
- **Database Indexing**: 
  - `games.user_id`, `games.end_time`, `games.is_analyzed`
  - `game_analyses.game_id`
  - `users.chesscom_username`

---

## 🧪 Testing Strategy

### **Unit Tests**
- `ChessAnalysisService`: ACPL calculation, move classification
- `TierManagementService`: Trial counter logic, tier checks
- `ChessComService`: API response parsing, filter logic

### **Integration Tests**
- Full analysis pipeline (PGN → Stockfish → AI → Database)
- User creation flow with game fetching

### **End-to-End Tests (Playwright)**
- Sign-in flow (new user)
- Dashboard with filters
- Trigger analysis and verify results
- Trial exhaustion and upgrade CTA

---

## 🚀 Future Roadmap

- [ ] Opening repertoire builder
- [ ] Tactical puzzle generator from user blunders
- [ ] Social leaderboard
- [ ] Mobile app (React Native)
- [ ] Browser extension (auto-analyze after each game)
- [ ] Coach mode (chat-based explanations)

---

**Last Updated**: November 1, 2025  
**Maintained by**: Chess Insight AI Team
