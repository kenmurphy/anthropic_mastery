from mongoengine import Document, StringField, DateTimeField, ListField, DictField
from datetime import datetime
from bson import ObjectId

class Conversation(Document):
    """Conversation model - stores multi-turn conversations with ChatGPT"""
    
    # Collection name in MongoDB
    meta = {'collection': 'conversations'}
    
    # Fields
    title = StringField(required=True, max_length=200)
    messages = ListField(DictField())  # Array of message objects
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def save(self, *args, **kwargs):
        """Override save to update the updated_at field"""
        self.updated_at = datetime.utcnow()
        return super(Conversation, self).save(*args, **kwargs)
    
    def add_message(self, role: str, content: str) -> str:
        """Add a message to the conversation and return message ID"""
        message_id = str(ObjectId())
        message = {
            'message_id': message_id,
            'role': role,
            'content': content,
            'timestamp': datetime.utcnow()
        }
        
        if not self.messages:
            self.messages = []
        
        self.messages.append(message)
        self.save()
        return message_id
    
    def get_message_history(self) -> list:
        """Get conversation messages formatted for OpenAI API"""
        if not self.messages:
            return []
        
        return [
            {
                'role': msg['role'],
                'content': msg['content']
            }
            for msg in self.messages
        ]
    
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
            'message_count': len(self.messages) if self.messages else 0
        }
        
        if include_messages and self.messages:
            result['messages'] = [
                {
                    'message_id': msg.get('message_id'),
                    'role': msg.get('role'),
                    'content': msg.get('content'),
                    'timestamp': format_datetime(msg.get('timestamp'))
                }
                for msg in self.messages
            ]
        
        return result
    
    def __str__(self):
        return f"Conversation(title={self.title})"
