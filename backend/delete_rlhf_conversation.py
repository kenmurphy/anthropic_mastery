#!/usr/bin/env python3
"""
Delete RLHF Conversation Script for Anthropic Mastery Project

This script searches for and deletes conversations/messages containing the specific text:
"What are alternatives to RLHF for aligning LLMs?"

The script will:
1. Search for messages containing the target text
2. Find associated conversations
3. Delete the messages and conversations
4. Provide detailed reporting of what was deleted

Usage:
    python delete_rlhf_conversation.py [--confirm] [--dry-run]
    
Options:
    --confirm    Skip confirmation prompt and delete immediately
    --dry-run    Show what would be deleted without actually deleting
"""

import os
import sys
import argparse
from typing import Dict, Any, Optional, Tuple, List
from dotenv import load_dotenv
from mongoengine import connect, disconnect

# Add the backend directory to the path so we can import models
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.conversation import Conversation
from models.message import Message

# Target text to search for
TARGET_TEXT = "What are alternatives to RLHF for aligning LLMs?"

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

def find_conversations_starting_with_target() -> List[Conversation]:
    """Find conversations that START with the target message"""
    try:
        # Get all conversations
        all_conversations = Conversation.objects()  # type: ignore
        matching_conversations = []
        
        for conv in all_conversations:
            try:
                # Get messages for this conversation, ordered by creation time
                messages = conv.get_messages()
                if messages and len(messages) > 0:
                    # Check if the first message contains the target text
                    first_message = messages[0]
                    if TARGET_TEXT.lower() in first_message.content.lower():
                        matching_conversations.append(conv)
            except Exception as e:
                print(f"⚠️  Warning: Could not check conversation {conv.id}: {e}")  # type: ignore
        
        return matching_conversations
    except Exception as e:
        print(f"❌ Error searching for conversations: {e}")
        return []

def analyze_conversations(conversations: List[Conversation]) -> Dict[str, Any]:
    """Analyze conversations that start with target message - all will be deleted entirely"""
    analysis = {
        'conversations_to_delete': [],
        'total_messages_in_conversations': 0,
        'total_conversations': len(conversations)
    }
    
    for conv in conversations:
        try:
            all_messages = conv.get_messages()
            analysis['total_messages_in_conversations'] += len(all_messages)
            
            # Since we found conversations that START with the target text,
            # we delete the entire conversation
            analysis['conversations_to_delete'].append({
                'conversation': conv,
                'message_count': len(all_messages),
                'starts_with_target': True
            })
        except Exception as e:
            print(f"⚠️  Warning: Could not analyze conversation {conv.id}: {e}")  # type: ignore
    
    return analysis

def delete_target_data(analysis: Dict[str, Any], dry_run: bool = False) -> Dict[str, int]:
    """Delete conversations that start with the target message"""
    results = {
        'messages_deleted': 0,
        'conversations_deleted': 0,
        'errors': 0
    }
    
    if dry_run:
        print("🔍 DRY RUN - No actual deletions will be performed")
        return results
    
    # Delete entire conversations that start with the target message
    for conv_info in analysis['conversations_to_delete']:
        conversation = conv_info['conversation']
        try:
            # Delete all messages in the conversation
            Message.objects(conversation_id=str(conversation.id)).delete()  # type: ignore
            results['messages_deleted'] += conv_info['message_count']
            
            # Delete the conversation itself
            conversation.delete()
            results['conversations_deleted'] += 1
            
            print(f"✅ Deleted entire conversation '{conversation.title}' with {conv_info['message_count']} messages")
            
        except Exception as e:
            print(f"❌ Error deleting conversation {conversation.id}: {e}")  # type: ignore
            results['errors'] += 1
    
    return results

def main() -> None:
    parser = argparse.ArgumentParser(description='Delete conversations/messages containing RLHF text')
    parser.add_argument('--confirm', action='store_true', 
                       help='Skip confirmation prompt and delete immediately')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be deleted without actually deleting')
    args = parser.parse_args()
    
    print("🎯 RLHF Conversation Deletion Script")
    print("=" * 50)
    print(f"Target text: '{TARGET_TEXT}'")
    
    # Connect to database
    if not connect_to_database():
        sys.exit(1)
    
    # Find conversations that start with target message
    print(f"\n🔍 Searching for conversations that START with target message...")
    conversations = find_conversations_starting_with_target()
    
    if not conversations:
        print("✨ No conversations found that start with the target text!")
        disconnect()
        return
    
    print(f"💬 Found {len(conversations)} conversation(s) that start with target message")
    
    # Analyze conversations
    print(f"\n📊 Analyzing conversations...")
    analysis = analyze_conversations(conversations)
    
    # Display analysis results
    print(f"\n📋 Analysis Results:")
    print(f"  Total conversations found: {analysis['total_conversations']}")
    print(f"  Conversations to delete entirely: {len(analysis['conversations_to_delete'])}")
    print(f"  Total messages in affected conversations: {analysis['total_messages_in_conversations']}")
    
    # Show detailed breakdown
    if analysis['conversations_to_delete']:
        print(f"\n🗑️  Conversations to delete entirely (start with target message):")
        for conv_info in analysis['conversations_to_delete']:
            conv = conv_info['conversation']
            print(f"  - '{conv.title}' ({conv_info['message_count']} messages)")
    
    # Show sample conversations
    print(f"\n📄 Sample conversations that start with target message:")
    for i, conv_info in enumerate(analysis['conversations_to_delete'][:3]):  # Show first 3 conversations
        conv = conv_info['conversation']
        try:
            messages = conv.get_messages()
            if messages:
                first_message = messages[0]
                content_str = str(first_message.content)
                preview = content_str[:100] + "..." if len(content_str) > 100 else content_str
                print(f"  {i+1}. '{conv.title}' - First message: [{first_message.speaker}] {preview}")
        except Exception as e:
            print(f"  {i+1}. '{conv.title}' - Could not load messages: {e}")
    if len(analysis['conversations_to_delete']) > 3:
        print(f"  ... and {len(analysis['conversations_to_delete']) - 3} more")
    
    if args.dry_run:
        print(f"\n🔍 DRY RUN MODE - No deletions will be performed")
    elif len(analysis['conversations_to_delete']) == 0:
        print(f"\n✨ No conversations to delete!")
        disconnect()
        return
    
    # Confirmation
    if not args.confirm and not args.dry_run:
        print(f"\n⚠️  WARNING: This will permanently delete:")
        print(f"   - {len(analysis['conversations_to_delete'])} entire conversations")
        print(f"   - {analysis['total_messages_in_conversations']} total messages")
        print("This action cannot be undone.")
        
        response = input("\nAre you sure you want to continue? (type 'yes' to confirm): ")
        if response.lower() != 'yes':
            print("❌ Operation cancelled")
            disconnect()
            return
    
    # Perform deletion
    print(f"\n🗑️  {'Simulating' if args.dry_run else 'Performing'} deletions...")
    results = delete_target_data(analysis, dry_run=args.dry_run)
    
    # Final results
    print(f"\n✅ {'Simulation' if args.dry_run else 'Deletion'} complete!")
    print(f"   Messages {'would be ' if args.dry_run else ''}deleted: {results['messages_deleted']}")
    print(f"   Conversations {'would be ' if args.dry_run else ''}deleted: {results['conversations_deleted']}")
    if results['errors'] > 0:
        print(f"   Errors encountered: {results['errors']}")
    
    disconnect()
    print(f"\n🎉 {'Simulation' if args.dry_run else 'Operation'} completed successfully!")

if __name__ == "__main__":
    main()
