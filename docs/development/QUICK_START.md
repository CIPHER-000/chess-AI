# ⚡ Quick Start - Chess Insight AI

**Get up and running in 30 minutes!**

---

## ✅ Security Update Complete

### OpenAI API Key Status

✅ **RESOLVED**: API key has been rotated and secured.

### 🆓 OpenRouter Setup (Recommended for Development)

For cost-effective development, we've integrated **OpenRouter** with free tier models:

1. Visit: https://openrouter.ai/keys
2. Sign up and generate free API key
3. Save it for Step 3 below

**Free Models Available:**
- `google/gemma-2-9b-it:free`
- `meta-llama/llama-3.1-8b-instruct:free`
- `mistralai/mistral-7b-instruct:free`

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
# 5. OPENROUTER_API_KEY (your OpenRouter key - FREE)
# 6. MODEL_PROVIDER=openrouter (use free models for dev)
# 7. OPENAI_API_KEY (optional - for production only)
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
