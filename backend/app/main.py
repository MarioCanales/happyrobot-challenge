from fastapi import FastAPI, Depends
from .auth import get_api_key
from .database import engine, Base
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from .models import Load, CallLog
from .database import get_db
from .fmcsa_service import verify_carrier_mc

# Create tables on startup / ephemeral DB for proof of concept
Base.metadata.create_all(bind=engine)

# Request Models
class CarrierCheckRequest(BaseModel):
    mc_number: str

# Response Models
class LoadResponse(BaseModel):
    load_id: str
    origin: str
    destination: str
    rate: float
    commodity: str
    equipment_type: str
    
    class Config:
        orm_mode = True # To work with ORM objects directly Pydantic <-> SQLAlchemy

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

# --- Endpoint 1: Verify Carrier ---
@app.post("/verify-carrier", dependencies=[Depends(get_api_key)])
def check_carrier(request: CarrierCheckRequest):
    """
    Receives an MC number from the AI agent.
    Returns valid=True if the carrier is found and active.
    """
    is_valid = verify_carrier_mc(request.mc_number)
    
    if is_valid:
        return {"status": "success", "eligible": True, "message": "Carrier is verified."}
    else:
        return {"status": "success", "eligible": False, "message": "Carrier not found or ineligible."}

# --- Endpoint 2: Search Loads ---
@app.get("/loads", response_model=List[LoadResponse], dependencies=[Depends(get_api_key)])
def search_loads(
    origin: Optional[str] = None, 
    destination: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    """
    Searches for available loads.
    Happy robot will pass origin/destination as query parameters.
    """
    query = db.query(Load).filter(Load.status == "available")
    
    if origin:
        # Case-insensitive partial match
        query = query.filter(Load.origin.ilike(f"%{origin}%"))
    
    if destination:
        query = query.filter(Load.destination.ilike(f"%{destination}%"))
        
    loads = query.all()
    return loads