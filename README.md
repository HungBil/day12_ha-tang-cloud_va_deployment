# 🤖 Production AI Agent — Day 12 Cloud Deployment Lab

> **Student:** Nguyễn Đông Hưng — 2A202600392  
> **Course:** AI Agent Development  
> **Lab:** Day 12 — Hạ Tầng Cloud và Deployment

---

## 📋 Overview

Production-ready AI Agent deployed on **Render** with:
- ✅ API Key authentication
- ✅ Rate limiting (20 req/min, sliding window)
- ✅ Cost guard ($5/day budget)
- ✅ Health check + Readiness probe
- ✅ Graceful shutdown (SIGTERM)
- ✅ Multi-stage Docker build (< 500 MB)
- ✅ Structured JSON logging
- ✅ Security headers (X-Content-Type-Options, X-Frame-Options)
- ✅ CORS middleware

---

## 🚀 Quick Setup

### Option 1: Docker (Recommended)

```bash
# 1. Clone repo
git clone https://github.com/<username>/day12_ha-tang-cloud_va_deployment.git
cd day12_ha-tang-cloud_va_deployment

# 2. Create environment file
cp .env.example .env

# 3. Build and run
docker compose up --build

# 4. Test
curl http://localhost:8000/health
```

### Option 2: Local Python

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create environment file
cp .env.example .env

# 3. Run
python -m app.main

# 4. Test
curl http://localhost:8000/health
```

---

## 📡 API Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/` | ❌ | App info + available endpoints |
| `POST` | `/ask` | ✅ `X-API-Key` | Send question to AI agent |
| `GET` | `/health` | ❌ | Liveness probe |
| `GET` | `/ready` | ❌ | Readiness probe |
| `GET` | `/metrics` | ✅ `X-API-Key` | Runtime metrics (protected) |
| `GET` | `/docs` | ❌ | Swagger UI (dev only) |

### POST `/ask` — Example

```bash
curl -X POST http://localhost:8000/ask \
  -H "X-API-Key: dev-key-change-me" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Docker?"}'
```

**Response:**
```json
{
  "question": "What is Docker?",
  "answer": "Container là cách đóng gói app để chạy ở mọi nơi...",
  "model": "gpt-4o-mini",
  "timestamp": "2026-04-17T08:00:00Z"
}
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                   Client (cURL)                 │
└───────────────────┬─────────────────────────────┘
                    │ HTTP Request
                    ▼
┌─────────────────────────────────────────────────┐
│              FastAPI Application                │
│  ┌──────────┐ ┌───────────┐ ┌──────────────┐   │
│  │ Auth     │→│ Rate      │→│ Cost Guard   │   │
│  │ (401)    │ │ Limiter   │ │ (402)        │   │
│  │          │ │ (429)     │ │              │   │
│  └──────────┘ └───────────┘ └──────┬───────┘   │
│                                     │           │
│                              ┌──────▼───────┐   │
│                              │  Mock LLM    │   │
│                              │  (or OpenAI) │   │
│                              └──────────────┘   │
│                                                 │
│  Endpoints: / | /ask | /health | /ready | /metrics│
└─────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
├── app/
│   ├── __init__.py          # Package init
│   ├── main.py              # FastAPI app, endpoints, middleware
│   ├── config.py            # 12-factor config (dataclass + os.getenv)
│   ├── auth.py              # API Key verification
│   ├── rate_limiter.py      # Sliding window rate limiter
│   └── cost_guard.py        # Budget protection
├── utils/
│   └── mock_llm.py          # Mock LLM responses
├── screenshots/             # Deployment evidence
├── Dockerfile               # Multi-stage build
├── docker-compose.yml       # Agent + Redis stack
├── render.yaml              # Render Blueprint
├── requirements.txt         # Pinned dependencies
├── .env.example             # Environment template
├── .dockerignore            # Docker build exclusions
├── MISSION_ANSWERS.md       # Lab exercise answers
└── DEPLOYMENT.md            # Public URL + test commands
```

---

## 🔒 Security Features

1. **API Key Auth** — `X-API-Key` header required for `/ask` and `/metrics`
2. **Rate Limiting** — 20 requests/minute per key (sliding window)
3. **Cost Guard** — $5/day budget limit per instance
4. **No Hardcoded Secrets** — All sensitive config from env vars
5. **Security Headers** — `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`
6. **Non-root Docker** — Container runs as `agent` user
7. **CORS** — Configurable allowed origins

---

## 📄 License

This project is created for educational purposes as part of the AI Agent Development course.
