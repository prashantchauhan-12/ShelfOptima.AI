import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import numpy as np


def _fig_to_base64(fig):
    """Convert a matplotlib figure to a base64-encoded PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', facecolor='#0f0f1a', bbox_inches='tight', dpi=120)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return b64


def _new_dark_figure(figsize=(10, 6)):
    """Create a new figure with dark theme applied locally (not globally)."""
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor('#0f0f1a')
    ax.set_facecolor('#16162a')
    ax.tick_params(colors='#9090a8')
    ax.xaxis.label.set_color('#c0c0d8')
    ax.yaxis.label.set_color('#c0c0d8')
    ax.title.set_color('#e0e0f0')
    for spine in ax.spines.values():
        spine.set_color('#2a2a4a')
    ax.grid(True, linestyle='--', alpha=0.3, color='#22223a')
    return fig, ax


def generate_profit_chart(df):
    """Horizontal bar chart: Top items by total profit."""
    if df.empty:
        return ""
    fig, ax = _new_dark_figure((10, 6))
    chart_data = df.sort_values(by='total_profit', ascending=True).tail(10)
    colors = sns.color_palette("viridis", n_colors=len(chart_data))
    ax.barh(chart_data['name'], chart_data['total_profit'], color=colors)
    ax.set_title("Top 10 Items by Total Profit", fontsize=15, weight='bold', pad=15)
    ax.set_xlabel("Total Profit ($)", fontsize=11)
    for i, v in enumerate(chart_data['total_profit']):
        ax.text(v + 10, i, f'${v:,.0f}', va='center', fontsize=9, color='#a0ffcc')
    return _fig_to_base64(fig)


def generate_sales_frequency_chart(df):
    """Distribution histogram with KDE of sales quantity."""
    if df.empty:
        return ""
    fig, ax = _new_dark_figure((10, 6))
    sns.histplot(df['sales_qty'], bins=12, kde=True, color='#00e5ff', ax=ax, edgecolor='#0a0a1e')
    mean_val = df['sales_qty'].mean()
    ax.axvline(mean_val, color='#ff6b6b', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.0f}')
    ax.legend(fontsize=10, facecolor='#16162a', edgecolor='#2a2a4a', labelcolor='#e0e0f0')
    ax.set_title("Sales Frequency Distribution", fontsize=15, weight='bold', pad=15)
    ax.set_xlabel("Sales Quantity", fontsize=11)
    ax.set_ylabel("Number of Items", fontsize=11)
    return _fig_to_base64(fig)


def generate_category_pie_chart(agg_df):
    """Pie chart of revenue share by category."""
    if agg_df.empty:
        return ""
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor('#0f0f1a')
    palette = ['#6366f1', '#22d3ee', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6']
    wedges, texts, autotexts = ax.pie(
        agg_df['total_revenue'], labels=agg_df['category'],
        autopct='%1.1f%%', startangle=140,
        colors=palette[:len(agg_df)],
        textprops={'color': '#e0e0f0', 'fontsize': 11},
        pctdistance=0.8, wedgeprops=dict(edgecolor='#0f0f1a', linewidth=2)
    )
    for t in autotexts:
        t.set_fontsize(10)
        t.set_color('#ffffff')
    ax.set_title("Revenue Share by Category", fontsize=15, weight='bold', pad=20, color='#e0e0f0')
    return _fig_to_base64(fig)


def generate_margin_comparison_chart(df):
    """Grouped bar chart comparing price vs cost per item."""
    if df.empty:
        return ""
    fig, ax = _new_dark_figure((12, 6))
    top = df.head(10)
    x = np.arange(len(top))
    w = 0.35
    ax.bar(x - w / 2, top['price'], w, label='Sale Price', color='#6366f1')
    ax.bar(x + w / 2, top['cost'], w, label='Cost Price', color='#ef4444', alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(top['name'], rotation=35, ha='right', fontsize=8)
    ax.legend(fontsize=10, facecolor='#16162a', edgecolor='#2a2a4a', labelcolor='#e0e0f0')
    ax.set_title("Price vs Cost Comparison (Top 10)", fontsize=15, weight='bold', pad=15)
    ax.set_ylabel("Price ($)", fontsize=11)
    return _fig_to_base64(fig)


def generate_shelf_allocation_chart(allocations):
    """Treemap-style horizontal stacked bar showing shelf space allocation."""
    if not allocations:
        return ""
    fig, ax = plt.subplots(figsize=(14, 3))
    fig.patch.set_facecolor('#0f0f1a')
    ax.set_facecolor('#16162a')

    sorted_alloc = sorted(allocations, key=lambda x: x['suggested_shelf_space_pct'], reverse=True)
    palette = sns.color_palette("Spectral", n_colors=len(sorted_alloc))

    left = 0
    for i, item in enumerate(sorted_alloc):
        pct = item['suggested_shelf_space_pct']
        ax.barh(0, pct, left=left, color=palette[i], edgecolor='#0f0f1a', height=0.6)
        if pct > 4:
            ax.text(left + pct / 2, 0, f"{item['name'][:12]}\n{pct}%",
                    ha='center', va='center', fontsize=7, color='white', weight='bold')
        left += pct

    ax.set_xlim(0, 100)
    ax.set_yticks([])
    ax.set_xlabel("Shelf Space (%)", fontsize=11, color='#c0c0d8')
    ax.set_title("Optimal Shelf Space Allocation Map", fontsize=15, weight='bold', pad=15, color='#e0e0f0')
    ax.tick_params(colors='#9090a8')
    for spine in ax.spines.values():
        spine.set_color('#2a2a4a')
    return _fig_to_base64(fig)
