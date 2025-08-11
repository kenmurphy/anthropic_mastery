#!/usr/bin/env python3
"""
Clear conversations and messages collections for testing the new Message model.
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
import mongoengine

def clear_collections():
    """Clear conversations and messages collections"""
    try:
        # Connect to database
        mongodb_settings = Config.MONGODB_SETTINGS
        mongoengine.connect(
            db=mongodb_settings['db'],
            host=mongodb_settings['host'],
            port=mongodb_settings['port'],
            username=mongodb_settings['username'],
            password=mongodb_settings['password'],
            authentication_source=mongodb_settings['authentication_source']
        )
        print("✅ Connected to MongoDB")
        
        # Drop collections
        from mongoengine.connection import get_db
        db = get_db()
        
        # Drop conversations collection
        db.conversations.drop()
        print("✅ Dropped conversations collection")
        
        # Drop messages collection
        db.messages.drop()
        print("✅ Dropped messages collection")
        
        print("🎉 Database cleared successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        return False

if __name__ == "__main__":
    clear_collections()
