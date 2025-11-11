"""
Test Frontend Integration - Verify API endpoints work
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_followup_questions():
    """Test the follow-up questions endpoint"""
    print("\n" + "="*60)
    print("🧪 Testing Follow-up Questions Endpoint")
    print("="*60)
    
    # Sample user answers from frontend
    user_answers = {
        "project_area": "Task Management",
        "platform": "web",
        "auth_type": "email",
        "database": "postgresql",
        "must_have_features": ["user authentication", "task creation", "task assignment"],
        "nice_to_have_features": ["notifications", "file uploads"]
    }
    
    print(f"\n📤 Sending POST to {BASE_URL}/api/v1/generate-followup-questions")
    print(f"📦 Payload: {json.dumps(user_answers, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/generate-followup-questions",
            json={"user_answers": user_answers},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS!")
            print(f"\n📊 Response Data:")
            print(f"  - Questions count: {len(data.get('questions', []))}")
            print(f"  - Provider: {data.get('provider', 'unknown')}")
            print(f"  - Is Fallback: {data.get('is_fallback', False)}")
            print(f"  - Timestamp: {data.get('timestamp', 'N/A')}")
            
            print(f"\n❓ Generated Questions:")
            for i, q in enumerate(data.get('questions', []), 1):
                print(f"  {i}. {q}")
            
            return True
        else:
            print(f"❌ FAILED!")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ REQUEST FAILED!")
        print(f"Error: {str(e)}")
        return False

def test_health():
    """Test health endpoint"""
    print("\n" + "="*60)
    print("🏥 Testing Health Endpoint")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is healthy!")
            print(f"  - AI Available: {data.get('ai_available')}")
            print(f"  - Generators: {', '.join(data.get('generators', []))}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n🚀 InfraNest Frontend Integration Test")
    print("="*60)
    
    # Test 1: Health
    health_ok = test_health()
    
    # Test 2: Follow-up questions (the failing endpoint)
    if health_ok:
        followup_ok = test_followup_questions()
        
        print("\n" + "="*60)
        print("📋 Test Summary")
        print("="*60)
        print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
        print(f"Follow-up Questions: {'✅ PASS' if followup_ok else '❌ FAIL'}")
        print("="*60)
        
        if health_ok and followup_ok:
            print("\n🎉 All tests passed! Frontend should work now.")
            print("\n📝 Next Steps:")
            print("  1. Open http://localhost:5173 in your browser")
            print("  2. Navigate to PromptToDSL page")
            print("  3. Fill out the 6 core questions")
            print("  4. Click 'Next' after must-have features")
            print("  5. Watch the console for API logs")
            print("  6. Watch Network tab for POST request")
        else:
            print("\n⚠️  Some tests failed. Check backend logs.")
    else:
        print("\n❌ Backend is not running or not healthy.")
        print("Start backend with: cd infranest\\core ; python server.py")
