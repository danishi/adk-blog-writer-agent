import os
import streamlit as st
from dotenv import load_dotenv
import vertexai
from vertexai import agent_engines
from vertexai.preview import reasoning_engines
import logging
import asyncio 

from blog_writer_agents.agent import root_agent

logging.basicConfig(level=logging.INFO)
load_dotenv()


def init_vertexai():
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")
    vertexai.init(project=project_id, location=location)


def sidebar_inputs():
    st.sidebar.title("設定")
    agent_id = st.sidebar.text_input(
        "Agent Engine の ID",
        value=os.getenv("GOOGLE_CLOUD_AGENT_ENGINE_ID"),
        max_chars=20
    )
    user_id = st.sidebar.text_input(
        "ユーザー ID",
        value="user1",
        max_chars=10
    )
    return agent_id, user_id


# チャット履歴の初期化
if "messages" not in st.session_state:
    st.session_state["messages"] = []

st.title("ADK Blog Writer Agent")

agent_id, user_id = sidebar_inputs()

init_vertexai()

ENV = os.getenv("ENV", "local")

# Agent取得
@st.cache_resource
def get_remote_agent(agent_id):
    try:
        if ENV == "local":
            return reasoning_engines.AdkApp(
                agent=root_agent,
                enable_tracing=True,
            )
        else:
            return agent_engines.get(agent_id)
    except Exception as e:
        st.error(f"Agent取得エラー: {e}")
        st.stop()

remote_agent = get_remote_agent(agent_id)

# セッション管理
async def manage_session(user_id, agent_id):
    if (
        "session_id" not in st.session_state or
        st.session_state.get("last_agent_id") != agent_id or
        st.session_state.get("last_user_id") != user_id
    ):
        try:
            if ENV == "local":
                session = await remote_agent.create_session(user_id=user_id)
                st.session_state["session_id"] = session.id
            else:
                session = remote_agent.create_session(user_id=user_id)
                st.session_state["session_id"] = session["id"]

            st.session_state["last_agent_id"] = agent_id
            st.session_state["last_user_id"] = user_id
            st.session_state["messages"] = []
        except Exception as e:
            st.error(f"セッション作成エラー: {e}")
            st.stop()

asyncio.run(manage_session(user_id, agent_id))

# チャット履歴表示
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ユーザー入力
async def handle_user_input(prompt):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    # Agentへ問い合わせ
    try:
        full_response = ""
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            if ENV != "local":
                stream = asyncio.wrap_async_iterable(remote_agent.stream_query(
                    user_id=user_id,
                    session_id=st.session_state["session_id"],
                    message=prompt,
                ))
            else:
                # Wrap the synchronous generator to make it async
                async def async_generator_wrapper(sync_generator):
                    for item in sync_generator:
                        yield item
                stream = async_generator_wrapper(remote_agent.stream_query(
                    user_id=user_id,
                    session_id=st.session_state["session_id"],
                    message=prompt,
                ))
            async for event in stream:
                logging.info(f"Received event: {str(event)}")
                for i, part in enumerate(event["content"]["parts"]):
                    if "text" in part:
                        full_response += part["text"] + " "
                        message_placeholder.markdown(full_response + "▌")
                    if "function_call" in part:
                        message_placeholder.markdown(full_response + f"\n\n🔧 tool_calling: {str(part['function_call'])}")
                    if "function_response" in part:
                        message_placeholder.markdown(full_response + f"\n\n🔨 tool_response: {str(part['function_response'])}")
            message_placeholder.markdown(full_response)
        st.session_state["messages"].append({"role": "assistant", "content": full_response})
    except Exception as e:
        st.error(f"エージェント応答エラー: {e}")

if prompt := st.chat_input("メッセージを入力..."):
    asyncio.run(handle_user_input(prompt))