import random
from datetime import datetime, timedelta

def generate_dummy_trip():
    today = datetime.now()
    trip_date = today + timedelta(days=random.randint(1, 10))
    time = f"{random.randint(6, 21)}:{random.choice(['00', '30'])}"
    return {
        "from": "Ahmedabad",
        "to": "Delhi",
        "date": trip_date.strftime("%Y-%m-%d"),
        "time": time
    }
