import requests
from typing import Union, Tuple

class WeatherAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    def get_weather(self, location: Union[str, Tuple[float, float]], units: str = 'metric') -> dict:
        """Get weather data with improved error handling"""
        params = {
            'appid': self.api_key,
            'units': units
        }
        
        try:
            if isinstance(location, str):
                params['q'] = location
            elif isinstance(location, (tuple, list)) and len(location) == 2:
                params['lat'] = str(location[0])
                params['lon'] = str(location[1])
            else:
                raise ValueError("Invalid location format")
            
            response = requests.get(self.base_url, params=params, timeout=5)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {'error': f"API request failed: {str(e)}"}
        except Exception as e:
            return {'error': f"An error occurred: {str(e)}"}
    
    def get_readable_weather(self, location: Union[str, Tuple[float, float]], units: str = 'metric') -> dict:
        """Get formatted weather information with better error handling"""
        data = self.get_weather(location, units)
        
        if 'error' in data:
            return data
        
        try:
            return {
                'location': data.get('name', 'Unknown location'),
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'conditions': data['weather'][0]['description'].title(),
                'wind_speed': data['wind']['speed'],
                'icon': data['weather'][0]['icon'] if 'weather' in data else None
            }
        except KeyError as e:
            return {'error': f"Missing expected data in API response: {str(e)}"}