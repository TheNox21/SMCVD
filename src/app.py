import os
import sys
from pathlib import Path
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# New imports for improvements
try:
    from src.utils.logging import setup_logging, get_logger
    from src.config.settings import config
except ImportError:
    # Fallback for missing modules
    def setup_logging(): pass
    def get_logger(name): 
        import logging
        return logging.getLogger(name)
    
    class MockConfig:
        class api:
            host = "0.0.0.0"
            port = 5000
            debug = False
            cors_origins = "*"
            secret_key = "dev-secret-change-me"
    config = MockConfig()

# Blueprint imports (after we add/move files into src/routes)
from src.routes.analysis import analysis_bp
from src.routes.github import github_bp
from src.routes.upload import upload_bp
from src.routes.report import report_bp


def create_app() -> Flask:
    # Initialize logging first
    setup_logging()
    logger = get_logger(__name__)
    logger.info("Starting SMCVD application...")
    
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))

    # Apply configuration
    try:
        app.config['SECRET_KEY'] = config.api.secret_key
        app.config['DEBUG'] = config.api.debug
        cors_origins = config.api.cors_origins
    except Exception as e:
        logger.warning(f"Using fallback config: {e}")
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-change-me')
        cors_origins = os.getenv('CORS_ORIGINS', '*')

    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": cors_origins}})

    # Register blueprints
    app.register_blueprint(analysis_bp, url_prefix='/api')
    app.register_blueprint(github_bp, url_prefix='/api')
    app.register_blueprint(upload_bp, url_prefix='/api')
    app.register_blueprint(report_bp, url_prefix='/api')
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'version': '2.0.0',
            'features': {
                'ai_enabled': os.getenv('ENABLE_AI', 'true').lower() == 'true',
                'db_persistence': True
            }
        })

    # Serve static index.html if present
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        static_folder_path = app.static_folder
        if static_folder_path is None:
            return "Static folder not configured", 404

        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                return "index.html not found", 404

    return app


if __name__ == '__main__':
    app = create_app()
    try:
        host = config.api.host
        port = config.api.port
        debug = config.api.debug
    except:
        host = '0.0.0.0'
        port = int(os.getenv('PORT', '5000'))
        debug = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
    
    print(f"\n🚀 Starting SMCVD on http://{host}:{port}")
    print(f"📊 Health check: http://{host}:{port}/api/health")
    app.run(host=host, port=port, debug=debug)


