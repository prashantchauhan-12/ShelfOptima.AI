import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def preprocess_sales_data(raw_data):
    """
    Cleans and prepares incoming sales data for the ML model and visualizations.
    Utilizes pandas and numpy to ensure the format is correct for our pipeline.
    """
    if not raw_data:
        raise ValueError("No data provided for preprocessing.")

    df = pd.DataFrame(raw_data)

    required_cols = ['item_id', 'name', 'category', 'sales_qty', 'price', 'cost']
    for col in required_cols:
        if col not in df.columns:
            df[col] = np.nan
            logger.warning(f"Field '{col}' is missing. Filled with NaN.")

    df = df.dropna(subset=['item_id', 'name'])

    df['sales_qty'] = pd.to_numeric(df['sales_qty'], errors='coerce').fillna(0).astype(int)
    df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0.0)
    df['cost'] = pd.to_numeric(df['cost'], errors='coerce').fillna(0.0)

    # Feature Engineering
    df['profit_margin'] = df['price'] - df['cost']
    df['margin_pct'] = np.where(df['price'] > 0, (df['profit_margin'] / df['price']) * 100, 0)
    df['total_revenue'] = df['sales_qty'] * df['price']
    df['total_profit'] = df['sales_qty'] * df['profit_margin']
    df['revenue_per_unit'] = df['price']
    df['profit_per_unit'] = df['profit_margin']

    df = df.sort_values(by='total_profit', ascending=False).reset_index(drop=True)
    return df


def aggregate_category_data(df):
    """Aggregates data by category for shelf space reporting."""
    if df.empty:
        return pd.DataFrame(columns=['category', 'total_sales_qty', 'total_revenue', 'total_profit', 'product_count', 'avg_margin_pct'])

    agg_df = df.groupby('category').agg(
        total_sales_qty=('sales_qty', 'sum'),
        total_revenue=('total_revenue', 'sum'),
        total_profit=('total_profit', 'sum'),
        product_count=('item_id', 'count'),
        avg_margin_pct=('margin_pct', 'mean')
    ).reset_index()
    agg_df['avg_margin_pct'] = agg_df['avg_margin_pct'].round(1)
    return agg_df


def compute_kpis(df):
    """Calculate high-level KPI metrics for the dashboard summary cards."""
    if df.empty:
        return {
            "total_revenue": 0, "total_profit": 0, "total_units_sold": 0,
            "avg_margin_pct": 0, "top_product": "N/A", "top_product_profit": 0,
            "num_products": 0, "num_categories": 0, "hhi_concentration": 0,
            "diversification_score": 0
        }

    total_revenue = float(df['total_revenue'].sum())
    total_profit = float(df['total_profit'].sum())
    total_units = int(df['sales_qty'].sum())
    avg_margin = float(df['margin_pct'].mean())
    top_product = str(df.iloc[0]['name'])
    top_product_profit = float(df.iloc[0]['total_profit'])
    num_products = len(df)
    num_categories = int(df['category'].nunique())

    # Revenue concentration — Herfindahl index
    if total_revenue > 0:
        shares = df['total_revenue'] / total_revenue
        hhi = float((shares ** 2).sum())
    else:
        hhi = 0.0

    return {
        "total_revenue": round(total_revenue, 2),
        "total_profit": round(total_profit, 2),
        "total_units_sold": total_units,
        "avg_margin_pct": round(avg_margin, 1),
        "top_product": top_product,
        "top_product_profit": round(top_product_profit, 2),
        "num_products": num_products,
        "num_categories": num_categories,
        "hhi_concentration": round(hhi, 4),
        "diversification_score": round((1 - hhi) * 100, 1)
    }


def compute_trend_data(history_records):
    """Process historical records into time-series trend data."""
    if not history_records:
        return {"dates": [], "series": {}}

    df = pd.DataFrame(history_records)
    df['daily_revenue'] = pd.to_numeric(df['daily_revenue'], errors='coerce').fillna(0)

    pivot = df.pivot_table(index='date', columns='category', values='daily_revenue', aggfunc='sum').fillna(0)
    pivot = pivot.sort_index()

    series = {}
    for col in pivot.columns:
        series[col] = [round(v, 2) for v in pivot[col].tolist()]

    series["Total"] = [round(v, 2) for v in pivot.sum(axis=1).tolist()]

    return {
        "dates": pivot.index.tolist(),
        "series": series
    }
