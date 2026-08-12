from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from .research_agent import research_agent
from .data_agent import data_agent
from .writer_agent import writer_agent

root_agent = Agent(
    model="gemini-2.5-flash",
    name="manager_agent",
    instruction="""You coordinate research reports. For each request:
    1. Call research_agent to gather sources
    2. Call data_agent if the topic needs numeric analysis
    3. Call writer_agent to draft the final report
    """,
    tools=[
        AgentTool(research_agent),
        AgentTool(data_agent),
        AgentTool(writer_agent),
    ],
)