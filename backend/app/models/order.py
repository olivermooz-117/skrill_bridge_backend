from app.extensions import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    gig_id = db.Column(db.Integer, db.ForeignKey('gigs.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    total_price = db.Column(db.Float, nullable=False)
    requirements = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    review = db.relationship('Review', backref='order', uselist=False, lazy=True, foreign_keys='Review.order_id')
    
    def to_dict(self):
        return {
            'id': self.id,
            'gig_id': self.gig_id,
            'gig_title': self.gig.title if self.gig else None,
            'client_id': self.client_id,
            'client_name': self.client.name if self.client else None,
            'status': self.status,
            'total_price': self.total_price,
            'requirements': self.requirements,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'review': self.review.to_dict() if self.review else None
        }