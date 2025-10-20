# 🚀 Implementation Plan - Chess Insight AI (Supabase Migration)

**Status**: In Progress  
**Last Updated**: 2025-10-20

---

## ✅ Completed Steps

### 1. Security Fixes ✓
- [x] Removed hardcoded OpenAI API key from MCP configuration
- [x] Updated to environment variable reference (`${OPENAI_API_KEY}`)
- [x] Created `SECURITY_NOTICE.md` with key rotation instructions
- [x] Added `OPENAI_API_KEY` to `.env.example`

**Files Modified:**
- `.windsurf/mcp/gpt5.mcp.json`
- `.env.example`
- `SECURITY_NOTICE.md` (new)

**ACTION REQUIRED**: Rotate the exposed OpenAI API key immediately!

---

### 2. Git Repository Initialization ✓
- [x] Initialized git repository
- [x] Added all files to version control
- [x] Created initial commit

**Command Run:**
```bash
git init
git add .
git commit -m "Initial commit: Chess Insight AI with Supabase migration"
```

---

### 3. Supabase Configuration ✓
- [x] Added Supabase client libraries to `requirements.txt`
- [x] Created `supabase_client.py` for client management
- [x] Created `auth_service.py` for authentication
- [x] Created `auth_middleware.py` for request authentication
- [x] Updated `config.py` with Supabase settings
- [x] Updated `.env.example` with all Supabase variables

**New Files:**
- `backend/app/core/supabase_client.py`
- `backend/app/services/auth_service.py`
- `backend/app/middleware/auth_middleware.py`
- `SUPABASE_SETUP.md` (comprehensive guide)

---

### 4. Testing Infrastructure ✓
- [x] Created `conftest.py` with pytest fixtures
- [x] Created `pytest.ini` with test configuration
- [x] Added test for authentication (`test_auth.py`)
- [x] Added test for user API (`test_api_users.py`)
- [x] Added test for chess analyzer (`test_chess_analyzer.py`)

**New Files:**
- `backend/conftest.py`
- `backend/pytest.ini`
- `backend/tests/test_auth.py`
- `backend/tests/test_api_users.py`
- `backend/tests/test_chess_analyzer.py`

---

### 5. Docker Compose Update ✓
- [x] Removed PostgreSQL service
- [x] Updated backend to use Supabase via env file
- [x] Updated Celery worker configuration
- [x] Removed PostgreSQL volume

**File Modified:**
- `docker-compose.yml`

---

## 🔄 Next Steps (In Order)

### Step 6: Create Supabase Project
**Priority**: HIGH  
**Estimated Time**: 10 minutes

1. Go to https://supabase.com and create account
2. Create new project: `chess-insight-ai`
3. Copy API keys and database password
4. Save credentials securely

**Resources**: See `SUPABASE_SETUP.md` Step 1-2

---

### Step 7: Set Up Supabase Database Schema
**Priority**: HIGH  
**Estimated Time**: 15 minutes

1. Open Supabase SQL Editor
2. Run the SQL schema from `SUPABASE_SETUP.md` Step 3
3. Enable Row Level Security (RLS)
4. Create storage bucket for files

**Tables to Create:**
- `users`
- `games`
- `user_insights`

**Resources**: See `SUPABASE_SETUP.md` Step 3-5

---

### Step 8: Update Local Environment
**Priority**: HIGH  
**Estimated Time**: 5 minutes

1. Create `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```

2. Fill in Supabase credentials:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   SUPABASE_DB_PASSWORD=your-db-password
   OPENAI_API_KEY=your-new-key (after rotation!)
   ```

3. Verify `.env` is in `.gitignore` ✓

---

### Step 9: Update Backend Models for Supabase
**Priority**: MEDIUM  
**Estimated Time**: 20 minutes

**Tasks:**
- [ ] Update `User` model to include `supabase_user_id`
- [ ] Add foreign key relationship to `auth.users`
- [ ] Update API endpoints to use Supabase auth
- [ ] Remove old PostgreSQL-specific code

**Files to Modify:**
- `backend/app/models/user.py`
- `backend/app/api/users.py`
- `backend/app/api/games.py`

---

### Step 10: Integrate Authentication in API Routes
**Priority**: MEDIUM  
**Estimated Time**: 30 minutes

**Tasks:**
- [ ] Add auth middleware to protected endpoints
- [ ] Create `/auth/register` endpoint
- [ ] Create `/auth/login` endpoint
- [ ] Create `/auth/logout` endpoint
- [ ] Add token refresh endpoint
- [ ] Update existing endpoints to require authentication

**New Endpoints:**
```
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/logout
POST /api/v1/auth/refresh
GET  /api/v1/auth/me
```

---

### Step 11: Test Installation and Run Tests
**Priority**: MEDIUM  
**Estimated Time**: 15 minutes

1. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. Run tests:
   ```bash
   pytest -v
   ```

3. Check coverage:
   ```bash
   pytest --cov=app --cov-report=html
   ```

---

### Step 12: Start Development Environment
**Priority**: MEDIUM  
**Estimated Time**: 10 minutes

1. Start services:
   ```bash
   docker-compose up --build
   ```

2. Verify services:
   - Backend: http://localhost:8000
   - API Docs: http://localhost:8000/api/v1/docs
   - Health: http://localhost:8000/health

3. Test Supabase connection:
   ```python
   from app.core.supabase_client import get_supabase
   supabase = get_supabase()
   print("✅ Connected!")
   ```

---

### Step 13: Update Deployment Configuration
**Priority**: LOW  
**Estimated Time**: 20 minutes

**Tasks:**
- [ ] Update `render.yaml` to remove PostgreSQL
- [ ] Add Supabase environment variables to Render
- [ ] Update build commands
- [ ] Update `DEPLOY_RENDER.md` documentation

---

### Step 14: Frontend Authentication Integration
**Priority**: LOW  
**Estimated Time**: 1-2 hours

**Tasks:**
- [ ] Install Supabase JS client in frontend
- [ ] Create auth context/hooks
- [ ] Add login/register pages
- [ ] Add protected route wrapper
- [ ] Update API client to include auth headers

---

### Step 15: Add More Tests
**Priority**: MEDIUM  
**Estimated Time**: 2-3 hours

**Test Coverage Needed:**
- [ ] Game fetching and storage
- [ ] Chess analysis pipeline
- [ ] Insights generation
- [ ] API endpoint integration tests
- [ ] Authentication flow end-to-end

**Target Coverage**: 70%+ (configured in `pytest.ini`)

---

## 🎯 Critical Path (Do First)

1. **🔴 Rotate OpenAI API key** (5 min) - SECURITY
2. **Create Supabase project** (10 min)
3. **Set up database schema** (15 min)
4. **Update local .env** (5 min)
5. **Test basic connectivity** (10 min)

Total time for critical path: **~45 minutes**

---

## 📊 Progress Tracker

| Phase | Status | Progress |
|-------|--------|----------|
| Security Fixes | ✅ Complete | 100% |
| Git Setup | ✅ Complete | 100% |
| Supabase Config | ✅ Complete | 100% |
| Testing Infrastructure | ✅ Complete | 100% |
| Docker Update | ✅ Complete | 100% |
| Supabase Project Setup | ⏳ Pending | 0% |
| Database Schema | ⏳ Pending | 0% |
| Model Updates | ⏳ Pending | 0% |
| Auth Integration | 🟡 Partial | 40% |
| Testing | 🟡 Partial | 30% |
| Deployment | ⏳ Pending | 0% |

**Overall Progress**: 58%

---

## 🚨 Known Issues

1. **Exposed API Key** - Must rotate immediately
2. **No Active Auth** - User model has OAuth fields but no implementation (now being added)
3. **Empty Test Directory** - Now populated with basic tests
4. **Frontend Components Missing** - To be addressed in Phase 5

---

## 📚 Documentation Created

- `SECURITY_NOTICE.md` - Critical security issue documentation
- `SUPABASE_SETUP.md` - Complete Supabase setup guide
- `IMPLEMENTATION_PLAN.md` - This file

---

## 🎓 Learning Resources

- [Supabase Python Docs](https://supabase.com/docs/reference/python/introduction)
- [FastAPI Authentication](https://fastapi.tiangolo.com/tutorial/security/)
- [Pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)
- [Docker Compose Env Files](https://docs.docker.com/compose/environment-variables/)

---

## 💡 Tips

- Use `service_role` key in backend for admin operations
- Use `anon` key in frontend for client operations
- Enable RLS on all tables for data security
- Store sensitive files in Supabase Storage, not local filesystem
- Use Supabase Auth triggers for user onboarding

---

**Next Action**: Follow `SUPABASE_SETUP.md` to create your Supabase project and database!
