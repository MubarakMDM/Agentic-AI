from google.adk.agents import Agent
from google.adk.tools import google_search

research_agent = Agent(
    model="gemini-2.5-flash",
    name="research_agent",
    description="Specialist in finding and summarizing web sources.",
    instruction="Use Google Search to gather relevant, current sources on the topic.",
    tools=[google_search],
)