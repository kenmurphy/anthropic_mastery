#!/usr/bin/env python3
"""
Test script to verify CourseConcept deduplication is working properly.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.course import CourseConcept
from services.study_guide_service import StudyGuideService

def test_deduplication():
    """Test the deduplication functionality"""
    print("🧪 Testing CourseConcept deduplication...")
    
    # Create test concepts with duplicates (case-insensitive)
    test_concepts = [
        CourseConcept(title="React Hooks", difficulty_level="medium", status="not_started", type="original"),
        CourseConcept(title="State Management", difficulty_level="advanced", status="not_started", type="original"),
        CourseConcept(title="react hooks", difficulty_level="beginner", status="not_started", type="related"),  # Duplicate (different case)
        CourseConcept(title="Component Lifecycle", difficulty_level="medium", status="not_started", type="related"),
        CourseConcept(title="State Management", difficulty_level="medium", status="not_started", type="related"),  # Exact duplicate
        CourseConcept(title="REACT HOOKS", difficulty_level="advanced", status="not_started", type="related"),  # Duplicate (different case)
        CourseConcept(title="Props and State", difficulty_level="beginner", status="not_started", type="related"),
    ]
    
    print(f"Original concepts count: {len(test_concepts)}")
    print("Original concepts:")
    for i, concept in enumerate(test_concepts, 1):
        print(f"  {i}. {concept.title} ({concept.type}, {concept.difficulty_level})")
    
    # Apply deduplication
    deduplicated = StudyGuideService._deduplicate_concepts_by_title(test_concepts)
    
    print(f"\nDeduplicated concepts count: {len(deduplicated)}")
    print("Deduplicated concepts (first occurrence kept):")
    for i, concept in enumerate(deduplicated, 1):
        print(f"  {i}. {concept.title} ({concept.type}, {concept.difficulty_level})")
    
    # Verify results
    expected_titles = ["React Hooks", "State Management", "Component Lifecycle", "Props and State"]
    actual_titles = [concept.title for concept in deduplicated]
    
    print(f"\nExpected unique titles: {expected_titles}")
    print(f"Actual unique titles: {actual_titles}")
    
    # Check that original concepts are preserved when duplicates exist
    react_hooks_concept = next((c for c in deduplicated if c.title.lower() == "react hooks"), None)
    state_mgmt_concept = next((c for c in deduplicated if c.title == "State Management"), None)
    
    success = True
    if react_hooks_concept and react_hooks_concept.type == "original":
        print("✅ Original 'React Hooks' concept preserved over related duplicates")
    else:
        print("❌ Original 'React Hooks' concept not preserved")
        success = False
    
    if state_mgmt_concept and state_mgmt_concept.type == "original":
        print("✅ Original 'State Management' concept preserved over related duplicates")
    else:
        print("❌ Original 'State Management' concept not preserved")
        success = False
    
    if len(deduplicated) == 4:
        print("✅ Correct number of unique concepts after deduplication")
    else:
        print(f"❌ Expected 4 unique concepts, got {len(deduplicated)}")
        success = False
    
    if success:
        print("\n🎉 All deduplication tests passed!")
    else:
        print("\n❌ Some deduplication tests failed!")
    
    return success

if __name__ == "__main__":
    test_deduplication()
