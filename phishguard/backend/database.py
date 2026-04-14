# This file handles storing user history and blocked links
# Uses SQLite - a simple file-based database (no separate server needed)

import sqlite3
from datetime import datetime

# Database file name
DB_NAME = "phishguard.db"

def get_connection():
    """Create and return connection to SQLite database"""
    return sqlite3.connect(DB_NAME)

def init_database():
    """Run this once to create tables if they don't exist"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table 1: Stores every URL a user has checked
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS url_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            label TEXT NOT NULL,
            confidence REAL NOT NULL,
            reasons TEXT NOT NULL,
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table 2: Stores URLs the user has permanently blocked
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blocked_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL UNIQUE,
            blocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

def save_url_check(url, label, confidence, reasons):
    """Save a checked URL to history"""
    conn = get_connection()
    cursor = conn.cursor()
    
    reasons_str = ",".join(reasons)  # Convert list to string for storage
    
    cursor.execute('''
        INSERT INTO url_history (url, label, confidence, reasons)
        VALUES (?, ?, ?, ?)
    ''', (url, label, confidence, reasons_str))
    
    conn.commit()
    conn.close()
    print(f"✅ Saved: {url} -> {label}")

def get_history(limit=50):
    """Get recent URL checks (last 50 by default)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT url, label, confidence, reasons, checked_at 
        FROM url_history 
        ORDER BY checked_at DESC 
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            "url": row[0],
            "label": row[1],
            "confidence": row[2],
            "reasons": row[3].split(","),  # Convert string back to list
            "checked_at": row[4]
        })
    
    return history

def block_link(url):
    """Add a URL to blocked list (user manually blocked it)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT INTO blocked_links (url) VALUES (?)', (url,))
        conn.commit()
        print(f"🚫 Blocked: {url}")
        return True
    except sqlite3.IntegrityError:
        print(f"⚠️ URL already blocked: {url}")
        return False
    finally:
        conn.close()

def unblock_link(url):
    """Remove a URL from blocked list"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM blocked_links WHERE url = ?', (url,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    
    return affected > 0

def get_blocked_links():
    """Get all permanently blocked URLs"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT url, blocked_at FROM blocked_links ORDER BY blocked_at DESC')
    rows = cursor.fetchall()
    conn.close()
    
    return [{"url": row[0], "blocked_at": row[1]} for row in rows]

def is_url_blocked(url):
    """Check if a specific URL is blocked"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT 1 FROM blocked_links WHERE url = ?', (url,))
    exists = cursor.fetchone() is not None
    conn.close()
    
    return exists

def clear_history():
    """Delete all records from url_history"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM url_history')
    conn.commit()
    conn.close()
    
    return True