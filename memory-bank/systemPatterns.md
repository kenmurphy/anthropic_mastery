# System Patterns

## Architecture Overview

Anthropic Mastery follows a **layered architecture** pattern with clear separation between frontend and backend, implementing modern full-stack development practices optimized for conversation analysis and learning experiences.

```
Frontend (React/TypeScript)
    ↓ HTTP/REST API
Backend (Flask/Python)
    ↓ ODM/ORM
Database (MongoDB)
```

## Backend Architecture Patterns

### Layered Architecture
The backend implements a clean 4-layer architecture adapted for learning analytics:

1. **Routes Layer** (`routes/`) - HTTP request handling and routing for conversation analysis and learning endpoints
2. **DTO Layer** (`dto/`) - Data Transfer Objects for validation and serialization of learning data
3. **Services Layer** (`services/`) - Business logic for conversation analysis, learning generation, and progress tracking
4. **Models Layer** (`models/`) - Data models for conversations, learning modules, assessments, and user progress

### Key Backend Patterns

#### Repository Pattern (via MongoEngine)
- Models encapsulate conversation and learning data operations
- Clean abstraction over MongoDB operations for complex learning analytics
- Built-in validation and type safety for learning progress tracking

#### DTO Pattern
- Request/response validation for conversation analysis and learning content
- Clear API contracts for learning analytics and progress tracking
- Separation of internal learning models from external interfaces

#### Service Layer Pattern
- Conversation analysis and learning generation logic isolated from HTTP concerns
- Reusable learning analytics and assessment operations
- Progress tracking and learning path management

## Frontend Architecture Patterns

### Component-Based Architecture
React components organized by learning features and functionality:

```
src/
├── components/          # Reusable UI components
│   ├── learning/        # Learning interface components (flashcards, quizzes)
│   ├── knowledge-map/   # Knowledge visualization components
│   ├── analytics/       # Progress tracking and analytics components
│   ├── conversations/   # Conversation analysis and display components
│   ├── tiptap-*        # Rich text editor components (repurposed for learning content)
│   └── tiptap-ui/      # Editor UI primitives (adaptable for learning interfaces)
├── pages/              # Route-level components (Knowledge Map, Flashcards, etc.)
├── hooks/              # Custom React hooks for learning analytics and progress
├── store/              # State management for learning data and user progress
├── types/              # TypeScript definitions for learning domain
└── utils/              # Utility functions for conversation analysis and learning
```

### State Management Pattern (Zustand)
- **Single Store per Domain**: `learningStore.ts` manages learning progress and analytics, `conversationStore.ts` manages conversation data
- **Selector Pattern**: Exported selectors for learning progress, proficiency levels, and conversation insights
- **Action-Based Updates**: Clear action methods for updating learning progress and assessment results
- **Immutable Updates**: State updates follow immutability patterns for learning analytics

### Custom Hooks Pattern
- **Domain-Specific Hooks**: `useLearning.ts` for learning operations, `useConversations.ts` for conversation analysis
- **Analytics Hooks**: `useProgress.ts` for progress tracking, `useProficiency.ts` for skill assessment
- **UI Hooks**: `use-cursor-visibility.ts`, `use-mobile.ts` for UI concerns (maintained)
- **Learning Interface Hooks**: `use-flashcards.ts`, `use-knowledge-map.ts` for learning components

## Data Flow Patterns

### Learning Analytics Flow
```
Learning Component
    ↓ Learning Action
Learning Store
    ↓ API Call
Conversation Analysis Route
    ↓ DTO Validation
Learning Service
    ↓ Pattern Recognition & Content Generation
Learning Models/Database
    ↓ Response
Learning DTO Serialization
    ↓ JSON Response
Learning State Update
    ↓ Re-render
Learning UI Update
```

### Conversation Analysis Flow
```
Conversation Import
    ↓ Analysis Request
Conversation Store
    ↓ API Call
Analysis Route
    ↓ Pattern Recognition
AI Service
    ↓ Knowledge Gap Identification
Learning Content Generation
    ↓ Personalized Learning Materials
Learning State Update
```

### State Synchronization
- **Optimistic Learning Updates**: Progress updates immediately, syncs with backend
- **Error Handling**: Rollback on learning operation failures
- **Loading States**: Clear indicators during conversation analysis and content generation

## Database Design Patterns

### Document-Oriented Design
MongoDB collections optimized for conversation analysis and learning data:

#### Core Entities
- **Users**: Authentication, profile, and learning preferences
- **Conversations**: AI interaction history and analysis results
- **LearningModules**: Generated learning content and assessments
- **Assessments**: User progress, proficiency levels, and learning analytics
- **KnowledgeAreas**: Domain expertise mapping and skill progression

#### Relationship Patterns
- **Reference Pattern**: Conversation → User (ownership and privacy)
- **Reference Pattern**: LearningModule → User (personalized content)
- **Embedded Pattern**: Assessment results embedded in user progress documents
- **Array Pattern**: Knowledge areas and proficiency levels stored as arrays

### Flexible Learning Data Storage
- **JSON Content**: Conversation data and learning content stored as flexible JSON documents
- **Analytics Pattern**: Learning progress and proficiency data in structured JSON
- **Temporal Pattern**: Time-series data for learning progression and conversation patterns
- **Versioning Ready**: Structure supports evolution of learning algorithms and content

## Learning Content Editor Patterns

### TipTap Extension Architecture (Repurposed for Learning)
Modular editor adapted for learning content creation and explanation practice:

#### Extension Categories
- **Learning Node Extensions**: Custom content types for learning materials (code examples, explanations)
- **Assessment Extensions**: Interactive quiz and flashcard components
- **Explanation Extensions**: Feynman Technique practice interfaces
- **Feedback Extensions**: Real-time AI coaching and correction

#### Component Composition Pattern
```
LearningEditor (Main Component)
├── Learning Toolbar Components
│   ├── Assessment Creation Buttons
│   ├── Explanation Tools
│   └── Feedback Interfaces
├── Learning Extensions
│   ├── Quiz Node Extensions
│   ├── Flashcard Extensions
│   └── Explanation Behavior Extensions
└── Learning Theme Components
```

### Learning Content State Management
- **Learning Editor Instance**: Managed through custom learning hooks
- **Content Synchronization**: Learning content synced with learning store
- **Assessment Pattern**: Learning actions implemented as assessment commands

## API Design Patterns

### RESTful Learning Resource Design
- **Resource-Based URLs**: `/api/conversations`, `/api/learning-modules`, `/api/assessments`
- **HTTP Method Semantics**: GET, POST, PUT, DELETE for learning operations
- **Nested Resources**: `/api/users/{id}/learning-progress`, `/api/conversations/{id}/analysis`
- **Query Parameters**: Filtering by proficiency level, time range, knowledge area

### Learning Analytics Response Patterns
- **Consistent Structure**: Standard response format for learning data and analytics
- **Progress Tracking**: Structured progress responses with proficiency indicators
- **Learning Content**: Standardized format for generated learning materials
- **Analytics Data**: Consistent format for learning effectiveness metrics

## Component Design Patterns

### Composition over Inheritance (Adapted for Learning)
- **Primitive Components**: Base UI components adaptable for learning interfaces
- **Learning Composed Components**: Learning-specific components built from primitives (flashcards, progress bars, knowledge maps)
- **Learning Context**: Context and state management for learning progress and analytics

### Learning-Focused Render Patterns
- **Learning Logic Separation**: Learning analytics and progress logic in custom hooks
- **Reusable Learning Patterns**: Common learning UI patterns abstracted into hooks
- **Component Simplicity**: Learning components focus on rendering, hooks handle learning logic

## Error Handling Patterns

### Backend Error Handling (Learning-Focused)
- **Learning Exceptions**: Custom exception classes for conversation analysis and learning generation errors
- **Analytics Error Middleware**: Centralized error processing for learning operations
- **Assessment Validation**: DTO validation for learning progress and assessment data

### Frontend Error Handling (Learning Context)
- **Learning Error Boundaries**: React error boundaries for learning component errors
- **Learning State Errors**: Error state in learning and conversation stores
- **Learning Feedback**: Clear error messages for learning operations and progress tracking

## Security Patterns

### Input Validation (Learning Data)
- **Learning DTO Validation**: Server-side validation for conversation data and learning content
- **Type Safety**: TypeScript for learning analytics and progress data
- **Content Sanitization**: Sanitization of user conversation data and learning content

### Learning Data Access Patterns
- **Privacy Protection**: Users can only access their own conversation and learning data
- **Secure Conversation Storage**: Encrypted storage of sensitive conversation history
- **Learning Audit Trail**: Tracking of learning progress and assessment attempts
- **Data Retention**: Configurable retention policies for conversation and learning data

## Performance Patterns

### Frontend Optimization (Learning-Focused)
- **Code Splitting**: Route-based splitting for learning modules and analytics components
- **Lazy Loading**: Component lazy loading for complex learning visualizations and knowledge maps
- **Learning Memoization**: React.memo and useMemo for expensive learning analytics computations

### Backend Optimization (Learning Analytics)
- **Conversation Indexing**: Indexes on conversation patterns and user learning data
- **Learning Pagination**: Efficient pagination for large conversation datasets and learning history
- **Analytics Caching**: Caching of frequently accessed learning analytics and progress data
- **Batch Processing**: Efficient batch processing of conversation analysis and learning content generation

## Development Patterns

### Type Safety (Learning Domain)
- **End-to-End Learning Types**: Shared TypeScript interfaces for learning data, progress tracking, and conversation analysis
- **Learning Runtime Validation**: DTO validation for learning operations and analytics
- **Learning IDE Support**: Full IntelliSense for learning domain types and operations

### Code Organization (Learning-Focused)
- **Learning Feature Structure**: Code organized by learning features (analytics, assessments, knowledge mapping)
- **Learning Domain Separation**: Clear boundaries between conversation analysis, learning generation, and progress tracking
- **Reusable Learning Components**: Shared learning interface components and analytics utilities
