import redis
import time
import os
import signal
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis configuration from environment variables
redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = int(os.getenv("REDIS_PORT", 6379))

try:
    r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
    r.ping()
    logger.info(f"Connected to Redis at {redis_host}:{redis_port}")
except redis.ConnectionError as e:
    logger.error(f"Failed to connect to Redis: {e}")
    sys.exit(1)


def process_job(job_id):
    """Process a single job"""
    try:
        logger.info(f"Processing job {job_id}")
        
        # Simulate work
        time.sleep(2)
        
        # Mark as completed
        r.hset(f"job:{job_id}", "status", "completed")
        logger.info(f"Completed: {job_id}")
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {e}")
        r.hset(f"job:{job_id}", "status", "failed")


def signal_handler(sig, frame):
    """Graceful shutdown handler"""
    logger.info("Shutting down worker...")
    sys.exit(0)


# Register signal handler for graceful shutdown
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


def main():
    """Main worker loop"""
    logger.info("Worker started, waiting for jobs...")
    
    while True:
        try:
            # Block and pop job from queue with 5 second timeout
            job = r.brpop("job_queue", timeout=5)
            
            if job:
                # job is (key, value) tuple, value is already a string
                _, job_id = job
                process_job(job_id)
            else:
                # Timeout — no job available, just loop
                time.sleep(0.1)
        except redis.ConnectionError as e:
            logger.error(f"Redis connection lost: {e}")
            time.sleep(5)
            # Try to reconnect
            try:
                r.ping()
                logger.info("Redis reconnected")
            except:
                pass
        except Exception as e:
            logger.error(f"Unexpected error in worker loop: {e}")
            time.sleep(1)


if __name__ == "__main__":
    main()
EOF
