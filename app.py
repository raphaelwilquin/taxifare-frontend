import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL") or st.secrets["API_URL"]

st.title("🚕 Taxi Fare Prediction")

st.write("Enter your trip details to estimate your taxi fare.")

pickup_date = st.date_input("Pickup date")
pickup_time = st.time_input("Pickup time (UTC)")

pickup_longitude = st.number_input("Pickup longitude", value=-73.9857, format="%.6f")

pickup_latitude = st.number_input("Pickup latitude", value=40.7484, format="%.6f")

dropoff_longitude = st.number_input("Dropoff longitude", value=-73.9680, format="%.6f")

dropoff_latitude = st.number_input("Dropoff latitude", value=40.7850, format="%.6f")

passenger_count = st.number_input(
    "Number of passengers", min_value=1, max_value=6, value=1
)

if st.button("Predict fare"):
    params = {
        "pickup_datetime": f"{pickup_date} {pickup_time} UTC",
        "pickup_longitude": pickup_longitude,
        "pickup_latitude": pickup_latitude,
        "dropoff_longitude": dropoff_longitude,
        "dropoff_latitude": dropoff_latitude,
        "passenger_count": passenger_count,
    }

     url = API_URL.rstrip("/")
    if not url.endswith("/predict"):
        url += "/predict"

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()

        fare = response.json()["fare"]

        st.success(f"Estimated fare: ${fare:.2f}")

    except requests.exceptions.RequestException as e:
        st.error(f"API error: {e}")
