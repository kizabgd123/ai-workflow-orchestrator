import streamlit as st
import os
import sys

# Add project root to sys.path so we can import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from memory.mongodb_atlas import MongoDBMemory

st.set_page_config(page_title="AI Debate Visualizer", layout="wide")

st.title("AI Workflow Orchestrator Dashboard")


# Initialize Memory
@st.cache_resource
def get_memory():
    return MongoDBMemory()


memory = get_memory()

# Sidebar for controls
st.sidebar.header("Dashboard Controls")
refresh = st.sidebar.button("Refresh Data")

# Main Content
st.header("Recent Debate Summaries")
debates = memory.get_recent_debates(limit=10)

if debates:
    for debate in debates:
        with st.expander(
            f"Debate: {debate.get('final_decision', 'No Decision')} - {debate.get('created_at')}"
        ):
            st.write(f"Confidence: {debate.get('confidence_score')}")
            # Here we could further query arguments if needed
else:
    st.info("No recent debates found.")

# Health Check
st.sidebar.header("System Status")
health = memory.health_check()
st.sidebar.json(health)
