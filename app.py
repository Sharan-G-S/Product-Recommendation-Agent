"""
Flask Application for Product Recommendation Agent
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from models import db, Product, User, UserHistory, Rating
from recommendation_engine import RecommendationEngine
from data_loader import load_sample_data, create_sample_users
import os
from datetime import datetime
import json

app = Flask(__name__, static_folder='.')
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recommendations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Initialize database
db.init_app(app)

# Initialize recommendation engine
rec_engine = None

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('.', path)

# Product endpoints
@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products with optional filtering"""
    category = request.args.get('category')
    search = request.args.get('search')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort_by = request.args.get('sort_by', 'name')
    
    query = Product.query.filter(Product.stock > 0)
    
    # Apply filters
    if category:
        query = query.filter(Product.category == category)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Product.name.ilike(search_term)) |
            (Product.description.ilike(search_term)) |
            (Product.brand.ilike(search_term))
        )
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    # Apply sorting
    if sort_by == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort_by == 'rating':
        query = query.order_by(Product.rating.desc())
    else:
        query = query.order_by(Product.name.asc())
    
    products = query.all()
    
    return jsonify({
        'products': [p.to_dict() for p in products],
        'count': len(products)
    })

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product by ID"""
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all unique categories"""
    categories = db.session.query(Product.category).distinct().all()
    return jsonify({
        'categories': [c[0] for c in categories]
    })

# User endpoints
@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    users = User.query.all()
    return jsonify({
        'users': [u.to_dict() for u in users]
    })

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user"""
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@app.route('/api/users/<int:user_id>/preferences', methods=['GET', 'POST'])
def user_preferences(user_id):
    """Get or update user preferences"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        data = request.json
        user.preferences = json.dumps(data.get('preferences', {}))
        db.session.commit()
        return jsonify({'message': 'Preferences updated', 'preferences': json.loads(user.preferences)})
    
    return jsonify({
        'preferences': json.loads(user.preferences) if user.preferences else {}
    })

# Recommendation endpoints
@app.route('/api/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    """Get personalized recommendations for a user"""
    num_recommendations = request.args.get('limit', 10, type=int)
    
    recommendations = rec_engine.get_recommendations(user_id, num_recommendations)
    
    return jsonify({
        'recommendations': [p.to_dict() for p in recommendations],
        'count': len(recommendations)
    })

# History endpoints
@app.route('/api/history/<int:user_id>', methods=['GET', 'POST'])
def user_history(user_id):
    """Get or add to user browsing history"""
    if request.method == 'POST':
        data = request.json
        product_id = data.get('product_id')
        action_type = data.get('action_type', 'view')
        
        if not product_id:
            return jsonify({'error': 'product_id is required'}), 400
        
        # Add to history
        history_item = UserHistory(
            user_id=user_id,
            product_id=product_id,
            action_type=action_type
        )
        db.session.add(history_item)
        db.session.commit()
        
        return jsonify({'message': 'History updated', 'item': history_item.to_dict()})
    
    # Get history
    limit = request.args.get('limit', 50, type=int)
    history = UserHistory.query.filter_by(user_id=user_id)\
        .order_by(UserHistory.timestamp.desc())\
        .limit(limit).all()
    
    return jsonify({
        'history': [h.to_dict() for h in history],
        'count': len(history)
    })

# Rating endpoints
@app.route('/api/ratings', methods=['POST'])
def add_rating():
    """Add or update a product rating"""
    data = request.json
    user_id = data.get('user_id')
    product_id = data.get('product_id')
    rating_value = data.get('rating')
    review = data.get('review', '')
    
    if not all([user_id, product_id, rating_value]):
        return jsonify({'error': 'user_id, product_id, and rating are required'}), 400
    
    if not (1 <= rating_value <= 5):
        return jsonify({'error': 'rating must be between 1 and 5'}), 400
    
    # Check if rating exists
    existing_rating = Rating.query.filter_by(
        user_id=user_id,
        product_id=product_id
    ).first()
    
    if existing_rating:
        existing_rating.rating = rating_value
        existing_rating.review = review
        existing_rating.timestamp = datetime.utcnow()
    else:
        new_rating = Rating(
            user_id=user_id,
            product_id=product_id,
            rating=rating_value,
            review=review
        )
        db.session.add(new_rating)
    
    db.session.commit()
    
    # Update product's average rating
    rec_engine.update_product_rating(product_id)
    
    return jsonify({'message': 'Rating submitted successfully'})

@app.route('/api/ratings/<int:product_id>', methods=['GET'])
def get_product_ratings(product_id):
    """Get all ratings for a product"""
    ratings = Rating.query.filter_by(product_id=product_id)\
        .order_by(Rating.timestamp.desc()).all()
    
    return jsonify({
        'ratings': [r.to_dict() for r in ratings],
        'count': len(ratings)
    })

# Statistics endpoint
@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get overall statistics"""
    total_products = Product.query.count()
    total_users = User.query.count()
    total_ratings = Rating.query.count()
    
    categories = db.session.query(Product.category, db.func.count(Product.id))\
        .group_by(Product.category).all()
    
    return jsonify({
        'total_products': total_products,
        'total_users': total_users,
        'total_ratings': total_ratings,
        'categories': {cat: count for cat, count in categories}
    })

def init_database():
    """Initialize database with sample data"""
    with app.app_context():
        db.create_all()
        
        # Check if data already exists
        if Product.query.count() == 0:
            load_sample_data()
            create_sample_users()
            print("Database initialized with sample data!")
        else:
            print("Database already contains data.")

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Initialize recommendation engine
    with app.app_context():
        rec_engine = RecommendationEngine(db)
    
    print("\n" + "="*60)
    print("🛍️  Product Recommendation Agent is running!")
    print("="*60)
    print("\n📍 Open your browser and navigate to:")
    print("   http://localhost:5000")
    print("\n✨ Features:")
    print("   • Browse product catalog")
    print("   • Get personalized recommendations")
    print("   • Track browsing history")
    print("   • Rate products")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, port=5000)
