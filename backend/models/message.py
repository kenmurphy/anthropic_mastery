from mongoengine import Document, StringField, DateTimeField, ListField, FloatField, BooleanField
from datetime import datetime
from bson import ObjectId

class Message(Document):
    """Message model - stores individual messages from conversations"""
    
    # Collection name in MongoDB
    meta = {'collection': 'messages'}
    
    # Fields
    conversation_id = StringField(required=True, max_length=24)  # ObjectId as string
    message_id = StringField(required=True, max_length=24, unique=True)  # Unique message identifier
    speaker = StringField(required=True, choices=['user', 'assistant'], max_length=20)
    content = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    
    # Semantic clustering fields
    technical_concepts = ListField(StringField())  # Extracted technical concepts
    embedding = ListField(FloatField())  # 1024-dim vector from Anthropic
    processed_for_clustering = BooleanField(default=False)  # Analysis status
    
    # Index for efficient queries
    meta = {
        'collection': 'messages',
        'indexes': [
            'conversation_id',
            'message_id',
            ('conversation_id', 'created_at'),  # Compound index for conversation message ordering
        ]
    }
    
    def save(self, *args, **kwargs):
        """Override save to ensure message_id is set"""
        if not self.message_id:
            self.message_id = str(ObjectId())
        return super(Message, self).save(*args, **kwargs)
    
    @classmethod
    def create_message(cls, conversation_id: str, speaker: str, content: str) -> 'Message':
        """Create a new message with auto-generated message_id"""
        message = cls(
            conversation_id=conversation_id,
            speaker=speaker,
            content=content,
            message_id=str(ObjectId())
        )
        message.save()
        return message
    
    @classmethod
    def get_conversation_messages(cls, conversation_id: str, limit: int = None):
        """Get all messages for a conversation, ordered by creation time"""
        query = cls.objects(conversation_id=conversation_id).order_by('created_at')
        if limit:
            query = query.limit(limit)
        return query
    
    @classmethod
    def get_message_history_for_ai(cls, conversation_id: str) -> list:
        """Get conversation messages formatted for AI API (role/content format)"""
        messages = cls.get_conversation_messages(conversation_id)
        return [
            {
                'role': msg.speaker,
                'content': msg.content
            }
            for msg in messages
        ]
    
    def to_dict(self):
        """Convert message to dictionary"""
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
            'id': self.message_id,
            'role': self.speaker,
            'content': self.content,
            'timestamp': format_datetime(self.created_at)
        }
    
    def __str__(self):
        return f"Message(conversation_id={self.conversation_id}, speaker={self.speaker})"
