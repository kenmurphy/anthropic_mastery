from mongoengine import Document, StringField, ListField, FloatField, IntField, DateTimeField
from datetime import datetime
from bson import ObjectId

class ConversationCluster(Document):
    """Conversation cluster model - stores semantic clusters of conversations"""
    
    # Collection name in MongoDB
    meta = {'collection': 'conversation_clusters'}
    
    # Fields
    cluster_id = StringField(required=True, unique=True, max_length=50)  # "cluster_0", "cluster_1", etc.
    label = StringField(required=True, max_length=200)  # "Database Design & Optimization"
    description = StringField(required=True, max_length=500)  # 2-sentence cluster summary
    conversation_ids = ListField(StringField())  # Conversations in this cluster
    key_concepts = ListField(StringField())  # Top technical concepts
    centroid = ListField(FloatField())  # Cluster center vector (1024-dim)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    # Index for efficient queries
    meta = {
        'collection': 'conversation_clusters',
        'indexes': [
            'cluster_id',
            'updated_at',
        ]
    }
    
    def save(self, *args, **kwargs):
        """Override save to update the updated_at field"""
        self.updated_at = datetime.utcnow()
        return super(ConversationCluster, self).save(*args, **kwargs)
    
    def add_conversation(self, conversation_id: str):
        """Add a conversation to this cluster"""
        if conversation_id not in self.conversation_ids:
            self.conversation_ids.append(conversation_id)
            self.save()
    
    def remove_conversation(self, conversation_id: str):
        """Remove a conversation from this cluster"""
        if conversation_id in self.conversation_ids:
            self.conversation_ids.remove(conversation_id)
            self.save()
    
    def get_conversation_count(self) -> int:
        """Get the number of conversations in this cluster"""
        return len(self.conversation_ids)
    
    def to_dict(self):
        """Convert cluster to dictionary"""
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
            'cluster_id': self.cluster_id,
            'label': self.label,
            'description': self.description,
            'conversation_count': self.get_conversation_count(),
            'conversation_ids': self.conversation_ids,
            'key_concepts': self.key_concepts,
            'created_at': format_datetime(self.created_at),
            'updated_at': format_datetime(self.updated_at)
        }
    
    def __str__(self):
        return f"ConversationCluster(cluster_id={self.cluster_id}, label={self.label})"


class ClusteringRun(Document):
    """Clustering run model - tracks clustering operations"""
    
    # Collection name in MongoDB
    meta = {'collection': 'clustering_runs'}
    
    # Fields
    run_id = StringField(required=True, unique=True, max_length=50)
    total_conversations = IntField(required=True)
    clusters_created = IntField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    
    # Index for efficient queries
    meta = {
        'collection': 'clustering_runs',
        'indexes': [
            'run_id',
            'created_at',
        ]
    }
    
    @classmethod
    def create_run(cls, total_conversations: int, clusters_created: int) -> 'ClusteringRun':
        """Create a new clustering run record"""
        run = cls(
            run_id=f"run_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            total_conversations=total_conversations,
            clusters_created=clusters_created
        )
        run.save()
        return run
    
    def to_dict(self):
        """Convert clustering run to dictionary"""
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
            'run_id': self.run_id,
            'total_conversations': self.total_conversations,
            'clusters_created': self.clusters_created,
            'created_at': format_datetime(self.created_at)
        }
    
    def __str__(self):
        return f"ClusteringRun(run_id={self.run_id}, conversations={self.total_conversations})"
