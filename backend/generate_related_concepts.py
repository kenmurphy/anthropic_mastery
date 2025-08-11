#!/usr/bin/env python3
"""
Generate related concepts for existing courses that don't have them.
This is a migration script to backfill related concepts for existing courses.

Usage:
    python generate_related_concepts.py
"""

import sys
import os
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialize MongoDB connection
from mongoengine import connect
from config import Config

# Connect to MongoDB
connect(
    db=Config.MONGODB_DB,
    host=Config.MONGODB_HOST,
    port=Config.MONGODB_PORT,
    username=Config.MONGODB_USERNAME,
    password=Config.MONGODB_PASSWORD,
    alias='default'
)

from models.course import Course, CourseConcept
from services.anthropic_service import AnthropicService
from services.study_guide_service import StudyGuideService

def find_courses_needing_related_concepts():
    """Find courses that have no related concepts or could use more"""
    try:
        all_courses = Course.objects.all()
        courses_to_process = []
        
        for course in all_courses:
            related_count = len([c for c in course.concepts if c.type == 'related'])
            original_count = len([c for c in course.concepts if c.type == 'original'])
            
            # Process all courses as requested - add more related concepts with deduplication
            courses_to_process.append({
                'course': course,
                'original_count': original_count,
                'related_count': related_count
            })
        
        return courses_to_process
    except Exception as e:
        print(f"Error finding courses: {e}")
        return []

def generate_and_add_related_concepts(course_info):
    """Generate related concepts and add to course with deduplication"""
    course = course_info['course']
    
    try:
        print(f"\nProcessing course: {course.label}")
        print(f"  Current concepts: {course_info['original_count']} original, {course_info['related_count']} related")
        
        # Get existing concept titles for AI context
        existing_titles = [concept.title for concept in course.concepts]
        
        # Generate new related concepts using Anthropic API
        anthropic_service = AnthropicService()
        new_concept_data = anthropic_service.generate_adjacent_concepts(
            existing_concepts=existing_titles,
            course_description=course.description
        )
        
        # Create new related concepts
        new_related_concepts = [
            CourseConcept(
                title=concept_data['title'],
                difficulty_level=concept_data['difficulty_level'],
                status='not_started',
                type='related'
            ) for concept_data in new_concept_data
        ]
        
        print(f"  Generated {len(new_related_concepts)} new related concepts")
        
        # Combine existing concepts with new ones
        all_concepts = list(course.concepts) + new_related_concepts
        
        # Apply deduplication (existing concepts come first, so they take priority)
        deduplicated_concepts = StudyGuideService._deduplicate_concepts_by_title(all_concepts)
        
        # Calculate how many new concepts were actually added
        concepts_added = len(deduplicated_concepts) - len(course.concepts)
        
        # Update course with deduplicated concepts
        course.concepts = deduplicated_concepts
        course.save()
        
        print(f"  ✅ Added {concepts_added} new unique related concepts")
        print(f"  Final count: {len([c for c in course.concepts if c.type == 'original'])} original, {len([c for c in course.concepts if c.type == 'related'])} related")
        
        return {
            'success': True,
            'concepts_generated': len(new_related_concepts),
            'concepts_added': concepts_added,
            'total_concepts': len(course.concepts)
        }
        
    except Exception as e:
        error_msg = f"Failed to generate concepts for course '{course.label}': {str(e)}"
        print(f"  ❌ {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }

def main():
    """Main function to process all courses"""
    print("🚀 Starting related concepts generation for existing courses...")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Find courses that need processing
    courses_to_process = find_courses_needing_related_concepts()
    
    if not courses_to_process:
        print("No courses found to process.")
        return
    
    print(f"\nFound {len(courses_to_process)} courses to process")
    
    # Process each course
    results = {
        'total_processed': 0,
        'successful': 0,
        'failed': 0,
        'total_concepts_generated': 0,
        'total_concepts_added': 0,
        'failures': []
    }
    
    for i, course_info in enumerate(courses_to_process, 1):
        print(f"\n[{i}/{len(courses_to_process)}]", end=" ")
        
        result = generate_and_add_related_concepts(course_info)
        results['total_processed'] += 1
        
        if result['success']:
            results['successful'] += 1
            results['total_concepts_generated'] += result['concepts_generated']
            results['total_concepts_added'] += result['concepts_added']
        else:
            results['failed'] += 1
            results['failures'].append(result['error'])
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 MIGRATION SUMMARY")
    print(f"{'='*60}")
    print(f"Total courses processed: {results['total_processed']}")
    print(f"Successful: {results['successful']}")
    print(f"Failed: {results['failed']}")
    print(f"Total concepts generated: {results['total_concepts_generated']}")
    print(f"Total concepts added (after deduplication): {results['total_concepts_added']}")
    
    if results['failures']:
        print(f"\n❌ FAILURES ({len(results['failures'])}):")
        for failure in results['failures']:
            print(f"  - {failure}")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("✅ Migration completed!")

if __name__ == "__main__":
    main()
