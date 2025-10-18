import streamlit as st
from datetime import date
from modules.discovery import run as run_discovery
from modules.curriculum import run as run_curriculum
from modules.timeline import run as run_timeline
from modules.ops import run as run_ops
from modules.docs import run as run_docs
from modules.retro import run as run_retro

st.set_page_config(page_title="Sparta EduPM Copilot", page_icon="🧭", layout="wide")

if "stage" not in st.session_state:
    st.session_state.stage = "discovery"
    st.session_state.brief = {}
    st.session_state.outputs = {}

st.title("Sparta EduPM Copilot")
st.caption("기업교육 PM 업무보조 챗봇 — Discovery → 설계 → 운영 → 회고")

st.sidebar.header("Flow")
stage = st.sidebar.radio("단계", ["discovery", "curriculum", "timeline", "ops", "docs", "retro"], index=["discovery", "curriculum", "timeline", "ops", "docs", "retro"].index(st.session_state.stage))
st.session_state.stage = stage

if st.session_state.stage == "discovery":
    run_discovery()
elif st.session_state.stage == "curriculum":
    run_curriculum()
elif st.session_state.stage == "timeline":
    run_timeline()
elif st.session_state.stage == "ops":
    run_ops()
elif st.session_state.stage == "docs":
    run_docs()
elif st.session_state.stage == "retro":
    run_retro()
