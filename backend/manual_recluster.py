#!/usr/bin/env python3
"""
Manual Re-Cluster Script for Anthropic Mastery

This script provides multiple ways to manually trigger conversation clustering:
1. Force immediate clustering via BackgroundClusteringService
2. Trigger clustering via API endpoints (if server is running)
3. Direct clustering service execution
4. Reset and re-cluster all conversations

Usage:
    python manual_recluster.py [options]

Options:
    --method [background|api|direct|reset]  Choose clustering method (default: background)
    --api-url [url]                        API base URL (default: http://localhost:5000)
    --reset                                Reset all clustering data before re-clustering
    --status                               Show clustering status only
    --help                                 Show this help message

Examples:
    python manual_recluster.py                    # Use background service (recommended)
    python manual_recluster.py --method api       # Use API endpoints
    python manual_recluster.py --method direct    # Direct service call
    python manual_recluster.py --reset            # Reset and re-cluster everything
    python manual_recluster.py --status           # Show current status
"""

import sys
import argparse
import logging
import requests
import time
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Setup the environment for running clustering services"""
    try:
        # Import required services
        from services.background_clustering_service import BackgroundClusteringService
        from services.conversation_clustering_service import ConversationClusteringService
        from models.conversation import Conversation
        from models.message import Message
        from models.cluster import ConversationCluster, ClusteringRun
        
        return {
            'background_service': BackgroundClusteringService(),
            'clustering_service': ConversationClusteringService(),
            'models': {
                'Conversation': Conversation,
                'Message': Message,
                'ConversationCluster': ConversationCluster,
                'ClusteringRun': ClusteringRun
            }
        }
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        logger.error("Make sure you're running this script from the backend directory")
        sys.exit(1)

def show_status(services=None):
    """Show current clustering status"""
    print("\n" + "="*60)
    print("CLUSTERING STATUS")
    print("="*60)
    
    if services:
        # Use direct service calls
        try:
            background_service = services['background_service']
            models = services['models']
            
            # Get background service status
            bg_status = background_service.get_status()
            
            # Get database counts
            total_conversations = models['Conversation'].objects.count()
            total_messages = models['Message'].objects.count()
            processed_messages = models['Message'].objects(processed_for_clustering=True).count()
            total_clusters = models['ConversationCluster'].objects.count()
            latest_run = models['ClusteringRun'].objects.order_by('-created_at').first()
            
            print(f"Database Status:")
            print(f"  Total Conversations: {total_conversations}")
            print(f"  Total Messages: {total_messages}")
            print(f"  Processed Messages: {processed_messages}")
            print(f"  Processing Progress: {processed_messages}/{total_messages} ({processed_messages/max(total_messages,1)*100:.1f}%)")
            print(f"  Total Clusters: {total_clusters}")
            
            print(f"\nBackground Clustering:")
            print(f"  Enabled: {bg_status.get('enabled', 'Unknown')}")
            print(f"  In Progress: {bg_status.get('clustering_in_progress', 'Unknown')}")
            print(f"  Unprocessed Messages: {bg_status.get('unprocessed_messages', 'Unknown')}")
            
            minutes_since = bg_status.get('minutes_since_last_clustering')
            if minutes_since is not None:
                print(f"  Minutes Since Last Clustering: {minutes_since}")
            else:
                print(f"  Minutes Since Last Clustering: Never")
            
            print(f"  Should Trigger: {bg_status.get('should_trigger_clustering', 'Unknown')}")
            print(f"  Trigger Reason: {bg_status.get('trigger_reason', 'Unknown')}")
            
            config = bg_status.get('configuration', {})
            print(f"\nConfiguration:")
            print(f"  Message Threshold: {config.get('message_threshold', 'Unknown')}")
            print(f"  Time Threshold: {config.get('time_threshold_minutes', 'Unknown')} minutes")
            
            if latest_run:
                print(f"\nLatest Clustering Run:")
                print(f"  Created: {latest_run.created_at}")
                print(f"  Total Conversations: {latest_run.total_conversations}")
                print(f"  Clusters Created: {latest_run.clusters_created}")
                print(f"  Status: {latest_run.status}")
            else:
                print(f"\nLatest Clustering Run: None")
                
        except Exception as e:
            logger.error(f"Error getting status via services: {e}")
            return False
    else:
        print("Services not available - run with clustering method to see detailed status")
    
    print("="*60)
    return True

def method_background(services, reset=False):
    """Use BackgroundClusteringService to trigger clustering"""
    print("\n" + "="*60)
    print("BACKGROUND SERVICE CLUSTERING")
    print("="*60)
    
    background_service = services['background_service']
    
    if reset:
        print("Resetting clustering data...")
        if not reset_clustering_data(services):
            return False
    
    # Show current status
    status = background_service.get_status()
    print(f"Current Status:")
    print(f"  Enabled: {status.get('enabled')}")
    print(f"  In Progress: {status.get('clustering_in_progress')}")
    print(f"  Should Trigger: {status.get('should_trigger_clustering')}")
    print(f"  Reason: {status.get('trigger_reason')}")
    
    # Force clustering
    print(f"\nForcing background clustering...")
    started = background_service.force_clustering()
    
    if started:
        print("✓ Background clustering started successfully")
        
        # Wait for completion (with timeout)
        print("Waiting for clustering to complete...")
        timeout = 300  # 5 minutes
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if not background_service.is_clustering_in_progress():
                print("✓ Clustering completed!")
                break
            print("  Still clustering...")
            time.sleep(5)
        else:
            print("⚠ Clustering is taking longer than expected (still running in background)")
        
        # Show final status
        print(f"\nFinal Status:")
        final_status = background_service.get_status()
        print(f"  Clusters Created: {len(services['clustering_service'].get_all_clusters())}")
        print(f"  Latest Run: {final_status.get('latest_clustering_run', {}).get('created_at', 'Unknown')}")
        
        return True
    else:
        print("✗ Clustering was already in progress")
        return False

def method_api(api_url, reset=False):
    """Use API endpoints to trigger clustering"""
    print("\n" + "="*60)
    print("API ENDPOINT CLUSTERING")
    print("="*60)
    
    if reset:
        print("⚠ Reset not available via API - use --method background --reset instead")
        return False
    
    try:
        # Check API status
        print(f"Checking API status at {api_url}...")
        response = requests.get(f"{api_url}/api/clustering/status", timeout=10)
        if response.status_code != 200:
            print(f"✗ API not available: {response.status_code}")
            return False
        
        status_data = response.json()
        print(f"✓ API is available")
        print(f"  Total Conversations: {status_data['status']['total_conversations']}")
        print(f"  Total Clusters: {status_data['status']['total_clusters']}")
        
        # Force background clustering via API
        print(f"\nTriggering clustering via API...")
        response = requests.post(f"{api_url}/api/clustering/background-force", timeout=30)
        
        if response.status_code == 200:
            print("✓ Clustering started successfully via API")
            
            # Monitor progress
            print("Monitoring clustering progress...")
            for i in range(60):  # Check for up to 5 minutes
                time.sleep(5)
                try:
                    bg_response = requests.get(f"{api_url}/api/clustering/background-status", timeout=10)
                    if bg_response.status_code == 200:
                        bg_data = bg_response.json()
                        in_progress = bg_data.get('background_clustering', {}).get('clustering_in_progress', False)
                        if not in_progress:
                            print("✓ Clustering completed!")
                            break
                        print(f"  Still clustering... ({i*5}s)")
                    else:
                        print(f"  Status check failed: {bg_response.status_code}")
                except requests.RequestException:
                    print(f"  Status check failed: connection error")
            else:
                print("⚠ Clustering is taking longer than expected")
            
            return True
        elif response.status_code == 409:
            print("⚠ Clustering was already in progress")
            return True
        else:
            print(f"✗ Failed to start clustering: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.RequestException as e:
        print(f"✗ API request failed: {e}")
        print(f"Make sure the Flask server is running at {api_url}")
        return False

def method_direct(services, reset=False):
    """Use ConversationClusteringService directly"""
    print("\n" + "="*60)
    print("DIRECT SERVICE CLUSTERING")
    print("="*60)
    
    clustering_service = services['clustering_service']
    
    if reset:
        print("Resetting clustering data...")
        if not reset_clustering_data(services):
            return False
    
    print("Running direct clustering...")
    try:
        success = clustering_service.cluster_all_conversations()
        
        if success:
            print("✓ Direct clustering completed successfully")
            
            # Show results
            clusters = clustering_service.get_all_clusters()
            print(f"  Clusters Created: {len(clusters)}")
            
            for i, cluster in enumerate(clusters, 1):
                print(f"  Cluster {i}: {cluster.get('name', 'Unnamed')} ({len(cluster.get('conversations', []))} conversations)")
            
            return True
        else:
            print("✗ Direct clustering failed")
            return False
            
    except Exception as e:
        print(f"✗ Direct clustering error: {e}")
        return False

def reset_clustering_data(services):
    """Reset all clustering data"""
    try:
        models = services['models']
        
        # Delete all clusters and clustering runs
        deleted_clusters = models['ConversationCluster'].objects.delete()
        deleted_runs = models['ClusteringRun'].objects.delete()
        
        # Reset message processing flags
        updated_messages = models['Message'].objects.update(
            processed_for_clustering=False,
            concepts=[],
            embedding=None
        )
        
        print(f"✓ Reset complete:")
        print(f"  Deleted {deleted_clusters} clusters")
        print(f"  Deleted {deleted_runs} clustering runs")
        print(f"  Reset {updated_messages} messages")
        
        return True
        
    except Exception as e:
        print(f"✗ Reset failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Manual re-cluster script for Anthropic Mastery",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split('Usage:')[1] if 'Usage:' in __doc__ else ""
    )
    
    parser.add_argument(
        '--method',
        choices=['background', 'api', 'direct', 'reset'],
        default='background',
        help='Clustering method to use (default: background)'
    )
    
    parser.add_argument(
        '--api-url',
        default='http://localhost:5000',
        help='API base URL (default: http://localhost:5000)'
    )
    
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset all clustering data before re-clustering'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show clustering status only'
    )
    
    args = parser.parse_args()
    
    print("Anthropic Mastery - Manual Re-Cluster Script")
    print(f"Started at: {datetime.now()}")
    
    # Setup environment (only if not using API-only method)
    services = None
    if args.method != 'api' or args.status:
        services = setup_environment()
    
    # Show status if requested
    if args.status:
        show_status(services)
        return
    
    # Execute clustering method
    success = False
    
    if args.method == 'background' or args.method == 'reset':
        success = method_background(services, reset=args.reset or args.method == 'reset')
    elif args.method == 'api':
        success = method_api(args.api_url, reset=args.reset)
    elif args.method == 'direct':
        success = method_direct(services, reset=args.reset)
    
    # Show final status
    if services:
        show_status(services)
    
    print(f"\nCompleted at: {datetime.now()}")
    if success:
        print("✓ Re-clustering completed successfully!")
        sys.exit(0)
    else:
        print("✗ Re-clustering failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
