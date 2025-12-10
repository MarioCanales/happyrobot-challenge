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
        "origin": "Dallas",
        "destination": "Phoenix",
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
        "origin": "Chicago",
        "destination": "Atlanta",
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
        "origin": "Miami",
        "destination": "Houston",
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
    },

    # --- More Available Loads ---
    {
        "load_id": "L1004",
        "origin": "Los Angeles",
        "destination": "Denver",
        "pickup_datetime": now + timedelta(days=2),
        "delivery_datetime": now + timedelta(days=3),
        "equipment_type": "Van",
        "loadboard_rate": 1500.00,
        "weight": 30000,
        "commodity_type": "Electronics",
        "num_of_pieces": 400,
        "miles": 1016.0,
        "dimensions": "Standard",
        "status": "available",
        "notes": "No team required."
    },
    {
        "load_id": "L1005",
        "origin": "Seattle",
        "destination": "Sacramento",
        "pickup_datetime": now + timedelta(days=1),
        "delivery_datetime": now + timedelta(days=2),
        "equipment_type": "Reefer",
        "loadboard_rate": 1600.00,
        "weight": 25000,
        "commodity_type": "Fresh Produce",
        "num_of_pieces": 900,
        "miles": 754.0,
        "dimensions": "Palletized",
        "status": "available",
        "notes": "Must keep temp at 36°F."
    },

    # --- BOOKED Loads ---
    {
        "load_id": "L1006",
        "origin": "Houston",
        "destination": "Kansas City",
        "pickup_datetime": now - timedelta(days=1),
        "delivery_datetime": now + timedelta(days=1),
        "equipment_type": "Flatbed",
        "loadboard_rate": 1900.00,
        "weight": 40000,
        "commodity_type": "Steel Coils",
        "num_of_pieces": 8,
        "miles": 747.0,
        "dimensions": "Coils",
        "status": "booked",
        "notes": "Loaded yesterday, en route."
    },
    {
        "load_id": "L1007",
        "origin": "Memphis",
        "destination": "Orlando",
        "pickup_datetime": now - timedelta(days=2),
        "delivery_datetime": now + timedelta(hours=10),
        "equipment_type": "Van",
        "loadboard_rate": 1700.00,
        "weight": 37000,
        "commodity_type": "Retail Goods",
        "num_of_pieces": 500,
        "miles": 824.0,
        "dimensions": "Standard",
        "status": "booked",
        "notes": "Driver ETA 10 hours."
    },

    # --- IN TRANSIT ---
    {
        "load_id": "L1008",
        "origin": "Salt Lake City",
        "destination": "Boise",
        "pickup_datetime": now - timedelta(hours=5),
        "delivery_datetime": now + timedelta(hours=7),
        "equipment_type": "Van",
        "loadboard_rate": 700.00,
        "weight": 18000,
        "commodity_type": "Machinery Parts",
        "num_of_pieces": 45,
        "miles": 340.0,
        "dimensions": "Standard",
        "status": "in_transit",
        "notes": "Driver currently in route."
    },

    # --- Delivered ---
    {
        "load_id": "L1009",
        "origin": "Boston",
        "destination": "Newark",
        "pickup_datetime": now - timedelta(days=3),
        "delivery_datetime": now - timedelta(days=2),
        "equipment_type": "Reefer",
        "loadboard_rate": 1400.00,
        "weight": 32000,
        "commodity_type": "Dairy",
        "num_of_pieces": 700,
        "miles": 260.0,
        "dimensions": "Palletized",
        "status": "delivered",
        "notes": "Delivered on time."
    },

    # --- Additional Loads ---
    {
        "load_id": "L1010",
        "origin": "Cleveland",
        "destination": "Detroit",
        "pickup_datetime": now + timedelta(days=1),
        "delivery_datetime": now + timedelta(days=1, hours=5),
        "equipment_type": "Van",
        "loadboard_rate": 550.00,
        "weight": 15000,
        "commodity_type": "Auto Parts",
        "num_of_pieces": 90,
        "miles": 170.0,
        "dimensions": "Boxes",
        "status": "available",
        "notes": "Light load."
    },
    {
        "load_id": "L1011",
        "origin": "St. Louis",
        "destination": "Minneapolis",
        "pickup_datetime": now + timedelta(days=2),
        "delivery_datetime": now + timedelta(days=3),
        "equipment_type": "Flatbed",
        "loadboard_rate": 1650.00,
        "weight": 42000,
        "commodity_type": "Pipe",
        "num_of_pieces": 12,
        "miles": 466.0,
        "dimensions": "Loaded side",
        "status": "available",
        "notes": "Straps and edge protectors needed."
    },

    # More booked / past loads
    {
        "load_id": "L1012",
        "origin": "Nashville",
        "destination": "Charlotte",
        "pickup_datetime": now - timedelta(days=1),
        "delivery_datetime": now + timedelta(hours=8),
        "equipment_type": "Reefer",
        "loadboard_rate": 1300.00,
        "weight": 28000,
        "commodity_type": "Produce",
        "num_of_pieces": 700,
        "miles": 420.0,
        "dimensions": "Palletized",
        "status": "booked",
        "notes": "Delayed at pickup but moving."
    },
    {
        "load_id": "L1013",
        "origin": "New Orleans",
        "destination": "San Antonio",
        "pickup_datetime": now - timedelta(days=4),
        "delivery_datetime": now - timedelta(days=3),
        "equipment_type": "Van",
        "loadboard_rate": 1100.00,
        "weight": 20000,
        "commodity_type": "Plastic Goods",
        "num_of_pieces": 200,
        "miles": 541.0,
        "dimensions": "Boxes",
        "status": "delivered",
        "notes": "Signed POD available."
    },

    {
        "load_id": "L1014",
        "origin": "Portland",
        "destination": "Salt Lake City",
        "pickup_datetime": now + timedelta(days=4),
        "delivery_datetime": now + timedelta(days=5),
        "equipment_type": "Flatbed",
        "loadboard_rate": 2500.00,
        "weight": 48000,
        "commodity_type": "Construction Materials",
        "num_of_pieces": 15,
        "miles": 762.0,
        "dimensions": "Overlength",
        "status": "available",
        "notes": "Permits included."
    },
    {
        "load_id": "L1015",
        "origin": "San Diego",
        "destination": "Las Vegas",
        "pickup_datetime": now + timedelta(days=1),
        "delivery_datetime": now + timedelta(days=1, hours=6),
        "equipment_type": "Van",
        "loadboard_rate": 900.00,
        "weight": 18000,
        "commodity_type": "Medical Supplies",
        "num_of_pieces": 300,
        "miles": 330.0,
        "dimensions": "Palletized",
        "status": "available",
        "notes": "High priority load."
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