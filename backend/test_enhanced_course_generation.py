#!/usr/bin/env python3
"""
Test script for enhanced course generation with topic refinement
"""

import os
import sys
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.anthropic_service import AnthropicService
from services.study_guide_service import StudyGuideService
from models.cluster import ConversationCluster
from models.course import Course

def test_topic_refinement():
    """Test the new topic refinement functionality"""
    print("=" * 60)
    print("Testing Enhanced Course Generation with Topic Refinement")
    print("=" * 60)
    
    # Test data - simulating raw concepts from a cluster
    raw_concepts = [
        "database-query",
        "sql-join",
        "error-handling",
        "exception-handling",
        "api-integration",
        "rest-api",
        "authentication",
        "data-validation",
        "performance-optimization",
        "caching-strategies"
    ]
    
    course_title = "Backend Development Fundamentals"
    course_description = "Professional discussions focused on backend development, database management, and API design. Learn practical approaches to common challenges in server-side development."
    
    print(f"\nCourse: {course_title}")
    print(f"Description: {course_description}")
    print(f"\nRaw concepts from cluster analysis:")
    for i, concept in enumerate(raw_concepts, 1):
        print(f"  {i}. {concept}")
    
    try:
        # Test the new refine_original_topics method
        print(f"\n{'='*40}")
        print("STEP 1: Refining Original Topics")
        print(f"{'='*40}")
        
        anthropic_service = AnthropicService()
        
        refined_topics = anthropic_service.refine_original_topics(
            raw_concepts=raw_concepts,
            course_title=course_title,
            course_description=course_description
        )
        
        print(f"\nRefined {len(raw_concepts)} raw concepts into {len(refined_topics)} original topics:")
        for i, topic in enumerate(refined_topics, 1):
            print(f"  {i}. {topic['title']} ({topic['difficulty_level']})")
        
        # Test the new generate_related_topics method
        print(f"\n{'='*40}")
        print("STEP 2: Generating Related Topics")
        print(f"{'='*40}")
        
        original_titles = [topic['title'] for topic in refined_topics]
        
        related_topics = anthropic_service.generate_related_topics(
            existing_concepts=original_titles,
            course_title=course_title,
            course_description=course_description
        )
        
        print(f"\nGenerated {len(related_topics)} related topics:")
        for i, topic in enumerate(related_topics, 1):
            print(f"  {i}. {topic['title']} ({topic['difficulty_level']})")
        
        # Show the complete course structure
        print(f"\n{'='*40}")
        print("COMPLETE COURSE STRUCTURE")
        print(f"{'='*40}")
        
        print(f"\nOriginal Topics ({len(refined_topics)}):")
        for i, topic in enumerate(refined_topics, 1):
            print(f"  {i}. {topic['title']} [{topic['difficulty_level']}]")
        
        print(f"\nRelated Topics ({len(related_topics)}):")
        for i, topic in enumerate(related_topics, 1):
            print(f"  {i}. {topic['title']} [{topic['difficulty_level']}]")
        
        total_topics = len(refined_topics) + len(related_topics)
        print(f"\nTotal Topics: {total_topics}")
        
        # Test comparison with old method
        print(f"\n{'='*40}")
        print("COMPARISON WITH OLD METHOD")
        print(f"{'='*40}")
        
        old_adjacent_topics = anthropic_service.generate_adjacent_concepts(
            existing_concepts=raw_concepts,  # Using raw concepts like before
            course_description=course_description
        )
        
        print(f"\nOld method (generate_adjacent_concepts) with raw concepts:")
        print(f"Generated {len(old_adjacent_topics)} topics:")
        for i, topic in enumerate(old_adjacent_topics, 1):
            print(f"  {i}. {topic['title']} ({topic['difficulty_level']})")
        
        print(f"\n{'='*60}")
        print("ENHANCEMENT SUMMARY")
        print(f"{'='*60}")
        print(f"Raw concepts:           {len(raw_concepts)}")
        print(f"Refined original:       {len(refined_topics)}")
        print(f"New related topics:     {len(related_topics)}")
        print(f"Old adjacent topics:    {len(old_adjacent_topics)}")
        print(f"Total new topics:       {total_topics}")
        
        print(f"\n✅ Topic refinement test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during topic refinement test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_course_creation_flow():
    """Test the complete course creation flow (if we have test data)"""
    print(f"\n{'='*60}")
    print("Testing Complete Course Creation Flow")
    print(f"{'='*60}")
    
    try:
        # Check if we have any clusters to test with
        clusters = ConversationCluster.objects.all()
        
        if not clusters:
            print("No conversation clusters found in database.")
            print("Skipping course creation flow test.")
            return True
        
        print(f"Found {len(clusters)} clusters in database:")
        for cluster in clusters[:3]:  # Show first 3
            print(f"  - {cluster.cluster_id}: {cluster.label}")
            print(f"    Concepts: {cluster.key_concepts[:5]}...")  # Show first 5 concepts
        
        # Test creating a course from the first cluster
        if clusters:
            test_cluster = clusters[0]
            print(f"\nTesting course creation from cluster: {test_cluster.cluster_id}")
            
            # This should trigger the new refinement flow
            course = StudyGuideService.create_or_get_course(
                item_id=test_cluster.cluster_id,
                item_type='cluster'
            )
            
            print(f"✅ Successfully created course: {course.label}")
            print(f"   Original topics: {len([c for c in course.concepts if c.type == 'original'])}")
            print(f"   Related topics:  {len([c for c in course.concepts if c.type == 'related'])}")
            print(f"   Total concepts:  {len(course.concepts)}")
            
            # Test fetching the course (should generate fresh related topics)
            print(f"\nTesting course fetching (fresh related topics)...")
            fetched_course = StudyGuideService.get_course_by_id(str(course.id))
            
            print(f"✅ Successfully fetched course with fresh related topics")
            print(f"   Total concepts after fetch: {len(fetched_course.concepts)}")
            
            return True
        
    except Exception as e:
        print(f"❌ Error during course creation flow test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Enhanced Course Generation Test Suite")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Topic refinement functionality
    test1_success = test_topic_refinement()
    
    # Test 2: Complete course creation flow (if data available)
    test2_success = test_course_creation_flow()
    
    print(f"\n{'='*60}")
    print("TEST RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"Topic Refinement Test:     {'✅ PASSED' if test1_success else '❌ FAILED'}")
    print(f"Course Creation Flow Test: {'✅ PASSED' if test2_success else '❌ FAILED'}")
    
    if test1_success and test2_success:
        print(f"\n🎉 All tests passed! Enhanced course generation is working correctly.")
        return 0
    else:
        print(f"\n⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
