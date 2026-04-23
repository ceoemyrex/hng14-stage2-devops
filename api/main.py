cat > /home/ubuntu/hng14-stage2-devops/api/main.py << 'EOF'
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
import uuid
import os
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

# Redis configuration from environment variables
redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = int(os.getenv("REDIS_PORT", 6379))

try:
    r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
    r.ping()
except redis.ConnectionError as e:
    logger.error(f"Failed to connect to Redis: {e}")
    r = None


class JobRequest(BaseModel):
    task: str


@app.get("/health")
def health_check():
    """Health check endpoint for Docker healthcheck"""
    try:
        r.ping()
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy"}, 503


@app.post("/jobs")
def create_job(request: JobRequest):
    """Create a new job and add it to the queue"""
    if not r:
        raise HTTPException(status_code=503, detail="Redis unavailable")
    
    job_id = str(uuid.uuid4())
    
    # Add job to queue
    r.rpush("job_queue", job_id)
    
    # Store job metadata
    r.hset(f"job:{job_id}", mapping={"status": "pending", "task": request.task})
    
    return {"job_id": job_id}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    """Get the status of a job"""
    if not r:
        raise HTTPException(status_code=503, detail="Redis unavailable")
    
    job_data = r.hgetall(f"job:{job_id}")
    
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"job_id": job_id, **job_data}
EOF
