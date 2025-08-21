from flask import Flask, render_template, request, jsonify
from models.recommender import AmazonFashionRecommender
import os
import urllib.parse

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'amazon-fashion-recommender-2024'

# Initialize Amazon Fashion Recommender
print("🚀 Initializing Amazon Fashion Recommender System...")
print("📥 This may take a few minutes for large datasets...")
recommender = AmazonFashionRecommender(data_path='data/clean_fashion_data.json')

if recommender.df is not None and len(recommender.df) > 0:
    print(f"✅ System ready! Loaded {len(recommender.df)} Amazon fashion products")
else:
    print("❌ Warning: No products loaded. Please check your Amazon dataset file.")

@app.route('/')
def home():
    """Homepage with featured Amazon fashion products"""
    try:
        featured_products = recommender.get_featured_products()
        categories = recommender.get_categories()
        brands = recommender.get_brands()
        stats = recommender.get_stats()
        return render_template('index.html', 
            featured_products=featured_products,
            categories=categories[:8],
            brands=brands[:10],
            stats=stats,
            page_title="Amazon Fashion Store")
    except Exception as e:
        print(f"Error in home route: {e}")
        return render_template('index.html', 
            featured_products=[],
            categories=[],
            brands=[],
            stats={},
            page_title="Amazon Fashion Store")

@app.route('/product/<product_id>')
def product_detail(product_id):
    """Amazon product detail page with recommendations"""
    try:
        product = recommender.get_product_by_id(product_id)
        if not product:
            return render_template('error.html', 
                message=f"Product {product_id} not found in Amazon dataset",
                error_code="404"), 404

        recommendations = recommender.get_recommendations(product_id, 8)

        related_by_brand = []
        related_by_category = []
        if product.get('brand') and product['brand'] != 'Unknown':
            related_by_brand = recommender.get_random_products(4, brand=product['brand'])
        if product.get('main_category'):
            related_by_category = recommender.get_random_products(4, category=product['main_category'])

        return render_template('product.html', 
            product=product,
            recommendations=recommendations,
            related_by_brand=related_by_brand,
            related_by_category=related_by_category,
            page_title=f"{product.get('name', 'Product')} - Amazon Fashion")
    except Exception as e:
        print(f"Error in product detail route: {e}")
        return render_template('error.html', 
            message="Error loading product details",
            error_code="500"), 500

@app.route('/search')
def search():
    """Search Amazon fashion products"""
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    brand = request.args.get('brand', '').strip()
    sort_by = request.args.get('sort', 'relevance')

    results = []
    search_info = {
        'query': query,
        'category': category,
        'brand': brand,
        'sort_by': sort_by,
        'total_results': 0
    }

    try:
        if query:
            results = recommender.search_products(query, 36)
            search_info['search_type'] = f'Search results for "{query}"'
        elif category:
            results = recommender.get_random_products(36, category=category)
            search_info['search_type'] = f'Products in "{category}"'
        elif brand:
            results = recommender.get_random_products(36, brand=brand)
            search_info['search_type'] = f'Products by "{brand}"'
        else:
            results = recommender.get_random_products(36)
            search_info['search_type'] = 'All products'

        if sort_by and results:
            if sort_by == 'price_low':
                results = sorted(results, key=lambda x: x.get('price', 0))
            elif sort_by == 'price_high':
                results = sorted(results, key=lambda x: x.get('price', 0), reverse=True)
            elif sort_by == 'rating':
                results = sorted(results, key=lambda x: x.get('rating', 0), reverse=True)
            elif sort_by == 'name':
                results = sorted(results, key=lambda x: x.get('name', '').lower())

        search_info['total_results'] = len(results)
        categories = recommender.get_categories()
        brands = recommender.get_brands()

        return render_template('search.html', 
            results=results,
            search_info=search_info,
            categories=categories[:15],
            brands=brands[:20],
            page_title=f"Search Results - Amazon Fashion")
    except Exception as e:
        print(f"Error in search route: {e}")
        return render_template('search.html', 
            results=[],
            search_info=search_info,
            categories=[],
            brands=[],
            page_title="Search - Amazon Fashion")

@app.route('/category/<category_name>')
def category_page(category_name):
    try:
        category_name = urllib.parse.unquote(category_name)
        results = recommender.get_random_products(36, category=category_name)
        categories = recommender.get_categories()
        brands = recommender.get_brands()
        stats = recommender.get_stats()
        return render_template('category.html',
            results=results,
            category_name=category_name,
            categories=categories[:15],
            brands=brands[:20],
            stats=stats,
            page_title=f"{category_name} - Category")
    except Exception as e:
        print(f"Error in category page: {e}")
        return render_template('category.html',
            results=[],
            category_name=category_name,
            categories=[],
            brands=[],
            stats={},
            page_title="Category Error")

@app.route('/brand/<brand_name>')
def brand_page(brand_name):
    try:
        brand_name = urllib.parse.unquote(brand_name)
        results = recommender.get_random_products(36, brand=brand_name)
        categories = recommender.get_categories()
        brands = recommender.get_brands()
        stats = recommender.get_stats()
        return render_template('brand.html',
            results=results,
            brand_name=brand_name,
            categories=categories[:15],
            brands=brands[:20],
            stats=stats,
            page_title=f"{brand_name} - Brand")
    except Exception as e:
        print(f"Error in brand page: {e}")
        return render_template('brand.html',
            results=[],
            brand_name=brand_name,
            categories=[],
            brands=[],
            stats={},
            page_title="Brand Error")

@app.route('/api/recommendations/<product_id>')
def api_recommendations(product_id):
    try:
        recommendations = recommender.get_recommendations(product_id, 8)
        return jsonify({
            'success': True,
            'product_id': product_id,
            'recommendations': recommendations,
            'count': len(recommendations)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/search')
def api_search():
    query = request.args.get('q', '').strip()
    limit = min(int(request.args.get('limit', 20)), 100)
    try:
        results = recommender.search_products(query, limit)
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'total': len(results)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats')
def api_stats():
    try:
        stats = recommender.get_stats()
        categories = recommender.get_categories()
        brands = recommender.get_brands()
        return jsonify({
            'success': True,
            'stats': stats,
            'categories': categories[:10],
            'brands': brands[:10]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.context_processor
def inject_globals():
    return dict(
        categories=recommender.get_categories(),
        brands=recommender.get_brands()
    )

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', 
        message="Page not found",
        error_code="404"), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('error.html', 
        message="Internal server error",
        error_code="500"), 500

@app.before_request
def log_request():
    print(f"[{request.method}] {request.path}")

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌟 AMAZON FASHION RECOMMENDATION SYSTEM")
    print("🚀 Starting Flask development server...")
    print("🌐 Open http://127.0.0.1:5000 in your browser")
    print("📊 Dataset:", f"{len(recommender.df) if recommender.df is not None else 0} Amazon products loaded")
    print("="*60)
    app.run(debug=True, host='127.0.0.1', port=5000)
