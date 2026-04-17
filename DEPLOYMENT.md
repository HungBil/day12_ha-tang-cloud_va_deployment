# Deployment Information

> **Student:** Nguyễn Đông Hưng — 2A202600392  
> **Date:** 17/4/2026

---

## Public URL

```
https://day12-agent-hung.onrender.com
```

> ⚠️ **Cold Start:** Render free tier spin-down sau 15 phút idle. Lần đầu gọi có thể mất 30-60s.

## Platform

- **Provider:** Render
- **Runtime:** Docker
- **Region:** Singapore
- **Plan:** Free tier

---

## Test Commands

### 1. Health Check
```bash
curl https://day12-agent-hung.onrender.com/health
# Expected: {"status": "ok", "version": "1.0.0", ...}
```

### 2. Readiness Check
```bash
curl https://day12-agent-hung.onrender.com/ready
# Expected: {"ready": true}
```

### 3. Authentication Test — No Key (expect 401)
```bash
curl -X POST https://day12-agent-hung.onrender.com/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
# Expected: 401 Unauthorized
```

### 4. Agent Query — With Key (expect 200)
```bash
curl -X POST https://day12-agent-hung.onrender.com/ask \
  -H "X-API-Key: <AGENT_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is deployment?"}'
# Expected: 200 + JSON response with answer
```

### 5. Rate Limiting Test (expect 429 after 10 requests)
```bash
for i in $(seq 1 25); do
  echo "Request $i: $(curl -s -o /dev/null -w '%{http_code}' \
    -X POST https://day12-agent-hung.onrender.com/ask \
    -H 'X-API-Key: <AGENT_API_KEY>' \
    -H 'Content-Type: application/json' \
    -d "{\"question\": \"test $i\"}")"
done
# Expected: 200 for first 10, 429 for remaining
```

### 6. Root Info
```bash
curl https://day12-agent-hung.onrender.com/
# Expected: JSON with app name, version, endpoints
```

---

## Environment Variables

| Variable | Description | How Set |
|----------|-------------|---------|
| `ENVIRONMENT` | production | render.yaml |
| `AGENT_API_KEY` | API authentication key | Render auto-generated |
| `JWT_SECRET` | JWT signing secret | Render auto-generated |
| `APP_VERSION` | Application version | render.yaml |
| `DAILY_BUDGET_USD` | Daily cost limit ($) | render.yaml |
| `RATE_LIMIT_PER_MINUTE` | Max requests per minute | render.yaml |
| `PORT` | Server port | Render injected |

---

## Screenshots

- [Deployment Dashboard](screenshots/dashboard.png)
- [Service Running](screenshots/running.png)
- [Test Results](screenshots/test.png)
