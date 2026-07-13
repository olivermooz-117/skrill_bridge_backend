from flask import Flask, jsonify
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
    
    # Configure CORS properly - Allow all origins for development
    CORS(app, 
         resources={r"/*": {
             "origins": "*",
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
             "allow_headers": ["Content-Type", "Authorization", "Accept", "X-Requested-With"],
             "expose_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True,
             "max_age": 3600
         }})
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(gigs_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(users_bp)
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'}), 200
    
    return app