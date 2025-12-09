import sys
import os
from datetime import datetime, timedelta

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models import Load

Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    
    # Check if data exists
    if db.query(Load).count() > 0:
        print("Data already seeded.")
        return

    # Mock Data to populate DB for this proof of concept
    # Using dynamic dates so they are always in the future relative to when you run this
    now = datetime.now()
    
    loads_data = [
        {
            "load_id": "L1001",
            "origin": "Dallas, TX",
            "destination": "Phoenix, AZ",
            "pickup_datetime": now + timedelta(days=1),
            "delivery_datetime": now + timedelta(days=2),
            "equipment_type": "Van",
            "loadboard_rate": 1200.00,
            "weight": 42000,
            "commodity_type": "Paper Rolls",
            "num_of_pieces": 20,
            "miles": 1065.0,
            "dimensions": "Standard",
            "status": "available",
            "notes": "Driver must strap load. FCFS."
        },
        {
            "load_id": "L1002",
            "origin": "Chicago, IL",
            "destination": "Atlanta, GA",
            "pickup_datetime": now + timedelta(days=3),
            "delivery_datetime": now + timedelta(days=4),
            "equipment_type": "Reefer",
            "loadboard_rate": 1800.00,
            "weight": 38000,
            "commodity_type": "Frozen Chicken",
            "num_of_pieces": 1200,
            "miles": 716.0,
            "dimensions": "48x40 Pallets",
            "status": "available",
            "notes": "-10 degrees continuous."
        },
        {
            "load_id": "L1003",
            "origin": "Miami, FL",
            "destination": "Houston, TX",
            "pickup_datetime": now + timedelta(days=5),
            "delivery_datetime": now + timedelta(days=6),
            "equipment_type": "Flatbed",
            "loadboard_rate": 2100.00,
            "weight": 45000,
            "commodity_type": "Lumber",
            "num_of_pieces": 10,
            "miles": 1180.0,
            "dimensions": "48ft Length",
            "status": "available",
            "notes": "Tarps required."
        }
    ]

    for item in loads_data:
        load = Load(**item)
        db.add(load)
    
    db.commit()
    print(f"Seeded {len(loads_data)} loads successfully!")
    db.close()

if __name__ == "__main__":
    seed_data()