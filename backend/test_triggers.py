#!/usr/bin/env python3
"""
Simple test to demonstrate background clustering triggers
"""

import os
import sys
import time
import logging

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_triggers():
    """Test background clustering triggers"""
    try:
        from app import create_app
        from services.conversation_service import ConversationService
        from services.background_clustering_service import BackgroundClusteringService
        
        app = create_app()
        with app.app_context():
            print('=== Testing Background Clustering Triggers ===')
            
            # Check initial status
            bg_service = BackgroundClusteringService()
            status = bg_service.get_status()
            print(f'Initial unprocessed messages: {status["unprocessed_messages"]}')
            
            # Create a new conversation (should trigger background analysis)
            print('Creating new conversation...')
            conversation = ConversationService.create_conversation('How do I implement OAuth2 authentication in a React application?')
            print(f'Created conversation: {conversation.id}')
            
            # Add another message (should trigger background analysis)
            print('Adding user message...')
            ConversationService.add_user_message(conversation, 'What are the security best practices I should follow?')
            print('Added user message')
            
            # Check status after messages
            time.sleep(2)  # Give background threads time to process
            status = bg_service.get_status()
            print(f'After new messages - unprocessed: {status["unprocessed_messages"]}')
            print(f'Should trigger clustering: {status["should_trigger_clustering"]}')
            print(f'Reason: {status["trigger_reason"]}')
            
            print('=== Test Complete ===')
            
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_triggers()
