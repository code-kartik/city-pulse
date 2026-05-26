import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

def fetch_weather_data(lat, lon):
    # Fetch data from OpenWeather API
    api_key = os.getenv("OPEN_WEATHER_API_KEY")
    api_endpoint = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"

    response = requests.get(api_endpoint)
    if response.status_code == 200:
        return response.json()
    else:        
        print(f"Error fetching data: {response.status_code}")
        return None
    
def fetch_traffic_data(lat, lon):
    api_key = os.getenv("TOMTOM_API_KEY")
    api_endpoint = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?key={api_key}&point={lat},{lon}"
    response = requests.get(api_endpoint)
    if response.status_code == 200:
        return response.text  # TomTom API returns XML, you may want to parse it
    else:
        print(f"Error fetching traffic data: {response.status_code}")
        return None

if __name__ == "__main__":
    # Example coordinates for a city (e.g., New York City)
    latitude = 40.7128
    longitude = -74.0060
    
    weather_data = fetch_weather_data(latitude, longitude)
    if weather_data:
        print(weather_data)
    else:
        print("Failed to retrieve weather data.")

    traffic_data = fetch_traffic_data(latitude, longitude)
    if traffic_data:
        print(traffic_data)
    else:
        print("Failed to retrieve traffic data.")