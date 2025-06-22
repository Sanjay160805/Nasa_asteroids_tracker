Code 1:
import requests
import time
import json
from datetime import datetime, timedelta

# Your API key
API_KEY = 'QzGFvBMqEY4nb8uJ19g6AJ4XjutL8C667DxDucpU'
BASE_URL = 'https://api.nasa.gov/neo/rest/v1/feed'

# Starting parameters
start_date = datetime.strptime('2024-01-01', '%Y-%m-%d')
record_limit = 10000
records = []

def extract_fields(asteroid, approach_data):
    """Extract required fields from each asteroid and its approach data."""
    return {
        "id": int(asteroid.get('id', 0)),
        "neo_reference_id": int(asteroid.get('neo_reference_id', 0)),
        "name": asteroid.get('name', ''),
        "absolute_magnitude_h": float(asteroid.get('absolute_magnitude_h', 0.0)),
        "estimated_diameter_min_km": float(asteroid['estimated_diameter']['kilometers']['estimated_diameter_min']),
        "estimated_diameter_max_km": float(asteroid['estimated_diameter']['kilometers']['estimated_diameter_max']),
        "is_potentially_hazardous_asteroid": bool(asteroid.get('is_potentially_hazardous_asteroid', False)),
        "close_approach_date": datetime.strptime(approach_data['close_approach_date'], '%Y-%m-%d').date(),
        "relative_velocity_kmph": float(approach_data['relative_velocity']['kilometers_per_hour']),
        "astronomical": float(approach_data['miss_distance']['astronomical']),
        "miss_distance_km": float(approach_data['miss_distance']['kilometers']),
        "miss_distance_lunar": float(approach_data['miss_distance']['lunar']),
        "orbiting_body": approach_data.get('orbiting_body', '')
    }

# Fetch and loop until 10,000 records
while len(records) < record_limit:
    end_date = start_date + timedelta(days=7)
    params = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'api_key': API_KEY
    }
    
    response = requests.get(BASE_URL, params=params)
    if response.status_code != 200:
        print("Error fetching data:", response.status_code, response.text)
        break
    
    data = response.json()
    near_earth_objects = data.get('near_earth_objects', {})
    
    for date in near_earth_objects:
        for asteroid in near_earth_objects[date]:
            for approach_data in asteroid.get('close_approach_data', []):
                record = extract_fields(asteroid, approach_data)
                records.append(record)
                if len(records) >= record_limit:
                    break
            if len(records) >= record_limit:
                break
        if len(records) >= record_limit:
            break
    
    # Update start date to next day after current end_date
    start_date = end_date + timedelta(days=1)
    
    print(f"Records collected so far: {len(records)}")
    
    # Polite pause to avoid hitting API limits
    time.sleep(1)

# Save the data to a JSON file
with open('nasa_asteroid_data.json', 'w') as f:
    json.dump(records, f, indent=4, default=str)

print(f"\n✅ Successfully collected {len(records)} records and saved to 'nasa_asteroid_data.json'!")

Code 2:

import sqlite3
import json

# Load the JSON data
with open('nasa_asteroid_data.json', 'r') as f:
    asteroid_data = json.load(f)

# Connect to SQLite database (or create one)
conn = sqlite3.connect('nasa_asteroids1.db')
cursor = conn.cursor()

# Create asteroids table
cursor.execute('''
CREATE TABLE IF NOT EXISTS asteroids (
    id INTEGER PRIMARY KEY,
    name TEXT,
    absolute_magnitude_h FLOAT,
    estimated_diameter_min_km FLOAT,
    estimated_diameter_max_km FLOAT,
    is_potentially_hazardous_asteroid BOOLEAN
);
''')

# Create close_approach table
cursor.execute('''
CREATE TABLE IF NOT EXISTS close_approach (
    neo_reference_id INTEGER,
    close_approach_date DATE,
    relative_velocity_kmph FLOAT,
    astronomical FLOAT,
    miss_distance_km FLOAT,
    miss_distance_lunar FLOAT,
    orbiting_body TEXT,
    FOREIGN KEY (neo_reference_id) REFERENCES asteroids(id)
);
''')

# Insert data
for record in asteroid_data:
    # Insert into asteroids table
    cursor.execute('''
    INSERT OR REPLACE INTO asteroids (id, name, absolute_magnitude_h, 
                                      estimated_diameter_min_km, estimated_diameter_max_km, 
                                      is_potentially_hazardous_asteroid)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        record['id'],
        record['name'],
        record['absolute_magnitude_h'],
        record['estimated_diameter_min_km'],
        record['estimated_diameter_max_km'],
        int(record['is_potentially_hazardous_asteroid'])  # boolean stored as 0/1
    ))
    
    # Insert into close_approach table
    cursor.execute('''
    INSERT OR REPLACE INTO close_approach (neo_reference_id, close_approach_date, 
                                          relative_velocity_kmph, astronomical, 
                                          miss_distance_km, miss_distance_lunar, orbiting_body)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        record['neo_reference_id'],
        record['close_approach_date'],
        record['relative_velocity_kmph'],
        record['astronomical'],
        record['miss_distance_km'],
        record['miss_distance_lunar'],
        record['orbiting_body']
    ))

# Commit and close
conn.commit()
conn.close()

print("✅ Data inserted successfully into SQLite database")

