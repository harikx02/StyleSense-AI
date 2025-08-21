import pandas as pd
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import gzip
import os
import re

class AmazonFashionRecommender:
    def __init__(self, data_path):
        self.data_path = data_path
        self.df = None
        self.tfidf_matrix = None
        self.vectorizer = None
        
        # Load and process data in the correct order
        self.load_amazon_data()
        if self.df is not None and len(self.df) > 0:
            self.clean_amazon_data()
            self.build_recommendation_matrix()
        else:
            print("❌ Failed to load data. Check your dataset file.")

    def _clean_text(self, text):
        """Clean text data"""
        if pd.isna(text):
            return ""
        return str(text).lower().replace('\n', ' ').replace('\r', '').strip()

    def load_amazon_data(self):
        """Load Amazon dataset from JSON file"""
        print("🔄 Loading Amazon Fashion Dataset...")
        
        if not os.path.exists(self.data_path):
            print(f"❌ Dataset file not found at: {self.data_path}")
            print("💡 Please ensure your dataset file exists or create a sample using the dataset sampler.")
            return

        products = []
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                # Try to load as JSON array first
                try:
                    f.seek(0)
                    data = json.load(f)
                    if isinstance(data, list):
                        products = data[:5000]  # Limit to 5000 items
                        print(f"✅ Loaded JSON array with {len(products)} products")
                    else:
                        products = [data]
                        print("✅ Loaded single JSON object")
                except json.JSONDecodeError:
                    # Try JSONL format (one JSON per line)
                    f.seek(0)
                    line_count = 0
                    for line in f:
                        if line_count >= 5000:  # Limit to 5000 items
                            break
                        try:
                            product = json.loads(line.strip())
                            # Only load if has title
                            if 'title' in product and product['title']:
                                products.append(product)
                                line_count += 1
                        except json.JSONDecodeError:
                            continue
                    print(f"✅ Loaded JSONL format with {len(products)} products")

            if products:
                self.df = pd.DataFrame(products)
                print(f"✅ Created DataFrame with {len(self.df)} products")
            else:
                print("❌ No valid products found in dataset")
                self.df = pd.DataFrame()

        except Exception as e:
            print(f"❌ Error loading dataset: {e}")
            self.df = pd.DataFrame()

    def clean_amazon_data(self):
        """Clean and prepare Amazon dataset"""
        print("🔄 Cleaning Amazon data...")
        
        if self.df is None or len(self.df) == 0:
            print("❌ No data to clean")
            return
        
        original_count = len(self.df)
        
        # Remove products without essential info
        if 'title' in self.df.columns:
            self.df = self.df.dropna(subset=['title'])
            self.df = self.df[self.df['title'].str.len() > 0]
        else:
            print("❌ No 'title' column found")
            return
        
        # Create standardized columns
        self.df['id'] = self.df.get('asin', pd.Series(range(len(self.df))))
        self.df['name'] = self.df['title']
        
        # Handle categories
        self.df['main_category'] = self.df.apply(self.extract_main_category, axis=1)
        self.df['subcategory'] = self.df.apply(self.extract_subcategory, axis=1)
        self.df['category_path'] = self.df.apply(self.extract_category_path, axis=1)
        
        # Handle brand
        if 'brand' in self.df.columns:
            self.df['brand'] = self.df['brand'].fillna('Unknown')
        else:
            self.df['brand'] = 'Unknown'
        self.df['brand'] = self.df['brand'].apply(lambda x: str(x) if pd.notna(x) else 'Unknown')
        
        # Handle description
        if 'description' in self.df.columns:
            self.df['description'] = self.df['description'].fillna('')
            self.df['description'] = self.df['description'].apply(self.clean_description)
        else:
            self.df['description'] = ''
        
        # Try converting to numeric, but allow missing prices
        self.df['price'] = pd.to_numeric(self.df.get('price'), errors='coerce')

        # After setting self.df['price']
        self.df = self.df[self.df['price'] > 0]


        
        # Handle images
        self.df['image_url'] = self.df.apply(self.extract_image_url, axis=1)
        
        # Handle ratings
        if 'overall' in self.df.columns:
            self.df['rating'] = pd.to_numeric(self.df['overall'], errors='coerce').fillna(4.0)
        else:
            self.df['rating'] = 4.0
        
        # Filter fashion-related products only
        self.df = self.filter_fashion_products()
        
        # Create combined text for recommendations
        self.df['combined_features'] = self.create_combined_features()
        
        print(f"✅ Cleaned: {original_count} → {len(self.df)} products")
    
    def extract_main_category(self, row):
        field = 'categories'
        if field in row and isinstance(row[field], list) and len(row[field]) > 0:
            # Handle nested list case like [['Clothing', 'Men', 'Shirts']]
            if isinstance(row[field][0], list) and len(row[field][0]) > 0:
                return row[field][0][0]  # e.g., 'Clothing'
            elif isinstance(row[field][0], str):
                return row[field][0]  # e.g., 'Clothing'
        return None

        
        # Fallback: try to extract from title
        title = str(row.get('title', '')).lower()
        if any(word in title for word in ['dress', 'shirt', 'clothing']):
            return 'Clothing'
        elif any(word in title for word in ['shoe', 'boot', 'sneaker']):
            return 'Shoes'
        elif any(word in title for word in ['jewelry', 'necklace', 'ring']):
            return 'Jewelry'
        
        return 'Fashion'
    
    def extract_subcategory(self, row):
        field = 'categories'
        if field in row and isinstance(row[field], list) and len(row[field]) > 0:
            if isinstance(row[field][0], list) and len(row[field][0]) > 1:
                return row[field][0][1]  # e.g., 'Men'
        return None

    
    def extract_category_path(self, row):
        field = 'categories'
        if field in row and isinstance(row[field], list) and len(row[field]) > 0:
            if isinstance(row[field][0], list):
                return " > ".join(row[field][0])  # e.g., "Clothing > Men > Shirts"
        return None

    
    def clean_description(self, desc):
        """Clean product description"""
        if pd.isna(desc) or desc == '':
            return ''
        
        if isinstance(desc, list):
            desc = ' '.join(str(d) for d in desc if pd.notna(d))
        
        desc = str(desc)
        # Remove HTML tags
        desc = re.sub(r'<[^>]+>', '', desc)
        # Remove extra whitespace
        desc = re.sub(r'\s+', ' ', desc).strip()
        
        return desc[:500]  # Limit length
    
    def extract_price(self, price):
        """Extract numeric price"""
        if pd.isna(price):
            return 0.0
        
        if isinstance(price, (int, float)):
            return float(price)
        
        if isinstance(price, str):
            # Extract numbers from price string
            price_match = re.search(r'[\d,]+\.?\d*', price.replace(',', ''))
            if price_match:
                try:
                    return float(price_match.group())
                except:
                    pass
        
        return 0.0
    
    def extract_image_url(self, row):
        """Extract image URL"""
        # Try different image fields
        image_fields = ['imUrl', 'imageURL', 'image', 'imageURLHighRes']
        
        for field in image_fields:
            if field in row and pd.notna(row[field]):
                url = row[field]
                if isinstance(url, list) and len(url) > 0:
                    return str(url[0])
                elif isinstance(url, str) and url.strip():
                    return str(url)
        
        # Fallback placeholder
        return 'https://via.placeholder.com/300x300?text=No+Image'
    
    def filter_fashion_products(self):
        """Filter to keep only fashion-related products"""
        fashion_keywords = [
            'clothing', 'shoes', 'jewelry', 'accessories', 'fashion',
            'apparel', 'dress', 'shirt', 'pants', 'jeans', 'jacket',
            'coat', 'sweater', 'hoodie', 'boots', 'sneakers', 'sandals',
            'necklace', 'bracelet', 'earrings', 'ring', 'watch',
            'bag', 'handbag', 'backpack', 'wallet', 'belt', 'hat',
            'scarf', 'gloves', 'socks', 'underwear', 'bra', 'swimwear'
        ]
        
        # Create fashion filter
        fashion_mask = (
            self.df['name'].str.lower().str.contains('|'.join(fashion_keywords), na=False) |
            self.df['main_category'].str.lower().str.contains('|'.join(fashion_keywords), na=False) |
            self.df['category_path'].str.lower().str.contains('|'.join(fashion_keywords), na=False)
        )
        
        filtered_df = self.df[fashion_mask]
        
        if len(filtered_df) < 100:  # If too few fashion items, keep all
            print("⚠️ Few fashion items found, keeping all products")
            return self.df
        
        print(f"✅ Filtered to {len(filtered_df)} fashion products")
        return filtered_df
    
    def create_combined_features(self):
        """Create combined text features for recommendations"""
        combined = (
            self.df['name'].astype(str) + ' ' +
            self.df['brand'].astype(str) + ' ' +
            self.df['main_category'].astype(str) + ' ' +
            self.df['subcategory'].astype(str) + ' ' +
            self.df['description'].astype(str)
        )
        
        return combined
    
    def build_recommendation_matrix(self):
        """Build TF-IDF matrix for recommendations"""
        if len(self.df) == 0:
            print("❌ No data available for building recommendation matrix")
            return
        
        print("🔄 Building recommendation matrix...")
        
        try:
            self.vectorizer = TfidfVectorizer(
                max_features=2000,  # Reduced for better performance
                stop_words='english',
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.8,
                lowercase=True
            )
            
            self.tfidf_matrix = self.vectorizer.fit_transform(self.df['combined_features'])
            print(f"✅ Built TF-IDF matrix: {self.tfidf_matrix.shape}")
            
        except Exception as e:
            print(f"❌ Error building recommendation matrix: {e}")
            self.tfidf_matrix = None
    
    def get_product_by_id(self, product_id):
        """Get product by ID"""
        try:
            if self.df is None or len(self.df) == 0:
                return None
                
            product = self.df[self.df['id'] == product_id]
            if len(product) > 0:
                return product.iloc[0].to_dict()
            return None
        except Exception as e:
            print(f"Error getting product {product_id}: {e}")
            return None
    
    def get_product_by_index(self, index):
        """Get product by index"""
        if self.df is not None and 0 <= index < len(self.df):
            return self.df.iloc[index].to_dict()
        return None
    
    def get_random_products(self, n=12, category=None, brand=None):
        """Get random products with filtering"""
        if self.df is None or len(self.df) == 0:
            return []
        
        try:
            filtered_df = self.df.copy()
            
            if category:
                filtered_df = filtered_df[
                    filtered_df['main_category'].str.lower().str.contains(category.lower(), na=False)
                ]
            
            if brand and brand != 'Unknown':
                filtered_df = filtered_df[
                    filtered_df['brand'].str.lower().str.contains(brand.lower(), na=False)
                ]
            
            sample_size = min(n, len(filtered_df))
            if sample_size > 0:
                return filtered_df.sample(n=sample_size).to_dict('records')
            else:
                # Fallback to any products
                return self.df.sample(n=min(n, len(self.df))).to_dict('records')
                
        except Exception as e:
            print(f"Error getting random products: {e}")
            return []
    
    def get_recommendations(self, product_id, n_recommendations=6):
        """Get content-based recommendations"""
        if self.tfidf_matrix is None or self.df is None or len(self.df) == 0:
            print("No recommendation matrix available, returning random products")
            return self.get_random_products(n_recommendations)
        
        try:
            product_indices = self.df[self.df['id'] == product_id].index
            if len(product_indices) == 0:
                print(f"Product {product_id} not found, returning random products")
                return self.get_random_products(n_recommendations)
            
            product_idx = product_indices[0]
            
            # Calculate similarities
            cosine_similarities = cosine_similarity(
                self.tfidf_matrix[product_idx:product_idx+1], 
                self.tfidf_matrix
            ).flatten()
            
            # Get most similar products (excluding the product itself)
            similar_indices = cosine_similarities.argsort()[::-1][1:n_recommendations+1]
            
            recommendations = self.df.iloc[similar_indices].to_dict('records')
            print(f"✅ Generated {len(recommendations)} recommendations for {product_id}")
            return recommendations
            
        except Exception as e:
            print(f"Error getting recommendations for {product_id}: {e}")
            return self.get_random_products(n_recommendations)
    
    def search_products(self, query, n_results=12):
        """Search products by query"""
        if self.df is None or len(self.df) == 0:
            return []
        
        try:
            query = query.lower().strip()
            if not query:
                return self.get_random_products(n_results)
            
            # Multi-field search
            mask = (
                self.df['name'].str.lower().str.contains(query, na=False) |
                self.df['brand'].str.lower().str.contains(query, na=False) |
                self.df['main_category'].str.lower().str.contains(query, na=False) |
                self.df['subcategory'].str.lower().str.contains(query, na=False) |
                self.df['description'].str.lower().str.contains(query, na=False)
            )
            
            results = self.df[mask].head(n_results)
            return results.to_dict('records')
            
        except Exception as e:
            print(f"Error searching for '{query}': {e}")
            return []
    
    def get_featured_products(self):
        """Get featured products for homepage"""
        try:
            if self.df is None or len(self.df) == 0:
                return []
                
            # Get high-rated products
            high_rated = self.df[self.df['rating'] >= 4.0]
            if len(high_rated) >= 8:
                return high_rated.sample(n=8).to_dict('records')
            else:
                return self.get_random_products(8)
        except Exception as e:
            print(f"Error getting featured products: {e}")
            return self.get_random_products(8)
    
    def get_categories(self):
        """Get available categories"""
        if self.df is None or len(self.df) == 0:
            return []
        
        try:
            categories = self.df['main_category'].value_counts().head(15)
            return [{'name': cat, 'count': count} for cat, count in categories.items()]
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []
    
    def get_brands(self):
        """Get available brands"""
        if self.df is None or len(self.df) == 0:
            return []
        
        try:
            brands = self.df['brand'].value_counts().head(20)
            return [{'name': brand, 'count': count} for brand, count in brands.items() if brand != 'Unknown']
        except Exception as e:
            print(f"Error getting brands: {e}")
            return []
    def get_products_by_category(self, category_name):
        return [p for p in self.products if p.get("main_category") == category_name]

    def get_products_by_brand(self, brand_name):
        return [p for p in self.products if p.get("brand") == brand_name]

    def get_stats(self):
        """Get dataset statistics"""
        if self.df is None or len(self.df) == 0:
            return {'total_products': 0}
        
        try:
            stats = {
                'total_products': len(self.df),
                'total_brands': self.df['brand'].nunique(),
                'total_categories': self.df['main_category'].nunique(),
                'avg_rating': round(self.df['rating'].mean(), 1)
            }
            
            # Add price stats if available
            price_data = self.df[self.df['price'] > 0]
            if len(price_data) > 0:
                stats.update({
                    'avg_price': round(price_data['price'].mean(), 2),
                    'price_range': {
                        'min': round(price_data['price'].min(), 2),
                        'max': round(price_data['price'].max(), 2)
                    }
                })
            else:
                stats.update({
                    'avg_price': 0,
                    'price_range': {'min': 0, 'max': 0}
                })
            
            return stats
            
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {'total_products': len(self.df) if self.df is not None else 0}