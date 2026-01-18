#!/usr/bin/env python3
"""
Test script for Product Recommendation Agent
Tests all API endpoints and core functionality
"""
import requests
import json
import sys

BASE_URL = "http://localhost:5000/api"

def test_endpoint(name, method, url, data=None):
    """Test an API endpoint"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        
        if response.status_code == 200:
            print(f"✓ {name}: PASSED")
            return True, response.json()
        else:
            print(f"✗ {name}: FAILED (Status: {response.status_code})")
            return False, None
    except Exception as e:
        print(f"✗ {name}: ERROR - {str(e)}")
        return False, None

def main():
    print("=" * 60)
    print("Product Recommendation Agent - Test Suite")
    print("=" * 60)
    print()
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Get all products
    print("Testing Product Endpoints...")
    success, data = test_endpoint("Get All Products", "GET", f"{BASE_URL}/products")
    if success:
        tests_passed += 1
        print(f"  → Found {data['count']} products")
    else:
        tests_failed += 1
    
    # Test 2: Get categories
    success, data = test_endpoint("Get Categories", "GET", f"{BASE_URL}/categories")
    if success:
        tests_passed += 1
        print(f"  → Found {len(data['categories'])} categories: {', '.join(data['categories'])}")
    else:
        tests_failed += 1
    
    # Test 3: Get specific product
    success, data = test_endpoint("Get Product Details", "GET", f"{BASE_URL}/products/1")
    if success:
        tests_passed += 1
        print(f"  → Product: {data['name']}")
    else:
        tests_failed += 1
    
    print()
    print("Testing User Endpoints...")
    
    # Test 4: Get all users
    success, data = test_endpoint("Get All Users", "GET", f"{BASE_URL}/users")
    if success:
        tests_passed += 1
        users = data['users']
        print(f"  → Found {len(users)} users")
        user_id = users[0]['id'] if users else None
    else:
        tests_failed += 1
        user_id = 1
    
    # Test 5: Get user preferences
    success, data = test_endpoint("Get User Preferences", "GET", f"{BASE_URL}/users/{user_id}/preferences")
    if success:
        tests_passed += 1
        print(f"  → User preferences loaded")
    else:
        tests_failed += 1
    
    print()
    print("Testing Recommendation Engine...")
    
    # Test 6: Get recommendations
    success, data = test_endpoint("Get Recommendations", "GET", f"{BASE_URL}/recommendations/{user_id}")
    if success:
        tests_passed += 1
        print(f"  → Generated {data['count']} recommendations")
        if data['recommendations']:
            print(f"  → Top recommendation: {data['recommendations'][0]['name']}")
    else:
        tests_failed += 1
    
    print()
    print("Testing History & Rating Endpoints...")
    
    # Test 7: Add to history
    success, data = test_endpoint(
        "Add to History", 
        "POST", 
        f"{BASE_URL}/history/{user_id}",
        {"product_id": 1, "action_type": "view"}
    )
    if success:
        tests_passed += 1
        print(f"  → History item added")
    else:
        tests_failed += 1
    
    # Test 8: Get history
    success, data = test_endpoint("Get User History", "GET", f"{BASE_URL}/history/{user_id}")
    if success:
        tests_passed += 1
        print(f"  → Found {data['count']} history items")
    else:
        tests_failed += 1
    
    # Test 9: Submit rating
    success, data = test_endpoint(
        "Submit Rating", 
        "POST", 
        f"{BASE_URL}/ratings",
        {"user_id": user_id, "product_id": 1, "rating": 5, "review": "Great product!"}
    )
    if success:
        tests_passed += 1
        print(f"  → Rating submitted")
    else:
        tests_failed += 1
    
    # Test 10: Get product ratings
    success, data = test_endpoint("Get Product Ratings", "GET", f"{BASE_URL}/ratings/1")
    if success:
        tests_passed += 1
        print(f"  → Found {data['count']} ratings")
    else:
        tests_failed += 1
    
    # Test 11: Get statistics
    success, data = test_endpoint("Get Statistics", "GET", f"{BASE_URL}/stats")
    if success:
        tests_passed += 1
        print(f"  → Total products: {data['total_products']}")
        print(f"  → Total users: {data['total_users']}")
        print(f"  → Total ratings: {data['total_ratings']}")
    else:
        tests_failed += 1
    
    # Test 12: Search products
    success, data = test_endpoint("Search Products", "GET", f"{BASE_URL}/products?search=laptop")
    if success:
        tests_passed += 1
        print(f"  → Search found {data['count']} products")
    else:
        tests_failed += 1
    
    # Test 13: Filter by category
    success, data = test_endpoint("Filter by Category", "GET", f"{BASE_URL}/products?category=Electronics")
    if success:
        tests_passed += 1
        print(f"  → Category filter found {data['count']} products")
    else:
        tests_failed += 1
    
    print()
    print("=" * 60)
    print(f"Test Results: {tests_passed} passed, {tests_failed} failed")
    print("=" * 60)
    
    if tests_failed == 0:
        print("✓ All tests passed! Application is working correctly.")
        return 0
    else:
        print(f"✗ {tests_failed} test(s) failed. Please check the application.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
