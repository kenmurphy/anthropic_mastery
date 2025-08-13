# Anthropic Mastery: Technical Documentation

## Technical Approach Overview

### Tech Stack

- **backend/**: Layered architecture using Flask (Python) with MongoDB.
- **frontend/**: React with TypeScript

### Anthropic Integration with Streaming

- **Real-time Claude Integration**: Server-Sent Events (SSE) for streaming responses
- **Conversation Management**: Complete chat interface with persistent message history
- **API Architecture**: RESTful endpoints with streaming support for seamless user experience
- **Memory-Efficient Streaming**: Generator functions for optimal performance during long conversations

### K-Means Clustering Implementation

- **Conversation Intelligence**: AI-powered clustering of user conversations into thematic projects
- **Pattern Recognition**: Identifies repeated questions and knowledge gaps from conversation history
- **Learning Analytics Foundation**: Clusters conversations to generate personalized learning content
- **Two-Phase Analysis**:
  - Semantic clustering of conversation topics
  - Knowledge gap detection for targeted learning interventions

## Architecture

The application follows a layered architecture:

```
Frontend (React/TypeScript)
    ↓ HTTP/REST API + Server-Sent Events
Backend (Flask/Python)
    ↓ Anthropic API Integration
    ↓ MongoEngine ODM
Database (MongoDB)
```

### Backend Layers

1. **Routes Layer** (`routes/`) - HTTP request handling and streaming endpoints
2. **DTO Layer** (`dto/`) - Data Transfer Objects for validation and serialization
3. **Services Layer** (`services/`) - Business logic for conversation analysis and AI integration
4. **Models Layer** (`models/`) - Data models for conversations, messages, and learning analytics

## Project Structure

```
backend/
├── app.py                              # Main Flask application
├── config.py                          # Configuration settings
├── requirements.txt                    # Python dependencies
├── docker-compose.yml                  # MongoDB Docker setup
├── init-mongo.js                      # MongoDB initialization script
├── .env                               # Environment variables
├── models/                            # MongoEngine models
│   ├── __init__.py
│   ├── conversation.py                # Conversation metadata model
│   ├── message.py                     # Individual message model with semantic analysis
│   └── cluster.py                     # Conversation clustering models
├── dto/                               # Data Transfer Objects
│   ├── __init__.py
│   ├── conversation_dto.py            # Conversation request/response DTOs
│   └── ai_dto.py                      # AI service DTOs
├── services/                          # Business logic services
│   ├── __init__.py
│   ├── conversation_service.py        # Core conversation management
│   ├── anthropic_service.py           # Claude API integration
│   ├── message_analysis_service.py    # Technical concept extraction
│   ├── conversation_clustering_service.py  # Semantic clustering
│   └── background_clustering_service.py    # Background analysis triggers
├── routes/                            # API endpoints
│   ├── __init__.py
│   ├── conversation_routes.py         # Conversation CRUD and streaming
│   └── clustering_routes.py           # Learning analytics endpoints
├── test_*.py                          # Comprehensive test suite
├── manual_recluster.py                # Manual clustering operations
├── recluster.sh                       # Clustering automation script
└── README_*.md                        # Feature-specific documentation
```

## Technology Stack

### Core Technologies

- **Flask 2.3.3**: Production-ready Python web framework
- **MongoDB**: Document-oriented database for flexible conversation storage
- **MongoEngine 0.27.0**: Python ODM with built-in validation
- **Anthropic API**: Claude integration for AI conversations
- **Server-Sent Events**: Real-time streaming responses

### AI & Analytics

- **Anthropic Claude**: Conversation responses and analysis
- **Semantic Embeddings**: 1024-dimensional vectors for conversation clustering
- **Technical Concept Extraction**: AI-powered analysis of conversation content
- **Background Processing**: Asynchronous analysis and clustering

### Data Validation & Serialization

- **Marshmallow 3.20.1**: Request/response validation and serialization
- **Marshmallow-MongoEngine**: MongoDB integration for data validation

## Setup Instructions

### Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Anthropic API key

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Start MongoDB with Docker

```bash
docker-compose up -d
```

This starts MongoDB with:

- Port: 27017
- Database: claude_db
- Admin user: admin/password123
- App user: mastery_user/mastery_password

### 3. Configure Environment Variables

Create or update `.env` file:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-change-in-production

# MongoDB Configuration
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB=claude_db
MONGODB_USERNAME=mastery_user
MONGODB_PASSWORD=mastery_password

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=10000

# AI Services Configuration
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

### 4. Run the Application

```bash
python app.py
```

The application starts on `http://localhost:10000`

## API Endpoints

### Health Check

- `GET /health` - Application health check
- `GET /` - Root endpoint with API information

### Conversations API (`/api/conversations`)

#### Core Conversation Operations

- `POST /api/conversations` - Create new conversation with initial message
- `GET /api/conversations` - Get paginated list of conversations
- `GET /api/conversations/<id>` - Get conversation with full message history
- `POST /api/conversations/<id>/messages` - Add message and stream AI response
- `POST /api/conversations/<id>/stream-response` - Stream AI response for existing conversation

#### Streaming Responses

All AI responses use Server-Sent Events (SSE) for real-time streaming:

- Content-Type: `text/event-stream`
- Real-time message chunks with completion status
- Automatic conversation title generation
- Background analysis triggering

### Learning Analytics API (`/api/clustering`)

#### Conversation Analysis

- `GET /api/clustering/conversations/<id>/analysis` - Get conversation analysis results
- `GET /api/clustering/conversations/<id>/cluster` - Get conversation cluster information
- `GET /api/clustering/conversations/<id>/similar` - Find similar conversations

#### Clustering Operations

- `POST /api/clustering/trigger-clustering` - Trigger manual clustering operation
- `GET /api/clustering/clusters` - Get all conversation clusters
- `GET /api/clustering/clusters/<cluster_id>` - Get specific cluster details
- `GET /api/clustering/status` - Get clustering system status

## Data Models

### Conversation Model

```python
class Conversation(Document):
    title = StringField(required=True, max_length=200)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    # Methods for message management and AI integration
    def add_message(speaker, content) -> str
    def get_messages() -> List[Message]
    def get_message_history() -> List[Dict]  # For AI API
```

### Message Model

```python
class Message(Document):
    conversation_id = StringField(required=True)
    message_id = StringField(required=True, unique=True)
    speaker = StringField(choices=['user', 'assistant'])
    content = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)

    # Semantic analysis fields
    technical_concepts = ListField(StringField())
    embedding = ListField(FloatField())  # 1024-dim vector
    processed_for_clustering = BooleanField(default=False)
```

### Conversation Cluster Model

```python
class ConversationCluster(Document):
    cluster_id = StringField(required=True, unique=True)
    label = StringField(required=True)  # "Database Design & Optimization"
    description = StringField(required=True)  # 2-sentence summary
    conversation_ids = ListField(StringField())
    key_concepts = ListField(StringField())
    centroid = ListField(FloatField())  # Cluster center vector
```

## Example API Usage

### Create a Conversation

```bash
curl -X POST http://localhost:10000/api/conversations \
  -H "Content-Type: application/json" \
  -d '{
    "initial_message": "How do I optimize a SQL query with multiple joins?",
    "title": "SQL Query Optimization"
  }'
```

### Stream AI Response

```bash
curl -X POST http://localhost:10000/api/conversations/<id>/stream-response \
  -H "Accept: text/event-stream"
```

### Add Message and Stream Response

```bash
curl -X POST http://localhost:10000/api/conversations/<id>/messages \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Can you explain the difference between INNER and LEFT JOIN?"
  }'
```

### Get Conversation Analysis

```bash
curl -X GET http://localhost:10000/api/clustering/conversations/<id>/analysis
```

## Learning Analytics Features

### Semantic Clustering

- **Automatic Grouping**: Conversations clustered by technical concepts and themes
- **Background Processing**: Real-time analysis triggered on message creation
- **Concept Extraction**: AI-powered identification of technical concepts
- **Similarity Detection**: Find related conversations and learning patterns

### Technical Concept Analysis

- **Concept Extraction**: Identify technical terms, frameworks, and methodologies
- **Embedding Generation**: 1024-dimensional vectors for semantic similarity
- **Pattern Recognition**: Detect repeated questions and knowledge gaps
- **Learning Opportunities**: Identify areas for skill development

### Conversation Intelligence

- **Cluster Analysis**: Group conversations into thematic learning areas
- **Dependency Mapping**: Track concepts users consistently ask about
- **Progress Tracking**: Monitor learning progression over time
- **Knowledge Gap Detection**: Identify areas needing improvement

## Development Features

### Testing Suite

- `test_conversation_endpoints.py` - API endpoint testing
- `test_semantic_clustering.py` - Clustering algorithm testing
- `test_background_clustering.py` - Background processing testing
- `test_anthropic_integration.py` - AI service integration testing
- `test_full_conversation_flow.py` - End-to-end conversation testing

### Development Tools

- `manual_recluster.py` - Manual clustering operations for development
- `recluster.sh` - Automated clustering script
- `clear_*.py` - Database cleanup utilities
- `restart_and_test.py` - Development workflow automation

### Background Processing

- **Asynchronous Analysis**: Non-blocking conversation analysis
- **Clustering Triggers**: Automatic clustering on conversation completion
- **Concept Extraction**: Real-time technical concept identification
- **Learning Analytics**: Background generation of learning insights

## Production Considerations

### Security

- **Input Validation**: Comprehensive DTO validation for all endpoints
- **API Key Management**: Secure Anthropic API key handling
- **CORS Configuration**: Proper cross-origin resource sharing setup
- **Error Handling**: Structured error responses with proper HTTP status codes

### Performance

- **MongoDB Indexing**: Optimized indexes for conversation and message queries
- **Streaming Responses**: Memory-efficient SSE implementation
- **Background Processing**: Non-blocking analysis and clustering
- **Connection Management**: Proper database connection handling

### Scalability

- **Document Storage**: Flexible MongoDB schema for conversation data
- **Service Architecture**: Modular services ready for microservice deployment
- **Clustering Optimization**: Efficient semantic clustering algorithms
- **API Design**: RESTful endpoints with proper pagination and filtering

### Monitoring

- **Health Endpoints**: Service health monitoring for all components
- **Logging**: Comprehensive logging for conversation operations and analysis
- **Error Tracking**: Detailed error handling and reporting
- **Performance Metrics**: Clustering performance and analysis timing

## Learning Platform Integration

This backend serves as the foundation for the Anthropic Mastery learning platform:

### Current Capabilities ✅

- **Complete Conversation System**: Full CRUD operations with streaming AI responses
- **Semantic Analysis**: Technical concept extraction and conversation clustering
- **Background Processing**: Asynchronous analysis and learning insight generation
- **Learning Analytics API**: Endpoints for conversation analysis and cluster information

### Planned Learning Features 🚧

- **Knowledge Gap Detection**: Advanced pattern recognition for learning opportunities
- **Learning Content Generation**: AI-powered creation of flashcards and quizzes
- **Progress Tracking**: User proficiency assessment and learning journey mapping
- **Adaptive Learning Paths**: Personalized learning recommendations based on conversation patterns

## Troubleshooting

### MongoDB Connection Issues

1. Ensure Docker is running: `docker ps`
2. Check MongoDB container: `docker logs anthropic_mastery_mongodb`
3. Verify network connectivity: `docker network ls`
4. Test connection: `python test_mongodb_connection.py`

### Anthropic API Issues

1. Verify API key in `.env` file
2. Test integration: `python test_anthropic_integration.py`
3. Check API rate limits and usage
4. Verify network connectivity to Anthropic services

### Clustering Issues

1. Check clustering status: `GET /api/clustering/status`
2. Trigger manual clustering: `python manual_recluster.py`
3. Verify message analysis: `python test_semantic_clustering.py`
4. Check background processing logs

### Application Errors

1. Check Python dependencies: `pip install -r requirements.txt`
2. Verify environment variables in `.env`
3. Run health checks: `GET /health`
4. Check application logs for detailed error messages

The Anthropic Mastery backend provides a robust foundation for conversation analysis and learning analytics, designed to scale from individual learning sessions to comprehensive knowledge mapping and skill development tracking.
