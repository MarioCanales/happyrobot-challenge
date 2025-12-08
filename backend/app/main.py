from fastapi import FastAPI, Depends
from .auth import get_api_key
from .database import engine, Base

# Create tables on startup / ephemeral DB for proof of concept
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="HappyRobot Inbound Carrier API",
    description="API for automating inbound carrier calls and negotiation.",
    version="1.0.0"
)

# Public Health Check (No Auth needed to verify deployment)
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "backend"}

# Protected Endpoint Example
@app.get("/secure-test", dependencies=[Depends(get_api_key)])
def secure_test():
    return {"status": "authenticated", "message": "You have a valid API Key!"}