"""
Clean Server Starter
Simple, reliable Flask server using Groq AI only
"""

import sys
import os

# Ensure we're in the correct directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Disable Flask debug mode
os.environ['FLASK_DEBUG'] = '0'

def main():
    try:
        # Import the clean app
        from app_clean import app
        
        print("\n✅ Application loaded successfully\n")
        
        # Start server
        from werkzeug.serving import run_simple
        run_simple(
            hostname='127.0.0.1',
            port=8000,
            application=app,
            use_reloader=False,
            use_debugger=False,
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
