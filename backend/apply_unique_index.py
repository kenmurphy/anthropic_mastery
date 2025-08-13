#!/usr/bin/env python3
"""
Simple script to apply unique index on source_cluster_id field.
"""

import pymongo
from pymongo.errors import OperationFailure, DuplicateKeyError
from config import Config

def apply_unique_index():
    """Apply unique index directly using pymongo"""
    try:
        config = Config()
        
        # Connect directly with pymongo
        client = pymongo.MongoClient(config.MONGODB_URI)
        db = client[config.MONGODB_DB]
        collection = db.courses
        
        print("Connected to MongoDB")
        
        # First, drop the existing non-unique index if it exists
        try:
            collection.drop_index("source_cluster_id_1")
            print("Dropped existing non-unique index")
        except OperationFailure as e:
            if "index not found" in str(e).lower():
                print("No existing index to drop")
            else:
                print(f"Error dropping index: {e}")
        
        # Create the unique index
        try:
            collection.create_index(
                [("source_cluster_id", 1)], 
                unique=True, 
                name="source_cluster_id_unique"
            )
            print("✅ Created unique index on source_cluster_id")
        except DuplicateKeyError:
            print("❌ Cannot create unique index - duplicate values exist in source_cluster_id")
            # Show duplicate values
            pipeline = [
                {"$group": {"_id": "$source_cluster_id", "count": {"$sum": 1}}},
                {"$match": {"count": {"$gt": 1}}}
            ]
            duplicates = list(collection.aggregate(pipeline))
            if duplicates:
                print("Duplicate source_cluster_id values found:")
                for dup in duplicates:
                    print(f"  - {dup['_id']}: {dup['count']} courses")
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
        print("✅ Index operation completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    apply_unique_index()
