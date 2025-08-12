from models.cluster import ConversationCluster
from models.course import Course, CourseConcept
from services.anthropic_service import AnthropicService

class StudyGuideService:
    """Service for managing unified study guides (courses + available clusters)"""
    
    @staticmethod
    def _deduplicate_concepts_by_title(concepts):
        """Remove duplicate concepts by title (case-insensitive), keeping first occurrence
        
        IMPORTANT: This preserves the full concept object (including status, summary, etc.)
        from the first occurrence, which is critical for maintaining user selections.
        """
        seen_titles = set()
        deduplicated = []
        for concept in concepts:
            title_lower = concept.title.lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                deduplicated.append(concept)  # Preserves full concept object
        return deduplicated
    
    @staticmethod
    def get_study_guides():
        """Get unified list of study guides (courses + available clusters)"""
        try:
            # Get all courses
            courses = Course.objects.all()
            course_study_guides = [course.to_study_guide_dict() for course in courses]
            
            # Get clusters that don't have associated courses
            course_cluster_ids = [course.source_cluster_id for course in courses]
            available_clusters = ConversationCluster.objects(cluster_id__nin=course_cluster_ids)
            cluster_study_guides = [cluster.to_study_guide_dict() for cluster in available_clusters]
            
            # Combine and sort by creation date (newest first)
            all_study_guides = course_study_guides + cluster_study_guides
            all_study_guides.sort(key=lambda x: x.get('created_at') or '', reverse=True)
            
            return all_study_guides
            
        except Exception as e:
            print(f"Error getting study guides: {e}")
            return []
    
    @staticmethod
    def create_or_get_course(item_id, item_type):
        """Create course from cluster or get existing course"""
        try:
            if item_type == 'course':
                # Already a course, just return it
                course = Course.objects(id=item_id).first()
                if not course:
                    raise ValueError("Course not found")
                return course
            
            elif item_type == 'cluster':
                # Create new course from cluster
                cluster = ConversationCluster.objects(cluster_id=item_id).first()
                if not cluster:
                    raise ValueError("Cluster not found")
                
                # Check if course already exists (shouldn't happen with filtering, but safety check)
                existing_course = Course.objects(source_cluster_id=item_id).first()
                if existing_course:
                    return existing_course
                
                anthropic_service = AnthropicService()
                
                # Step 1: Refine original topics from raw cluster concepts
                try:
                    refined_original_data = anthropic_service.refine_original_topics(
                        raw_concepts=cluster.key_concepts,
                        course_title=cluster.label,
                        course_description=cluster.description
                    )
                    
                    # Create refined original concepts
                    original_concepts = [
                        CourseConcept(
                            title=concept_data['title'],
                            difficulty_level=concept_data['difficulty_level'],
                            status='not_started',
                            type='original'
                        ) for concept_data in refined_original_data
                    ]
                    
                    print(f"Refined {len(cluster.key_concepts)} raw concepts into {len(original_concepts)} original topics for course: {cluster.label}")
                    
                except Exception as e:
                    print(f"Error refining original topics: {e}")
                    # Fallback: use raw concepts with default formatting
                    original_concepts = [
                        CourseConcept(
                            title=concept.replace('-', ' ').title(),
                            difficulty_level='medium',
                            status='not_started',
                            type='original'
                        ) for concept in cluster.key_concepts
                    ]
                
                # Deduplicate original concepts (in case refinement has duplicates)
                original_concepts = StudyGuideService._deduplicate_concepts_by_title(original_concepts)
                
                # Create new course with only original concepts
                # Related topics will be generated asynchronously by the frontend
                course = Course(
                    label=cluster.label,
                    description=cluster.description,
                    conversation_ids=cluster.conversation_ids,
                    source_cluster_id=item_id,
                    concepts=original_concepts
                )
                course.save()
                return course
            
            else:
                raise ValueError("Invalid item type. Must be 'course' or 'cluster'")
                
        except Exception as e:
            print(f"Error creating or getting course: {e}")
            raise e
    
    @staticmethod
    def get_course_by_id(course_id):
        """Get course by ID immediately without generating related topics"""
        try:
            course = Course.objects(id=course_id).first()
            if not course:
                raise ValueError("Course not found")
            
            return course
        except Exception as e:
            print(f"Error getting course by ID: {e}")
            raise e
    
    @staticmethod
    def generate_fresh_related_topics(course_id):
        """Generate fresh related topics for a course asynchronously"""
        try:
            course = Course.objects(id=course_id).first()
            if not course:
                raise ValueError("Course not found")
            
            anthropic_service = AnthropicService()
            
            # Get current original topics (type='original')
            original_topics = [concept.title for concept in course.concepts if concept.type == 'original']
            
            if not original_topics:
                return course  # No original topics to base related topics on
            
            # Generate fresh related topics
            fresh_related_data = anthropic_service.generate_related_topics(
                existing_concepts=original_topics,
                course_title=course.label,
                course_description=course.description
            )
            
            # Create fresh related concepts - explicitly set all required fields
            fresh_related_concepts = []
            for concept_data in fresh_related_data:
                fresh_related_concepts.append(CourseConcept(
                    title=str(concept_data.get('title', 'Unknown Topic'))[:200],
                    difficulty_level=str(concept_data.get('difficulty_level', 'medium')),
                    status='not_started',  # Explicitly set status
                    type='related'  # Explicitly set type
                ))
            
            # Replace existing related topics with fresh ones
            # Keep original topics WITH THEIR CURRENT STATUS, replace related topics
            original_concepts = [concept for concept in course.concepts if concept.type == 'original']
            all_concepts = original_concepts + fresh_related_concepts
            
            # Apply deduplication
            deduplicated_concepts = StudyGuideService._deduplicate_concepts_by_title(all_concepts)
            
            # Update course with fresh related topics
            course.concepts = deduplicated_concepts
            course.save()
            
            print(f"Generated {len(fresh_related_concepts)} fresh related topics for course: {course.label}")
            
            return course
        except Exception as e:
            print(f"Error generating fresh related topics for course {course_id}: {e}")
            raise e
    
    @staticmethod
    def update_concept_status(course_id, concept_title, new_status):
        """Update the status of a specific concept in a course"""
        try:
            course = Course.objects(id=course_id).first()
            if not course:
                raise ValueError("Course not found")
            
            # Validate status
            valid_statuses = ['not_started', 'reviewing']
            if new_status not in valid_statuses:
                raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
            
            # Update concept status
            success = course.update_concept_status(concept_title, new_status)
            if not success:
                raise ValueError("Concept not found in course")
            
            return course
            
        except Exception as e:
            print(f"Error updating concept status: {e}")
            raise e
    
    @staticmethod
    def get_all_courses():
        """Get all courses"""
        try:
            courses = Course.objects.all()
            return [course.to_dict() for course in courses]
        except Exception as e:
            print(f"Error getting all courses: {e}")
            return []
    
    @staticmethod
    def start_course_review(course_id, selected_concept_titles):
        """Start review process for selected concepts in a course"""
        try:
            course = Course.objects(id=course_id).first()
            if not course:
                raise ValueError("Course not found")
            
            # Validate that course is in explore stage
            if course.current_stage != 'explore':
                raise ValueError("Course must be in 'explore' stage to start review")
            
            # Validate that selected concepts exist and are not_started
            valid_concepts = []
            for title in selected_concept_titles:
                concept = course.get_concept_by_title(title)
                if not concept:
                    raise ValueError(f"Concept '{title}' not found in course")
                if concept.status != 'not_started':
                    raise ValueError(f"Concept '{title}' is not available for selection (status: {concept.status})")
                valid_concepts.append(concept)
            
            # Start the review process
            success = course.start_review(selected_concept_titles)
            if not success:
                raise ValueError("Failed to start review process")
            
            return course
            
        except Exception as e:
            print(f"Error starting course review: {e}")
            raise e

    @staticmethod
    def delete_course(course_id):
        """Delete a course by ID"""
        try:
            course = Course.objects(id=course_id).first()
            if not course:
                raise ValueError("Course not found")
            
            course.delete()
            return True
            
        except Exception as e:
            print(f"Error deleting course: {e}")
            raise e
