#!/usr/bin/env python3
"""
InfraNest LLM Setup Script
Helps users configure Groq API for follow-up question generation
"""

import os
from pathlib import Path
from typing import Dict, Optional


def check_existing_key() -> Optional[str]:
    """Check if API key already exists and ask user if they want to update"""
    existing_key = os.getenv('GROQ_API_KEY')
    if existing_key:
        print(f"✅ Groq API key already set: {existing_key[:8]}...")
        if input("Do you want to update it? (y/N): ").lower() != 'y':
            return None  # User doesn't want to update
    return existing_key


def get_api_key_from_user() -> Optional[str]:
    """Prompt user for API key and validate it"""
    print("To get a Groq API key:")
    print("1. Go to https://console.groq.com/keys")
    print("2. Sign in with your account")
    print("3. Click 'Create API Key'")
    print("4. Copy the key")
    print()
    
    api_key = input("Enter your Groq API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Exiting.")
        return None
    
    # Validate API key format (basic check)
    if len(api_key) < 20:
        print("⚠️  Warning: API key seems too short. Please verify.")
        if input("Continue anyway? (y/N): ").lower() != 'y':
            return None
    
    return api_key


def save_api_key(api_key: str) -> bool:
    """Save API key to .env file"""
    env_file = Path.home() / '.infranest' / '.env'
    env_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Read existing content if file exists
        existing_vars = read_existing_env_vars(env_file)
        
        # Update with new API key
        existing_vars['GROQ_API_KEY'] = api_key
        
        # Write back all variables
        write_env_vars(env_file, existing_vars)
        
        print(f"✅ API key saved to {env_file}")
        return True
    except Exception as e:
        print(f"❌ Error saving API key: {e}")
        print("You can manually set it with: export GROQ_API_KEY=your_key_here")
        return False


def read_existing_env_vars(env_file: Path) -> Dict[str, str]:
    """Read existing environment variables from file"""
    existing_vars: Dict[str, str] = {}
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    existing_vars[key] = value
    return existing_vars


def write_env_vars(env_file: Path, vars_dict: Dict[str, str]) -> None:
    """Write environment variables to file"""
    with open(env_file, 'w') as f:
        for key, value in vars_dict.items():
            f.write(f"{key}={value}\n")


def print_success_message() -> None:
    """Print success message with usage instructions"""
    print()
    print("🚀 You're all set! InfraNest will now use Groq for:")
    print("   • Intelligent follow-up question generation")
    print("   • Advanced DSL specification creation")
    print("   • Better backend code generation")
    print()
    print("Try running: python copilot.py design-backend")


def setup_groq():
    """Setup Groq API key for InfraNest"""
    print("🤖 InfraNest LLM Setup (Groq)")
    print("=" * 50)
    print()
    print("This script will help you configure Groq API for intelligent")
    print("follow-up question generation in InfraNest.")
    print()
    
    # Check if API key already exists
    if check_existing_key() is None and os.getenv('GROQ_API_KEY'):
        return  # User chose not to update
    
    # Get API key from user
    api_key = get_api_key_from_user()
    if not api_key:
        return
    
    # Set environment variable for current session
    os.environ['GROQ_API_KEY'] = api_key
    
    # Save to file
    if save_api_key(api_key):
        print_success_message()

def load_env():
    """Load environment variables from .env file"""
    env_file = Path.home() / '.infranest' / '.env'
    if env_file.exists():
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
        except Exception as e:
            print(f"⚠️  Warning: Could not load .env file: {e}")

if __name__ == '__main__':
    load_env()
    setup_groq()
