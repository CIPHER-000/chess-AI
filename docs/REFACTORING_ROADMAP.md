# 🚀 Chess Insight AI - Product Flow Refactoring Roadmap

**Started**: November 1, 2025  
**Status**: In Progress  
**Goal**: Complete product flow refinement with filtering, tier management, and testing

---

## ✅ Phase 1: Documentation & Backend Models (COMPLETED)

**Status**: ✅ DONE

**Completed**:
- [x] Created `/docs/PRODUCT_FLOW.md` - Comprehensive product flow documentation
- [x] Updated User model with tier management fields:
  - `tier` (free/pro)
  - `ai_analyses_used`
  - `ai_analyses_limit`
  - `trial_exhausted_at`
  - `total_games`
  - `analyzed_games`
- [x] Added User model properties:
  - `is_pro`
  - `can_use_ai_analysis`
  - `remaining_ai_analyses`
  - `increment_ai_usage()`
- [x] Created `TierService` in `/backend/app/services/tier_service.py`
- [x] Created database migration `/backend/alembic/versions/0002_add_tier_management.py`

**Files Changed**:
- `backend/app/models/user.py`
- `backend/app/services/tier_service.py` (new)
- `backend/alembic/versions/0002_add_tier_management.py` (new)
- `docs/PRODUCT_FLOW.md` (new)

---

## ✅ Phase 2: Backend API Updates (COMPLETED)

**Status**: ✅ DONE

**Completed Tasks**:
- [x] Update `users` API to return tier status
  - ✅ Added `/api/v1/users/{user_id}/tier-status` endpoint
  - ✅ Include tier info in user GET response (tier, ai_analyses_used, remaining_ai_analyses)
  - ✅ Added `/api/v1/users/{user_id}/upgrade-to-pro` endpoint for testing
  
- [x] Create filtering service
  - ✅ New file: `/backend/app/services/filter_service.py`
  - ✅ Support filters:
    - Game count (10, 25, 50, custom)
    - Date range (start_date, end_date)
    - Time control (bullet, blitz, rapid, daily)
    - Rated/unrated filter
  - ✅ `GameFilter` class for configuration
  - ✅ `FilterService` with apply_filters() method
  - ✅ get_filter_summary() for statistics
  
- [x] Update games fetch endpoint
  - ✅ `/api/v1/games/fetch` accepts comprehensive filter parameters
  - ✅ Apply FilterService post-fetch from Chess.com API
  - ✅ Return filter metadata in response
  - ✅ Update user.total_games count automatically
  
- [x] Update analysis endpoint
  - ✅ Check tier status before analysis
  - ✅ Increment AI usage counter if using AI layer
  - ✅ Return HTTP 403 with upgrade message when trial exhausted
  - ✅ Update user.analyzed_games count
  
- [x] Add analysis mode to analyze endpoint
  - ✅ `/api/v1/analysis/{user_id}/analyze` with `mode` parameter:
    - `"auto"` - Use AI if available, fallback to Stockfish (default)
    - `"stockfish-only"` - Just Stockfish metrics
    - `"ai-enhanced"` - Full AI insights (requires tier check)
  - ✅ Return analysis_mode and tier_info in response

**Files Created**:
- `backend/app/services/filter_service.py` (319 lines)

**Files Modified**:
- `backend/app/api/users.py` (+tier endpoints, +TierService)
- `backend/app/api/games.py` (+comprehensive filtering, +FilterService)
- `backend/app/api/analysis.py` (+tier checks, +analysis modes)

**API Endpoints Added**:
1. `GET /api/v1/users/{user_id}/tier-status` - Get tier status
2. `POST /api/v1/users/{user_id}/upgrade-to-pro` - Upgrade to Pro (testing)

**API Endpoints Enhanced**:
1. `GET /api/v1/users/{user_id}` - Now includes tier fields
2. `POST /api/v1/games/{user_id}/fetch` - Now accepts filter parameters
3. `POST /api/v1/analysis/{user_id}/analyze` - Now checks tier and modes
4. `GET /api/v1/analysis/{user_id}/summary` - Now includes tier_status

**Commit**: `e026ca9` - "feat: Phase 2 - Backend API updates with filtering and tier management"

---

## 🎨 Phase 3: Frontend Landing Page Filters (TODO)

**Status**: ⏳ PENDING

**Tasks**:
- [ ] Add filter UI to `frontend/src/pages/index.tsx`
  - Game count selector
  - Date range picker (react-datepicker)
  - Time control checkboxes
  - Rated/unrated toggle
  
- [ ] Create filter types
  - Update `frontend/src/types/index.ts` with `FilterOptions` interface
  
- [ ] Pass filters to API on user creation
  - Update `api.users.create()` to accept filters
  - Store filters in user preferences

**Files to Modify**:
- `frontend/src/pages/index.tsx`
- `frontend/src/types/index.ts`
- `frontend/src/services/api.ts`

**Dependencies**:
```bash
cd frontend
npm install react-datepicker
npm install @types/react-datepicker --save-dev
```

---

## 📊 Phase 4: Frontend Dashboard Updates (TODO)

**Status**: ⏳ PENDING

**Tasks**:
- [ ] Add tier status display to dashboard
  - Show current tier (Free/Pro)
  - Show remaining AI analyses (if free)
  - Show upgrade CTA banner when trial exhausted
  
- [ ] Add re-filtering panel
  - Reuse filter UI from landing page
  - "Apply Filters" button to refetch games
  
- [ ] Update "Analyze with AI" button logic
  - Check tier status before allowing analysis
  - Show different button text based on tier:
    - Pro: "Analyze with AI"
    - Free (trial available): "Analyze with AI (X remaining)"
    - Free (trial exhausted): "Analyze with Stockfish" (disabled AI icon)
  
- [ ] Add upgrade modal/banner
  - Trigger when user clicks analyze with no trial remaining
  - Clear benefits of Pro tier
  - "Upgrade to Pro" CTA button

**Files to Modify**:
- `frontend/src/pages/dashboard.tsx`
- `frontend/src/components/TierBanner.tsx` (new)
- `frontend/src/components/UpgradeModal.tsx` (new)
- `frontend/src/components/FilterPanel.tsx` (new)

---

## ⚙️ Phase 5: Analysis Pipeline Separation (TODO)

**Status**: ⏳ PENDING

**Tasks**:
- [ ] Update `ChessAnalysisService` to support modes
  - `analyze_stockfish_only()` - Returns only Stockfish metrics
  - `analyze_with_ai()` - Returns Stockfish + AI insights
  
- [ ] Create AI insights service (if not exists)
  - New file: `/backend/app/services/ai_insights_service.py`
  - Pattern detection logic
  - YouTube recommendation logic
  
- [ ] Update analysis endpoint to route based on tier
  ```python
  if tier_service.can_use_ai_analysis(user):
      result = await analysis_service.analyze_with_ai(game)
      tier_service.increment_ai_usage(user)
  else:
      result = await analysis_service.analyze_stockfish_only(game)
  ```

**Files to Modify**:
- `backend/app/services/chess_analysis.py`
- `backend/app/services/ai_insights_service.py` (new)
- `backend/app/api/analysis.py`

---

## 🧪 Phase 6: Testing with Playwright (TODO)

**Status**: ⏳ PENDING

**Tasks**:
- [ ] Set up Playwright in project
  ```bash
  cd frontend
  npm install -D @playwright/test
  npx playwright install
  ```
  
- [ ] Create test file structure
  - `frontend/tests/e2e/sign-in.spec.ts`
  - `frontend/tests/e2e/dashboard.spec.ts`
  - `frontend/tests/e2e/analysis-flow.spec.ts`
  - `frontend/tests/e2e/tier-limits.spec.ts`
  
- [ ] Write E2E tests:
  - **Sign-in flow**
    - New user creation
    - Existing user login
    - Filter application
    - Game fetching
  
  - **Dashboard flow**
    - Display tier status
    - Re-filtering games
    - Trigger analysis
    - View results
  
  - **Tier limits**
    - Free user uses 5 AI analyses
    - 6th analysis triggers Stockfish-only mode
    - Upgrade banner appears
  
  - **Chess.com API verification**
    - Verify all endpoints match latest docs
    - Test error handling (404, 429, etc.)

**Files to Create**:
- `frontend/playwright.config.ts` (new)
- `frontend/tests/e2e/` (new directory)

---

## 📚 Phase 7: Documentation Updates (TODO)

**Status**: ⏳ PENDING

**Tasks**:
- [ ] Update `README.md` to focus on setup only
  - Docker commands
  - Environment variables
  - Quick start guide
  - Remove product flow details (moved to PRODUCT_FLOW.md)
  
- [ ] Create API documentation
  - `/docs/API_ENDPOINTS.md`
  - Document all endpoints with examples
  - Include filter parameters
  - Include tier-specific behavior
  
- [ ] Create developer guide
  - `/docs/DEVELOPER_GUIDE.md`
  - How to add new filters
  - How to add new chess metrics
  - How to extend AI insights
  - How to add new tiers

**Files to Modify/Create**:
- `README.md`
- `docs/API_ENDPOINTS.md` (new)
- `docs/DEVELOPER_GUIDE.md` (new)

---

## 🚀 Phase 8: Database Migration & Deployment (TODO)

**Status**: ⏳ PENDING

**Tasks**:
- [ ] Run database migration
  ```bash
  docker-compose exec backend alembic upgrade head
  ```
  
- [ ] Verify migration
  - Check all columns exist
  - Test tier logic with real user
  
- [ ] Rebuild Docker containers
  ```bash
  docker-compose down
  docker-compose build
  docker-compose up -d
  ```
  
- [ ] Test full flow end-to-end
  - Create new user
  - Apply filters
  - Analyze games
  - Exhaust free trial
  - Verify Stockfish-only mode

---

## 📋 Current Status Summary

### ✅ Completed (Phase 1)
- Product flow documentation
- Backend User model with tier fields
- TierService implementation
- Database migration file

### ⏳ In Progress
- None (ready to start Phase 2)

### 🔜 Next Steps
1. **Run database migration** to apply tier management fields
2. **Update backend APIs** to support filtering and tier checks
3. **Add frontend filters** to landing page
4. **Update dashboard** with tier display and re-filtering
5. **Separate analysis pipeline** (Stockfish-only vs AI-enhanced)
6. **Write Playwright tests**
7. **Update documentation**

---

## 🎯 Estimated Timeline

| Phase | Estimated Time | Status |
|-------|---------------|--------|
| 1. Documentation & Backend Models | 2 hours | ✅ DONE |
| 2. Backend API Updates | 4 hours | ✅ DONE |
| 3. Frontend Landing Page Filters | 3 hours | ⏳ TODO |
| 4. Frontend Dashboard Updates | 4 hours | ⏳ TODO |
| 5. Analysis Pipeline Separation | 3 hours | ✅ DONE (Backend) |
| 6. Testing with Playwright | 5 hours | ⏳ TODO |
| 7. Documentation Updates | 2 hours | ⏳ TODO |
| 8. Migration & Deployment | 1 hour | ⏳ TODO |
| **Total** | **24 hours** | **38% Complete** |

---

## 🚨 Breaking Changes

**Database Schema**:
- Added columns to `users` table (requires migration)
- Existing users will default to `tier='free'`, `ai_analyses_used=0`, `ai_analyses_limit=5`

**API Changes**:
- User response will include new tier fields
- Analysis endpoint will require tier check
- Game fetch endpoint will accept filter parameters

**Frontend Changes**:
- Landing page will have filter UI
- Dashboard will show tier status and upgrade CTAs
- Analysis flow will differ based on tier

---

## 📞 Support & Questions

If you encounter issues during refactoring:
1. Check this roadmap for current progress
2. Review `/docs/PRODUCT_FLOW.md` for architecture details
3. Check git commits for implementation examples
4. Test each phase independently before moving to next

---

**Last Updated**: November 1, 2025  
**Maintainer**: Chess Insight AI Team
