# app.py
import os
import streamlit as st
import requests
import uuid
from datetime import datetime
from typing import List, Dict
from db import init_db, save_message, get_history, search_by_symbol

# -------------------------
# Configuration
# -------------------------
# ✅ Hardcode your Gemini API key here for demo (replace with your own key)
GEMINI_API_KEY = ""  # <-- Replace this before running
MODEL = "gemini-2.0-flash"
API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

# -------------------------
# Gemini API Call
# -------------------------
def call_gemini(prompt: str) -> str:
    """Call Gemini model and return generated text."""
    if not GEMINI_API_KEY:
        return "⚠️ Gemini API key not set. Please add it in the code."

    url = f"{API_BASE}/{MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=payload, timeout=30)

    if response.status_code != 200:
        return f"❌ Gemini API Error {response.status_code}: {response.text}"

    data = response.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return str(data)
    
import yfinance as yf

def get_stock_data(symbol: str) -> dict:
    """Fetch key metrics for a given stock symbol using yfinance."""
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        data = {
            "Company Name": info.get("longName", "N/A"),
            "Sector": info.get("sector", "N/A"),
            "Industry": info.get("industry", "N/A"),
            "Country": info.get("country", "N/A"),
            "Market Cap": info.get("marketCap", "N/A"),
            "Current Price": info.get("currentPrice", "N/A"),
            "Previous Close": info.get("previousClose", "N/A"),
            "PE Ratio": info.get("trailingPE", "N/A"),
            "EPS": info.get("trailingEps", "N/A"),
            "ROE": info.get("returnOnEquity", "N/A"),
            "Debt/Equity": info.get("debtToEquity", "N/A"),
            "52 Week High": info.get("fiftyTwoWeekHigh", "N/A"),
            "52 Week Low": info.get("fiftyTwoWeekLow", "N/A"),
            "Dividend Yield": info.get("dividendYield", "N/A")
        }
        return data
    except Exception as e:
        return {"error": str(e)}


# -------------------------
# Prompt Builder
# -------------------------
def format_prompt(history: List[dict], user_msg: str, stock_symbol: str = None) -> str:
    """Format a prompt with system instructions and live stock data."""
    system_instructions = (
        "You are an intelligent financial research assistant built for Tikona Capital Finserv Pvt. Ltd., "
        "specialized in stock market analysis, portfolio research, and AI-driven insights. "
        "Provide structured, factual, and data-backed summaries. "
        "Never leave placeholders like [Insert Data]. Always use the provided stock data.\n\n"
        "When stock data is available, include:\n"
        "- Company Overview\n"
        "- Recent Performance\n"
        "- Fundamental Metrics (PE, EPS, ROE, Market Cap, etc.)\n"
        "- Technical / Comparative Insights\n"
        "- Summary Insight (neutral, analytical tone)\n\n"
        "End with a disclaimer: 'This information is factual and for educational purposes only. Not financial advice.'"
    )

    context = "\n".join(
        f"{'User' if m['role']=='user' else 'Assistant'}: {m['text']}"
        for m in history[-6:]
    )

    stock_info_text = ""
    if stock_symbol:
        data = get_stock_data(stock_symbol)
        if "error" not in data:
            stock_info_text = "\nLive Stock Data:\n" + "\n".join(
                [f"{k}: {v}" for k, v in data.items()]
            )
        else:
            stock_info_text = f"\n(Note: Could not fetch live data for {stock_symbol} — {data['error']})"

    return f"{system_instructions}\n\nConversation Context:\n{context}\n\nUser Query: {user_msg}\n{stock_info_text}\n\nAnswer:"

# -------------------------
# UI Config
# -------------------------
st.set_page_config(page_title="Stock Assistant — Tikona Capital", layout="wide")

# Init DB
init_db()

# Session
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "history" not in st.session_state:
    st.session_state.history = get_history(st.session_state.session_id)

# -------------------------
# Sidebar (Search + Info)
# -------------------------
with st.sidebar:
    st.title("📊 Stock Chat Assistant")
    st.markdown("#### Search Past Chats")
    symbol_search = st.text_input("Enter Stock Symbol (e.g. AAPL, INFY):")

    if st.button("🔍 Search"):
        if symbol_search.strip():
            matches = search_by_symbol(symbol_search.strip().upper())
            if matches:
                st.success(f"Found {len(matches)} related messages")
                for m in matches[:10]:
                    st.markdown(f"**{m['role'].title()}** | {m['created_at']}")
                    st.write(m['text'])
            else:
                st.warning("No messages found for that symbol.")
        else:
            st.info("Enter a symbol to search chats.")

    st.markdown("---")
    st.caption("🎯 Built for Tikona Capital Finserv Pvt. Ltd.\nAI Generalist & Quant Research Intern Interview Project")

# -------------------------
# Main Chat Layout
# -------------------------
st.title("💬 Stock Assistant (Gemini Powered)")
st.write("Ask questions about **stocks, financial terms, or investment insights.**")

st.markdown(
    """
    <style>
    .chat-box {border:1px solid #ddd; border-radius:12px; padding:16px; background:#f9f9f9;}
    .user-msg {background:#E8F0FE; padding:10px 14px; border-radius:12px; margin-bottom:8px;}
    .assistant-msg {background:#F4F7EF; padding:10px 14px; border-radius:12px; margin-bottom:8px;}
    .meta {color:#6c757d; font-size:12px;}
    </style>
    """,
    unsafe_allow_html=True,
)

chat_col, info_col = st.columns([3, 1])

# -------------------------
# Chat Display
# -------------------------
with chat_col:
    st.subheader("Conversation")
    chat_container = st.container()

    def render_chat():
        for msg in st.session_state.history:
            role = msg["role"]
            if role == "user":
                st.markdown(
                    f"<div class='user-msg'><b>You</b> <span class='meta'>· {msg['created_at']}</span><br>{msg['text']}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<div class='assistant-msg'><b>Assistant</b> <span class='meta'>· {msg['created_at']}</span><br>{msg['text']}</div>",
                    unsafe_allow_html=True,
                )

    render_chat()
    st.markdown("---")

    # Input Form
    with st.form("user_input_form", clear_on_submit=True):
        user_input = st.text_area("Type your question:", placeholder="e.g. What are Tesla’s recent revenue trends?", height=100)
        stock_tag = st.text_input("Optional: Stock Symbol", placeholder="e.g. TSLA")
        submitted = st.form_submit_button("🚀 Send")

        if submitted and user_input.strip():
            save_message(st.session_state.session_id, "user", user_input, stock_tag.strip().upper() or None)
            st.session_state.history = get_history(st.session_state.session_id)

            with st.spinner("Analyzing with Gemini..."):
                prompt = format_prompt(st.session_state.history, user_input, stock_tag.strip().upper() or None)
                response = call_gemini(prompt)

            save_message(st.session_state.session_id, "assistant", response, stock_tag.strip().upper() or None)
            st.session_state.history = get_history(st.session_state.session_id)
            st.rerun()

# -------------------------
# Info Panel
# -------------------------
with info_col:
    st.subheader("⚙️ Session Info")
    st.write(f"Session ID: `{st.session_state.session_id[:8]}...`")
    st.write(f"Total Messages: {len(st.session_state.history)}")

    if st.button("🧹 Clear Chat"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.history = []
        st.success("Session cleared. Start a new chat!")
        st.rerun()

    st.download_button(
        "📄 Export Chat (.txt)",
        data="\n\n".join([f"[{m['created_at']}] {m['role'].upper()}: {m['text']}" for m in st.session_state.history]),
        file_name=f"chat_{st.session_state.session_id}.txt",
        mime="text/plain",
    )

# Footer
st.markdown("---")
st.caption("© 2025 Tikona Capital Finserv Pvt. Ltd. | Demo project by Ansh Vishwakarma")
