from flask import Blueprint, jsonify, request, Response
from services.anthropic_service import AnthropicService
from services.study_guide_service import StudyGuideService
import json

study_bp = Blueprint('study', __name__, url_prefix='/api')

@study_bp.route('/concepts/summary', methods=['POST'])
def generate_concept_summary():
    """Generate AI-powered concept summary with streaming, using cached summary when available"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        concept_title = data.get('concept_title')
        course_id = data.get('course_id')
        force_regenerate = data.get('force_regenerate', False)
        
        if not concept_title:
            return jsonify({
                'success': False,
                'error': 'concept_title is required'
            }), 400
        
        # Get course and concept
        course = None
        concept = None
        if course_id:
            try:
                course = StudyGuideService.get_course_by_id(course_id)
                concept = course.get_concept_by_title(concept_title)
            except:
                # Continue without course context if course not found
                pass
        
        # Check if we have a cached summary and don't need to regenerate
        if concept and concept.has_summary() and not force_regenerate:
            def generate_cached():
                # Return cached summary immediately
                cached_chunk = {
                    'content': concept.summary,
                    'is_complete': True,
                    'cached': True
                }
                yield f"data: {json.dumps(cached_chunk)}\n\n"
            
            return Response(
                generate_cached(),
                mimetype='text/plain',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Access-Control-Allow-Origin': '*'
                }
            )
        
        # Generate new summary
        course_context = ""
        if course:
            course_context = f"Course: {course.label}\nDescription: {course.description}"
        
        anthropic_service = AnthropicService()
        
        def generate():
            try:
                accumulated_summary = ""
                for chunk in anthropic_service.stream_concept_summary(concept_title, course_context):
                    # Accumulate content for saving
                    if chunk.get('content'):
                        accumulated_summary += chunk['content']
                    
                    yield f"data: {json.dumps(chunk)}\n\n"
                    
                    # Save summary when complete
                    if chunk.get('is_complete') and concept and course and accumulated_summary.strip():
                        concept.set_summary(accumulated_summary.strip())
                        course.save()
                        
            except Exception as e:
                error_chunk = {
                    'content': '',
                    'is_complete': True,
                    'error': str(e)
                }
                yield f"data: {json.dumps(error_chunk)}\n\n"
        
        return Response(
            generate(),
            mimetype='text/plain',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*'
            }
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@study_bp.route('/study/chat', methods=['POST'])
def study_chat():
    """Handle study chat with streaming responses"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        message = data.get('message')
        course_title = data.get('course_title', '')
        active_concept = data.get('active_concept', '')
        message_history = data.get('message_history', [])
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'message is required'
            }), 400
        
        # Stream study chat response
        anthropic_service = AnthropicService()
        
        def generate():
            try:
                for chunk in anthropic_service.stream_study_chat_response(
                    message=message,
                    course_title=course_title,
                    active_concept=active_concept,
                    message_history=message_history
                ):
                    yield f"data: {json.dumps(chunk)}\n\n"
            except Exception as e:
                error_chunk = {
                    'content': '',
                    'is_complete': True,
                    'error': str(e)
                }
                yield f"data: {json.dumps(error_chunk)}\n\n"
        
        return Response(
            generate(),
            mimetype='text/plain',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*'
            }
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
