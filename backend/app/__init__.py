from flask import Flask, jsonify, request
from flask_cors import CORS
from app.config import Config
from app.extensions import db, migrate, jwt
from app.routes.auth import auth_bp
from app.routes.gigs import gigs_bp
from app.routes.orders import orders_bp
from app.routes.users import users_bp

def create_app():
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # CORS - Allow all origins
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(gigs_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(users_bp)
    
    # Error handler for 415 Unsupported Media Type
    @app.errorhandler(415)
    def handle_unsupported_media(e):
        return jsonify({
            'error': 'Unsupported Media Type',
            'message': 'Please set Content-Type header to application/json'
        }), 415
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'}), 200
    
    return app