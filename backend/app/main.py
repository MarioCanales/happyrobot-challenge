from datetime import datetime
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
    pickup_datetime : datetime
    delivery_datetime : datetime
    loadboard_rate: float
    commodity_type: str
    equipment_type: str
    status: str
    
    class Config:
        orm_mode = True # To work with ORM objects directly Pydantic <-> SQLAlchemy

class NegotiationRequest(BaseModel):
    load_id: str
    offer_amount: float

class NegotiationResponse(BaseModel):
    decision: str  # "accept", "counter", "reject"
    counter_amount: Optional[float] = None
    message: str

class CallSummaryRequest(BaseModel):
    session_id : str
    carrier_mc: Optional[str] = None # Assuming MC might not always be captured
    load_id_ref: Optional[str] = None 
    offered_rate: Optional[float] = None
    sentiment : str
    outcome : str

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

# --- Endpoint 3: Negotiate ---
@app.post("/negotiate", response_model=NegotiationResponse, dependencies=[Depends(get_api_key)])
def negotiate_offer(
    request: NegotiationRequest, 
    db: Session = Depends(get_db)
):
    # Fail fast if the load isn't found
    load = db.query(Load).filter(Load.load_id == request.load_id).first()
    if not load:
        raise HTTPException(status_code=404, detail="Load not found")
    
    # --- Strategy Setup ---
    target = load.loadboard_rate
    floor = target * 0.85  # 15% margin floor
    offer = request.offer_amount
    
    # --- Negotiation Logic ---
    decision = "reject"
    counter = None
    message = ""

    # --- 1: Offer meets or exceeds target (instant accept) ---
    if offer >= target:
        decision = "accept"
        counter = offer
        message = f"That works. We can book it at ${offer}."

    # --- 2: Offer is below the hard floor (reject + return target) ---
    elif offer < floor:
        decision = "reject"
        counter = target
        message = f"That is too low. The best I can do is ${target}."

    # --- 3: Offer is between floor and target (negotiate) ---
    else:
        midpoint = (target + offer) / 2
        counter = round(midpoint, -1)  # Round to nearest 10

        # If counter is very close to the offer, accept it
        if counter <= offer + 20:
            decision = "accept"
            counter = offer
            message = f"I can make that work at ${offer}. Let's book it."
        else:
            decision = "counter"
            message = f"I can't do ${offer}, but I can meet you at ${counter}."

    # --- Update load status if accepted ---
    if decision == "accept":
        load.status = "booked"

    db.commit()  # Save DB changes
    
    return NegotiationResponse(
        decision=decision, 
        counter_amount=counter, 
        message=message
    )

# --- Endpoint 4: Save Call Summary ---
@app.post("/call-summary", dependencies=[Depends(get_api_key)])
def save_call_summary(
    request: CallSummaryRequest, 
    db: Session = Depends(get_db)
):
    """
    Receives final analysis from HappyRobot after call ends and creates the complete CallLog record.
    The offered_rate is stored as NULL unless the outcome is 'Success'.
    """
    # 1. Prepare offered_rate value
    final_rate = request.offered_rate
    
    # Validation logic: If the outcome is NOT 'booked', set the final rate to None (NULL in DB)
    if request.outcome != "Success":
        final_rate = None
        
    # 2. Create a new CallLog object
    new_call_log = CallLog(
        session_id=request.session_id,
        carrier_mc=request.carrier_mc,
        load_id_ref=request.load_id_ref,
        offered_rate=final_rate, 
        sentiment=request.sentiment,
        outcome=request.outcome
    )
    
    db.add(new_call_log)
    
    # 3. Commit and Error Handling
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        # If the session_id already exists (due to unique constraint), return an error
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(status_code=409, detail=f"Call summary for session ID {request.session_id} already exists.")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
        
    return {"status": "created", "session_id": request.session_id}


# --- Dashboard specific Endpoint: Fetch Call Logs for Dashboard ---
# TODO: separate auth? To block this to other callers
@app.get("/logs", dependencies=[Depends(get_api_key)])
def get_call_logs(db: Session = Depends(get_db)):
    """
    Returns all call logs for the dashboard.
    """
    logs = db.query(CallLog).order_by(CallLog.created_at.desc()).all()
    return logs

@app.get("/loads/all", dependencies=[Depends(get_api_key)])
def get_all_loads(db: Session = Depends(get_db)):
    return db.query(Load).all()
