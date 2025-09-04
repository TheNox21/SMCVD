import os
from flask import Flask, send_from_directory
from flask_cors import CORS

# Blueprint imports (after we add/move files into src/routes)
from src.routes.analysis import analysis_bp
from src.routes.github import github_bp
from src.routes.upload import upload_bp
from src.routes.report import report_bp


def create_app() -> Flask:
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))

    # Config from environment
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-change-me')

    # Enable CORS (restrict in production via CORS_ORIGINS)
    cors_origins = os.getenv('CORS_ORIGINS', '*')
    CORS(app, resources={r"/api/*": {"origins": cors_origins}})

    # Register blueprints
    app.register_blueprint(analysis_bp, url_prefix='/api')
    app.register_blueprint(github_bp, url_prefix='/api')
    app.register_blueprint(upload_bp, url_prefix='/api')
    app.register_blueprint(report_bp, url_prefix='/api')

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
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5000')), debug=os.getenv('FLASK_DEBUG', 'true').lower() == 'true')


