#!/usr/bin/env python3
"""
Script to clear all conversations and messages from MongoDB
This script clears the current conversation and message collections used by the Anthropic Mastery platform.
"""

import os
import sys
from mongoengine import connect, disconnect
from config import Config

# Import current models
from models.conversation import Conversation
from models.message import Message

def clear_conversations_and_messages():
    """Clear all conversations and messages from the database"""
    try:
        # Connect to MongoDB
        config = Config()
        connect(**config.MONGODB_SETTINGS)
        
        print("Connected to MongoDB...")
        
        # Get counts before clearing
        message_count = Message.objects.count()
        conversation_count = Conversation.objects.count()
        
        print(f"Found {conversation_count} conversations and {message_count} messages")
        
        # Clear messages first (they reference conversations)
        if message_count > 0:
            Message.drop_collection()
            print(f"✅ Cleared {message_count} messages from 'messages' collection")
        else:
            print("No messages found in 'messages' collection")
        
        # Clear conversations
        if conversation_count > 0:
            Conversation.drop_collection()
            print(f"✅ Cleared {conversation_count} conversations from 'conversations' collection")
        else:
            print("No conversations found in 'conversations' collection")
        
        print(f"\n🎉 Database cleared successfully!")
        print(f"   - {conversation_count} conversations deleted")
        print(f"   - {message_count} messages deleted")
        
    except Exception as e:
        print(f"❌ Error clearing database: {str(e)}")
        sys.exit(1)
    finally:
        disconnect()

if __name__ == "__main__":
    print("🗑️  Clearing all conversations and messages from MongoDB...")
    print("⚠️  This will permanently delete all conversation data!")
    
    # Ask for confirmation
    confirm = input("Are you sure you want to continue? (yes/no): ").lower().strip()
    
    if confirm in ['yes', 'y']:
        clear_conversations_and_messages()
    else:
        print("Operation cancelled.")
