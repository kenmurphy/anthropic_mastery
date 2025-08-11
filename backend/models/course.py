from mongoengine import Document, StringField, ListField, EmbeddedDocument, EmbeddedDocumentField, DateTimeField
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
        choices=['not_started', 'reviewed', 'not_interested', 'already_know'], 
        default='not_started'
    )
    
    def to_dict(self):
        """Convert concept to dictionary"""
        return {
            'title': self.title,
            'difficulty_level': self.difficulty_level,
            'status': self.status
        }

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
        completed = len([c for c in self.concepts if c.status in ['reviewed', 'already_know']])
        return round((completed / len(self.concepts)) * 100)
    
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
            'progress': self._calculate_progress(),
            'created_at': format_datetime(self.created_at),
            'updated_at': format_datetime(self.updated_at)
        }
    
    def __str__(self):
        return f"Course(id={self.id}, label={self.label}, progress={self._calculate_progress()}%)"
