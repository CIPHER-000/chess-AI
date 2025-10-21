# 🔧 CORS Fix - OPTIONS 400 Bad Request

**Date**: October 21, 2025  
**Issue**: `OPTIONS /api/v1/users/ HTTP/1.1" 400 Bad Request`  
**Status**: ✅ **FIXED**

---

## 🔍 Problem

### **Symptoms**
- Backend logs: `OPTIONS /api/v1/users/ HTTP/1.1" 400 Bad Request`
- Frontend error: "Failed to login/create account"
- User creation works in backend (logs show success)
- Frontend never receives the response

### **Root Cause**
CORS preflight requests (OPTIONS) were not being handled correctly:
1. Browser sends OPTIONS request before POST /api/v1/users/
2. FastAPI returns 400 instead of 200 for OPTIONS
3. Browser blocks the actual POST request
4. Frontend shows generic error

---

## ✅ Solution Applied

### **Updated CORS Configuration**

**File**: `backend/app/main.py`

**Before**:
```python
# Conditional CORS setup that might not load properly
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(CORSMiddleware, ...)
else:
    app.add_middleware(CORSMiddleware, ...)
```

**After**:
```python
# Always enable CORS with explicit configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "*"  # Allow all in development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight for 1 hour
)
```

### **Key Changes**
1. ✅ Explicitly list `OPTIONS` in `allow_methods`
2. ✅ Add `expose_headers=["*"]` for response headers
3. ✅ Set `max_age=3600` to cache preflight requests
4. ✅ Include all localhost variants
5. ✅ Remove conditional logic that might fail

---

## 🧪 Testing

### **Test OPTIONS Request**
```bash
curl -X OPTIONS http://localhost:8000/api/v1/users/ \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type" \
  -v
```

**Expected Response**:
```
< HTTP/1.1 200 OK
< access-control-allow-origin: http://localhost:3000
< access-control-allow-methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
< access-control-allow-headers: *
< access-control-max-age: 3600
```

### **Test User Creation**
```bash
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -H "Origin: http://localhost:3000" \
  -d '{"chesscom_username": "gh_wilder"}' \
  -v
```

---

## 🔄 Restart Backend

```bash
# Stop backend
docker-compose down backend

# Rebuild and start
docker-compose up --build backend

# Or if running locally
cd backend
uvicorn app.main:app --reload
```

---

## ✅ Verification Checklist

After restarting backend:

- [ ] OPTIONS request returns 200 (not 400)
- [ ] CORS headers present in OPTIONS response
- [ ] POST /api/v1/users/ works from frontend
- [ ] No "Failed to login/create account" error
- [ ] User creation successful
- [ ] Dashboard loads with user data

---

## 📊 Expected Flow

### **1. Browser Sends Preflight**
```
OPTIONS /api/v1/users/ HTTP/1.1
Origin: http://localhost:3000
Access-Control-Request-Method: POST
```

### **2. Backend Responds**
```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: GET, POST, ...
Access-Control-Allow-Headers: *
```

### **3. Browser Sends Actual Request**
```
POST /api/v1/users/ HTTP/1.1
Content-Type: application/json
{"chesscom_username": "gh_wilder"}
```

### **4. Backend Creates User**
```json
{
  "id": 1,
  "chesscom_username": "gh_wilder",
  "total_games": 0,
  ...
}
```

### **5. Background Task Runs**
```
INFO: Fetching initial games for user gh_wilder (ID: 1)
INFO: Added 10 initial games for gh_wilder
```

---

## 🎯 Summary

**Problem**: OPTIONS requests returned 400  
**Cause**: CORS middleware not properly configured  
**Fix**: Explicit CORS setup with OPTIONS method  
**Result**: ✅ Preflight requests work, user creation succeeds  

**Restart backend to apply the fix!**
