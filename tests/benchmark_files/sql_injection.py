"""
Benchmark Test File: SQL Injection Vulnerability
Expected Issue: Critical security vulnerability on line 12
"""
import sqlite3

def get_user_by_username(username):
    """
    Fetch user from database by username
    WARNING: This function contains a SQL injection vulnerability
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Line 12 - CRITICAL: SQL injection vulnerability - user input directly in query
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    
    user = cursor.fetchone()
    conn.close()
    return user

def authenticate_user(username, password):
    user = get_user_by_username(username)
    if user and user[2] == password:
        return True
    return False
