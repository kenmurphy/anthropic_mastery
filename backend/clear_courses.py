#!/usr/bin/env python3
"""
Clear Courses Script

This script deletes all courses from the database while leaving other data intact.
Use this to clean up duplicate courses or reset the course system.

Usage:
    python clear_courses.py
"""

import os
import sys
from mongoengine import connect, disconnect
from models.course import Course

def clear_courses():
    """Delete all courses from the database"""
    try:
        # Connect to MongoDB using the same config as the main app
        from config import Config
        
        # Initialize configuration
        config = Config()
        
        # Connect to MongoDB
        connect(
            db=config.MONGODB_DB,
            host=config.MONGODB_URI,
            alias='default'
        )
        
        print("Connected to MongoDB")
        
        # Count existing courses
        course_count = Course.objects.count()
        print(f"Found {course_count} courses in the database")
        
        if course_count == 0:
            print("No courses to delete")
            return
        
        # Confirm deletion
        response = input(f"Are you sure you want to delete all {course_count} courses? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Operation cancelled")
            return
        
        # Delete all courses
        result = Course.objects.all().delete()
        print(f"Successfully deleted {result} courses")
        
        # Verify deletion
        remaining_count = Course.objects.count()
        if remaining_count == 0:
            print("✅ All courses have been successfully deleted")
        else:
            print(f"⚠️  Warning: {remaining_count} courses still remain")
        
    except Exception as e:
        print(f"❌ Error clearing courses: {e}")
        sys.exit(1)
    finally:
        # Disconnect from MongoDB
        disconnect()
        print("Disconnected from MongoDB")

if __name__ == "__main__":
    print("🗑️  Course Cleanup Script")
    print("=" * 40)
    clear_courses()
    print("=" * 40)
    print("✨ Course cleanup complete")
