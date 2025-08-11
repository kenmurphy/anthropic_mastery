import json
import logging
from typing import List, Optional
from anthropic import Anthropic
from models.message import Message
from config import Config

logger = logging.getLogger(__name__)

class MessageAnalysisService:
    """Service for analyzing messages to extract technical concepts and generate embeddings"""
    
    def __init__(self):
        self.anthropic_client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
    
    def analyze_message(self, message: Message) -> bool:
        """
        Analyze a message to extract technical concepts and generate embeddings
        Returns True if analysis was successful, False otherwise
        """
        try:
            # Skip if already processed
            if message.processed_for_clustering:
                logger.info(f"Message {message.message_id} already processed for clustering")
                return True
            
            # Extract technical concepts
            concepts = self.extract_technical_concepts(message.content)
            if not concepts:
                logger.warning(f"No technical concepts extracted from message {message.message_id}. Concepts is {concepts}")
                concepts = []
            # concepts is a list of dicts with 'title' and 'summary' fields.
            # Combine them into a single string per concept: "Title: Summary"
            concepts_str = ", ".join(f"{c.get('title', '')}: {c.get('summary', '')}" for c in concepts)
            # Generate embedding
            embedding = self.generate_embedding(concepts_str)
            if not embedding:
                logger.error(f"Failed to generate embedding for message {message.message_id}")
                return False
            
            # Update message with analysis results
            message.technical_concepts = [c.get('title') for c in concepts]
            message.embedding = embedding
            message.processed_for_clustering = True
            message.save()
            
            logger.info(f"Successfully analyzed message {message.message_id} - found {len(concepts)} concepts")
            return True
            
        except Exception as e:
            logger.error(f"Error analyzing message {message.message_id}: {str(e)}")
            return False
    
    def extract_technical_concepts(self, content: str) -> List[str]:
        """
        Extract technical concepts from message content using Anthropic API
        """
        try:
            prompt = f"""You are an assistant that extracts 0–3 key concepts from a single message in a conversation.
A concept is a short, self-contained description of a distinct subject, theme, or problem discussed.
Do not include chit-chat, pleasantries, or unrelated text.

Guidelines:
- Each concept must have both a title and a one-sentence summary.
- The title must be 2–6 words.
- Use plain language, no hashtags.
- Prefer combining closely related details into one clear concept.
- If no meaningful concept is present, return an empty list.

Output:
- Return JSON only. No extra text, no code fences, no markdown.
- Use exactly this schema and field names:

{{
  "concepts": [
    {{
      "title": "short title (2–6 words)",
      "summary": "one-sentence summary of the concept"
    }}
  ]
}}

If none, return: {{"concepts": []}}

Message: {content}"""
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                temperature=0.1,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse the JSON response
            response_text = response.content[0].text.strip()
            # Try to extract JSON from the response
            try:
                # Look for JSON in the response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx != 0:
                    json_str = response_text[start_idx:end_idx]
                    result = json.loads(json_str)
                    concepts = result.get('concepts', [])
                    return concepts
                else:
                    logger.warning(f"No JSON found in concept extraction response: {response_text}")
                    return []
                    
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON from concept extraction: {response_text}, error: {e}")
                return []
                
        except Exception as e:
            logger.error(f"Error extracting technical concepts: {str(e)}")
            return []
    
    def generate_embedding(self, content: str) -> Optional[List[float]]:
        """
        Generate embedding for message content using Anthropic API
        Note: This is a placeholder - Anthropic doesn't have a direct embedding API
        For now, we'll create a simple hash-based embedding for prototype
        """
        try:
            # For prototype: create a simple embedding based on content
            # In production, you'd use a proper embedding model like OpenAI's text-embedding-ada-002
            
            # Simple approach: use content characteristics to create a basic embedding
            import hashlib
            import struct
            
            # Create a hash of the content
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Convert hash to a list of floats (1024 dimensions for consistency)
            embedding = []
            for i in range(0, len(content_hash), 2):
                # Convert hex pairs to integers, then normalize to [-1, 1]
                hex_pair = content_hash[i:i+2]
                int_val = int(hex_pair, 16)
                normalized_val = (int_val - 127.5) / 127.5  # Normalize to [-1, 1]
                embedding.append(normalized_val)
            
            # Pad or truncate to 1024 dimensions
            while len(embedding) < 1024:
                embedding.extend(embedding[:min(len(embedding), 1024 - len(embedding))])
            
            embedding = embedding[:1024]
            
            logger.info(f"Generated {len(embedding)}-dimensional embedding")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return None
    
    def analyze_conversation_messages(self, conversation_id: str) -> int:
        """
        Analyze all unprocessed messages in a conversation
        Returns the number of messages successfully analyzed
        """
        try:
            # Get all unprocessed messages for this conversation
            unprocessed_messages = Message.objects(
                conversation_id=conversation_id,
                processed_for_clustering=False
            )
            
            analyzed_count = 0
            for message in unprocessed_messages:
                if self.analyze_message(message):
                    analyzed_count += 1
            
            logger.info(f"Analyzed {analyzed_count} messages for conversation {conversation_id}")
            return analyzed_count
            
        except Exception as e:
            logger.error(f"Error analyzing conversation messages {conversation_id}: {str(e)}")
            return 0
    
    def get_conversation_concepts(self, conversation_id: str) -> List[str]:
        """
        Get all unique technical concepts from a conversation
        """
        try:
            messages = Message.objects(
                conversation_id=conversation_id,
                processed_for_clustering=True
            )
            
            all_concepts = []
            for message in messages:
                if message.technical_concepts:
                    all_concepts.extend(message.technical_concepts)
            
            # Return unique concepts
            unique_concepts = list(set(all_concepts))
            return unique_concepts
            
        except Exception as e:
            logger.error(f"Error getting conversation concepts {conversation_id}: {str(e)}")
            return []
    
    def get_conversation_embedding(self, conversation_id: str) -> Optional[List[float]]:
        """
        Get average embedding for all messages in a conversation
        """
        try:
            messages = Message.objects(
                conversation_id=conversation_id,
                processed_for_clustering=True
            )
            
            if not messages:
                return None
            
            # Calculate average embedding
            embeddings = []
            for message in messages:
                if message.embedding and len(message.embedding) == 1024:
                    embeddings.append(message.embedding)
            
            if not embeddings:
                return None
            
            # Calculate element-wise average
            avg_embedding = []
            for i in range(1024):
                avg_val = sum(emb[i] for emb in embeddings) / len(embeddings)
                avg_embedding.append(avg_val)
            
            return avg_embedding
            
        except Exception as e:
            logger.error(f"Error getting conversation embedding {conversation_id}: {str(e)}")
            return None
