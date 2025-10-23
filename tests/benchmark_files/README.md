# Benchmark Test Files

This directory contains benchmark test files used to evaluate the LLM insight quality.

## Files

### 1. hardcoded_secret.py
- **Purpose**: Tests detection of hardcoded API keys
- **Known Issue**: Line 5 - Hardcoded API key (CRITICAL)
- **Expected Detection**: Security vulnerability

### 2. sql_injection.py
- **Purpose**: Tests detection of SQL injection vulnerabilities
- **Known Issue**: Line 12 - SQL injection via string formatting (CRITICAL)
- **Expected Detection**: Security vulnerability

### 3. high_complexity.py
- **Purpose**: Tests detection of high cyclomatic complexity
- **Known Issue**: Line 1 - Function with CC of 15 (MEDIUM)
- **Expected Detection**: Complexity issue

### 4. race_condition.py
- **Purpose**: Tests detection of concurrency issues
- **Known Issue**: Line 8-11 - Non-atomic increment operation (CRITICAL)
- **Expected Detection**: Concurrency/logic bug

## Usage

These files are automatically used by the evaluation system when you run:

```bash
curl http://localhost:8000/api/evaluation/benchmark
```

## Adding New Benchmark Files

1. Create a new `.py` file in this directory
2. Add comments indicating the known issues
3. Register the file in `app/evaluation/insight_quality.py`
4. Run the evaluation to test

## Notes

- Do NOT modify these files unless updating the benchmark tests
- Each file should have clear, documented known issues
- Issues should be realistic and representative of common problems
