from mongoengine import Document, StringField, DateTimeField
from datetime import datetime
from bson import ObjectId

class Conversation(Document):
    """Conversation model - stores conversation metadata, messages stored separately"""
    
    # Collection name in MongoDB
    meta = {'collection': 'conversations'}
    
    # Fields
    title = StringField(required=True, max_length=200)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def save(self, *args, **kwargs):
        """Override save to update the updated_at field"""
        self.updated_at = datetime.utcnow()
        return super(Conversation, self).save(*args, **kwargs)
    
    def add_message(self, speaker: str, content: str) -> str:
        """Add a message to the conversation using the separate Message model"""
        # Import here to avoid circular imports
        from .message import Message
        
        message = Message.create_message(
            conversation_id=str(self.id),
            speaker=speaker,
            content=content
        )
        
        # Update conversation timestamp
        self.save()
        
        return message.message_id
    
    def get_messages(self):
        """Get all messages for this conversation"""
        # Import here to avoid circular imports
        from .message import Message
        return Message.get_conversation_messages(str(self.id))
    
    def get_message_history(self) -> list:
        """Get conversation messages formatted for AI API"""
        # Import here to avoid circular imports
        from .message import Message
        return Message.get_message_history_for_ai(str(self.id))
    
    def get_message_count(self) -> int:
        """Get the number of messages in this conversation"""
        # Import here to avoid circular imports
        from .message import Message
        return Message.objects(conversation_id=str(self.id)).count()
    
    def to_dict(self, include_messages=True):
        """Convert conversation to dictionary"""
        def format_datetime(dt):
            """Helper to safely format datetime objects"""
            if dt is None:
                return None
            if isinstance(dt, datetime):
                return dt.isoformat()
            if isinstance(dt, str):
                return dt
            return str(dt)
        
        result = {
            'id': str(self.id),
            'title': self.title,
            'created_at': format_datetime(self.created_at),
            'updated_at': format_datetime(self.updated_at),
            'message_count': self.get_message_count()
        }
        
        if include_messages:
            messages = self.get_messages()
            result['messages'] = [msg.to_dict() for msg in messages]
        
        return result
    
    def __str__(self):
        return f"Conversation(title={self.title})"
