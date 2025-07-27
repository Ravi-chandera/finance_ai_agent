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

domain_check_prompt = (
    "You are a domain classifier. "
    "Given a user question or text, determine if it is related to the finance domain. "
    "Respond ONLY with a single line of JSON in the following format: {\"is_finance\": true} or {\"is_finance\": false}. "
    "Do not provide any explanation or extra text. "
    "If the question is about financial reports, markets, stocks, investments, accounting, economics, or similar topics, return true. "
    "Otherwise, return false."
)
# Create a simple story generator agent
root_agent = Agent(
    name="finance_domain_check_agent",
    model="gemini-2.5-flash",
    instruction=domain_check_prompt,
    description="This agent is used to check if the given domain is related to finance or not"
)

# Initial session state
# INITIAL_STATE = {"topic": "A brave cat in a big city"}

async def domain_check(question):
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
            # print("Story:", event.content.parts[0].text)
            return event.content.parts[0].text
    raise Exception("No response")


if __name__ == "__main__":
    print(asyncio.run(domain_check("Analyze the financial reports and transcripts for the last three quarters and provide a qualitative forecast for the upcoming quarter. Your forecast must identify key financial trends (e.g., revenue growth, margin pressure), summarize management's stated outlook, and highlight any significant risks or opportunities mentioned")))