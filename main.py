from fastapi import FastAPI, Request
from prometheus_fastapi_instrumentator import Instrumentator
import logging
import time
import random

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("devops-api")

app = FastAPI()

# Activation des métriques (Prometheus)
Instrumentator().instrument(app).expose(app)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"Path: {request.url.path} - Method: {request.method} - Time: {process_time:.4f}s")
    return response

@app.get("/")
def read_root():
    return {"message": "Hello DevOps World!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}