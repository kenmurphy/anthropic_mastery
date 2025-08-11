#!/usr/bin/env python3
"""
Reset Clustering Status Script

This script resets the 'processed_for_clustering' field to False for all Message models
in the MongoDB database. This is useful when you want to reprocess all messages for
clustering analysis.

Usage:
    python reset_clustering_status.py

The script will:
1. Connect to the MongoDB database using the same configuration as the main app
2. Update all Message documents to set processed_for_clustering = False
3. Report the number of documents updated
4. Handle errors gracefully
"""

import os
import sys
from mongoengine import connect, disconnect
from dotenv import load_dotenv

# Add the backend directory to the Python path so we can import our models
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.message import Message
from config import Config

def connect_to_database():
    """Connect to MongoDB using the application configuration"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Build connection string
        config = Config()
        
        # Connect to MongoDB
        if config.MONGODB_USERNAME and config.MONGODB_PASSWORD:
            connect(
                db=config.MONGODB_DB,
                host=config.MONGODB_HOST,
                port=config.MONGODB_PORT,
                username=config.MONGODB_USERNAME,
                password=config.MONGODB_PASSWORD,
                authentication_source='admin'
            )
        else:
            connect(
                db=config.MONGODB_DB,
                host=config.MONGODB_HOST,
                port=config.MONGODB_PORT
            )
        
        print(f"✅ Connected to MongoDB database: {config.MONGODB_DB}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {str(e)}")
        return False

def get_clustering_status_summary():
    """Get a summary of current clustering status"""
    try:
        total_messages = Message.objects.count()
        processed_messages = Message.objects(processed_for_clustering=True).count()
        unprocessed_messages = Message.objects(processed_for_clustering=False).count()
        
        return {
            'total': total_messages,
            'processed': processed_messages,
            'unprocessed': unprocessed_messages
        }
    except Exception as e:
        print(f"❌ Error getting status summary: {str(e)}")
        return None

def reset_clustering_status():
    """Reset processed_for_clustering to False for all messages"""
    try:
        print("🔄 Resetting clustering status for all messages...")
        
        # Perform bulk update
        result = Message.objects.update(processed_for_clustering=False)
        
        print(f"✅ Successfully updated {result} message documents")
        return result
        
    except Exception as e:
        print(f"❌ Error resetting clustering status: {str(e)}")
        return 0

def main():
    """Main function to execute the reset operation"""
    print("=" * 60)
    print("🔄 Message Clustering Status Reset Script")
    print("=" * 60)
    
    # Connect to database
    if not connect_to_database():
        sys.exit(1)
    
    try:
        # Get current status
        print("\n📊 Current Status:")
        status = get_clustering_status_summary()
        if status:
            print(f"   Total messages: {status['total']}")
            print(f"   Processed for clustering: {status['processed']}")
            print(f"   Unprocessed: {status['unprocessed']}")
        else:
            print("   Unable to get current status")
        
        # Confirm operation
        if status and status['total'] == 0:
            print("\n⚠️  No messages found in database. Nothing to reset.")
            return
        
        print(f"\n⚠️  This will reset the 'processed_for_clustering' field to False")
        print(f"   for ALL {status['total'] if status else 'existing'} message documents.")
        
        confirm = input("\n❓ Do you want to continue? (y/N): ").strip().lower()
        
        if confirm not in ['y', 'yes']:
            print("❌ Operation cancelled by user")
            return
        
        # Perform the reset
        updated_count = reset_clustering_status()
        
        if updated_count > 0:
            print(f"\n✅ Reset complete!")
            print(f"   Updated {updated_count} message documents")
            print(f"   All messages are now marked as unprocessed for clustering")
        else:
            print(f"\n⚠️  No documents were updated")
        
        # Show final status
        print("\n📊 Final Status:")
        final_status = get_clustering_status_summary()
        if final_status:
            print(f"   Total messages: {final_status['total']}")
            print(f"   Processed for clustering: {final_status['processed']}")
            print(f"   Unprocessed: {final_status['unprocessed']}")
        
    except KeyboardInterrupt:
        print("\n❌ Operation interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
    finally:
        # Disconnect from database
        disconnect()
        print("\n🔌 Disconnected from database")

if __name__ == "__main__":
    main()
