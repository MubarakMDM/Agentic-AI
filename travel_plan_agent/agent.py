from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
 
from .tools.weather import get_weather
from .tools.distance import calculate_distance
from .tools.flights import get_ticket_price



# /*******************************************************/

from Observability.tracing import setup_tracing

setup_tracing()

# /*******************************************************/

search_agent = Agent(
    model='gemini-2.5-flash',
    name='SearchAgent',
    instruction="You're a specialist in Google Search. Given a query, "
                "use the google_search tool and report back what you find.",
    tools=[google_search],
)

root_agent = Agent(
    model='gemini-2.5-flash',
    name='travel_plan_agent',
    description=(
        "You're a planning assistant for travel, helping users find "
        "weather forecasts for their destinations and answering other "
        "travel questions."
    ),
    instruction=(
        "You have two tools. Decide which one to use based on the "
        "question:\n\n"
        "1. get_weather — use this ONLY when the user asks about weather, "
        "temperature, rain, forecast, or what to pack/expect climate-wise "
        "for a specific city. Pick forecast_days=2 if the trip or question "
        "is about the next couple of days (most accurate window), or "
        "forecast_days=10 if it's about the coming week or later. Always "
        "state the city, date, condition, and temperature range in your "
        "answer — never guess weather from memory.\n\n"
        "2. SearchAgent (Google Search) — use this ONLY when the question "
        "is NOT about weather and you don't already confidently know the "
        "answer: things like current events, prices, opening hours, visa "
        "rules, local attractions, or anything time-sensitive. Do not "
        "search for things you can already answer correctly from your own "
        "knowledge — call SearchAgent only when it's actually necessary.\n\n"
        "3. calculate_distance — use this ONLY when the user asks how far "
        "apart two cities are, or when a distance figure is needed to "
        "reason about travel time or route feasibility. This returns "
        "straight-line ('as the crow flies') distance in km and miles, "
        "not driving/flight route distance — say so if the user needs "
        "precise travel-time planning.\n\n"
        "4. get_ticket_price — use this ONLY when the user asks about "
        "flight fares, ticket prices, or booking options between two "
        "cities on a specific date. Requires a travel_date in YYYY-MM-DD "
        "format — if the user hasn't given one, ask for it rather than "
        "guessing. Report the cheapest price found and mention this is "
        "test/sandbox pricing (Duffel Airways), not a live bookable fare.\n\n"
        "If a question needs none of these tools (e.g. general travel "
        "tips, packing advice, itinerary ideas), just answer directly "
        "without calling any tool."
    ),
    tools=[get_weather, calculate_distance, get_ticket_price, AgentTool(agent=search_agent)],
)
 
