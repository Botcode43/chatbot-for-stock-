# Stock Chat Assistant — Tikona Capital

A Streamlit-based chatbot for financial research, powered by Google Gemini and yfinance.  
Built for AI Generalist & Quant Research Intern Interview Project.

---

## Features

- Chatbot interface for stock market queries
- Fetches live stock data using yfinance
- Stores and searches chat history in SQLite
- Uses Google Gemini LLM for responses

---

## Setup Instructions

1. **Clone the repository**  
   ```sh
   git clone <your-repo-url>
   cd chatbot
   ```

2. **Install dependencies**  
   ```sh
   pip install -r requirements.txt
   ```

3. **Set up environment variables**  
   - Edit the `.env` file with your Google API Key:
     ```
     export GOOGLE_API_KEY="your-google-api-key"
     export GEMINI_MODEL="gemini-2.0-flash"
     ```
   - On Windows, you can use [python-dotenv](https://pypi.org/project/python-dotenv/) or set variables in your terminal.

4. **Run the app**  
   ```sh
   streamlit run app.py
   ```

---

## File Structure

- `app.py` — Main Streamlit app
- `db.py` — Database functions (SQLite)
- `chat_history.db` — SQLite database file
- `.env` — Environment variables (API keys)
- `requirements.txt` — Python dependencies

---

## Notes

- Requires a valid Google Gemini API key.
- For demo, you can hardcode the API key in `app.py` or use the `.env` file.
- All chat history is stored locally in `chat_history.db`.

---


project by Ansh Vishwakarma
