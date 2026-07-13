from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.gig import Gig
from app.models.tag import Tag
from app.models.user import User
from app.extensions import db

gigs_bp = Blueprint('gigs', __name__, url_prefix='/api/gigs')

@gigs_bp.route('', methods=['GET', 'OPTIONS'])
def get_gigs():
    if request.method == 'OPTIONS':
        return make_response(), 200
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        
        query = Gig.query.filter_by(is_active=True)
        
        if search:
            query = query.filter(
                Gig.title.ilike(f'%{search}%') | 
                Gig.description.ilike(f'%{search}%')
            )
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'gigs': [gig.to_dict() for gig in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }), 200
    except Exception as e:
        print(f"Error fetching gigs: {str(e)}")
        return jsonify({'error': str(e)}), 500

@gigs_bp.route('/<int:gig_id>', methods=['GET', 'OPTIONS'])
def get_gig(gig_id):
    if request.method == 'OPTIONS':
        return make_response(), 200
    
    try:
        gig = Gig.query.get(gig_id)
        if not gig or not gig.is_active:
            return jsonify({'error': 'Gig not found'}), 404
        return jsonify(gig.to_dict()), 200
    except Exception as e:
        print(f"Error fetching gig: {str(e)}")
        return jsonify({'error': str(e)}), 500

@gigs_bp.route('', methods=['POST', 'OPTIONS'])
@jwt_required()
def create_gig():
    if request.method == 'OPTIONS':
        return make_response(), 200
    
    try:
        data = request.get_json()
        print(f"📥 Received gig data: {data}")
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Get user ID from JWT
        try:
            current_user_id = get_jwt_identity()
            print(f"👤 User ID from token: {current_user_id}")
            
            # Convert to int if it's a string
            if isinstance(current_user_id, str):
                current_user_id = int(current_user_id)
        except Exception as e:
            print(f"❌ Error getting user ID: {str(e)}")
            return jsonify({'error': 'Invalid authentication'}), 401
        
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.role != 'freelancer':
            return jsonify({'error': 'Only freelancers can create gigs'}), 403
        
        # Validate required fields
        required_fields = ['title', 'description', 'price', 'delivery_days']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Parse and validate data
        try:
            title = str(data['title']).strip()
            description = str(data['description']).strip()
            price = float(data['price'])
            delivery_days = int(data['delivery_days'])
        except (ValueError, TypeError) as e:
            return jsonify({'error': f'Invalid data type: {str(e)}'}), 400
        
        if not title:
            return jsonify({'error': 'Title cannot be empty'}), 400
        if not description:
            return jsonify({'error': 'Description cannot be empty'}), 400
        if price <= 0:
            return jsonify({'error': 'Price must be greater than 0'}), 400
        if delivery_days <= 0:
            return jsonify({'error': 'Delivery days must be greater than 0'}), 400
        
        # Create the gig
        gig = Gig(
            title=title,
            description=description,
            price=price,
            delivery_days=delivery_days,
            user_id=current_user_id
        )
        
        # Handle tags
        if 'tags' in data and isinstance(data['tags'], list):
            for tag_name in data['tags']:
                if tag_name and str(tag_name).strip():
                    tag = Tag.query.filter_by(name=str(tag_name).lower().strip()).first()
                    if not tag:
                        tag = Tag(name=str(tag_name).lower().strip())
                        db.session.add(tag)
                    gig.tags.append(tag)
        
        db.session.add(gig)
        db.session.commit()
        print(f"✅ Gig created successfully: {gig.id}")
        
        return jsonify({
            'message': 'Gig created successfully',
            'gig': gig.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating gig: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@gigs_bp.route('/<int:gig_id>', methods=['PUT', 'OPTIONS'])
@jwt_required()
def update_gig(gig_id):
    if request.method == 'OPTIONS':
        return make_response(), 200
    
    try:
        current_user_id = get_jwt_identity()
        if isinstance(current_user_id, str):
            current_user_id = int(current_user_id)
        
        gig = Gig.query.get(gig_id)
        if not gig:
            return jsonify({'error': 'Gig not found'}), 404
        
        if gig.user_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        if 'title' in data:
            gig.title = str(data['title']).strip()
        if 'description' in data:
            gig.description = str(data['description']).strip()
        if 'price' in data:
            gig.price = float(data['price'])
        if 'delivery_days' in data:
            gig.delivery_days = int(data['delivery_days'])
        if 'is_active' in data:
            gig.is_active = bool(data['is_active'])
        
        if 'tags' in data and isinstance(data['tags'], list):
            gig.tags.clear()
            for tag_name in data['tags']:
                if tag_name and str(tag_name).strip():
                    tag = Tag.query.filter_by(name=str(tag_name).lower().strip()).first()
                    if not tag:
                        tag = Tag(name=str(tag_name).lower().strip())
                        db.session.add(tag)
                    gig.tags.append(tag)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Gig updated successfully',
            'gig': gig.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating gig: {str(e)}")
        return jsonify({'error': str(e)}), 500

@gigs_bp.route('/<int:gig_id>', methods=['DELETE', 'OPTIONS'])
@jwt_required()
def delete_gig(gig_id):
    if request.method == 'OPTIONS':
        return make_response(), 200
    
    try:
        current_user_id = get_jwt_identity()
        if isinstance(current_user_id, str):
            current_user_id = int(current_user_id)
        
        gig = Gig.query.get(gig_id)
        if not gig:
            return jsonify({'error': 'Gig not found'}), 404
        
        if gig.user_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        gig.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Gig deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting gig: {str(e)}")
        return jsonify({'error': str(e)}), 500