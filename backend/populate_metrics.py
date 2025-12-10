"""
Script to populate the database with sample call logs for dashboard demonstration.
This script creates realistic call log data to showcase the dashboard metrics.
"""

import sys
import os
import random
import time
from datetime import datetime, timedelta

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models import CallLog, Load

# Ensure tables exist
Base.metadata.create_all(bind=engine)

# Sample data for realistic call logs
SAMPLE_MC_NUMBERS = [
    "MC-123456", "MC-234567", "MC-345678", "MC-456789", "MC-567890",
    "MC-678901", "MC-789012", "MC-890123", "MC-901234", "MC-012345"
]

OUTCOMES = ["Success", "Negotiation Failed", "Hangup"]
SENTIMENTS = ["positive", "neutral", "negative"]

# Weighted probabilities for more realistic distribution
OUTCOME_WEIGHTS = [0.55, 0.30, 0.15]  # 55% success, 30% failed, 15% hangup
SENTIMENT_WEIGHTS = [0.60, 0.25, 0.15]  # 60% positive, 25% neutral, 15% negative


def generate_session_id():
    """Generate a unique session ID"""
    timestamp = int(time.time() * 1000)
    random_suffix = random.randint(1000, 9999)
    return f"session_{timestamp}_{random_suffix}"


def populate_call_logs(num_calls=20):
    """
    Populate the database with sample call logs.
    
    Args:
        num_calls: Number of call logs to generate (default: 20)
    """
    db = SessionLocal()
    
    try:
        # Get available loads
        loads = db.query(Load).all()
        if not loads:
            print("⚠️  No loads found in database. Please run seed_loads.py first.")
            return
        
        load_ids = [load.load_id for load in loads]
        
        print(f"🚀 Generating {num_calls} sample call logs...")
        
        created_count = 0
        now = datetime.now()
        
        for i in range(num_calls):
            # Generate call data with temporal distribution (spread over last 7 days)
            days_ago = random.randint(0, 7)
            hours_ago = random.randint(0, 23)
            created_time = now - timedelta(days=days_ago, hours=hours_ago)
            
            # Select outcome and sentiment with weighted probabilities
            outcome = random.choices(OUTCOMES, weights=OUTCOME_WEIGHTS)[0]
            sentiment = random.choices(SENTIMENTS, weights=SENTIMENT_WEIGHTS)[0]
            
            # Select random carrier and load
            carrier_mc = random.choice(SAMPLE_MC_NUMBERS)
            load_id = random.choice(load_ids)
            
            # Get the load to determine offered rate
            load = db.query(Load).filter(Load.load_id == load_id).first()
            
            # Generate offered rate based on outcome
            if outcome == "Success":
                # Successful calls have rates close to loadboard rate (85-105%)
                rate_factor = random.uniform(0.85, 1.05)
                offered_rate = round(load.loadboard_rate * rate_factor, 2)
            elif outcome == "Negotiation Failed":
                # Failed negotiations might have lower offers or None
                if random.random() > 0.3:  # 70% have an offer
                    rate_factor = random.uniform(0.70, 0.90)
                    offered_rate = round(load.loadboard_rate * rate_factor, 2)
                else:
                    offered_rate = None
            else:  # Hangup
                # Hangups typically don't have offers
                offered_rate = None
            
            # Create call log
            session_id = generate_session_id()
            
            call_log = CallLog(
                session_id=session_id,
                carrier_mc=carrier_mc,
                load_id_ref=load_id,
                offered_rate=offered_rate,
                sentiment=sentiment,
                outcome=outcome,
                created_at=created_time
            )
            
            db.add(call_log)
            created_count += 1
            
            # Print progress
            if (i + 1) % 5 == 0:
                print(f"  ✓ Created {i + 1}/{num_calls} call logs...")
        
        # Commit all changes
        db.commit()
        print(f"\n✅ Successfully created {created_count} call logs!")
        
        # Print summary statistics
        print("\n📊 Summary Statistics:")
        for outcome in OUTCOMES:
            count = db.query(CallLog).filter(CallLog.outcome == outcome).count()
            percentage = (count / created_count * 100) if created_count > 0 else 0
            print(f"   {outcome}: {count} ({percentage:.1f}%)")
        
        total_revenue = db.query(CallLog).filter(
            CallLog.outcome == "Success",
            CallLog.offered_rate.isnot(None)
        ).with_entities(CallLog.offered_rate).all()
        
        if total_revenue:
            revenue_sum = sum([r[0] for r in total_revenue if r[0]])
            print(f"\n💰 Total Revenue from Successful Calls: ${revenue_sum:,.2f}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error populating call logs: {e}")
        raise
    finally:
        db.close()


def clear_call_logs():
    """Clear all existing call logs from the database"""
    db = SessionLocal()
    try:
        count = db.query(CallLog).count()
        if count > 0:
            db.query(CallLog).delete()
            db.commit()
            print(f"🗑️  Cleared {count} existing call logs")
        else:
            print("ℹ️  No existing call logs to clear")
    except Exception as e:
        db.rollback()
        print(f"❌ Error clearing call logs: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("📞 HappyRobot Call Logs Population Script")
    print("=" * 60)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Populate call logs for dashboard")
    parser.add_argument(
        "--count",
        type=int,
        default=20,
        help="Number of call logs to generate (default: 20)"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing call logs before populating"
    )
    
    args = parser.parse_args()
    
    # Clear existing data if requested
    if args.clear:
        clear_call_logs()
        print()
    
    # Populate with new data
    populate_call_logs(num_calls=args.count)
