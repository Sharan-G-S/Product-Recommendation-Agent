"""
Data loader for sample products
"""
import json
from models import db, Product

SAMPLE_PRODUCTS = [
    # Electronics - Laptops
    {
        "name": "MacBook Pro 16-inch",
        "category": "Electronics",
        "subcategory": "Laptops",
        "price": 2499.99,
        "description": "Powerful laptop with M3 Pro chip, 16-inch Liquid Retina XDR display, and up to 22 hours of battery life.",
        "features": ["M3 Pro chip", "16-inch display", "32GB RAM", "1TB SSD", "macOS"],
        "brand": "Apple",
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500",
        "rating": 4.8,
        "num_ratings": 245
    },
    {
        "name": "Dell XPS 15",
        "category": "Electronics",
        "subcategory": "Laptops",
        "price": 1799.99,
        "description": "Premium laptop with Intel Core i7, stunning InfinityEdge display, and exceptional build quality.",
        "features": ["Intel i7", "15.6-inch 4K display", "16GB RAM", "512GB SSD", "Windows 11"],
        "brand": "Dell",
        "image_url": "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=500",
        "rating": 4.6,
        "num_ratings": 189
    },
    {
        "name": "ThinkPad X1 Carbon",
        "category": "Electronics",
        "subcategory": "Laptops",
        "price": 1599.99,
        "description": "Business ultrabook with legendary ThinkPad keyboard, military-grade durability, and all-day battery.",
        "features": ["Intel i7", "14-inch display", "16GB RAM", "512GB SSD", "Windows 11 Pro"],
        "brand": "Lenovo",
        "image_url": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=500",
        "rating": 4.7,
        "num_ratings": 156
    },
    
    # Electronics - Smartphones
    {
        "name": "iPhone 15 Pro",
        "category": "Electronics",
        "subcategory": "Smartphones",
        "price": 999.99,
        "description": "Latest iPhone with titanium design, A17 Pro chip, and advanced camera system.",
        "features": ["A17 Pro chip", "6.1-inch display", "Pro camera system", "Action button", "iOS 17"],
        "brand": "Apple",
        "image_url": "https://images.unsplash.com/photo-1592286927505-2fd0f8fc8e3d?w=500",
        "rating": 4.9,
        "num_ratings": 512
    },
    {
        "name": "Samsung Galaxy S24 Ultra",
        "category": "Electronics",
        "subcategory": "Smartphones",
        "price": 1199.99,
        "description": "Flagship Android phone with S Pen, 200MP camera, and AI-powered features.",
        "features": ["Snapdragon 8 Gen 3", "6.8-inch AMOLED", "200MP camera", "S Pen", "Android 14"],
        "brand": "Samsung",
        "image_url": "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=500",
        "rating": 4.7,
        "num_ratings": 423
    },
    {
        "name": "Google Pixel 8 Pro",
        "category": "Electronics",
        "subcategory": "Smartphones",
        "price": 899.99,
        "description": "Google's flagship with best-in-class AI features, exceptional camera, and pure Android experience.",
        "features": ["Google Tensor G3", "6.7-inch OLED", "AI camera", "7 years updates", "Android 14"],
        "brand": "Google",
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=500",
        "rating": 4.6,
        "num_ratings": 298
    },
    
    # Electronics - Headphones
    {
        "name": "AirPods Pro (2nd Gen)",
        "category": "Electronics",
        "subcategory": "Headphones",
        "price": 249.99,
        "description": "Premium wireless earbuds with active noise cancellation and spatial audio.",
        "features": ["Active ANC", "Spatial audio", "Adaptive transparency", "H2 chip", "MagSafe charging"],
        "brand": "Apple",
        "image_url": "https://images.unsplash.com/photo-1606841837239-c5a1a4a07af7?w=500",
        "rating": 4.8,
        "num_ratings": 678
    },
    {
        "name": "Sony WH-1000XM5",
        "category": "Electronics",
        "subcategory": "Headphones",
        "price": 399.99,
        "description": "Industry-leading noise canceling headphones with exceptional sound quality.",
        "features": ["Premium ANC", "30-hour battery", "LDAC support", "Multipoint connection", "Touch controls"],
        "brand": "Sony",
        "image_url": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=500",
        "rating": 4.9,
        "num_ratings": 534
    },
    
    # Fashion - Clothing
    {
        "name": "Classic Denim Jacket",
        "category": "Fashion",
        "subcategory": "Clothing",
        "price": 89.99,
        "description": "Timeless denim jacket with vintage wash and comfortable fit.",
        "features": ["100% cotton", "Vintage wash", "Button closure", "Multiple pockets", "Unisex"],
        "brand": "Levi's",
        "image_url": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500",
        "rating": 4.5,
        "num_ratings": 234
    },
    {
        "name": "Premium Wool Sweater",
        "category": "Fashion",
        "subcategory": "Clothing",
        "price": 129.99,
        "description": "Luxurious merino wool sweater with classic crew neck design.",
        "features": ["Merino wool", "Crew neck", "Ribbed cuffs", "Machine washable", "Multiple colors"],
        "brand": "J.Crew",
        "image_url": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=500",
        "rating": 4.7,
        "num_ratings": 167
    },
    
    # Fashion - Shoes
    {
        "name": "Air Max 90",
        "category": "Fashion",
        "subcategory": "Shoes",
        "price": 139.99,
        "description": "Iconic sneakers with visible Air cushioning and retro style.",
        "features": ["Air cushioning", "Leather and mesh upper", "Rubber outsole", "Classic design", "Multiple colors"],
        "brand": "Nike",
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500",
        "rating": 4.6,
        "num_ratings": 892
    },
    {
        "name": "Chuck Taylor All Star",
        "category": "Fashion",
        "subcategory": "Shoes",
        "price": 65.99,
        "description": "Classic canvas sneakers that never go out of style.",
        "features": ["Canvas upper", "Rubber sole", "Iconic design", "High-top", "Multiple colors"],
        "brand": "Converse",
        "image_url": "https://images.unsplash.com/photo-1607522370275-f14206abe5d3?w=500",
        "rating": 4.8,
        "num_ratings": 1245
    },
    
    # Home & Living - Furniture
    {
        "name": "Modern Ergonomic Office Chair",
        "category": "Home & Living",
        "subcategory": "Furniture",
        "price": 449.99,
        "description": "Premium office chair with lumbar support and breathable mesh back.",
        "features": ["Lumbar support", "Breathable mesh", "Adjustable armrests", "Tilt mechanism", "5-year warranty"],
        "brand": "Herman Miller",
        "image_url": "https://images.unsplash.com/photo-1580480055273-228ff5388ef8?w=500",
        "rating": 4.9,
        "num_ratings": 345
    },
    {
        "name": "Minimalist Standing Desk",
        "category": "Home & Living",
        "subcategory": "Furniture",
        "price": 599.99,
        "description": "Electric height-adjustable desk with memory presets and cable management.",
        "features": ["Electric adjustment", "Memory presets", "Cable management", "Solid wood top", "Quiet motor"],
        "brand": "Uplift",
        "image_url": "https://images.unsplash.com/photo-1595515106969-1ce29566ff1c?w=500",
        "rating": 4.7,
        "num_ratings": 278
    },
    
    # Home & Living - Appliances
    {
        "name": "Smart Coffee Maker",
        "category": "Home & Living",
        "subcategory": "Appliances",
        "price": 199.99,
        "description": "WiFi-enabled coffee maker with programmable brewing and voice control.",
        "features": ["WiFi enabled", "Voice control", "Programmable", "Thermal carafe", "Auto-shutoff"],
        "brand": "Breville",
        "image_url": "https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=500",
        "rating": 4.5,
        "num_ratings": 456
    },
    {
        "name": "Robot Vacuum Cleaner",
        "category": "Home & Living",
        "subcategory": "Appliances",
        "price": 399.99,
        "description": "Smart robot vacuum with mapping, auto-empty base, and app control.",
        "features": ["Smart mapping", "Auto-empty", "App control", "Voice assistant", "2-hour runtime"],
        "brand": "iRobot",
        "image_url": "https://images.unsplash.com/photo-1558317374-067fb5f30001?w=500",
        "rating": 4.6,
        "num_ratings": 623
    },
    
    # Sports & Outdoors
    {
        "name": "Yoga Mat Pro",
        "category": "Sports & Outdoors",
        "subcategory": "Fitness",
        "price": 79.99,
        "description": "Premium yoga mat with superior grip and cushioning.",
        "features": ["6mm thick", "Non-slip surface", "Eco-friendly", "Carrying strap", "Easy to clean"],
        "brand": "Manduka",
        "image_url": "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=500",
        "rating": 4.8,
        "num_ratings": 234
    },
    {
        "name": "Adjustable Dumbbells Set",
        "category": "Sports & Outdoors",
        "subcategory": "Fitness",
        "price": 299.99,
        "description": "Space-saving adjustable dumbbells from 5 to 52.5 lbs per hand.",
        "features": ["5-52.5 lbs range", "Quick adjustment", "Compact design", "Durable coating", "Includes stand"],
        "brand": "Bowflex",
        "image_url": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=500",
        "rating": 4.7,
        "num_ratings": 567
    },
    {
        "name": "Mountain Bike 29er",
        "category": "Sports & Outdoors",
        "subcategory": "Cycling",
        "price": 899.99,
        "description": "Full-suspension mountain bike with 29-inch wheels and hydraulic disc brakes.",
        "features": ["29-inch wheels", "Full suspension", "Hydraulic brakes", "21-speed", "Aluminum frame"],
        "brand": "Trek",
        "image_url": "https://images.unsplash.com/photo-1576435728678-68d0fbf94e91?w=500",
        "rating": 4.6,
        "num_ratings": 189
    },
    
    # Books & Media
    {
        "name": "Kindle Paperwhite",
        "category": "Books & Media",
        "subcategory": "E-Readers",
        "price": 139.99,
        "description": "Waterproof e-reader with adjustable warm light and weeks of battery life.",
        "features": ["6.8-inch display", "Waterproof", "Adjustable warm light", "Weeks battery", "16GB storage"],
        "brand": "Amazon",
        "image_url": "https://images.unsplash.com/photo-1592496001020-d31bd830651f?w=500",
        "rating": 4.8,
        "num_ratings": 1234
    },
    {
        "name": "Bluetooth Bookshelf Speakers",
        "category": "Books & Media",
        "subcategory": "Audio",
        "price": 349.99,
        "description": "Premium powered speakers with Bluetooth, optical, and analog inputs.",
        "features": ["Bluetooth 5.0", "Multiple inputs", "Remote control", "100W power", "Wooden cabinet"],
        "brand": "Edifier",
        "image_url": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=500",
        "rating": 4.7,
        "num_ratings": 445
    }
]

def load_sample_data():
    """Load sample products into database"""
    print("Loading sample products...")
    
    # Clear existing products
    Product.query.delete()
    db.session.commit()
    
    # Add sample products
    for product_data in SAMPLE_PRODUCTS:
        product = Product(
            name=product_data["name"],
            category=product_data["category"],
            subcategory=product_data.get("subcategory"),
            price=product_data["price"],
            description=product_data["description"],
            features=json.dumps(product_data["features"]),
            brand=product_data.get("brand"),
            image_url=product_data.get("image_url"),
            rating=product_data.get("rating", 0.0),
            num_ratings=product_data.get("num_ratings", 0),
            stock=100
        )
        db.session.add(product)
    
    db.session.commit()
    print(f"Loaded {len(SAMPLE_PRODUCTS)} products successfully!")

def create_sample_users():
    """Create sample users for testing"""
    from models import User
    
    print("Creating sample users...")
    
    # Clear existing users
    User.query.delete()
    db.session.commit()
    
    sample_users = [
        {
            "name": "Demo User",
            "email": "demo@example.com",
            "preferences": json.dumps({
                "categories": ["Electronics", "Sports & Outdoors"],
                "brands": ["Apple", "Nike"]
            })
        },
        {
            "name": "Tech Enthusiast",
            "email": "tech@example.com",
            "preferences": json.dumps({
                "categories": ["Electronics"],
                "brands": ["Apple", "Sony", "Dell"]
            })
        },
        {
            "name": "Fashion Lover",
            "email": "fashion@example.com",
            "preferences": json.dumps({
                "categories": ["Fashion"],
                "brands": ["Nike", "Levi's"]
            })
        }
    ]
    
    for user_data in sample_users:
        user = User(**user_data)
        db.session.add(user)
    
    db.session.commit()
    print(f"Created {len(sample_users)} sample users!")
