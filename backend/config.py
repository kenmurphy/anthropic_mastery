import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # MongoDB Configuration
    MONGODB_SETTINGS = {
        'host': os.environ.get('MONGODB_HOST', 'localhost'),
        'port': int(os.environ.get('MONGODB_PORT', 27017)),
        'db': os.environ.get('MONGODB_DB', 'claude_db'),
        'username': os.environ.get('MONGODB_USERNAME'),
        'password': os.environ.get('MONGODB_PASSWORD'),
        'authentication_source': os.environ.get('MONGODB_AUTH_SOURCE', 'admin')
    }
    
    # Application Configuration
    APP_HOST = os.environ.get('APP_HOST', '0.0.0.0')
    APP_PORT = int(os.environ.get('APP_PORT', 5000))
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # AI Services Configuration
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    
    # MongoDB Database Names
    MONGODB_DB = os.environ.get('MONGODB_DB', 'anthropic_mastery_db')
    MONGODB_HOST = os.environ.get('MONGODB_HOST', 'localhost')
    MONGODB_PORT = int(os.environ.get('MONGODB_PORT', 27017))
    MONGODB_USERNAME = os.environ.get('MONGODB_USERNAME')
    MONGODB_PASSWORD = os.environ.get('MONGODB_PASSWORD')

    # Clustering settings
    CLUSTERING_AUTO_K = True
    CLUSTERING_MIN_K = 2
    CLUSTERING_MAX_K = 12
    CLUSTERING_K = 5  # used only if CLUSTERING_AUTO_K is False
    
    # Background clustering settings
    BACKGROUND_CLUSTERING_ENABLED = os.environ.get('BACKGROUND_CLUSTERING_ENABLED', 'true').lower() == 'true'
    CLUSTERING_MESSAGE_THRESHOLD = int(os.environ.get('CLUSTERING_MESSAGE_THRESHOLD', '1'))
    CLUSTERING_TIME_THRESHOLD_MINUTES = int(os.environ.get('CLUSTERING_TIME_THRESHOLD_MINUTES', '5'))

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
