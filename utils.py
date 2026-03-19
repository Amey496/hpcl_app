import sqlite3
import hashlib
import pandas as pd

def init_db():
    conn = sqlite3.connect('hpcl_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (username TEXT PRIMARY KEY, password TEXT, name TEXT, role TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS operational_logs 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       category TEXT, 
                       item_name TEXT, 
                       value REAL, 
                       timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        pw = hashlib.sha256(str.encode("admin123")).hexdigest()
        cursor.execute("INSERT INTO users VALUES ('admin', ?, 'Amey Sawant', 'Admin')", (pw,))
    conn.commit()
    conn.close()

def add_log(category, item, value):
    conn = sqlite3.connect('hpcl_data.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO operational_logs (category, item_name, value) VALUES (?, ?, ?)", 
                   (category, item, value))
    conn.commit()
    conn.close()

def delete_log(log_id):
    conn = sqlite3.connect('hpcl_data.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM operational_logs WHERE id=?", (log_id,))
    conn.commit()
    conn.close()

def get_logs(category=None):
    conn = sqlite3.connect('hpcl_data.db')
    query = "SELECT * FROM operational_logs" if not category else f"SELECT * FROM operational_logs WHERE category='{category}'"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def authenticate_user(username, password):
    conn = sqlite3.connect('hpcl_data.db')
    cursor = conn.cursor()
    hashed_pw = hashlib.sha256(str.encode(password)).hexdigest()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_pw))
    user = cursor.fetchone()
    conn.close()
    return user