import os
import json
from typing import Generator, List, Dict, Any, Optional
from anthropic import Anthropic
from datetime import datetime

class AnthropicService:
    """Service for handling Anthropic API interactions with streaming support"""
    
    def __init__(self):
        """Initialize Anthropic client"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        self.client = Anthropic(api_key=api_key)
        
        # Model configurations
        self.models = {
            'research': 'claude-3-5-sonnet-20241022',  # Complex reasoning for sidebar
            'snippets': 'claude-3-haiku-20240307',  # Fast edits for Command-K
            'cards': 'claude-3-5-sonnet-20241022'  # Comprehensive analysis for cards
        }
    
    
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)"""
        # Rough approximation: 1 token ≈ 3.5 characters for Claude
        return len(text) // 4
    
    def stream_conversation_response(
        self, 
        message_history: List[Dict[str, str]]
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Stream Claude conversation responses
        
        Args:
            message_history: List of conversation messages
            
        Yields:
            Dict with content, is_complete, and error fields
        """
        try:
            # Build conversation messages with system prompt
            system_message = "You are Claude, a helpful AI assistant created by Anthropic. Provide helpful, accurate, and engaging responses to user questions and requests. Use markdown formatting."
            
            # Filter out any existing system messages and use only user/assistant messages
            filtered_messages = []
            for msg in message_history:
                if msg.get('role') in ['user', 'assistant']:
                    filtered_messages.append({
                        'role': msg['role'],
                        'content': msg['content']
                    })
            
            # Stream response from Anthropic
            with self.client.messages.stream(
                model=self.models['research'],  # Use research model for conversations
                max_tokens=2000,
                temperature=0.7,
                system=system_message,
                messages=filtered_messages
            ) as stream:
                for text in stream.text_stream:
                    yield {
                        'content': text,
                        'is_complete': False,
                        'error': None
                    }
            
            # Send completion signal
            yield {
                'content': '',
                'is_complete': True,
                'error': None
            }
            
        except Exception as e:
            yield {
                'content': '',
                'is_complete': True,
                'error': str(e)
            }
    
    def generate_conversation_title(self, message_history: List[Dict[str, str]]) -> str:
        """
        Generate a title for a conversation based on its content
        
        Args:
            message_history: List of conversation messages
            
        Returns:
            Generated title string
        """
        try:
            # Build prompt for title generation
            conversation_text = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in message_history[:6]  # Use first 6 messages for title
            ])
            
            system_message = "Generate a concise, descriptive title (max 50 characters) for this conversation. Return only the title, no quotes or extra text."
            
            user_message = f"Conversation:\n{conversation_text}\n\nGenerate a title:"
            
            response = self.client.messages.create(
                model=self.models['snippets'],  # Use faster model for title generation
                max_tokens=20,
                temperature=0.3,
                system=system_message,
                messages=[{"role": "user", "content": user_message}]
            )
            
            title = response.content[0].text.strip()
            
            # Clean up the title
            title = title.strip('"\'')  # Remove quotes
            if len(title) > 50:
                title = title[:47] + "..."
            
            return title if title else "Conversation"
            
        except Exception as e:
            print(f"Error generating conversation title: {e}")
            return "Conversation"
    
    def refine_original_topics(self, raw_concepts: List[str], course_title: str, course_description: str) -> List[Dict[str, str]]:
        """
        Refine raw cluster concepts into high-quality original learning topics
        
        Args:
            raw_concepts: List of raw concept strings from cluster analysis
            course_title: Title of the course for context
            course_description: Description of the course for context
            
        Returns:
            List of dictionaries with 'title' and 'difficulty_level' keys for refined original topics
        """
        try:
            # Build prompt for topic refinement
            concepts_text = "\n".join([f"- {concept}" for concept in raw_concepts])
            
            system_prompt = """You are an AI learning assistant that refines raw technical concepts into high-quality learning topics.

Your task is to review a list of raw concepts extracted from professional conversations and improve them for educational purposes. You should:

1. **Collapse Similar Topics**: Merge concepts that are too similar or overlapping
2. **Improve Formatting**: Convert technical terms into clear, learnable topic titles
3. **Ensure Appropriate Granularity**: Topics should be substantial enough for meaningful learning
4. **Maintain Relevance**: Keep topics connected to the original conversation content
5. **Add Difficulty Levels**: Assign beginner, medium, or advanced based on complexity

Guidelines:
- Convert "database-query" → "Database Query Fundamentals"
- Merge "error-handling" + "exception-handling" → "Error and Exception Handling"
- Remove overly specific items that aren't broadly educational
- Ensure each topic represents a learnable skill or concept area

Respond with ONLY a valid JSON array in this format:
[
  {
    "title": "Refined Topic Title",
    "difficulty_level": "beginner|medium|advanced"
  }
]

Do not include any explanations or additional text outside the JSON."""

            user_prompt = f"""Course: {course_title}
Description: {course_description}

Raw Concepts to Refine:
{concepts_text}

Please refine these concepts into high-quality learning topics:"""

            response = self.client.messages.create(
                model=self.models['research'],
                max_tokens=800,
                temperature=0.3,  # Lower temperature for more consistent refinement
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            # Parse the JSON response
            response_text = response.content[0].text.strip()
            
            # Try to extract JSON if there's extra text
            import json
            import re
            
            # Look for JSON array pattern
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            
            refined_topics = json.loads(response_text)
            
            # Validate the response structure
            validated_topics = []
            for topic in refined_topics:
                if isinstance(topic, dict) and 'title' in topic and 'difficulty_level' in topic:
                    # Validate difficulty level
                    if topic['difficulty_level'] in ['beginner', 'medium', 'advanced']:
                        validated_topics.append({
                            'title': topic['title'][:200],  # Truncate to max length
                            'difficulty_level': topic['difficulty_level']
                        })
            
            return validated_topics[:10]  # Limit to 10 refined topics max
            
        except Exception as e:
            print(f"Error refining original topics: {e}")
            # Fallback: return raw concepts with default difficulty
            return [
                {
                    'title': concept.replace('-', ' ').title(),
                    'difficulty_level': 'medium'
                } for concept in raw_concepts[:10]
            ]

    def generate_related_topics(self, existing_concepts: List[str], course_title: str, course_description: str) -> List[Dict[str, str]]:
        """
        Generate related topics using existing course concepts as input
        
        Args:
            existing_concepts: List of current course concept titles (refined originals)
            course_title: Title of the course for context
            course_description: Description of the course for context
            
        Returns:
            List of dictionaries with 'title' and 'difficulty_level' keys
        """
        try:
            # Build prompt for related topic generation
            concepts_text = "\n".join([f"- {concept}" for concept in existing_concepts])
            
            system_prompt = """You are an AI learning assistant that identifies related concepts for educational courses.

Given a course and its existing topics, suggest 5-8 related topics that would complement the learning journey. These should be:
1. Related to the existing topics but not duplicates
2. At appropriate difficulty levels (beginner, medium, advanced)
3. Valuable for deepening understanding of the subject area
4. Practical and actionable learning topics
5. Expand the learning scope without being too distant from the core topics

Respond with ONLY a valid JSON array in this format:
[
  {
    "title": "Related Topic Title",
    "difficulty_level": "beginner|medium|advanced"
  }
]

Do not include any explanations or additional text outside the JSON."""

            user_prompt = f"""Course: {course_title}
Description: {course_description}

Existing Topics:
{concepts_text}

Generate 5-8 related topics that would complement this learning path:"""

            response = self.client.messages.create(
                model=self.models['research'],
                max_tokens=800,
                temperature=0.7,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            # Parse the JSON response
            response_text = response.content[0].text.strip()
            
            # Try to extract JSON if there's extra text
            import json
            import re
            
            # Look for JSON array pattern
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            
            related_topics = json.loads(response_text)
            
            # Validate the response structure
            validated_topics = []
            for topic in related_topics:
                if isinstance(topic, dict) and 'title' in topic and 'difficulty_level' in topic:
                    # Validate difficulty level
                    if topic['difficulty_level'] in ['beginner', 'medium', 'advanced']:
                        # Only extract the fields we need, ignore any other fields from AI response
                        validated_topics.append({
                            'title': str(topic['title'])[:200],  # Ensure string and truncate to max length
                            'difficulty_level': str(topic['difficulty_level'])
                        })
            
            return validated_topics[:8]  # Limit to 8 related topics max
            
        except Exception as e:
            print(f"Error generating related topics: {e}")
            return []  # Return empty list on error

    def generate_adjacent_concepts(self, existing_concepts: List[str], course_description: str) -> List[Dict[str, str]]:
        """
        Legacy method - now delegates to generate_related_topics for backward compatibility
        
        Args:
            existing_concepts: List of current course concept titles
            course_description: Description of the course for context
            
        Returns:
            List of dictionaries with 'title' and 'difficulty_level' keys
        """
        # For backward compatibility, use the course description as both title and description
        return self.generate_related_topics(existing_concepts, "Course", course_description)
    
    def stream_concept_summary(
        self, 
        concept_title: str, 
        course_context: str = ""
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Stream AI-generated concept summaries for study content
        
        Args:
            concept_title: The concept to explain
            course_context: Optional course context for better explanations
            
        Yields:
            Dict with content, is_complete, and error fields
        """
        try:
            # Build prompt for concept explanation
            system_message = """You are an AI learning assistant that creates clear, comprehensive explanations of concepts for students.

Your task is to provide a detailed explanation of the given concept that includes:
1. A clear definition or overview
2. Key principles or components
3. Practical examples or applications
4. Common misconceptions or pitfalls to avoid
5. How it relates to broader topics

Make your explanation:
- Clear and accessible to learners
- Practical with real-world examples
- Comprehensive but not overwhelming. Don't make it too long.
- Engaging and educational

Use markdown formatting for better readability."""

            user_prompt = f"""Concept to explain: {concept_title}

{f"Course context: {course_context}" if course_context else ""}

Please provide a comprehensive explanation of this concept:"""

            # Build messages array (without system message)
            messages = [
                {"role": "user", "content": user_prompt}
            ]

            # Stream response from Anthropic with system message as separate parameter
            with self.client.messages.stream(
                model=self.models['research'],
                max_tokens=1500,
                temperature=0.7,
                system=system_message,
                messages=messages
            ) as stream:
                for text in stream.text_stream:
                    yield {
                        'content': text,
                        'is_complete': False,
                        'error': None
                    }
            
            # Send completion signal
            yield {
                'content': '',
                'is_complete': True,
                'error': None
            }
            
        except Exception as e:
            yield {
                'content': '',
                'is_complete': True,
                'error': str(e)
            }

    def stream_study_chat_response(
        self, 
        message: str,
        course_title: str = "",
        active_concept: str = "",
        message_history: Optional[List[Dict[str, str]]] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Stream AI responses for study chat
        
        Args:
            message: User's question or message
            course_title: Current course title for context
            active_concept: Currently active concept for context
            message_history: Previous conversation messages
            
        Yields:
            Dict with content, is_complete, and error fields
        """
        try:
            # Build context-aware system prompt
            context_parts = []
            if course_title:
                context_parts.append(f"Course: {course_title}")
            if active_concept:
                context_parts.append(f"Currently studying: {active_concept}")
            
            context_str = " | ".join(context_parts) if context_parts else "General study session"

            system_message = f"""You are an AI study assistant helping a student learn. 

Context: {context_str}

Your role is to:
- Answer questions clearly and helpfully
- Provide explanations tailored to the student's current study focus
- Offer examples and practical applications
- Encourage learning and understanding
- Ask follow-up questions when helpful
- Break down complex topics into manageable parts

Be supportive, educational, and engaging in your responses."""

            # Build message history (without system message in the messages array)
            messages = []
            
            # Add conversation history
            if message_history:
                for msg in message_history[-10:]:  # Keep last 10 messages for context
                    if msg.get('role') in ['user', 'assistant']:
                        messages.append({
                            "role": msg['role'],
                            "content": msg['content']
                        })
            
            # Add current message
            messages.append({"role": "user", "content": message})

            # Stream response from Anthropic
            with self.client.messages.stream(
                model=self.models['research'],
                max_tokens=1000,
                temperature=0.7,
                system=system_message,
                messages=messages
            ) as stream:
                for text in stream.text_stream:
                    yield {
                        'content': text,
                        'is_complete': False,
                        'error': None
                    }
            
            # Send completion signal
            yield {
                'content': '',
                'is_complete': True,
                'error': None
            }
            
        except Exception as e:
            yield {
                'content': '',
                'is_complete': True,
                'error': str(e)
            }

    def stream_teachback_chat_response(
        self, 
        message: str,
        course_title: str = "",
        active_concept: str = "",
        message_history: Optional[List[Dict[str, str]]] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Stream AI responses for TeachBack chat (teaching assistant)
        
        Args:
            message: User's question or message
            course_title: Current course title for context
            active_concept: Currently active concept being taught
            message_history: Previous conversation messages
            
        Yields:
            Dict with content, is_complete, and error fields
        """
        try:
            # Build context-aware system prompt for teaching assistance
            context_parts = []
            if course_title:
                context_parts.append(f"Course: {course_title}")
            if active_concept:
                context_parts.append(f"Teaching concept: {active_concept}")
            
            context_str = " | ".join(context_parts) if context_parts else "TeachBack session"

            system_message = f"""You are an AI teaching assistant helping a student practice the Feynman Technique.

Context: {context_str}

Your role is to:
- Provide feedback on student explanations of concepts
- Help students improve their teaching and explanation skills
- Ask probing questions to deepen understanding
- Identify gaps in explanations and suggest improvements
- Encourage clear, simple explanations that anyone could understand
- Guide students toward mastery through teaching practice

When a student submits an explanation:
- Highlight what they explained well
- Identify areas that need clarification or improvement
- Ask follow-up questions to test deeper understanding
- Suggest ways to make explanations clearer or more complete
- Encourage them to think about how they would teach it to different audiences

Be supportive but constructively critical. The goal is to help them truly master concepts by teaching them effectively."""

            # Build message history (without system message in the messages array)
            messages = []
            
            # Add conversation history
            if message_history:
                for msg in message_history[-10:]:  # Keep last 10 messages for context
                    if msg.get('role') in ['user', 'assistant']:
                        messages.append({
                            "role": msg['role'],
                            "content": msg['content']
                        })
            
            # Add current message
            messages.append({"role": "user", "content": message})

            # Stream response from Anthropic
            with self.client.messages.stream(
                model=self.models['research'],
                max_tokens=1200,
                temperature=0.7,
                system=system_message,
                messages=messages
            ) as stream:
                for text in stream.text_stream:
                    yield {
                        'content': text,
                        'is_complete': False,
                        'error': None
                    }
            
            # Send completion signal
            yield {
                'content': '',
                'is_complete': True,
                'error': None
            }
            
        except Exception as e:
            yield {
                'content': '',
                'is_complete': True,
                'error': str(e)
            }

    def generate_concept_summary(self, concept_title: str, course_context: str = "") -> str:
        """Generate concept summary (non-streaming)"""
        try:
            system_message = """You are an AI learning assistant that creates clear, comprehensive explanations of concepts for students.

Create a detailed explanation that includes:
1. Clear definition or overview
2. Key principles or components  
3. Practical examples or applications
4. Common misconceptions to avoid
5. How it relates to broader topics

Make it comprehensive but concise (aim for 200-400 words). Use markdown formatting."""

            user_prompt = f"""Concept: {concept_title}
{f"Course context: {course_context}" if course_context else ""}

Provide a comprehensive explanation:"""

            response = self.client.messages.create(
                model=self.models['research'],
                max_tokens=800,
                temperature=0.7,
                system=system_message,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            print(f"Error generating concept summary: {e}")
            return f"Error generating summary for {concept_title}"

    def generate_teaching_questions(self, concept_title: str, summary: str = "") -> List[str]:
        """Generate teaching questions for Feynman technique (non-streaming)"""
        try:
            system_message = """You are an AI learning assistant that creates teaching questions for the Feynman Technique.

Generate 1-3 questions that would help someone practice explaining this concept clearly. Questions should:
1. Test understanding of core principles
2. Encourage simple, clear explanations
3. Identify potential knowledge gaps
4. Be suitable for teaching to a beginner
5. Focus on practical application

Return ONLY a JSON array of question strings."""

            context = summary if summary else f"Concept: {concept_title}"
            user_prompt = f"""Context: {context}

Generate teaching questions for: {concept_title}"""

            response = self.client.messages.create(
                model=self.models['research'],
                max_tokens=400,
                temperature=0.7,
                system=system_message,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            # Parse JSON response
            import json
            import re
            
            response_text = response.content[0].text.strip()
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                questions = json.loads(json_match.group(0))
                return [q for q in questions if isinstance(q, str)][:3]  # Max 3 questions
            
            # Fallback if JSON parsing fails
            return [f"How would you explain {concept_title} to someone who has never heard of it?"]
            
        except Exception as e:
            print(f"Error generating teaching questions: {e}")
            return [f"How would you explain {concept_title} to someone who has never heard of it?"]

    def truncate_context(self, context: str, max_tokens: int = 3000) -> str:
        """Truncate context to fit within token limits"""
        estimated_tokens = self.count_tokens(context)
        
        if estimated_tokens <= max_tokens:
            return context
        
        # Truncate from the beginning, keeping the most recent content
        target_chars = max_tokens * 4
        if len(context) > target_chars:
            return "...[content truncated]...\n" + context[-target_chars:]
        
        return context
