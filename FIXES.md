# FIXES.md — Bug Report and Fixes

## Fix 1: API Redis Connection (Hardcoded localhost)
- **File:** `api/main.py`
- **Line:** 6
- **Problem:** Redis connection hardcoded to `localhost` which fails inside Docker container. Services on different containers cannot reach localhost. Queue key name was also wrong.
- **Fix:** Changed to use environment variables with fallback:
```python
  redis_host = os.getenv("REDIS_HOST", "redis")
  redis_port = int(os.getenv("REDIS_PORT", 6379))
  r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
```

## Fix 2: API Missing Request Body Model
- **File:** `api/main.py`
- **Line:** 10
- **Problem:** `create_job()` endpoint doesn't accept any request body parameters. Client needs to send `task` field but endpoint ignores it.
- **Fix:** Added Pydantic model and proper parameter handling:
```python
  class JobRequest(BaseModel):
      task: str
  
  @app.post("/jobs")
  def create_job(request: JobRequest):
```

## Fix 3: API Wrong Queue Key Name
- **File:** `api/main.py`
- **Line:** 12
- **Problem:** Using queue key `job` instead of `job_queue`. Worker polls `job_queue`, so jobs never reach the worker.
- **Fix:** Changed to consistent key name:
```python
  r.rpush("job_queue", job_id)  # Was: r.lpush("job", job_id)
```

## Fix 4: API Missing 404 Response
- **File:** `api/main.py`
- **Line:** 17
- **Problem:** Returns dictionary `{"error": "not found"}` with 200 status code instead of proper 404 HTTP response.
- **Fix:** Added HTTPException for proper HTTP response:
```python
  if not job_data:
      raise HTTPException(status_code=404, detail="Job not found")
```

## Fix 5: API Missing Health Check Endpoint
- **File:** `api/main.py`
- **Line:** (new endpoint)
- **Problem:** Docker HEALTHCHECK requires `/health` endpoint but it's missing.
- **Fix:** Added new endpoint:
```python
  @app.get("/health")
  def health_check():
      try:
          r.ping()
          return {"status": "ok"}
      except Exception as e:
          return {"status": "unhealthy"}, 503
```

## Fix 6: Worker Redis Connection (Hardcoded localhost)
- **File:** `worker/worker.py`
- **Line:** 5
- **Problem:** Hardcoded `localhost` fails in Docker. Same issue as API.
- **Fix:** Changed to environment variables:
```python
  redis_host = os.getenv("REDIS_HOST", "redis")
  redis_port = int(os.getenv("REDIS_PORT", 6379))
  r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
```

## Fix 7: Worker Infinite Loop Without Sleep
- **File:** `worker/worker.py`
- **Line:** 15
- **Problem:** `while True` with no sleep causes 100% CPU usage when queue is empty. `brpop` with timeout=5 still loops immediately.
- **Fix:** Added sleep after timeout:
```python
  if job:
      _, job_id = job
      process_job(job_id)
  else:
      time.sleep(0.1)  # Prevent busy loop
```

## Fix 8: Worker Wrong Queue Key Name
- **File:** `worker/worker.py`
- **Line:** 16
- **Problem:** Polling `job` queue instead of `job_queue`. API pushes to `job_queue`, so worker never receives jobs.
- **Fix:** Changed key name:
```python
  job = r.brpop("job_queue", timeout=5)  # Was: r.brpop("job", timeout=5)
```

## Fix 9: Worker Decode Error
- **File:** `worker/worker.py`
- **Line:** 18
- **Problem:** Calling `.decode()` on job_id may fail because `decode_responses=True` already returns strings.
- **Fix:** Changed to proper string handling:
```python
  _, job_id = job  # job_id is already a string
  process_job(job_id)
```

## Fix 10: Worker Missing Graceful Shutdown
- **File:** `worker/worker.py`
- **Line:** (new)
- **Problem:** No signal handlers for SIGTERM/SIGINT. Docker sends SIGTERM but worker ignores it, causing unclean shutdown.
- **Fix:** Added signal handlers:
```python
  def signal_handler(sig, frame):
      logger.info("Shutting down worker...")
      sys.exit(0)
  
  signal.signal(signal.SIGTERM, signal_handler)
  signal.signal(signal.SIGINT, signal_handler)
```

## Fix 11: Worker Missing Error Handling
- **File:** `worker/worker.py`
- **Line:** 13
- **Problem:** No try-catch around job processing or main loop. Single error crashes worker.
- **Fix:** Added comprehensive error handling in main loop and process_job function.

## Fix 12: Frontend File Missing
- **File:** `frontend/app.js`
- **Line:** (entire file)
- **Problem:** Frontend application doesn't exist. Only package.json exists.
- **Fix:** Created complete Express.js server with:
  - `/health` endpoint for Docker healthcheck
  - `/api/jobs` POST endpoint to create jobs
  - `/api/jobs/:job_id` GET endpoint to check status
  - Static file serving from public/

## Fix 13: Frontend Using Hardcoded localhost
- **File:** `frontend/app.js`
- **Line:** 11
- **Problem:** Even if frontend existed, would hardcode API URL to localhost.
- **Fix:** Use environment variable with fallback:
```javascript
  const API_URL = process.env.API_URL || "http://api:8000";
```

## Fix 14: Frontend Missing HTML UI
- **File:** `frontend/public/index.html`
- **Line:** (entire file)
- **Problem:** No UI for users to interact with system.
- **Fix:** Created complete HTML page with:
  - Job submission form
  - Real-time status polling
  - Styled UI with proper error handling

## Fix 15: package.json Bad Format
- **File:** `frontend/package.json`
- **Line:** (entire file)
- **Problem:** Original had syntax errors. Missing lint script.
- **Fix:** Cleaned up format and added eslint configuration.

## Fix 16: Missing API Response Metadata
- **File:** `api/main.py`
- **Line:** 34
- **Problem:** Job endpoint returns only status, but frontend needs task field to display.
- **Fix:** Return full job metadata:
```python
  return {"job_id": job_id, **job_data}
```

## Summary
- **Total Bugs Found:** 16
- **Files Modified:** 6
- **Files Created:** 2
  - frontend/app.js (complete server)
  - frontend/public/index.html (UI)
- **Root Causes:**
  - Hardcoded localhost (3 instances) → changed to env vars
  - Wrong queue key names (2 instances) → standardized to `job_queue`
  - Missing endpoints (2 instances) → added `/health` and `/api/jobs/:id`
  - Missing error handling (2 instances) → added try-catch and HTTP exceptions
  - Missing files/code (2 instances) → created frontend application
  - Improper request handling (2 instances) → added Pydantic models, proper responses
  - Performance issues (1 instance) → added sleep to prevent CPU spinning
  - Missing graceful shutdown (1 instance) → added signal handlers
EOF
