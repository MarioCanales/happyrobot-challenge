from fastapi import FastAPI, Depends, HTTPException
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

class NegotiationRequest(BaseModel):
    load_id: str
    offer_amount: float
    session_id: str  # Unique ID for this call from HappyRobot
    carrier_mc: Optional[str] = "Unknown" 

class NegotiationResponse(BaseModel):
    decision: str  # "accept", "counter", "reject"
    counter_amount: Optional[float] = None
    message: str

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

@app.post("/negotiate", response_model=NegotiationResponse, dependencies=[Depends(get_api_key)])
def negotiate_offer(
    request: NegotiationRequest, 
    db: Session = Depends(get_db)
):
    #TODO: this is a first approach, we need to revisit this as the core business decission logic!

    # Fail fast if the load isn't found
    load = db.query(Load).filter(Load.load_id == request.load_id).first()
    if not load:
        raise HTTPException(status_code=404, detail="Load not found")
    
    # --- Strategy Setup ---
    target = load.loadboard_rate
    floor = target * 0.85  # 15% margin
    offer = request.offer_amount
    
    # --- Session Tracking ---
    # Get existing log or start a new one
    call_log = db.query(CallLog).filter(CallLog.session_id == request.session_id).first()
    if not call_log:
        call_log = CallLog(
            session_id=request.session_id,
            load_id_ref=request.load_id,
            carrier_mc=request.carrier_mc,
            outcome="negotiating"
        )
        db.add(call_log)
    
    call_log.offered_rate = offer

    # --- Negotiation Logic ---
    decision = "reject"
    counter = None
    message = ""

    if offer >= target:
        # Carrier offered our asking price (or more)
        decision = "accept"
        message = f"That works. We can book it at ${offer}."
        counter = offer

    elif offer < floor:
        # Offer is below our hard floor
        decision = "reject"
        message = f"That is too low. The best I can do is ${target}."
        counter = target
        call_log.sentiment = "negative"

    else:
        # Negotiation range: Split the difference
        midpoint = (target + offer) / 2
        counter = round(midpoint, -1) # Round to nearest $10 for a clean number
        # TODO: refine rounding logic if needed - do we actually want to pretend we are humans?
        
        # If we are within $20 of their offer, just accept it to close the deal
        if counter <= offer + 20:
            decision = "accept"
            message = f"I can make that work at ${offer}. Let's book it."
            counter = offer
        else:
            decision = "counter"
            message = f"I can't do ${offer}, but I can meet you at ${counter}."

    # --- Finalize State ---
    # TODO: when integrating with HappyRobot, we need to get call sentiment from there. Not based on accept/reject logic.
    if decision == "accept":
        call_log.outcome = "booked"
        call_log.agreed_rate = counter
        call_log.sentiment = "positive"
    elif decision == "reject":
        call_log.outcome = "negotiation_failed"

    db.commit()
    
    return NegotiationResponse(
        decision=decision, 
        counter_amount=counter, 
        message=message
    )

# --- Endpoint: Fetch Call Logs for Dashboard ---
# TODO: separate auth? To block this to other callers
@app.get("/logs", dependencies=[Depends(get_api_key)])
def get_call_logs(db: Session = Depends(get_db)):
    """
    Returns all call logs for the dashboard.
    """
    logs = db.query(CallLog).order_by(CallLog.created_at.desc()).all()
    return logs