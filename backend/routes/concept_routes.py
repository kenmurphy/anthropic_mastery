from flask import Blueprint, request, jsonify, Response
import json
from models.course import Course
from services.anthropic_service import AnthropicService

concept_bp = Blueprint('concept', __name__)

@concept_bp.route('/courses/<course_id>/concepts/<concept_title>/summary/stream', methods=['GET'])
def stream_concept_summary(course_id, concept_title):
    """Stream concept summary generation"""
    try:
        # Get course and concept
        course = Course.objects(id=course_id).first()
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        concept = course.get_concept_by_title(concept_title)
        if not concept:
            return jsonify({'error': 'Concept not found'}), 404
        
        # Check if already streaming
        if getattr(concept, 'is_streaming_summary', False):
            return jsonify({'error': 'Summary generation already in progress'}), 409
        
        # Set streaming flag
        concept.is_streaming_summary = True
        course.save()
        
        anthropic_service = AnthropicService()
        
        def generate():
            try:
                full_content = ""
                for chunk in anthropic_service.stream_concept_summary(
                    concept_title, 
                    course.description
                ):
                    if chunk.get('content'):
                        full_content += chunk['content']
                    yield f"data: {json.dumps(chunk)}\n\n"
                    
                    if chunk.get('is_complete'):
                        # Reload course to get fresh state
                        fresh_course = Course.objects(id=course_id).first()
                        fresh_concept = fresh_course.get_concept_by_title(concept_title)
                        
                        if fresh_concept:
                            # Save the complete summary
                            fresh_concept.set_summary(full_content)
                            fresh_concept.is_streaming_summary = False
                            fresh_course.save()
                        break
                        
            except Exception as e:
                # Clear streaming flag on error
                try:
                    error_course = Course.objects(id=course_id).first()
                    error_concept = error_course.get_concept_by_title(concept_title)
                    if error_concept:
                        error_concept.is_streaming_summary = False
                        error_course.save()
                except:
                    pass
                
                yield f"data: {json.dumps({'error': str(e), 'is_complete': True})}\n\n"
        
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
        return jsonify({'error': str(e)}), 500

@concept_bp.route('/courses/<course_id>/concepts/<concept_title>/questions/stream', methods=['GET'])
def stream_concept_questions(course_id, concept_title):
    """Stream teaching questions generation"""
    try:
        # Get course and concept
        course = Course.objects(id=course_id).first()
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        concept = course.get_concept_by_title(concept_title)
        if not concept:
            return jsonify({'error': 'Concept not found'}), 404
        
        # Check if already streaming
        if getattr(concept, 'is_streaming_questions', False):
            return jsonify({'error': 'Questions generation already in progress'}), 409
        
        # Set streaming flag
        concept.is_streaming_questions = True
        course.save()
        
        anthropic_service = AnthropicService()
        
        def generate():
            try:
                # Use existing summary if available, or concept title as context
                context = getattr(concept, 'summary', None) or f"Concept: {concept_title}"
                
                # Generate questions (non-streaming for now, but we can make it streaming later)
                questions = anthropic_service.generate_teaching_questions(
                    concept_title, 
                    str(context)
                )
                
                # Send questions as streaming response
                yield f"data: {json.dumps({'content': json.dumps(questions), 'is_complete': False, 'error': None})}\n\n"
                
                # Reload course to get fresh state
                fresh_course = Course.objects(id=course_id).first()
                fresh_concept = fresh_course.get_concept_by_title(concept_title)
                
                if fresh_concept:
                    # Save the questions
                    fresh_concept.set_teaching_questions(questions)
                    fresh_concept.is_streaming_questions = False
                    fresh_course.save()
                
                # Send completion signal
                yield f"data: {json.dumps({'content': '', 'is_complete': True, 'error': None})}\n\n"
                        
            except Exception as e:
                # Clear streaming flag on error
                try:
                    error_course = Course.objects(id=course_id).first()
                    error_concept = error_course.get_concept_by_title(concept_title)
                    if error_concept:
                        error_concept.is_streaming_questions = False
                        error_course.save()
                except:
                    pass
                
                yield f"data: {json.dumps({'error': str(e), 'is_complete': True})}\n\n"
        
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
        return jsonify({'error': str(e)}), 500

@concept_bp.route('/courses/<course_id>/concepts/<concept_title>/content', methods=['GET'])
def get_concept_content(course_id, concept_title):
    """Get current concept content (summary and questions)"""
    try:
        # Get course and concept
        course = Course.objects(id=course_id).first()
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        concept = course.get_concept_by_title(concept_title)
        if not concept:
            return jsonify({'error': 'Concept not found'}), 404
        
        # Return current content state
        return jsonify({
            'summary': getattr(concept, 'summary', None),
            'summary_generated_at': concept.summary_generated_at.isoformat() if getattr(concept, 'summary_generated_at', None) else None,
            'teaching_questions': getattr(concept, 'teaching_questions', None),
            'teaching_questions_generated_at': concept.teaching_questions_generated_at.isoformat() if getattr(concept, 'teaching_questions_generated_at', None) else None,
            'is_streaming_summary': getattr(concept, 'is_streaming_summary', False),
            'is_streaming_questions': getattr(concept, 'is_streaming_questions', False)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
