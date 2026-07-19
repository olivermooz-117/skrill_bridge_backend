from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.gig import Gig
from app.models.tag import Tag  # <-- Fixed import
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