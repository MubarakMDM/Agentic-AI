from google.adk.agents import Agent
from google.adk.code_executors import BuiltInCodeExecutor

data_agent = Agent(
    model="gemini-2.5-flash",
    name="data_agent",
    description="Specialist in running code and computing statistics.",
    instruction="Write and execute code to analyze the data given to you.",
    code_executor=BuiltInCodeExecutor(),
)