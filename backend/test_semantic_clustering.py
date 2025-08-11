#!/usr/bin/env python3
"""
Test script for semantic clustering functionality
"""

import os
import sys
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.conversation import Conversation
from models.message import Message
from models.cluster import ConversationCluster, ClusteringRun
from services.message_analysis_service import MessageAnalysisService
from services.conversation_clustering_service import ConversationClusteringService
from config import Config
from mongoengine import connect

def setup_database():
    """Setup database connection"""
    try:
        connect(
            db=Config.MONGODB_DB,
            host=Config.MONGODB_HOST,
            port=Config.MONGODB_PORT,
            username=Config.MONGODB_USERNAME,
            password=Config.MONGODB_PASSWORD
        )
        print("✅ Connected to MongoDB successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return False

def create_test_conversations():
    """Create test conversations with different technical topics"""
    test_conversations = [
        {
            'title': 'Python Flask API Development',
            'messages': [
                ('user', 'How do I create a REST API with Flask?'),
                ('assistant', 'To create a REST API with Flask, you need to install Flask, create routes with decorators, and handle HTTP methods. Here\'s a basic example with GET and POST endpoints.'),
                ('user', 'How do I handle database connections in Flask?'),
                ('assistant', 'You can use SQLAlchemy or MongoEngine for database connections. For MongoDB, use MongoEngine with connection configuration.')
            ]
        },
        {
            'title': 'React Component Architecture',
            'messages': [
                ('user', 'What are the best practices for React component structure?'),
                ('assistant', 'Best practices include using functional components with hooks, proper state management, component composition, and separating concerns between UI and business logic.'),
                ('user', 'How do I manage state in React applications?'),
                ('assistant', 'You can use useState for local state, useContext for shared state, or external libraries like Redux or Zustand for complex state management.')
            ]
        },
        {
            'title': 'Database Query Optimization',
            'messages': [
                ('user', 'How can I optimize slow SQL queries?'),
                ('assistant', 'Query optimization involves adding proper indexes, analyzing query execution plans, avoiding N+1 queries, and using appropriate JOIN strategies.'),
                ('user', 'What are database indexes and when should I use them?'),
                ('assistant', 'Indexes are data structures that improve query performance by creating shortcuts to data. Use them on frequently queried columns, foreign keys, and WHERE clause conditions.')
            ]
        },
        {
            'title': 'Machine Learning Model Training',
            'messages': [
                ('user', 'How do I train a classification model with scikit-learn?'),
                ('assistant', 'Use scikit-learn\'s classification algorithms like RandomForest or SVM. Split your data, fit the model, and evaluate with metrics like accuracy and F1-score.'),
                ('user', 'What is cross-validation and why is it important?'),
                ('assistant', 'Cross-validation splits data into multiple folds to evaluate model performance more reliably and detect overfitting.')
            ]
        },
        {
            'title': 'Docker Container Deployment',
            'messages': [
                ('user', 'How do I containerize a Python application with Docker?'),
                ('assistant', 'Create a Dockerfile with Python base image, copy your code, install dependencies with pip, and expose the application port.'),
                ('user', 'What are Docker best practices for production?'),
                ('assistant', 'Use multi-stage builds, minimize image size, run as non-root user, and use specific version tags instead of latest.')
            ]
        },
        {
            'title': 'API Authentication and Security',
            'messages': [
                ('user', 'How do I implement JWT authentication in my API?'),
                ('assistant', 'JWT authentication involves creating tokens with user claims, signing them with a secret, and validating them on protected routes.'),
                ('user', 'What are the security considerations for REST APIs?'),
                ('assistant', 'Key security practices include HTTPS, input validation, rate limiting, proper authentication, and protecting against common vulnerabilities like SQL injection.')
            ]
        }
    ]
    
    created_conversations = []
    
    for conv_data in test_conversations:
        # Create conversation
        conversation = Conversation(title=conv_data['title'])
        conversation.save()
        
        # Add messages
        for speaker, content in conv_data['messages']:
            conversation.add_message(speaker, content)
        
        created_conversations.append(conversation)
        print(f"✅ Created conversation: {conv_data['title']}")
    
    return created_conversations

def test_message_analysis():
    """Test message analysis functionality"""
    print("\n🔍 Testing Message Analysis...")
    
    analysis_service = MessageAnalysisService()
    
    # Get a test message
    message = Message.objects.first()
    if not message:
        print("❌ No messages found for testing")
        return False
    
    print(f"📝 Analyzing message: {message.content[:50]}...")
    
    # Test analysis
    success = analysis_service.analyze_message(message)
    
    if success:
        print(f"✅ Message analysis successful")
        print(f"   Technical concepts: {message.technical_concepts}")
        print(f"   Embedding dimensions: {len(message.embedding) if message.embedding else 0}")
        return True
    else:
        print("❌ Message analysis failed")
        return False

def test_conversation_clustering():
    """Test conversation clustering functionality"""
    print("\n🎯 Testing Conversation Clustering...")
    
    clustering_service = ConversationClusteringService()
    
    # Run clustering
    success = clustering_service.cluster_all_conversations()
    
    if success:
        print("✅ Clustering completed successfully")
        
        # Get clusters
        clusters = clustering_service.get_all_clusters()
        print(f"📊 Created {len(clusters)} clusters:")
        
        for cluster in clusters:
            print(f"   • {cluster['label']}: {cluster['conversation_count']} conversations")
            print(f"     Key concepts: {', '.join(cluster['key_concepts'][:3])}")
        
        return True
    else:
        print("❌ Clustering failed")
        return False

def test_api_endpoints():
    """Test that the clustering API endpoints are working"""
    print("\n🌐 Testing API Integration...")
    
    try:
        from routes.clustering_routes import clustering_service
        
        # Test getting all clusters
        clusters = clustering_service.get_all_clusters()
        print(f"✅ API can retrieve {len(clusters)} clusters")
        
        if clusters:
            # Test getting specific cluster
            cluster = clustering_service.get_cluster_by_id(clusters[0]['cluster_id'])
            if cluster:
                print(f"✅ API can retrieve specific cluster: {cluster['label']}")
            else:
                print("❌ Failed to retrieve specific cluster")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def cleanup_test_data():
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    
    try:
        # Delete all test data
        ConversationCluster.objects.delete()
        ClusteringRun.objects.delete()
        Message.objects.delete()
        Conversation.objects.delete()
        
        print("✅ Test data cleaned up")
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")

def main():
    """Main test function"""
    print("🚀 Starting Semantic Clustering Test Suite")
    print("=" * 50)
    
    # Setup database
    if not setup_database():
        return
    
    try:
        # Clean up any existing data
        cleanup_test_data()
        
        # Create test conversations
        conversations = create_test_conversations()
        print(f"✅ Created {len(conversations)} test conversations")
        
        # Test message analysis
        if not test_message_analysis():
            print("❌ Message analysis test failed")
            return
        
        # Test clustering
        if not test_conversation_clustering():
            print("❌ Clustering test failed")
            return
        
        # Test API integration
        if not test_api_endpoints():
            print("❌ API integration test failed")
            return
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed! Semantic clustering system is working.")
        print("\nNext steps:")
        print("1. Start the Flask server: python app.py")
        print("2. Test the API endpoints:")
        print("   - GET /api/clusters")
        print("   - GET /api/clustering/status")
        print("   - POST /api/clustering/run")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Ask if user wants to keep test data
        keep_data = input("\nKeep test data for further testing? (y/N): ").lower().strip()
        if keep_data != 'y':
            cleanup_test_data()

if __name__ == "__main__":
    main()
