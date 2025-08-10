from marshmallow import Schema, fields, validate, post_load

# Conversation History Item Schema
class ConversationItemDTO(Schema):
    """Schema for conversation history items"""
    role = fields.Str(validate=validate.OneOf(['user', 'assistant']))
    content = fields.Str()
    timestamp = fields.Str(allow_none=True)
