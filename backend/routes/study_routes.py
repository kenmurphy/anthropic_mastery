from flask import Blueprint, jsonify, request, Response
from services.anthropic_service import AnthropicService
from services.study_guide_service import StudyGuideService
import json

study_bp = Blueprint('study', __name__, url_prefix='/api')

@study_bp.route('/concepts/summary', methods=['POST'])
def generate_concept_summary():
    """Generate AI-powered concept summary with streaming"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        concept_title = data.get('concept_title')
        course_id = data.get('course_id')
        
        if not concept_title:
            return jsonify({
                'success': False,
                'error': 'concept_title is required'
            }), 400
        
        # Get course context if course_id provided
        course_context = ""
        if course_id:
            try:
                course = StudyGuideService.get_course_by_id(course_id)
                course_context = f"Course: {course.title}\nDescription: {course.description}"
            except:
                # Continue without course context if course not found
                pass
        
        # Stream concept summary
        anthropic_service = AnthropicService()
        
        def generate():
            try:
                for chunk in anthropic_service.stream_concept_summary(concept_title, course_context):
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
