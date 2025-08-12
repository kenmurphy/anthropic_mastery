from flask import Blueprint, jsonify, request, Response
from services.study_guide_service import StudyGuideService
from services.anthropic_service import AnthropicService
import json

study_guide_bp = Blueprint('study_guide', __name__, url_prefix='/api')

@study_guide_bp.route('/study-guides', methods=['GET'])
def get_study_guides():
    """Get unified list of study guides (courses + available clusters)"""
    try:
        study_guides = StudyGuideService.get_study_guides()
        return jsonify({
            'success': True,
            'study_guides': study_guides,
            'total': len(study_guides)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@study_guide_bp.route('/study-guides/<item_id>/start', methods=['POST'])
def start_study_guide(item_id):
    """Start studying - create course from cluster or get existing course"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        item_type = data.get('type')
        if not item_type:
            return jsonify({
                'success': False,
                'error': 'Type is required'
            }), 400
        
        if item_type not in ['course', 'cluster']:
            return jsonify({
                'success': False,
                'error': 'Type must be either "course" or "cluster"'
            }), 400
        
        course = StudyGuideService.create_or_get_course(item_id, item_type)
        if not course:
            return jsonify({
                'success': False,
                'error': 'Failed to create or retrieve course'
            }), 404
        
        return jsonify({
            'success': True,
            'course': course.to_dict(),
            'message': 'Course ready'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@study_guide_bp.route('/courses/<course_id>', methods=['GET'])
def get_course(course_id):
    """Get course details by ID"""
    try:
        course = StudyGuideService.get_course_by_id(course_id)
        return jsonify({
            'success': True,
            'course': course.to_dict()
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@study_guide_bp.route('/courses/<course_id>/concepts/<concept_title>/status', methods=['PUT'])
def update_concept_status(course_id, concept_title):
    """Update the status of a specific concept in a course"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        new_status = data.get('status')
        if not new_status:
            return jsonify({
                'success': False,
                'error': 'Status is required'
            }), 400
        
        course = StudyGuideService.update_concept_status(course_id, concept_title, new_status)
        return jsonify({
            'success': True,
            'course': course.to_dict(),
            'message': f'Concept "{concept_title}" status updated to "{new_status}"'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@study_guide_bp.route('/concepts/status', methods=['PUT'])
def update_concept_status_simple():
    """Update the status of a specific concept in a course (simplified endpoint)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        concept_title = data.get('concept_title')
        course_id = data.get('course_id')
        new_status = data.get('status')
        
        if not concept_title:
            return jsonify({
                'success': False,
                'error': 'concept_title is required'
            }), 400
        
        if not course_id:
            return jsonify({
                'success': False,
                'error': 'course_id is required'
            }), 400
        
        if not new_status:
            return jsonify({
                'success': False,
                'error': 'status is required'
            }), 400
        
        course = StudyGuideService.update_concept_status(course_id, concept_title, new_status)
        return jsonify({
            'success': True,
            'course': course.to_dict(),
            'message': f'Concept "{concept_title}" status updated to "{new_status}"'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@study_guide_bp.route('/courses', methods=['GET'])
def get_all_courses():
    """Get all courses"""
    try:
        courses = StudyGuideService.get_all_courses()
        return jsonify({
            'success': True,
            'courses': courses,
            'total': len(courses)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@study_guide_bp.route('/courses/<course_id>/start-review', methods=['POST'])
def start_course_review(course_id):
    """Start review process for selected concepts in a course"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        selected_concept_titles = data.get('selected_concept_titles')
        if not selected_concept_titles:
            return jsonify({
                'success': False,
                'error': 'selected_concept_titles is required'
            }), 400
        
        if not isinstance(selected_concept_titles, list):
            return jsonify({
                'success': False,
                'error': 'selected_concept_titles must be a list'
            }), 400
        
        if len(selected_concept_titles) == 0:
            return jsonify({
                'success': False,
                'error': 'At least one concept must be selected'
            }), 400
        
        course = StudyGuideService.start_course_review(course_id, selected_concept_titles)
        return jsonify({
            'success': True,
            'course': course.to_dict(),
            'message': f'Review started for {len(selected_concept_titles)} concept(s)'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@study_guide_bp.route('/courses/<course_id>/update-selection', methods=['POST'])
def update_concept_selection(course_id):
    """Update concept selection - set selected concepts to 'reviewing' and unselected to 'not_started'"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        selected_concept_titles = data.get('selected_concept_titles')
        if selected_concept_titles is None:
            return jsonify({
                'success': False,
                'error': 'selected_concept_titles is required'
            }), 400
        
        if not isinstance(selected_concept_titles, list):
            return jsonify({
                'success': False,
                'error': 'selected_concept_titles must be a list'
            }), 400
        
        course = StudyGuideService.update_concept_selection(course_id, selected_concept_titles)
        return jsonify({
            'success': True,
            'course': course.to_dict(),
            'message': f'Updated selection: {len(selected_concept_titles)} concept(s) selected for review'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@study_guide_bp.route('/courses/<course_id>/related-topics', methods=['POST'])
def generate_related_topics(course_id):
    """Generate fresh related topics for a course asynchronously"""
    try:
        course = StudyGuideService.generate_fresh_related_topics(course_id)
        return jsonify({
            'success': True,
            'course': course.to_dict(),
            'message': 'Related topics generated successfully'
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@study_guide_bp.route('/courses/<course_id>/stage', methods=['PUT'])
def update_course_stage(course_id):
    """Update the current stage of a course"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        new_stage = data.get('stage')
        if not new_stage:
            return jsonify({
                'success': False,
                'error': 'stage is required'
            }), 400
        
        course = StudyGuideService.update_course_stage(course_id, new_stage)
        return jsonify({
            'success': True,
            'course': course.to_dict(),
            'message': f'Course stage updated to "{new_stage}"'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@study_guide_bp.route('/courses/<course_id>', methods=['DELETE'])
def delete_course(course_id):
    """Delete a course by ID"""
    try:
        StudyGuideService.delete_course(course_id)
        return jsonify({
            'success': True,
            'message': 'Course deleted successfully'
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@study_guide_bp.route('/teachback/submit-explanation', methods=['POST'])
def submit_explanation():
    """Submit explanation for feedback in TeachBack stage"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        concept_title = data.get('concept_title')
        teaching_question = data.get('teaching_question')
        user_explanation = data.get('user_explanation')
        course_id = data.get('course_id')
        
        if not concept_title:
            return jsonify({
                'success': False,
                'error': 'concept_title is required'
            }), 400
        
        if not teaching_question:
            return jsonify({
                'success': False,
                'error': 'teaching_question is required'
            }), 400
        
        if not user_explanation:
            return jsonify({
                'success': False,
                'error': 'user_explanation is required'
            }), 400
        
        # Get course for context
        course_title = ""
        if course_id:
            try:
                course = StudyGuideService.get_course_by_id(course_id)
                course_title = course.label
            except:
                pass  # Continue without course context if not found
        
        # Create feedback message for the AI
        feedback_message = f"""I just explained the concept "{concept_title}" in response to this teaching question:

**Question:** {teaching_question}

**My Explanation:**
{user_explanation}

Please provide constructive feedback on my explanation. What did I do well? What could be improved? Are there any important points I missed?"""

        # Stream feedback using the teachback chat response
        def generate_feedback():
            try:
                anthropic_service = AnthropicService()
                
                for chunk in anthropic_service.stream_teachback_chat_response(
                    message=feedback_message,
                    course_title=course_title,
                    active_concept=concept_title
                ):
                    if chunk.get('error'):
                        yield f"data: {json.dumps({'error': chunk['error']})}\n\n"
                        break
                    elif chunk.get('content'):
                        yield f"data: {json.dumps({'content': chunk['content']})}\n\n"
                    elif chunk.get('is_complete'):
                        yield f"data: {json.dumps({'is_complete': True})}\n\n"
                        break
                        
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(
            generate_feedback(),
            mimetype='text/plain',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST'
            }
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
