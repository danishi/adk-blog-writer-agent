import os

from dotenv import load_dotenv
from google.adk.tools import ToolContext
from google.genai import Client, types


async def generate_image(prompt: str, tool_context: ToolContext):
    """Generates an image based on the prompt."""
    MODEL_IMAGE = "imagen-3.0-generate-002"

    load_dotenv()

    # Only Vertex AI supports image generation for now.
    client = Client(
        vertexai=True,
        project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION"),
    )

    response = client.models.generate_images(
        model=MODEL_IMAGE,
        prompt=prompt,
        config={"number_of_images": 1},
    )
    if not response.generated_images:
        return {"status": "failed"}
    image_bytes = response.generated_images[0].image.image_bytes
    image_name = os.getenv("IMAGE_FILE_NAME", "image.png")
    await tool_context.save_artifact(
        image_name,
        types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
    )
    return {
        "status": "success",
        "detail": "Image generated successfully and stored in artifacts.",
        "filename": image_name,
    }
