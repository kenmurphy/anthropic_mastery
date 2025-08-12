#!/usr/bin/env python3
"""
Generate a secure SECRET_KEY for Flask application
"""

import secrets
import string

def generate_secret_key(length=32):
    """Generate a cryptographically secure random string for Flask SECRET_KEY"""
    # Use a combination of letters, digits, and some special characters
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    secret_key = ''.join(secrets.choice(alphabet) for _ in range(length))
    return secret_key

if __name__ == "__main__":
    # Generate a 32-character secret key
    secret_key = generate_secret_key(32)
    
    print("=" * 60)
    print("FLASK SECRET_KEY GENERATOR")
    print("=" * 60)
    print(f"Generated SECRET_KEY: {secret_key}")
    print("=" * 60)
    print("\nInstructions:")
    print("1. Copy the SECRET_KEY above")
    print("2. Add it to your environment variables:")
    print("   - For local development: Add to backend/.env")
    print("   - For Render deployment: Add to Environment Variables")
    print("   - For other deployments: Set as environment variable")
    print("\nExample usage:")
    print(f"SECRET_KEY={secret_key}")
    print("=" * 60)
