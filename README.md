# Chess Insight AI

An AI-powered companion app that analyzes Chess.com users' recent games, identifies why their rating changes, and provides actionable improvement insights.

## 🎯 Problem Statement

Chess.com players often don't understand why their rating drops or where their weaknesses lie. Existing analysis is fragmented or requires manual game review. This tool automates that process, delivering clear explanations and targeted recommendations.

## 👥 Target Audience

- Casual to intermediate Chess.com players who want to improve their skills
- Coaches who want to provide feedback faster
- Competitive hobbyists tracking performance trends

## 🚀 Core Features

- **Chess.com Integration**: Username lookup + game archive fetch via API
- **Game Analysis**: PGN parsing and engine evaluation (Stockfish 16)
- **Performance Metrics**: ACPL, blunder count, phase-based performance, opening analysis
- **Visual Dashboard**: Charts and insights with actionable advice
- **Reports**: Downloadable weekly PDF reports
- **Caching**: Smart game storage with ETag/Last-Modified headers

## 🛠 Tech Stack

### Backend
- **Framework**: Python FastAPI
- **Chess Engine**: Stockfish 16 + python-chess
- **Database**: PostgreSQL (users, games, insights) + Redis (caching, queues)
- **Workers**: Celery for background analysis tasks
- **Storage**: Local file system (configurable for S3/Supabase later)

### Frontend
- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **UI Components**: Custom components with modern design

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Database**: PostgreSQL + Redis
- **Background Jobs**: Celery with Redis broker

## 📁 Project Structure

```
chess-insight-ai/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── workers/        # Background tasks
│   ├── tests/              # Backend tests
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Next.js pages
│   │   ├── hooks/          # Custom React hooks
│   │   ├── services/       # API clients
│   │   └── types/          # TypeScript types
│   ├── public/             # Static assets
│   ├── package.json
│   └── Dockerfile
├── shared/                 # Shared types and utilities
├── docker/                 # Docker configurations
├── docs/                   # Documentation
└── docker-compose.yml      # Multi-service setup
```

## 🏗 Development Plan

### Phase 1: Core Infrastructure (Week 1-2)
1. ✅ Project setup and directory structure
2. ✅ Backend FastAPI setup with basic routes
3. ✅ Database schema design and models
4. ✅ Chess.com API integration
5. ✅ Docker containerization

### Phase 2: Game Analysis Engine (Week 2-3)
1. ✅ Stockfish integration and PGN parsing
2. ✅ Analysis metrics calculation (ACPL, blunders)
3. ✅ Background job system with Celery
4. ✅ Caching strategy implementation

### Phase 3: Frontend Development (Week 3-4)
1. ✅ Next.js setup with TypeScript
2. ✅ Dashboard UI components
3. ✅ Charts and visualizations
4. ✅ API integration and data fetching

### Phase 4: Integration & Polish (Week 4-5)
1. ✅ End-to-end testing setup
2. ⏳ Performance optimization (ongoing)
3. ✅ Error handling and user feedback
4. ✅ Documentation and deployment guides


### Phase 5: YouTube Learning Engine (Week 6–8)

#### 🎥 Overview  
This phase introduces a groundbreaking **AI-powered learning engine** that transforms chess tutorials from passive YouTube videos into interactive practice sessions. By combining speech recognition, move extraction, and engine-backed simulation, users can learn and reinforce new openings, tactics, and concepts directly from the content they already watch.

#### 🧠 Problem  
Chess players often rely on YouTube tutorials to learn new openings or concepts, but retention is low. After watching, players must manually recreate positions to practice — a tedious process that breaks learning flow.  

**Chess Insight AI** bridges this gap by converting tutorial videos into playable, annotated experiences inside the app.

#### 🚀 Key Features  
- **YouTube Integration**: Paste a YouTube link of any chess tutorial  
- **AI Move Extraction**: Automatically detect moves and lines from the video using Whisper (speech-to-text) and NLP  
- **Annotated PGN Generation**: Convert extracted moves into PGN format with commentary  
- **Interactive Practice Mode**: Play against Stockfish following the exact lines explained in the video  
- **Concept Highlights**: On-screen notes (“control the center”, “avoid early queen development”) during play  
- **Video Sync** *(optional)*: Watch and practice in parallel — the chessboard syncs with the tutorial’s timeline  

#### ⚙️ Technical Design  
- **Backend Service**:  
  - New module: `/backend/app/services/youtube_learning_service.py`  
  - Handles video download (`yt-dlp`), audio transcription (Whisper), and move extraction  
  - Stores processed games as annotated PGNs in PostgreSQL  

- **Database**:  
  ```python
  class VideoLesson(Base):
      __tablename__ = "video_lessons"
      id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
      youtube_url = Column(String, nullable=False)
      title = Column(String)
      pgn_data = Column(Text)
      annotations = Column(JSONB)
      created_at = Column(DateTime, default=datetime.utcnow)

Frontend Integration:

- New dashboard tab: “Learn From YouTube”
- Input: Paste YouTube link → process → view playable annotated lines
- Interactive chessboard using react-chessboard
- Tooltip commentary & practice feedback

🧩 Integration with Core Engine
- This feature naturally extends the app’s analysis insights:
- Detects user weaknesses → suggests related YouTube lessons
- Auto-generates training drills based on the user’s most common blunders

Creates a feedback loop:
Analyze → Learn → Practice → Improve

🔮 Future Enhancements
- Personalized study plans based on game analytics
- “Explain This Move” chat-based mode using GPT
- AI summarization of video lessons into quick bullet-point takeaways

Partnerships with chess creators for exclusive “AI-practice-ready” tutorials

## 🚦 Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Quick Start
```bash
# Clone and navigate to project
git clone <repository-url>
cd chess-insight-ai

# Start all services
docker-compose up --build

# Frontend will be available at http://localhost:3000
# Backend API at http://localhost:8000
# API docs at http://localhost:8000/docs
```

## 🎨 Design Philosophy

- **Clean & Modern**: Analytical dashboard feel like a coach's performance report
- **Clarity First**: Insights should be immediately actionable and easy to understand
- **Minimal but Motivating**: Focus on essential information that drives improvement

## 🔮 Future Features

- Opening repertoire clustering (ECO → family → winrate)
- Opponent-strength normalization (performance by rating buckets)
- Tactical motif detection (forks, pins, back-rank weakness)
- Personalized 7-day improvement plans
- Coaching mode: chat-based explanations of blunders
- Social leaderboard / community comparisons
- Browser extension integration

## 📄 License

MIT License - see LICENSE file for details
