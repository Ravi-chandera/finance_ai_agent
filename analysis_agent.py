import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
import asyncio
from google.adk.agents import Agent
from google.adk.tools import google_search
from get_latest_price import get_latest_price_of_tcs_stock
import json


# Load environment variables
with open("config.json", 'r') as file:
    config = json.load(file)

api_key = config["GOOGLE_API_KEY"]
os.environ['GOOGLE_API_KEY'] = api_key

async def latest_price_details():
    latest_details = await get_latest_price_of_tcs_stock()
    return latest_details
latest_details = asyncio.run(latest_price_details())

# --- Agent Setup ---
GEMINI_2_FLASH = "gemini-2.0-flash"
APP_NAME = "simple_app"
USER_ID = "user1"
SESSION_ID = "session1"
STOCK_NAME = os.getenv("STOCK_NAME")

analysis_prompt = (
    "You are a financial analyst. Analyze the provided financial reports and management transcripts for the last three quarters. Report should be aesthetic. "
    "Use the SPECIFIED QUESTIONS as a guide for what your report should contain. "
    "Write a detailed, well-structured qualitative forecast for the upcoming quarter. "
    "Your analysis must:\n"
    "- Address each aspect of the SPECIFIED QUESTIONS in a cohesive narrative (not Q&A format)\n"
    "- Identify and discuss key financial trends (such as revenue growth, margin pressure, profitability, client metrics, etc.)\n"
    "- Summarize management's stated outlook and expectations for the upcoming quarter\n"
    "- Highlight and explain any significant risks or opportunities mentioned by management or evident in the data\n"
    "- Do not return intial commentry about you, start your report directly.\n"
    "Synthesize the information into a clear, insightful report as a professional analyst would, providing reasoning and supporting evidence for your forecast."
    "Latest details of TCS stock:"
    f"{latest_details}"
)

# Create a simple story generator agent
root_agent = Agent(
    name="google_search_agent",
    model="gemini-2.5-flash",
    instruction=analysis_prompt,
    description="It gives analysis of stock from given details in markdown format.",
)

# Initial session state
# INITIAL_STATE = {"topic": "A brave cat in a big city"}

async def analysis_agent(question):
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
