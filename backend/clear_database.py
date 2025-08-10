#!/usr/bin/env python3
"""
Script to clear all MongoDB documents from the database
"""

import os
import sys
from mongoengine import connect, disconnect
from config import Config

# Import all models to ensure they're registered
from models.user import User
from models.thread import Thread
from models.thought import Thought

def clear_database():
    """Clear all documents from all collections"""
    try:
        # Connect to MongoDB
        config = Config()
        connect(**config.MONGODB_SETTINGS)
        
        print("Connected to MongoDB...")
        
        # Clear all collections
        collections_cleared = 0
        
        # Clear Thoughts first (due to references)
        thought_count = Thought.objects.count()
        if thought_count > 0:
            Thought.drop_collection()
            print(f"Cleared {thought_count} thoughts from 'Thoughts' collection")
            collections_cleared += 1
        else:
            print("No thoughts found in 'Thoughts' collection")
        
        # Clear Threads
        thread_count = Thread.objects.count()
        if thread_count > 0:
            Thread.drop_collection()
            print(f"Cleared {thread_count} threads from 'threads' collection")
            collections_cleared += 1
        else:
            print("No threads found in 'threads' collection")
        
        # Clear Users last
        user_count = User.objects.count()
        if user_count > 0:
            User.drop_collection()
            print(f"Cleared {user_count} users from 'users' collection")
            collections_cleared += 1
        else:
            print("No users found in 'users' collection")
        
        print(f"\n✅ Database cleared successfully! {collections_cleared} collections were cleared.")
        
    except Exception as e:
        print(f"❌ Error clearing database: {str(e)}")
        sys.exit(1)
    finally:
        disconnect()

if __name__ == "__main__":
    print("🗑️  Clearing all MongoDB documents...")
    print("⚠️  This will permanently delete all data!")
    
    # Ask for confirmation
    confirm = input("Are you sure you want to continue? (yes/no): ").lower().strip()
    
    if confirm in ['yes', 'y']:
        clear_database()
    else:
        print("Operation cancelled.")
