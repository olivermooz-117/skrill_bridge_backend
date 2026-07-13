from app.extensions import db
from datetime import datetime

# Many-to-Many relationship table
gig_tags = db.Table('gig_tags',
    db.Column('gig_id', db.Integer, db.ForeignKey('gigs.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

class Gig(db.Model):
    __tablename__ = 'gigs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    delivery_days = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='gig', lazy=True, foreign_keys='Order.gig_id')
    tags = db.relationship('Tag', secondary=gig_tags, lazy='subquery', backref=db.backref('gigs', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': str(self.title) if self.title else '',
            'description': str(self.description) if self.description else '',
            'price': float(self.price) if self.price else 0,
            'delivery_days': int(self.delivery_days) if self.delivery_days else 0,
            'user_id': self.user_id,
            'freelancer': self.freelancer.to_dict() if self.freelancer else None,
            'tags': [tag.to_dict() for tag in self.tags] if self.tags else [],
            'is_active': bool(self.is_active),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_average_rating(self):
        from app.models.order import Order
        orders = Order.query.filter_by(gig_id=self.id, status='completed').all()
        if not orders:
            return None
        reviews = [order.review.rating for order in orders if order.review]
        return round(sum(reviews) / len(reviews), 1) if reviews else None