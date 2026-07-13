from app.extensions import db
from datetime import datetime
import bcrypt

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='client')
    bio = db.Column(db.Text, default='')
    profile_picture = db.Column(db.String(255), default='')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    gigs = db.relationship('Gig', backref='freelancer', lazy=True, foreign_keys='Gig.user_id')
    orders_as_client = db.relationship('Order', backref='client', lazy=True, foreign_keys='Order.client_id')
    reviews = db.relationship('Review', backref='user', lazy=True, foreign_keys='Review.user_id')
    
    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(
            str(password).encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(
            str(password).encode('utf-8'), 
            self.password_hash.encode('utf-8')
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': str(self.name) if self.name else '',
            'email': str(self.email) if self.email else '',
            'role': str(self.role) if self.role else 'client',
            'bio': str(self.bio) if self.bio else '',
            'profile_picture': str(self.profile_picture) if self.profile_picture else '',
            'is_active': bool(self.is_active),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }