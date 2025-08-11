import os
import json
import difflib
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
    
    def stream_research(
        self, 
        thread_context: str, 
        selected_text: str, 
        message: str, 
        conversation_history: List[Dict],
        last_updated_Thought: Dict = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Stream AI research responses for sidebar chat
        
        Args:
            thread_context: Full thread content for context
            selected_text: User's selected text
            message: User's question/instruction
            conversation_history: Previous conversation messages
            last_updated_Thought: Last updated thought context
            
        Yields:
            Dict with content, is_complete, and error fields
        """
        try:
            # Build conversation messages
            messages = self._build_research_messages(
                thread_context, selected_text, message, conversation_history, last_updated_Thought
            )
            
            # Extract system message if present
            system_message = None
            if messages and messages[0].get('role') == 'system':
                system_message = messages[0]['content']
                messages = messages[1:]  # Remove system message from messages list
            
            # Stream response from Anthropic
            with self.client.messages.stream(
                model=self.models['research'],
                max_tokens=2000,
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
    
    def stream_snippet_edit(
        self, 
        text: str, 
        selected_text: str, 
        instruction: str
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Stream AI snippet edits for Command-K functionality
        
        Args:
            text: Full Thought content
            selected_text: Highlighted text to edit
            instruction: User's edit instruction
            
        Yields:
            Dict with original_text, edited_text, diff_operations, is_complete, error
        """
        try:
            # Build edit prompt
            messages = self._build_snippet_messages(text, selected_text, instruction)
            
            # Extract system message if present
            system_message = None
            if messages and messages[0].get('role') == 'system':
                system_message = messages[0]['content']
                messages = messages[1:]
            
            accumulated_content = ""
            
            # Stream response from Anthropic
            with self.client.messages.stream(
                model=self.models['snippets'],
                max_tokens=1000,
                temperature=0.3,  # Lower temperature for more consistent edits
                system=system_message,
                messages=messages
            ) as stream:
                for text in stream.text_stream:
                    accumulated_content += text
                    
                    yield {
                        'original_text': selected_text,
                        'edited_text': accumulated_content,
                        'diff_operations': [],  # Will be computed on completion
                        'is_complete': False,
                        'error': None
                    }
            
            # Compute final diff operations
            diff_ops = self._compute_diff_operations(selected_text, accumulated_content)
            
            # Send completion with diff
            yield {
                'original_text': selected_text,
                'edited_text': accumulated_content,
                'diff_operations': diff_ops,
                'is_complete': True,
                'error': None
            }
            
        except Exception as e:
            yield {
                'original_text': selected_text,
                'edited_text': '',
                'diff_operations': [],
                'is_complete': True,
                'error': str(e)
            }
    
    def stream_card_response(
        self, 
        thread_context: str, 
        card_type: str, 
        focus_instruction: str = ""
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Stream AI card responses for additional AI cards
        
        Args:
            thread_context: Full thread content
            card_type: Type of card (summary, questions, etc.)
            focus_instruction: Optional focus instruction
            
        Yields:
            Dict with content, card_type, is_complete, error
        """
        try:
            # Build card-specific prompt
            messages = self._build_card_messages(thread_context, card_type, focus_instruction)
            
            # Extract system message if present
            system_message = None
            if messages and messages[0].get('role') == 'system':
                system_message = messages[0]['content']
                messages = messages[1:]
            
            # Stream response from Anthropic
            with self.client.messages.stream(
                model=self.models['cards'],
                max_tokens=1500,
                temperature=0.7,
                system=system_message,
                messages=messages
            ) as stream:
                for text in stream.text_stream:
                    yield {
                        'content': text,
                        'card_type': card_type,
                        'is_complete': False,
                        'error': None
                    }
            
            # Send completion signal
            yield {
                'content': '',
                'card_type': card_type,
                'is_complete': True,
                'error': None
            }
            
        except Exception as e:
            yield {
                'content': '',
                'card_type': card_type,
                'is_complete': True,
                'error': str(e)
            }
    
    def _build_research_messages(
        self, 
        thread_context: str, 
        selected_text: str, 
        message: str, 
        conversation_history: List[Dict],
        last_updated_Thought: Dict = None
    ) -> List[Dict[str, str]]:
        """Build messages for research API"""
        
        # Build a simplified system prompt that focuses on the last updated Thought (if any)
        target_Thought_id = last_updated_Thought.get('id') if last_updated_Thought else None
        Thought_text = ""
        if last_updated_Thought and last_updated_Thought.get('content'):
            Thought_content = last_updated_Thought.get('content', {})
            Thought_text = Thought_content.get('text', '') or str(Thought_content)

        system_prompt_parts = [
            "You are an AI writing assistant for a note-taking system.",
            "",
            "Context:",
        ]

        if target_Thought_id and Thought_text.strip():
            system_prompt_parts.append(
                f"The user just updated this Thought (ID: {target_Thought_id}): {Thought_text.strip()}"
            )

        system_prompt_parts.append(f"Full thread context: {thread_context}")

        if selected_text:
            system_prompt_parts.append(f"User's selected text: \"{selected_text}\"")
        else:
            system_prompt_parts.append("No text currently selected.")

        system_prompt_parts.extend([
            "",
            "Instructions:",
            "- Focus first on the Thought the user just updated (if provided).",
            "- Answer any user questions. Use full prose when the topic needs depth,",
            "  then add a *note-version* summary (concise bullet points or fragments).",
            "- Suggest specific text that could be inserted into that Thought, always in concise note style.",
            "- If the current Thought is missing or unrelated, consider the broader thread context.",
            "- Keep every suggestion actionable and concrete.",
            "- If your suggestion is effectively identical to the current Thought, treat it as a no-op:",
            "  * Return that text as the `content`, and set `suggestions` to an empty array.",
            "",
            "NOTE STYLE GUIDELINES (for summaries & suggestions):",
            "- Prefer Markdown bullets (\"- \") or numbered steps.",
            "- One idea per line; omit filler words.",
            "- Sentence fragments are fine if meaning is clear (e.g., \"Add hook about user benefit\").",
            "",
            "RESPONSE FORMAT (respond ONLY with valid JSON):",
            "{",
            '  "content": "<full answer (if needed) **plus** note-version summary or identical text>",',
            '  "suggestions": [',
            "    {",
            '      "title": "<Short suggestion title>",',
            '      "Thought_id": "<Thought id if suggestion applies to a specific Thought, else null>",',
            '      "suggestion": "<Concrete, note-style text to insert into the Thought>"',
            "    }",
            "    // ... more suggestions",
            "  ]",
            "}",
            "",
            "Do not include any explanations outside the JSON. Be concise, practical, and consistent."
        ])

        system_prompt = "\n".join(system_prompt_parts)
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for item in conversation_history:
            if item.get('role') in ['user', 'assistant']:
                messages.append({
                    "role": item['role'],
                    "content": item['content']
                })
        
        # Add current user message
        messages.append({"role": "user", "content": message})
        
        return messages
    
    def _build_snippet_messages(
        self, 
        text: str, 
        selected_text: str, 
        instruction: str
    ) -> List[Dict[str, str]]:
        """Build messages for snippet editing"""
        
        system_prompt = """You are an AI assistant that helps edit text based on user instructions. 
        
Your task is to:
1. Take the selected text and apply the user's instruction
2. Return ONLY the edited version of the selected text
3. Maintain the original meaning unless explicitly asked to change it
4. Keep the same tone and style unless instructed otherwise
5. Be precise and focused on the specific instruction

Do not add explanations or commentary - just return the edited text."""

        user_prompt = f"""Full context: {text}

Selected text to edit: "{selected_text}"

Instruction: {instruction}

Please edit the selected text according to the instruction:"""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    
    def _build_card_messages(
        self, 
        thread_context: str, 
        card_type: str, 
        focus_instruction: str
    ) -> List[Dict[str, str]]:
        """Build messages for card generation"""
        
        card_prompts = {
            'summary': "Provide a concise summary of the main points and key takeaways from this content.",
            'questions': "Generate thoughtful questions that would help deepen understanding of this content.",
            'insights': "Identify key insights, patterns, or connections within this content.",
            'connections': "Suggest how this content connects to broader topics, concepts, or fields of study.",
            'next_steps': "Recommend next steps, further research, or actions based on this content."
        }
        
        base_prompt = card_prompts.get(card_type, "Analyze this content and provide helpful insights.")
        
        if focus_instruction:
            base_prompt += f" Focus specifically on: {focus_instruction}"
        
        system_prompt = f"""You are an AI assistant helping with content analysis and learning. 
        
Your task is to analyze the provided content and {base_prompt}

Be specific, actionable, and helpful. Structure your response clearly with bullet points or numbered lists when appropriate."""

        user_prompt = f"""Content to analyze:
{thread_context}

Please provide your analysis:"""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    
    def _compute_diff_operations(self, original: str, edited: str) -> List[Dict[str, str]]:
        """Compute diff operations between original and edited text"""
        
        differ = difflib.SequenceMatcher(None, original, edited)
        operations = []
        
        for tag, i1, i2, j1, j2 in differ.get_opcodes():
            if tag == 'equal':
                operations.append({
                    'operation': 'equal',
                    'text': original[i1:i2]
                })
            elif tag == 'delete':
                operations.append({
                    'operation': 'delete',
                    'text': original[i1:i2]
                })
            elif tag == 'insert':
                operations.append({
                    'operation': 'insert',
                    'text': edited[j1:j2]
                })
            elif tag == 'replace':
                # Split replace into delete + insert
                operations.append({
                    'operation': 'delete',
                    'text': original[i1:i2]
                })
                operations.append({
                    'operation': 'insert',
                    'text': edited[j1:j2]
                })
        
        return operations
    
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
            system_message = "You are Claude, a helpful AI assistant created by Anthropic. Provide helpful, accurate, and engaging responses to user questions and requests."
            
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
                        validated_topics.append({
                            'title': topic['title'][:200],  # Truncate to max length
                            'difficulty_level': topic['difficulty_level']
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
            system_prompt = """You are an AI learning assistant that creates clear, comprehensive explanations of concepts for students.

Your task is to provide a detailed explanation of the given concept that includes:
1. A clear definition or overview
2. Key principles or components
3. Practical examples or applications
4. Common misconceptions or pitfalls to avoid
5. How it relates to broader topics

Make your explanation:
- Clear and accessible to learners
- Well-structured with headings or bullet points
- Practical with real-world examples
- Comprehensive but not overwhelming
- Engaging and educational

Use markdown formatting for better readability."""

            user_prompt = f"""Concept to explain: {concept_title}

{f"Course context: {course_context}" if course_context else ""}

Please provide a comprehensive explanation of this concept:"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            # Stream response from Anthropic
            with self.client.messages.stream(
                model=self.models['research'],
                max_tokens=1500,
                temperature=0.7,
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

            system_prompt = f"""You are an AI study assistant helping a student learn. 

Context: {context_str}

Your role is to:
- Answer questions clearly and helpfully
- Provide explanations tailored to the student's current study focus
- Offer examples and practical applications
- Encourage learning and understanding
- Ask follow-up questions when helpful
- Break down complex topics into manageable parts

Be supportive, educational, and engaging in your responses."""

            # Build message history
            messages = [{"role": "system", "content": system_prompt}]
            
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
