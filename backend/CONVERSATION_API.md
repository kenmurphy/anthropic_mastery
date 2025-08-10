# Conversation API Documentation

This document describes the multi-turn conversation API that enables ChatGPT conversations with persistent message history.

## Overview

The Conversation API provides endpoints for creating and managing multi-turn conversations with ChatGPT. Each conversation maintains a complete message history and supports real-time streaming responses.

## Endpoints

### 1. Create Conversation
**POST** `/api/conversations`

Creates a new conversation with an initial user message.

**Headers:**
- `Content-Type: application/json`
- `X-User-ID: <user_id>` (required for authentication)

**Request Body:**
```json
{
  "initial_message": "Hello! Can you help me understand Python decorators?",
  "title": "Learning Python Decorators" // optional
}
```

**Response (201 Created):**
```json
{
  "id": "conversation_id",
  "title": "Learning Python Decorators",
  "owner": {
    "id": "user_id",
    "name": "John Doe",
    "email": "john@example.com"
  },
  "created_at": "2025-01-10T14:30:00Z",
  "updated_at": "2025-01-10T14:30:00Z",
  "message_count": 1,
  "messages": [
    {
      "message_id": "msg_id",
      "role": "user",
      "content": "Hello! Can you help me understand Python decorators?",
      "timestamp": "2025-01-10T14:30:00Z"
    }
  ]
}
```

### 2. List Conversations
**GET** `/api/conversations`

Lists user's conversations (without message content for performance).

**Headers:**
- `X-User-ID: <user_id>` (required)

**Query Parameters:**
- `limit`: Maximum conversations to return (default: 50, max: 100)
- `offset`: Number of conversations to skip (default: 0)

**Response (200 OK):**
```json
{
  "conversations": [
    {
      "id": "conversation_id",
      "title": "Learning Python Decorators",
      "owner": {...},
      "created_at": "2025-01-10T14:30:00Z",
      "updated_at": "2025-01-10T14:35:00Z",
      "message_count": 3
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

### 3. Get Conversation
**GET** `/api/conversations/{conversation_id}`

Retrieves a specific conversation with full message history.

**Headers:**
- `X-User-ID: <user_id>` (required)

**Response (200 OK):**
```json
{
  "id": "conversation_id",
  "title": "Learning Python Decorators",
  "owner": {...},
  "created_at": "2025-01-10T14:30:00Z",
  "updated_at": "2025-01-10T14:35:00Z",
  "message_count": 3,
  "messages": [
    {
      "message_id": "msg_1",
      "role": "user",
      "content": "Hello! Can you help me understand Python decorators?",
      "timestamp": "2025-01-10T14:30:00Z"
    },
    {
      "message_id": "msg_2",
      "role": "assistant",
      "content": "I'd be happy to help you understand Python decorators...",
      "timestamp": "2025-01-10T14:30:15Z"
    },
    {
      "message_id": "msg_3",
      "role": "user",
      "content": "Can you give me a simple example?",
      "timestamp": "2025-01-10T14:35:00Z"
    }
  ]
}
```

### 4. Add Message
**POST** `/api/conversations/{conversation_id}/messages`

Adds a user message to the conversation and streams the AI response.

**Headers:**
- `Content-Type: application/json`
- `X-User-ID: <user_id>` (required)

**Request Body:**
```json
{
  "message": "Can you give me a simple example of a decorator?"
}
```

**Response:** Server-Sent Events (SSE) stream

**Stream Format:**
```
data: {"content": "", "message_id": "user_msg_id", "is_complete": false, "error": null, "conversation_id": "conv_id", "message_type": "user_added"}

data: {"content": "Sure! Here's a simple", "is_complete": false, "error": null, "conversation_id": "conv_id"}

data: {"content": " example of a Python decorator:", "is_complete": false, "error": null, "conversation_id": "conv_id"}

data: {"content": "", "message_id": "assistant_msg_id", "is_complete": true, "error": null, "conversation_id": "conv_id"}
```

### 5. Health Check
**GET** `/api/conversations/health`

Checks the health of conversation services.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "conversation_routes",
  "services": {
    "conversation_service": "healthy",
    "openai_service": "healthy"
  },
  "timestamp": "2025-01-10T14:30:00Z"
}
```

## Features

### Auto-Generated Titles
- Initial titles are generated from the first message (truncated to 50 characters)
- Titles are automatically updated using AI after the conversation develops (3+ messages)
- Users cannot manually edit titles (they're always AI-generated)

### Message History
- Complete conversation history is maintained
- Messages include unique IDs, roles (user/assistant), content, and timestamps
- Message history is used for context in subsequent AI responses

### Streaming Responses
- AI responses are streamed in real-time using Server-Sent Events (SSE)
- Responses are saved to the database after streaming completes
- Error handling for failed streams

### User Isolation
- Users can only access their own conversations
- Authentication via `X-User-ID` header (placeholder implementation)
- All operations are scoped to the authenticated user

## Database Schema

### Conversation Model
```python
{
  "_id": ObjectId,
  "title": String (max 200 chars),
  "owner": ObjectId (User reference),
  "messages": [
    {
      "message_id": String,
      "role": "user" | "assistant",
      "content": String,
      "timestamp": DateTime
    }
  ],
  "created_at": DateTime,
  "updated_at": DateTime
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Validation error",
  "details": {
    "initial_message": ["Field is required"]
  }
}
```

### 401 Unauthorized
```json
{
  "error": "Authentication required"
}
```

### 404 Not Found
```json
{
  "error": "Conversation not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "Detailed error message"
}
```

## Testing

Use the provided test script to verify functionality:

```bash
cd backend
python test_conversation_endpoints.py
```

Make sure to:
1. Update `TEST_USER_ID` in the test script with a valid user ID
2. Ensure the server is running on `http://localhost:5000`
3. Have a valid OpenAI API key configured

## Integration Notes

### Authentication
The current implementation uses a simple `X-User-ID` header for authentication. In production, this should be replaced with proper JWT or session-based authentication.

### OpenAI Integration
- Uses the existing `OpenAIService` class
- Leverages GPT-4 for conversation responses
- Includes conversation context in all requests
- Automatic title generation using GPT-3.5-turbo

### Performance Considerations
- Conversation listing excludes message content for better performance
- Message history is loaded only when specifically requested
- Streaming responses provide immediate user feedback
- Database indexes should be added for `owner` and `updated_at` fields

## Future Enhancements

1. **Message Search**: Full-text search across conversation messages
2. **Conversation Sharing**: Share conversations with other users
3. **Export/Import**: Export conversations to various formats
4. **Message Editing**: Allow users to edit their messages
5. **Conversation Folders**: Organize conversations into folders/categories
6. **Usage Analytics**: Track conversation patterns and usage statistics
