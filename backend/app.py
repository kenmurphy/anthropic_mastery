from flask import Flask, jsonify
from flask_cors import CORS
from mongoengine import connect
from config import config
from routes import conversation_bp, clustering_bp, study_guide_bp
from routes.study_routes import study_bp
from routes.concept_routes import concept_bp
import os
import sys

def is_debugger_attached():
    """Check if we're running under a debugger"""
    return hasattr(sys, 'gettrace') and sys.gettrace() is not None

def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Enable CORS with specific configuration for SSE
    # Include both development and production origins
    allowed_origins = [
        'http://localhost:3000', 
        'http://localhost:5173', 
        'http://localhost:5175', 
        'http://127.0.0.1:3000', 
        'http://127.0.0.1:5173', 
        'http://127.0.0.1:5175'
    ]
    
    # Add production Vercel domain if specified
    vercel_domain = os.environ.get('VERCEL_DOMAIN')
    if vercel_domain:
        allowed_origins.extend([
            f'https://{vercel_domain}',
            f'https://{vercel_domain}.vercel.app'
        ])
    
    # Allow all Vercel preview deployments in production
    if config_name == 'production':
        allowed_origins.append('https://*.vercel.app')
    
    CORS(app, 
         origins=allowed_origins,
         allow_headers=['Content-Type', 'X-User-ID', 'Cache-Control'],
         expose_headers=['Cache-Control'],
         supports_credentials=True)
    
    # Initialize MongoDB connection
    try:
        connect(**app.config['MONGODB_SETTINGS'])
        print("Connected to MongoDB successfully")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise
    
    # Register blueprints
    app.register_blueprint(conversation_bp)
    app.register_blueprint(clustering_bp)
    app.register_blueprint(study_guide_bp)
    app.register_blueprint(study_bp)
    app.register_blueprint(concept_bp, url_prefix='/api')
    
    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'claude_backend',
            'version': '1.0.0'
        }), 200
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            'message': 'Welcome to Claude Backend API',
            'version': '1.0.0',
            'endpoints': {
                'conversations': '/api/conversations',
            }
        }), 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    host = app.config.get('APP_HOST', '0.0.0.0')
    port = app.config.get('APP_PORT', 5000)
    debug = app.config.get('DEBUG', True)
    
    # Check if we're running under a debugger
    debugger_attached = is_debugger_attached()
    
    # Disable Flask's reloader when debugging to prevent conflicts
    reloader_env = os.environ.get('FLASK_RUN_RELOAD')
    if reloader_env is not None:
        use_reloader = reloader_env.lower() == 'true'
    elif debugger_attached:
        use_reloader = False
    else:
        use_reloader = debug
    
    print(f"Starting Claude Backend on {host}:{port}")
    print(f"Debug mode: {debug}")
    print(f"Debugger attached: {debugger_attached}")
    print(f"Using reloader: {use_reloader}")
    
    if debugger_attached:
        print("VSCode debugger detected - disabling Flask reloader for better debugging experience")
    
    app.run(host=host, port=port, debug=debug, use_reloader=use_reloader)
