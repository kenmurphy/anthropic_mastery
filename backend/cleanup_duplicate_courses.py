#!/usr/bin/env python3
"""
Script to clean up duplicate courses and apply unique index.
"""

import pymongo
from pymongo.errors import OperationFailure, DuplicateKeyError
from config import Config

def cleanup_and_apply_index():
    """Clean up duplicate courses and apply unique index"""
    try:
        config = Config()
        
        # Connect directly with pymongo
        client = pymongo.MongoClient(config.MONGODB_URI)
        db = client[config.MONGODB_DB]
        collection = db.courses
        
        print("Connected to MongoDB")
        
        # Find duplicate source_cluster_id values
        pipeline = [
            {"$group": {"_id": "$source_cluster_id", "docs": {"$push": "$$ROOT"}, "count": {"$sum": 1}}},
            {"$match": {"count": {"$gt": 1}}}
        ]
        duplicates = list(collection.aggregate(pipeline))
        
        if duplicates:
            print(f"Found {len(duplicates)} duplicate cluster IDs")
            
            for dup_group in duplicates:
                cluster_id = dup_group['_id']
                docs = dup_group['docs']
                count = dup_group['count']
                
                print(f"\nProcessing cluster_id: {cluster_id} ({count} duplicates)")
                
                # Sort by created_at to keep the oldest one
                docs.sort(key=lambda x: x.get('created_at', ''))
                
                # Keep the first (oldest) document, delete the rest
                keep_doc = docs[0]
                delete_docs = docs[1:]
                
                print(f"  Keeping course: {keep_doc['_id']} (created: {keep_doc.get('created_at', 'unknown')})")
                
                for doc in delete_docs:
                    print(f"  Deleting course: {doc['_id']} (created: {doc.get('created_at', 'unknown')})")
                    collection.delete_one({"_id": doc["_id"]})
                
                print(f"  Cleaned up {len(delete_docs)} duplicate courses for cluster {cluster_id}")
        else:
            print("No duplicate courses found")
        
        # Now apply the unique index
        print("\nApplying unique index...")
        try:
            collection.create_index(
                [("source_cluster_id", 1)], 
                unique=True, 
                name="source_cluster_id_unique"
            )
            print("✅ Created unique index on source_cluster_id")
        except OperationFailure as e:
            if "already exists" in str(e).lower():
                print("✅ Unique index already exists")
            else:
                print(f"❌ Error creating index: {e}")
        
        # Verify the index
        indexes = list(collection.list_indexes())
        for index in indexes:
            if 'source_cluster_id' in index.get('key', {}):
                unique_status = "UNIQUE" if index.get('unique', False) else "NON-UNIQUE"
                print(f"Index: {index.get('name')} - {unique_status}")
        
        client.close()
        print("✅ Cleanup and index operation completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    cleanup_and_apply_index()
