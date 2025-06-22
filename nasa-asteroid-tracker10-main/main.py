import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Database connection
conn = sqlite3.connect("nasa_asteroids_10k.db")

st.set_page_config(layout="wide", page_title="🚀 NASA Asteroid Tracker", page_icon="🚀")
st.title("🚀 NASA Asteroid Tracker")
st.markdown("### Explore close-approach data of asteroids from NASA's NEO database")

# Sidebar filters
with st.sidebar:
    st.header("🔎 Filters")
    start_date = st.date_input("Start Date", value=datetime(2024, 1, 1))
    end_date = st.date_input("End Date", value=datetime(2025, 1, 1))
    velocity_min = st.slider("Min Velocity (km/h)", 0, 150000, 0, step=1000)
    astro_limit = st.slider("Max Astronomical Unit", 0.0, 1.0, 0.5)
    lunar_limit = st.slider("Max Lunar Distance", 0.0, 100.0, 10.0)
    hazardous = st.radio("Potentially Hazardous", ["All", "Yes", "No"])

    st.markdown("---")
    selected_query = st.selectbox("📊 Choose Analysis", [
        "All Filtered Asteroids",
        "Count asteroid approaches",
        "Average velocity of each asteroid",
        "Top 10 fastest asteroids",
        "Hazardous asteroids with >3 approaches",
        "Month with most approaches",
        "Fastest ever asteroid approach",
        "Asteroids sorted by max estimated diameter",
        "Asteroids getting closer over time",
        "Closest approach details by asteroid",
        "Asteroids with velocity > 50000 km/h",
        "Approaches per month",
        "Asteroid with highest brightness (lowest magnitude)",
        "Hazardous vs non-hazardous asteroid count",
        "Hazardous vs non-hazardous approach events",
        "Asteroids closer than Moon",
        "Asteroids within 0.05 AU",
        "Asteroids with maximum relative velocity",
        "Asteroids with the closest approach to Earth",
        "Asteroids with the highest estimated diameter",
        "Asteroids approaching at high velocity",
        "Asteroids approaching Earth during a specific month",
        "Asteroids with highest approach frequency",
        "Asteroids with the highest miss distance",
        "Asteroids with multiple approaches in a month",
        "Asteroids that are both fast and hazardous",
        "Asteroids with increasing approach velocity over time"
    ])

# Filter construction
where_clause = f"""
ca.close_approach_date BETWEEN '{start_date}' AND '{end_date}'
AND ca.astronomical < {astro_limit}
AND ca.miss_distance_lunar < {lunar_limit}
AND ca.relative_velocity_kmph >= {velocity_min}
"""

hazard_filter = ""
if hazardous == "Yes":
    hazard_filter = "AND a.is_potentially_hazardous_asteroid = 1"
elif hazardous == "No":
    hazard_filter = "AND a.is_potentially_hazardous_asteroid = 0"

# All queries
query_map = {
    "All Filtered Asteroids": f"""
    SELECT a.name, a.absolute_magnitude_h, a.estimated_diameter_min_km,
           a.estimated_diameter_max_km, a.is_potentially_hazardous_asteroid,
           ca.close_approach_date, ca.relative_velocity_kmph,
           ca.astronomical, ca.miss_distance_lunar
    FROM close_approach ca
    JOIN asteroids a ON ca.neo_reference_id = a.id
    WHERE {where_clause} {hazard_filter}
    LIMIT 10000
    """,
    "Count asteroid approaches": f"""
    SELECT ca.neo_reference_id, COUNT(*) as approach_count
    FROM close_approach ca
    WHERE {where_clause}
    GROUP BY ca.neo_reference_id
    LIMIT 10000
    """,
    "Average velocity of each asteroid": f"""
    SELECT ca.neo_reference_id, AVG(ca.relative_velocity_kmph) as avg_velocity
    FROM close_approach ca
    WHERE {where_clause}
    GROUP BY ca.neo_reference_id
    LIMIT 10000
    """,
    "Top 10 fastest asteroids": f"""
    SELECT ca.neo_reference_id, MAX(ca.relative_velocity_kmph) as max_velocity
    FROM close_approach ca
    WHERE {where_clause}
    GROUP BY ca.neo_reference_id
    ORDER BY max_velocity DESC
    LIMIT 10
    """,
    "Hazardous asteroids with >3 approaches": f"""
    SELECT ca.neo_reference_id, COUNT(*) as approach_count
    FROM close_approach ca
    JOIN asteroids a ON ca.neo_reference_id = a.id
    WHERE a.is_potentially_hazardous_asteroid = 1
    GROUP BY ca.neo_reference_id
    HAVING approach_count > 3
    LIMIT 10000
    """,
    "Month with most approaches": f"""
    SELECT STRFTIME('%Y-%m', ca.close_approach_date) as month, COUNT(*) as total
    FROM close_approach ca
    WHERE {where_clause}
    GROUP BY month
    ORDER BY total DESC
    LIMIT 1
    """,
    "Fastest ever asteroid approach": """
    SELECT ca.neo_reference_id, ca.relative_velocity_kmph, ca.close_approach_date
    FROM close_approach ca
    WHERE ca.relative_velocity_kmph = (SELECT MAX(relative_velocity_kmph) FROM close_approach)
    LIMIT 1
    """,
    "Asteroids sorted by max estimated diameter": """
    SELECT id, name, estimated_diameter_max_km
    FROM asteroids
    ORDER BY estimated_diameter_max_km DESC
    LIMIT 10
    """,
    "Asteroids getting closer over time": f"""
    SELECT ca.neo_reference_id, ca.close_approach_date, ca.miss_distance_lunar
    FROM close_approach ca
    WHERE {where_clause}
    ORDER BY ca.neo_reference_id, ca.close_approach_date
    LIMIT 10000
    """,
    "Closest approach details by asteroid": f"""
    SELECT a.name, ca.close_approach_date, MIN(ca.miss_distance_lunar) as closest
    FROM close_approach ca
    JOIN asteroids a ON ca.neo_reference_id = a.id
    WHERE {where_clause}
    GROUP BY ca.neo_reference_id
    LIMIT 10000
    """,
    "Asteroids with velocity > 50000 km/h": f"""
    SELECT a.name, ca.relative_velocity_kmph, ca.close_approach_date
    FROM close_approach ca
    JOIN asteroids a ON ca.neo_reference_id = a.id
    WHERE ca.relative_velocity_kmph > 50000 AND {where_clause}
    LIMIT 10000
    """,
    "Approaches per month": f"""
    SELECT STRFTIME('%Y-%m', ca.close_approach_date) as month, COUNT(*) as count
    FROM close_approach ca
    WHERE {where_clause}
    GROUP BY month
    LIMIT 10000
    """,
    "Asteroid with highest brightness (lowest magnitude)": """
    SELECT id, name, absolute_magnitude_h
    FROM asteroids
    ORDER BY absolute_magnitude_h ASC
    LIMIT 1
    """,
    "Hazardous vs non-hazardous asteroid count": f"""
    SELECT hazard_status, COUNT(*) as count
    FROM (
        SELECT 
            CASE 
                WHEN a.is_potentially_hazardous_asteroid = 1 THEN 'Hazardous'
                ELSE 'Non-Hazardous'
            END AS hazard_status
        FROM asteroids a
        JOIN close_approach ca ON ca.neo_reference_id = a.id
        WHERE ca.close_approach_date BETWEEN '{start_date}' AND '{end_date}'
        AND ca.astronomical < {astro_limit}
        AND ca.miss_distance_lunar < {lunar_limit}
        AND ca.relative_velocity_kmph >= {velocity_min}
        LIMIT 10000
    )
    GROUP BY hazard_status
    """,
    "Hazardous vs non-hazardous approach events": f"""
    SELECT 
        CASE WHEN a.is_potentially_hazardous_asteroid = 1 THEN 'Hazardous'
             ELSE 'Non-Hazardous'
        END AS hazard_status,
        COUNT(*) as count
    FROM close_approach ca
    JOIN asteroids a ON ca.neo_reference_id = a.id
    WHERE {where_clause}
    GROUP BY a.is_potentially_hazardous_asteroid
    LIMIT 10000
    """,
    "Asteroids closer than Moon": f"""
    SELECT a.name, ca.close_approach_date, ca.miss_distance_lunar
    FROM close_approach ca
    JOIN asteroids a ON ca.neo_reference_id = a.id
    WHERE ca.miss_distance_lunar < 1.0 AND {where_clause}
    LIMIT 10000
    """,
    "Asteroids within 0.05 AU": f"""
    SELECT a.name, ca.close_approach_date, ca.astronomical
    FROM close_approach ca
    JOIN asteroids a ON ca.neo_reference_id = a.id
    WHERE ca.astronomical < 0.05 AND {where_clause}
    LIMIT 10000
    """,
    # Additional 10 queries
    "Asteroids with maximum relative velocity": f"""
    SELECT a.name, ca.relative_velocity_kmph, ca.close_approach_date
    FROM close_approach ca
    JOIN asteroids a ON ca.neo_reference_id = a.id
    WHERE {where_clause}
    ORDER BY ca.relative_velocity_kmph DESC
    LIMIT 10
    """,
    "Asteroids with the closest approach to Earth": f"""
    SELECT a.name, ca.close_approach_date, ca.miss_distance_lunar
    FROM close_approach ca
    JOIN asteroids a ON ca.neo_reference_id = a.id
    WHERE {where_clause}
    ORDER BY ca.miss_distance_lunar ASC
    LIMIT 10
    """,
    "Asteroids with the highest estimated diameter": f"""
    SELECT a.name, a.estimated_diameter_max_km, a.estimated_diameter_min_km
    FROM asteroids a
    WHERE {where_clause}
    ORDER BY a.estimated_diameter_max_km DESC
    LIMIT 10
    """,
    "Asteroids approaching at high velocity": f"""
    SELECT a.name, ca.relative_velocity_kmph, ca.close_approach_date
    FROM close_approach ca
    JOIN asteroids a ON ca.neo_reference_id = a.id
    WHERE ca.relative_velocity_kmph > 60000 AND {where_clause}
    LIMIT 10
    """,
    "Asteroids approaching Earth during a specific month": f"""
    SELECT a.name, ca.close_approach_date, ca.miss_distance_lunar
    FROM close_approach ca
    JOIN asteroids a ON ca.neo_reference_id = a.id
    WHERE STRFTIME('%Y-%m', ca.close_approach_date) = STRFTIME('%Y-%m', '{start_date}') AND {where_clause}
    LIMIT 10
    """,
    "Asteroids with highest approach frequency": f"""
    SELECT ca.neo_reference_id, COUNT(*) as approach_count
    FROM close_approach ca
    WHERE {where_clause}
    GROUP BY ca.neo_reference_id
    ORDER BY approach_count DESC
    LIMIT 10
    """,
    "Asteroids with the highest miss distance": f"""
    SELECT a.name, ca.close_approach_date, ca.miss_distance_lunar
    FROM close_approach ca
    JOIN asteroids a ON ca.neo_reference_id = a.id
    WHERE {where_clause}
    ORDER BY ca.miss_distance_lunar DESC
    LIMIT 10
    """,
    "Asteroids with multiple approaches in a month": f"""
    SELECT ca.neo_reference_id, STRFTIME('%Y-%m', ca.close_approach_date) as month, COUNT(*) as approach_count
    FROM close_approach ca
    WHERE {where_clause}
    GROUP BY ca.neo_reference_id, month
    HAVING approach_count > 1
    LIMIT 10
    """,
    "Asteroids that are both fast and hazardous": f"""
    SELECT a.name, ca.relative_velocity_kmph, ca.close_approach_date
    FROM close_approach ca
    JOIN asteroids a ON ca.neo_reference_id = a.id
    WHERE ca.relative_velocity_kmph > 50000 AND a.is_potentially_hazardous_asteroid = 1 AND {where_clause}
    LIMIT 10
    """,
    "Asteroids with increasing approach velocity over time": f"""
    SELECT ca.neo_reference_id, ca.close_approach_date, ca.relative_velocity_kmph
    FROM close_approach ca
    WHERE {where_clause}
    ORDER BY ca.neo_reference_id, ca.close_approach_date
    """
}

# Query execution based on user selection
query = query_map[selected_query]
df = pd.read_sql_query(query, conn)
st.write(df)
