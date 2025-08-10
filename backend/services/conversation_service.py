from typing import List, Optional, Dict, Any
from models.conversation import Conversation
from services.anthropic_service import AnthropicService

class ConversationService:
    """Service for managing conversations and Claude interactions"""
    
    def __init__(self):
        self.anthropic_service = AnthropicService()
    
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
        conversation = Conversation(
            title=title,
            messages=[]
        )
        conversation.save()
        
        # Add initial user message
        conversation.add_message('user', initial_message)
        
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
        return conversation.add_message('user', message)
    
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
        if len(conversation.messages) >= 3:  # User + Assistant + User (at least)
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
