# Manual Re-Clustering Scripts

This directory contains scripts to manually trigger conversation clustering in the Anthropic Mastery system.

## Quick Start

### Using the Shell Wrapper (Recommended)
```bash
cd backend

# Show current clustering status
./recluster.sh status

# Run clustering using background service (recommended)
./recluster.sh run

# Run clustering via API (if server is running)
./recluster.sh api

# Reset all clustering data and re-cluster everything
./recluster.sh reset

# Show detailed help
./recluster.sh help
```

### Using the Python Script Directly
```bash
cd backend

# Show current status
python manual_recluster.py --status

# Run clustering (default: background method)
python manual_recluster.py

# Use different methods
python manual_recluster.py --method background
python manual_recluster.py --method api
python manual_recluster.py --method direct

# Reset and re-cluster
python manual_recluster.py --reset

# Show help
python manual_recluster.py --help
```

## Clustering Methods

### 1. Background Service (Recommended)
- **Command**: `./recluster.sh run` or `python manual_recluster.py --method background`
- **Description**: Uses the BackgroundClusteringService to force clustering
- **Advantages**: 
  - Same method used by the automatic system
  - Proper threading and status tracking
  - Can monitor progress and completion
- **Requirements**: None (works offline)

### 2. API Endpoints
- **Command**: `./recluster.sh api` or `python manual_recluster.py --method api`
- **Description**: Triggers clustering via REST API endpoints
- **Advantages**: 
  - Works remotely if server is accessible
  - Uses the same endpoints as the web interface
- **Requirements**: Flask server must be running

### 3. Direct Service
- **Command**: `python manual_recluster.py --method direct`
- **Description**: Calls ConversationClusteringService directly
- **Advantages**: 
  - Bypasses background service layer
  - Immediate execution
- **Requirements**: None (works offline)

### 4. Reset and Re-cluster
- **Command**: `./recluster.sh reset` or `python manual_recluster.py --reset`
- **Description**: Deletes all existing clusters and re-clusters from scratch
- **Advantages**: 
  - Clean slate clustering
  - Useful for testing or after system changes
- **Requirements**: None (works offline)

## Status Information

The status command shows comprehensive information about the clustering system:

```bash
./recluster.sh status
```

This displays:
- **Database Status**: Total conversations, messages, processing progress
- **Background Clustering**: Current status, configuration, trigger conditions
- **Latest Clustering Run**: When it ran, how many clusters were created

## Configuration

The clustering system uses these environment variables (set in `.env`):

```bash
# Enable/disable background clustering
BACKGROUND_CLUSTERING_ENABLED=true

# Number of unprocessed messages to trigger clustering
CLUSTERING_MESSAGE_THRESHOLD=3

# Minutes since last clustering to trigger new run
CLUSTERING_TIME_THRESHOLD_MINUTES=30
```

## Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Make sure you're running from the `backend` directory
   - Ensure all dependencies are installed: `pip install -r requirements.txt`

2. **"API not available" when using API method**
   - Start the Flask server: `python app.py`
   - Check the API URL: `--api-url http://localhost:5000`

3. **Clustering fails**
   - Check your `.env` file has `ANTHROPIC_API_KEY` set
   - Ensure MongoDB is running and accessible
   - Verify you have at least 2 conversations with messages

4. **Permission denied**
   - Make scripts executable: `chmod +x recluster.sh manual_recluster.py`

### Debug Information

For detailed logging, run with Python directly:
```bash
python manual_recluster.py --method background
```

The script provides detailed output including:
- Current clustering status and configuration
- Progress monitoring during clustering
- Final results and cluster information
- Error messages if something goes wrong

### Manual API Testing

You can also test the API endpoints directly:

```bash
# Check clustering status
curl http://localhost:5000/api/clustering/status

# Check background clustering status
curl http://localhost:5000/api/clustering/background-status

# Force background clustering
curl -X POST http://localhost:5000/api/clustering/background-force

# Run direct clustering
curl -X POST http://localhost:5000/api/clustering/run
```

## Integration with Development Workflow

### During Development
- Use `./recluster.sh status` to check current state
- Use `./recluster.sh run` to test clustering after making changes
- Use `./recluster.sh reset` when you need a clean slate

### For Testing
- The `--reset` option is useful for testing clustering algorithms
- The `--status` option helps verify clustering is working correctly
- Different methods help test various code paths

### For Production
- The background service method is recommended for production use
- API method can be used for remote management
- Status monitoring helps track system health

## Files

- **`manual_recluster.py`**: Main Python script with full functionality
- **`recluster.sh`**: Shell wrapper for quick commands
- **`README_manual_clustering.md`**: This documentation file

## Related Documentation

- **`README_background_clustering.md`**: Details about the automatic clustering system
- **`test_background_clustering.py`**: Test script for the clustering system
- **API endpoints**: See `routes/clustering_routes.py` for all available endpoints
