from models.cluster import ConversationCluster
from models.course import Course, CourseConcept

class StudyGuideService:
    """Service for managing unified study guides (courses + available clusters)"""
    
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
                
                # Create new course
                course = Course(
                    label=cluster.label,
                    description=cluster.description,
                    conversation_ids=cluster.conversation_ids,
                    source_cluster_id=item_id,
                    concepts=[
                        CourseConcept(
                            title=concept,
                            difficulty_level='medium',
                            status='not_started'
                        ) for concept in cluster.key_concepts
                    ]
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
        """Get course by ID"""
        try:
            course = Course.objects(id=course_id).first()
            if not course:
                raise ValueError("Course not found")
            return course
        except Exception as e:
            print(f"Error getting course by ID: {e}")
            raise e
    
    @staticmethod
    def update_concept_status(course_id, concept_title, new_status):
        """Update the status of a specific concept in a course"""
        try:
            course = Course.objects(id=course_id).first()
            if not course:
                raise ValueError("Course not found")
            
            # Validate status
            valid_statuses = ['not_started', 'reviewed', 'not_interested', 'already_know']
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
