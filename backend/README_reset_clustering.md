# Reset Clustering Status Script

## Overview

The `reset_clustering_status.py` script resets the `processed_for_clustering` field to `False` for all Message models in the MongoDB database. This is useful when you want to reprocess all messages for clustering analysis.

## Usage

```bash
cd backend
python reset_clustering_status.py
```

## What it does

1. **Connects to MongoDB** using the same configuration as the main application
2. **Shows current status** of message processing (total, processed, unprocessed)
3. **Asks for confirmation** before making changes
4. **Performs bulk update** to set `processed_for_clustering = False` for all messages
5. **Reports results** showing how many documents were updated
6. **Shows final status** after the operation

## Example Output

```
============================================================
🔄 Message Clustering Status Reset Script
============================================================
✅ Connected to MongoDB database: claude_db

📊 Current Status:
   Total messages: 16
   Processed for clustering: 8
   Unprocessed: 0

⚠️  This will reset the 'processed_for_clustering' field to False
   for ALL 16 message documents.

❓ Do you want to continue? (y/N): y
🔄 Resetting clustering status for all messages...
✅ Successfully updated 16 message documents

✅ Reset complete!
   Updated 16 message documents
   All messages are now marked as unprocessed for clustering

📊 Final Status:
   Total messages: 16
   Processed for clustering: 0
   Unprocessed: 16

🔌 Disconnected from database
```

## Safety Features

- **Confirmation prompt**: The script asks for user confirmation before making changes
- **Status reporting**: Shows before and after statistics
- **Error handling**: Gracefully handles database connection errors and other issues
- **Idempotent**: Safe to run multiple times
- **Non-destructive**: Only updates the `processed_for_clustering` field, doesn't delete data

## When to Use

- When you want to rerun clustering analysis on all messages
- After updating clustering algorithms or parameters
- When troubleshooting clustering issues
- During development and testing of clustering features

## Requirements

- Python 3.x
- MongoDB running and accessible
- Same environment variables as the main application (.env file)
- Required Python packages (mongoengine, python-dotenv)
