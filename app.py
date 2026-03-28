import os
import sys
import logging
import csv
import io

from flask import Flask, jsonify, request, render_template

# Add backend directory to Python path so imports resolve correctly
BACKEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, BACKEND_DIR)

from database import db
from data_processing import preprocess_sales_data, aggregate_category_data, compute_kpis, compute_trend_data
from ml_model import predict_shelf_space
from visualization import (
    generate_profit_chart,
    generate_sales_frequency_chart,
    generate_category_pie_chart,
    generate_margin_comparison_chart,
    generate_shelf_allocation_chart
)

# Flask app with explicit template and static folder paths
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')

app = Flask(
    __name__,
    template_folder=os.path.join(FRONTEND_DIR, 'templates'),
    static_folder=os.path.join(FRONTEND_DIR, 'static')
)

logging.basicConfig(level=logging.INFO)


# ======================== ROUTES ========================

@app.route('/')
def dashboard():
    """Serves the main dashboard UI."""
    return render_template('index.html')


@app.route('/api/status', methods=['GET'])
def system_status():
    """Returns system health and DB connection metadata."""
    try:
        info = db.get_connection_info()
        return jsonify({"status": "ok", "db": info})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/sales', methods=['GET', 'POST', 'DELETE'])
def manage_sales():
    """CRUD endpoint for sales records."""
    if request.method == 'POST':
        data = request.json
        if not data:
            return jsonify({"error": "Invalid payload. Send JSON body."}), 400
        result = db.insert_sales_data(data)
        return jsonify(result), 201

    elif request.method == 'DELETE':
        item_id = request.args.get('item_id')
        if not item_id:
            return jsonify({"error": "item_id query parameter required."}), 400
        result = db.delete_product(item_id)
        return jsonify({"status": "success", **result})

    else:  # GET
        records = db.get_all_sales()
        return jsonify({"status": "success", "data": records, "count": len(records)})


@app.route('/api/search', methods=['GET'])
def search():
    """Search products by name, category, or item_id."""
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({"results": [], "count": 0})
    results = db.search_products(q)
    return jsonify({"results": results, "count": len(results)})


@app.route('/api/insights', methods=['GET'])
def get_insights():
    """
    Main ML pipeline endpoint:
    1. Fetches data from MongoDB
    2. Cleans with Pandas/NumPy
    3. Runs TF model inference
    4. Generates Seaborn/Matplotlib charts
    5. Computes KPIs
    """
    raw_data = db.get_all_sales()
    if not raw_data:
        return jsonify({"status": "error", "message": "No sales data available. Add data first."}), 404

    try:
        clean_df = preprocess_sales_data(raw_data)
        shelf_allocations = predict_shelf_space(clean_df)
        agg_data = aggregate_category_data(clean_df)
        kpis = compute_kpis(clean_df)

        charts = {
            "profit_per_item": generate_profit_chart(clean_df),
            "sales_frequency": generate_sales_frequency_chart(clean_df),
            "category_pie": generate_category_pie_chart(agg_data),
            "margin_comparison": generate_margin_comparison_chart(clean_df),
            "shelf_allocation_map": generate_shelf_allocation_chart(shelf_allocations)
        }

    except Exception as e:
        app.logger.error(f"Pipeline error: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({
        "status": "success",
        "kpis": kpis,
        "predictions": shelf_allocations,
        "charts": charts,
        "category_summary": agg_data.to_dict(orient='records')
    })


@app.route('/api/trends', methods=['GET'])
def get_trends():
    """Returns 30-day historical trend data for time-series charting."""
    try:
        history = db.get_historical_data()
        trend_data = compute_trend_data(history)
        return jsonify({"status": "success", "trends": trend_data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/export', methods=['GET'])
def export_csv():
    """Export current predictions as a downloadable CSV file."""
    raw_data = db.get_all_sales()
    if not raw_data:
        return jsonify({"error": "No data to export."}), 404

    try:
        clean_df = preprocess_sales_data(raw_data)
        allocations = predict_shelf_space(clean_df)

        if not allocations:
            return jsonify({"error": "No predictions generated."}), 404

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=allocations[0].keys())
        writer.writeheader()
        writer.writerows(allocations)

        return app.response_class(
            output.getvalue(),
            mimetype='text/csv',
            headers={"Content-Disposition": "attachment; filename=shelf_space_predictions.csv"}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ======================== ENTRY POINT ========================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
