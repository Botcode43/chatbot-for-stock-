import sqlite3
from datetime import datetime

DB_FILE = "chat_history.db"

# -------------------------
# Initialize Database
# -------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            text TEXT,
            stock_symbol TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

# -------------------------
# Save Message
# -------------------------
def save_message(session_id: str, role: str, text: str, stock_symbol: str = None):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (session_id, role, text, stock_symbol, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (session_id, role, text, stock_symbol, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

# -------------------------
# Get Chat History
# -------------------------
def get_history(session_id: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT role, text, stock_symbol, created_at
        FROM messages
        WHERE session_id = ?
        ORDER BY id ASC
    """, (session_id,))
    rows = cursor.fetchall()
    conn.close()

    return [
        {"role": r[0], "text": r[1], "stock_symbol": r[2], "created_at": r[3]}
        for r in rows
    ]

# -------------------------
# Search Messages by Symbol
# -------------------------
def search_by_symbol(stock_symbol: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT role, text, stock_symbol, created_at
        FROM messages
        WHERE stock_symbol = ?
        ORDER BY created_at DESC
    """, (stock_symbol,))
    rows = cursor.fetchall()
    conn.close()

    return [
        {"role": r[0], "text": r[1], "stock_symbol": r[2], "created_at": r[3]}
        for r in rows
    ]
