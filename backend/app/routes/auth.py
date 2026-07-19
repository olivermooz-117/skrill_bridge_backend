from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from app.models.user import User
from app.extensions import db
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    # Get JSON data
    data = request.get_json()
    
    # Check if data exists
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    # Validate required fields
    if not all(k in data for k in ('name', 'email', 'password', 'role')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate email
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['email']):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Check if user exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    # Create user
    user = User(
        name=data['name'],
        email=data['email'],
        role=data['role'],
        bio=data.get('bio', '')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict(),
        'access_token': access_token
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 403
    
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'access_token': access_token
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict()), 200

@auth_bp.route('/password-reset/request', methods=['POST'])
def request_password_reset():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email required'}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Email not found'}), 404
    
    reset_token = create_access_token(identity=user.id, expires_delta=False)
    reset_link = f"http://localhost:5173/password-reset/confirm?token={reset_token}"
    
    return jsonify({
        'message': 'Password reset link sent',
        'reset_link': reset_link
    }), 200

@auth_bp.route('/password-reset/confirm', methods=['POST'])
def confirm_password_reset():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    token = data.get('token')
    new_password = data.get('new_password')
    
    if not token or not new_password:
        return jsonify({'error': 'Token and new password required'}), 400
    
    if len(new_password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    try:
        from flask_jwt_extended import decode_token
        decoded = decode_token(token)
        user_id = decoded['sub']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Invalid token'}), 400
        
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({'message': 'Password reset successful'}), 200
    except Exception as e:
        return jsonify({'error': 'Invalid or expired token'}), 400