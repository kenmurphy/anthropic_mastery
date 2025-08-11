from flask import Blueprint, jsonify, request
from services.conversation_clustering_service import ConversationClusteringService
from services.message_analysis_service import MessageAnalysisService
from services.background_clustering_service import BackgroundClusteringService
import logging

logger = logging.getLogger(__name__)

clustering_bp = Blueprint('clustering', __name__)

# Initialize services
clustering_service = ConversationClusteringService()
message_analysis_service = MessageAnalysisService()

@clustering_bp.route('/api/clusters', methods=['GET'])
def get_all_clusters():
    """Get all conversation clusters"""
    try:
        clusters = clustering_service.get_all_clusters()
        return jsonify({
            'success': True,
            'clusters': clusters,
            'total_clusters': len(clusters)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting all clusters: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve clusters'
        }), 500

@clustering_bp.route('/api/clusters/<cluster_id>', methods=['GET'])
def get_cluster_details(cluster_id):
    """Get detailed information about a specific cluster"""
    try:
        cluster = clustering_service.get_cluster_by_id(cluster_id)
        
        if not cluster:
            return jsonify({
                'success': False,
                'error': 'Cluster not found'
            }), 404
        
        return jsonify({
            'success': True,
            'cluster': cluster
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting cluster {cluster_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve cluster details'
        }), 500

@clustering_bp.route('/api/conversations/<conversation_id>/cluster', methods=['GET'])
def get_conversation_cluster(conversation_id):
    """Get the cluster that contains a specific conversation"""
    try:
        cluster = clustering_service.get_conversation_cluster(conversation_id)
        
        if not cluster:
            return jsonify({
                'success': False,
                'error': 'Conversation not found in any cluster'
            }), 404
        
        return jsonify({
            'success': True,
            'cluster': cluster
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting cluster for conversation {conversation_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve conversation cluster'
        }), 500

@clustering_bp.route('/api/conversations/<conversation_id>/similar', methods=['GET'])
def get_similar_conversations(conversation_id):
    """Get conversations similar to the specified conversation"""
    try:
        # Get threshold from query parameters (default 0.6)
        threshold = float(request.args.get('threshold', 0.6))
        
        similar_conversations = clustering_service.find_similar_conversations(
            conversation_id, 
            threshold=threshold
        )
        
        return jsonify({
            'success': True,
            'similar_conversations': similar_conversations,
            'threshold': threshold,
            'count': len(similar_conversations)
        }), 200
        
    except Exception as e:
        logger.error(f"Error finding similar conversations for {conversation_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to find similar conversations'
        }), 500

@clustering_bp.route('/api/conversations/<conversation_id>/analyze', methods=['POST'])
def analyze_conversation(conversation_id):
    """Trigger analysis of a specific conversation"""
    try:
        analyzed_count = message_analysis_service.analyze_conversation_messages(conversation_id)
        
        return jsonify({
            'success': True,
            'conversation_id': conversation_id,
            'messages_analyzed': analyzed_count
        }), 200
        
    except Exception as e:
        logger.error(f"Error analyzing conversation {conversation_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to analyze conversation'
        }), 500

@clustering_bp.route('/api/clustering/run', methods=['POST'])
def run_clustering():
    """Trigger a full clustering run on all conversations"""
    try:
        success = clustering_service.cluster_all_conversations()
        
        if success:
            clusters = clustering_service.get_all_clusters()
            return jsonify({
                'success': True,
                'message': 'Clustering completed successfully',
                'clusters_created': len(clusters)
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Clustering failed - check logs for details'
            }), 500
        
    except Exception as e:
        logger.error(f"Error running clustering: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to run clustering'
        }), 500

@clustering_bp.route('/api/conversations/<conversation_id>/concepts', methods=['GET'])
def get_conversation_concepts(conversation_id):
    """Get technical concepts extracted from a conversation"""
    try:
        concepts = message_analysis_service.get_conversation_concepts(conversation_id)
        
        return jsonify({
            'success': True,
            'conversation_id': conversation_id,
            'concepts': concepts,
            'count': len(concepts)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting concepts for conversation {conversation_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve conversation concepts'
        }), 500

@clustering_bp.route('/api/clustering/status', methods=['GET'])
def get_clustering_status():
    """Get status information about clustering"""
    try:
        from models.conversation import Conversation
        from models.message import Message
        from models.cluster import ConversationCluster, ClusteringRun
        
        # Get counts
        total_conversations = Conversation.objects.count()
        total_messages = Message.objects.count()
        processed_messages = Message.objects(processed_for_clustering=True).count()
        total_clusters = ConversationCluster.objects.count()
        
        # Get latest clustering run
        latest_run = ClusteringRun.objects.order_by('-created_at').first()
        
        return jsonify({
            'success': True,
            'status': {
                'total_conversations': total_conversations,
                'total_messages': total_messages,
                'processed_messages': processed_messages,
                'processing_progress': processed_messages / max(total_messages, 1),
                'total_clusters': total_clusters,
                'latest_run': latest_run.to_dict() if latest_run else None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting clustering status: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve clustering status'
        }), 500

@clustering_bp.route('/api/clustering/background-status', methods=['GET'])
def get_background_clustering_status():
    """Get status of background clustering service"""
    try:
        background_service = BackgroundClusteringService()
        status = background_service.get_status()
        
        return jsonify({
            'success': True,
            'background_clustering': status
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting background clustering status: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve background clustering status'
        }), 500

@clustering_bp.route('/api/clustering/background-force', methods=['POST'])
def force_background_clustering():
    """Force background clustering to run immediately"""
    try:
        background_service = BackgroundClusteringService()
        started = background_service.force_clustering()
        
        if started:
            return jsonify({
                'success': True,
                'message': 'Background clustering started'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Clustering already in progress'
            }), 409
        
    except Exception as e:
        logger.error(f"Error forcing background clustering: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to start background clustering'
        }), 500

@clustering_bp.route('/api/messages/<message_id>/trigger-analysis', methods=['POST'])
def trigger_message_analysis(message_id):
    """Trigger background analysis for a specific message"""
    try:
        background_service = BackgroundClusteringService()
        background_service.trigger_background_analysis(message_id)
        
        return jsonify({
            'success': True,
            'message': f'Background analysis triggered for message {message_id}'
        }), 200
        
    except Exception as e:
        logger.error(f"Error triggering message analysis for {message_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to trigger message analysis'
        }), 500
