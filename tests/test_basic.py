"""
Basic tests for Code Review Assistant
"""
import pytest
from app.analyzers.basic_analyzer import BasicAnalyzer
from app.analyzers.context_builder import ContextBuilder


def test_analyzer_structure():
    """Test that analyzer extracts code structure correctly"""
    code = """
def hello():
    return 'world'

class MyClass:
    pass
"""
    analyzer = BasicAnalyzer()
    result = analyzer.analyze_file(code, "test.py")
    
    assert result['structure']['functions_count'] == 1
    assert result['structure']['classes_count'] == 1
    assert result['metadata']['language'] == 'python'


def test_analyzer_complexity():
    """Test complexity analysis"""
    code = """
def complex_function():
    if True:
        for i in range(10):
            if i > 5:
                while i < 20:
                    i += 1
"""
    analyzer = BasicAnalyzer()
    result = analyzer.analyze_file(code, "test.py")
    
    assert 'complexity' in result
    assert result['complexity']['total'] > 0


def test_analyzer_patterns():
    """Test pattern detection"""
    code = """
import requests

async def fetch_data():
    response = await requests.get('http://api.example.com')
    return response.json()
"""
    analyzer = BasicAnalyzer()
    result = analyzer.analyze_file(code, "test.py")
    
    patterns = result['patterns']
    assert len(patterns) > 0
    assert any(p['category'] == 'async' for p in patterns)


def test_analyzer_issues():
    """Test issue detection"""
    code = """
password = "hardcoded_secret_123"
api_key = "sk-1234567890"

def unsafe_query():
    query = "SELECT * FROM users WHERE id = " + user_id
    print("Debug:", query)
"""
    analyzer = BasicAnalyzer()
    result = analyzer.analyze_file(code, "test.py")
    
    issues = result['issues']
    assert len(issues) > 0
    
    # Should detect hardcoded secrets
    secret_issues = [i for i in issues if i['type'] == 'Hardcoded Secret']
    assert len(secret_issues) > 0


def test_context_builder():
    """Test context generation"""
    analysis = {
        "structure": {
            "total_lines": 100,
            "functions_count": 5,
            "classes_count": 2,
            "code_lines": 80,
            "comment_lines": 10,
            "blank_lines": 10,
            "imports_count": 3,
            "is_async": True,
            "functions": [{"name": "test", "line": 1}],
            "classes": []
        },
        "complexity": {
            "average": 5,
            "max": 10,
            "total": 25,
            "complex_functions": []
        },
        "patterns": [
            {
                "name": "API Endpoint",
                "category": "api",
                "count": 3,
                "occurrences": [{"line": 1, "code": "@app.get"}]
            }
        ],
        "issues": [
            {
                "line": 10,
                "severity": "critical",
                "type": "Hardcoded Secret",
                "message": "Secret detected",
                "code_snippet": "password = '123'"
            }
        ],
        "metadata": {
            "filename": "test.py",
            "language": "python"
        }
    }
    
    builder = ContextBuilder()
    context = builder.build_context(analysis, "test code")
    
    assert "CODE ANALYSIS CONTEXT" in context
    assert "File Overview" in context
    assert "python" in context
    assert "5" in context  # functions count
    assert "Critical" in context or "critical" in context


def test_language_detection():
    """Test language detection from filename"""
    analyzer = BasicAnalyzer()
    
    assert analyzer._detect_language("test.py") == "python"
    assert analyzer._detect_language("test.js") == "javascript"
    assert analyzer._detect_language("test.java") == "java"
    assert analyzer._detect_language("test.ts") == "typescript"
    assert analyzer._detect_language("test.go") == "go"


def test_long_line_detection():
    """Test detection of long lines"""
    long_line = "x = " + "a" * 150
    code = f"""
def test():
    {long_line}
"""
    
    analyzer = BasicAnalyzer()
    result = analyzer.analyze_file(code, "test.py")
    
    long_line_issues = [i for i in result['issues'] if i['type'] == 'Long Line']
    assert len(long_line_issues) > 0


def test_sql_injection_detection():
    """Test SQL injection pattern detection"""
    code = """
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    return db.execute(query)
"""
    
    analyzer = BasicAnalyzer()
    result = analyzer.analyze_file(code, "test.py")
    
    sql_issues = [i for i in result['issues'] if 'SQL' in i['type']]
    assert len(sql_issues) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
