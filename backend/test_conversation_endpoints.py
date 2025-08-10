#!/usr/bin/env python3
"""
Test script for conversation endpoints
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
TEST_USER_ID = "60f1b2b3c4d5e6f7a8b9c0d1"  # Replace with actual user ID

def test_conversation_endpoints():
    """Test all conversation endpoints"""
    
    print("🧪 Testing Conversation Endpoints")
    print("=" * 50)
    
    headers = {
        'Content-Type': 'application/json',
        'X-User-ID': TEST_USER_ID
    }
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/conversations/health")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
            print("   ✅ Health check passed")
        else:
            print(f"   ❌ Health check failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    # Test 2: Create conversation
    print("\n2. Testing conversation creation...")
    conversation_data = {
        "initial_message": "Hello! Can you help me understand Python decorators?",
        "title": "Learning Python Decorators"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/conversations",
            headers=headers,
            json=conversation_data
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            conversation = response.json()
            conversation_id = conversation['id']
            print(f"   Created conversation: {conversation_id}")
            print(f"   Title: {conversation['title']}")
            print(f"   Messages: {len(conversation.get('messages', []))}")
            print("   ✅ Conversation creation passed")
        else:
            print(f"   ❌ Conversation creation failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Conversation creation error: {e}")
        return False
    
    # Test 3: List conversations
    print("\n3. Testing conversation listing...")
    try:
        response = requests.get(f"{BASE_URL}/api/conversations", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {data['total']} conversations")
            print("   ✅ Conversation listing passed")
        else:
            print(f"   ❌ Conversation listing failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Conversation listing error: {e}")
        return False
    
    # Test 4: Get specific conversation
    print("\n4. Testing conversation retrieval...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/conversations/{conversation_id}",
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            conversation = response.json()
            print(f"   Retrieved conversation: {conversation['title']}")
            print(f"   Messages: {len(conversation.get('messages', []))}")
            print("   ✅ Conversation retrieval passed")
        else:
            print(f"   ❌ Conversation retrieval failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Conversation retrieval error: {e}")
        return False
    
    # Test 5: Add message and stream response (simplified test)
    print("\n5. Testing message addition...")
    message_data = {
        "message": "Can you give me a simple example of a decorator?"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/conversations/{conversation_id}/messages",
            headers=headers,
            json=message_data,
            stream=True
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   Streaming response...")
            chunk_count = 0
            for line in response.iter_lines():
                if line:
                    chunk_count += 1
                    if chunk_count <= 3:  # Show first few chunks
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith('data: '):
                            try:
                                data = json.loads(decoded_line[6:])
                                if data.get('content'):
                                    print(f"   Chunk: {data['content'][:50]}...")
                                elif data.get('is_complete'):
                                    print("   ✅ Streaming completed")
                                    break
                            except json.JSONDecodeError:
                                pass
            print("   ✅ Message addition and streaming passed")
        else:
            print(f"   ❌ Message addition failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Message addition error: {e}")
        return False
    
    print("\n🎉 All conversation endpoint tests passed!")
    return True

def check_prerequisites():
    """Check if server is running and user exists"""
    print("🔍 Checking prerequisites...")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
        print("✅ Server is running")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print(f"   Make sure the server is running on {BASE_URL}")
        return False
    
    # Check if test user exists
    try:
        headers = {'X-User-ID': TEST_USER_ID}
        response = requests.get(f"{BASE_URL}/api/users", headers=headers)
        if response.status_code == 401:
            print(f"❌ Test user {TEST_USER_ID} not found")
            print("   Please create a test user or update TEST_USER_ID in this script")
            return False
        print("✅ Test user exists")
    except Exception as e:
        print(f"⚠️  Could not verify user existence: {e}")
        print("   Proceeding anyway...")
    
    return True

if __name__ == "__main__":
    print("🚀 Conversation API Test Suite")
    print(f"Testing against: {BASE_URL}")
    print(f"Test user ID: {TEST_USER_ID}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Exiting.")
        sys.exit(1)
    
    if test_conversation_endpoints():
        print("\n✅ All tests passed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)
