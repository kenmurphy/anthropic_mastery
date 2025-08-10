#!/usr/bin/env python3
"""
Test Flask app's MongoDB connection directly
"""

import os
import sys
from dotenv import load_dotenv
from mongoengine import connect, disconnect
from config import config
from models.conversation import Conversation

# Load environment variables
load_dotenv()

def test_flask_mongodb_connection():
    """Test MongoDB connection using Flask app configuration"""
    print("🧪 Testing Flask App MongoDB Connection")
    print("=" * 50)
    
    # Get configuration
    config_name = os.environ.get('FLASK_ENV', 'development')
    app_config = config[config_name]
    
    print(f"Configuration: {config_name}")
    print(f"MongoDB Settings: {app_config.MONGODB_SETTINGS}")
    
    try:
        # Disconnect any existing connections
        disconnect()
        
        # Connect using Flask app configuration
        connect(**app_config.MONGODB_SETTINGS)
        print("✅ MongoDB connection established")
        
        # Test creating a conversation
        conversation = Conversation(
            title="Flask MongoDB Test",
            messages=[]
        )
        
        # Add a test message
        conversation.add_message("user", "This is a test message from Flask app")
        print("✅ Conversation created and message added")
        
        # Retrieve the conversation
        retrieved = Conversation.objects(id=conversation.id).first()
        if retrieved:
            print(f"✅ Conversation retrieved: {retrieved.title}")
            print(f"   Messages: {len(retrieved.messages)}")
            
            # Clean up - delete the test conversation
            retrieved.delete()
            print("✅ Test conversation deleted")
            
            return True
        else:
            print("❌ Could not retrieve conversation")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_direct_pymongo():
    """Test direct PyMongo connection with same credentials"""
    print("\n🔧 Testing Direct PyMongo Connection")
    print("=" * 40)
    
    from pymongo import MongoClient
    
    # Get credentials from environment
    host = os.getenv('MONGODB_HOST', 'localhost')
    port = int(os.getenv('MONGODB_PORT', 27017))
    db_name = os.getenv('MONGODB_DB', 'claude_db')
    username = os.getenv('MONGODB_USERNAME')
    password = os.getenv('MONGODB_PASSWORD')
    auth_source = os.getenv('MONGODB_AUTH_SOURCE', 'admin')
    
    uri = f'mongodb://{username}:{password}@{host}:{port}/{db_name}?authSource={auth_source}'
    print(f"URI: {uri.replace(f':{password}', ':***')}")
    
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        print("✅ Direct PyMongo connection successful")
        
        # Test database operations
        db = client[db_name]
        test_collection = db.test_flask_connection
        
        # Insert test document
        result = test_collection.insert_one({'test': 'flask_test', 'timestamp': 'now'})
        print(f"✅ Document inserted: {result.inserted_id}")
        
        # Clean up
        test_collection.delete_one({'_id': result.inserted_id})
        print("✅ Test document cleaned up")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Direct PyMongo error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Flask MongoDB Connection Test")
    print("=" * 40)
    
    # Test 1: Direct PyMongo connection
    pymongo_success = test_direct_pymongo()
    
    # Test 2: Flask app MongoDB connection
    flask_success = test_flask_mongodb_connection()
    
    if pymongo_success and flask_success:
        print("\n🎉 All tests passed!")
        print("✅ MongoDB connection is working correctly")
        print("✅ Flask app can connect to MongoDB")
        print("✅ Conversation model works properly")
        return True
    else:
        print("\n❌ Some tests failed")
        if not pymongo_success:
            print("   - Direct PyMongo connection failed")
        if not flask_success:
            print("   - Flask app MongoDB connection failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
