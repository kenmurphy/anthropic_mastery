# Background Clustering System

This document explains the background clustering system that automatically triggers conversation analysis and clustering when new messages are added to conversations.

## Overview

The background clustering system provides automatic, non-blocking analysis of conversations and clustering updates triggered by new message activity. It uses Python threading to perform analysis in the background without impacting the user experience.

## Architecture

### Components

1. **BackgroundClusteringService** - Main service that manages background clustering operations
2. **ConversationService Integration** - Hooks into message creation to trigger analysis
3. **API Endpoints** - REST endpoints for monitoring and controlling background clustering
4. **Configuration** - Environment-based configuration for clustering behavior

### Flow Diagram

```
New Message Created
    ↓
BackgroundClusteringService.trigger_background_analysis()
    ↓
Background Thread Started
    ↓
1. Analyze message (concepts + embeddings)
2. Check clustering trigger conditions
3. If conditions met: Run full clustering
    ↓
Update Database with Results
```

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Background clustering settings
BACKGROUND_CLUSTERING_ENABLED=true
CLUSTERING_MESSAGE_THRESHOLD=1
CLUSTERING_TIME_THRESHOLD_MINUTES=5
```

### Configuration Options

- **BACKGROUND_CLUSTERING_ENABLED**: Enable/disable background clustering (default: true)
- **CLUSTERING_MESSAGE_THRESHOLD**: Number of unprocessed messages to trigger clustering (default: 1)
- **CLUSTERING_TIME_THRESHOLD_MINUTES**: Minutes since last clustering to trigger new run (default: 5)

## Trigger Conditions

Background clustering is triggered when ANY of these conditions are met:

1. **Message Threshold**: 3 or more unprocessed messages exist
2. **Time Threshold**: 30+ minutes since last clustering run
3. **First Run**: No clustering runs exist and there are 2+ messages

## API Endpoints

### Get Background Status
```http
GET /api/clustering/background-status
```

Returns current status of the background clustering service including:
- Whether clustering is enabled
- Current clustering progress
- Unprocessed message count
- Time since last clustering
- Configuration settings

### Force Background Clustering
```http
POST /api/clustering/background-force
```

Manually trigger background clustering immediately, regardless of conditions.

### Trigger Message Analysis
```http
POST /api/messages/{message_id}/trigger-analysis
```

Manually trigger background analysis for a specific message.

## Integration Points

### Automatic Triggers

The system automatically triggers background analysis at these points:

1. **New Conversation Creation**: When `ConversationService.create_conversation()` is called
2. **User Message Addition**: When `ConversationService.add_user_message()` is called  
3. **AI Response Completion**: When streaming AI responses complete in `stream_ai_response()`

### Manual Triggers

You can also manually trigger analysis:

```python
from services.background_clustering_service import BackgroundClusteringService

background_service = BackgroundClusteringService()

# Trigger analysis for a specific message
background_service.trigger_background_analysis(message_id)

# Force clustering to run immediately
background_service.force_clustering()

# Check current status
status = background_service.get_status()
```

## Thread Safety

The system uses threading locks to ensure:
- Only one clustering operation runs at a time
- Singleton pattern for service instance
- Safe concurrent access to clustering status

## Monitoring

### Status Information

The background service provides detailed status information:

```python
{
    "enabled": true,
    "clustering_in_progress": false,
    "unprocessed_messages": 5,
    "minutes_since_last_clustering": 45,
    "should_trigger_clustering": true,
    "trigger_reason": "5 unprocessed messages (threshold: 3)",
    "configuration": {
        "message_threshold": 3,
        "time_threshold_minutes": 30
    },
    "latest_clustering_run": {
        "created_at": "2025-01-10T21:30:00Z",
        "total_conversations": 15,
        "clusters_created": 4
    }
}
```

### Logging

The system provides detailed logging at INFO level:

```
2025-01-10 21:30:00 - BackgroundClusteringService - INFO - Triggered background analysis for message abc123
2025-01-10 21:30:01 - BackgroundClusteringService - INFO - Starting background clustering operation
2025-01-10 21:30:15 - BackgroundClusteringService - INFO - Background clustering completed successfully
```

## Testing

### Test Script

Run the test script to verify the system works:

```bash
cd backend
python test_background_clustering.py
```

This will:
1. Initialize the background service
2. Create test conversations if needed
3. Trigger background analysis
4. Force clustering if conditions are met
5. Display final status and cluster results

### Manual Testing

1. **Create a new conversation** - Should trigger background analysis
2. **Add messages to existing conversations** - Should trigger analysis after threshold
3. **Check API endpoints** - Verify status and force clustering work
4. **Monitor logs** - Confirm background threads are working

## Performance Considerations

### Threading Approach

- Uses daemon threads that die with the main process
- Non-blocking for user interactions
- Simple thread locks prevent concurrent clustering

### Scalability

For production use, consider:
- Moving to Celery for better job management
- Adding Redis for job queuing
- Implementing retry mechanisms
- Adding job monitoring and alerting

### Resource Usage

- Background threads use minimal resources
- Clustering operations are CPU-intensive but infrequent
- Memory usage scales with conversation/message count

## Troubleshooting

### Common Issues

1. **Background clustering not triggering**
   - Check `BACKGROUND_CLUSTERING_ENABLED` setting
   - Verify message threshold and time conditions
   - Check logs for error messages

2. **Clustering fails**
   - Ensure Anthropic API key is configured
   - Check MongoDB connection
   - Verify sufficient conversations exist (2+ required)

3. **Performance issues**
   - Lower message threshold for more frequent clustering
   - Increase time threshold to reduce clustering frequency
   - Monitor thread count and resource usage

### Debug Commands

```python
# Check service status
background_service = BackgroundClusteringService()
print(background_service.get_status())

# Check if clustering is in progress
print(background_service.is_clustering_in_progress())

# Force clustering for testing
background_service.force_clustering()
```

## Future Enhancements

Potential improvements for production:

1. **Job Queue Integration**: Replace threading with Celery/Redis
2. **Retry Mechanisms**: Automatic retry for failed clustering operations
3. **Batch Processing**: Process multiple messages in single clustering run
4. **Smart Scheduling**: Cluster during off-peak hours
5. **Progress Tracking**: Detailed progress reporting for long-running operations
6. **Health Monitoring**: Alerts for failed clustering operations
