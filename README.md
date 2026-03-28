# 🧠 ShelfOptima AI — Shelf Space Optimization System

ShelfOptima is a full-stack AI-powered system built to help retailers intelligently optimize their shelf space allocation. By analyzing profit margins, sales velocity, and historical trends, the system uses a Neural Network to score items and suggest optimal display real-estate percentages.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-API-green?logo=flask)
![TensorFlow](https://img.shields.io/badge/TensorFlow-ML-orange?logo=tensorflow)
![MongoDB](https://img.shields.io/badge/MongoDB-Database-brightgreen?logo=mongodb)
![Pandas](https://img.shields.io/badge/Pandas-DataProcessing-purple?logo=pandas)

---

## 🚀 Key Features

| Feature | Description |
|--------|-------------|
| **AI Shelf Allocation** | TensorFlow Sequential model dynamically determines shelf space % based on a multi-factor composite score (profit, velocity, revenue, margin) |
| **5 Visual Dashboards** | Seaborn/Matplotlib generated: Profit Index, Sales Distribution, Category Pie, Price vs Cost, Shelf Allocation Map |
| **Real-Time KPI Cards** | Animated counters for Total Revenue, Profit, Units Sold, Avg Margin, Top Product, and Portfolio Diversity Score (HHI) |
| **MongoDB Integration** | Full CRUD via PyMongo — insert, retrieve, delete, and search products with graceful in-memory fallback |
| **30-Day Trend Analysis** | Canvas-rendered multi-line chart showing historical revenue trends per category |
| **Product Search** | Debounced global search with dropdown results across ID, name, and category |
| **Inventory Management** | Full inventory table with inline search, filtering, and delete capabilities |
| **CSV Export** | One-click export of ML predictions to downloadable CSV |
| **Priority Tiers** | Products classified as HIGH / MEDIUM / LOW priority based on neural network scoring |
| **Premium Dark UI** | Glassmorphism design with animated gradients, pulse effects, and responsive layout |

---

## 🛠 Tech Stack

| Layer | Technologies |
|-------|------------|
| **Backend / API** | Python 3, Flask, Werkzeug |
| **Machine Learning** | TensorFlow / Keras (Sequential API, 4-layer Dense NN) |
| **Data Processing** | Pandas, NumPy (Feature Engineering, KPI Computation, Trend Analysis) |
| **Database** | MongoDB (PyMongo) with in-memory fallback |
| **Data Visualization** | Seaborn, Matplotlib (5 chart types, Base64 serialization) |
| **Frontend** | HTML5, CSS3 (Custom Design System), Vanilla JavaScript (Canvas API) |

---

## 📂 Project Structure

```
shelf-space-optimizer/
├── app.py                         # Flask entry point — routes & API gateway
├── requirements.txt               # Python dependencies
├── .gitignore
├── README.md
│
├── backend/                       # Server-side logic
│   ├── __init__.py
│   ├── database.py                # MongoDB connection + mock fallback + CRUD
│   ├── data_processing.py         # Pandas/NumPy cleaning, KPI computation, trends
│   ├── ml_model.py                # TensorFlow neural network inference interface
│   └── visualization.py           # Seaborn/Matplotlib chart generation (5 types)
│
└── frontend/                      # Client-side presentation layer
    ├── templates/
    │   └── index.html             # Main dashboard UI (6 views)
    └── static/
        ├── css/
        │   └── style.css          # Premium dark-mode design system
        └── js/
            └── main.js            # Frontend controller (AJAX, Canvas, animations)
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves the dashboard UI |
| `GET` | `/api/status` | System health and DB connection metadata |
| `GET` | `/api/sales` | Retrieve all sales records |
| `POST` | `/api/sales` | Insert new sales data into MongoDB |
| `DELETE` | `/api/sales?item_id=P001` | Delete a product by ID |
| `GET` | `/api/search?q=coffee` | Search products by name/category/ID |
| `GET` | `/api/insights` | **Main pipeline** — preprocessing → TF inference → visualization |
| `GET` | `/api/trends` | 30-day historical revenue trend data |
| `GET` | `/api/export` | Export predictions as CSV download |

---

## 📌 My Contribution

My primary focus was the **Full-Stack API Integration and Frontend Experience**. 
1. **API Architecture**: Designed and built all 7 Flask endpoints that route frontend requests to the underlying ML and data processing layers.
2. **Data Preprocessing Engine**: Used Pandas and NumPy to clean incoming sales data, compute feature vectors (margin %, total profit, revenue per unit), and aggregate category-level insights.
3. **Visualizing Insights**: Created 5 distinct Seaborn/Matplotlib chart types (profit bars, frequency distributions, pie charts, price-cost comparisons, and shelf allocation maps), serialized as Base64 for API delivery.
4. **Database Layer**: Implemented the PyMongo connection logic with a graceful in-memory fallback, CRUD operations, and product search functionality.
5. **Frontend Dashboard**: Designed a premium, responsive dark-mode interface with 6 distinct views, animated KPI counters, canvas-based trend charts, debounced search, and real-time system logs.
6. **Data Pipeline Orchestration**: Built the `/api/insights` endpoint that chains data retrieval → cleaning → TF inference → visualization generation → KPI computation in a single, cohesive pipeline.

---

## ⚙️ Running Locally

### Prerequisites
- Python 3.8+
- MongoDB (Optional — the app includes a graceful fallback to a mock in-memory DB)

### Installation

```bash
git clone https://github.com/yourusername/shelf-space-optimizer.git
cd shelf-space-optimizer
pip install -r requirements.txt
```

### Start the Server

```bash
python app.py
```

Navigate to **`http://localhost:5000`** in your browser.

The dashboard auto-triggers the ML pipeline on load, processes the seed dataset, and renders all visualizations.

---
