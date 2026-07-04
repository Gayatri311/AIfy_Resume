# Alfy Resume

Transform traditional resumes into AI-ready resumes — authentically.

Alfy Resume parses your existing resume, analyzes ATS friendliness, calculates an AI Readiness Score, identifies gaps, and rewrites your experience into recruiter-friendly AI narratives. Every change is explained, validated for authenticity, and reviewable in a GitHub-style diff viewer.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Next.js 15     │────▶│  FastAPI API     │────▶│  PostgreSQL     │
│  Frontend       │     │  + Celery Worker │     │  + Redis        │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

### Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 15, React, TypeScript, TailwindCSS, Shadcn UI, Framer Motion |
| Backend | FastAPI, Python, PostgreSQL, Redis, Celery |
| AI | LangGraph, LangChain (GPT-4.1 / Claude Sonnet when configured) |
| Export | React PDF, ReportLab (PDF), python-docx |

## Quick Start

### Prerequisites

- Node.js 20+
- Python 3.12+
- Docker & Docker Compose (recommended)

### 1. Start infrastructure

```bash
docker compose up -d postgres redis
```

### 2. Backend

```bash
cd backend
cp .env.example .env
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

In a second terminal, start the Celery worker:

```bash
cd backend && source venv/bin/activate
celery -A app.core.celery_app worker --loglevel=info
```

### 3. Frontend

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Full Docker Stack

```bash
docker compose up --build
```

## User Flow

1. **Landing Page** — Hero, features, 5-step process
2. **Upload** — PDF/DOCX drag-and-drop (max 10MB)
3. **Processing** — Animated 8-step timeline with recruiter insights
4. **Diff Review** — Section-by-section GitHub-style comparison
5. **Dashboard** — AI Readiness Score, gaps, next actions
6. **Interview Prep** — 15 tailored questions
7. **Export** — ATS-friendly PDF

## AI Agents

| Agent | Purpose |
|-------|---------|
| Resume Parser | Extract & normalize resume into JSON |
| ATS Analyzer | Score ATS friendliness, find missing keywords |
| Experience Enhancer | Plausible AI framing of existing work |
| AI Project Generator | Role-specific project suggestions |
| AI Readiness Scorer | 0-100 composite score |
| Gap Analyzer | Missing skills, projects, certifications |
| Authenticity Validator | SAFE / STRETCH / UNVERIFIABLE classification |

## Authenticity Policy

- **Never fabricate experience**
- Enhancements are plausible extensions of existing work
- UNVERIFIABLE claims are automatically removed
- Every change includes confidence, authenticity, and interview risk ratings

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/resumes/upload` | Upload resume file |
| GET | `/api/v1/resumes/{id}` | Get full analysis |
| PATCH | `/api/v1/resumes/{id}/sections/{section}` | Update/accept section |
| POST | `/api/v1/resumes/{id}/sections/{section}/regenerate` | Regenerate section |
| GET | `/api/v1/resumes/{id}/export?format=pdf` | Export PDF |

## Environment Variables

See `backend/.env.example` and `frontend/.env.local.example`.

## Deployment

**Private beta today:** see **[DEPLOY.md](./DEPLOY.md)** (Vercel + Railway checklist).

Env templates:
- `backend/.env.production.example`
- `frontend/.env.production.example`

- **Frontend**: Vercel (`frontend/`)
- **Backend**: Railway or Fly (`backend/` + `backend/Dockerfile`)

## License

Proprietary — Alfy Resume
