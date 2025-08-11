#!/usr/bin/env python3
"""
Test script for background clustering functionality
"""

import os
import sys
import time
import logging
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_background_clustering():
    """Test the background clustering system"""
    try:
        # Import after setting up path
        from app import create_app
        from models.conversation import Conversation
        from models.message import Message
        from services.background_clustering_service import BackgroundClusteringService
        from services.conversation_service import ConversationService
        
        # Create Flask app context
        app = create_app()
        
        with app.app_context():
            logger.info("=== Background Clustering Test ===")
            
            # Test 1: Check service initialization
            logger.info("Test 1: Initializing BackgroundClusteringService...")
            background_service = BackgroundClusteringService()
            status = background_service.get_status()
            logger.info(f"Service status: {status}")
            
            # Test 2: Create test conversations if needed
            logger.info("Test 2: Checking existing conversations...")
            conversation_count = Conversation.objects.count()
            message_count = Message.objects.count()
            logger.info(f"Found {conversation_count} conversations and {message_count} messages")
            
            if conversation_count < 3:
                logger.info("Creating test conversations...")
                test_messages = [
                    "How do I implement a REST API in Python using Flask?",
                    "What's the difference between SQL joins and how do I use them?",
                    "Can you help me debug this JavaScript async/await function?",
                    "How do I set up a MongoDB database with proper indexing?",
                    "What are the best practices for React component architecture?"
                ]
                
                for i, msg in enumerate(test_messages):
                    logger.info(f"Creating conversation {i+1}: {msg[:50]}...")
                    conversation = ConversationService.create_conversation(msg)
                    logger.info(f"Created conversation {conversation.id}")
                    
                    # Add a follow-up message to make it more realistic
                    follow_up = f"Can you provide more details about this topic?"
                    ConversationService.add_user_message(conversation, follow_up)
                    logger.info(f"Added follow-up message to conversation {conversation.id}")
                    
                    # Small delay to avoid overwhelming the system
                    time.sleep(1)
            
            # Test 3: Check background service status after message creation
            logger.info("Test 3: Checking background service status...")
            status = background_service.get_status()
            logger.info(f"Updated service status: {status}")
            
            # Test 4: Force clustering if needed
            if status.get('should_trigger_clustering', False):
                logger.info("Test 4: Forcing background clustering...")
                started = background_service.force_clustering()
                if started:
                    logger.info("Background clustering started successfully")
                    
                    # Wait a bit for clustering to complete
                    logger.info("Waiting for clustering to complete...")
                    for i in range(30):  # Wait up to 30 seconds
                        time.sleep(1)
                        if not background_service.is_clustering_in_progress():
                            logger.info(f"Clustering completed after {i+1} seconds")
                            break
                    else:
                        logger.warning("Clustering is still in progress after 30 seconds")
                else:
                    logger.info("Clustering was already in progress")
            else:
                logger.info("Test 4: Clustering not needed based on current conditions")
            
            # Test 5: Check final status
            logger.info("Test 5: Final status check...")
            final_status = background_service.get_status()
            logger.info(f"Final service status: {final_status}")
            
            # Test 6: Check if clusters were created
            from services.conversation_clustering_service import ConversationClusteringService
            clustering_service = ConversationClusteringService()
            clusters = clustering_service.get_all_clusters()
            logger.info(f"Found {len(clusters)} clusters:")
            for cluster in clusters:
                logger.info(f"  - {cluster['label']}: {len(cluster['conversation_ids'])} conversations")
            
            logger.info("=== Background Clustering Test Complete ===")
            
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_background_clustering()
