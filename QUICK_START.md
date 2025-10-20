# ⚡ Quick Start - Chess Insight AI

**Get up and running in 30 minutes!**

---

## 🔥 Critical First Step

### Rotate Your OpenAI API Key (5 min)

Your API key was exposed in git. **You must rotate it immediately:**

1. Visit: https://platform.openai.com/api-keys
2. Revoke key: `sk-proj-w3nSFuFg5yeFMjzB3ii...`
3. Generate new key
4. Save it for Step 3 below

---

## 🚀 Setup Steps

### 1️⃣ Create Supabase Project (10 min)

```bash
# Go to: https://supabase.com
# Click: New Project
# Name: chess-insight-ai
# Database Password: Generate and SAVE IT
# Region: Choose closest
# Plan: Free
```

**Wait 1-2 minutes for project creation**

---

### 2️⃣ Set Up Database (15 min)

1. Open your Supabase dashboard
2. Go to **SQL Editor**
3. Open `SUPABASE_SETUP.md` in this project
4. Copy SQL from **Step 3** (tables) → Execute
5. Copy SQL from **Step 4** (RLS policies) → Execute
6. Go to **Storage** → Create bucket: `chess-insight-files`

---

### 3️⃣ Configure Environment (5 min)

```powershell
# Create .env file
cd C:\Users\HP\chess-insight-ai
cp .env.example .env

# Edit .env and fill in:
# 1. SUPABASE_URL (from Supabase → Settings → API)
# 2. SUPABASE_ANON_KEY (from Supabase → Settings → API)
# 3. SUPABASE_SERVICE_ROLE_KEY (from Supabase → Settings → API)
# 4. SUPABASE_DB_PASSWORD (from Supabase → Settings → Database)
# 5. OPENAI_API_KEY (your NEW rotated key)
```

---

### 4️⃣ Install & Run (5 min)

```powershell
# Install dependencies
cd backend
pip install -r requirements.txt

# Run tests
pytest -v

# Start server
cd ..
docker-compose up --build
```

**Access:**
- API: http://localhost:8000
- Docs: http://localhost:8000/api/v1/docs

---

## ✅ Verify Everything Works

```bash
# Test Supabase connection
curl http://localhost:8000/health

# Test API docs
# Open: http://localhost:8000/api/v1/docs
```

---

## 📚 Full Documentation

- **Security**: `SECURITY_NOTICE.md`
- **Supabase Setup**: `SUPABASE_SETUP.md` (detailed guide)
- **Implementation Plan**: `IMPLEMENTATION_PLAN.md`
- **Migration Summary**: `README_MIGRATION.md`

---

## 🆘 Need Help?

**Issue**: Can't connect to Supabase  
→ Check `.env` file has correct URL and keys

**Issue**: Tests failing  
→ Run `pip install -r requirements.txt` again

**Issue**: Docker errors  
→ Make sure `.env` file exists in project root

---

**🎉 That's it! You're ready to build!**
