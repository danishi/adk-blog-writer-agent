import os
import streamlit as st
from dotenv import load_dotenv
import vertexai
from vertexai import agent_engines
import logging

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

# Agent取得
try:
    remote_agent = agent_engines.get(agent_id)
except Exception as e:
    st.error(f"Agent取得エラー: {e}")
    st.stop()

# セッション管理
if (
    "session_id" not in st.session_state or
    st.session_state.get("last_agent_id") != agent_id or
    st.session_state.get("last_user_id") != user_id
):
    try:
        session = remote_agent.create_session(user_id=user_id)
        st.session_state["session_id"] = session["id"]
        st.session_state["last_agent_id"] = agent_id
        st.session_state["last_user_id"] = user_id
        st.session_state["messages"] = []
    except Exception as e:
        st.error(f"セッション作成エラー: {e}")
        st.stop()

# チャット履歴表示
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ユーザー入力
if prompt := st.chat_input("メッセージを入力..."):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    # Agentへ問い合わせ
    try:
        for event in remote_agent.stream_query(
            user_id=user_id,
            session_id=st.session_state["session_id"],
            message=prompt,
        ):
            logging.info(f"Received event: {str(event)}")
            for i, part in enumerate(event["content"]["parts"]):
                if "text" in part:
                    st.session_state["messages"].append({
                        "role": "assistant",
                        "content": part["text"]
                    })
                    with st.chat_message("assistant"):
                        st.markdown(part["text"])
                if "function_call" in part:
                    with st.chat_message("tool", avatar="🔧"):
                        st.markdown(f"tool_calling: {str(part['function_call'])}")
                if "function_response" in part:
                    with st.chat_message("tool", avatar="🔨"):
                        st.markdown(f"tool_response: {str(part['function_response'])}")
    except Exception as e:
        st.error(f"エージェント応答エラー: {e}")
