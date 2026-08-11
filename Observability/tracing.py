
from langfuse import get_client
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

def setup_tracing():
    langfuse = get_client()
    if langfuse.auth_check():
        GoogleADKInstrumentor().instrument()
        print("Langfuse tracing enabled for Google ADK Agent and Tools.")
    else:
        # log/warn, don't crash
        print("Langfuse authentication failed - tracing will not be enabled.")
        pass