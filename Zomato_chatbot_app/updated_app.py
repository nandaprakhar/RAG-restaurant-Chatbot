"""
app.py
------
Streamlit UI for the Zomato RAG Chatbot.

Features:
- Conversational memory using `st.session_state`
- Rich HTML-styled user/bot cards
- Async-like update with form submission and rerun
- Minimalist input box with submit icon
- Sidebar instructions for structured search keywords
"""

import streamlit as st
from updated_rag_engine import get_rag_response  # ⬅️ Core RAG logic

# -------------------------------
# Streamlit Config & Header
# -------------------------------
st.set_page_config(page_title="Zomato RAG Chatbot", page_icon="🍽️")
st.title("🍽️ Zomato RAG Chatbot")
st.markdown("Ask anything about restaurants, menus, cuisines, or specific dishes.")

# -------------------------------
# Sidebar Instructions
# -------------------------------
with st.sidebar:
    st.header("How to Use")
    st.markdown("""
**Special Retrieval Commands:**

- 🏪 `restaurant-list`  
  ➤ Lists all restaurant names.

- 🍽️ `menu-list <restaurant>`  
  ➤ Lists dishes and prices from a specific restaurant.  
  _Example: `menu-list Bikanervala`_

- 🔍 `serves-dish-item <dish>`  
  ➤ Shows which restaurant serves a given dish.  
  _Example: `serves-dish-item Butter Paneer`_

""")

# -------------------------------
# State Initialization
# -------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -------------------------------
# HTML Styling for Chat Cards
# -------------------------------
def user_card(text: str) -> str:
    return f"""
    <div style="background-color:#f0f2f6;padding:10px;border-radius:10px;margin-bottom:10px;">
        <b style="color:#1f77b4;">You:</b> {text}
    </div>
    """

def bot_card(text: str) -> str:
    return f"""
    <div style="background-color:#d2f8d2;padding:10px;border-radius:10px;margin-bottom:15px;">
        <b style="color:#2c7a7b;">Bot:</b> {text}
    </div>
    """

# -------------------------------
# User Input Form (with icon)
# -------------------------------
with st.form(key="query_form", clear_on_submit=True):
    user_input = st.text_input(
        label="Type your question here 👇",
        placeholder="e.g., Which restaurants serve vegan dishes?",
        label_visibility="collapsed"
    )
    submitted = st.form_submit_button("➤ Send", use_container_width=True)

# -------------------------------
# Step 1: Handle Form Submit
# -------------------------------
if submitted and user_input:
    st.session_state.chat_history.append({
        "user": user_input,
        "bot": "⏳ Thinking..."
    })
    st.rerun()

# -------------------------------
# Step 2: Render Chat Cards
# -------------------------------
for message in st.session_state.chat_history:
    st.markdown(user_card(message["user"]), unsafe_allow_html=True)

    if message["bot"] == "⏳ Thinking...":
        try:
            response = get_rag_response(message["user"])
            message["bot"] = response or "Sorry, I couldn’t find a confident answer."
        except Exception:
            message["bot"] = "Oops! Something went wrong while processing your request."
        st.rerun()

    st.markdown(bot_card(message["bot"]), unsafe_allow_html=True)
