from google.adk.agents import Agent

writer_agent = Agent(
    model="gemini-2.5-flash",
    name="writer_agent",
    description="Specialist in drafting clear, well-structured report text.",
    instruction="Turn the given research and analysis into a polished report section.",
)