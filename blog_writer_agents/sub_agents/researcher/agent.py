"""researcher_agent: for generating blog ideas based on user input"""

from google.adk import Agent
from google.adk.tools import google_search

from . import prompt

MODEL = "gemini-2.5-flash-preview-05-20" 

researcher_agent = Agent(
    model=MODEL,
    name="researcher_agent",
    instruction=prompt.RESEARCHER_PROMPT,
    output_key="researcher_agent_output",
    tools=[google_search],
)
