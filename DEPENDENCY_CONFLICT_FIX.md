# 🔧 Dependency Conflict Fix

## Issue
Docker build failed with dependency conflict:

```
ERROR: Cannot install -r requirements.txt (line 7) and httpx==0.25.2 
because these package versions have conflicting dependencies.

The conflict is caused by:
    The user requested httpx==0.25.2  
    supabase 2.3.0 depends on httpx<0.25.0 and >=0.24.0
```

## Root Cause
- **requirements.txt**: `httpx==0.25.2`
- **supabase==2.3.0 requires**: `httpx<0.25.0 and >=0.24.0`

Version 0.25.2 is **too new** for supabase 2.3.0.

## Fix Applied
```diff
# requirements.txt
- httpx==0.25.2
+ httpx==0.24.1  # Compatible with supabase 2.3.0 (requires <0.25.0)
```

## Why 0.24.1?
- Within supabase's range: `>=0.24.0 and <0.25.0` ✅
- Latest stable version in that range
- Maintains security and bug fixes

## Related Fixes (This Session)
1. ✅ Removed invalid `supabase-auth==2.12.4`
2. ✅ Downgraded `httpx==0.25.2` → `httpx==0.24.1`
3. ✅ Added frontend username normalization

## Testing
```bash
# Rebuild with fixed dependencies
docker-compose build --no-cache backend

# Expected: Build succeeds without conflicts
```

## Verification
- [ ] Docker build completes successfully
- [ ] No dependency conflict errors
- [ ] Backend starts and responds to requests
- [ ] All HTTP requests work (using httpx 0.24.1)
