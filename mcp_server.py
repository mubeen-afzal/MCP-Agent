import os
from datetime import datetime
from dotenv import load_dotenv

import weatherapi
from weatherapi.rest import ApiException

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MCP APP")

load_dotenv()
WAETHER_API = os.getenv("WEATHER_API") # update this path to add your API Key from (https://www.weatherapi.com/)

configuration = weatherapi.Configuration()
configuration.api_key['key'] = WAETHER_API
api_instance = weatherapi.APIsApi(weatherapi.ApiClient(configuration))

@mcp.tool()
def get_weather_using_city_name(city_name: str) -> str:
    """
    Retrieves and formats the current weather information for a specified city 
    using the WeatherAPI service.

    Args:
        city_name (str): The name of the city for which to fetch the weather 
        data. This should be a valid location supported by WeatherAPI.

    Returns:
        str: A formatted string containing weather information including 
        location, condition, temperature, wind details, and humidity.

    Raises:
        ApiException: If there is an issue communicating with the WeatherAPI 
        service or processing the response data.
    """
    try:    
        data = api_instance.realtime_weather(city_name)

        # Extract data
        location = f"{data['location']['name']}, {data['location']['country']}"
        condition = data['current']['condition']['text']
        temp_c = data['current']['temp_c']
        feelslike_c = data['current']['feelslike_c']
        wind_kph = data['current']['wind_kph']
        wind_dir = data['current']['wind_dir']
        humidity = data['current']['humidity']

        # Format as clean readable string
        weather_summary = (
            f"🌍 Location: {location}\n"
            f"🌤️ Condition: {condition}\n"
            f"🌡️ Temperature: {temp_c}°C (Feels like {feelslike_c}°C)\n"
            f"💨 Wind: {wind_kph} km/h from {wind_dir}\n"
            f"💧 Humidity: {humidity}%"
        )

        return weather_summary
    except ApiException as e:
        print("Exception when calling APIsApi->astronomy: %s\n" % e)

@mcp.tool()
def get_current_date() -> str:
    """
    Returns the current system date in YYYY-MM-DD format.

    This function fetches the current date from the system clock 
    and formats it as a string in the standard ISO 8601 format.

    Returns:
        str: A string representing the current date (e.g., '2025-04-14').
    """
    return f'Current date is: {datetime.now().strftime("%Y-%m-%d")}'

@mcp.tool()
def get_current_time() -> str:
    """
    Returns the current system time in HH:MM:SS format (24-hour clock).

    This function retrieves the current time down to seconds and 
    returns it as a formatted string.

    Returns:
        str: A string representing the current time (e.g., '14:26:53').
    """
    return f'Current Time is: {datetime.now().strftime("%H:%M:%S")}'

@mcp.tool()
def read_txt_file(file_path: str) -> str:
    """
    Reads and returns the content of a text (.txt) file from the specified file path.

    This function opens a text file in read mode and retrieves its entire content 
    as a single string. It ensures the file is properly closed after reading. 
    If the file does not exist or cannot be read, an appropriate exception is raised.

    Args:
        file_path (str): The absolute or relative path to the .txt file.

    Returns:
        str: The full content of the file as a string.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        IOError: If an error occurs while reading the file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except IOError as e:
        raise IOError(f"Error reading file {file_path}: {e}")


if __name__ == "__main__":
    mcp.run(transport="stdio")