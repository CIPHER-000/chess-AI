# 🔐 SECURITY NOTICE

## ✅ Security Issue RESOLVED

**Date**: 2025-10-20  
**Severity**: HIGH  
**Status**: ✅ RESOLVED (Key rotated by user)

### Issue Identified
The OpenAI API key was **hardcoded and exposed** in version control at:
- `.windsurf/mcp/gpt5.mcp.json`

### Actions Taken
✅ Removed hardcoded API key from configuration  
✅ Updated to use environment variable: `${OPENAI_API_KEY}`  
✅ Added `OPENAI_API_KEY` to `.env.example`  

### ✅ Actions Completed

1. **API Key Rotated:**
   - Exposed key has been deleted and rotated by user
   - New key secured in environment variables

2. **OpenRouter Integration Added:**
   - Free tier OpenRouter support for development
   - Reduces costs during testing and development
   - See `backend/app/core/ai_client.py` for abstraction layer

3. **Update Local Environment:**
   ```bash
   # Create .env file (if it doesn't exist)
   cp .env.example .env
   
   # Add your keys
   OPENROUTER_API_KEY=your-openrouter-key-here  # For development (free)
   OPENAI_API_KEY=your-openai-key-here          # For production (optional)
   MODEL_PROVIDER=openrouter                    # Use OpenRouter by default
   ```

4. **Get OpenRouter Key (Free):**
   - Visit: https://openrouter.ai/keys
   - Sign up and generate free API key
   - Free models available: `google/gemma-2-9b-it:free`, `meta-llama/llama-3.1-8b-instruct:free`

### Why This Matters
Exposed API keys can be:
- Used by unauthorized parties
- Result in unexpected charges to your OpenAI account
- Violate OpenAI's terms of service
- Lead to rate limit exhaustion

### Prevention Going Forward
- ✅ Never commit `.env` files (already in `.gitignore`)
- ✅ Use environment variables for all secrets
- ✅ Regularly rotate API keys
- ✅ Use API key restrictions (IP whitelisting, usage limits)

### Git History Consideration
If this repository has been pushed to GitHub/GitLab:
1. The exposed key is **permanently in git history**
2. Even after deletion, it remains in commit history
3. This is why immediate key rotation is critical
4. Consider using tools like `git-filter-repo` to purge history (advanced)

---

**Next Steps**: Complete the key rotation, then proceed with Supabase migration.
