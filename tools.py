from langchain.agents import Tool
from langchain.tools import Tool
import requests
from datetime import datetime, timedelta
from ddgs import DDGS
import re

open_meteo_API="https://api.open-meteo.com/v1/forecast"
duckDuckGo_API=""
frankfurter_API="https://api.frankfurter.app/latest"

# re.match() vs re.search()
# re.match(pattern, string)
# → Checks for a match only at the beginning of the string.
# → Returns None if the pattern is not at position 0.
# re.search(pattern, string)
# → Scans the entire string.
# → Returns the first match found anywhere.
# text = "I love Paris"
# re.match("Paris", text)   # None (not at start)
# re.search("Paris", text)  # Match object (found in string)


def get_weather_by_city(user_input: str) -> str:
    # --- Step 1: Parse city and date keyword ---
    # Example patterns: "Tokyo today", "Paris tomorrow", "New York next 7 days"
    city_match = re.match(r"([a-zA-Z\s]+)", user_input)  #r"([a-zA-ZÀ-ÿ\s'-]+)"
    if not city_match:
        return "Could not parse city from input."
    city = city_match.group(1).strip()

    days = 1  # default
    if "tomorrow" in user_input.lower():
        days = 2
    elif "next" in user_input.lower():
        n_match = re.search(r"next\s+(\d+)", user_input.lower())
        if n_match:
            days = min(int(n_match.group(1)), 10)
        else:
            days = 2  # fallback
    elif "today" in user_input.lower():
        days = 1

    # --- Step 2: Geocode city ---
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_params = {"name": city, "count": 1, "format": "json"}
    geo_resp = requests.get(geo_url, params=geo_params)
    if geo_resp.status_code != 200:
        return "Failed to geocode city."
    
    geo_data = geo_resp.json()
    if "results" not in geo_data or not geo_data["results"]:
        return f"City not found: {city}"
    
    loc = geo_data["results"][0]
    lat = loc["latitude"]
    lon = loc["longitude"]
    resolved_name = f"{loc['name']}, {loc.get('country', '')}"

    # --- Step 3: Fetch weather ---
    start_date = datetime.today().date()
    end_date = start_date + timedelta(days=days-1)

    weather_params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,weathercode",
        "timezone": "auto",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }

    weather_resp = requests.get(open_meteo_API, params=weather_params)
    if weather_resp.status_code != 200:
        return "Failed to fetch weather data."

    data = weather_resp.json()
    daily = data.get("daily")
    if not daily:
        return "No daily weather data available."

    # --- Step 4: Format output ---
    output = [f"Weather forecast for {resolved_name}:"]
    for i in range(days):
        date = daily['time'][i]
        max_temp = daily['temperature_2m_max'][i]
        min_temp = daily['temperature_2m_min'][i]
        code = daily['weathercode'][i]
        output.append(f"- {date}: High {max_temp}°C, Low {min_temp}°C, Weather code {code}")

    return "\n".join(output)


def web_search(query: str) -> str:
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(
            query,
            region="wt-wt",
            safesearch="moderate",
            timelimit=None,
            max_results=5,
        ):
            results.append(
                f"- {r['title']}\n  {r['body']}\n  Source: {r['href']}"
            )
    if not results:
        return "No results found."

    return "Top web search results:\n" + "\n\n".join(results)


def convert_currency(input: str) -> str:
    # --- Parse user input ---
    pattern = r'(?:(\d+(?:\.\d+)?)\s*)?([a-zA-Z]{3})\s*(?:to|in)?\s*([a-zA-Z]{3})'
    match = re.search(pattern, input.lower())

    if not match:
        return "Could not parse currency conversion request."

    amount = float(match.group(1)) if match.group(1) else 1.0
    from_currency = match.group(2).upper()
    to_currency = match.group(3).upper()

    params = {
        "amount": amount,
        "from": from_currency,
        "to": to_currency
    }

    response = requests.get(frankfurter_API, params=params)
    if response.status_code != 200:
        return "Failed to fetch exchange rates."

    data = response.json()
    rates = data.get("rates", {})

    if to_currency not in rates:
        return f"Conversion from {from_currency} to {to_currency} is not available."

    converted_amount = rates[to_currency]

    # --- Format response ---
    return (
        f"{amount} {from_currency} = {round(converted_amount, 2)} {to_currency}"
    )


def build_tools():
    weather_tool = Tool(
        name="Weather",
        func=get_weather_by_city,
        description=(
            "Get the weather forecast for a city. "
            "You can get today, tomorrow, or up to 10 days. "
            "Input: city name, e.g. 'Tokyo', 'Paris'. "
            "Optional: number of days (default 1)."
        )
    )
    websearch_tool = Tool(
        name="WebSearch",
        func=web_search,
        description=(
            "Search the web for up-to-date information using DuckDuckGo. "
            "Input should be a natural language search query."
        )
    )
    currency_tool = Tool(
        name="CurrencyConverter",
        func=convert_currency,
        description=(
            "Convert between global currencies using Frankfurter (ECB) exchange rates. "
            "Input should be like '100 USD to EUR' or 'GBP to INR'."
        )
    )

    # tools_list for MCP routing
    tools_list = [
        {"name": weather_tool.name, "keywords": ["weather","temperature","forecast","today","tomorrow","days"], "func": weather_tool.func},
        {"name": currency_tool.name, "keywords": ["convert","currency","usd","eur","gbp","inr"], "func": currency_tool.func},
        {"name": websearch_tool.name, "keywords": ["search","info","who","what","where"], "func": websearch_tool.func}
    ]

    return [weather_tool, websearch_tool, currency_tool], tools_list

# Usage
tools, tools_list = build_tools()

