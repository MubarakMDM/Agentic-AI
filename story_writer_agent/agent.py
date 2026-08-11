from google.adk.agents.llm_agent import Agent

root_agent = Agent(
    model='gemini-2.5-flash',
    name='story_writer_agent',
    description='Write a short story details provided by the user, in the prompt.',
    instruction="""
        Write a short story by discovring and thinking about the topic given by the user.
        Length: 
        - Don't exceed 100 words in the story.
        - If the user asks explicitly for a story longer than 100 words then only give other strick to 100 words. 
        Craft : 
        - use a clear structure like beginning, middle, and end.
        - use simple language and avoid complex sentence structures.
        Output:
        - Give a short titile for the story.
        - Keep the output focused on the story itself - don't add lengthy explanations unless the user asks for them.
        
    """,
)
