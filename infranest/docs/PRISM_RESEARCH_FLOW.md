# PRISM Research Flow - Complete System Architecture

## Overview

**PRISM** (Prompt-Refined Intelligent System for Microservices) is a comprehensive AI-powered backend code generation platform that transforms natural language prompts into production-ready backend applications through a sophisticated 9-step research and refinement flow.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PRISM RESEARCH FLOW                                  │
│                     (9-Step Intelligent Pipeline)                           │
└─────────────────────────────────────────────────────────────────────────────┘

STEP 1: USER PROMPT INPUT
┌─────────────────────────────────────┐
│  User Input: Natural Language       │
│  "Build a blog platform with..."    │
│  → Frontend: PromptToDSL.tsx        │
│  → Endpoint: /api/generate-dsl      │
└──────────────┬──────────────────────┘
               ↓
STEP 2: INITIAL CONTEXT-BUILDING (6 Core Questions)
┌─────────────────────────────────────┐
│  Intelligent Question Generator      │
│  1. Authentication type?            │
│  2. Database preference?            │
│  3. API design (REST/GraphQL)?      │
│  4. Deployment target?              │
│  5. Testing requirements?           │
│  6. Scaling expectations?           │
│  → Component: QuestionFlow.tsx      │
│  → Backend: groq_provider.py        │
└──────────────┬──────────────────────┘
               ↓
STEP 3: FOLLOW-UP REFINEMENT (Dynamic 2-10 Questions)
┌─────────────────────────────────────┐
│  LLM-Powered Dynamic Questions      │
│  → Analyzes user responses          │
│  → Generates context-specific Qs    │
│  → Refines until complete context   │
│  → Hyperparams: temp=0.8, top_p=0.95│
│  → Model: Mixtral-8x7b-32768        │
│  → File: groq_provider.py:314-323   │
└──────────────┬──────────────────────┘
               ↓
STEP 4: DSL PARSING LAYER (Editable, Visual)
┌─────────────────────────────────────┐
│  Domain-Specific Language           │
│  → YAML-based specification         │
│  → Visual editor (DSLEditor.tsx)    │
│  → Real-time validation             │
│  → User can edit before generation  │
│  → Parser: dsl_parser.py            │
│  Example:                           │
│    models:                          │
│      - name: Post                   │
│        fields:                      │
│          - title: string            │
│          - content: text            │
└──────────────┬──────────────────────┘
               ↓
STEP 5: CODE GENERATION (Multi-Framework)
┌─────────────────────────────────────────────────────────────┐
│  Framework-Specific Generators                              │
│  ┌──────────────┬──────────────┬──────────────┐           │
│  │   Django     │      Go      │    Rails     │           │
│  │   23 files   │  10-20 files │  9-25 files  │           │
│  │  ├models.py  │  ├main.go    │  ├models.rb  │           │
│  │  ├views.py   │  ├handlers   │  ├controllers│           │
│  │  ├serializ.  │  ├middleware │  ├routes.rb  │           │
│  │  ├urls.py    │  ├config.go  │  ├Gemfile    │           │
│  │  ├tests.py   │  ├tests      │  ├spec/      │           │
│  │  ├Docker     │  ├Docker     │  ├Docker     │           │
│  │  └requirements│ └go.mod     │  └database.yml│          │
│  └──────────────┴──────────────┴──────────────┘           │
│  → Hyperparams: temp=0.15, max_tokens=8000                 │
│  → Adaptive scaling based on project size                  │
│  → Files: django_generator.py, go_generator.py, rails_gen  │
└─────────────────────────┬───────────────────────────────────┘
                          ↓
STEP 6: LLM SELECTION & HYPERPARAMETER TUNING
┌─────────────────────────────────────────────────────────────┐
│  Adaptive Hyperparameter System                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Use Case        │ Temp │ Max Tokens │ Top-P │ ...  │   │
│  ├─────────────────┼──────┼────────────┼───────┼──────┤   │
│  │ Code Gen        │ 0.15 │ 8000       │ 0.80  │ ...  │   │
│  │ DSL Gen         │ 0.20 │ 6000       │ 0.85  │ ...  │   │
│  │ Follow-up Qs    │ 0.80 │ 800        │ 0.95  │ ...  │   │
│  │ Analysis        │ 0.60 │ 3000       │ 0.90  │ ...  │   │
│  │ Documentation   │ 0.30 │ 4000       │ 0.85  │ ...  │   │
│  └─────────────────────────────────────────────────────┘   │
│  → Context-aware scaling (10+ models → ↓temp, ↑tokens)     │
│  → Files: groq_provider.py:14-67, gemini_provider.py:13-58 │
│  → Model: Mixtral-8x7b-32768 (32K context)                  │
│  → API: https://api.groq.com                                │
└─────────────────────────┬───────────────────────────────────┘
                          ↓
STEP 7: PACKAGING & OUTPUT (ZIP Download)
┌─────────────────────────────────────┐
│  Complete Project Package           │
│  → All generated code files         │
│  → Dockerfile + docker-compose.yml  │
│  → requirements.txt / go.mod        │
│  → README.md with setup instructions│
│  → Deployment scripts               │
│  → Environment configuration        │
│  → Component: CodePreview.tsx       │
│  → Endpoint: /api/download-code     │
└──────────────┬──────────────────────┘
               ↓
STEP 8: TESTING & FEEDBACK LOOP
┌─────────────────────────────────────────────────────────────┐
│  Quality Assurance & Continuous Improvement                 │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │  Testing Layer   │  │  Feedback Loop   │               │
│  │  ✓ Unit tests    │  │  ⚠️ PARTIAL      │               │
│  │  ✓ Integration   │  │  → User feedback │               │
│  │  ✓ pytest suite  │  │  → Error analysis│               │
│  │  ✓ Test coverage │  │  → Refinement    │               │
│  │  ✓ Validation    │  │  → Iteration     │               │
│  └──────────────────┘  └──────────────────┘               │
│  → Static Analysis: SonarQube integration (PLANNED)         │
│  → PRISM Refiner: Automated feedback loop (MISSING)         │
│  → Files: test_end_to_end.py, test_results.json            │
└─────────────────────────┬───────────────────────────────────┘
                          ↓
STEP 9: EVALUATION & BENCHMARKING
┌─────────────────────────────────────────────────────────────┐
│  Performance Metrics & Quality Analysis                     │
│  ⚠️ STATUS: MISSING - TO BE IMPLEMENTED                     │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Metrics Dashboard                                    │ │
│  │  ├─ Prompt Engineering Quality                       │ │
│  │  │  └─ Context completeness, clarity, specificity    │ │
│  │  ├─ LLM Performance Comparison                       │ │
│  │  │  └─ Mixtral vs LLaMA vs Meta vs Mistral          │ │
│  │  ├─ Code Quality Metrics                             │ │
│  │  │  └─ Complexity, maintainability, best practices   │ │
│  │  ├─ Test Coverage Analysis                           │ │
│  │  │  └─ Unit/integration coverage percentages         │ │
│  │  ├─ Generation Time & Token Usage                    │ │
│  │  │  └─ Performance benchmarks per framework          │ │
│  │  └─ Success Rate Tracking                            │ │
│  │     └─ Successful builds, deployments, tests         │ │
│  └───────────────────────────────────────────────────────┘ │
│  → Visualization: Matrices, graphs, comparative charts      │
│  → Storage: metrics.db, benchmark_results.json              │
│  → TO BE CREATED: core/evaluation/benchmark_system.py       │
└─────────────────────────────────────────────────────────────┘
```

## System Design Principles

### 1. Modularity
- **AI Providers**: Pluggable LLM backends (`groq_provider.py`, `gemini_provider.py`)
- **Generators**: Framework-specific code generators (`django_generator.py`, `go_generator.py`, `rails_generator.py`)
- **Parsers**: Separate DSL parsing logic (`dsl_parser.py`, `agentic_parser.py`)
- **Analyzers**: Intelligent analysis modules (`intelligent_analyzer.py`, `agentic_analyzer.py`)

### 2. Separation of Concerns
- **Frontend**: React/TypeScript UI (`src/components/`, `src/pages/`)
- **Backend**: Flask API (`core/app_clean.py`)
- **AI Layer**: LLM providers and orchestration (`core/ai_providers/`)
- **Generation Layer**: Code generation logic (`core/generators/`)
- **Analysis Layer**: Intelligent code analysis (`core/analyzers/`)

### 3. Scalability
- **Adaptive Hyperparameters**: Automatically scale based on project complexity
- **Caching**: DSL and generation results cached for reuse
- **Async Processing**: Background tasks for large codebases
- **Docker Support**: Containerized deployment for horizontal scaling

### 4. Observability
- **Logging**: Comprehensive logging throughout pipeline
- **Metrics**: Performance tracking (generation time, token usage)
- **Testing**: End-to-end test suite (`test_end_to_end.py`)
- **Monitoring**: Prometheus/Grafana setup (`monitoring/`)

## Data Flow

### Request Flow
```
User Input → Frontend (React)
           → API Gateway (Flask)
           → AI Provider (Groq/Gemini)
           → Question Generator
           ↓
User Responses → Context Builder
               → DSL Generator
               → DSL Parser
               → Code Generator (Django/Go/Rails)
               → Packager
               → ZIP Download
```

### LLM Integration Points

1. **Initial Questions** (`/api/generate-dsl`)
   - Model: Mixtral-8x7b-32768
   - Hyperparams: temp=0.2, max_tokens=6000, top_p=0.85
   - Input: User prompt + context
   - Output: Structured DSL YAML

2. **Follow-up Questions** (`/api/generate-followup`)
   - Model: Mixtral-8x7b-32768
   - Hyperparams: temp=0.8, max_tokens=800, top_p=0.95
   - Input: User prompt + previous answers
   - Output: 2-10 dynamic questions

3. **Code Generation** (`/api/generate-code`)
   - Model: Mixtral-8x7b-32768
   - Hyperparams: temp=0.15, max_tokens=8000, top_p=0.8
   - Input: DSL specification + framework choice
   - Output: Complete project files

4. **Analysis & Refinement** (`/api/analyze`)
   - Model: Mixtral-8x7b-32768
   - Hyperparams: temp=0.6, max_tokens=3000, top_p=0.9
   - Input: Generated code + user feedback
   - Output: Improvement suggestions

## Technology Stack

### Frontend
- **Framework**: React 18 + TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Hooks (useState, useEffect)
- **Build Tool**: Vite
- **Components**: 15+ custom components (DSLEditor, CodeEditor, QuestionFlow, etc.)

### Backend
- **Framework**: Flask (Python 3.10+)
- **AI Providers**: Groq API, Google Gemini
- **Code Generators**: Django, Go (Gin), Rails
- **Testing**: pytest, end-to-end tests
- **Database**: SQLite (development), PostgreSQL (production)

### Infrastructure
- **Containerization**: Docker + docker-compose
- **Monitoring**: Prometheus + Grafana
- **Deployment**: Docker Swarm / Kubernetes ready

## API Endpoints

### Core Endpoints
```
POST /api/generate-dsl          → Generate DSL from prompt
POST /api/generate-followup     → Generate follow-up questions
POST /api/generate-code         → Generate code from DSL
GET  /api/download-code/:id     → Download generated ZIP
POST /api/analyze               → Analyze and improve code
GET  /api/health                → Health check
```

### Data Schema
```typescript
// Request: Generate DSL
{
  prompt: string;
  context?: Record<string, any>;
  preferences?: {
    framework?: 'django' | 'go' | 'rails';
    database?: 'postgresql' | 'mysql' | 'sqlite';
    auth?: 'jwt' | 'oauth' | 'session';
  };
}

// Response: DSL
{
  dsl: string;              // YAML content
  questions: Question[];    // Follow-up questions
  metadata: {
    model: string;
    tokens_used: number;
    generation_time: number;
  };
}
```

## Current System Status

### ✅ Implemented (Steps 1-7)
- **Step 1**: User prompt input interface
- **Step 2**: 6 core context-building questions
- **Step 3**: LLM-powered follow-up questions (2-10 dynamic)
- **Step 4**: DSL parsing with visual editor
- **Step 5**: Code generation for Django/Go/Rails
- **Step 6**: Adaptive hyperparameter tuning system
- **Step 7**: ZIP packaging and download

### ⚠️ Partial (Step 8)
- **Testing**: pytest suite, end-to-end tests ✓
- **Feedback Loop**: PRISM Refiner NOT IMPLEMENTED
- **Static Analysis**: SonarQube integration PLANNED

### ❌ Missing (Step 9)
- **Evaluation System**: No benchmarking framework
- **Metrics Dashboard**: No quality/performance tracking
- **LLM Comparison**: No Mixtral vs LLaMA vs others analysis
- **Visualization**: No matrices, graphs, charts

## Performance Metrics (Current)

Based on `test_results.json` and manual testing:

- **Test Success Rate**: 80% (16/20 tests passing)
- **Code Quality Score**: 9.2/10 (manual review)
- **Generation Time**: 
  - Django: 8-12 seconds (23 files)
  - Go: 5-8 seconds (10-20 files)
  - Rails: 10-15 seconds (9-25 files)
- **Token Usage**: 
  - Average per generation: 12,000-18,000 tokens
  - Cost per generation: ~$0.02-0.05 (Groq pricing)

## Next Steps: Implementation Roadmap

### Priority 1: Evaluation & Benchmarking System (Step 9)
**File**: `core/evaluation/benchmark_system.py`
**Goal**: Track metrics, compare LLMs, visualize quality

### Priority 2: PRISM Refiner (Step 8 Completion)
**File**: `core/refinement/prism_refiner.py`
**Goal**: Automated feedback loop for continuous improvement

### Priority 3: LLM Comparison Documentation
**File**: `docs/LLM_BENCHMARKING.md`
**Goal**: Document Mixtral vs LLaMA vs Meta selection rationale

### Priority 4: Static Analysis Integration
**File**: `core/analysis/sonarqube_integration.py`
**Goal**: Automated code quality checks

## References

- **Groq API Docs**: https://console.groq.com/docs
- **LLM Hyperparameters Guide**: https://platform.openai.com/docs/guides/text-generation
- **DSL Design**: `dsl/README.md`, `dsl/example_blog.yml`
- **Generator Docs**: `core/generators/README.md`
- **Test Results**: `test_results.json`
