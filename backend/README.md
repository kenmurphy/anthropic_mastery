# Claude Backend

A Flask-based backend application with MongoDB using a layered architecture.

## Architecture

The application follows a layered architecture pattern:

1. **API Routes** (`routes/`) - Handle HTTP requests and responses
2. **DTO Layer** (`dto/`) - Data Transfer Objects for request/response validation and serialization
3. **Services** (`services/`) - Business logic layer
4. **Models** (`models/`) - MongoEngine models for database interaction

## Project Structure

```
backend/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # MongoDB Docker setup
├── init-mongo.js        # MongoDB initialization script
├── .env                 # Environment variables
├── models/              # MongoEngine models
│   ├── __init__.py
│   ├── user.py
│   └── course.py
├── dto/                 # Data Transfer Objects
│   ├── __init__.py
│   ├── user_dto.py
│   └── course_dto.py
├── services/            # Business logic
│   ├── __init__.py
│   ├── user_service.py
│   └── course_service.py
└── routes/              # API endpoints
    ├── __init__.py
    ├── user_routes.py
    └── course_routes.py
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- Docker and Docker Compose
- pip (Python package manager)

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Start MongoDB with Docker

```bash
docker-compose up -d
```

This will start a MongoDB container with:
- Port: 27017
- Database: claude_db
- Admin user: admin/password123
- App user: claude_user/claude_password

### 3. Configure Environment Variables

The `.env` file is already configured with default values. Modify if needed:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-change-in-production

# MongoDB Configuration
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB=claude_db
MONGODB_USERNAME=claude_user
MONGODB_PASSWORD=claude_password

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=5000
```

### 4. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## API Endpoints

### Health Check
- `GET /health` - Application health check
- `GET /` - Root endpoint with API information

### Users API (`/api/users`)
- `POST /api/users` - Create a new user
- `GET /api/users` - Get paginated list of users
- `GET /api/users/<user_id>` - Get user by ID
- `PUT /api/users/<user_id>` - Update user
- `DELETE /api/users/<user_id>` - Delete user (soft delete)
- `GET /api/users/search?q=<query>` - Search users
- `GET /api/users/email/<email>` - Get user by email
- `GET /api/users/health` - User service health check

### Courses API (`/api/courses`)
- `POST /api/courses` - Create a new course
- `GET /api/courses` - Get paginated list of courses
- `GET /api/courses/<course_id>` - Get course by ID
- `PUT /api/courses/<course_id>` - Update course
- `DELETE /api/courses/<course_id>` - Delete course (soft delete)
- `POST /api/courses/<course_id>/enroll` - Enroll student in course
- `POST /api/courses/<course_id>/unenroll` - Remove student from course
- `GET /api/courses/<course_id>/students` - Get course students
- `GET /api/courses/instructor/<instructor_id>` - Get courses by instructor
- `GET /api/courses/student/<student_id>` - Get courses by student
- `GET /api/courses/search?q=<query>` - Search courses
- `GET /api/courses/health` - Course service health check

## Example API Usage

### Create a User

```bash
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "password": "securepassword"
  }'
```

### Create a Course

```bash
curl -X POST http://localhost:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Introduction to Python",
    "description": "Learn Python programming basics",
    "instructor_id": "<instructor_user_id>",
    "duration_hours": 40
  }'
```

### Enroll Student in Course

```bash
curl -X POST http://localhost:5000/api/courses/<course_id>/enroll \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "<student_user_id>"
  }'
```

## Development

### Running in Development Mode

The application is configured to run in development mode by default with:
- Debug mode enabled
- Auto-reload on file changes
- Detailed error messages

### Database Management

To reset the database:

```bash
docker-compose down -v
docker-compose up -d
```

To view MongoDB data:

```bash
docker exec -it claude_mongodb mongosh -u admin -p password123 --authenticationDatabase admin
```

## Production Considerations

1. **Security**: Change default passwords and secret keys
2. **Environment Variables**: Use production-specific values
3. **Database**: Consider MongoDB Atlas or a managed MongoDB service
4. **Logging**: Implement proper logging
5. **Authentication**: Add JWT or session-based authentication
6. **Rate Limiting**: Implement API rate limiting
7. **Input Validation**: Additional validation beyond DTOs
8. **Error Handling**: More comprehensive error handling
9. **Testing**: Add unit and integration tests
10. **Documentation**: API documentation with Swagger/OpenAPI

## Troubleshooting

### MongoDB Connection Issues

1. Ensure Docker is running
2. Check if MongoDB container is running: `docker ps`
3. Verify MongoDB logs: `docker logs claude_mongodb`
4. Check network connectivity: `docker network ls`

### Application Errors

1. Check Python dependencies are installed
2. Verify environment variables in `.env`
3. Check application logs for detailed error messages
4. Ensure MongoDB is accessible from the application

### Port Conflicts

If port 5000 or 27017 are in use:
1. Change ports in `.env` and `docker-compose.yml`
2. Update any hardcoded references
3. Restart services
