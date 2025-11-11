🧠 InfraNest (PRISM) — AI Coding Agent Operations Manual
🧭 Objective

This AI Copilot operates as a structured backend generation assistant. Its responsibility is to preserve repo integrity, enforce architectural consistency, and generate complete, deployable backend systems from refined prompts — with no bloat, no duplication, and no structural violations.

💡 System Purpose

InfraNest (PRISM) is a research-backed AI system that turns natural language into full-stack backend applications using a controlled pipeline:

Prompt → Context Builder → Follow-up Refinement → DSL (YAML) → Validation → LLM → Code → Packaging → Testing → Evaluation


📌 Copilot must prioritize error resolution, file cleanliness, and maintain structural fidelity — never overwrite working files unless validation fails.

✅ Non-Negotiable Principles

One File, One Purpose: Do not generate alternate versions (server_old.py, server_v2.py, run_server.py). Stick to:

core/server.py → ✅ canonical backend entry point

core/app_clean.py → ✅ router handler layer

No Redundancy: Periodically scan for obsolete or duplicated files. Use integrity.json + file hashes to:

Flag duplicate modules

Remove old stubs or partials

Fix, Don't Replace: If an error exists in a valid file, repair it. Do not generate new files in parallel (e.g., don’t create config_dev.py if dev_settings.py exists).

Only Work with Best Version: Validate all similar files and select the one with:

Highest code coverage

Functional test pass rate

Most complete logic

No TODOs or placeholder sections

📦 Startup Checklist

🔄 Clean up temp files:

Remove unused: *_old.py, *_v2.py, __tmp__*/

Clear cache: __pycache__/, .DS_Store

✅ Load canonical files:

core/server.py

core/app_clean.py

parsers/dsl_parser.py

ai_providers/simple_ai_manager.py

✅ Validate DSL spec

🧠 Inject into LLM via simple_ai_manager.py

🏗️ Generate all code via BaseGenerator-based module

🧪 Run test suite

📁 Package & ZIP

📊 Log metrics

📋 Copilot Tasks
Task	Description
Prompt Processing	Use follow-ups + context questions to refine input
DSL Validation	Validate required fields in YAML spec
AI Execution (LLM)	Use only simple_ai_manager.py → Mixtral (Groq)
Code Generation	Generate complete, testable files only
Regeneration Logic	Regenerate only the broken module (never all)
File Integrity Management	Use integrity.json to check structure and hash
Clean-Up Ops	Periodically purge stale/unused code
Evaluation	Store generation metrics, compare over time
🔒 File Access Control
Directory	Purpose	Copilot Write Access
core/	API logic, entrypoint	✅ Controlled
generators/	Framework-specific gen	✅ Controlled
parsers/	DSL parser + validator	✅ Controlled
dsl/	YAML DSL definitions	✅ Controlled
frontend/	React frontend	❌ No
tests/	Test execution only	❌ No
evaluation/	Benchmark logs	✅ Append-only
templates/	Jinja2 for backend	✅ Controlled

🛑 Never write to frontend/, tests/, or overwrite working files in core/ without validation failure.

⚙️ Canonical Files Only

Allowed Backend Entrypoints (do not replicate):

✅ core/server.py ← Main

✅ core/app_clean.py ← Routes

❌ run_server.py, server_v2.py, old_server.py → Must be deleted if found

Code Generator Entrypoints:

✅ generators/django_generator.py

✅ generators/rails_generator.py

✅ generators/go_fiber_generator.py

AI Routing Logic:

✅ ai_providers/simple_ai_manager.py

❌ __init__.py legacy switch → deprecated

🛠️ Maintenance Rules

Validate Before Action:
Call validate_dsl() first — if invalid, exit gracefully and log error.

Auto-Detect Broken Modules:
Scan logs + tracebacks → isolate failure → regenerate only that unit.

Log All Events:
Save every generation's timestamp, metrics, failures in evaluation/metrics.json.

Purge Stale Code Periodically:
On every third run or on version upgrade, scan and delete:

Redundant files

Placeholder files

Anything outside defined schema

📊 Metric Logging Fields

prompt_type: raw / refined / injected

framework: django / go-fiber / rails

files_generated: count

test_pass_rate: float

generation_time_seconds: float

code_quality_score: 0–10 (external linter)

retries: int

integrity_passed: bool

🔥 Security & Quality Enforcement

LLM outputs must be post-processed:

Strip placeholder tokens

Remove shell escape commands

DSL injection strictly controlled via JSON schema

Sanitize inputs from Groq/Gemini before templating

Every generated file must pass linting and static analysis

Default to enterprise-grade test coverage + structure

🚫 Forbidden Actions

❌ Never overwrite existing working modules blindly

❌ Never generate files with duplicate intent (server.py, run_server.py, etc.)

❌ Never push placeholders like # TODO, pass, or ...

❌ Never inject uncontrolled DSL into template render

❌ Never bypass DSL validation

✅ Required Final Deliverables

✔️ Functional backend (Django, Go, or Rails)

✔️ Docker-ready

✔️ Test suite: all pass

✔️ Full file tree packaged

✔️ Prompt → DSL → Code trace saved

✔️ No redundant files in repo

✔️ Metrics updated in evaluation/

Agent Version: PRISM-Agent-v2.1
Status: 🔒 Hardened for Production Delivery
Last Updated: November 2025