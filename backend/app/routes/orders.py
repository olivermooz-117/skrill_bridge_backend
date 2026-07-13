from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.order import Order
from app.models.gig import Gig
from app.models.review import Review
from app.extensions import db

orders_bp = Blueprint('orders', __name__, url_prefix='/api/orders')

@orders_bp.route('', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_orders():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response, 200
    
    try:
        current_user_id = get_jwt_identity()
        print(f"📥 Fetching orders for user: {current_user_id}")
        
        # Get all orders for the user
        orders = Order.query.filter_by(client_id=current_user_id).all()
        
        return jsonify({
            'orders': [order.to_dict() for order in orders]
        }), 200
    except Exception as e:
        print(f"❌ Error fetching orders: {str(e)}")
        return jsonify({'error': str(e)}), 500

@orders_bp.route('', methods=['POST', 'OPTIONS'])
@jwt_required()
def create_order():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response, 200
    
    try:
        data = request.get_json()
        print(f"📥 Received order data: {data}")
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        current_user_id = get_jwt_identity()
        
        if 'gig_id' not in data:
            return jsonify({'error': 'Gig ID required'}), 400
        
        gig = Gig.query.get(data['gig_id'])
        if not gig or not gig.is_active:
            return jsonify({'error': 'Gig not found or inactive'}), 404
        
        existing_order = Order.query.filter_by(
            gig_id=gig.id,
            client_id=current_user_id,
            status='pending'
        ).first()
        
        if existing_order:
            return jsonify({'error': 'You already have a pending order for this gig'}), 409
        
        order = Order(
            gig_id=gig.id,
            client_id=current_user_id,
            total_price=gig.price,
            requirements=data.get('requirements', '')
        )
        
        db.session.add(order)
        db.session.commit()
        
        print(f"✅ Order created: {order.id}")
        
        return jsonify({
            'message': 'Order created successfully',
            'order': order.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating order: {str(e)}")
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/<int:order_id>', methods=['PUT', 'OPTIONS'])
@jwt_required()
def update_order_status(order_id):
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response, 200
    
    try:
        current_user_id = get_jwt_identity()
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        if order.client_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        new_status = data.get('status')
        
        valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
        if new_status not in valid_statuses:
            return jsonify({'error': 'Invalid status'}), 400
        
        order.status = new_status
        db.session.commit()
        
        return jsonify({
            'message': 'Order status updated',
            'order': order.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error updating order: {str(e)}")
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/<int:order_id>', methods=['DELETE', 'OPTIONS'])
@jwt_required()
def cancel_order(order_id):
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response, 200
    
    try:
        current_user_id = get_jwt_identity()
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        if order.client_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if order.status in ['completed', 'cancelled']:
            return jsonify({'error': 'Cannot cancel a completed or cancelled order'}), 400
        
        order.status = 'cancelled'
        db.session.commit()
        
        return jsonify({'message': 'Order cancelled successfully'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error cancelling order: {str(e)}")
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/<int:order_id>/review', methods=['POST', 'OPTIONS'])
@jwt_required()
def create_review(order_id):
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response, 200
    
    try:
        current_user_id = get_jwt_identity()
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        if order.client_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if order.status != 'completed':
            return jsonify({'error': 'Can only review completed orders'}), 400
        
        if order.review:
            return jsonify({'error': 'Review already exists for this order'}), 409
        
        data = request.get_json()
        if 'rating' not in data:
            return jsonify({'error': 'Rating required'}), 400
        
        rating = data['rating']
        if not 1 <= rating <= 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        
        review = Review(
            order_id=order.id,
            user_id=current_user_id,
            rating=rating,
            comment=data.get('comment', '')
        )
        
        db.session.add(review)
        db.session.commit()
        
        return jsonify({
            'message': 'Review created successfully',
            'review': review.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating review: {str(e)}")
        return jsonify({'error': str(e)}), 500