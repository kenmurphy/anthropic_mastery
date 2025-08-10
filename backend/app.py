from flask import Flask, jsonify
from flask_cors import CORS
from mongoengine import connect
from config import config
from routes import conversation_bp
import os

def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Enable CORS with specific configuration for SSE
    CORS(app, 
         origins=['http://localhost:3000', 'http://localhost:5173', 'http://127.0.0.1:3000', 'http://127.0.0.1:5173'],
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
    
    print(f"Starting Claude Backend on {host}:{port}")
    print(f"Debug mode: {debug}")
    
    app.run(host=host, port=port, debug=debug)
