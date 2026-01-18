"""
Database models for Product Recommendation Agent
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

class Product(db.Model):
    """Product model for catalog items"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    subcategory = db.Column(db.String(100))
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    features = db.Column(db.Text)  # JSON string
    image_url = db.Column(db.String(500))
    brand = db.Column(db.String(100))
    rating = db.Column(db.Float, default=0.0)
    num_ratings = db.Column(db.Integer, default=0)
    stock = db.Column(db.Integer, default=100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'subcategory': self.subcategory,
            'price': self.price,
            'description': self.description,
            'features': json.loads(self.features) if self.features else [],
            'image_url': self.image_url,
            'brand': self.brand,
            'rating': round(self.rating, 1),
            'num_ratings': self.num_ratings,
            'stock': self.stock
        }

class User(db.Model):
    """User model for tracking preferences and history"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), unique=True)
    preferences = db.Column(db.Text)  # JSON string of preferred categories/brands
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'preferences': json.loads(self.preferences) if self.preferences else {}
        }

class UserHistory(db.Model):
    """Track user browsing and interaction history"""
    __tablename__ = 'user_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)  # view, click, add_to_cart, purchase
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='history')
    product = db.relationship('Product', backref='views')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'action_type': self.action_type,
            'timestamp': self.timestamp.isoformat(),
            'product': self.product.to_dict() if self.product else None
        }

class Rating(db.Model):
    """Product ratings by users"""
    __tablename__ = 'ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)  # 1-5 stars
    review = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='ratings')
    product = db.relationship('Product', backref='product_ratings')
    
    # Ensure one rating per user per product
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='_user_product_uc'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'rating': self.rating,
            'review': self.review,
            'timestamp': self.timestamp.isoformat()
        }
