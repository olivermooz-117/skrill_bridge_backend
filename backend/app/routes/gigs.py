from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.gig import Gig
from app.models.tag import Tag
from app.models.user import User
from app.extensions import db
from app.utils.decorators import role_required

gigs_bp = Blueprint('gigs', __name__, url_prefix='/api/gigs')

@gigs_bp.route('/', methods=['GET'])
def get_gigs():
    """GET endpoint 1: List all gigs with search/filter"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    tag = request.args.get('tag', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    query = Gig.query.filter_by(is_active=True)
    
    if search:
        query = query.filter(Gig.title.ilike(f'%{search}%') | Gig.description.ilike(f'%{search}%'))
    if tag:
        query = query.join(Gig.tags).filter(Tag.name == tag)
    if min_price:
        query = query.filter(Gig.price >= min_price)
    if max_price:
        query = query.filter(Gig.price <= max_price)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'gigs': [gig.to_dict() for gig in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200

@gigs_bp.route('/<int:gig_id>', methods=['GET'])
def get_gig(gig_id):
    """GET endpoint 2: Get single gig by ID"""
    gig = Gig.query.get(gig_id)
    if not gig or not gig.is_active:
        return jsonify({'error': 'Gig not found'}), 404
    return jsonify(gig.to_dict()), 200

@gigs_bp.route('/', methods=['POST'])
@jwt_required()
def create_gig():
    """POST endpoint 1: Create a new gig"""
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    # Check if user is freelancer
    user = User.query.get(current_user_id)
    if user.role != 'freelancer':
        return jsonify({'error': 'Only freelancers can create gigs'}), 403
    
    required_fields = ['title', 'description', 'price', 'delivery_days']
    if not all(k in data for k in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    gig = Gig(
        title=data['title'],
        description=data['description'],
        price=data['price'],
        delivery_days=data['delivery_days'],
        user_id=current_user_id
    )
    
    # Handle tags
    if 'tags' in data and isinstance(data['tags'], list):
        for tag_name in data['tags']:
            tag = Tag.query.filter_by(name=tag_name.lower()).first()
            if not tag:
                tag = Tag(name=tag_name.lower())
                db.session.add(tag)
            gig.tags.append(tag)
    
    db.session.add(gig)
    db.session.commit()
    
    return jsonify({
        'message': 'Gig created successfully',
        'gig': gig.to_dict()
    }), 201

@gigs_bp.route('/<int:gig_id>', methods=['PUT'])
@jwt_required()
def update_gig(gig_id):
    """PUT endpoint 1: Update a gig"""
    current_user_id = get_jwt_identity()
    gig = Gig.query.get(gig_id)
    
    if not gig:
        return jsonify({'error': 'Gig not found'}), 404
    
    if gig.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Update fields
    if 'title' in data:
        gig.title = data['title']
    if 'description' in data:
        gig.description = data['description']
    if 'price' in data:
        gig.price = data['price']
    if 'delivery_days' in data:
        gig.delivery_days = data['delivery_days']
    if 'is_active' in data:
        gig.is_active = data['is_active']
    
    # Update tags
    if 'tags' in data and isinstance(data['tags'], list):
        gig.tags.clear()
        for tag_name in data['tags']:
            tag = Tag.query.filter_by(name=tag_name.lower()).first()
            if not tag:
                tag = Tag(name=tag_name.lower())
                db.session.add(tag)
            gig.tags.append(tag)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Gig updated successfully',
        'gig': gig.to_dict()
    }), 200

@gigs_bp.route('/<int:gig_id>', methods=['DELETE'])
@jwt_required()
def delete_gig(gig_id):
    """DELETE endpoint 1: Delete a gig"""
    current_user_id = get_jwt_identity()
    gig = Gig.query.get(gig_id)
    
    if not gig:
        return jsonify({'error': 'Gig not found'}), 404
    
    if gig.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Soft delete
    gig.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'Gig deleted successfully'}), 200

@gigs_bp.route('/<int:gig_id>/orders', methods=['GET'])
@jwt_required()
def get_gig_orders(gig_id):
    """GET endpoint for gig orders (protected)"""
    current_user_id = get_jwt_identity()
    gig = Gig.query.get(gig_id)
    
    if not gig:
        return jsonify({'error': 'Gig not found'}), 404
    
    if gig.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    from app.models.order import Order
    orders = Order.query.filter_by(gig_id=gig_id).all()
    
    return jsonify({
        'orders': [order.to_dict() for order in orders]
    }), 200