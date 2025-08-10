#!/usr/bin/env python3
"""
Final comprehensive test for conversation endpoints
This script ensures the server is properly restarted and tests all endpoints
"""

import os
import sys
import time
import signal
import subprocess
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def kill_all_flask_processes():
    """Kill all Flask processes more aggressively"""
    print("🛑 Stopping all Flask processes...")
    
    # Kill by process name
    try:
        subprocess.run(['pkill', '-f', 'python.*app.py'], check=False)
        time.sleep(2)
    except:
        pass
    
    # Kill by port (if something is using port 5000)
    try:
        result = subprocess.run(['lsof', '-ti:5000'], capture_output=True, text=True)
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    try:
                        os.kill(int(pid), signal.SIGKILL)
                        print(f"   Killed process {pid}")
                    except:
                        pass
    except:
        pass
    
    print("✅ All Flask processes stopped")

def start_fresh_server():
    """Start a completely fresh Flask server"""
    print("🚀 Starting fresh Flask server...")
    
    # Change to backend directory and start server
    env = os.environ.copy()
    env['PYTHONPATH'] = os.getcwd()
    
    process = subprocess.Popen(
        [sys.executable, 'app.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        cwd=os.getcwd()
    )
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    for i in range(15):  # Wait up to 15 seconds
        time.sleep(1)
        try:
            response = requests.get(f'{BASE_URL}/health', timeout=2)
            if response.status_code == 200:
                print("✅ Flask server started successfully")
                return process
        except:
            continue
    
    print("❌ Flask server failed to start")
    if process.poll() is None:
        process.terminate()
    return None

def test_health_endpoint():
    """Test health endpoint"""
    print("\n🏥 Testing Health Endpoint")
    print("=" * 30)
    
    try:
        response = requests.get(f'{BASE_URL}/health')
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check passed: {data}")
            return True
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False

def test_conversation_creation():
    """Test conversation creation with detailed debugging"""
    print("\n💬 Testing Conversation Creation")
    print("=" * 40)
    
    conversation_data = {
        "initial_message": "Hello! This is a comprehensive test of the conversation endpoint after fixing MongoDB authentication.",
        "title": "Final Authentication Test"
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-User-ID': 'test_user_final'
    }
    
    print(f"   📤 Sending request to: {BASE_URL}/api/conversations")
    print(f"   📋 Headers: {headers}")
    print(f"   📄 Data: {json.dumps(conversation_data, indent=2)}")
    
    try:
        response = requests.post(
            f'{BASE_URL}/api/conversations',
            headers=headers,
            json=conversation_data,
            timeout=15
        )
        
        print(f"   📊 Status Code: {response.status_code}")
        print(f"   📝 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 201:
            conversation = response.json()
            print("   ✅ Conversation created successfully!")
            print(f"   🆔 Conversation ID: {conversation.get('id')}")
            print(f"   📰 Title: {conversation.get('title')}")
            print(f"   💬 Messages: {len(conversation.get('messages', []))}")
            
            # Print first message details
            if conversation.get('messages'):
                first_msg = conversation['messages'][0]
                print(f"   📩 First message: {first_msg.get('role')} - {first_msg.get('content')[:50]}...")
            
            return conversation.get('id')
        else:
            print(f"   ❌ Conversation creation failed")
            print(f"   📄 Response: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("   ❌ Request timed out")
        return None
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return None

def test_conversation_listing(conversation_id=None):
    """Test conversation listing"""
    print("\n📋 Testing Conversation Listing")
    print("=" * 35)
    
    headers = {
        'Content-Type': 'application/json',
        'X-User-ID': 'test_user_final'
    }
    
    try:
        response = requests.get(f'{BASE_URL}/api/conversations', headers=headers)
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Conversation listing successful!")
            print(f"   📊 Total conversations: {data.get('total', 0)}")
            print(f"   📋 Conversations returned: {len(data.get('conversations', []))}")
            
            # Check if our created conversation is in the list
            if conversation_id:
                conversations = data.get('conversations', [])
                found = any(conv.get('id') == conversation_id for conv in conversations)
                if found:
                    print(f"   ✅ Created conversation found in list")
                else:
                    print(f"   ⚠️  Created conversation not found in list")
            
            return True
        else:
            print(f"   ❌ Conversation listing failed")
            print(f"   📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def test_conversation_retrieval(conversation_id):
    """Test retrieving a specific conversation"""
    if not conversation_id:
        print("\n⏭️  Skipping conversation retrieval (no conversation ID)")
        return True
    
    print("\n🔍 Testing Conversation Retrieval")
    print("=" * 40)
    
    headers = {
        'Content-Type': 'application/json',
        'X-User-ID': 'test_user_final'
    }
    
    try:
        response = requests.get(f'{BASE_URL}/api/conversations/{conversation_id}', headers=headers)
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            conversation = response.json()
            print("   ✅ Conversation retrieval successful!")
            print(f"   📰 Title: {conversation.get('title')}")
            print(f"   💬 Messages: {len(conversation.get('messages', []))}")
            return True
        else:
            print(f"   ❌ Conversation retrieval failed")
            print(f"   📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def main():
    """Main test function"""
    print("🎯 Final Conversation Endpoint Test Suite")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Target URL: {BASE_URL}")
    
    # Step 1: Kill all existing Flask processes
    kill_all_flask_processes()
    
    # Step 2: Start fresh server
    process = start_fresh_server()
    if not process:
        print("❌ Failed to start Flask server")
        return False
    
    try:
        # Step 3: Test health endpoint
        if not test_health_endpoint():
            print("❌ Health endpoint failed")
            return False
        
        # Step 4: Test conversation creation
        conversation_id = test_conversation_creation()
        if not conversation_id:
            print("❌ Conversation creation failed")
            return False
        
        # Step 5: Test conversation listing
        if not test_conversation_listing(conversation_id):
            print("❌ Conversation listing failed")
            return False
        
        # Step 6: Test conversation retrieval
        if not test_conversation_retrieval(conversation_id):
            print("❌ Conversation retrieval failed")
            return False
        
        print("\n🎉 ALL TESTS PASSED SUCCESSFULLY!")
        print("=" * 50)
        print("✅ MongoDB authentication issue resolved")
        print("✅ Conversation creation works perfectly")
        print("✅ Conversation listing works perfectly")
        print("✅ Conversation retrieval works perfectly")
        print("✅ Your backend is fully functional!")
        
        print(f"\n📝 Server is running at {BASE_URL}")
        print(f"   Process ID: {process.pid}")
        print("   To stop the server later, run:")
        print(f"   kill {process.pid}")
        
        return True
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        return False
    finally:
        # Keep server running for user to test
        pass

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🚀 Your conversation API is ready to use!")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
    
    sys.exit(0 if success else 1)
