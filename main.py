from fastapi import FastAPI, Response, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from apscheduler.schedulers.background import BackgroundScheduler
import secrets
from celery import Celery
import time

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

@app.on_event("shutdown")
async def shutdown_event():
    app.state.scheduler.shutdown()
    
    
## Endpoints
#############################################################################################
    
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
    
# Create a counter metric
REQUEST_COUNT = Counter('request_count', 'Total number of requests')

@app.get("/metrics")
def metrics(credentials: HTTPBasicCredentials = Depends(authenticate)):
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

@app.get("/")
def read_root():
    REQUEST_COUNT.inc()
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
