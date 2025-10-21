# 🐳 Docker Testing Instructions

## Quick Test (Recommended)

```bash
# Clean everything
docker-compose down -v
docker system prune -f

# Rebuild backend only (frontend optional)
docker-compose build --no-cache backend

# Start backend + dependencies
docker-compose up backend redis

# Expected output:
# ✅ "Successfully installed supabase-2.3.0 supabase-auth-X.X.X"
# ✅ "INFO: Application startup complete"
# ✅ "Uvicorn running on http://0.0.0.0:8000"
```

## Full Test (With Frontend)

```bash
# Clean everything
docker-compose down -v

# Rebuild all services
docker-compose build --no-cache

# Start backend + frontend
docker-compose up backend frontend redis

# Test in browser:
# 1. Go to http://localhost:3000
# 2. Enter username: "GH_Wilder" (mixed case)
# 3. Should create/load user successfully
# 4. Dashboard should display game data
```

## Verification Checklist

### Backend
- [ ] Container builds without errors
- [ ] No "supabase-auth==2.12.4" error
- [ ] Logs show: "INFO: Application startup complete"
- [ ] API responds: `curl http://localhost:8000/api/v1/health`

### Frontend
- [ ] Can enter mixed-case username: "GH_Wilder"
- [ ] User lookup succeeds (normalized to "gh_wilder")
- [ ] Dashboard loads without infinite loading
- [ ] Game data displays correctly

## Troubleshooting

### Issue: Backend won't start
```bash
# Check logs
docker-compose logs backend

# If dependency errors:
docker-compose build --no-cache backend
```

### Issue: Frontend infinite loading
```bash
# Check browser console
# Should see: GET /api/v1/users/by-username/gh_wilder → 200

# If 404:
# Check that frontend normalization is applied
cat frontend/src/services/api.ts | grep toLowerCase
```

## Clean Slate

```bash
# Nuclear option - reset everything
docker-compose down -v
docker system prune -af --volumes
docker-compose build --no-cache
docker-compose up
```
