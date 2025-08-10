from flask import Blueprint, request, jsonify, Response
from marshmallow import ValidationError
import json
from datetime import datetime

from dto.conversation_dto import (
    ConversationCreateRequestDTO, ConversationMessageRequestDTO,
    ConversationListResponseDTO, ConversationResponseDTO,
    ConversationStreamResponseDTO
)
from services.conversation_service import ConversationService

# Create blueprint
conversation_bp = Blueprint('conversations', __name__, url_prefix='/api/conversations')

# Initialize service
conversation_service = ConversationService()

def create_sse_response(generator):
    """Create Server-Sent Events response from generator"""
    def event_stream():
        try:
            for data in generator:
                # Format as SSE
                json_data = json.dumps(data)
                yield f"data: {json_data}\n\n"
        except Exception as e:
            # Send error event
            error_data = json.dumps({
                'error': str(e),
                'is_complete': True
            })
            yield f"data: {error_data}\n\n"
    
    return Response(
        event_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type, X-User-ID, Cache-Control',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Expose-Headers': 'Cache-Control'
        }
    )

@conversation_bp.route('', methods=['POST'])
def create_conversation():
    """
    Create a new conversation
    
    Request body:
    {
        "initial_message": "string",
        "title": "string" (optional)
    }
    
    Response: Conversation object with initial message
    """
    try:
        # Validate request data
        schema = ConversationCreateRequestDTO()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return jsonify({'error': 'Validation error', 'details': err.messages}), 400
        
        # Create conversation
        conversation = ConversationService.create_conversation(
            initial_message=data['initial_message'],
            title=data.get('title')
        )
        
        # Return conversation data
        response_schema = ConversationResponseDTO()
        return jsonify(response_schema.dump(conversation.to_dict(include_messages=True))), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@conversation_bp.route('', methods=['GET'])
def list_conversations():
    """
    List all conversations
    
    Query parameters:
    - limit: Maximum number of conversations (default: 50)
    - offset: Number of conversations to skip (default: 0)
    
    Response: List of conversations (without messages)
    """
    try:
        # Get query parameters
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100
        offset = int(request.args.get('offset', 0))
        
        # Get all conversations
        conversations = ConversationService.get_all_conversations(
            limit=limit,
            offset=offset
        )
        
        # Serialize response
        response_schema = ConversationListResponseDTO(many=True)
        conversations_data = [conv.to_dict(include_messages=False) for conv in conversations]
        
        return jsonify({
            'conversations': response_schema.dump(conversations_data),
            'total': len(conversations_data),
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@conversation_bp.route('/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """
    Get a specific conversation with full message history
    
    Response: Full conversation object with messages
    """
    try:
        # Get conversation
        conversation = ConversationService.get_conversation_by_id(conversation_id)
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        # Serialize response
        response_schema = ConversationResponseDTO()
        return jsonify(response_schema.dump(conversation.to_dict(include_messages=True))), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@conversation_bp.route('/<conversation_id>/stream-response', methods=['POST'])
def stream_response(conversation_id):
    """
    Stream AI response for existing conversation without adding a new user message
    
    This is used for the first AI response after creating a conversation,
    where the user message is already in the conversation.
    
    Response: Server-Sent Events stream with AI response
    """
    try:
        # Get conversation
        conversation = ConversationService.get_conversation_by_id(conversation_id)
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        # Stream AI response directly (no new user message)
        def response_generator():
            # Stream AI response
            for chunk in conversation_service.stream_ai_response(conversation):
                yield chunk
            
            # Update conversation title if needed (async)
            try:
                ConversationService.update_conversation_title(conversation)
            except Exception as e:
                print(f"Failed to update conversation title: {e}")
        
        return create_sse_response(response_generator())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@conversation_bp.route('/<conversation_id>/messages', methods=['POST'])
def add_message(conversation_id):
    """
    Add a message to conversation and stream AI response
    
    Request body:
    {
        "message": "string"
    }
    
    Response: Server-Sent Events stream with AI response
    """
    try:
        # Validate request data
        schema = ConversationMessageRequestDTO()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return jsonify({'error': 'Validation error', 'details': err.messages}), 400
        
        # Get conversation
        conversation = ConversationService.get_conversation_by_id(conversation_id)
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        # Add user message
        user_message_id = ConversationService.add_user_message(
            conversation=conversation,
            message=data['message']
        )
        
        # Stream AI response
        def response_generator():
            # First, yield the user message confirmation
            yield {
                'content': '',
                'message_id': user_message_id,
                'is_complete': False,
                'error': None,
                'conversation_id': conversation_id,
                'message_type': 'user_added'
            }
            
            # Then stream AI response
            for chunk in conversation_service.stream_ai_response(conversation):
                yield chunk
            
            # Update conversation title if needed (async)
            try:
                ConversationService.update_conversation_title(conversation)
            except Exception as e:
                print(f"Failed to update conversation title: {e}")
        
        return create_sse_response(response_generator())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@conversation_bp.route('/health', methods=['GET'])
def conversation_health_check():
    """Health check endpoint for conversation services"""
    try:
        # Test service initialization
        service_status = {
            'conversation_service': 'healthy' if conversation_service else 'unhealthy',
            'anthropic_service': 'healthy' if conversation_service.anthropic_service else 'unhealthy'
        }
        
        return jsonify({
            'status': 'healthy',
            'service': 'conversation_routes',
            'services': service_status,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Error handlers for conversation blueprint
@conversation_bp.errorhandler(400)
def conversation_bad_request(error):
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400

@conversation_bp.errorhandler(401)
def conversation_unauthorized(error):
    return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401

@conversation_bp.errorhandler(404)
def conversation_not_found(error):
    return jsonify({'error': 'Resource not found', 'message': str(error)}), 404

@conversation_bp.errorhandler(500)
def conversation_internal_error(error):
    return jsonify({'error': 'Internal server error', 'message': str(error)}), 500
