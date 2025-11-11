#!/usr/bin/env python3
"""
Debug Test Script for InfraNest PRISM API
Tests all AI-dependent endpoints with full traceability
No silent failures - raises exceptions on error
"""

import requests
import json
from typing import Dict, Any

# Backend URL
BASE_URL = "http://localhost:8000/api/v1"

# Test data
SAMPLE_PROMPT = """
Create a task management system with:
- User authentication
- Task CRUD operations
- Task assignment to users
- Due dates and priorities
"""

SAMPLE_USER_ANSWERS = {
    "database": "PostgreSQL",
    "auth": "JWT",
    "deployment": "Docker"
}

SAMPLE_DSL = {
    "meta": {
        "name": "task_manager",  # lowercase with underscores
        "version": "1.0.0",
        "framework": "django"
    },
    "models": {
        "Task": {
            "fields": {
                "title": {"type": "string", "required": True, "max_length": 200},
                "description": {"type": "text"},
                "due_date": {"type": "datetime"},
                "completed": {"type": "boolean", "default": False}
            }
        },
        "User": {
            "fields": {
                "email": {"type": "email", "required": True, "unique": True},
                "password": {"type": "string", "required": True, "hashed": True},
                "created_at": {"type": "datetime", "auto_now_add": True}
            }
        }
    }
}


def print_response(response: requests.Response, endpoint: str) -> None:
    """Pretty print API response with full details"""
    print("\n" + "="*80)
    print(f"🔍 API TRACE: {endpoint}")
    print("="*80)
    print(f"📊 Status Code: {response.status_code}")
    print(f"⏱️  Response Time: {response.elapsed.total_seconds():.2f}s")
    print("-"*80)
    
    try:
        data = response.json()
        print("📋 Response JSON:")
        print(json.dumps(data, indent=2)[:2000])  # First 2000 chars
        
        # Extract key metrics
        if 'provider' in data:
            print(f"\n🎯 Provider: {data['provider']}")
        if 'is_fallback' in data:
            print(f"⚠️  Is Fallback: {data['is_fallback']}")
        if 'files' in data:
            print(f"📂 Files Generated: {len(data['files'])}")
            if isinstance(data['files'], list) and len(data['files']) > 0:
                print(f"📄 First file: {data['files'][0].get('path', 'unknown')}")
        if 'questions' in data:
            print(f"❓ Questions Count: {len(data['questions'])}")
            if data['questions']:
                print(f"📝 First question: {data['questions'][0]}")
        if 'error' in data:
            print(f"❌ Error: {data['error']}")
            
    except json.JSONDecodeError:
        print("❌ Non-JSON Response:")
        print(response.text[:500])
    
    print("="*80 + "\n")
    
    # Raise exception if not successful
    if response.status_code >= 400:
        raise RuntimeError(f"API request failed with status {response.status_code}: {response.text[:200]}")


def test_health() -> None:
    """Test health check endpoint"""
    print("\n🏥 Testing Health Check Endpoint...")
    
    response = requests.get("http://localhost:8000/health")  # No /api/v1 prefix
    print_response(response, "GET /health")
    
    data = response.json()
    assert data.get('status') == 'healthy', "Health check failed"
    print("✅ Health check passed")


def test_followup() -> None:
    """Test follow-up question generation"""
    print("\n❓ Testing Follow-up Question Generation...")
    
    payload = {
        "user_answers": SAMPLE_USER_ANSWERS,
        "num_questions": 3
    }
    
    response = requests.post(
        f"{BASE_URL}/generate-followup-questions",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print_response(response, "POST /api/v1/generate-followup-questions")
    
    data = response.json()
    assert 'questions' in data, "No questions in response"
    assert len(data['questions']) > 0, "Empty questions array"
    assert data.get('provider') != 'default', "Using default fallback instead of LLM"
    
    print(f"✅ Follow-up test passed - Generated {len(data['questions'])} questions")


def test_code_generation() -> None:
    """Test code generation endpoint"""
    print("\n🔨 Testing Code Generation...")
    
    payload = {
        "dsl": SAMPLE_DSL,
        "framework": "django"
    }
    
    response = requests.post(
        f"{BASE_URL}/generate-code",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print_response(response, "POST /api/v1/generate-code")
    
    data = response.json()
    assert 'files' in data, "No files in response"
    assert len(data['files']) > 0, "No files generated"
    
    print(f"✅ Code generation test passed - Generated {len(data['files'])} files")
    
    # Show file structure
    print("\n📂 Generated File Structure:")
    for i, file_data in enumerate(data['files'][:10]):  # First 10 files
        path = file_data.get('path', 'unknown')
        size = len(file_data.get('content', ''))
        print(f"   {i+1}. {path} ({size} bytes)")
    
    if len(data['files']) > 10:
        print(f"   ... and {len(data['files']) - 10} more files")


def main():
    """Run all debug tests"""
    print("\n" + "🚀 "*20)
    print("InfraNest PRISM - API Debug Test Suite")
    print("🚀 "*20 + "\n")
    
    try:
        # Test in order of dependency
        test_health()
        test_followup()
        test_code_generation()
        
        print("\n" + "✅ "*20)
        print("ALL TESTS PASSED - No silent failures detected")
        print("✅ "*20 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend at", BASE_URL)
        print("   Make sure the backend is running on port 8000")
        print("   Run: cd infranest/core && python server.py\n")
        
    except Exception as e:
        print("\n" + "❌ "*20)
        print(f"TEST FAILED: {str(e)}")
        print("❌ "*20 + "\n")
        raise


if __name__ == "__main__":
    main()
