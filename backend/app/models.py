from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from .database import Base

"""
# This is the class for the models: we are creating 2 tables. The first one is for loads,
# which follows strictly the structure of the document with instructions. The second one
# hosts the data about each call according to requirements.

This module declares two SQLAlchemy ORM models that map to database tables

1) Load
    - Table name: "loads"
    - Purpose: Persist load (shipment) information as extracted from source documents/PDFs.
    - Indexes/constraints: load_id is unique and indexed for fast lookup. Still keeping another id as primary key for performance and integrity.

2) CallLog
    - Table name: "call_logs"
    - Purpose: Store metadata and results for each call session handled by the system (e.g., negotiations, transcriptions).
    - Indexes/constraints: session_id is unique and indexed; carrier_mc is indexed for querying by carrier.

Notes and design rationale:
- Enumerated domain values (e.g., status, outcome, sentiment) are represented as strings in the
  schema; we might want to enforce constraints at the application layer or via DB CHECK/ENUMs if needed.
- Keeping both a unique load_id and a surrogate primary key id for performance and integrity.
"""

class Load(Base):
    __tablename__ = "loads"

    id = Column(Integer, primary_key=True, index=True)
    load_id = Column(String, unique=True, index=True) # The unique ID referenced in other databases
    origin = Column(String)
    destination = Column(String)
    pickup_datetime = Column(DateTime(timezone=True), server_default=func.now())
    delivery_datetime = Column(DateTime(timezone=True), server_default=func.now())
    equipment_type = Column(String)
    loadboard_rate = Column(Float)
    weight = Column(Integer)
    commodity_type = Column(String)
    num_of_pieces = Column(Integer)
    miles = Column(Float)
    dimensions = Column(String)
    status = Column(String, default="available") # available, booked
    notes = Column(Text, nullable=True)

class CallLog(Base):
    __tablename__ = "call_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True) # From HappyRobot
    carrier_mc = Column(String, index=True)
    carrier_phone = Column(String)
    load_id_ref = Column(String) # Which load were they discussing?
    offered_rate = Column(Float, nullable=True)
    agreed_rate = Column(Float, nullable=True)
    sentiment = Column(String, nullable=True) # positive, neutral, negative
    outcome = Column(String) # booked, negotiation_failed, hangup
    transcription = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())