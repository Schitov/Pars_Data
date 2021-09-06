import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_key")
city = "Moscow"

def get_city_weather(city=city, api_key=""):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
        repo = requests.get(url).json()
        print(f"""The weather is {repo["weather"][0]["main"]} in {city}.\nFahrenheit temperature is {repo["main"]["temp"]} degrees""")
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        raise SystemExit(e)


get_city_weather(city, api_key)
