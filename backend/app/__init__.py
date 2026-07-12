from flask import Flask
from app.config import Config
from app.extensions import db, migrate, jwt, cors
from app.routes.auth import auth_bp
from app.routes.gigs import gigs_bp
from app.routes.orders import orders_bp
from app.routes.users import users_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Configure CORS to allow all origins (for development)
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Accept"],
            "supports_credentials": True
        },
        r"/health": {
            "origins": "*",
            "methods": ["GET"]
        }
    })
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(gigs_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(users_bp)
    
    @app.route('/health')
    def health():
        return {'status': 'healthy'}, 200
    
    return app