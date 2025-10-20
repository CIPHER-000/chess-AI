# Development Guide

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit the environment variables as needed
# The default values work for Docker Compose setup
```

### 2. Start Services

```bash
# Start all services (backend + database + redis)
docker-compose up --build

# Or start specific services
docker-compose up postgres redis backend

# To include frontend (when ready)
docker-compose --profile frontend up
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/v1/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## 🏗 Development Workflow

### Backend Development

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run migrations (if using Alembic in the future)
# alembic upgrade head

# Start development server
python -m app.main

# Or use uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint
```

### Database Management

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U chessai -d chessai

# View logs
docker-compose logs postgres

# Reset database (WARNING: This will delete all data)
docker-compose down -v
docker-compose up postgres
```

### Background Tasks

```bash
# Start Celery worker for background processing
docker-compose --profile celery up

# Or run locally
cd backend
celery -A app.workers.celery_app worker --loglevel=info
```

## 📊 API Usage Examples

### 1. Create a User

```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{"chesscom_username": "your_username", "email": "your@email.com"}'
```

### 2. Fetch Recent Games

```bash
curl -X POST "http://localhost:8000/api/v1/games/1/fetch" \
  -H "Content-Type: application/json" \
  -d '{"days": 7, "time_classes": ["rapid", "blitz"]}'
```

### 3. Analyze Games

```bash
curl -X POST "http://localhost:8000/api/v1/analysis/1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"days": 7, "force_reanalysis": false}'
```

### 4. Get Analysis Summary

```bash
curl "http://localhost:8000/api/v1/analysis/1/summary?days=7"
```

### 5. Generate Insights

```bash
curl -X POST "http://localhost:8000/api/v1/insights/1/generate" \
  -H "Content-Type: application/json" \
  -d '{"period_days": 7, "analysis_type": "weekly"}'
```

## 🧪 Testing

### Backend Testing

```bash
cd backend

# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Frontend Testing

```bash
cd frontend

# Install test dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom jest

# Run tests (when test files are created)
npm test
```

## 🚧 Common Issues & Solutions

### 1. Stockfish Not Found
```bash
# Install Stockfish on Ubuntu/Debian
sudo apt-get install stockfish

# Or use custom path in environment
STOCKFISH_PATH=/usr/local/bin/stockfish
```

### 2. Chess.com API Rate Limiting
- The app respects Chess.com's rate limits (100 requests/minute)
- If you hit rate limits, wait a minute before retrying
- Consider implementing exponential backoff for production

### 3. Database Connection Issues
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check connection
docker-compose exec postgres pg_isready -U chessai

# View logs
docker-compose logs postgres
```

### 4. Memory Issues with Analysis
- Stockfish analysis can be memory-intensive
- Adjust Docker memory limits if needed
- Consider reducing analysis depth for large batches

## 📈 Performance Optimization

### Backend Optimizations
1. **Database Indexing**: Add indexes on frequently queried fields
2. **Redis Caching**: Cache API responses and analysis results
3. **Background Jobs**: Use Celery for time-consuming analysis tasks
4. **Database Connection Pooling**: Configure SQLAlchemy pool settings

### Frontend Optimizations
1. **React Query**: Smart caching and background refetching
2. **Code Splitting**: Lazy load dashboard components
3. **Image Optimization**: Use Next.js Image component
4. **Bundle Analysis**: Use `npm run build` to analyze bundle size

## 🔒 Security Considerations

1. **Environment Variables**: Never commit secrets to version control
2. **API Rate Limiting**: Implement rate limiting for production
3. **Input Validation**: Validate all user inputs
4. **CORS Configuration**: Configure proper CORS origins
5. **Database Security**: Use connection pooling and prepared statements

## 📦 Deployment

### Docker Production Build

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables for Production

```bash
# Required production environment variables
SECRET_KEY=your-secure-random-secret-key
POSTGRES_PASSWORD=secure-database-password
BACKEND_CORS_ORIGINS=https://yourdomain.com
LOG_LEVEL=INFO
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Chess.com Public API](https://www.chess.com/news/view/published-data-api)
- [Stockfish Documentation](https://stockfishchess.org/download/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
