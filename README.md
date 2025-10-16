# Code Review Assistant

AI-powered code review system with support for multiple LLM providers (Cloud and Local).

## Features

- 🤖 **Multiple AI Providers**: Anthropic Claude, OpenAI GPT, Google Gemini, or Local Ollama
- 🔍 **Smart Pre-Analysis**: Extracts structure, complexity, and patterns before AI review
- 📊 **Quality Scoring**: 0-100 score based on code quality
- 🎯 **Issue Detection**: Categorized by severity (critical, medium, low)
- 🌐 **Web Dashboard**: Interactive UI for uploading and viewing reviews
- 🗄️ **Database Storage**: SQLite for review history
- 🔌 **REST API**: Full API for programmatic access
- 🆓 **Local LLM Support**: Run completely offline with Ollama

## Supported Languages

Python, JavaScript, TypeScript, Java, Go, Ruby, PHP, C++, C, C#, Swift

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure AI Provider

Edit `.env` file and choose your provider:

**Option A: Cloud AI (Gemini - Fast & Cheap)**
```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your_api_key_here
AI_MODEL=gemini-2.0-flash
```

**Option B: Local AI (Ollama - FREE & Private)**
```env
AI_PROVIDER=ollama
AI_MODEL=qwen2.5-coder
OLLAMA_BASE_URL=http://localhost:11434
```

### 3. Start Application
```bash
python -m app.main
```

### 4. Open Dashboard
Navigate to: **http://localhost:8000**

## Getting API Keys

| Provider | Get Key From | Cost |
|----------|-------------|------|
| **Gemini** | https://makersuite.google.com/app/apikey | Paid |
| **Claude** | https://console.anthropic.com/ | Paid |
| **OpenAI** | https://platform.openai.com/ | Paid |
| **Ollama** | https://ollama.ai | FREE |

## Local LLM Setup (Ollama)

### 1. Install Ollama
Download from: https://ollama.ai

### 2. Pull a Model
```bash
ollama pull qwen2.5-coder  # Best for code review
```

### 3. Configure .env
```env
AI_PROVIDER=ollama
AI_MODEL=qwen2.5-coder
```

### Benefits
- ✅ 100% FREE
- ✅ Complete privacy
- ✅ Works offline
- ✅ No API limits

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/review` | Full AI-powered review |
| POST | `/api/review/quick` | Quick scan (no AI) |
| GET | `/api/review/{id}` | Get review by ID |
| GET | `/api/reviews` | List all reviews |
| DELETE | `/api/review/{id}` | Delete review |
| GET | `/api/stats` | Get statistics |
| GET | `/docs` | API documentation |

## Configuration

All settings in `.env`:

```env
# AI Provider
AI_PROVIDER=gemini  # Options: anthropic, openai, gemini, ollama
AI_MODEL=gemini-2.0-flash
GEMINI_API_KEY=your_key_here

# API Settings
MAX_TOKENS=8000
API_TIMEOUT=120

# File Upload
MAX_FILE_SIZE=5242880
ALLOWED_EXTENSIONS=.py,.js,.java,.ts,.jsx,.tsx,.go,.rb,.php,.cpp,.c,.cs,.swift
```

## Project Structure

```
code-review-assistant/
├── app/
│   ├── analyzers/          # Static code analysis
│   ├── services/           # LLM & review orchestration
│   ├── routers/            # API routes
│   ├── config.py           # Configuration
│   ├── database.py         # Database setup
│   └── main.py             # FastAPI application
├── templates/              # Web dashboard
├── tests/                  # Unit tests
├── .env                    # Configuration (create from .env.example)
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Test with sample file
python -m app.main
# Upload sample_buggy_code.py via dashboard
```

## Troubleshooting

**Cannot connect to Ollama**
```bash
ollama serve  # Start Ollama manually
```

**API key invalid**
- Check `.env` file has correct API key
- Verify provider name matches (anthropic/openai/gemini/ollama)

**Module not found**
```bash
pip install -r requirements.txt
```

## Complete Documentation

See [DOCUMENTATION.md](DOCUMENTATION.md) for:
- Detailed architecture
- System flow diagrams
- API specifications
- Development guide
- Advanced configuration

## Support

For issues or questions, refer to the comprehensive [DOCUMENTATION.md](DOCUMENTATION.md) file.
