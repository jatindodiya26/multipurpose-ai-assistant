import os

import numexpr
import requests

from dotenv import load_dotenv
from currency_converter import CurrencyConverter
from langchain_core.tools import tool
from tavily import TavilyClient


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()


# --------------------------------------------------
# Calculator Tool
# --------------------------------------------------

@tool
def calculator(expression: str) -> str:
    """
    Calculate a mathematical expression.

    Use this tool for arithmetic calculations.
    """

    try:

        result = numexpr.evaluate(expression)

        return str(result)

    except Exception as e:

        return f"Unable to calculate the expression: {str(e)}"


# --------------------------------------------------
# Currency Converter Tool
# --------------------------------------------------

currency_converter = CurrencyConverter()


@tool
def currency_conversion(
    amount: float,
    from_currency: str,
    to_currency: str
) -> str:
    """
    Convert an amount from one currency to another.

    Example:
    100 USD to INR
    50 EUR to USD
    """

    try:

        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        result = currency_converter.convert(
            amount,
            from_currency,
            to_currency
        )

        return (
            f"{amount} {from_currency} = "
            f"{result:.2f} {to_currency}"
        )

    except Exception as e:

        return (
            f"Unable to convert currency. "
            f"Please check the currency codes. "
            f"Error: {str(e)}"
        )


# --------------------------------------------------
# Weather Tool
# --------------------------------------------------

@tool
def weather(city: str) -> str:
    """
    Get the current weather for a city.
    """

    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:

        return (
            "OPENWEATHER_API_KEY is missing. "
            "Please add it to the .env file."
        )

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        data = response.json()

        if response.status_code != 200:

            return (
                f"Unable to get weather for {city}. "
                f"{data.get('message', 'Unknown error')}"
            )

        temperature = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]

        description = data["weather"][0]["description"]

        wind_speed = data["wind"]["speed"]

        return (
            f"Weather in {city}:\n"
            f"Temperature: {temperature}°C\n"
            f"Feels like: {feels_like}°C\n"
            f"Condition: {description}\n"
            f"Humidity: {humidity}%\n"
            f"Wind speed: {wind_speed} m/s"
        )

    except requests.exceptions.RequestException as e:

        return (
            f"Unable to connect to the weather service: {str(e)}"
        )

    except Exception as e:

        return (
            f"Unable to process weather information: {str(e)}"
        )


# --------------------------------------------------
# Web Search Tool
# --------------------------------------------------

@tool
def web_search(query: str) -> str:
    """
    Search the internet for up-to-date information.

    Use this tool when the user asks about:
    current events,
    recent information,
    latest news,
    current facts,
    or information not available in the uploaded PDF.
    """

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:

        return (
            "TAVILY_API_KEY is missing. "
            "Please add it to the .env file."
        )

    try:

        tavily_client = TavilyClient(
            api_key=api_key
        )

        response = tavily_client.search(
            query=query,
            search_depth="basic",
            max_results=5
        )

        results = response.get("results", [])

        if not results:

            return "No search results found."

        formatted_results = []

        for result in results:

            title = result.get("title", "")
            content = result.get("content", "")
            url = result.get("url", "")

            formatted_results.append(
                f"Title: {title}\n"
                f"Content: {content}\n"
                f"URL: {url}"
            )

        return "\n\n".join(formatted_results)

    except Exception as e:

        return f"Web search failed: {str(e)}"