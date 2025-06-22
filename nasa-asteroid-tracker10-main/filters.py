import streamlit as st
from datetime import datetime

def get_filters():
    st.sidebar.header("🔎 Filters")
    start_date = st.sidebar.date_input("Start Date", value=datetime(2024, 1, 1))
    end_date = st.sidebar.date_input("End Date", value=datetime(2025, 1, 1))
    velocity_min = st.sidebar.slider("Min Velocity (km/h)", 0, 150000, 0, step=1000)
    astro_limit = st.sidebar.slider("Max Astronomical Unit", 0.0, 1.0, 0.5)
    lunar_limit = st.sidebar.slider("Max Lunar Distance", 0.0, 100.0, 10.0)
    hazardous = st.sidebar.radio("Potentially Hazardous", ["All", "Yes", "No"])

    st.sidebar.markdown("---")
    selected_query = st.sidebar.selectbox("📊 Choose Analysis", [
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

    return start_date, end_date, velocity_min, astro_limit, lunar_limit, hazardous, selected_query
