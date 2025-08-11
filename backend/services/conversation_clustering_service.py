import json
import logging
import numpy as np
from typing import List, Dict, Optional, Tuple
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from anthropic import Anthropic
from models.conversation import Conversation
from models.cluster import ConversationCluster, ClusteringRun
from services.message_analysis_service import MessageAnalysisService
from config import Config
from sklearn.metrics import silhouette_score

logger = logging.getLogger(__name__)

class ConversationClusteringService:
    """Service for clustering conversations based on semantic similarity"""
    
    def __init__(self):
        self.anthropic_client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.message_analysis_service = MessageAnalysisService()
        self.auto_k = getattr(Config, "CLUSTERING_AUTO_K", True)
        self.min_k = getattr(Config, "CLUSTERING_MIN_K", 2)
        self.max_k = getattr(Config, "CLUSTERING_MAX_K", 12)
        self.n_clusters = None if self.auto_k else getattr(Config, "CLUSTERING_K", 5)
        self.cluster_centers = None
    
    def cluster_all_conversations(self) -> bool:
        """
        Perform clustering on all conversations
        Returns True if clustering was successful, False otherwise
        """
        try:
            logger.info("Starting conversation clustering process")
            
            # Step 1: Analyze all unprocessed messages
            self._analyze_all_messages()
            
            # Step 2: Get conversation data for clustering
            conversation_data = self._get_conversation_data()
            
            if len(conversation_data) < 2:
                logger.warning("Not enough conversations to form clusters")
                return False
            
            if self.auto_k:
                embeddings = np.array([c['embedding'] for c in conversation_data])
                selected_k = self._select_optimal_k(embeddings)
                if not selected_k:
                    logger.warning("Could not determine a suitable number of clusters")
                    return False
                self.n_clusters = selected_k
                logger.info(f"Auto-selected k={self.n_clusters}")
            else:
                if len(conversation_data) < self.n_clusters:
                    logger.warning(f"Not enough conversations ({len(conversation_data)}) for {self.n_clusters} clusters")
                    return False
            
            # Step 3: Perform k-means clustering
            cluster_assignments = self._perform_clustering(conversation_data)
            
            if cluster_assignments is None:
                logger.error("Clustering failed")
                return False
            
            # Step 4: Generate cluster labels and descriptions
            clusters_info = self._generate_cluster_labels(conversation_data, cluster_assignments)
            
            # Step 5: Save clusters to database
            self._save_clusters(clusters_info)
            
            # Step 6: Record clustering run
            ClusteringRun.create_run(
                total_conversations=len(conversation_data),
                clusters_created=self.n_clusters
            )
            
            logger.info(f"Successfully clustered {len(conversation_data)} conversations into {self.n_clusters} clusters")
            return True
            
        except Exception as e:
            logger.error(f"Error in conversation clustering: {str(e)}")
            return False
    
    def _analyze_all_messages(self):
        """Analyze all unprocessed messages for technical concepts and embeddings"""
        try:
            conversations = Conversation.objects.all()
            total_analyzed = 0
            
            for conversation in conversations:
                analyzed_count = self.message_analysis_service.analyze_conversation_messages(str(conversation.id))
                total_analyzed += analyzed_count
            
            logger.info(f"Analyzed {total_analyzed} messages across all conversations")
            
        except Exception as e:
            logger.error(f"Error analyzing messages: {str(e)}")
    
    def _get_conversation_data(self) -> List[Dict]:
        """
        Get conversation data with embeddings and concepts for clustering
        """
        try:
            conversations = Conversation.objects.all()
            conversation_data = []
            
            for conversation in conversations:
                # Get conversation embedding (average of message embeddings)
                embedding = self.message_analysis_service.get_conversation_embedding(str(conversation.id))
                
                # Get conversation concepts
                concepts = self.message_analysis_service.get_conversation_concepts(str(conversation.id))
                
                if embedding and concepts:
                    conversation_data.append({
                        'conversation_id': str(conversation.id),
                        'title': conversation.title,
                        'embedding': embedding,
                        'concepts': concepts,
                        'created_at': conversation.created_at
                    })
            
            logger.info(f"Retrieved data for {len(conversation_data)} conversations")
            return conversation_data
            
        except Exception as e:
            logger.error(f"Error getting conversation data: {str(e)}")
            return []
    
    def _perform_clustering(self, conversation_data: List[Dict]) -> Optional[List[int]]:
        """
        Perform k-means clustering on conversation embeddings
        """
        try:
            # Extract embeddings
            embeddings = np.array([conv['embedding'] for conv in conversation_data])
            
            # Perform k-means clustering
            kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
            cluster_assignments = kmeans.fit_predict(embeddings)
            
            # Store cluster centers for later use
            self.cluster_centers = kmeans.cluster_centers_
            
            logger.info(f"K-means clustering completed with {self.n_clusters} clusters")
            return cluster_assignments.tolist()
            
        except Exception as e:
            logger.error(f"Error performing clustering: {str(e)}")
            return None
    
    def _generate_cluster_labels(self, conversation_data: List[Dict], cluster_assignments: List[int]) -> List[Dict]:
        """
        Generate labels and descriptions for each cluster using Anthropic API
        """
        try:
            clusters_info = []
            
            for cluster_id in range(self.n_clusters):
                # Get conversations in this cluster
                cluster_conversations = [
                    conversation_data[i] for i, assignment in enumerate(cluster_assignments)
                    if assignment == cluster_id
                ]
                
                if not cluster_conversations:
                    # Empty cluster - create default
                    clusters_info.append({
                        'cluster_id': f"cluster_{cluster_id}",
                        'label': f"Miscellaneous Topics {cluster_id + 1}",
                        'description': "Various technical discussions and problem-solving conversations.",
                        'conversation_ids': [],
                        'key_concepts': [],
                        'centroid': self.cluster_centers[cluster_id].tolist()
                    })
                    continue
                
                # Collect all concepts from conversations in this cluster
                all_concepts = []
                for conv in cluster_conversations:
                    all_concepts.extend(conv['concepts'])
                
                # Get top concepts (most frequent)
                concept_counts = {}
                for concept in all_concepts:
                    concept_counts[concept] = concept_counts.get(concept, 0) + 1
                
                top_concepts = sorted(concept_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                top_concept_names = [concept for concept, count in top_concepts]
                
                # Generate cluster label and description using Anthropic
                label, description = self._generate_cluster_label_with_ai(top_concept_names)
                
                clusters_info.append({
                    'cluster_id': f"cluster_{cluster_id}",
                    'label': label,
                    'description': description,
                    'conversation_ids': [conv['conversation_id'] for conv in cluster_conversations],
                    'key_concepts': top_concept_names,
                    'centroid': self.cluster_centers[cluster_id].tolist()
                })
                
                logger.info(f"Generated label for cluster {cluster_id}: {label}")
            
            return clusters_info
            
        except Exception as e:
            logger.error(f"Error generating cluster labels: {str(e)}")
            return []
    
    def _generate_cluster_label_with_ai(self, top_concepts: List[str]) -> Tuple[str, str]:
        """
        Generate cluster label and description using Anthropic API
        """
        try:
            concepts_text = ", ".join(top_concepts[:8])  # Use top 8 concepts
            
            prompt = f"""You are analyzing clusters of professional conversations where people use AI for work assistance.

Here are the top technical concepts from a cluster:
{concepts_text}

Create a study guide title and description:
- Title: 3-5 words describing the technical domain
- Description: 2 sentences explaining what professionals would learn from this cluster

Format as JSON: {{"title": "...", "description": "..."}}"""
            
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=300,
                temperature=0.1,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            response_text = response.content[0].text.strip()
            
            # Try to extract JSON from the response
            try:
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx != 0:
                    json_str = response_text[start_idx:end_idx]
                    result = json.loads(json_str)
                    
                    title = result.get('title', 'Technical Concepts').strip()
                    description = result.get('description', 'Professional technical discussions and problem-solving.').strip()
                    
                    return title, description
                else:
                    logger.warning(f"No JSON found in cluster labeling response: {response_text}")
                    return self._generate_fallback_label(top_concepts)
                    
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON from cluster labeling: {response_text}, error: {e}")
                return self._generate_fallback_label(top_concepts)
                
        except Exception as e:
            logger.error(f"Error generating cluster label with AI: {str(e)}")
            return self._generate_fallback_label(top_concepts)
    
    def _generate_fallback_label(self, top_concepts: List[str]) -> Tuple[str, str]:
        """Generate fallback label when AI generation fails"""
        if not top_concepts:
            return "General Technical Topics", "Various technical discussions and professional problem-solving conversations."
        
        # Use the most common concept as the basis for the label
        main_concept = top_concepts[0].replace('-', ' ').title()
        label = f"{main_concept} & Related Topics"
        description = f"Professional discussions focused on {main_concept.lower()} and related technical concepts. Learn practical approaches to common challenges in this domain."
        
        return label, description
    
    def _save_clusters(self, clusters_info: List[Dict]):
        """Save cluster information to database"""
        try:
            # Clear existing clusters
            ConversationCluster.objects.delete()
            
            # Save new clusters
            for cluster_info in clusters_info:
                cluster = ConversationCluster(
                    cluster_id=cluster_info['cluster_id'],
                    label=cluster_info['label'],
                    description=cluster_info['description'],
                    conversation_ids=cluster_info['conversation_ids'],
                    key_concepts=cluster_info['key_concepts'],
                    centroid=cluster_info['centroid']
                )
                cluster.save()
                
                logger.info(f"Saved cluster {cluster_info['cluster_id']}: {cluster_info['label']}")
            
        except Exception as e:
            logger.error(f"Error saving clusters: {str(e)}")
    
    def get_all_clusters(self) -> List[Dict]:
        """Get all clusters with their information"""
        try:
            clusters = ConversationCluster.objects.all().order_by('cluster_id')
            return [cluster.to_dict() for cluster in clusters]
            
        except Exception as e:
            logger.error(f"Error getting all clusters: {str(e)}")
            return []
    
    def get_cluster_by_id(self, cluster_id: str) -> Optional[Dict]:
        """Get specific cluster information"""
        try:
            cluster = ConversationCluster.objects(cluster_id=cluster_id).first()
            if cluster:
                return cluster.to_dict()
            return None
            
        except Exception as e:
            logger.error(f"Error getting cluster {cluster_id}: {str(e)}")
            return None
    
    def get_conversation_cluster(self, conversation_id: str) -> Optional[Dict]:
        """Get the cluster that contains a specific conversation"""
        try:
            cluster = ConversationCluster.objects(conversation_ids=conversation_id).first()
            if cluster:
                return cluster.to_dict()
            return None
            
        except Exception as e:
            logger.error(f"Error getting cluster for conversation {conversation_id}: {str(e)}")
            return None
    
    def find_similar_conversations(self, conversation_id: str, threshold: float = 0.6) -> List[Dict]:
        """Find conversations similar to the given conversation"""
        try:
            # Get the target conversation's embedding
            target_embedding = self.message_analysis_service.get_conversation_embedding(conversation_id)
            if not target_embedding:
                return []
            
            # Get all conversation data
            conversation_data = self._get_conversation_data()
            
            # Calculate similarities
            target_embedding = np.array(target_embedding).reshape(1, -1)
            similarities = []
            
            for conv_data in conversation_data:
                if conv_data['conversation_id'] == conversation_id:
                    continue  # Skip the target conversation itself
                
                conv_embedding = np.array(conv_data['embedding']).reshape(1, -1)
                similarity = cosine_similarity(target_embedding, conv_embedding)[0][0]
                
                if similarity >= threshold:
                    similarities.append({
                        'conversation_id': conv_data['conversation_id'],
                        'title': conv_data['title'],
                        'similarity': float(similarity),
                        'concepts': conv_data['concepts']
                    })
            
            # Sort by similarity (highest first)
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            return similarities[:10]  # Return top 10 similar conversations
            
        except Exception as e:
            logger.error(f"Error finding similar conversations: {str(e)}")
            return []

    def _select_optimal_k(self, embeddings: np.ndarray) -> Optional[int]:
        n = embeddings.shape[0]
        if n < 2:
            return None
        k_min = max(2, min(self.min_k, n))
        k_max = min(self.max_k, n - 1)
        if k_max < 2 or k_min > k_max:
            return None

        best_k, best_score = None, -1.0
        for k in range(k_min, k_max + 1):
            try:
                km = KMeans(n_clusters=k, random_state=42, n_init=10)
                labels = km.fit_predict(embeddings)
                # Skip degenerate solutions
                if len(set(labels)) < 2:
                    continue
                score = silhouette_score(embeddings, labels, metric="cosine")
                if score > best_score:
                    best_score = score
                    best_k = k
            except Exception as e:
                logger.warning(f"Silhouette eval failed for k={k}: {e}")
        return best_k
