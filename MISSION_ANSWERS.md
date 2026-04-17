# Day 12 Lab — Mission Answers

> **Student:** Nguyễn Đông Hưng  
> **MSSV:** 2A202600392  
> **Date:** 17/4/2026

---

## Part 1: Localhost vs Production (8 điểm)

### Exercise 1.1: Anti-patterns Found in `develop/app.py`

| # | Anti-pattern | Dòng code | Rủi ro |
|---|-------------|-----------|--------|
| 1 | **API key hardcode** | `OPENAI_API_KEY = "sk-hardcoded-fake-key-never-do-this"` | Push lên GitHub → key bị lộ, bị revoke, tốn tiền |
| 2 | **Database URL hardcode với password** | `DATABASE_URL = "postgresql://admin:password123@..."` | Lộ credentials database, attacker có thể truy cập DB |
| 3 | **Debug flag cứng `True`** | `DEBUG = True` | Stack traces lộ ra cho user trong production, thông tin nhạy cảm |
| 4 | **Dùng `print()` thay structured logging** + **Log ra secret** | `print(f"Using key: {OPENAI_API_KEY}")` | Không parse/search được trong log aggregator; secret xuất hiện trong log files |
| 5 | **Không có `/health` endpoint** | _(thiếu hoàn toàn)_ | Platform (Render/Railway) không biết khi nào restart container bị crash |
| 6 | **Host bind `localhost`** + **port cứng** + **reload=True** | `host="localhost", port=8000, reload=True` | Container/cloud cần `0.0.0.0`; Platform inject PORT khác; reload tốn RAM trong production |

### Exercise 1.3: Comparison Table — Develop vs Production

| Feature | Develop (❌ Basic) | Production (✅ Advanced) | Tại sao quan trọng? |
|---------|-------------------|------------------------|---------------------|
| **Config** | `OPENAI_API_KEY = "sk-..."` hardcode | `os.getenv("OPENAI_API_KEY")` từ env var | Thay đổi config không cần sửa code; không lộ secret trên GitHub |
| **Health check** | Không có | `GET /health` + `GET /ready` | Platform biết khi nào restart container; LB biết khi nào route traffic |
| **Logging** | `print(f"Using key: {API_KEY}")` | JSON structured, không log secret | Parse/search dễ trong Datadog/CloudWatch; tuân thủ security compliance |
| **Shutdown** | Tắt đột ngột (kill process) | `signal.signal(SIGTERM, handler)` graceful | Hoàn thành in-flight requests trước khi tắt; không mất data giữa chừng |
| **Host binding** | `localhost` (chỉ local) | `0.0.0.0` (chấp nhận external traffic) | Container/cloud cần nhận traffic từ outside network interface |
| **Port** | Cứng `8000` | `int(os.getenv("PORT", "8000"))` | Railway/Render inject PORT khác nhau tùy instance |
| **Error handling** | Crash + traceback hiện cho user | Try/catch + structured error response | User không thấy internal details; app recover được từ lỗi |
| **Authentication** | Không có | API Key qua header `X-API-Key` | Chỉ authorized clients mới gọi được agent; chống abuse |

---

## Part 2: Docker (8 điểm)

### Exercise 2.1: Dockerfile Analysis

1. **Base image là gì?** → `python:3.11-slim` — Debian slim + Python 3.11 runtime, nhỏ gọn (~130 MB) so với `python:3.11` full (~900 MB)

2. **Working directory `/app`** → Tất cả lệnh sau (`COPY`, `RUN`, `CMD`) đều thực thi trong `/app`. Giữ code tách biệt khỏi system files.

3. **Tại sao COPY `requirements.txt` trước code?** → **Docker layer caching**: nếu chỉ sửa code mà không đổi dependencies, Docker skip layer `pip install` (tốn 30s+). Chỉ rebuild layer cuối `COPY app/`. Tiết kiệm thời gian build đáng kể.

4. **CMD vs ENTRYPOINT:**
   - `CMD` → có thể override khi `docker run <image> <other-command>` (linh hoạt)
   - `ENTRYPOINT` → cố định executable, chỉ thay arguments (dùng khi container = executable)
   - Chúng ta dùng `CMD` vì muốn override command trên Render (`dockerCommand`)

### Exercise 2.3: Image Size Comparison

| Image | Base | Size | Giải thích |
|-------|------|------|-----------|
| **Develop** | `python:3.11` (full) | ~890 MB | Bao gồm gcc, build tools, docs, man pages |
| **Production** | `python:3.11-slim` + multi-stage | ~160 MB | Stage 1: install + compile; Stage 2: chỉ copy runtime files |
| **Giảm** | — | **~82%** | Loại bỏ build tools, cache, intermediate files |

**Multi-stage build hoạt động thế nào:**
- **Stage 1 (builder):** Install gcc + pip install → tạo compiled packages
- **Stage 2 (runtime):** Copy CHỈ site-packages từ builder → không có gcc, cache, source
- Kết quả: image nhỏ, ít CVE (ít packages = ít attack surface)

---

## Part 3: Cloud Deployment (8 điểm)

### Exercise 3.1: Render Deployment

- **Platform:** Render (Docker runtime)
- **Public URL:** https://day12-agent-hung.onrender.com
- **Region:** Singapore (gần Việt Nam nhất)
- **Plan:** Free tier (spin-down sau 15 phút idle, cold start ~30-60s)

### Exercise 3.2: Deploy Config Comparison

| Feature | `render.yaml` (Render) | `railway.toml` (Railway) |
|---------|----------------------|------------------------|
| **Format** | YAML | TOML |
| **Service definition** | `services:` array, khai báo type/runtime/envVars | `[build]` + `[deploy]` sections |
| **Env vars** | Inline trong YAML, hỗ trợ `generateValue: true` tự tạo secret | Set qua dashboard hoặc CLI |
| **Health check** | `healthCheckPath: /health` | Qua dashboard |
| **Auto deploy** | `autoDeploy: true` (push = deploy) | Mặc định auto-deploy từ linked repo |
| **Docker support** | `runtime: docker` + `dockerCommand` override | `[build] dockerfile = "Dockerfile"` |

**Nhận xét:** Render YAML mô tả rõ ràng hơn, Railway TOML ngắn gọn hơn. Render hỗ trợ `generateValue` tiện cho secrets.

---

## Part 4: API Security (8 điểm)

### Exercise 4.1: Authentication — API Key

**Cách hoạt động:**
```
Client → Header "X-API-Key: <secret>" → Server kiểm tra → Match? → 200 / 401
```

- Server đọc `AGENT_API_KEY` từ environment variable (không hardcode)
- So sánh header `X-API-Key` với `settings.agent_api_key`
- Thiếu/sai key → `401 Unauthorized`
- Đúng key → cho phép tiếp tục

**Test không có key → 401:**
```bash
curl -X POST https://<URL>/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
# Response: 401 {"detail": "Invalid or missing API key..."}
```

### Exercise 4.2: Rate Limiting

**Algorithm:** Sliding Window Counter
- Dùng `deque` lưu timestamps của mỗi request
- Mỗi request mới: xóa entries cũ hơn 60s, đếm còn lại
- Nếu >= `RATE_LIMIT_PER_MINUTE` (20) → `429 Too Many Requests` + header `Retry-After: 60`
- Key bucket = 8 ký tự đầu của API key (group rate per client)

**Tại sao sliding window?**
- Fixed window có edge case: 19 req ở giây 59, thêm 19 req ở giây 61 → 38 req trong 2 giây thực tế
- Sliding window đếm chính xác trong bất kỳ 60s window nào

### Exercise 4.3: Test Results

```bash
# Gửi 25 requests liên tục, expect: 20×200, 5×429
for i in $(seq 1 25); do
  echo "Request $i: $(curl -s -o /dev/null -w '%{http_code}' \
    -X POST $URL/ask \
    -H 'X-API-Key: $KEY' \
    -H 'Content-Type: application/json' \
    -d "{\"question\": \"test $i\"}")"
done
# Request 1-20: 200
# Request 21-25: 429
```

### Exercise 4.4: Cost Guard

**Cách hoạt động:**
- Track `_daily_cost` (accumulated) và `_cost_reset_day`
- Mỗi request: ước tính tokens → tính cost theo GPT-4o-mini pricing
- Nếu `_daily_cost >= DAILY_BUDGET_USD` ($5.0) → `402 Payment Required`
- Reset về 0 khi ngày mới (so sánh `strftime("%Y-%m-%d")`)

**Tại sao cần cost guard?**
- Một user spam 10,000 requests → bill $500 → phá sản
- Cost guard giới hạn $5/ngày → worst case $150/tháng (chấp nhận được)
- Kết hợp rate limit (20/min) → double protection

---

## Part 5: Scaling & Reliability (8 điểm)

### Exercise 5.1: Health Check (`/health`)

**Mục đích:** Liveness probe — platform biết process có đang sống không.

```json
{
  "status": "ok",
  "version": "1.0.0",
  "environment": "production",
  "uptime_seconds": 1234.5,
  "total_requests": 42,
  "checks": {"llm": "mock"},
  "timestamp": "2026-04-17T08:00:00Z"
}
```

- Trả **200** → process sống, không cần restart
- Không trả (timeout) → platform kill + restart container
- Chạy mỗi 30s (HEALTHCHECK trong Dockerfile)

### Exercise 5.2: Readiness Probe (`/ready`)

**Mục đích:** Load balancer biết khi nào instance sẵn sàng nhận traffic.

- Startup: `_is_ready = False` → init xong → `_is_ready = True`
- Shutdown: `_is_ready = False` → LB ngừng route traffic
- Trả **200** nếu ready, **503** nếu chưa

**Khác biệt với `/health`:**
- `/health`: process sống ≠ sẵn sàng (đang init DB, load model)
- `/ready`: sẵn sàng handle requests → LB route traffic vào

### Exercise 5.3: Graceful Shutdown

```python
def _handle_signal(signum, _frame):
    logger.info(json.dumps({"event": "signal", "signum": signum}))

signal.signal(signal.SIGTERM, _handle_signal)
```

- Khi platform muốn tắt container → gửi `SIGTERM`
- Handler log event → uvicorn có 30s (`timeout_graceful_shutdown=30`) để finish in-flight requests
- Sau 30s → `SIGKILL` (force kill)

**Tại sao quan trọng?**
- Không graceful: user đang giữa request → response bị cắt → bad UX
- Có graceful: finish requests → drain connections → clean shutdown

### Exercise 5.4: Stateless Design

**Nguyên tắc:** Mỗi instance KHÔNG chứa state critical → scale horizontally dễ dàng.

- **Rate limiter + Cost guard:** In-memory (mỗi instance tự track)
- **Nếu cần shared state:** Redis (`REDIS_URL` env var) → tất cả instances dùng chung
- **Conversation history:** Không lưu trong process → client gửi lại context mỗi request

**Trade-off:**
- In-memory: đơn giản, nhanh, mất khi restart
- Redis: shared across instances, persist across restarts, thêm operational complexity

### Exercise 5.5: Load Balancing

```bash
docker compose up --scale agent=3
```

- Docker Compose tạo 3 instances của `agent` service
- Load balancer (round-robin) phân tán traffic
- Stateless design cho phép bất kỳ instance nào handle bất kỳ request nào
- Nếu 1 instance crash → 2 còn lại tiếp tục serve
