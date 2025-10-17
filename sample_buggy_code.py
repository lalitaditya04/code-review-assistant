"""
Sample buggy code for testing Code Review Assistant
This file intentionally contains various code quality issues
"""
import sqlite3
import requests

# CRITICAL: Hardcoded credentials
API_KEY = "sk-1234567890abcdefghijklmnopqrstuvwxyz"
DATABASE_PASSWORD = "admin123"
SECRET_TOKEN = "super_secret_token_12345"

class UserManager:
    """Manages user authentication and data"""
    
    def __init__(self):
        self.db = sqlite3.connect('users.db')
        print("Database connected")  # Should use logging
    
    def authenticate(self, username, password):
        # CRITICAL: SQL Injection vulnerability
        query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
        cursor = self.db.execute(query)
        result = cursor.fetchone()
        
        # MEDIUM: Bare except clause
        try:
            if result:
                return True
        except:
            pass
        
        return False
    
    def get_user_data(self, user_id):
        # MEDIUM: SQL string concatenation
        query = f"SELECT * FROM users WHERE id = {user_id}"
        return self.db.execute(query).fetchall()
    
    def process_payment(self, amount, card_number, cvv, user_id):
        # HIGH COMPLEXITY: Nested conditionals (cyclomatic complexity > 10)
        if amount > 0:
            if amount < 10:
                fee = 0.5
            elif amount < 100:
                fee = 1.0
            else:
                if amount < 1000:
                    fee = 5.0
                else:
                    if amount < 10000:
                        fee = 10.0
                    else:
                        if amount < 100000:
                            fee = 20.0
                        else:
                            fee = 50.0
        
        # CRITICAL: Logging sensitive data
        print(f"Processing payment: ${amount} for user {user_id}, card: {card_number}, CVV: {cvv}")
        
        # MEDIUM: No error handling for network request
        response = requests.post('https://api.payment.com/charge', 
                                json={'amount': amount, 'card': card_number})
        
        # TODO: Actually implement payment logic
        # FIXME: This is not production ready
        return True

def fetch_user_profile(user_id):
    """Fetch user profile from external API"""
    # MEDIUM: No error handling
    url = f"https://api.example.com/users/{user_id}"
    response = requests.get(url, headers={'Authorization': f'Bearer {API_KEY}'})
    return response.json()

def calculate_discount(user_type, purchase_amount, loyalty_points, is_premium, coupon_code):
    # HIGH COMPLEXITY: Too many parameters and complex logic
    discount = 0
    
    if user_type == 'regular':
        if purchase_amount > 100:
            if is_premium:
                if loyalty_points > 500:
                    discount = 0.25
                else:
                    discount = 0.15
            else:
                discount = 0.10
        else:
            if is_premium:
                discount = 0.10
    elif user_type == 'vip':
        if purchase_amount > 50:
            if is_premium:
                if loyalty_points > 1000:
                    discount = 0.40
                else:
                    discount = 0.30
            else:
                discount = 0.20
    
    if coupon_code:
        discount += 0.05
    
    return discount

# LONG LINE: This line is intentionally very long to trigger the long line issue detection in the static analyzer - it exceeds 120 characters

class DataProcessor:
    """Process and analyze data"""
    
    def process_large_dataset(self, data):
        """
        LONG FUNCTION: This function is intentionally long (>50 lines)
        to trigger complexity warnings
        """
        results = []
        
        for item in data:
            if item['type'] == 'A':
                if item['value'] > 100:
                    results.append(item['value'] * 2)
                else:
                    results.append(item['value'] * 1.5)
            elif item['type'] == 'B':
                if item['value'] > 200:
                    results.append(item['value'] * 3)
                else:
                    results.append(item['value'] * 2.5)
            elif item['type'] == 'C':
                if item['value'] > 300:
                    results.append(item['value'] * 4)
                else:
                    results.append(item['value'] * 3.5)
            
            # More processing
            if item.get('special'):
                results[-1] *= 1.1
            
            if item.get('urgent'):
                results[-1] *= 1.2
            
            # Even more processing
            if len(results) > 10:
                avg = sum(results[-10:]) / 10
                if avg > 1000:
                    results = [r * 0.9 for r in results]
            
            # TODO: Optimize this
            # FIXME: This is very slow
            for i in range(len(results)):
                if results[i] > 5000:
                    results[i] = 5000
        
        print("Processed", len(results), "items")  # Should use logging
        return results

if __name__ == "__main__":
    # Test the buggy code
    manager = UserManager()
    
    # This will trigger SQL injection warning
    manager.authenticate("admin' OR '1'='1", "anything")
    
    # This will show hardcoded credentials
    fetch_user_profile(123)
