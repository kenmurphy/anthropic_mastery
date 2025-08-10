#!/usr/bin/env python3
"""
Test script to verify full conversation flow with Anthropic integration
"""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_conversation_creation():
    """Test creating a new conversation"""
    print("🧪 Testing conversation creation...")
    
    try:
        from services.conversation_service import ConversationService
        
        # Create a new conversation
        initial_message = "Hello Claude! Can you help me understand machine learning?"
        conversation = ConversationService.create_conversation(initial_message)
        
        print(f"✅ Created conversation with ID: {conversation.id}")
        print(f"✅ Title: '{conversation.title}'")
        print(f"✅ Initial message count: {len(conversation.messages)}")
        
        return conversation
        
    except Exception as e:
        print(f"❌ Error creating conversation: {e}")
        return None

def test_streaming_response(conversation):
    """Test streaming AI response"""
    print("\n🧪 Testing streaming AI response...")
    
    try:
        from services.conversation_service import ConversationService
        
        service = ConversationService()
        
        # Add a user message
        user_message = "What are the main types of machine learning?"
        ConversationService.add_user_message(conversation, user_message)
        
        print(f"✅ Added user message: '{user_message}'")
        
        # Stream AI response
        print("🔄 Streaming AI response...")
        accumulated_response = ""
        chunk_count = 0
        
        for chunk in service.stream_ai_response(conversation):
            chunk_count += 1
            if chunk.get('content'):
                accumulated_response += chunk['content']
                # Print first few characters of each chunk for verification
                if len(chunk['content']) > 0:
                    print(f"   Chunk {chunk_count}: '{chunk['content'][:50]}{'...' if len(chunk['content']) > 50 else ''}'")
            
            if chunk.get('is_complete'):
                print(f"✅ Streaming completed after {chunk_count} chunks")
                break
        
        if accumulated_response:
            print(f"✅ Full response length: {len(accumulated_response)} characters")
            print(f"✅ Response preview: '{accumulated_response[:200]}{'...' if len(accumulated_response) > 200 else ''}'")
        else:
            print("❌ No response content received")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error streaming response: {e}")
        return False

def test_conversation_retrieval(conversation):
    """Test retrieving conversation by ID"""
    print("\n🧪 Testing conversation retrieval...")
    
    try:
        from services.conversation_service import ConversationService
        
        # Retrieve conversation by ID
        retrieved = ConversationService.get_conversation_by_id(str(conversation.id))
        
        if retrieved:
            print(f"✅ Retrieved conversation with ID: {retrieved.id}")
            print(f"✅ Message count: {len(retrieved.messages)}")
            print(f"✅ Title: '{retrieved.title}'")
            
            # Check message types
            user_messages = [msg for msg in retrieved.messages if msg.role == 'user']
            assistant_messages = [msg for msg in retrieved.messages if msg.role == 'assistant']
            
            print(f"✅ User messages: {len(user_messages)}")
            print(f"✅ Assistant messages: {len(assistant_messages)}")
            
            return True
        else:
            print("❌ Failed to retrieve conversation")
            return False
        
    except Exception as e:
        print(f"❌ Error retrieving conversation: {e}")
        return False

def test_title_generation(conversation):
    """Test conversation title generation"""
    print("\n🧪 Testing title generation...")
    
    try:
        from services.conversation_service import ConversationService
        
        # Update conversation title
        ConversationService.update_conversation_title(conversation)
        
        # Reload conversation to see updated title
        updated = ConversationService.get_conversation_by_id(str(conversation.id))
        
        if updated:
            print(f"✅ Updated title: '{updated.title}'")
            return True
        else:
            print("❌ Failed to update title")
            return False
        
    except Exception as e:
        print(f"❌ Error updating title: {e}")
        return False

def cleanup_test_conversation(conversation):
    """Clean up test conversation"""
    try:
        if conversation:
            conversation.delete()
            print(f"🧹 Cleaned up test conversation {conversation.id}")
    except Exception as e:
        print(f"⚠️ Warning: Could not clean up conversation: {e}")

def main():
    """Run full conversation flow test"""
    print("=" * 60)
    print("FULL CONVERSATION FLOW TEST WITH ANTHROPIC")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key or api_key == "your-anthropic-api-key-here":
        print("❌ ANTHROPIC_API_KEY not set properly in .env file")
        print("Please set a valid Anthropic API key to test the full flow")
        return
    
    success = True
    conversation = None
    
    try:
        # Test conversation creation
        conversation = test_conversation_creation()
        if not conversation:
            success = False
        
        # Test streaming response
        if conversation and not test_streaming_response(conversation):
            success = False
        
        # Test conversation retrieval
        if conversation and not test_conversation_retrieval(conversation):
            success = False
        
        # Test title generation
        if conversation and not test_title_generation(conversation):
            success = False
        
    except Exception as e:
        print(f"❌ Unexpected error during testing: {e}")
        success = False
    
    finally:
        # Clean up
        if conversation:
            cleanup_test_conversation(conversation)
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL CONVERSATION FLOW TESTS PASSED!")
        print("\nThe Anthropic integration is working correctly:")
        print("✅ Conversation creation")
        print("✅ Streaming AI responses")
        print("✅ Message storage and retrieval")
        print("✅ Title generation")
        print("\nYour app is ready to use Claude for conversations!")
    else:
        print("❌ SOME TESTS FAILED")
        print("Please check the errors above and ensure:")
        print("- MongoDB is running")
        print("- ANTHROPIC_API_KEY is valid")
        print("- All dependencies are installed")
    print("=" * 60)

if __name__ == "__main__":
    main()
