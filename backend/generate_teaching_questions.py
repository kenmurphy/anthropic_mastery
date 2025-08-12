#!/usr/bin/env python3
"""
Script to generate teaching questions for all concepts with status "reviewing"

This script:
1. Connects to MongoDB
2. Finds all courses with concepts that have status "reviewing"
3. Generates teaching questions for concepts that don't have them or need updates
4. Updates the database with the generated questions

Usage:
    python generate_teaching_questions.py [--force] [--course-id COURSE_ID]
    
Options:
    --force: Force regeneration of questions even if they already exist
    --course-id: Only process a specific course ID
"""

import os
import sys
import argparse
from datetime import datetime
from mongoengine import connect, disconnect
from models.course import Course, CourseConcept
from services.anthropic_service import AnthropicService

def setup_database():
    """Setup MongoDB connection"""
    try:
        # Get MongoDB configuration from environment
        mongodb_host = os.getenv('MONGODB_HOST', 'localhost')
        mongodb_port = int(os.getenv('MONGODB_PORT', 27017))
        mongodb_db = os.getenv('MONGODB_DB', 'claude_db')
        mongodb_username = os.getenv('MONGODB_USERNAME', 'mastery_user')
        mongodb_password = os.getenv('MONGODB_PASSWORD', 'mastery_password')
        
        # Connect to MongoDB
        connect(
            db=mongodb_db,
            host=mongodb_host,
            port=mongodb_port,
            username=mongodb_username,
            password=mongodb_password,
            authentication_source='admin'
        )
        print(f"✅ Connected to MongoDB: {mongodb_host}:{mongodb_port}/{mongodb_db}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return False

def find_concepts_needing_questions(course_id=None, force=False):
    """
    Find all concepts with status "reviewing" that need teaching questions
    
    Args:
        course_id: Optional specific course ID to process
        force: If True, regenerate questions even if they exist
        
    Returns:
        List of tuples: (course, concept)
    """
    concepts_to_process = []
    
    try:
        # Query courses
        if course_id:
            courses = Course.objects(id=course_id)
            if not courses:
                print(f"❌ Course with ID {course_id} not found")
                return []
        else:
            courses = Course.objects()
        
        print(f"🔍 Scanning {len(courses)} course(s) for concepts needing teaching questions...")
        
        for course in courses:
            reviewing_concepts = [c for c in course.concepts if c.status == 'reviewing']
            
            if not reviewing_concepts:
                continue
                
            print(f"\n📚 Course: {course.label}")
            print(f"   Found {len(reviewing_concepts)} concept(s) with 'reviewing' status")
            
            for concept in reviewing_concepts:
                needs_questions = force or concept.should_generate_questions()
                
                if needs_questions:
                    concepts_to_process.append((course, concept))
                    status = "🔄 Needs questions" if not concept.teaching_questions else "🔄 Questions outdated"
                    print(f"   - {concept.title} ({concept.difficulty_level}) - {status}")
                else:
                    print(f"   - {concept.title} ({concept.difficulty_level}) - ✅ Questions up to date")
        
        print(f"\n📊 Summary: {len(concepts_to_process)} concept(s) need teaching questions generated")
        return concepts_to_process
        
    except Exception as e:
        print(f"❌ Error finding concepts: {e}")
        return []

def generate_questions_for_concept(anthropic_service, course, concept):
    """
    Generate teaching questions for a specific concept
    
    Args:
        anthropic_service: AnthropicService instance
        course: Course object
        concept: CourseConcept object
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"🤖 Generating teaching questions for: {concept.title}")
        
        # Set streaming flag to prevent concurrent generation
        concept.is_streaming_questions = True
        course.save()
        
        # Generate questions using the concept's summary if available
        summary = concept.summary if concept.has_summary() else ""
        questions = anthropic_service.generate_teaching_questions(
            concept_title=concept.title,
            summary=summary
        )
        
        if questions:
            # Update the concept with generated questions
            concept.set_teaching_questions(questions)
            concept.is_streaming_questions = False
            course.save()
            
            print(f"   ✅ Generated {len(questions)} question(s)")
            for i, question in enumerate(questions, 1):
                print(f"      {i}. {question}")
            
            return True
        else:
            print(f"   ❌ No questions generated")
            concept.is_streaming_questions = False
            course.save()
            return False
            
    except Exception as e:
        print(f"   ❌ Error generating questions: {e}")
        # Reset streaming flag on error
        try:
            concept.is_streaming_questions = False
            course.save()
        except:
            pass
        return False

def main():
    """Main script execution"""
    parser = argparse.ArgumentParser(
        description="Generate teaching questions for concepts with 'reviewing' status"
    )
    parser.add_argument(
        '--force', 
        action='store_true',
        help='Force regeneration of questions even if they already exist'
    )
    parser.add_argument(
        '--course-id',
        type=str,
        help='Only process a specific course ID'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be processed without making changes'
    )
    
    args = parser.parse_args()
    
    print("🚀 Teaching Questions Generation Script")
    print("=" * 50)
    
    # Setup database connection
    if not setup_database():
        sys.exit(1)
    
    try:
        # Initialize Anthropic service
        print("🤖 Initializing Anthropic service...")
        anthropic_service = AnthropicService()
        print("✅ Anthropic service ready")
        
        # Find concepts that need questions
        concepts_to_process = find_concepts_needing_questions(
            course_id=args.course_id,
            force=args.force
        )
        
        if not concepts_to_process:
            print("\n🎉 No concepts need teaching questions generated!")
            return
        
        if args.dry_run:
            print(f"\n🔍 DRY RUN: Would process {len(concepts_to_process)} concept(s)")
            return
        
        # Process each concept
        print(f"\n🔄 Processing {len(concepts_to_process)} concept(s)...")
        print("-" * 50)
        
        successful = 0
        failed = 0
        
        for i, (course, concept) in enumerate(concepts_to_process, 1):
            print(f"\n[{i}/{len(concepts_to_process)}] Course: {course.label}")
            
            if generate_questions_for_concept(anthropic_service, course, concept):
                successful += 1
            else:
                failed += 1
        
        # Final summary
        print("\n" + "=" * 50)
        print("📊 FINAL SUMMARY")
        print(f"✅ Successfully processed: {successful} concept(s)")
        print(f"❌ Failed to process: {failed} concept(s)")
        print(f"📝 Total concepts processed: {len(concepts_to_process)}")
        
        if successful > 0:
            print(f"\n🎉 Teaching questions have been generated and saved to the database!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Script interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
    finally:
        # Cleanup database connection
        try:
            disconnect()
            print("\n🔌 Database connection closed")
        except:
            pass

if __name__ == "__main__":
    main()
