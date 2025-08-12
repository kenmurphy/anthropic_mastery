from mongoengine import Document, StringField, ListField, EmbeddedDocument, EmbeddedDocumentField, DateTimeField, BooleanField
from datetime import datetime

class CourseConcept(EmbeddedDocument):
    """Embedded document for course concepts with learning status"""
    title = StringField(required=True, max_length=200)
    difficulty_level = StringField(
        required=True, 
        choices=['beginner', 'medium', 'advanced'], 
        default='medium'
    )
    status = StringField(
        required=True, 
        choices=['not_started', 'reviewing'], 
        default='not_started'
    )
    type = StringField(
        required=True,
        choices=['original', 'related'],
        default='original'
    )
    summary = StringField()  # Cached AI-generated summary
    summary_generated_at = DateTimeField()  # When summary was generated
    teaching_questions = ListField(StringField())  # AI-generated teaching questions
    teaching_questions_generated_at = DateTimeField()  # When questions were generated
    
    # Streaming control flags
    is_streaming_summary = BooleanField(default=False)
    is_streaming_questions = BooleanField(default=False)
    
    def to_dict(self):
        """Convert concept to dictionary"""
        def format_datetime(dt):
            """Helper to safely format datetime objects"""
            if dt is None:
                return None
            if isinstance(dt, datetime):
                return dt.isoformat()
            if isinstance(dt, str):
                return dt
            return str(dt)
        
        return {
            'title': self.title,
            'difficulty_level': self.difficulty_level,
            'status': self.status,
            'type': self.type,
            'summary': self.summary,
            'summary_generated_at': format_datetime(self.summary_generated_at),
            'teaching_questions': getattr(self, 'teaching_questions', None),
            'teaching_questions_generated_at': format_datetime(getattr(self, 'teaching_questions_generated_at', None)),
            'is_streaming_summary': getattr(self, 'is_streaming_summary', False),
            'is_streaming_questions': getattr(self, 'is_streaming_questions', False)
        }
    
    def has_summary(self):
        """Check if concept has a cached summary"""
        return bool(self.summary and str(self.summary).strip())
    
    def set_summary(self, summary_text):
        """Set the summary and update timestamp"""
        self.summary = summary_text
        self.summary_generated_at = datetime.utcnow()
    
    def should_generate_summary(self):
        """Check if summary needs generation"""
        if getattr(self, 'is_streaming_summary', False):
            return False
        summary = getattr(self, 'summary', None)
        if not summary or not str(summary).strip():
            return True
        # Check if summary is older than 7 days (configurable)
        summary_date = getattr(self, 'summary_generated_at', None)
        if summary_date and isinstance(summary_date, datetime):
            age = datetime.utcnow() - summary_date
            return age.days > 7
        return True
    
    def should_generate_questions(self):
        """Check if questions need generation"""
        if getattr(self, 'is_streaming_questions', False):
            return False
        questions = getattr(self, 'teaching_questions', None)
        if not questions or len(questions) == 0:
            return True
        # Check if questions are older than 3 days (configurable)
        questions_date = getattr(self, 'teaching_questions_generated_at', None)
        if questions_date and isinstance(questions_date, datetime):
            age = datetime.utcnow() - questions_date
            return age.days > 3
        return True
    
    def set_teaching_questions(self, questions):
        """Set the teaching questions and update timestamp"""
        self.teaching_questions = questions
        self.teaching_questions_generated_at = datetime.utcnow()

class Course(Document):
    """Course model - created from conversation clusters for structured learning"""
    
    # Collection name in MongoDB
    meta = {'collection': 'courses'}
    
    # Basic fields copied from ConversationCluster
    label = StringField(required=True, max_length=200)
    description = StringField(required=True, max_length=500) 
    conversation_ids = ListField(StringField())
    
    # Structured concepts array with learning status
    concepts = ListField(EmbeddedDocumentField(CourseConcept))
    
    # Learning stage tracking
    current_stage = StringField(
        required=True,
        choices=['explore', 'absorb', 'teach_back'],
        default='explore'
    )
    
    # Reference back to source cluster (may become orphaned after re-clustering)
    source_cluster_id = StringField(required=True, max_length=50)
    
    # Metadata
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    # Index for efficient queries
    meta = {
        'collection': 'courses',
        'indexes': [
            'source_cluster_id',
            'created_at',
            'updated_at',
        ]
    }
    
    def save(self, *args, **kwargs):
        """Override save to update the updated_at field"""
        self.updated_at = datetime.utcnow()
        return super(Course, self).save(*args, **kwargs)
    
    def _calculate_progress(self):
        """Calculate learning progress percentage"""
        if not self.concepts:
            return 0
        # With simplified status model, progress is based on concepts being reviewed
        reviewing = len([c for c in self.concepts if c.status == 'reviewing'])
        return round((reviewing / len(self.concepts)) * 100)
    
    def get_concept_by_title(self, title: str):
        """Get a specific concept by title"""
        for concept in self.concepts:
            if concept.title == title:
                return concept
        return None
    
    def update_concept_status(self, concept_title: str, new_status: str):
        """Update the status of a specific concept"""
        concept = self.get_concept_by_title(concept_title)
        if concept:
            concept.status = new_status
            self.save()
            return True
        return False
    
    def start_review(self, selected_concept_titles: list, concept_content_service=None):
        """Start review process by updating concept statuses and course stage"""
        # Update selected concepts to 'reviewing' status
        # Leave unselected concepts as 'not_started'
        for concept in self.concepts:
            if concept.title in selected_concept_titles:
                concept.status = 'reviewing'
            # Unselected concepts remain 'not_started' - no change needed
        
        # Update course stage to 'absorb'
        self.current_stage = 'absorb'
        
        # Save changes
        self.save()
        
        # Start background content generation if service is provided
        if concept_content_service:
            concept_content_service.generate_concept_content_batch(
                str(self.id), 
                selected_concept_titles
            )
        
        return True
    
    def to_study_guide_dict(self):
        """Convert to unified study guide format"""
        def format_datetime(dt):
            """Helper to safely format datetime objects"""
            if dt is None:
                return None
            if isinstance(dt, datetime):
                return dt.isoformat()
            if isinstance(dt, str):
                return dt
            return str(dt)
        
        return {
            'id': str(self.id),
            'type': 'course',
            'label': self.label,
            'description': self.description,
            'conversation_count': len(self.conversation_ids),
            'conversation_ids': self.conversation_ids,
            'key_concepts': [concept.title for concept in self.concepts],
            'created_at': format_datetime(self.created_at),
            'updated_at': format_datetime(self.updated_at),
            # Course-specific fields
            'progress': self._calculate_progress(),
            'concepts_detail': [concept.to_dict() for concept in self.concepts],
            'source_cluster_id': self.source_cluster_id
        }
    
    def to_dict(self):
        """Convert course to dictionary"""
        def format_datetime(dt):
            """Helper to safely format datetime objects"""
            if dt is None:
                return None
            if isinstance(dt, datetime):
                return dt.isoformat()
            if isinstance(dt, str):
                return dt
            return str(dt)
        
        return {
            'id': str(self.id),
            'label': self.label,
            'description': self.description,
            'conversation_ids': self.conversation_ids,
            'concepts': [concept.to_dict() for concept in self.concepts],
            'source_cluster_id': self.source_cluster_id,
            'current_stage': self.current_stage,
            'progress': self._calculate_progress(),
            'created_at': format_datetime(self.created_at),
            'updated_at': format_datetime(self.updated_at)
        }
    
    def __str__(self):
        return f"Course(id={self.id}, label={self.label}, progress={self._calculate_progress()}%)"
