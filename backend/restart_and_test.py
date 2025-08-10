#!/usr/bin/env python3
"""
Script to restart Flask server and test conversation endpoints
"""

import os
import sys
import time
import signal
import subprocess
import requests
from datetime import datetime

def find_flask_process():
    """Find running Flask process"""
    try:
        result = subprocess.run(['pgrep', '-f', 'python.*app.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            return [int(pid) for pid in pids if pid]
        return []
    except Exception:
        return []

def stop_flask_server():
    """Stop running Flask server"""
    pids = find_flask_process()
    if pids:
        print(f"🛑 Stopping Flask server (PIDs: {pids})")
        for pid in pids:
            try:
                os.kill(pid, signal.SIGTERM)
                time.sleep(1)
            except ProcessLookupError:
                pass
        
        # Wait a bit and check if processes are still running
        time.sleep(2)
        remaining_pids = find_flask_process()
        if remaining_pids:
            print(f"⚠️  Force killing remaining processes: {remaining_pids}")
            for pid in remaining_pids:
                try:
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        print("✅ Flask server stopped")
    else:
        print("ℹ️  No Flask server running")

def start_flask_server():
    """Start Flask server in background"""
    print("🚀 Starting Flask server...")
    
    # Start server in background
    process = subprocess.Popen(
        ['python', 'app.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.getcwd()
    )
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    for i in range(10):
        time.sleep(1)
        try:
            response = requests.get('http://localhost:5000/health', timeout=2)
            if response.status_code == 200:
                print("✅ Flask server started successfully")
                return process
        except:
            continue
    
    print("❌ Flask server failed to start")
    process.terminate()
    return None

def test_conversation_creation():
    """Test conversation creation"""
    print("\n💬 Testing Conversation Creation")
    print("=" * 40)
    
    conversation_data = {
        "initial_message": "Hello! This is a test after server restart.",
        "title": "Server Restart Test"
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-User-ID': 'test_user_restart'
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/api/conversations',
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
            return True
        else:
            print(f"   ❌ Conversation creation failed")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Main function"""
    print("🔄 Flask Server Restart & Test")
    print("=" * 40)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Step 1: Stop existing server
    stop_flask_server()
    
    # Step 2: Start new server
    process = start_flask_server()
    if not process:
        print("❌ Failed to start Flask server")
        return False
    
    # Step 3: Test conversation creation
    success = test_conversation_creation()
    
    if success:
        print("\n🎉 Success! Conversation endpoint is working!")
        print("✅ MongoDB authentication issue resolved")
        print("✅ Server is running with correct configuration")
        print("\n📝 Server is running in background. To stop it later:")
        print(f"   kill {process.pid}")
    else:
        print("\n❌ Conversation creation still failing")
        print("Check server logs for more details")
        process.terminate()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
