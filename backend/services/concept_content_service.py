import threading
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import List

from models.course import Course
from services.anthropic_service import AnthropicService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConceptContentService:
    """Service for generating concept summaries and teaching questions in background threads"""
    
    def __init__(self, anthropic_service: AnthropicService):
        self.anthropic_service = anthropic_service
        self.executor = ThreadPoolExecutor(max_workers=10)  # Configurable
        
    def generate_concept_content_batch(self, course_id: str, concept_titles: List[str]):
        """Start background generation for multiple concepts"""
        try:
            course = Course.objects.get(id=course_id)
            
            for concept_title in concept_titles:
                concept = course.get_concept_by_title(concept_title)
                if not concept:
                    logger.warning(f"Concept not found: {concept_title}")
                    continue
                
                # Start summary thread if needed
                if concept.should_generate_summary():
                    logger.info(f"Starting summary generation for: {concept_title}")
                    self.executor.submit(
                        self._generate_summary_worker, 
                        course_id, 
                        concept_title
                    )
                    
                # Start questions thread if needed  
                if concept.should_generate_questions():
                    logger.info(f"Starting questions generation for: {concept_title}")
                    self.executor.submit(
                        self._generate_questions_worker, 
                        course_id, 
                        concept_title
                    )
                    
        except Exception as e:
            logger.error(f"Error starting batch generation for course {course_id}: {e}")
    
    def _generate_summary_worker(self, course_id: str, concept_title: str):
        """Background worker for summary generation"""
        try:
            # Reload fresh data in this thread
            course = Course.objects.get(id=course_id)
            concept = course.get_concept_by_title(concept_title)
            
            if not concept:
                logger.warning(f"Concept not found in worker: {concept_title}")
                return
            
            # Double-check if still needed (race condition protection)
            if not concept.should_generate_summary():
                logger.info(f"Summary generation no longer needed: {concept_title}")
                return
                
            logger.info(f"Generating summary for concept: {concept_title}")
            
            # Generate summary
            summary = self.anthropic_service.generate_concept_summary(
                concept_title, 
                course.description
            )
            
            # Reload course again to check streaming flag
            course = Course.objects.get(id=course_id)
            concept = course.get_concept_by_title(concept_title)
            
            if not concept:
                logger.warning(f"Concept disappeared during generation: {concept_title}")
                return
            
            # Only save if not currently streaming
            if not getattr(concept, 'is_streaming_summary', False):
                concept.set_summary(summary)
                course.save()
                logger.info(f"Summary saved for concept: {concept_title}")
            else:
                logger.info(f"Summary generation cancelled (streaming active): {concept_title}")
                
        except Exception as e:
            logger.error(f"Error generating summary for {concept_title}: {e}")
    
    def _generate_questions_worker(self, course_id: str, concept_title: str):
        """Background worker for questions generation"""
        try:
            # Reload fresh data in this thread
            course = Course.objects.get(id=course_id)
            course_label = getattr(course, 'label', None)
            course_description = getattr(course, 'description', None)
            concept = course.get_concept_by_title(concept_title)
            
            if not concept:
                logger.warning(f"Concept not found in worker: {concept_title}")
                return
            
            # Double-check if still needed
            if not concept.should_generate_questions():
                logger.info(f"Questions generation no longer needed: {concept_title}")
                return
                
            logger.info(f"Generating questions for concept: {concept_title}")
            
            concept_summary = getattr(concept, 'summary', None)
            context = (
                f"Course title: {course_label}\n"
                f"Course description: {course_description}\n"
                f"Concept: {concept_title}\n"
                f"Concept summary: {concept_summary if concept_summary else ''}"
            )
            # Generate questions
            questions = self.anthropic_service.generate_teaching_questions(
                concept_title, 
                str(context)
            )
            print(f"Questions generated: {questions}")
            
            # Reload course again to check streaming flag
            course = Course.objects.get(id=course_id)
            concept = course.get_concept_by_title(concept_title)
            
            if not concept:
                logger.warning(f"Concept disappeared during generation: {concept_title}")
                return
            
            # Only save if not currently streaming
            if not getattr(concept, 'is_streaming_questions', False):
                concept.set_teaching_questions(questions)
                course.save()
                logger.info(f"Questions saved for concept: {concept_title}")
            else:
                logger.info(f"Questions generation cancelled (streaming active): {concept_title}")
                
        except Exception as e:
            logger.error(f"Error generating questions for {concept_title}: {e}")
    
    def shutdown(self):
        """Shutdown the thread pool executor"""
        self.executor.shutdown(wait=True)
