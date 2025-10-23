"""
Benchmark Test File: Hardcoded Secret Detection
Expected Issue: Critical security vulnerability on line 5
"""
import requests

def fetch_data():
    api_key = "sk-1234567890abcdef"  # Line 5 - CRITICAL: Hardcoded API key
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get("https://api.example.com/data", headers=headers)
    return response.json()

def process_data():
    data = fetch_data()
    return data
