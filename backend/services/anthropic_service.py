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
