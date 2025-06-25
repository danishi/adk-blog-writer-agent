"""blog_editor_agent: formatting and editing blog content```"""

from google.adk import Agent
from google.adk.tools import google_search
from google.adk.planners import BuiltInPlanner
from google.genai import types

from . import prompt

MODEL = "gemini-2.5-pro"

blog_editor_agent = Agent(
    model=MODEL,
    name="blog_editor_agent",
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            thinking_budget=5120,
        )
    ),
    instruction=prompt.BLOG_CREATE_PROMPT,
    output_key="blog_editor_output",
    tools=[google_search],
)
