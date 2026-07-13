from flask import Blueprint, request, jsonify, current_app, make_response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, decode_token
from app.models.user import User
from app.extensions import db

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return make_response(), 200
    
    data = request.get_json()
    
    if not data or not all(k in data for k in ('name', 'email', 'password', 'role')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    user = User(
        name=str(data['name']),
        email=str(data['email']),
        role=str(data['role']),
        bio=str(data.get('bio', ''))
    )
    user.set_password(str(data['password']))
    
    db.session.add(user)
    db.session.commit()
    
    # Create access token with proper subject
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict(),
        'access_token': access_token
    }), 201

@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return make_response(), 200
    
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 403
    
    # Create access token with proper subject
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/me', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_current_user():
    if request.method == 'OPTIONS':
        return make_response(), 200
    
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(user.to_dict()), 200
    except Exception as e:
        print(f"Error in /me: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/password-reset/request', methods=['POST', 'OPTIONS'])
def request_password_reset():
    if request.method == 'OPTIONS':
        return make_response(), 200
    
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email required'}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Email not found'}), 404
    
    reset_token = create_access_token(identity=str(user.id), expires_delta=False)
    frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5181')
    reset_link = f"{frontend_url}/password-reset/confirm?token={reset_token}"
    
    return jsonify({
        'message': 'Password reset link sent',
        'reset_link': reset_link
    }), 200

@auth_bp.route('/password-reset/confirm', methods=['POST', 'OPTIONS'])
def confirm_password_reset():
    if request.method == 'OPTIONS':
        return make_response(), 200
    
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')
    
    if not token or not new_password:
        return jsonify({'error': 'Token and new password required'}), 400
    
    if len(new_password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    try:
        decoded = decode_token(token)
        user_id = decoded['sub']
        user = User.query.get(int(user_id))
        
        if not user:
            return jsonify({'error': 'Invalid token'}), 400
        
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({'message': 'Password reset successful'}), 200
    except Exception as e:
        print(f"Error in password reset: {str(e)}")
        return jsonify({'error': 'Invalid or expired token'}), 400
