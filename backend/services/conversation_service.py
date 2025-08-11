from typing import List, Optional, Dict, Any
from models.conversation import Conversation
from models.message import Message
from services.anthropic_service import AnthropicService
from services.message_analysis_service import MessageAnalysisService
from services.conversation_clustering_service import ConversationClusteringService
from services.background_clustering_service import BackgroundClusteringService
import logging

logger = logging.getLogger(__name__)

class ConversationService:
    """Service for managing conversations and Claude interactions"""
    
    def __init__(self):
        self.anthropic_service = AnthropicService()
        self.message_analysis_service = MessageAnalysisService()
        self.clustering_service = ConversationClusteringService()
    
    @staticmethod
    def create_conversation(initial_message: str, title: str = None) -> Conversation:
        """
        Create a new conversation with an initial user message
        
        Args:
            initial_message: First message from the user
            title: Optional custom title, will be auto-generated if not provided
            
        Returns:
            Created conversation object
        """
        # Generate title if not provided
        if not title:
            title = ConversationService._generate_title_from_message(initial_message)
        
        # Create conversation
        conversation = Conversation(title=title)
        conversation.save()
        
        # Add initial user message
        message_id = conversation.add_message('user', initial_message)
        
        # Trigger background analysis for the initial message
        try:
            background_service = BackgroundClusteringService()
            background_service.trigger_background_analysis(message_id)
            logger.info(f"Triggered background analysis for initial message {message_id} in new conversation {conversation.id}")
        except Exception as e:
            logger.error(f"Error triggering background analysis for initial message: {str(e)}")
        
        return conversation
    
    @staticmethod
    def get_all_conversations(limit: int = 50, offset: int = 0) -> List[Conversation]:
        """
        Get all conversations
        
        Args:
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip
            
        Returns:
            List of all conversations
        """
        return Conversation.objects().order_by('-updated_at').skip(offset).limit(limit)
    
    @staticmethod
    def get_conversation_by_id(conversation_id: str) -> Optional[Conversation]:
        """
        Get a specific conversation by ID
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            Conversation object if found, None otherwise
        """
        try:
            return Conversation.objects(id=conversation_id).first()
        except Exception:
            return None
    
    @staticmethod
    def add_user_message(conversation: Conversation, message: str) -> str:
        """
        Add a user message to the conversation
        
        Args:
            conversation: Conversation to add message to
            message: User's message content
            
        Returns:
            Message ID of the added message
        """
        message_id = conversation.add_message('user', message)
        
        # Trigger background analysis for the user message
        try:
            background_service = BackgroundClusteringService()
            background_service.trigger_background_analysis(message_id)
            logger.info(f"Triggered background analysis for user message {message_id} in conversation {conversation.id}")
        except Exception as e:
            logger.error(f"Error triggering background analysis for user message: {str(e)}")
        
        return message_id
    
    def stream_ai_response(self, conversation: Conversation):
        """
        Stream AI response for the conversation
        
        Args:
            conversation: Conversation to generate response for
            
        Yields:
            Dict with streaming response data
        """
        try:
            # Get conversation history for Anthropic
            message_history = conversation.get_message_history()
            
            # Stream response from Anthropic
            accumulated_content = ""
            
            for chunk in self.anthropic_service.stream_conversation_response(message_history):
                if chunk.get('content'):
                    accumulated_content += chunk['content']
                
                yield {
                    'content': chunk.get('content', ''),
                    'is_complete': chunk.get('is_complete', False),
                    'error': chunk.get('error'),
                    'conversation_id': str(conversation.id)
                }
                
                # If response is complete, save the assistant message
                if chunk.get('is_complete') and not chunk.get('error'):
                    message_id = conversation.add_message('assistant', accumulated_content)
                    
                    # Trigger real-time analysis and clustering
                    self._trigger_conversation_analysis(conversation)
                    
                    yield {
                        'content': '',
                        'message_id': message_id,
                        'is_complete': True,
                        'error': None,
                        'conversation_id': str(conversation.id)
                    }
                    break
                    
        except Exception as e:
            yield {
                'content': '',
                'is_complete': True,
                'error': str(e),
                'conversation_id': str(conversation.id)
            }
    
    @staticmethod
    def update_conversation_title(conversation: Conversation, anthropic_service: AnthropicService = None):
        """
        Update conversation title based on conversation content
        
        Args:
            conversation: Conversation to update title for
            anthropic_service: Optional Anthropic service instance
        """
        if not anthropic_service:
            anthropic_service = AnthropicService()
        
        # Only update title if conversation has multiple messages
        if conversation.get_message_count() >= 3:  # User + Assistant + User (at least)
            try:
                new_title = anthropic_service.generate_conversation_title(
                    conversation.get_message_history()
                )
                if new_title and new_title != conversation.title:
                    conversation.title = new_title
                    conversation.save()
            except Exception as e:
                # Silently fail title updates to not disrupt conversation flow
                print(f"Failed to update conversation title: {e}")
    
    @staticmethod
    def _generate_title_from_message(message: str) -> str:
        """
        Generate a simple title from the initial message
        
        Args:
            message: Initial message content
            
        Returns:
            Generated title
        """
        # Simple title generation - take first 50 characters
        title = message.strip()
        if len(title) > 50:
            title = title[:47] + "..."
        
        return title if title else "New Conversation"
    
    def _trigger_conversation_analysis(self, conversation: Conversation):
        """
        Trigger background analysis and clustering for a conversation
        
        Args:
            conversation: Conversation to analyze
        """
        try:
            # Get the latest message from the conversation to trigger background analysis
            messages = Message.get_conversation_messages(str(conversation.id))
            if messages:
                latest_message = messages.order_by('-created_at').first()
                if latest_message:
                    # Trigger background analysis and clustering
                    background_service = BackgroundClusteringService()
                    background_service.trigger_background_analysis(latest_message.message_id)
                    logger.info(f"Triggered background analysis for message {latest_message.message_id} in conversation {conversation.id}")
                else:
                    logger.warning(f"No messages found in conversation {conversation.id}")
            else:
                logger.warning(f"Could not retrieve messages for conversation {conversation.id}")
            
        except Exception as e:
            # Don't let analysis errors disrupt the conversation flow
            logger.error(f"Error triggering background analysis: {str(e)}")
    
    def get_conversation_analysis(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get analysis results for a conversation
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Get technical concepts
            concepts = self.message_analysis_service.get_conversation_concepts(conversation_id)
            
            # Get cluster information
            cluster = self.clustering_service.get_conversation_cluster(conversation_id)
            
            # Get similar conversations
            similar_conversations = self.clustering_service.find_similar_conversations(conversation_id)
            
            return {
                'conversation_id': conversation_id,
                'technical_concepts': concepts,
                'cluster': cluster,
                'similar_conversations': similar_conversations,
                'analysis_available': len(concepts) > 0
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation analysis: {str(e)}")
            return {
                'conversation_id': conversation_id,
                'technical_concepts': [],
                'cluster': None,
                'similar_conversations': [],
                'analysis_available': False,
                'error': str(e)
            }
