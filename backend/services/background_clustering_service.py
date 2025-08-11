import threading
import logging
from datetime import datetime, timedelta
from typing import Optional
from models.message import Message
from models.cluster import ClusteringRun
from services.conversation_clustering_service import ConversationClusteringService
from services.message_analysis_service import MessageAnalysisService
from config import Config

logger = logging.getLogger(__name__)

class BackgroundClusteringService:
    """Service for managing background clustering operations triggered by new messages"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance manages clustering"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(BackgroundClusteringService, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.clustering_service = ConversationClusteringService()
        self.message_analysis_service = MessageAnalysisService()
        
        # Threading controls
        self._clustering_lock = threading.Lock()
        self._clustering_in_progress = False
        self._last_clustering_check = None
        
        # Configuration
        self.enabled = getattr(Config, 'BACKGROUND_CLUSTERING_ENABLED', True)
        self.message_threshold = getattr(Config, 'CLUSTERING_MESSAGE_THRESHOLD', 3)
        self.time_threshold_minutes = getattr(Config, 'CLUSTERING_TIME_THRESHOLD_MINUTES', 30)
        
        self._initialized = True
        logger.info(f"BackgroundClusteringService initialized - enabled: {self.enabled}, "
                   f"message_threshold: {self.message_threshold}, "
                   f"time_threshold: {self.time_threshold_minutes}min")
    
    def trigger_background_analysis(self, message_id: str):
        """
        Trigger background analysis for a new message
        This is the main entry point called when new messages are created
        """
        logger.info(f"See if background clustering is enabled for {message_id}")
        if not self.enabled:
            logger.debug("Background clustering is disabled")
            return
        
        logger.info(f"Triggering background analysis for message {message_id}")
        
        # Start background thread
        thread = threading.Thread(
            target=self._analyze_and_maybe_cluster,
            args=(message_id,),
            daemon=True,  # Dies when main process dies
            name=f"clustering-analysis-{message_id[:8]}"
        )
        thread.start()
    
    def _analyze_and_maybe_cluster(self, message_id: str):
        """
        Background thread function that analyzes a message and triggers clustering if needed
        """
        try:
            logger.info(f"Starting background analysis for message {message_id}")
            
            # Step 1: Analyze the new message for concepts and embeddings
            message = Message.objects(message_id=message_id).first()
            if not message:
                logger.warning(f"Message {message_id} not found for analysis")
                return
            
            # Analyze the message
            analysis_success = self.message_analysis_service.analyze_message(message)
            if analysis_success:
                logger.info(f"Successfully analyzed message {message_id}")
            else:
                logger.warning(f"Failed to analyze message {message_id}")
            
            # Step 2: Check if we should trigger clustering
            should_cluster, reason = self._should_trigger_clustering()
            if should_cluster:
                logger.info(f"Triggering clustering: {reason}")
                self._run_clustering_if_not_in_progress()
            else:
                logger.debug(f"Clustering not triggered: {reason}")
                
        except Exception as e:
            logger.error(f"Background analysis failed for message {message_id}: {str(e)}")
    
    def _should_trigger_clustering(self) -> tuple:
        """
        Determine if clustering should be triggered based on various conditions
        Returns (should_trigger, reason)
        """
        try:
            # Check 1: Count unprocessed messages
            unprocessed_count = self._count_unprocessed_messages()
            if unprocessed_count >= self.message_threshold:
                return True, f"{unprocessed_count} unprocessed messages (threshold: {self.message_threshold})"
            
            # Check 2: Time since last clustering
            minutes_since_last = self._minutes_since_last_clustering()
            if minutes_since_last >= self.time_threshold_minutes:
                return True, f"{minutes_since_last} minutes since last clustering (threshold: {self.time_threshold_minutes})"
            
            # Check 3: No clustering runs exist yet
            if not ClusteringRun.objects.first():
                total_messages = Message.objects.count()
                if total_messages >= 2:  # Need at least 2 messages to cluster
                    return True, "No clustering runs exist and have sufficient messages"
            
            return False, f"Conditions not met - unprocessed: {unprocessed_count}, minutes: {minutes_since_last}"
            
        except Exception as e:
            logger.error(f"Error checking clustering conditions: {str(e)}")
            return False, f"Error checking conditions: {str(e)}"
    
    def _count_unprocessed_messages(self) -> int:
        """Count messages that haven't been processed for clustering"""
        try:
            return Message.objects(processed_for_clustering=False).count()
        except Exception as e:
            logger.error(f"Error counting unprocessed messages: {str(e)}")
            return 0
    
    def _minutes_since_last_clustering(self) -> int:
        """Get minutes since the last clustering run"""
        try:
            latest_run = ClusteringRun.objects.order_by('-created_at').first()
            if not latest_run:
                return float('inf')  # No clustering runs yet
            
            time_diff = datetime.utcnow() - latest_run.created_at
            return int(time_diff.total_seconds() / 60)
            
        except Exception as e:
            logger.error(f"Error calculating time since last clustering: {str(e)}")
            return 0
    
    def _run_clustering_if_not_in_progress(self):
        """
        Run clustering if not already in progress
        Uses threading lock to prevent concurrent clustering operations
        """
        with self._clustering_lock:
            if self._clustering_in_progress:
                logger.info("Clustering already in progress, skipping")
                return
            
            self._clustering_in_progress = True
            logger.info("Starting background clustering operation")
            
            try:
                success = self.clustering_service.cluster_all_conversations()
                if success:
                    logger.info("Background clustering completed successfully")
                else:
                    logger.error("Background clustering failed")
                    
            except Exception as e:
                logger.error(f"Error during background clustering: {str(e)}")
                
            finally:
                self._clustering_in_progress = False
                logger.info("Background clustering operation finished")
    
    def is_clustering_in_progress(self) -> bool:
        """Check if clustering is currently in progress"""
        return self._clustering_in_progress
    
    def get_status(self) -> dict:
        """Get current status of background clustering service"""
        try:
            unprocessed_count = self._count_unprocessed_messages()
            minutes_since_last = self._minutes_since_last_clustering()
            should_cluster, reason = self._should_trigger_clustering()
            
            latest_run = ClusteringRun.objects.order_by('-created_at').first()
            
            return {
                'enabled': self.enabled,
                'clustering_in_progress': self._clustering_in_progress,
                'unprocessed_messages': unprocessed_count,
                'minutes_since_last_clustering': minutes_since_last if minutes_since_last != float('inf') else None,
                'should_trigger_clustering': should_cluster,
                'trigger_reason': reason,
                'configuration': {
                    'message_threshold': self.message_threshold,
                    'time_threshold_minutes': self.time_threshold_minutes
                },
                'latest_clustering_run': latest_run.to_dict() if latest_run else None
            }
            
        except Exception as e:
            logger.error(f"Error getting background clustering status: {str(e)}")
            return {
                'enabled': self.enabled,
                'error': str(e)
            }
    
    def force_clustering(self) -> bool:
        """
        Force clustering to run immediately (for testing/manual triggers)
        Returns True if clustering was started, False if already in progress
        """
        if self._clustering_in_progress:
            return False
        
        logger.info("Force clustering requested")
        thread = threading.Thread(
            target=self._run_clustering_if_not_in_progress,
            daemon=True,
            name="force-clustering"
        )
        thread.start()
        return True
