# System Patterns

## Architecture Overview

Anthropic Mastery implements a **production-ready layered architecture** with complete conversation system and streaming capabilities, providing the foundation for advanced learning analytics.

```
Frontend (React/TypeScript)
    ↓ HTTP/REST API + Server-Sent Events
Backend (Flask/Python)
    ↓ Anthropic API Integration
    ↓ MongoEngine ODM
Database (MongoDB)
```

### Implemented System Flow
```
User Interface (Conversation.tsx)
    ↓ REST API Calls
Conversation Routes (conversation_routes.py)
    ↓ Service Layer
ConversationService + AnthropicService
    ↓ Data Persistence
Conversation Model (MongoDB)
    ↓ Real-time Streaming
Server-Sent Events → Frontend
```

## Backend Architecture Patterns

### Layered Architecture
The backend implements a clean 4-layer architecture adapted for learning analytics:

1. **Routes Layer** (`routes/`) - HTTP request handling and routing for conversation analysis and learning endpoints
2. **DTO Layer** (`dto/`) - Data Transfer Objects for validation and serialization of learning data
3. **Services Layer** (`services/`) - Business logic for conversation analysis, learning generation, and progress tracking
4. **Models Layer** (`models/`) - Data models for conversations, learning modules, assessments, and user progress

### Implemented Backend Patterns

#### Service Layer Pattern ✅
- **ConversationService**: Business logic for conversation management, message handling, and title generation
- **AnthropicService**: AI integration for streaming Claude responses and conversation analysis
- **Clean Separation**: HTTP concerns isolated from business logic and AI integration

#### Repository Pattern (via MongoEngine) ✅
- **Conversation Model**: Encapsulates conversation and message operations with built-in validation
- **MongoDB Abstraction**: Clean abstraction over MongoDB operations with automatic timestamp management
- **Type Safety**: MongoEngine provides validation and type safety for conversation data

#### DTO Pattern ✅
- **Request Validation**: ConversationCreateRequestDTO and ConversationMessageRequestDTO for input validation
- **Response Serialization**: ConversationResponseDTO and ConversationListResponseDTO for consistent API responses
- **Clear API Contracts**: Marshmallow schemas ensure consistent request/response formats

#### Streaming Pattern ✅
- **Server-Sent Events**: Real-time streaming of Claude responses with proper error handling
- **Event Stream Generation**: Generator functions for efficient streaming with memory management
- **Connection Management**: Proper SSE headers and connection handling for reliable streaming

## Frontend Architecture Patterns

### Implemented Component Architecture ✅
React components organized by conversation and learning functionality:

```
src/
├── components/          # Implemented UI components
│   ├── Conversation.tsx # Complete conversation interface with streaming
│   ├── Sidebar.tsx      # Navigation with conversation history
│   └── ClaudeMastery.tsx # Learning platform homepage
├── App.tsx             # Main application with navigation state management
├── main.tsx            # Application entry point
├── types/              # TypeScript definitions (ready for learning domain extension)
└── assets/             # Static assets and styling
```

### Component Responsibilities ✅
- **Conversation.tsx**: Full-featured chat interface with streaming message display, conversation management, and user input handling
- **Sidebar.tsx**: Navigation component with conversation history, new chat creation, and Claude Mastery access
- **ClaudeMastery.tsx**: Learning platform homepage with feature overview and placeholder learning interfaces
- **App.tsx**: Main application component managing navigation state and component routing

### Implemented State Management Pattern ✅
- **React State**: Component-level state management for conversation data and navigation
- **Callback Pattern**: Proper event handling with callback functions for conversation creation and selection
- **State Lifting**: Shared state managed in App.tsx and passed down to child components
- **Navigation State**: Clean separation between conversation state and navigation state

### Current State Flow ✅
- **Conversation State**: Managed in Conversation.tsx with local state for current conversation and streaming
- **Navigation State**: Managed in App.tsx for current tab (conversation vs mastery) and selected conversation
- **Sidebar State**: Conversation list fetched and managed locally with refresh capabilities
- **Event Handling**: Proper callback patterns for new conversation creation and conversation selection

### Ready for Extension 🚧
- **Learning State**: Architecture ready for learning analytics and progress tracking state
- **Custom Hooks**: Component structure prepared for learning-specific hooks
- **Store Pattern**: Can easily add Zustand stores for learning data when needed

## Data Flow Patterns

### Implemented Conversation Flow ✅
```
User Input (Conversation.tsx)
    ↓ Form Submit
API Call (POST /api/conversations or /api/conversations/{id}/messages)
    ↓ Request Validation
Conversation Routes (conversation_routes.py)
    ↓ Service Layer
ConversationService.create_conversation() or .add_user_message()
    ↓ Database Operation
Conversation.save() (MongoDB)
    ↓ AI Integration
AnthropicService.stream_conversation_response()
    ↓ Streaming Response
Server-Sent Events → Frontend
    ↓ State Update
Conversation Component Re-render
```

### Planned Learning Analytics Flow 🚧
```
Conversation Data (MongoDB)
    ↓ Analysis Request
Learning Analytics Service
    ↓ Pattern Recognition
AI-Powered Conversation Analysis
    ↓ Knowledge Gap Identification
Learning Content Generation
    ↓ Personalized Learning Materials
Learning State Update
    ↓ UI Re-render
Learning Interface Components
```

### Implemented State Synchronization ✅
- **Real-time Updates**: Streaming responses update UI immediately with proper loading states
- **Error Handling**: Comprehensive error handling with user feedback for failed operations
- **Loading States**: Clear indicators during conversation creation, message sending, and streaming
- **Conversation Refresh**: Automatic conversation list refresh when new conversations are created

### Planned Learning State Synchronization 🚧
- **Optimistic Learning Updates**: Progress updates immediately, syncs with backend
- **Learning Content Caching**: Cache generated learning materials for offline access
- **Progress Synchronization**: Real-time sync of learning progress across sessions

## Database Design Patterns

### Implemented Document-Oriented Design ✅
MongoDB collections optimized for conversation storage and ready for learning analytics:

#### Current Entities ✅
- **Conversations**: Complete conversation storage with message arrays, timestamps, and metadata
- **Messages**: Embedded in conversations with role, content, timestamp, and message_id
- **Conversation Metadata**: Title, creation/update timestamps, and message count

#### Implemented Patterns ✅
- **Embedded Pattern**: Messages stored as arrays within conversation documents for efficient retrieval
- **Timestamp Pattern**: Automatic timestamp management for conversations and messages
- **Flexible Schema**: JSON-like document structure ready for learning analytics extension

#### Planned Extensions 🚧
- **Users**: Authentication, profile, and learning preferences
- **LearningModules**: Generated learning content and assessments linked to conversations
- **Assessments**: User progress, proficiency levels, and learning analytics
- **KnowledgeAreas**: Domain expertise mapping and skill progression

#### Future Relationship Patterns 🚧
- **Reference Pattern**: Conversation → User (ownership and privacy)
- **Reference Pattern**: LearningModule → Conversation (source conversation for learning content)
- **Embedded Pattern**: Assessment results embedded in user progress documents
- **Array Pattern**: Knowledge areas and proficiency levels stored as arrays

### Implemented Flexible Data Storage ✅
- **JSON Content**: Conversation data stored as flexible JSON documents with message arrays
- **Temporal Pattern**: Time-series data with created_at and updated_at timestamps for conversation tracking
- **Metadata Storage**: Conversation titles, message counts, and timestamps for efficient querying
- **Extensible Schema**: Document structure ready for learning analytics and progress data

### Planned Learning Data Extensions 🚧
- **Analytics Pattern**: Learning progress and proficiency data in structured JSON
- **Learning Content Storage**: AI-generated flashcards, quizzes, and learning materials
- **Progress Tracking**: Time-series learning progression and conversation pattern analysis
- **Versioning Ready**: Structure supports evolution of learning algorithms and content

## Learning Content Editor Patterns

### Future Learning Content Architecture 🚧
Rich text editing capabilities available for learning content creation:

#### Planned Learning Extensions 🚧
- **Learning Content Creation**: Rich text editor for creating learning materials and explanations
- **Assessment Interfaces**: Interactive quiz and flashcard creation tools
- **Explanation Practice**: Feynman Technique interfaces with rich text support
- **Feedback Systems**: Real-time AI coaching with formatted feedback

#### Future Component Composition 🚧
```
LearningContentEditor (Future Component)
├── Learning Toolbar Components
│   ├── Flashcard Creation Tools
│   ├── Quiz Generation Buttons
│   └── Explanation Practice Tools
├── Learning Extensions
│   ├── Code Example Extensions
│   ├── Concept Explanation Extensions
│   └── Assessment Creation Extensions
└── Learning Theme Components
```

### Current Rich Text Capabilities ✅
- **TipTap Integration**: Available in tech stack for future learning content creation
- **Component Library**: Rich text components ready for learning interface adaptation
- **Extensible Architecture**: Editor system ready for learning-specific extensions

## API Design Patterns

### Implemented RESTful API Design ✅
- **Resource-Based URLs**: `/api/conversations`, `/api/conversations/{id}`, `/api/conversations/{id}/messages`
- **HTTP Method Semantics**: GET, POST for conversation operations with proper status codes
- **Streaming Endpoints**: `/api/conversations/{id}/stream-response` for real-time Claude responses
- **Query Parameters**: Limit and offset for conversation pagination

### Implemented Response Patterns ✅
- **Consistent Structure**: Standard JSON response format for all conversation endpoints
- **Error Handling**: Structured error responses with proper HTTP status codes
- **Streaming Format**: Server-Sent Events with JSON data chunks for real-time responses
- **Metadata Inclusion**: Conversation metadata (title, timestamps, message count) in responses

### Planned Learning API Extensions 🚧
- **Learning Resources**: `/api/learning-modules`, `/api/assessments`, `/api/knowledge-areas`
- **Analysis Endpoints**: `/api/conversations/{id}/analysis`, `/api/users/{id}/learning-progress`
- **Content Generation**: `/api/conversations/{id}/generate-flashcards`, `/api/conversations/{id}/generate-quiz`
- **Progress Tracking**: Structured progress responses with proficiency indicators and learning analytics

## Component Design Patterns

### Implemented Component Composition ✅
- **Primitive Components**: Base UI components with clean separation of concerns
- **Composed Components**: Conversation, Sidebar, and ClaudeMastery components built with clear responsibilities
- **State Management**: React state with proper callback patterns for component communication

### Current Render Patterns ✅
- **Logic Separation**: Business logic separated from rendering in component methods
- **Reusable Patterns**: Common UI patterns (loading states, error handling) consistently implemented
- **Component Simplicity**: Components focus on rendering, with clear data flow and event handling

### Planned Learning Component Patterns 🚧
- **Learning Composed Components**: Learning-specific components built from primitives (flashcards, progress bars, knowledge maps)
- **Learning Context**: Context and state management for learning progress and analytics
- **Learning Logic Separation**: Learning analytics and progress logic in custom hooks
- **Reusable Learning Patterns**: Common learning UI patterns abstracted into hooks

## Error Handling Patterns

### Implemented Backend Error Handling ✅
- **HTTP Status Codes**: Proper status codes (400, 404, 500) for different error types
- **Structured Error Responses**: Consistent JSON error format with error messages and details
- **Validation Errors**: DTO validation with detailed error messages for malformed requests
- **Exception Handling**: Try-catch blocks with proper error logging and user feedback

### Implemented Frontend Error Handling ✅
- **API Error Handling**: Proper error handling for failed API calls with user feedback
- **Loading States**: Clear loading indicators during API operations
- **Error Messages**: User-friendly error messages for conversation operations
- **Graceful Degradation**: Fallback UI states when operations fail

### Planned Learning Error Handling 🚧
- **Learning Exceptions**: Custom exception classes for conversation analysis and learning generation errors
- **Analytics Error Middleware**: Centralized error processing for learning operations
- **Learning Error Boundaries**: React error boundaries for learning component errors
- **Assessment Validation**: DTO validation for learning progress and assessment data

## Security Patterns

### Implemented Input Validation ✅
- **DTO Validation**: Server-side validation for conversation creation and message requests
- **Type Safety**: TypeScript across frontend and backend for conversation data
- **Request Validation**: Marshmallow schemas ensure proper request format and content

### Current Data Access Patterns ✅
- **Conversation Storage**: Secure storage of conversation data in MongoDB
- **Data Integrity**: Proper validation and error handling for data operations
- **API Security**: CORS configuration and proper HTTP methods

### Planned Learning Security Patterns 🚧
- **Privacy Protection**: Users can only access their own conversation and learning data
- **Secure Learning Storage**: Encrypted storage of sensitive learning progress and conversation analysis
- **Learning Audit Trail**: Tracking of learning progress and assessment attempts
- **Data Retention**: Configurable retention policies for conversation and learning data

## Performance Patterns

### Implemented Frontend Optimization ✅
- **Vite Build System**: Fast development builds and hot module replacement
- **Component Optimization**: Efficient re-rendering with proper state management
- **Streaming Updates**: Real-time UI updates without full page refreshes
- **TypeScript Compilation**: Fast type checking and compilation

### Implemented Backend Optimization ✅
- **MongoDB Indexing**: Efficient queries with proper indexing on conversation data
- **Streaming Responses**: Memory-efficient streaming with generator functions
- **Connection Management**: Proper database connection handling and cleanup
- **Pagination**: Efficient pagination for conversation lists

### Planned Learning Performance Patterns 🚧
- **Code Splitting**: Route-based splitting for learning modules and analytics components
- **Lazy Loading**: Component lazy loading for complex learning visualizations and knowledge maps
- **Learning Memoization**: React.memo and useMemo for expensive learning analytics computations
- **Analytics Caching**: Caching of frequently accessed learning analytics and progress data
- **Batch Processing**: Efficient batch processing of conversation analysis and learning content generation

## Development Patterns

### Implemented Type Safety ✅
- **End-to-End Types**: TypeScript interfaces for conversation data and API responses
- **Runtime Validation**: DTO validation with Marshmallow schemas for API requests
- **IDE Support**: Full IntelliSense for conversation types and operations
- **Type Consistency**: Consistent typing across frontend components and backend DTOs

### Current Code Organization ✅
- **Feature Structure**: Code organized by conversation functionality with clear separation
- **Domain Separation**: Clear boundaries between UI components, API routes, and business logic
- **Reusable Components**: Shared conversation interface components and utilities
- **Service Layer**: Clean separation between conversation management and AI integration

### Planned Learning Code Organization 🚧
- **Learning Feature Structure**: Code organized by learning features (analytics, assessments, knowledge mapping)
- **Learning Domain Separation**: Clear boundaries between conversation analysis, learning generation, and progress tracking
- **Reusable Learning Components**: Shared learning interface components and analytics utilities
- **Learning Type System**: Extended TypeScript interfaces for learning data, progress tracking, and conversation analysis
