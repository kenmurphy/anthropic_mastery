#!/usr/bin/env python3
"""
Script to create unique index on source_cluster_id field in courses collection.
This prevents multiple courses from being created from the same cluster.
"""

import os
import sys
from mongoengine import connect
from models.course import Course

def create_unique_index():
    """Create unique index on source_cluster_id field"""
    try:
        # Connect to MongoDB using the same configuration as the main app
        from config import Config
        config = Config()
        
        # Connect to MongoDB
        connect(
            db=config.MONGODB_DB,
            host=config.MONGODB_URI,
            alias='default'
        )
        
        print("Connected to MongoDB")
        
        # Get the courses collection
        collection = Course._get_collection()
        
        # Check if unique index already exists
        existing_indexes = list(collection.list_indexes())
        has_unique_index = False
        needs_recreation = False
        
        for index in existing_indexes:
            if 'source_cluster_id' in index.get('key', {}):
                if index.get('unique', False):
                    has_unique_index = True
                    print("Unique index on source_cluster_id already exists")
                    break
                else:
                    # Drop non-unique index if it exists
                    print("Found existing non-unique index on source_cluster_id")
                    print(f"Index name: {index.get('name')}")
                    needs_recreation = True
        
        if needs_recreation:
            # Drop the existing non-unique index by name
            print("Dropping existing non-unique index...")
            collection.drop_index("source_cluster_id_1")
            print("Existing index dropped")
        
        if not has_unique_index:
            # Create unique index with explicit name
            print("Creating unique index on source_cluster_id...")
            collection.create_index(
                [('source_cluster_id', 1)], 
                unique=True, 
                name="source_cluster_id_unique"
            )
            print("✅ Unique index created successfully")
        
        # Verify the index was created
        indexes = list(collection.list_indexes())
        for index in indexes:
            if 'source_cluster_id' in index.get('key', {}):
                print(f"Index details: {index}")
        
        print("✅ Index creation completed")
        
    except Exception as e:
        print(f"❌ Error creating unique index: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_unique_index()
