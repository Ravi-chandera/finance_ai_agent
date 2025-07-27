import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
import asyncio
from google.adk.agents import Agent
from google.adk.tools import google_search
import json


# Load environment variables
with open("config.json", 'r') as file:
    config = json.load(file)

api_key = config["GOOGLE_API_KEY"]
os.environ['GOOGLE_API_KEY'] = api_key

# --- Agent Setup ---
GEMINI_2_FLASH = "gemini-2.0-flash"
APP_NAME = "simple_app"
USER_ID = "user1"
SESSION_ID = "session1"
STOCK_NAME = os.getenv("STOCK_NAME")

# Create a simple story generator agent
root_agent = Agent(
    name="google_search_agent",
    model="gemini-2.5-flash",
    instruction="Answer questions using Google Search when needed. Always cite sources.",
    description="Professional search assistant with Google Search capabilities",
    tools=[google_search]
)

# Initial session state
# INITIAL_STATE = {"topic": "A brave cat in a big city"}

async def get_latest_price_of_tcs_stock():
    question = "Latest price of TCS stock in NSE. Along with latest price, provide 24-hour change, weekly change, monthly change, annual change, market capitalization, all-time-high, all-time-low and dividends."
    # Setup session and runner
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service
    )

    content = types.Content(role='user', parts=[types.Part(text=question)])

    # Run the agent
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)
    async for event in events:
        if event.is_final_response() and event.content and event.content.parts:
            return event.content.parts[0].text
    return "No response from agent"

if __name__ == "__main__":
    print(asyncio.run(get_latest_price_of_tcs_stock()))