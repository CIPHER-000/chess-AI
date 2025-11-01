# 🚀 Supabase Schema Migration Guide

## Current Status

Your Chess Insight AI app is currently using **LOCAL PostgreSQL (Docker)**, not Supabase.

```
Current:  postgresql://chessai:chessai@postgres:5432/chessai (LOCAL)
Supabase: https://kkgdxjypcvvrnqtocazc.supabase.co (EMPTY)
```

## What Needs to Be Done

1. ✅ **Schema SQL file created** → `backend/supabase_schema.sql`
2. ⏳ **Run schema on Supabase** → You need to do this manually
3. ⏳ **Update DATABASE_URL** → Point to Supabase
4. ⏳ **Test connection** → Verify everything works

---

## Step 1: Run Schema on Supabase 📊

### Option A: Using Supabase Dashboard (Recommended)

1. Go to your Supabase dashboard: https://supabase.com/dashboard/project/kkgdxjypcvvrnqtocazc

2. Click **SQL Editor** in the left sidebar

3. Click **New Query**

4. Copy the entire contents of `backend/supabase_schema.sql` and paste it into the editor

5. Click **Run** (or press Ctrl+Enter)

6. You should see: ✅ "Schema migration completed successfully!"

7. Go to **Database** → **Tables** to verify:
   - `users` table (with tier management fields)
   - `games` table
   - `game_analyses` table
   - `user_insights` table

### Option B: Using Supabase CLI (Advanced)

```bash
# Install Supabase CLI
npm install -g supabase

# Link to your project
supabase link --project-ref kkgdxjypcvvrnqtocazc

# Run migration
supabase db push

# Or execute SQL directly
psql "postgresql://postgres.[YOUR_PASSWORD]@db.kkgdxjypcvvrnqtocazc.supabase.co:5432/postgres" < backend/supabase_schema.sql
```

---

## Step 2: Get Supabase Database URL 🔗

You need the **direct PostgreSQL connection string** from Supabase:

1. Go to: https://supabase.com/dashboard/project/kkgdxjypcvvrnqtocazc/settings/database

2. Scroll to **Connection String** section

3. Select **URI** tab

4. Copy the connection string (it looks like):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.kkgdxjypcvvrnqtocazc.supabase.co:5432/postgres
   ```

5. Replace `[YOUR-PASSWORD]` with your actual database password

---

## Step 3: Update Your .env File ⚙️

Open `C:\Users\HP\chess-insight-ai\.env` and replace:

### OLD (Local PostgreSQL):
```env
DATABASE_URL=postgresql://chessai:chessai@postgres:5432/chessai
POSTGRES_SERVER=postgres
POSTGRES_USER=chessai
POSTGRES_PASSWORD=chessai
POSTGRES_DB=chessai
POSTGRES_PORT=5432
```

### NEW (Supabase):
```env
# Supabase PostgreSQL Database
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.kkgdxjypcvvrnqtocazc.supabase.co:5432/postgres?sslmode=require

# Keep these for reference
POSTGRES_SERVER=db.kkgdxjypcvvrnqtocazc.supabase.co
POSTGRES_USER=postgres
POSTGRES_PASSWORD=[YOUR-PASSWORD]
POSTGRES_DB=postgres
POSTGRES_PORT=5432
```

**Important**: 
- Replace `[YOUR-PASSWORD]` with your actual Supabase database password
- Add `?sslmode=require` at the end (Supabase requires SSL)

---

## Step 4: Update Docker Compose (Optional) 🐳

If you want to keep using local PostgreSQL for development and Supabase for production:

Create a `.env.local` file:
```env
# Local development
DATABASE_URL=postgresql://chessai:chessai@postgres:5432/chessai
```

Create a `.env.production` file:
```env
# Production (Supabase)
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.kkgdxjypcvvrnqtocazc.supabase.co:5432/postgres?sslmode=require
```

---

## Step 5: Restart Backend & Test 🧪

### Restart the backend container:
```powershell
cd C:\Users\HP\chess-insight-ai
docker-compose down
docker-compose up -d backend
```

### Test the connection:
```powershell
# Check logs
docker logs chess-insight-backend

# Test API
curl http://localhost:8000/api/v1/users/

# Should return [] (empty list) since Supabase DB is fresh
```

---

## Step 6: Migrate Existing Data (Optional) 📦

If you have existing users/games in local PostgreSQL and want to move them to Supabase:

### Export from local:
```powershell
docker exec chess-insight-postgres pg_dump -U chessai -d chessai -t users -t games -t game_analyses -t user_insights --data-only > local_data.sql
```

### Import to Supabase:
1. Open `local_data.sql`
2. Copy contents
3. Go to Supabase SQL Editor
4. Paste and Run

---

## Verification Checklist ✅

After migration, verify:

- [ ] Tables visible in Supabase Dashboard
- [ ] Backend connects to Supabase (check logs)
- [ ] Can create new user via API
- [ ] Can fetch games
- [ ] Tier management fields exist (`tier`, `ai_analyses_used`, etc.)
- [ ] RLS policies are enabled

---

## Troubleshooting 🔧

### Error: "password authentication failed"
- Check your DATABASE_URL password
- Get correct password from Supabase dashboard

### Error: "SSL connection required"
- Add `?sslmode=require` to DATABASE_URL

### Error: "table does not exist"
- Schema migration didn't run
- Re-run `backend/supabase_schema.sql` in Supabase SQL Editor

### Tables not showing in Supabase Dashboard
- Refresh the page
- Check **Database** → **Tables** in left sidebar
- Verify schema migration completed successfully

---

## What's in the Schema? 📋

The `supabase_schema.sql` file creates:

### 1. **users** table
- Basic user info (username, email)
- Chess.com connection status
- **Tier management** (tier, ai_analyses_used, ai_analyses_limit)
- Game statistics (total_games, analyzed_games)

### 2. **games** table
- Chess.com game data
- PGN, FEN, time controls
- Results and ratings
- Analysis status

### 3. **game_analyses** table
- Stockfish analysis results
- Move classifications (blunders, mistakes, etc.)
- ACPL by game phase
- Opening information

### 4. **user_insights** table
- AI-generated coaching insights
- Recommendations
- Performance trends

---

## Need Help?

If you encounter issues:
1. Check Supabase dashboard logs
2. Check backend container logs: `docker logs chess-insight-backend`
3. Verify DATABASE_URL is correct
4. Ensure schema migration completed successfully

---

**Ready to migrate? Follow the steps above!** 🚀
