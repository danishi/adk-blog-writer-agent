"""ルートエージェント"""

import copy
import base64
import os
from io import BytesIO
from PIL import Image
import logging

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from dotenv import load_dotenv

from .sub_agents.researcher import researcher_agent
from .sub_agents.blog_editor import blog_editor_agent
from .tools.generate_image import generate_image
from .tools.get_current_datetime import get_current_datetime
from google.adk.tools import load_artifacts
from google.genai.types import Part
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse

load_dotenv()
logging.basicConfig(level=logging.ERROR)

MODEL = "gemini-2.5-pro-preview-05-06"
IMAGE_FILE_NAME = os.getenv("IMAGE_FILE_NAME", "image.png")

BLOG_COORDINATOR_PROMPT = """
マーケティングとコンテンツ戦略の専門家です。あなたの目的は、ユーザーが魅力的なブログ記事を作成し、多くの反響を得られるようにサポートすることです。
デジタル上の個性を明確に定義し、それを形にしていくプロセスを段階的に案内してください。

各ステップでは、必ず指定されたサブエージェントを呼び出し、指定された入力および出力形式を厳密に守ってください。
必ずしも各ステップを遵守する必要はなく、ユーザーの求めがあれば柔軟に振る舞ってください。

---

### ステップ 1：ブログのための魅力的なテーマやネタを決める（Subagent: `researcher`）

* **入力内容：** ユーザーにブログのテーマやキーワード（例：旅行、ガジェット、育児など）を尋ねてください。
* **実行内容：** そのキーワードを使ってリサーチャーサブエージェントを呼び出してください。
* **期待される出力：** リサーチャーサブエージェントは、少なくとも10個の鮮度の高いブログ記事のアイデアを生成します。
* **注意点：** ユーザーが選んだテーマに基づいて、ブログ記事のアイデアを提案してください。例えば、旅行なら「世界の絶景スポット」や「バックパッカーの旅のコツ」など。
  ユニークで読者の関心を引くような、ブランド性の高い名前を提案してください。
  アイデアのもととなったURLが提示されている場合はそれも示しましょう。
  リストをユーザーに提示し、1つを選んでもらいましょう。

---

### ステップ 2：プロフェッショナルなブログ記事を作成する（Subagent: `blog_editor`）

* **入力内容：** ユーザーが選んだブログ記事のテーマやネタ。
* **実行内容：** ブログ編集者サブエージェントを使って、選ばれたテーマに基づいてブログ記事を作成してください。
* **期待される出力：** プロフェッショナルなブログ記事が生成され内容の全文が出力されます。
* **注意点：** 記事はSEOを意識し、読者の興味を引くような内容にしてください。見出しや段落分けも適切に行い、読みやすい構成にしてください。
  また、記事の最後には読者に行動を促すCTA（Call to Action）を含めることも忘れずに。

---

### ステップ 3：ブログの印象を決定づけるアイキャッチをデザインする（Tool: `generate_image`）

* **入力内容：** ユーザーが選んだブログ記事のテーマやネタ、およびブランドイメージ。
* **実行内容：** 画像生成ツールを使って、ブログ用のアイキャッチ画像を作成してください。
* **期待される出力：** プロフェッショナルで魅力的なアイキャッチ画像が生成されます。
* **注意点：** アイキャッチ画像は、ブログ記事の内容を視覚的に表現し、読者の興味を引くものでなければなりません。
  ブランドカラーやフォントを使用して、一貫したブランドイメージを保つようにしてください。

---

### サブエージェント使用時の注意事項：

ユーザーが迷わず進めるように、それぞれのステップで丁寧にサブエージェントに委任する背景と意図も説明してください。
"""


async def callback_load_artifact(
    callback_context: CallbackContext,
    llm_response: LlmResponse
) -> LlmResponse:

    try:
        if not (llm_response.content and llm_response.content.parts):
            return llm_response

        parts_new = []
        for part in copy.deepcopy(llm_response.content.parts):
            parts_new.append(part)
            if not part.text:
                continue

            image_artifact = await callback_context.load_artifact(filename=IMAGE_FILE_NAME)
            if not image_artifact:
                part.text = part.text.replace(
                    f'<artifact>{IMAGE_FILE_NAME}</artifact>',
                    f'<artifact>_none_{IMAGE_FILE_NAME}</artifact>'
                )
                parts_new[-1] = part
            # Convert PNG to JPEG to reduce data size
            image_bytes = image_artifact.inline_data.data
            img = Image.open(BytesIO(image_bytes)).convert('RGB')
            img = img.resize((500, int(img.height * (500 / img.width))))
            jpg_buffer = BytesIO()
            img.save(jpg_buffer, 'JPEG', quality=70)
            jpg_binary = jpg_buffer.getvalue()
            base64_encoded = base64.b64encode(jpg_binary).decode('utf-8')
            mime_string = f'data:image/jpeg;base64,{base64_encoded}'
            parts_new.append(Part.from_text(text=mime_string))

        llm_response_new = copy.deepcopy(llm_response)
        llm_response_new.content.parts = parts_new
        return llm_response_new

    except Exception as e:  # fall back to the original response
        logging.error(e)
        return llm_response


blog_coordinator = LlmAgent(
    name="blog_coordinator",
    model=MODEL,
    description=(
        "ブログ記事の作成を支援するエージェントです。"
        "ユーザーが魅力的なブログ記事を作成し、多くの反響を得られるようにサポートします。"
        "デジタル上の個性を明確に定義し、それを形にしていくプロセスを段階的に案内します。"
        "サブエージェントを呼び出して、ブログ記事のテーマ決定、記事作成、アイキャッチデザインを行います。"
        "各ステップでは、ユーザーに必要な情報を尋ね、サブエージェントに適切な入力を提供します。"
    ),
    instruction=BLOG_COORDINATOR_PROMPT,
    tools=[
        AgentTool(agent=researcher_agent),
        AgentTool(agent=blog_editor_agent),
        generate_image,
        get_current_datetime,
        load_artifacts
    ],
    sub_agents=[],
    after_model_callback=callback_load_artifact
)

root_agent = blog_coordinator
