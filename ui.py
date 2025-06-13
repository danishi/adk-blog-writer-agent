import os
import streamlit as st
from dotenv import load_dotenv
import vertexai
from vertexai import agent_engines
from vertexai.preview import reasoning_engines
import logging
import asyncio

# Python 3.12 introduced ``asyncio.wrap_async_iterable`` for turning a
# synchronous iterator into an asynchronous one.  Earlier Python versions do
# not provide this helper, so we implement a compatible fallback.  This ensures
# that streaming works regardless of the Python runtime version.
if hasattr(asyncio, "wrap_async_iterable"):
    _wrap_async_iterable = asyncio.wrap_async_iterable
else:
    def _wrap_async_iterable(iterable):
        async def _gen():
            for item in iterable:
                yield item
        return _gen()

from blog_writer_agents.agent import root_agent

logging.basicConfig(level=logging.INFO, force=True)
load_dotenv()


def init_vertexai():
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")
    vertexai.init(project=project_id, location=location)


def sidebar_inputs():
    st.sidebar.title("設定")
    agent_id = st.sidebar.text_input(
        "Agent Engine の ID",
        value=os.getenv("REMOTE_AGENT_ENGINE_ID"),
        max_chars=20,
    )
    user_id = st.sidebar.text_input(
        "ユーザー ID",
        value="user1",
        max_chars=10,
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


# ユーザーに紐づくセッション一覧取得
async def fetch_session_ids(user_id: str):
    try:
        if ENV == "local":
            response = await remote_agent.list_sessions(user_id=user_id)
        else:
            response = remote_agent.list_sessions(user_id=user_id)
        # response may be an object or a plain dictionary depending on environment
        sessions = None
        if isinstance(response, dict):
            sessions = response.get("sessions", response)
        else:
            sessions = getattr(response, "sessions", response)

        session_ids = []
        for s in sessions:
            if isinstance(s, dict):
                session_ids.append(s.get("id") or s.get("session_id") or s.get("name"))
            else:
                session_ids.append(getattr(s, "id", getattr(s, "session_id", None)))
        return [sid for sid in session_ids if sid]
    except Exception as e:
        st.sidebar.error(f"セッション一覧取得エラー: {e}")
        return []

# 既存セッション一覧の取得と選択
session_list = asyncio.run(fetch_session_ids(user_id))
options = ["新規セッション"] + session_list
index = 0
if "session_id" in st.session_state and st.session_state["session_id"] in session_list:
    index = session_list.index(st.session_state["session_id"]) + 1
selected = st.sidebar.selectbox("セッション選択", options=options, index=index)


# セッション管理


async def manage_session(user_id, agent_id, selected_session_id=None):
    if (
        "session_id" not in st.session_state
        or st.session_state.get("last_agent_id") != agent_id
        or st.session_state.get("last_user_id") != user_id
        or (
            selected_session_id
            and st.session_state.get("session_id") != selected_session_id
        )
    ):
        try:
            if selected_session_id:
                st.session_state["session_id"] = selected_session_id
            else:
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

selected_session_id = None if selected == "新規セッション" else selected
asyncio.run(manage_session(user_id, agent_id, selected_session_id))

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
            stream = _wrap_async_iterable(
                remote_agent.stream_query(
                    user_id=user_id,
                    session_id=st.session_state["session_id"],
                    message=prompt,
                )
            )
            async for event in stream:
                logging.info(f"Received event: {str(event)}")
                for i, part in enumerate(event["content"]["parts"]):
                    if "text" in part:
                        if part["text"].startswith("data:image"):
                            st.image(part["text"], use_container_width=True)
                        else:
                            full_response += part["text"] + " "
                        message_placeholder.markdown(full_response + "▌")
                    if "function_call" in part:
                        message_placeholder.markdown(
                            full_response + f"\n\n🔧 tool_calling: {str(part['function_call'])}"
                        )
                    if "function_response" in part:
                        message_placeholder.markdown(
                            full_response + f"\n\n🔨 tool_response: {str(part['function_response'])}"
                        )
            message_placeholder.markdown(full_response)
        st.session_state["messages"].append({"role": "assistant", "content": full_response})
    except Exception as e:
        st.error(f"エージェント応答エラー: {e}")

if prompt := st.chat_input("メッセージを入力..."):
    asyncio.run(handle_user_input(prompt))
