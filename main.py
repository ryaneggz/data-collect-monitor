import time
import random
import secrets
from datetime import datetime
from fastapi import FastAPI, Response, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from apscheduler.schedulers.background import BackgroundScheduler
from prometheus_client import Counter, Gauge, Summary, Histogram, generate_latest, CONTENT_TYPE_LATEST
from celery import Celery

app = FastAPI()

# Configure Celery
celery = Celery(__name__, broker='redis://redis:6379/0', backend='redis://redis:6379/0')

@celery.task
def my_job():
    print("Job executed at", time.strftime("%Y-%m-%d %H:%M:%S"))

def schedule_jobs():
    scheduler = BackgroundScheduler()
    scheduler.add_job(my_job.apply_async, 'interval', seconds=5)
    scheduler.start()
    return scheduler

@app.on_event("startup")
async def startup_event():
    app.state.scheduler = schedule_jobs()
    API_UPTIME.set_to_current_time()

@app.on_event("shutdown")
async def shutdown_event():
    app.state.scheduler.shutdown()
    
# Basic Auth
security = HTTPBasic()
USERNAME = "admin"
PASSWORD = "password"

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, USERNAME)
    correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials

# Create metrics
REQUEST_COUNT = Counter('request_count', 'Total number of requests')
REQUEST_ERRORS = Counter('request_errors', 'Total number of errors')
IN_PROGRESS_REQUESTS = Gauge('in_progress_requests', 'Number of in-progress requests')
REQUEST_LATENCY = Summary('request_latency_seconds', 'Request latency in seconds')
REQUEST_LATENCY_HISTOGRAM = Histogram('request_latency_seconds_histogram', 'Request latency in seconds')
API_UPTIME = Gauge('api_uptime', 'API Uptime in seconds')

@app.get("/metrics")
def metrics(credentials: HTTPBasicCredentials = Depends(authenticate)):
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

@app.get("/")
def read_root():
    REQUEST_COUNT.inc()
    IN_PROGRESS_REQUESTS.inc()
    start_time = time.time()
    try:
        # Simulate processing time
        processing_time = random.uniform(0.1, 2.0)
        time.sleep(processing_time)
        REQUEST_LATENCY.observe(processing_time)
        REQUEST_LATENCY_HISTOGRAM.observe(processing_time)
        return {"message": "Hello, World!"}
    except Exception:
        REQUEST_ERRORS.inc()
        raise
    finally:
        IN_PROGRESS_REQUESTS.dec()
        REQUEST_LATENCY.observe(time.time() - start_time)
        REQUEST_LATENCY_HISTOGRAM.observe(time.time() - start_time)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)