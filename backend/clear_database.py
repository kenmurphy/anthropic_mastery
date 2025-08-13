#!/usr/bin/env python3
"""
Database Clear Script for Anthropic Mastery Project

This script connects to the MongoDB database and clears out all model collections:
- conversations
- messages  
- conversation_clusters
- clustering_runs
- courses

Usage:
    python clear_database.py [--confirm]
    
Options:
    --confirm    Skip confirmation prompt and clear immediately
"""

import os
import sys
import argparse
from typing import Dict, Any, Optional, Tuple
from dotenv import load_dotenv
from mongoengine import connect, disconnect
from pymongo import MongoClient

# Add the backend directory to the path so we can import models
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.conversation import Conversation
from models.message import Message
from models.cluster import ConversationCluster, ClusteringRun
from models.course import Course

def get_database_connection() -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """Get MongoDB connection details from config"""
    load_dotenv()
    
    # Use the same connection logic as the main app
    mongodb_uri = os.environ.get('MONGODB_URI')
    if mongodb_uri:
        return mongodb_uri, None
    else:
        db_config: Dict[str, Any] = {
            'host': os.environ.get('MONGODB_HOST', 'localhost'),
            'port': int(os.environ.get('MONGODB_PORT', 27017)),
            'db': os.environ.get('MONGODB_DB', 'claude_db'),
        }
        
        # Add authentication if provided
        username = os.environ.get('MONGODB_USERNAME')
        password = os.environ.get('MONGODB_PASSWORD')
        if username and password:
            db_config['username'] = username
            db_config['password'] = password
            db_config['authentication_source'] = os.environ.get('MONGODB_AUTH_SOURCE', 'admin')
        
        return None, db_config

def connect_to_database() -> bool:
    """Connect to MongoDB using the same configuration as the main app"""
    mongodb_uri, db_config = get_database_connection()
    
    try:
        if mongodb_uri:
            print(f"Connecting to MongoDB via URI...")
            connect(host=mongodb_uri)
        elif db_config:
            host = db_config.get('host', 'localhost')
            port = db_config.get('port', 27017)
            db = db_config.get('db', 'claude_db')
            print(f"Connecting to MongoDB at {host}:{port}/{db}...")
            connect(**db_config)
        else:
            print("❌ No database configuration found")
            return False
        print("✅ Connected to MongoDB successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return False

def get_collection_stats() -> Dict[str, Any]:
    """Get current document counts for all collections"""
    stats: Dict[str, Any] = {}
    
    try:
        # Use the MongoEngine objects manager
        stats['conversations'] = Conversation.objects.count()  # type: ignore
        stats['messages'] = Message.objects.count()  # type: ignore
        stats['conversation_clusters'] = ConversationCluster.objects.count()  # type: ignore
        stats['clustering_runs'] = ClusteringRun.objects.count()  # type: ignore
        stats['courses'] = Course.objects.count()  # type: ignore
    except Exception as e:
        print(f"⚠️  Warning: Could not get collection stats: {e}")
        stats = {
            'conversations': '?',
            'messages': '?', 
            'conversation_clusters': '?',
            'clustering_runs': '?',
            'courses': '?'
        }
    
    return stats

def clear_all_collections() -> Tuple[int, int]:
    """Clear all model collections"""
    collections_cleared = 0
    total_documents_deleted = 0
    
    # Define collections to clear in dependency order (messages before conversations, etc.)
    collections = [
        ('messages', Message),
        ('conversations', Conversation),
        ('conversation_clusters', ConversationCluster),
        ('clustering_runs', ClusteringRun),
        ('courses', Course),
    ]
    
    for collection_name, model_class in collections:
        try:
            count_before = model_class.objects.count()  # type: ignore
            if count_before > 0:
                print(f"Clearing {collection_name} ({count_before} documents)...")
                model_class.drop_collection()  # type: ignore
                print(f"✅ Cleared {collection_name}")
                total_documents_deleted += count_before
                collections_cleared += 1
            else:
                print(f"⏭️  {collection_name} already empty")
        except Exception as e:
            print(f"❌ Failed to clear {collection_name}: {e}")
    
    return collections_cleared, total_documents_deleted

def main() -> None:
    parser = argparse.ArgumentParser(description='Clear all database collections for Anthropic Mastery project')
    parser.add_argument('--confirm', action='store_true', 
                       help='Skip confirmation prompt and clear immediately')
    args = parser.parse_args()
    
    print("🗑️  Anthropic Mastery Database Clear Script")
    print("=" * 50)
    
    # Connect to database
    if not connect_to_database():
        sys.exit(1)
    
    # Get current stats
    print("\n📊 Current Database Status:")
    stats = get_collection_stats()
    total_docs = 0
    for collection, count in stats.items():
        print(f"  {collection}: {count} documents")
        if isinstance(count, int):
            total_docs += count
    
    if total_docs == 0:
        print("\n✨ Database is already empty!")
        disconnect()
        return
    
    # Confirmation
    if not args.confirm:
        print(f"\n⚠️  WARNING: This will permanently delete ALL {total_docs} documents from the database!")
        print("This action cannot be undone.")
        
        response = input("\nAre you sure you want to continue? (type 'yes' to confirm): ")
        if response.lower() != 'yes':
            print("❌ Operation cancelled")
            disconnect()
            return
    
    # Clear collections
    print("\n🧹 Clearing database collections...")
    collections_cleared, documents_deleted = clear_all_collections()
    
    # Final stats
    print(f"\n✅ Database clearing complete!")
    print(f"   Collections cleared: {collections_cleared}")
    print(f"   Documents deleted: {documents_deleted}")
    
    # Verify clearing
    print("\n📊 Final Database Status:")
    final_stats = get_collection_stats()
    for collection, count in final_stats.items():
        print(f"  {collection}: {count} documents")
    
    disconnect()
    print("\n🎉 Database successfully cleared!")

if __name__ == "__main__":
    main()
