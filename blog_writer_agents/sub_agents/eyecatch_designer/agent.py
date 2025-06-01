"""eyecatch_designer_agent: for creating eyecatch"""

import os

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.tools import ToolContext, load_artifacts
from google.genai import Client, types


MODEL = "gemini-2.5-flash-preview-05-20" 
MODEL_IMAGE = "imagen-3.0-generate-002"

load_dotenv()

# Only Vertex AI supports image generation for now.
client = Client(
    vertexai=True,
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION"),
)


def generate_image(img_prompt: str, tool_context: "ToolContext"):
    """Generates an image based on the prompt."""
    response = client.models.generate_images(
        model=MODEL_IMAGE,
        prompt=img_prompt,
        config={"number_of_images": 1},
    )
    if not response.generated_images:
        return {"status": "failed"}
    image_bytes = response.generated_images[0].image.image_bytes
    tool_context.save_artifact(
        "image.png",
        types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
    )
    return {
        "status": "success",
        "detail": "Image generated successfully and stored in artifacts.",
        "filename": "image.png",
    }


EYECATCH_CREATE_PROMPT = """
あなたはブログ記事のアイキャッチ画像をデザインする専門家です。ユーザーが提供するテーマやブランドイメージに基づいて、プロフェッショナルなアイキャッチ画像を作成します。
"""

eyecatch_designer_agent = Agent(
    model=MODEL,
    name="eyecatch_designer_agent",
    description=(
        "eyecatch_designer_agent: for creating eyecatch images for blog posts"
        " based on user-provided themes and brand images."
        " The agent generates a professional eyecatch image that visually represents"
    ),
    instruction=EYECATCH_CREATE_PROMPT,
    output_key="eyecatch_designer_output",
    tools=[generate_image, load_artifacts],
)
