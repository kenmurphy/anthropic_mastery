#!/usr/bin/env python3
"""
Test script to verify the new Message model works correctly.
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
import mongoengine
from models.conversation import Conversation
from models.message import Message
from services.conversation_service import ConversationService

def test_message_model():
    """Test the new Message model functionality"""
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
        
        # Test 1: Create a conversation with initial message
        print("\n🧪 Test 1: Creating conversation with initial message")
        conversation = ConversationService.create_conversation(
            initial_message="Hello, can you help me understand Python decorators?",
            title="Python Decorators Discussion"
        )
        print(f"✅ Created conversation: {conversation.id}")
        print(f"   Title: {conversation.title}")
        print(f"   Message count: {conversation.get_message_count()}")
        
        # Test 2: Add a user message
        print("\n🧪 Test 2: Adding user message")
        user_message_id = ConversationService.add_user_message(
            conversation=conversation,
            message="Can you give me a simple example?"
        )
        print(f"✅ Added user message: {user_message_id}")
        print(f"   Message count: {conversation.get_message_count()}")
        
        # Test 3: Add an assistant message
        print("\n🧪 Test 3: Adding assistant message")
        assistant_message_id = conversation.add_message(
            speaker="assistant",
            text="Sure! Here's a simple decorator example:\n\n```python\ndef my_decorator(func):\n    def wrapper():\n        print('Before function')\n        func()\n        print('After function')\n    return wrapper\n```"
        )
        print(f"✅ Added assistant message: {assistant_message_id}")
        print(f"   Message count: {conversation.get_message_count()}")
        
        # Test 4: Retrieve messages
        print("\n🧪 Test 4: Retrieving messages")
        messages = conversation.get_messages()
        print(f"✅ Retrieved {len(messages)} messages:")
        for i, msg in enumerate(messages, 1):
            print(f"   {i}. [{msg.speaker}] {msg.text[:50]}...")
        
        # Test 5: Get message history for AI
        print("\n🧪 Test 5: Getting AI-formatted message history")
        history = conversation.get_message_history()
        print(f"✅ AI history has {len(history)} messages:")
        for i, msg in enumerate(history, 1):
            print(f"   {i}. {msg['role']}: {msg['content'][:50]}...")
        
        # Test 6: Convert to dictionary
        print("\n🧪 Test 6: Converting conversation to dictionary")
        conv_dict = conversation.to_dict(include_messages=True)
        print(f"✅ Conversation dictionary:")
        print(f"   ID: {conv_dict['id']}")
        print(f"   Title: {conv_dict['title']}")
        print(f"   Message count: {conv_dict['message_count']}")
        print(f"   Messages in dict: {len(conv_dict['messages'])}")
        
        # Test 7: Direct Message model operations
        print("\n🧪 Test 7: Direct Message model operations")
        direct_message = Message.create_message(
            conversation_id=str(conversation.id),
            speaker="user",
            text="This is a direct message creation test"
        )
        print(f"✅ Created direct message: {direct_message.message_id}")
        
        # Final verification
        final_count = conversation.get_message_count()
        print(f"\n🎉 Final message count: {final_count}")
        
        # Test message retrieval by conversation ID
        all_messages = Message.get_conversation_messages(str(conversation.id))
        print(f"✅ Retrieved {len(all_messages)} messages via Message.get_conversation_messages()")
        
        print("\n🎉 All tests passed! Message model is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_message_model()
    sys.exit(0 if success else 1)
