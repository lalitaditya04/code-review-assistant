# 🎨 Architecture Diagram

Visual representation of the Code Review Assistant system.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Web Dashboard (dashboard.html)                  │  │
│  │                                                            │  │
│  │  • Drag & Drop Upload                                     │  │
│  │  • Real-time Results Display                              │  │
│  │  • Review History                                         │  │
│  │  • Statistics Dashboard                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API LAYER (FastAPI)                       │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Router (review.py)                       │  │
│  │                                                            │  │
│  │  POST   /api/review          • Full AI Review            │  │
│  │  POST   /api/review/quick    • Quick Scan                │  │
│  │  GET    /api/review/{id}     • Get Review                │  │
│  │  GET    /api/reviews         • List Reviews              │  │
│  │  DELETE /api/review/{id}     • Delete Review             │  │
│  │  GET    /api/stats           • Statistics                │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                          │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           ReviewService (review_service.py)               │  │
│  │                                                            │  │
│  │  📥 Receive Code File                                     │  │
│  │  🔍 Trigger Pre-Analysis                                  │  │
│  │  📝 Build AI Context                                      │  │
│  │  🤖 Call AI Provider                                      │  │
│  │  🔄 Merge Results                                         │  │
│  │  💾 Save to Database                                      │  │
│  │  📤 Return Review                                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                     │
│              ┌──────────────┼──────────────┐                    │
│              ▼              ▼               ▼                    │
│  ┌──────────────┐ ┌─────────────┐ ┌──────────────┐            │
│  │   Analyzer   │ │   Context   │ │  LLM Service │            │
│  │              │ │   Builder   │ │              │            │
│  └──────────────┘ └─────────────┘ └──────────────┘            │
└─────────────────────────────────────────────────────────────────┘
                             │
            ┌────────────────┼────────────────┐
            ▼                ▼                 ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
│   SQLite DB      │ │  AI Provider │ │  External APIs   │
│   (reviews.db)   │ │  • Anthropic │ │  (if needed)     │
│                  │ │  • OpenAI    │ │                  │
└──────────────────┘ └──────────────┘ └──────────────────┘
```

---

## 🔄 Data Flow Diagram

```
┌─────────────┐
│  Code File  │
│  (.py, .js) │
└──────┬──────┘
       │
       ▼
┌───────────────────────────────────────────────────────────┐
│              STEP 1: Pre-Analysis Phase                   │
│                                                             │
│  BasicAnalyzer.analyze_file()                             │
│  ├─ Extract Structure                                     │
│  │  • Count functions, classes, imports                   │
│  │  • Identify async patterns                             │
│  │                                                         │
│  ├─ Calculate Complexity                                  │
│  │  • Cyclomatic complexity (Radon)                       │
│  │  • Flag high-complexity functions                      │
│  │                                                         │
│  ├─ Detect Patterns                                       │
│  │  • API endpoints, DB queries                           │
│  │  • File I/O, HTTP requests                             │
│  │  • Authentication code                                 │
│  │                                                         │
│  └─ Find Basic Issues                                     │
│     • Hardcoded secrets (regex)                           │
│     • SQL injection patterns                              │
│     • Long lines, long functions                          │
│     • Missing error handling                              │
└──────────────┬────────────────────────────────────────────┘
               │
               │ Metadata Dict
               │
               ▼
┌───────────────────────────────────────────────────────────┐
│              STEP 2: Context Building                     │
│                                                             │
│  ContextBuilder.build_context()                           │
│  ├─ Format Structure Info                                 │
│  │  "File has 5 functions, 2 classes..."                  │
│  │                                                         │
│  ├─ Format Complexity                                     │
│  │  "Average complexity: 5.2"                             │
│  │  "High complexity: process_payment (12)"               │
│  │                                                         │
│  ├─ List Detected Patterns                                │
│  │  "🗄️ 3 database queries found"                        │
│  │  "🌐 5 API endpoints detected"                        │
│  │                                                         │
│  └─ Format Pre-Identified Issues                          │
│     "🔴 Critical: Line 23 - Hardcoded API key"           │
│     "🟡 Medium: Line 45 - SQL injection risk"            │
└──────────────┬────────────────────────────────────────────┘
               │
               │ Natural Language Context
               │
               ▼
┌───────────────────────────────────────────────────────────┐
│              STEP 3: AI Review                            │
│                                                             │
│  LLMService.review_with_context()                         │
│  ├─ Build Enriched Prompt                                 │
│  │  Context + Code + Instructions                         │
│  │                                                         │
│  ├─ Call AI Provider                                      │
│  │  • Anthropic Claude API                                │
│  │  • OR OpenAI GPT API                                   │
│  │                                                         │
│  ├─ Parse Response                                        │
│  │  Extract JSON from AI response                         │
│  │                                                         │
│  └─ Return Structured Results                             │
│     • Validated issues                                    │
│     • False positives                                     │
│     • New findings                                        │
│     • Recommendations                                     │
└──────────────┬────────────────────────────────────────────┘
               │
               │ AI Review Dict
               │
               ▼
┌───────────────────────────────────────────────────────────┐
│              STEP 4: Result Merging                       │
│                                                             │
│  ReviewService._merge_results()                           │
│  ├─ Combine Pre-Analysis + AI Results                     │
│  │                                                         │
│  ├─ Remove False Positives                                │
│  │  Issues AI marked as not real problems                 │
│  │                                                         │
│  ├─ Calculate Final Score                                 │
│  │  Score = Base - (Critical×15) - (Medium×5) - (Low×1)  │
│  │                                                         │
│  └─ Build Statistics                                      │
│     • Total issues by severity                            │
│     • Pre-analysis vs AI findings                         │
│     • Processing metrics                                  │
└──────────────┬────────────────────────────────────────────┘
               │
               │ Final Review
               │
               ▼
┌───────────────────────────────────────────────────────────┐
│              STEP 5: Storage & Response                   │
│                                                             │
│  ├─ Save to Database                                      │
│  │  Review model with all details                         │
│  │                                                         │
│  └─ Return to User                                        │
│     • Quality Score (0-100)                               │
│     • All Issues (categorized)                            │
│     • Summary & Recommendations                           │
│     • Processing time                                     │
└───────────────────────────────────────────────────────────┘
```

---

## 🧩 Component Interaction

```
┌─────────────────────────────────────────────────────────────┐
│                      main.py (FastAPI App)                   │
│                                                               │
│  • Initializes all components                                │
│  • Sets up routes                                            │
│  • Manages lifecycle                                         │
└───────┬───────────────────────────────┬─────────────────────┘
        │                               │
        ▼                               ▼
┌──────────────────┐            ┌──────────────────┐
│   config.py      │            │   database.py    │
│                  │            │                  │
│ • Environment    │            │ • DB connection  │
│ • API keys       │            │ • Session mgmt   │
│ • Settings       │            │ • Init tables    │
└──────────────────┘            └────────┬─────────┘
                                         │
                                         ▼
                                ┌──────────────────┐
                                │    models.py     │
                                │                  │
                                │ • Review model   │
                                │ • Stats model    │
                                └──────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   routers/review.py                          │
│                                                               │
│  POST /api/review                                            │
│    ├─ Validate file                                          │
│    ├─ Save temporarily                                       │
│    ├─ Call ReviewService                                     │
│    ├─ Save to database                                       │
│    └─ Return results                                         │
│                                                               │
│  GET /api/reviews                                            │
│    ├─ Query database                                         │
│    ├─ Apply filters                                          │
│    └─ Return list                                            │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              services/review_service.py                      │
│                                                               │
│  process_review()                                            │
│    ├─ Read code file                                         │
│    ├─ analyzer.analyze_file() ────────┐                     │
│    ├─ context_builder.build_context() │                     │
│    ├─ llm.review_with_context() ──────┤                     │
│    └─ _merge_results() ───────────────┤                     │
└────────────────────────────────────────┼─────────────────────┘
                                         │
        ┌────────────────────────────────┼────────────────┐
        │                                │                 │
        ▼                                ▼                 ▼
┌───────────────┐            ┌──────────────┐   ┌──────────────┐
│ BasicAnalyzer │            │ ContextBuilder│   │ LLMService   │
│               │            │               │   │              │
│ • Structure   │──────────▶ │ • Format data │   │ • AI calls   │
│ • Complexity  │            │ • Build prompt│◀──│ • Parse JSON │
│ • Patterns    │            │ • Natural lang│   │ • Universal  │
│ • Issues      │            │               │   │   provider   │
└───────────────┘            └──────────────┘   └──────────────┘
```

---

## 🎯 Decision Flow

```
                    User Uploads File
                           │
                           ▼
                    ┌─────────────┐
                    │ File Valid? │
                    └──────┬──────┘
                           │
                 ┌─────────┴─────────┐
                 │                   │
              YES│                   │NO
                 ▼                   ▼
         ┌───────────────┐    ┌──────────┐
         │ Quick or Full?│    │ Return   │
         └───────┬───────┘    │ Error    │
                 │            └──────────┘
        ┌────────┴────────┐
        │                 │
     QUICK│             FULL│
        ▼                 ▼
┌─────────────┐   ┌──────────────┐
│ Pre-Analysis│   │ Pre-Analysis │
│    Only     │   │      +       │
└──────┬──────┘   │  AI Review   │
       │          └──────┬───────┘
       │                 │
       └────────┬────────┘
                ▼
        ┌───────────────┐
        │ Calculate     │
        │ Score         │
        └───────┬───────┘
                ▼
        ┌───────────────┐
        │ Save to DB    │
        └───────┬───────┘
                ▼
        ┌───────────────┐
        │ Return Results│
        └───────────────┘
```

---

## 💾 Database Schema

```
┌──────────────────────────────────────────────────────────┐
│                    Review Table                           │
├──────────────────────────────────────────────────────────┤
│ id               STRING (PK, UUID)                        │
│ filename         STRING                                   │
│ language         STRING                                   │
│ file_size        INTEGER                                  │
│                                                            │
│ pre_analysis     JSON                                     │
│   ├─ structure                                            │
│   ├─ complexity                                           │
│   ├─ patterns                                             │
│   └─ issues                                               │
│                                                            │
│ ai_review        JSON                                     │
│   ├─ validated_issues                                     │
│   ├─ false_positives                                      │
│   ├─ new_findings                                         │
│   └─ recommendations                                      │
│                                                            │
│ final_result     JSON                                     │
│   ├─ all_issues                                           │
│   ├─ statistics                                           │
│   └─ summary                                              │
│                                                            │
│ score            INTEGER (0-100)                          │
│ total_issues     INTEGER                                  │
│ critical_issues  INTEGER                                  │
│ medium_issues    INTEGER                                  │
│ low_issues       INTEGER                                  │
│                                                            │
│ ai_provider      STRING                                   │
│ ai_model         STRING                                   │
│ summary          TEXT                                     │
│                                                            │
│ created_at       DATETIME                                 │
│ processing_time  FLOAT (seconds)                          │
└──────────────────────────────────────────────────────────┘
```

---

## 🔐 Security Model

```
┌─────────────────────────────────────────────────────────┐
│                   Environment (.env)                     │
│                                                           │
│  • API Keys (never in code)                              │
│  • Configuration (not in git)                            │
│  • Secrets management                                    │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│                 Application Layer                        │
│                                                           │
│  • Input validation                                      │
│  • File type checking                                    │
│  • Size limits                                           │
│  • Sanitization                                          │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│                   API Layer                              │
│                                                           │
│  • CORS configuration                                    │
│  • Rate limiting (optional)                              │
│  • Error handling                                        │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│                 External APIs                            │
│                                                           │
│  • HTTPS only                                            │
│  • API key authentication                                │
│  • Timeout handling                                      │
└─────────────────────────────────────────────────────────┘
```

---

**This diagram shows the complete architecture of your Code Review Assistant!** 🎨

