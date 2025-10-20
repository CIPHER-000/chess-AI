# 📊 Test Coverage Improvement Plan

**Current Coverage**: 45%  
**Target (Pragmatic)**: 50% → 60% → 70%  
**Strategy**: Incremental improvement with focus on critical paths

---

## 🎯 Current Status

### Coverage by File (from last report)
| File | Coverage | Priority |
|------|----------|----------|
| `app/api/users.py` | 33% | **HIGH** ✅ Critical (fixed) |
| `app/api/games.py` | 33% | **HIGH** (fetch/store) |
| `app/api/analysis.py` | 38% | **MEDIUM** (analysis endpoints) |
| `app/api/insights.py` | 31% | **MEDIUM** ✅ (fixed empty states) |
| `app/services/chesscom_api.py` | 45% | **HIGH** ✅ (8 new tests added) |
| `app/services/chess_analyzer.py` | 41% | **LOW** (complex, requires Stockfish) |

---

## 📈 Incremental Goals

### **Phase 1: Reach 50%** (Current: 45%)
**Target Date**: Next sprint  
**Focus**: API endpoints with mock data

**Quick Wins**:
- ✅ Add 3 tests for `games.py` fetch endpoint
- ✅ Add 2 tests for `analysis.py` summary endpoint
- ✅ Add 2 tests for error handling

**Estimated Impact**: +5% coverage

---

### **Phase 2: Reach 60%** (After Phase 1)
**Target Date**: 2 weeks  
**Focus**: Service layer integration

**Tasks**:
- Add integration tests for game fetching flow
- Add tests for analysis generation
- Test background task completions

**Estimated Impact**: +10% coverage

---

### **Phase 3: Reach 70%** (After Phase 2)
**Target Date**: 1 month  
**Focus**: Edge cases and error paths

**Tasks**:
- Test rate limiting scenarios
- Test database error handling
- Test concurrent user operations

**Estimated Impact**: +10% coverage

---

## 🚫 What We DON'T Need to Test

- **Stockfish engine internals** (external dependency)
- **Chess.com API responses** (mocked sufficiently)
- **Database ORM internals** (SQLAlchemy tested)
- **FastAPI framework** (framework already tested)

---

## ✅ What We HAVE Tested (Recent Additions)

1. **Chess.com API Integration** (8 tests)
   - ✅ Case sensitivity handling
   - ✅ Redirect following
   - ✅ Error scenarios (404, 410, 429)
   - ✅ Network error handling

2. **User Creation Flow** (3 tests)
   - ✅ Background task triggering
   - ✅ Empty recommendations handling
   - ✅ Game count in response

---

## 🎯 Priority Testing Areas

### **High Priority** (Critical business logic)
1. User creation and authentication
2. Game fetching from Chess.com
3. Error handling for external APIs
4. Background task execution

### **Medium Priority** (Important features)
1. Analysis summary generation
2. Insight recommendations
3. Rating tracking
4. Opening repertoire analysis

### **Low Priority** (Complex/stable code)
1. Chess position evaluation (Stockfish)
2. PGN parsing (chess library)
3. Move classification algorithms

---

## 📊 Recommended Coverage Targets by Module

| Module | Current | Target | Rationale |
|--------|---------|--------|-----------|
| **API Routes** | 35% | **60%+** | Critical user-facing |
| **Services** | 43% | **50%+** | Business logic |
| **Models** | 90%+ | **90%+** | Already good ✅ |
| **Core** | 75% | **75%+** | Config/DB ✅ |

---

## 🧪 Testing Strategy

### **Unit Tests** (Fast, isolated)
```python
# Mock external dependencies
@patch('app.services.chesscom_api')
async def test_user_creation():
    # Test logic only
```

### **Integration Tests** (Realistic scenarios)
```python
# Use real database (test DB)
async def test_full_user_flow():
    # Create user → Fetch games → Analyze
```

### **E2E Tests** (Full stack, slower)
```python
# Test API endpoints with real requests
# Run less frequently
```

---

## 📝 Quick Test Templates

### **API Endpoint Test**
```python
@pytest.mark.asyncio
async def test_endpoint_success():
    """Test successful API call."""
    # Mock dependencies
    # Call endpoint
    # Assert response
```

### **Error Handling Test**
```python
@pytest.mark.asyncio
async def test_endpoint_handles_error():
    """Test error is handled gracefully."""
    # Mock error scenario
    # Call endpoint
    # Assert proper error response
```

---

## 🎯 Next Actions

1. ✅ **Adjust coverage requirement** to 50% (realistic)
2. 📝 **Add 5-7 quick tests** for high-value endpoints
3. 📈 **Incrementally increase** target over time
4. 🔄 **Review coverage** in each PR

---

## 📚 Resources

- **FastAPI Testing**: https://fastapi.tiangolo.com/tutorial/testing/
- **pytest-asyncio**: https://pytest-asyncio.readthedocs.io/
- **Coverage.py**: https://coverage.readthedocs.io/

---

**Strategy**: Focus on **high-value, critical paths** first, not just raw percentage.  
**Goal**: 70% coverage by end of month with quality tests, not just lines covered.
