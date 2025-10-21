# 🚀 Deploy Chess Insight AI to Render

Complete guide to deploy your Chess Insight AI backend to Render with PostgreSQL and Redis.

## 📋 Prerequisites

- [Render account](https://render.com) (free tier available)
- Git repository with your code
- This Chess Insight AI project

## 🏗️ Deployment Methods

### Method 1: Blueprint Deployment (Recommended)

**1. Push to GitHub/GitLab:**
```bash
# Initialize git (if not done)
git init
git add .
git commit -m "Initial Chess Insight AI commit"
git branch -M main
git remote add origin https://github.com/yourusername/chess-insight-ai.git
git push -u origin main
```

**2. Deploy via Render Dashboard:**
- Go to [render.com/dashboard](https://render.com/dashboard)
- Click "New" → "Blueprint"
- Connect your GitHub repository
- Select your `chess-insight-ai` repository
- Render will automatically detect `render.yaml` and deploy all services

### Method 2: Manual Service Creation

**1. Create PostgreSQL Database:**
- Dashboard → "New" → "PostgreSQL"
- Name: `chess-insight-postgres`
- Database Name: `chessai`
- User: `chessai`
- Region: Oregon (or nearest)
- Plan: Free

**2. Create Redis Instance:**
- Dashboard → "New" → "Redis"
- Name: `chess-insight-redis`
- Region: Same as PostgreSQL
- Plan: Free

**3. Create Web Service:**
- Dashboard → "New" → "Web Service"
- Connect Git repository
- Root Directory: Leave blank
- Environment: Python 3
- Build Command: `cd backend && pip install -r requirements.txt && python -m alembic upgrade head`
- Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**4. Configure Environment Variables:**
Add these in Web Service → Environment:
```
POSTGRES_SERVER=[Internal connection string from PostgreSQL service]
POSTGRES_PORT=5432
POSTGRES_USER=chessai
POSTGRES_PASSWORD=[Generated password from PostgreSQL service]
POSTGRES_DB=chessai
REDIS_HOST=[Internal connection string from Redis service]  
REDIS_PORT=[Redis port from service]
SECRET_KEY=[Generate a secure key]
LOG_LEVEL=INFO
CHESSCOM_API_BASE_URL=https://api.chess.com/pub
CHESSCOM_API_RATE_LIMIT=100
MAX_GAMES_PER_ANALYSIS=50
STOCKFISH_PATH=/usr/games/stockfish
STOCKFISH_DEPTH=15
STOCKFISH_TIME=1.0
UPLOAD_DIR=/tmp/uploads
REPORTS_DIR=/tmp/reports
```

## 🔧 Service Configuration

### Free Tier Limits
- **PostgreSQL**: 1GB storage, 97 hours/month
- **Redis**: 25MB memory, 97 hours/month  
- **Web Service**: 512MB RAM, 750 hours/month
- **Custom domains**: Available on free tier

### Scaling Options
- **PostgreSQL**: Upgrade to $7/month for 1GB persistent storage
- **Redis**: Upgrade to $7/month for 256MB memory
- **Web Service**: Upgrade to $7/month for 1GB RAM + custom domain

## 🌐 Domain & URLs

**Free tier URLs:**
- Backend API: `https://chess-insight-backend.onrender.com`
- Health check: `https://chess-insight-backend.onrender.com/health`
- API docs: `https://chess-insight-backend.onrender.com/api/v1/docs`

**Custom domain (paid):**
- Set up custom domain in service settings
- Update frontend API URL to your custom domain

## 🔍 Monitoring & Logs

**Access logs:**
- Service dashboard → "Logs" tab
- Real-time log streaming
- Filter by log level

**Health monitoring:**
- Automatic health checks via `/api/v1/health`
- Email alerts on service failures
- Uptime monitoring

## 🚢 Deployment Process

**What happens during deployment:**

1. **Build Phase:**
   ```bash
   cd backend
   pip install -r requirements.txt
   python -m alembic upgrade head  # Creates database tables
   ```

2. **Start Phase:**
   ```bash
   cd backend
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

3. **Health Check:**
   - Render pings `/api/v1/health` endpoint
   - Service marked as "Live" when healthy

## 🔧 Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `POSTGRES_SERVER` | PostgreSQL host | `dpg-xyz.oregon-postgres.render.com` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `POSTGRES_USER` | Database user | `chessai` |
| `POSTGRES_PASSWORD` | Database password | `generated-password` |
| `POSTGRES_DB` | Database name | `chessai` |
| `REDIS_HOST` | Redis host | `red-xyz.oregon-redis.render.com` |
| `REDIS_PORT` | Redis port | `6379` |
| `SECRET_KEY` | App secret key | `your-secret-key-here` |

## 🚨 Troubleshooting

### Common Issues

**1. Build Failures:**
```
Error: Could not install packages due to EnvironmentError
```
*Solution:* Check requirements.txt formatting and package availability

**2. Database Connection Errors:**
```
Error: could not connect to server
```
*Solution:* Verify PostgreSQL environment variables and internal connection string

**3. Alembic Migration Errors:**
```
Error: Target database is not up to date
```
*Solution:* Ensure Alembic configuration is correct and migrations run during build

**4. Health Check Failures:**
```
Error: Health check timeout
```
*Solution:* Verify health endpoint returns 200 status within 30 seconds

### Debug Commands

**View logs:**
```bash
# In Render dashboard
Services → Your Service → Logs
```

**Check service status:**
```bash
# Test health endpoint
curl https://your-service.onrender.com/health
```

**Database connectivity:**
```bash
# Test from another service or shell
curl https://your-service.onrender.com/api/v1/users/
```

## 📈 Performance Optimization

**Free Tier Tips:**
- Services sleep after 15 minutes of inactivity
- Cold start takes 30-60 seconds
- Use for development/testing

**Production Optimization:**
- Upgrade to paid tier for always-on services
- Enable auto-scaling for traffic spikes
- Use CDN for static assets
- Monitor performance with built-in metrics

## 🔐 Security Best Practices

**Environment Variables:**
- Never commit secrets to git
- Use Render's secret management
- Rotate keys regularly

**HTTPS:**
- Automatic SSL certificates
- Force HTTPS redirects
- Secure headers enabled

**Database:**
- Internal connection strings only
- Encrypted connections
- Regular backups

## 🎯 Next Steps

**After deployment:**

1. **Test API endpoints:**
   ```bash
   curl https://your-service.onrender.com/health
   curl https://your-service.onrender.com/api/v1/docs
   ```

2. **Create first user:**
   ```bash
   curl -X POST https://your-service.onrender.com/api/v1/users/ \
     -H "Content-Type: application/json" \
     -d '{"chesscom_username": "testuser", "email": "test@example.com"}'
   ```

3. **Update frontend:**
   - Update API URL in frontend to production URL
   - Deploy frontend to Vercel/Netlify/Render

4. **Monitor and maintain:**
   - Set up uptime monitoring
   - Configure error alerts
   - Plan database backups

## 🌟 Production Checklist

- [ ] Services deployed and healthy
- [ ] Database tables created via Alembic
- [ ] Environment variables configured
- [ ] Health checks passing
- [ ] API endpoints responding
- [ ] CORS configured for frontend domain
- [ ] Error monitoring set up
- [ ] Custom domain configured (optional)
- [ ] SSL certificate active
- [ ] Performance monitoring enabled

Your Chess Insight AI backend is now live on Render! 🚀
