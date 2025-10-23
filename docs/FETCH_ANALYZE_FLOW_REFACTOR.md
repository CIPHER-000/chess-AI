# 🔍 Fetch vs Analyze Flow - Analysis & Refactoring Plan

**Date**: October 23, 2025  
**Status**: Implementation Required  
**Chess.com API Validation**: ✅ Complete

---

## 📊 **Current Implementation Analysis**

### ✅ **Good News: Backend Already Separates Flows!**

The backend **correctly separates** fetch and analyze:

#### **1. Fetch Endpoint** (`/api/v1/games/{user_id}/fetch`)
- ✅ Fetches games from Chess.com
- ✅ Stores in database WITHOUT analyzing
- ✅ Returns: `games_added`, `games_updated`, `total_games`
- ✅ **No AI analysis triggered**

#### **2. Analyze Endpoint** (`/api/v1/analysis/{user_id}/analyze`)
- ✅ Analyzes ALREADY FETCHED games
- ✅ Runs Stockfish engine
- ✅ Computes ACPL, mistakes, blunders
- ✅ Updates graphs and insights
- ✅ **Only runs on games in database**

---

## ⚠️ **Issues Found**

### **Issue #1: Frontend Confusion**
- Homepage creates user and implicitly triggers background fetch
- No clear UI indication that fetch is happening
- User flow not explicit enough

### **Issue #2: Limited Fetch Options**
- Current: Only "last N days"
- Missing: "last N games" filter
- Chess.com API supports both but we only use one

### **Issue #3: Mixed Messaging**
- "Get Started" button name doesn't clearly indicate it's for signup + fetch
- Dashboard buttons are clear but initial flow isn't

---

## 🎯 **Chess.com API Validation**

### **Validated Endpoints** (from official docs)

#### **1. Player Profile**
```
GET https://api.chess.com/pub/player/{username}
```
✅ Currently used in: `chesscom_api.py:get_player_profile()`

#### **2. Available Archives**
```
GET https://api.chess.com/pub/player/{username}/games/archives
```
**Returns**: List of URLs like `["https://api.chess.com/pub/player/{username}/games/2025/01", ...]`

✅ Currently used in: `chesscom_api.py:get_player_games_archive_list()`

#### **3. Monthly Game Archive**
```
GET https://api.chess.com/pub/player/{username}/games/{YYYY}/{MM}
```
**Returns**: All games played in that month

✅ Currently used in: `chesscom_api.py:get_player_games_by_month()`

**Game Data Structure**:
```json
{
  "games": [
    {
      "url": "https://www.chess.com/game/live/...",
      "pgn": "[Event \"Live Chess\"]...",
      "time_control": "600",
      "end_time": 1738260000,
      "rated": true,
      "tcn": "...",
      "uuid": "...",
      "initial_setup": "...",
      "fen": "...",
      "time_class": "rapid",
      "rules": "chess",
      "white": {
        "rating": 1500,
        "result": "win",
        "@id": "https://api.chess.com/pub/player/username",
        "username": "username",
        "uuid": "..."
      },
      "black": {
        "rating": 1480,
        "result": "checkmated",
        "@id": "https://api.chess.com/pub/player/opponent",
        "username": "opponent",
        "uuid": "..."
      }
    }
  ]
}
```

#### **4. Game Result Codes**
✅ Validated from docs:
- `win`, `checkmated`, `agreed`, `repetition`, `timeout`, `resigned`
- `stalemate`, `lose`, `insufficient`, `50move`, `abandoned`
- `kingofthehill`, `threecheck`, `timevsinsufficient`, `bughousepartnerlose`

✅ Currently handled in: `games.py` lines 86-92

---

## 🔧 **Required Changes**

### **Change 1: Add "Fetch by Count" Support**

#### **Backend: Update `chesscom_api.py`**
Add new parameter to `get_recent_games()`:

```python
async def get_recent_games(
    self, 
    username: str, 
    days: Optional[int] = None,
    count: Optional[int] = None
) -> List[Dict]:
    """
    Get recent games for a player.
    
    Args:
        username: Chess.com username
        days: Get games from last N days (mutually exclusive with count)
        count: Get last N games (mutually exclusive with days)
    
    Returns:
        List of game dictionaries
    """
    if days and count:
        raise ValueError("Specify either 'days' or 'count', not both")
    
    if not days and not count:
        days = 7  # Default
    
    # Implementation...
```

#### **Backend: Update `games.py` Fetch Request Model**

```python
class GameFetchRequest(BaseModel):
    days: Optional[int] = None
    count: Optional[int] = None
    time_classes: Optional[List[str]] = None
    
    @validator('count')
    def validate_fetch_params(cls, v, values):
        if v and values.get('days'):
            raise ValueError("Specify either 'days' or 'count', not both")
        if not v and not values.get('days'):
            return None  # Will use default days=7
        return v
```

---

### **Change 2: Frontend - Explicit Two-Stage Flow**

#### **Update Homepage (`index.tsx`)**

**Current Flow**:
```
1. User enters username
2. "Get Started" button clicked
3. User created + background fetch starts (implicit)
4. Redirect to dashboard
```

**New Flow**:
```
1. User enters username
2. "Get Started" button clicked
3. User created
4. Show explicit "Fetching games..." progress
5. Display fetch results
6. "Go to Dashboard" button (explicit navigation)
```

#### **Update Dashboard (`dashboard.tsx`)**

Add clear two-stage UI:

```tsx
<div className="flex gap-4 mb-8">
  {/* Stage 1: Fetch */}
  <button
    onClick={handleFetchGames}
    disabled={isFetching}
    className="btn btn-primary"
  >
    {isFetching ? '⏳ Fetching...' : '🎮 Sync New Games'}
  </button>
  
  {/* Stage 2: Analyze */}
  <button
    onClick={() => handleAnalyzeGames()}
    disabled={isAnalyzing || !hasUnanalyzedGames}
    className="btn btn-secondary"
  >
    {isAnalyzing ? '🧠 Analyzing...' : '🔬 Analyze with AI'}
  </button>
</div>

{/* Status Indicator */}
<div className="status-card">
  <p>📊 Total Games: {totalGames}</p>
  <p>✅ Analyzed: {analyzedGames}</p>
  <p>⏳ Pending Analysis: {unanalyzedGames}</p>
</div>
```

---

### **Change 3: Enhanced Fetch Options**

#### **Frontend: Add Fetch Configuration**

```tsx
const [fetchConfig, setFetchConfig] = useState({
  mode: 'days' as 'days' | 'count',
  days: 10,
  count: 10,
  timeClasses: [] as string[]
});

const handleFetchGames = async () => {
  const request = fetchConfig.mode === 'days'
    ? { days: fetchConfig.days, time_classes: fetchConfig.timeClasses }
    : { count: fetchConfig.count, time_classes: fetchConfig.timeClasses };
    
  const result = await api.games.fetchRecent(user.id, request);
  // ...
};
```

#### **UI for Fetch Options**

```tsx
<div className="fetch-options">
  <select onChange={(e) => setFetchConfig({...fetchConfig, mode: e.target.value})}>
    <option value="days">Last N Days</option>
    <option value="count">Last N Games</option>
  </select>
  
  {fetchConfig.mode === 'days' ? (
    <input
      type="number"
      value={fetchConfig.days}
      onChange={(e) => setFetchConfig({...fetchConfig, days: +e.target.value})}
      min="1"
      max="30"
    />
  ) : (
    <input
      type="number"
      value={fetchConfig.count}
      onChange={(e) => setFetchConfig({...fetchConfig, count: +e.target.value})}
      min="1"
      max="50"
    />
  )}
  
  <select
    multiple
    onChange={(e) => setFetchConfig({
      ...fetchConfig,
      timeClasses: Array.from(e.target.selectedOptions, option => option.value)
    })}
  >
    <option value="bullet">Bullet</option>
    <option value="blitz">Blitz</option>
    <option value="rapid">Rapid</option>
    <option value="daily">Daily</option>
  </select>
</div>
```

---

## 📝 **Updated Type Definitions**

### **Backend: `games.py`**

```python
class GameFetchRequest(BaseModel):
    """Request model for fetching games from Chess.com."""
    
    days: Optional[int] = None  # Fetch games from last N days
    count: Optional[int] = None  # Fetch last N games
    time_classes: Optional[List[str]] = None  # Filter by time class
    
    @validator('count')
    def validate_mutually_exclusive(cls, v, values):
        """Ensure only one of days/count is specified."""
        if v is not None and values.get('days') is not None:
            raise ValueError("Specify either 'days' or 'count', not both")
        return v
    
    @validator('days', 'count', pre=True, always=True)
    def set_default(cls, v, values, field):
        """Set default to days=7 if neither specified."""
        if field.name == 'days' and v is None and values.get('count') is None:
            return 7
        return v


class GameFetchResponse(BaseModel):
    """Response model for fetch operation."""
    
    message: str
    games_added: int
    games_updated: int
    total_games: int
    existing_games: int  # NEW: Count of games already in database
    fetch_method: str  # NEW: "days" or "count"
    fetch_value: int  # NEW: The actual days/count used
```

### **Frontend: Update `types/index.ts`**

```typescript
export interface FetchGamesRequest {
  days?: number;  // Mutually exclusive with count
  count?: number;  // Mutually exclusive with days
  time_classes?: string[];
}

export interface FetchGamesResponse {
  message: string;
  games_added: number;
  games_updated: number;
  total_games: number;
  existing_games: number;
  fetch_method: 'days' | 'count';
  fetch_value: number;
}
```

---

## 🧪 **Testing Plan with Playwright MCP**

### **Test 1: Fetch-Only Flow**
```typescript
// Navigate to homepage
await page.goto('http://localhost:3001');

// Enter username
await page.fill('input[name="chesscom_username"]', 'gh_wilder');
await page.click('button:has-text("Get Started")');

// Wait for fetch to complete
await page.waitForSelector('text=games fetched');

// Verify NO analysis has run yet
const analysisStatus = await page.textContent('.analysis-status');
expect(analysisStatus).toContain('0 analyzed');

// Verify games are displayed
const gamesList = await page.locator('.games-list > *').count();
expect(gamesList).toBeGreaterThan(0);
```

### **Test 2: Analyze-Only Flow**
```typescript
// Assume games already fetched
await page.goto('http://localhost:3001/dashboard?username=gh_wilder');

// Click analyze button
await page.click('button:has-text("Analyze with AI")');

// Wait for analysis to start
await page.waitForSelector('text=Analyzing');

// Wait for completion
await page.waitForSelector('text=Analysis complete', { timeout: 60000 });

// Verify graphs updated
const acplValue = await page.textContent('.acpl-stat');
expect(acplValue).not.toBe('--');
```

### **Test 3: Fetch Options**
```typescript
// Test "Last 10 days"
await page.selectOption('select[name="fetch-mode"]', 'days');
await page.fill('input[name="fetch-value"]', '10');
await page.click('button:has-text("Sync Games")');
await page.waitForSelector('text=from last 10 days');

// Test "Last 10 games"
await page.selectOption('select[name="fetch-mode"]', 'count');
await page.fill('input[name="fetch-value"]', '10');
await page.click('button:has-text("Sync Games")');
await page.waitForSelector('text=10 games fetched');
```

---

## 📊 **Expected User Experience**

### **Scenario 1: New User**

```
1. Homepage → Enter "gh_wilder" → Click "Get Started"
2. ✅ User created
3. ⏳ "Fetching your recent games from Chess.com..."
4. ✅ "Found 15 games from the last 7 days"
5. 📋 Display game list:
   - vs Magnus_Carlsen | Rapid | Loss | Jan 20
   - vs Hikaru | Blitz | Win | Jan 19
   - ...
6. 🔘 "Go to Dashboard" button (explicit)
7. Dashboard shows:
   - 📊 15 games fetched
   - ⏳ 15 games pending analysis
   - 🔬 "Analyze with AI" button (enabled)
```

### **Scenario 2: Returning User - Analyze New Games**

```
1. Dashboard → User has 15 fetched, 0 analyzed
2. Click "🔬 Analyze with AI"
3. ⏳ "Analyzing 15 games..."
4. ✅ "Analysis complete!"
5. 📈 Graphs populate:
   - Average ACPL: 45
   - Mistakes: 12
   - Blunders: 3
   - Opening Performance: ...
6. 🧠 AI Coach Insights appear
```

### **Scenario 3: Sync More Games**

```
1. Dashboard → User has 15 fetched, 15 analyzed
2. Click "🎮 Sync New Games"
3. ⏳ "Checking for new games..."
4. ✅ "5 new games found!"
5. Status updates:
   - 📊 20 total games
   - ✅ 15 analyzed
   - ⏳ 5 pending analysis
6. 🔬 "Analyze with AI" button (enabled again)
```

---

## ✅ **Implementation Checklist**

### **Phase 1: Backend Enhancements** ⏳
- [ ] Add `count` parameter to `chesscom_api.get_recent_games()`
- [ ] Update `GameFetchRequest` with validation
- [ ] Update `GameFetchResponse` with new fields
- [ ] Test fetch by days
- [ ] Test fetch by count
- [ ] Validate against Chess.com API docs

### **Phase 2: Frontend Refactor** ⏳
- [ ] Update homepage flow (explicit fetch status)
- [ ] Add fetch configuration UI
- [ ] Update dashboard with two-stage buttons
- [ ] Add status indicators (fetched/analyzed/pending)
- [ ] Update TypeScript types
- [ ] Improve loading states

### **Phase 3: Testing** ⏳
- [ ] Write Playwright MCP tests for fetch flow
- [ ] Write Playwright MCP tests for analyze flow
- [ ] Write Playwright MCP tests for combined flow
- [ ] Test edge cases (no games, all analyzed, errors)

### **Phase 4: Documentation** ⏳
- [ ] Update API documentation
- [ ] Update user guide
- [ ] Create flow diagrams
- [ ] Document Chess.com API validation

---

## 🎯 **Success Criteria**

1. ✅ User can fetch games WITHOUT analyzing
2. ✅ User can analyze ALREADY FETCHED games
3. ✅ Clear visual separation of two stages
4. ✅ Fetch supports both "days" and "count"
5. ✅ All flows tested with Playwright MCP
6. ✅ Chess.com API usage validated against official docs
7. ✅ Zero confusion about which button does what

---

## 📚 **Chess.com API Compliance Summary**

| Endpoint | Purpose | Status | Implementation |
|----------|---------|--------|----------------|
| `/player/{username}` | Get profile | ✅ Compliant | `chesscom_api.py:89` |
| `/player/{username}/stats` | Get ratings | ✅ Compliant | `chesscom_api.py:107` |
| `/player/{username}/games/archives` | List archives | ✅ Compliant | `chesscom_api.py:113` |
| `/player/{username}/games/{Y}/{M}` | Monthly games | ✅ Compliant | `chesscom_api.py:119` |
| Rate Limiting | 300/min | ✅ Handled | `chesscom_api.py:22` |
| Case Normalization | Lowercase | ✅ Handled | `chesscom_api.py:103` |
| Result Codes | All codes | ✅ Handled | `games.py:86-92` |
| PGN Parsing | Standard | ✅ Handled | `chesscom_api.py:193` |

---

**All Chess.com API usage is validated and compliant with official documentation!** ✅

---

*This document serves as the implementation blueprint for separating fetch and analyze flows while maintaining Chess.com API compliance.*
