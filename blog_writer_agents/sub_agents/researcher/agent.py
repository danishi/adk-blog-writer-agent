"""researcher_agent: for generating blog ideas based on user input"""
import logging
import copy
from google.adk import Agent
from google.adk.tools import google_search
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.genai import types
from typing import Optional

from . import prompt

logging.basicConfig(level=logging.INFO, force=True)
MODEL = "gemini-2.5-flash-preview-05-20"


def grounding_metadata_callback(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """LLM応答を受信後に検査/変更します。"""
    agent_name = callback_context.agent_name
    logging.info(f"[Callback] After model call for agent: {agent_name}")

    # --- 検査 ---
    original_text = ""
    if llm_response.content and llm_response.content.parts:
        if llm_response.content.parts[0].text:
            original_text = llm_response.content.parts[0].text
            logging.info(f"[Callback] original_text:\n{original_text}")

            modified_parts = [copy.deepcopy(part) for part in llm_response.content.parts]

            grounding_chunks = []
            grounding_metadata = getattr(llm_response, 'grounding_metadata', None)

            if grounding_metadata:
                chunks = getattr(grounding_metadata, 'grounding_chunks', None)
                if isinstance(chunks, list):
                    grounding_chunks = chunks
                else:
                    logging.warning("[Callback] grounding_chunks is None or not a list.")
            else:
                logging.warning("[Callback] grounding_metadata is None.")

            logging.info(f"[Callback] grounding_chunks: {grounding_chunks}")

            references = {}
            for i, chunk in enumerate(grounding_chunks):
                web = getattr(chunk, 'web', None)
                if web:
                    uri = getattr(web, 'uri', None)
                    title = getattr(web, 'title', None)
                    if uri and title:
                        references[uri] = {"index": i + 1, "title": title, "uri": uri}

            modified_text = ""
            for line in original_text.split("\n"):
                modified_line = line
                if hasattr(llm_response.grounding_metadata, 'grounding_supports'):
                    for support in llm_response.grounding_metadata.grounding_supports:
                        segment = getattr(support, 'segment', None)
                        segment_text = getattr(segment, 'text', None)
                        if segment_text and segment_text in line:
                            for chunk_index in support.grounding_chunk_indices:
                                chunk = grounding_chunks[chunk_index]
                                web = getattr(chunk, 'web', None)
                                if web:
                                    uri = getattr(web, 'uri', None)
                                    if uri in references:
                                        ref = references[uri]
                                        # 表示例: [1. Wikipedia](https://example.com)
                                        ref_tag = f"[{ref['index']}. {ref['title']}]({ref['uri']})"
                                        modified_line = modified_line.replace(segment_text, f"{segment_text} {ref_tag}")
                modified_text += f"{modified_line}\n"

            modified_parts[0].text = modified_text

            logging.info(f"[Callback] Returning modified response:\n{modified_text}")
            new_response = LlmResponse(
                content=types.Content(role="model", parts=modified_parts),
                grounding_metadata=llm_response.grounding_metadata
            )
            return new_response

        elif llm_response.content.parts[0].function_call:
            logging.info(f"[Callback] Inspected response: Contains function call '{llm_response.content.parts[0].function_call.name}'. No text modification.")
            return None

        else:
            logging.info("[Callback] Inspected response: No text content found.")
            return None

    elif llm_response.error_message:
        logging.info(f"[Callback] Inspected response: Contains error '{llm_response.error_message}'. No modification.")
        return None

    else:
        logging.info("[Callback] Inspected response: Empty LlmResponse.")
        return None


researcher_agent = Agent(
    model=MODEL,
    name="researcher_agent",
    instruction=prompt.RESEARCHER_PROMPT,
    output_key="researcher_agent_output",
    tools=[google_search],
    after_model_callback=grounding_metadata_callback,
)
