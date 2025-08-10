#!/usr/bin/env python3
"""
Test script to verify Anthropic integration is working properly
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_anthropic_service():
    """Test basic Anthropic service functionality"""
    print("Testing Anthropic Service Integration...")
    
    try:
        from services.anthropic_service import AnthropicService
        
        # Check if API key is set
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key or api_key == "your-anthropic-api-key-here":
            print("❌ ANTHROPIC_API_KEY not set properly in .env file")
            print("Please set a valid Anthropic API key to test the integration")
            return False
        
        print("✅ Anthropic API key found in environment")
        
        # Initialize service
        service = AnthropicService()
        print("✅ AnthropicService initialized successfully")
        
        # Test basic conversation response (non-streaming for simplicity)
        print("🧪 Testing conversation title generation...")
        
        test_messages = [
            {"role": "user", "content": "Hello, can you help me understand Python decorators?"},
            {"role": "assistant", "content": "I'd be happy to help you understand Python decorators! Decorators are a powerful feature in Python that allow you to modify or extend the behavior of functions or classes without permanently modifying their code."}
        ]
        
        title = service.generate_conversation_title(test_messages)
        print(f"✅ Generated title: '{title}'")
        
        print("\n🎉 All Anthropic integration tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure the anthropic package is installed: pip install anthropic")
        return False
    except Exception as e:
        print(f"❌ Error testing Anthropic service: {e}")
        return False

def test_conversation_service():
    """Test conversation service with Anthropic integration"""
    print("\nTesting Conversation Service with Anthropic...")
    
    try:
        from services.conversation_service import ConversationService
        
        # Initialize service
        service = ConversationService()
        print("✅ ConversationService initialized with Anthropic")
        
        # Check that it's using AnthropicService
        if hasattr(service, 'anthropic_service'):
            print("✅ ConversationService is using AnthropicService")
        else:
            print("❌ ConversationService is not using AnthropicService")
            return False
        
        print("✅ Conversation service integration test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing conversation service: {e}")
        return False

def main():
    """Run all integration tests"""
    print("=" * 50)
    print("ANTHROPIC INTEGRATION TEST")
    print("=" * 50)
    
    success = True
    
    # Test Anthropic service
    if not test_anthropic_service():
        success = False
    
    # Test conversation service
    if not test_conversation_service():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED - Anthropic integration is working!")
        print("\nNext steps:")
        print("1. Set a valid ANTHROPIC_API_KEY in your .env file")
        print("2. Start the Flask server: python app.py")
        print("3. Test the conversation endpoints")
    else:
        print("❌ SOME TESTS FAILED - Please check the errors above")
    print("=" * 50)

if __name__ == "__main__":
    main()
