**StyleSense AI – ML-Powered Recommendation System**👗🧠
---
**StyleSense AI** is a Flask-based web application that uses machine learning to recommend fashion products (Clothing, Shoes, Jewelry) based on user search, categories, brands, and product similarity. Built using real-world Amazon fashion product metadata, the system aims to bring smart, intuitive e-commerce recommendations using data science.

<img width="1919" height="921" alt="image" src="https://github.com/user-attachments/assets/21305e9d-baf4-4d8e-9f93-2d01b9a43b0c" />

---

## 🚀 Features

- 🔍 Product Search with intelligent keyword matching  
- 🧠 ML-powered product similarity using TF-IDF and cosine similarity  
- 🏷️ Filter by brand, category  
- 📊 Dataset statistics (total products, average rating, etc.)  
- 📷 Product image rendering with dynamic HTML display  
- 💬 Clean and responsive Bootstrap UI  

---

## 🛠 Languages, Libraries & Tools-

### 🧑‍💻 Programming Languages
- Python 3.12
- HTML, CSS (Bootstrap 5)
- JavaScript

### ⚙️ Python Libraries
- `Flask` – Web framework  
- `scikit-learn` – TF-IDF Vectorization & Similarity  
- `pandas`, `numpy` – Data processing  
- `json` – Metadata parsing  
- `gunicorn` – For deployment (optional)

### 🖼 Frontend Tools
- Bootstrap 5.3  
- Font Awesome  
- Jinja2 (Flask templating)

---

## 📁 Project Structure

```

project/
├── app.py                       # Main Flask app logic
├── requirements.txt             # Python dependencies
├── data/
│   └── clean_fashion_data.json  # Amazon metadata
├── models/
│   └── recommender.py           # Core recommendation logic
├── static/
│   ├── css/style.css            # Custom styling
│   └── js/main.js               # Main Script
├── templates/
│   ├── index.html               # Homepage template
│   ├── product.html             # Product details page
│   ├── search.html              # Search results page
│   ├── brand.html               # Brand results page
│   ├── category.html            # Category results page
│   ├── error.html               # Error page
│   └── base.html                # Base layout for all pages
├── .gitignore                   # Ignored files

````

---

## 🧠 Data Science Concepts Used

- **TF-IDF Vectorization**: To extract relevant textual features from product titles and descriptions.  
- **Cosine Similarity**: For recommending similar products based on TF-IDF vectors.  
- **Data Cleaning**: Removing missing/null entries, duplicate filtering.  
- **Dimensionality Reduction (optional)**: To speed up similarity computations.  
- **Categorical Data Handling**: Grouping by brand, category for filtering.  
- **Web Scraping Handling (if added)**: Not currently implemented but extendable.

---

## 📈 Business Analytics Concepts Used

- **Customer Segmentation** (via category/brand filtering)  
- **Product Recommendation Systems** (content-based filtering)  
- **Search Behavior Analytics** (query matching)  
- **Product Metadata Analysis** (rating averages, counts)  
- **Dashboard-like Visual Summary** (in footer)

---

### 🌐 Hosting the Website (Ways to Share)

### Method 1: GitHub + Render (Free)
1. Push your project to GitHub.
2. Go to [https://render.com](https://render.com), create a free account.
3. Create a new Web Service → Connect GitHub repo → Choose Flask `app.py`.
4. In Build & Deploy:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. Set environment variable: `PORT=10000` if needed.

### Method 2: Localhost (for demo on your PC)
```bash
git clone https://github.com/YOUR_USERNAME/stylesense-ai.git
cd stylesense-ai
pip install -r requirements.txt
python app.py
````

Then open: `http://127.0.0.1:5000`



## ✅ How the Website Works

* `index.html` displays featured products with stats from the dataset.
* Product info is read from `clean_fashion_data.json` and loaded into memory.
* Users can:

  * Search products → `search_results.html`
  * Click product → `product.html`
  * Browse by category/brand → `catgory.html`,`brand.html`
* Similar items are fetched using **TF-IDF + cosine similarity** from `recommender.py`.

---

## 🔍 How `recommender.py` Works

The `AmazonFashionRecommender` class:

* Loads JSON data and preprocesses it
* Applies TF-IDF vectorization on product titles
* Stores cosine similarity matrix
* Provides `recommend(product_id)` to fetch top-k similar items

---

## 📷 Troubleshooting Images

Ensure:

* Image URLs are correct in the dataset
* You're using `{{ product.image }}` correctly inside the template
* Static images (if used locally) are placed in `static/product_images/`

---

## 📃 License

This project is for educational purposes. You are free to reuse, modify, or extend it.

---

## 🙌 Credits

* Amazon Open Metadata (Fashion)
* Bootstrap, Flask, scikit-learn
* Developed by Harika Ayyalasomayajula and Aashray Boddu


---
