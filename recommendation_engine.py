"""
Recommendation Engine for Product Recommendations
Implements collaborative filtering, content-based filtering, and hybrid approach
"""
import numpy as np
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import json

class RecommendationEngine:
    def __init__(self, db):
        self.db = db
        
    def get_recommendations(self, user_id, num_recommendations=10):
        """
        Generate personalized product recommendations using hybrid approach
        """
        from models import User, Product, Rating, UserHistory
        
        user = User.query.get(user_id)
        if not user:
            # Return popular products for new users
            return self._get_popular_products(num_recommendations)
        
        # Get user's rating history
        user_ratings = Rating.query.filter_by(user_id=user_id).all()
        
        # Get user's browsing history
        user_history = UserHistory.query.filter_by(user_id=user_id)\
            .order_by(UserHistory.timestamp.desc()).limit(50).all()
        
        # Combine different recommendation strategies
        collaborative_recs = self._collaborative_filtering(user_id, user_ratings)
        content_recs = self._content_based_filtering(user_id, user_history, user.preferences)
        popular_recs = self._get_popular_products(num_recommendations)
        
        # Merge recommendations with weighted scoring
        merged_scores = defaultdict(float)
        
        # Weight: 40% collaborative, 40% content-based, 20% popular
        for product_id, score in collaborative_recs.items():
            merged_scores[product_id] += score * 0.4
            
        for product_id, score in content_recs.items():
            merged_scores[product_id] += score * 0.4
            
        for idx, product in enumerate(popular_recs):
            # Decreasing score for popular items
            merged_scores[product.id] += (1.0 - idx / len(popular_recs)) * 0.2
        
        # Filter out products user has already rated highly
        rated_product_ids = {r.product_id for r in user_ratings if r.rating >= 4}
        for product_id in rated_product_ids:
            if product_id in merged_scores:
                merged_scores[product_id] *= 0.3  # Reduce score but don't eliminate
        
        # Sort by score and get top recommendations
        sorted_products = sorted(merged_scores.items(), key=lambda x: x[1], reverse=True)
        top_product_ids = [pid for pid, score in sorted_products[:num_recommendations]]
        
        # Fetch product objects
        recommendations = Product.query.filter(Product.id.in_(top_product_ids)).all()
        
        # Sort by merged score
        recommendations.sort(key=lambda p: merged_scores[p.id], reverse=True)
        
        return recommendations
    
    def _collaborative_filtering(self, user_id, user_ratings):
        """
        Collaborative filtering based on similar users' preferences
        """
        from models import Rating, Product
        
        if not user_ratings:
            return {}
        
        # Get all ratings
        all_ratings = Rating.query.all()
        
        # Build user-product rating matrix
        user_product_matrix = defaultdict(dict)
        for rating in all_ratings:
            user_product_matrix[rating.user_id][rating.product_id] = rating.rating
        
        # Calculate user similarity using Pearson correlation
        current_user_ratings = {r.product_id: r.rating for r in user_ratings}
        similar_users = []
        
        for other_user_id, other_ratings in user_product_matrix.items():
            if other_user_id == user_id:
                continue
            
            # Find common products
            common_products = set(current_user_ratings.keys()) & set(other_ratings.keys())
            
            if len(common_products) < 2:
                continue
            
            # Calculate similarity
            similarity = self._pearson_correlation(
                [current_user_ratings[p] for p in common_products],
                [other_ratings[p] for p in common_products]
            )
            
            if similarity > 0:
                similar_users.append((other_user_id, similarity))
        
        # Sort by similarity
        similar_users.sort(key=lambda x: x[1], reverse=True)
        
        # Get recommendations from similar users
        recommendations = defaultdict(float)
        total_similarity = 0
        
        for other_user_id, similarity in similar_users[:10]:  # Top 10 similar users
            other_ratings = user_product_matrix[other_user_id]
            
            for product_id, rating in other_ratings.items():
                if product_id not in current_user_ratings and rating >= 4:
                    recommendations[product_id] += similarity * rating
                    total_similarity += similarity
        
        # Normalize scores
        if total_similarity > 0:
            for product_id in recommendations:
                recommendations[product_id] /= total_similarity
        
        return recommendations
    
    def _content_based_filtering(self, user_id, user_history, preferences_json):
        """
        Content-based filtering based on product features and user preferences
        """
        from models import Product
        
        # Parse user preferences
        try:
            preferences = json.loads(preferences_json) if preferences_json else {}
        except:
            preferences = {}
        
        # Analyze user's browsing history
        category_counts = Counter()
        brand_counts = Counter()
        viewed_products = set()
        
        for history_item in user_history:
            product = history_item.product
            if product:
                viewed_products.add(product.id)
                category_counts[product.category] += 1
                if product.brand:
                    brand_counts[product.brand] += 1
        
        # Get all products
        all_products = Product.query.filter(Product.stock > 0).all()
        
        recommendations = {}
        
        for product in all_products:
            if product.id in viewed_products:
                continue
            
            score = 0.0
            
            # Category matching
            if product.category in category_counts:
                score += category_counts[product.category] / max(category_counts.values()) * 0.4
            
            # Brand matching
            if product.brand and product.brand in brand_counts:
                score += brand_counts[product.brand] / max(brand_counts.values()) * 0.3
            
            # Preference matching
            if 'categories' in preferences and product.category in preferences['categories']:
                score += 0.2
            
            if 'brands' in preferences and product.brand in preferences['brands']:
                score += 0.1
            
            # Boost by product rating
            if product.num_ratings > 0:
                score += (product.rating / 5.0) * 0.1
            
            if score > 0:
                recommendations[product.id] = score
        
        return recommendations
    
    def _get_popular_products(self, num_products=10):
        """
        Get popular products based on ratings and views
        """
        from models import Product
        
        products = Product.query.filter(Product.stock > 0)\
            .order_by(Product.rating.desc(), Product.num_ratings.desc())\
            .limit(num_products).all()
        
        return products
    
    def _pearson_correlation(self, x, y):
        """
        Calculate Pearson correlation coefficient
        """
        if len(x) != len(y) or len(x) == 0:
            return 0
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_x_sq = sum(xi**2 for xi in x)
        sum_y_sq = sum(yi**2 for yi in y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = np.sqrt((n * sum_x_sq - sum_x**2) * (n * sum_y_sq - sum_y**2))
        
        if denominator == 0:
            return 0
        
        return numerator / denominator
    
    def update_product_rating(self, product_id):
        """
        Update product's average rating
        """
        from models import Product, Rating
        
        product = Product.query.get(product_id)
        if not product:
            return
        
        ratings = Rating.query.filter_by(product_id=product_id).all()
        
        if ratings:
            product.rating = sum(r.rating for r in ratings) / len(ratings)
            product.num_ratings = len(ratings)
        else:
            product.rating = 0.0
            product.num_ratings = 0
        
        self.db.session.commit()
