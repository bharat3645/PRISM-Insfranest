# Intelligent Question Generation System

This system provides intelligent requirements gathering by asking 6 predefined questions first, then using an LLM (Mistral 7B) to generate additional contextual follow-up questions.

## System Architecture

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   Core Questions    │───▶│  LLM Question Gen    │───▶│  Intelligent       │
│   (6 predefined)    │    │  (Mistral 7B)        │    │  Analysis          │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
```

## Core Questions (Always Asked First)

1. **What do you want this software to do?** - Project description
2. **Who will use it?** - Target audience (Just me, My team, My customers)
3. **Where would you like to use it?** - Platform (Mobile app, Website, Desktop, Chatbot)
4. **Which area best fits your project?** - Domain (Web app, E-commerce, Healthcare, etc.)
5. **Choose a programming language** - Technology preference
6. **List the must-have features** - Core functionality

## Files Structure

- `mistral_7b_model.py` - Placeholder for Mistral 7B model (you'll paste your model here)
- `question_generator.py` - Core question generation logic
- `intelligent_analyzer.py` - Integration between questions and analysis
- `api_interface.py` - REST API interface
- `agentic_analyzer.py` - Existing neural network analyzer

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Prepare Your Mistral 7B GGUF File

The system now supports GGUF format files. You'll need:

- A Mistral 7B GGUF file (e.g., `mistral-7b-instruct-v0.1.Q4_K_M.gguf`)
- Place it in your project directory or provide the full path

**Recommended GGUF files:**
- `mistral-7b-instruct-v0.1.Q4_K_M.gguf` (balanced quality/speed)
- `mistral-7b-instruct-v0.1.Q5_K_M.gguf` (higher quality)
- `mistral-7b-instruct-v0.1.Q4_0.gguf` (faster, lower memory)

**Download from Hugging Face:**
```bash
# Example download (replace with actual model)
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf
```

### 3. Run the API Server

```bash
python api_interface.py
```

The API will be available at `http://localhost:5001`

## API Usage

### Start a Session

```bash
curl -X POST http://localhost:5001/api/session/start
```

Response:
```json
{
  "success": true,
  "session_id": "uuid-here",
  "message": "Session started successfully"
}
```

### Get Core Questions

```bash
curl "http://localhost:5001/api/questions/core?session_id=uuid-here"
```

Response:
```json
{
  "success": true,
  "questions": [
    {
      "id": "description",
      "text": "What do you want this software to do?",
      "type": "core",
      "category": "purpose",
      "required": true
    },
    // ... 5 more questions
  ],
  "count": 6
}
```

### Submit Core Answer

```bash
curl -X POST http://localhost:5001/api/questions/core/description/answer \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "uuid-here",
    "question_id": "description",
    "answer": "A task management web application for teams"
  }'
```

### Generate Follow-up Questions

```bash
curl -X POST http://localhost:5001/api/questions/generate \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "uuid-here",
    "num_questions": 5
  }'
```

Response:
```json
{
  "success": true,
  "questions": [
    {
      "id": "generated_1",
      "text": "Do you need real-time collaboration features?",
      "type": "generated",
      "category": "followup",
      "required": false
    },
    // ... more generated questions
  ],
  "count": 5,
  "message": "Generated 5 follow-up questions"
}
```

### Analyze Requirements

```bash
curl -X POST http://localhost:5001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "uuid-here"
  }'
```

## Python Usage

```python
from intelligent_analyzer import IntelligentAnalyzer

# Initialize analyzer with GGUF model
mistral_path = "path/to/your/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
analyzer = IntelligentAnalyzer(mistral_path)
session_id = analyzer.start_new_session()

# Get core questions
core_questions = analyzer.get_core_questions()

# Answer core questions
analyzer.submit_core_response('description', 'A task management app')
analyzer.submit_core_response('userAudience', 'My team')
# ... answer all 6 core questions

# Generate follow-up questions
followup_result = analyzer.generate_followup_questions(5)
if followup_result['success']:
    questions = followup_result['questions']
    
    # Answer some follow-up questions
    for question in questions[:3]:
        answer = input(f"{question['text']}: ")
        analyzer.submit_followup_response(question['id'], answer)

# Perform analysis
analysis_result = analyzer.analyze_requirements()
if analysis_result['success']:
    print(f"Analysis complete! Validity: {analysis_result['analysis']['validity_score']:.2f}")
    print(f"Insights: {analysis_result['analysis']['insights']}")
    print(f"Recommendations: {analysis_result['analysis']['recommendations']}")
```

## Fallback Behavior

If the Mistral 7B model is not loaded or fails, the system automatically falls back to rule-based question generation that creates context-aware questions based on:

- Project domain (e-commerce, healthcare, etc.)
- Platform (mobile, web, desktop)
- Target audience (personal, team, customers)
- Core features mentioned

## Integration with Existing System

The system integrates with the existing `agentic_analyzer.py` to provide:

- Neural network-based complexity analysis
- Validity scoring of requirements
- Automated insights generation
- Architecture recommendations

## Example Generated Questions

**For E-commerce Projects:**
- "Do you need payment gateway integration (Stripe, PayPal)?"
- "Should products have inventory tracking and stock management?"

**For Healthcare Projects:**
- "Do you need HIPAA compliance or patient data encryption?"
- "Should the system support appointment scheduling?"

**For Mobile Apps:**
- "Do you need push notifications for mobile users?"
- "Should the app work offline or require internet connection?"

## Quick Start with GGUF

```python
# Example: Load your GGUF file and test the system
from intelligent_analyzer import IntelligentAnalyzer

# Replace with your actual GGUF file path
gguf_path = "mistral-7b-instruct-v0.1.Q4_K_M.gguf"

# Initialize with GGUF model
analyzer = IntelligentAnalyzer(gguf_path)

# Start session and get questions
session_id = analyzer.start_new_session()
questions = analyzer.get_core_questions()

# Answer questions and generate follow-ups
analyzer.submit_core_response('description', 'A task management app')
# ... answer all 6 core questions

# Generate contextual follow-up questions using Mistral 7B
followup_result = analyzer.generate_followup_questions(5)

# Perform analysis
analysis_result = analyzer.analyze_requirements()
```

## Next Steps

1. **Download your GGUF file** from Hugging Face (see recommended files above)
2. **Update the path** in `example_usage.py` to point to your GGUF file
3. **Run the example**: `python example_usage.py`
4. **Test the system** with your own requirements
5. **Integrate with frontend** using the API endpoints
6. **Customize prompts** and question generation as needed
