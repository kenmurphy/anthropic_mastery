#!/usr/bin/env python3
"""
Simple test script to verify the Flask backend setup
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the server. Make sure the Flask app is running.")
        return False

def test_root_endpoint():
    """Test the root endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Root endpoint passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Root endpoint failed with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the server")
        return False

def test_user_creation():
    """Test user creation"""
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/users",
            headers={"Content-Type": "application/json"},
            data=json.dumps(user_data)
        )
        
        if response.status_code == 201:
            print("✅ User creation passed")
            user_info = response.json()
            print(f"   Created user: {user_info['user']['email']}")
            return user_info['user']['id']
        else:
            print(f"❌ User creation failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the server")
        return None


def test_thread_creation(owner_id):
    """Test thread creation"""
    if not owner_id:
        print("❌ Cannot test thread creation without owner ID")
        return None
        
    thread_data = {
        "title": "Test Thread"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/threads",
            headers={
                "Content-Type": "application/json",
                "X-User-ID": owner_id
            },
            data=json.dumps(thread_data)
        )
        
        if response.status_code == 201:
            print("✅ Thread creation passed")
            thread_info = response.json()
            print(f"   Created thread: {thread_info['thread']['title']}")
            return thread_info['thread']['id']
        else:
            print(f"❌ Thread creation failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the server")
        return None

def test_Thought_creation(thread_id):
    """Test Thought creation"""
    if not thread_id:
        print("❌ Cannot test Thought creation without thread ID")
        return None
        
    Thought_data = {
        "thread_id": thread_id,
        "type": "note",
        "content": {
            "markdown": "# Test Thought\nThis is a test Thought with some markdown content."
        },
        "metadata": {
            "tags": ["test", "demo"]
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/Thoughts",
            headers={"Content-Type": "application/json"},
            data=json.dumps(Thought_data)
        )
        
        if response.status_code == 201:
            print("✅ Thought creation passed")
            Thought_info = response.json()
            print(f"   Created Thought: {Thought_info['Thought']['type']} (order: {Thought_info['Thought']['order']})")
            return Thought_info['Thought']['id']
        else:
            print(f"❌ Thought creation failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the server")
        return None

def test_get_users():
    """Test getting users list"""
    try:
        response = requests.get(f"{BASE_URL}/api/users")
        if response.status_code == 200:
            print("✅ Get users list passed")
            users_info = response.json()
            print(f"   Found {users_info['total']} users")
            return True
        else:
            print(f"❌ Get users list failed with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the server")
        return False


def main():
    """Run all tests"""
    print("🧪 Testing Claude Backend Setup")
    print("=" * 40)
    
    # Test basic connectivity
    if not test_health_check():
        print("\n❌ Basic connectivity failed. Please check:")
        print("   1. Flask app is running (python app.py)")
        print("   2. MongoDB is running (docker-compose up -d)")
        return
    
    if not test_root_endpoint():
        return
    
    # Test API functionality
    print("\n🔧 Testing API functionality...")
    
    # Create a test user
    user_id = test_user_creation()
    
    # Create a test thread
    thread_id = test_thread_creation(user_id)
    
    # Create a test Thought
    Thought_id = test_Thought_creation(thread_id)
    
    # Test listing endpoints
    test_get_users()
    
    print("\n" + "=" * 40)
    if user_id and thread_id and Thought_id:
        print("🎉 All tests passed! Your backend is working correctly.")
        print(f"\n📝 Test data created:")
        print(f"   User ID: {user_id}")
        print(f"   Thread ID: {thread_id}")
        print(f"   Thought ID: {Thought_id}")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
    
    print(f"\n🌐 API is available at: {BASE_URL}")
    print(f"📚 API documentation: {BASE_URL}/")

if __name__ == "__main__":
    main()
