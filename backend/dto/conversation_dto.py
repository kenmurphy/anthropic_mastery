from marshmallow import Schema, fields, validate, post_load
from datetime import datetime

class MessageSchema(Schema):
    """Schema for individual message within a conversation"""
    id = fields.Str(required=True)
    role = fields.Str(required=True, validate=validate.OneOf(['user', 'assistant']))
    content = fields.Str(required=True)
    timestamp = fields.Str(allow_none=True)  # Changed to Str since we're formatting as ISO string

class ConversationCreateRequestDTO(Schema):
    """DTO for creating a new conversation"""
    initial_message = fields.Str(required=True, validate=validate.Length(min=1, max=10000))
    title = fields.Str(missing=None, validate=validate.Length(max=200))
    
    @post_load
    def make_conversation_create_request(self, data, **kwargs):
        return data

class ConversationMessageRequestDTO(Schema):
    """DTO for adding a message to an existing conversation"""
    message = fields.Str(required=True, validate=validate.Length(min=1, max=10000))
    
    @post_load
    def make_message_request(self, data, **kwargs):
        return data

class ConversationListResponseDTO(Schema):
    """DTO for conversation list response (without messages)"""
    id = fields.Str(required=True)
    title = fields.Str(required=True)
    created_at = fields.Str(allow_none=True)  # Changed to allow None and use Str
    updated_at = fields.Str(allow_none=True)  # Changed to allow None and use Str
    message_count = fields.Int(required=True)

class ConversationResponseDTO(Schema):
    """DTO for full conversation response (with messages)"""
    id = fields.Str(required=True)
    title = fields.Str(required=True)
    created_at = fields.Str(allow_none=True)  # Changed to allow None and use Str
    updated_at = fields.Str(allow_none=True)  # Changed to allow None and use Str
    message_count = fields.Int(required=True)
    messages = fields.List(fields.Nested(MessageSchema), missing=[])

class ConversationStreamResponseDTO(Schema):
    """DTO for streaming conversation responses"""
    content = fields.Str(required=True)
    message_id = fields.Str(missing=None)
    is_complete = fields.Bool(required=True)
    error = fields.Str(missing=None)
    conversation_id = fields.Str(required=True)
