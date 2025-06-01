"""blog_editor_agent: formatting and editing blog content```"""

from google.adk import Agent

from . import prompt

MODEL = "gemini-2.5-pro-preview-05-06" 

blog_editor_agent = Agent(
    model=MODEL,
    name="blog_editor_agent",
    instruction=prompt.BLOG_CREATE_PROMPT,
    output_key="blog_editor_output",
)
