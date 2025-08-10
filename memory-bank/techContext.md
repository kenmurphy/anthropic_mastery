# Technology Context

## Technology Stack

### Backend Technologies

#### Core Framework
- **Flask 2.3.3**: Lightweight Python web framework ideal for learning analytics APIs
- **Python 3.8+**: Programming language with excellent ML/AI library ecosystem
- **Flask-CORS 4.0.0**: Cross-origin resource sharing support for learning interfaces

#### Database & ODM
- **MongoDB**: Document-oriented NoSQL database perfect for flexible conversation and learning data
- **MongoEngine 0.27.0**: Python ODM for MongoDB with excellent support for learning analytics schemas
- **PyMongo 4.5.0**: Low-level MongoDB driver for complex conversation analysis queries

#### Data Validation & Serialization
- **Marshmallow 3.20.1**: Object serialization/deserialization for learning data and progress tracking
- **Marshmallow-MongoEngine 0.30.0**: MongoEngine integration for learning model validation

#### AI & Analytics
- **Anthropic API**: For conversation analysis and learning content generation using Claude models
- **scikit-learn**: For pattern recognition and learning analytics (planned)
- **pandas**: For conversation data analysis and learning metrics (planned)

#### Development & Utilities
- **python-dotenv 1.0.0**: Environment variable management
- **requests 2.31.0**: HTTP library for AI service integration
- **ipdb**: Interactive Python debugger

### Frontend Technologies

#### Core Framework
- **React 19.1.0**: Modern React perfect for interactive learning interfaces
- **TypeScript 5.8.3**: Static type checking essential for learning analytics
- **Vite 6.3.5**: Fast build tool and development server for rapid learning feature development

#### Learning Content & Rich Text
- **@tiptap/react 2.14.1**: React wrapper for TipTap editor (repurposed for learning content creation)
- **@tiptap/starter-kit 2.14.1**: Essential TipTap extensions adaptable for learning interfaces
- **@tiptap/pm 2.14.1**: ProseMirror integration for explanation practice
- **Multiple TipTap Extensions**: Comprehensive editing features adaptable for learning:
  - Highlight, Image, Link for learning content creation
  - Task Item, Task List for learning checklists and progress tracking
  - Typography, Underline for explanation formatting

#### State Management & Data Fetching
- **Zustand 5.0.5**: Lightweight state management perfect for learning progress and analytics
- **@tanstack/react-query 5.80.7**: Server state management for conversation analysis and learning data
- **Axios 1.10.0**: HTTP client for learning analytics API calls

#### UI & Styling
- **Tailwind CSS 4.1.10**: Utility-first CSS framework ideal for learning interface components
- **@tailwindcss/typography 0.5.16**: Typography plugin for learning content display
- **Sass-embedded 1.89.2**: CSS preprocessor for complex learning visualizations
- **@floating-ui/react 0.27.12**: Positioning library for learning tooltips and progress indicators

#### Visualization & Analytics (Future)
- **D3.js**: For knowledge map visualizations and learning progress charts (planned)
- **Chart.js**: For learning analytics dashboards (planned)
- **React Flow**: For interactive knowledge mapping (planned)

#### Form Handling & Routing
- **React Hook Form 7.58.1**: Form state management for assessments and learning preferences
- **React Router DOM 7.6.2**: Client-side routing for learning modules and progress pages

#### Development Tools
- **ESLint 9.25.0**: Code linting
- **TypeScript ESLint 8.30.1**: TypeScript-specific linting
- **Autoprefixer 10.4.21**: CSS vendor prefixing
- **PostCSS 8.5.6**: CSS processing

## Development Environment

### Backend Setup

#### Prerequisites
- Python 3.8 or higher
- Docker and Docker Compose for MongoDB
- pip package manager
- Anthropic API key for conversation analysis and learning content generation

#### Environment Configuration
```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-change-in-production

# MongoDB Configuration
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB=anthropic_mastery_db
MONGODB_USERNAME=mastery_user
MONGODB_PASSWORD=mastery_password

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=5000

# AI Services Configuration
ANTHROPIC_API_KEY=your-anthropic-api-key-here
CONVERSATION_ANALYSIS_MODEL=claude-3-5-sonnet-20241022
LEARNING_GENERATION_MODEL=claude-3-haiku-20240307
```

#### Database Setup
- **MongoDB via Docker**: Containerized database setup optimized for conversation and learning data
- **Initialization Script**: `init-mongo.js` adapted for learning platform setup
- **User Management**: Admin and application users configured for learning platform
- **Learning Data Indexes**: Optimized indexes for conversation analysis and learning queries

### Frontend Setup

#### Development Server
- **Vite Dev Server**: Hot module replacement and fast builds for learning interface development
- **TypeScript Compilation**: Real-time type checking for learning analytics and progress tracking
- **ESLint Integration**: Code quality enforcement for learning-focused components

#### Build Configuration
- **Vite Config**: Optimized for React and TypeScript with learning visualization support
- **Tailwind Config**: Custom design system for learning interfaces and progress visualization
- **PostCSS Config**: CSS processing pipeline for learning component styling
- **TypeScript Config**: Strict type checking enabled for learning domain types

## Architecture Decisions

### Backend Architecture Choices

#### Flask over Django
- **Lightweight**: Minimal overhead perfect for learning analytics APIs
- **Flexibility**: Easy to structure for conversation analysis and learning generation
- **AI Integration**: Simple integration with ML/AI libraries for conversation analysis
- **Microservice Ready**: Can be split into conversation analysis and learning generation services

#### MongoDB over SQL
- **Document Structure**: Perfect fit for flexible conversation data and learning content
- **JSON Storage**: Native JSON support for conversation history and learning analytics
- **Schema Flexibility**: Easy evolution of learning algorithms and data structures
- **Analytics Performance**: Excellent for time-series learning progress data and conversation analysis

#### MongoEngine ODM
- **Pythonic Interface**: Clean model definitions for learning domain entities
- **Validation**: Built-in validation for learning progress and conversation data
- **Relationship Management**: Easy handling of user-conversation-learning relationships
- **Analytics Queries**: Efficient querying for learning analytics and progress tracking

### Frontend Architecture Choices

#### React with TypeScript
- **Type Safety**: Essential for complex learning analytics and progress tracking
- **Developer Experience**: Excellent IDE support for learning domain development
- **Component Architecture**: Perfect for modular learning interfaces and knowledge visualization
- **Ecosystem**: Rich ecosystem including visualization libraries for learning analytics

#### Vite over Create React App
- **Performance**: Faster development builds crucial for iterative learning interface development
- **Modern Tooling**: Native ES modules perfect for learning component libraries
- **Flexibility**: Easy configuration for learning visualization and analytics tools

#### Zustand over Redux
- **Simplicity**: Less boilerplate ideal for learning progress and analytics state
- **TypeScript Support**: Excellent integration for learning domain types
- **Performance**: Minimal re-renders crucial for real-time learning progress updates
- **Bundle Size**: Smaller footprint important for learning interface performance

#### TipTap over Other Editors
- **Extensibility**: Perfect for custom learning content creation and explanation practice
- **Modern Architecture**: Ideal foundation for Feynman Technique interfaces
- **Customization**: Full control for learning-specific editor behaviors
- **TypeScript Support**: Essential for learning content type safety

## Development Workflow

### Backend Development (Learning-Focused)
1. **Virtual Environment**: Python virtual environment with ML/AI libraries for conversation analysis
2. **Docker Compose**: MongoDB container optimized for learning and conversation data
3. **Environment Variables**: `.env` file including AI service configurations
4. **Hot Reloading**: Flask debug mode for rapid learning feature development

### Frontend Development (Learning Interface)
1. **Package Management**: npm/yarn for learning interface dependencies
2. **Development Server**: Vite dev server optimized for learning component development
3. **Type Checking**: Real-time TypeScript compilation for learning domain types
4. **Linting**: ESLint integration focused on learning interface code quality

### Code Quality (Learning Domain)
- **Type Safety**: TypeScript essential for learning analytics and progress tracking
- **Linting**: ESLint with rules adapted for learning interface development
- **Code Formatting**: Consistent style for learning component libraries
- **Git Hooks**: Quality gates for learning feature commits

## Deployment Considerations

### Backend Deployment (Learning Platform)
- **WSGI Server**: Gunicorn or uWSGI for production learning analytics APIs
- **Environment Variables**: Production configuration including AI service keys
- **Database**: MongoDB Atlas optimized for conversation and learning data
- **Security**: HTTPS, CORS, input validation, and secure conversation data handling
- **AI Services**: Secure integration with Anthropic and other ML services

### Frontend Deployment (Learning Interface)
- **Static Hosting**: CDN deployment optimized for learning interface assets
- **Environment Variables**: Build-time configuration for learning analytics endpoints
- **Code Splitting**: Optimized bundle splitting for learning modules and visualizations
- **Caching**: Proper cache headers for learning content and progress data

## Performance Considerations

### Backend Performance (Learning Analytics)
- **Conversation Indexing**: Indexes optimized for conversation pattern analysis
- **Learning Pagination**: Efficient pagination for large learning datasets
- **Analytics Caching**: Redis for learning progress and conversation analysis caching
- **Batch Processing**: Efficient batch processing for conversation analysis and learning generation
- **AI Service Optimization**: Caching and rate limiting for AI-powered learning content generation

### Frontend Performance (Learning Interface)
- **Learning Module Splitting**: Route-based splitting for different learning interfaces
- **Visualization Lazy Loading**: Deferred loading of complex knowledge maps and analytics charts
- **Learning Memoization**: React.memo and useMemo for expensive learning analytics computations
- **Bundle Optimization**: Tree shaking optimized for learning interface libraries

## Security Considerations

### Backend Security (Learning Platform)
- **Learning Data Validation**: DTO validation for conversation and learning data
- **CORS Configuration**: Secure cross-origin handling for learning interfaces
- **Conversation Privacy**: Encrypted storage and secure handling of conversation history
- **AI Service Security**: Secure API key management for conversation analysis services
- **Data Retention**: Configurable retention policies for sensitive conversation data

### Frontend Security (Learning Interface)
- **Content Sanitization**: Secure handling of user conversation data and learning content
- **HTTPS**: Secure communication for learning analytics and progress data
- **Privacy Protection**: Secure handling of learning progress and conversation insights
- **Content Security Policy**: CSP headers for learning interface protection

## Monitoring and Debugging

### Development Tools (Learning-Focused)
- **Browser DevTools**: React DevTools for learning component debugging and learning analytics inspection
- **Python Debugger**: ipdb for conversation analysis and learning generation debugging
- **MongoDB Compass**: Database inspection for conversation and learning data
- **Postman/Insomnia**: API testing for learning analytics and conversation analysis endpoints

### Logging and Monitoring (Learning Analytics)
- **Flask Logging**: Structured logging for conversation analysis and learning operations
- **Learning Analytics Logging**: Detailed logging of learning progress and assessment results
- **Database Monitoring**: MongoDB performance monitoring for conversation and learning queries
- **AI Service Monitoring**: Tracking of conversation analysis and learning generation performance
- **Error Tracking**: Specialized error reporting for learning operations and conversation analysis
