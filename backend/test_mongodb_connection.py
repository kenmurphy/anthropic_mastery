#!/usr/bin/env python3
"""
MongoDB Connection and Conversation Endpoint Test Script
This script tests MongoDB connectivity and conversation endpoints
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = "http://localhost:5000"
MONGODB_HOST = os.getenv('MONGODB_HOST', 'localhost')
MONGODB_PORT = int(os.getenv('MONGODB_PORT', 27017))
MONGODB_DB = os.getenv('MONGODB_DB', 'claude_db')
MONGODB_USERNAME = os.getenv('MONGODB_USERNAME', 'claude_user')
MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD', 'claude_password')

def test_mongodb_connection():
    """Test direct MongoDB connection with different authentication methods"""
    print("🔍 Testing MongoDB Connection")
    print("=" * 50)
    
    # Test configurations to try
    test_configs = [
        {
            'name': 'App User (claude_user)',
            'uri': f'mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}/{MONGODB_DB}?authSource={MONGODB_DB}'
        },
        {
            'name': 'App User with admin authSource',
            'uri': f'mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}/{MONGODB_DB}?authSource=admin'
        },
        {
            'name': 'Root User (admin)',
            'uri': f'mongodb://admin:password123@{MONGODB_HOST}:{MONGODB_PORT}/{MONGODB_DB}?authSource=admin'
        },
        {
            'name': 'No Authentication',
            'uri': f'mongodb://{MONGODB_HOST}:{MONGODB_PORT}/{MONGODB_DB}'
        }
    ]
    
    successful_config = None
    
    for config in test_configs:
        print(f"\n🧪 Testing: {config['name']}")
        print(f"   URI: {config['uri'].replace(':password123', ':***').replace(f':{MONGODB_PASSWORD}', ':***')}")
        
        try:
            client = MongoClient(config['uri'], serverSelectionTimeoutMS=5000)
            
            # Test connection
            client.admin.command('ping')
            print("   ✅ Connection successful")
            
            # Test database access
            db = client[MONGODB_DB]
            collections = db.list_collection_names()
            print(f"   ✅ Database access successful. Collections: {collections}")
            
            # Test write operation
            test_collection = db.test_connection
            test_doc = {'test': True, 'timestamp': datetime.now()}
            result = test_collection.insert_one(test_doc)
            print(f"   ✅ Write test successful. Document ID: {result.inserted_id}")
            
            # Clean up test document
            test_collection.delete_one({'_id': result.inserted_id})
            print("   ✅ Cleanup successful")
            
            successful_config = config
            client.close()
            break
            
        except OperationFailure as e:
            if e.code == 18:  # Authentication failed
                print(f"   ❌ Authentication failed: {e}")
            else:
                print(f"   ❌ Operation failed: {e}")
        except ConnectionFailure as e:
            print(f"   ❌ Connection failed: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
    
    if successful_config:
        print(f"\n✅ MongoDB connection successful with: {successful_config['name']}")
        return successful_config
    else:
        print("\n❌ All MongoDB connection attempts failed")
        return None

def fix_env_file(successful_config):
    """Update .env file with working MongoDB configuration"""
    if not successful_config:
        return False
    
    print(f"\n🔧 Updating .env file with working configuration...")
    
    # Parse the successful URI to extract credentials
    uri = successful_config['uri']
    
    # Extract username and password from URI
    if 'admin:password123' in uri:
        username = 'admin'
        password = 'password123'
        auth_source = 'admin'
    elif f'{MONGODB_USERNAME}:{MONGODB_PASSWORD}' in uri:
        username = MONGODB_USERNAME
        password = MONGODB_PASSWORD
        if 'authSource=admin' in uri:
            auth_source = 'admin'
        else:
            auth_source = MONGODB_DB
    else:
        # No auth case
        username = ''
        password = ''
        auth_source = MONGODB_DB
    
    # Read current .env file
    env_path = '.env'
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    # Update MongoDB configuration lines
    updated_lines = []
    for line in lines:
        if line.startswith('MONGODB_USERNAME='):
            updated_lines.append(f'MONGODB_USERNAME={username}\n')
        elif line.startswith('MONGODB_PASSWORD='):
            updated_lines.append(f'MONGODB_PASSWORD={password}\n')
        elif line.startswith('MONGODB_AUTH_SOURCE='):
            updated_lines.append(f'MONGODB_AUTH_SOURCE={auth_source}\n')
        else:
            updated_lines.append(line)
    
    # Add auth source if it doesn't exist
    if not any(line.startswith('MONGODB_AUTH_SOURCE=') for line in updated_lines):
        updated_lines.append(f'MONGODB_AUTH_SOURCE={auth_source}\n')
    
    # Write updated .env file
    with open(env_path, 'w') as f:
        f.writelines(updated_lines)
    
    print("   ✅ .env file updated successfully")
    return True

def test_flask_server():
    """Test if Flask server is running"""
    print("\n🌐 Testing Flask Server")
    print("=" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Flask server is running")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"   ❌ Flask server returned status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to Flask server")
        print(f"   Make sure the server is running on {BASE_URL}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def test_conversation_creation():
    """Test conversation creation endpoint"""
    print("\n💬 Testing Conversation Creation")
    print("=" * 40)
    
    # Test data
    conversation_data = {
        "initial_message": "Hello! This is a test conversation to verify MongoDB connectivity.",
        "title": "MongoDB Connection Test"
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-User-ID': 'test_user_123'  # Using a simple test user ID
    }
    
    try:
        print("   📤 Sending conversation creation request...")
        response = requests.post(
            f"{BASE_URL}/api/conversations",
            headers=headers,
            json=conversation_data,
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 201:
            conversation = response.json()
            print("   ✅ Conversation created successfully!")
            print(f"   Conversation ID: {conversation.get('id')}")
            print(f"   Title: {conversation.get('title')}")
            print(f"   Messages: {len(conversation.get('messages', []))}")
            return conversation.get('id')
        else:
            print(f"   ❌ Conversation creation failed")
            print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("   ❌ Request timed out")
        return None
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return None

def test_conversation_listing():
    """Test conversation listing endpoint"""
    print("\n📋 Testing Conversation Listing")
    print("=" * 35)
    
    headers = {
        'Content-Type': 'application/json',
        'X-User-ID': 'test_user_123'
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/conversations", headers=headers)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Conversation listing successful!")
            print(f"   Total conversations: {data.get('total', 0)}")
            print(f"   Conversations returned: {len(data.get('conversations', []))}")
            return True
        else:
            print(f"   ❌ Conversation listing failed")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 MongoDB Connection & Conversation API Test Suite")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"MongoDB Host: {MONGODB_HOST}:{MONGODB_PORT}")
    print(f"Database: {MONGODB_DB}")
    print(f"Flask Server: {BASE_URL}")
    
    # Step 1: Test MongoDB connection
    successful_config = test_mongodb_connection()
    if not successful_config:
        print("\n❌ Cannot establish MongoDB connection. Please check:")
        print("   1. MongoDB is running (docker-compose up -d)")
        print("   2. Credentials in .env file are correct")
        print("   3. MongoDB initialization completed successfully")
        return False
    
    # Step 2: Update .env file if needed
    if 'admin:password123' in successful_config['uri']:
        print("\n⚠️  Using admin credentials. Consider updating .env file.")
        fix_env_file(successful_config)
    
    # Step 3: Test Flask server
    if not test_flask_server():
        print("\n❌ Flask server is not running. Please start it with:")
        print("   cd backend && python app.py")
        return False
    
    # Step 4: Test conversation creation
    conversation_id = test_conversation_creation()
    if not conversation_id:
        print("\n❌ Conversation creation failed. Check server logs for details.")
        return False
    
    # Step 5: Test conversation listing
    if not test_conversation_listing():
        print("\n❌ Conversation listing failed.")
        return False
    
    print("\n🎉 All tests passed successfully!")
    print("\n✅ Your MongoDB connection is working correctly")
    print("✅ Conversation endpoints are functioning properly")
    print("✅ You can now create and retrieve conversations")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
