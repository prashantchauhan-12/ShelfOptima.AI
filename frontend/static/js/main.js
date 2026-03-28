// ============================================================
// ShelfOptima AI — Frontend Controller
// Handles API calls, data rendering, navigation, and charting
// ============================================================

const logEl = document.getElementById('system-logs');
let allPredictions = []; // Cache for filtering
let inventoryData = [];  // Cache for inventory filtering

// ====================== LOGGING ======================
function addLog(msg) {
    const ts = new Date().toISOString().split('T')[1].split('.')[0];
    logEl.innerHTML += `\n<span style="color:#666">[${ts}]</span> ${msg}`;
    logEl.scrollTo(0, logEl.scrollHeight);
}

function clearLogs() {
    logEl.innerHTML = 'Logs cleared.\n';
}

// ====================== NAVIGATION ======================
document.querySelectorAll('.nav-links li').forEach(item => {
    item.addEventListener('click', () => {
        document.querySelectorAll('.nav-links li').forEach(l => l.classList.remove('active'));
        document.querySelectorAll('.view-section').forEach(v => v.classList.add('hidden'));

        item.classList.add('active');
        const viewId = item.dataset.view + '-view';
        document.getElementById(viewId).classList.remove('hidden');

        // Update page title
        const titles = {
            'dashboard': ['Dashboard', 'Real-time ML predictions & shelf space optimization'],
            'analytics': ['Analytics', 'Seaborn & Matplotlib powered visual insights'],
            'inventory': ['Inventory', 'Complete product inventory management'],
            'add-data': ['Add Data', 'Ingest new POS data into MongoDB'],
            'trends': ['Trends', '30-day historical revenue analysis'],
            'logs': ['System Logs', 'Real-time pipeline execution logs']
        };
        const [title, subtitle] = titles[item.dataset.view] || ['Dashboard', ''];
        document.getElementById('page-title').textContent = title;
        document.getElementById('page-subtitle').textContent = subtitle;

        addLog(`Navigated to <span style="color:#818cf8">${title}</span>`);

        // Load specific views
        if (item.dataset.view === 'inventory') loadInventory();
        if (item.dataset.view === 'trends') loadTrends();
    });
});

// ====================== NUMBER FORMATTING ======================
function formatCurrency(val) {
    if (val >= 1000) return '$' + (val / 1000).toFixed(1) + 'K';
    return '$' + val.toFixed(2);
}

function animateCounter(el, target, prefix = '', suffix = '') {
    const duration = 800;
    const start = 0;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        // Ease out cubic
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = start + (target - start) * eased;

        if (typeof target === 'number' && target >= 100) {
            el.textContent = prefix + Math.round(current).toLocaleString() + suffix;
        } else {
            el.textContent = prefix + current.toFixed(1) + suffix;
        }

        if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
}

// ====================== SYSTEM STATUS ======================
async function checkStatus() {
    try {
        const res = await fetch('/api/status');
        const data = await res.json();
        document.getElementById('db-type-label').textContent = data.db.type;
        document.getElementById('product-count-label').textContent = data.db.records;
        addLog(`DB Status: <span style="color:#10b981">${data.db.type}</span> | ${data.db.records} records`);
    } catch (e) {
        addLog(`<span style="color:#ef4444">Status check failed</span>`);
    }
}

// ====================== MAIN PIPELINE ======================
async function runPipeline() {
    addLog('🚀 Initiating Full ML Pipeline...');
    const btn = document.getElementById('run-btn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing...';

    document.getElementById('loader').classList.remove('hidden');
    document.getElementById('predictions-section').classList.add('hidden');
    document.getElementById('shelf-map-section').classList.add('hidden');

    const stepsEl = document.getElementById('loader-steps');
    const steps = [
        'Fetching data from MongoDB...',
        'Running Pandas preprocessing...',
        'Computing NumPy feature vectors...',
        'Loading TensorFlow model...',
        'Running neural network inference...',
        'Generating Seaborn visualizations...',
        'Computing shelf allocations...'
    ];

    let stepIdx = 0;
    const stepInterval = setInterval(() => {
        if (stepIdx < steps.length) {
            stepsEl.textContent = `▸ ${steps[stepIdx]}`;
            addLog(`   ↳ ${steps[stepIdx]}`);
            stepIdx++;
        }
    }, 400);

    try {
        const res = await fetch('/api/insights');
        const data = await res.json();
        clearInterval(stepInterval);

        if (data.status === 'success') {
            addLog('✅ <span style="color:#10b981">Pipeline completed successfully!</span>');

            // KPIs
            const k = data.kpis;
            animateCounter(document.getElementById('kpi-revenue'), k.total_revenue, '$');
            animateCounter(document.getElementById('kpi-profit'), k.total_profit, '$');
            animateCounter(document.getElementById('kpi-units'), k.total_units_sold);
            animateCounter(document.getElementById('kpi-margin'), k.avg_margin_pct, '', '%');
            document.getElementById('kpi-top').textContent = k.top_product;
            animateCounter(document.getElementById('kpi-diversity'), k.diversification_score, '', '%');

            // Predictions table
            allPredictions = data.predictions;
            renderPredictions(allPredictions);
            document.getElementById('predictions-section').classList.remove('hidden');

            // Charts (for analytics view, pre-cache)
            if (data.charts.profit_per_item) {
                document.getElementById('profit-chart').src = 'data:image/png;base64,' + data.charts.profit_per_item;
            }
            if (data.charts.sales_frequency) {
                document.getElementById('freq-chart').src = 'data:image/png;base64,' + data.charts.sales_frequency;
            }
            if (data.charts.category_pie) {
                document.getElementById('category-pie-chart').src = 'data:image/png;base64,' + data.charts.category_pie;
            }
            if (data.charts.margin_comparison) {
                document.getElementById('margin-chart').src = 'data:image/png;base64,' + data.charts.margin_comparison;
            }
            if (data.charts.shelf_allocation_map) {
                document.getElementById('shelf-map-chart').src = 'data:image/png;base64,' + data.charts.shelf_allocation_map;
                document.getElementById('shelf-map-section').classList.remove('hidden');
            }

            // Category summary table
            renderCategorySummary(data.category_summary);

            addLog(`   📊 ${data.predictions.length} predictions generated`);
            addLog(`   📈 5 visualizations rendered`);
            addLog(`   📁 ${data.category_summary.length} categories analyzed`);
        } else {
            addLog(`<span style="color:#ef4444">Error: ${data.message}</span>`);
        }
    } catch (err) {
        clearInterval(stepInterval);
        addLog(`<span style="color:#ef4444">Connection Error: ${err.message}</span>`);
    } finally {
        document.getElementById('loader').classList.add('hidden');
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-bolt"></i> Run ML Pipeline';
    }
}

// ====================== RENDER PREDICTIONS TABLE ======================
function renderPredictions(predictions) {
    const tbody = document.querySelector('#predictions-table tbody');
    tbody.innerHTML = '';
    predictions.forEach(p => {
        const prioClass = p.priority === 'HIGH' ? 'badge-high' : p.priority === 'MEDIUM' ? 'badge-medium' : 'badge-low';
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${p.item_id}</strong></td>
            <td>${p.name}</td>
            <td><span class="badge-cat">${p.category}</span></td>
            <td>${p.shelf_location || '—'}</td>
            <td>${p.sales_qty.toLocaleString()}</td>
            <td style="color:#10b981">$${p.total_profit.toLocaleString()}</td>
            <td>${p.margin_pct}%</td>
            <td><strong style="color:#22d3ee">${p.suggested_shelf_space_pct}%</strong></td>
            <td><span class="badge ${prioClass}">${p.priority}</span></td>
        `;
        tbody.appendChild(tr);
    });
}

function filterPredictions() {
    const val = document.getElementById('filter-priority').value;
    if (val === 'ALL') {
        renderPredictions(allPredictions);
    } else {
        renderPredictions(allPredictions.filter(p => p.priority === val));
    }
}

// ====================== CATEGORY SUMMARY TABLE ======================
function renderCategorySummary(summary) {
    const tbody = document.querySelector('#category-table tbody');
    tbody.innerHTML = '';
    summary.forEach(c => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><span class="badge-cat">${c.category}</span></td>
            <td>${c.product_count}</td>
            <td>${c.total_sales_qty.toLocaleString()}</td>
            <td style="color:#10b981">$${c.total_revenue.toLocaleString()}</td>
            <td style="color:#22d3ee">$${c.total_profit.toLocaleString()}</td>
            <td>${c.avg_margin_pct}%</td>
        `;
        tbody.appendChild(tr);
    });
}

// ====================== INVENTORY ======================
async function loadInventory() {
    addLog('Loading inventory data...');
    try {
        const res = await fetch('/api/sales');
        const data = await res.json();
        inventoryData = data.data;
        renderInventory(inventoryData);
        addLog(`Inventory loaded: ${data.count} products`);
    } catch (e) {
        addLog(`<span style="color:#ef4444">Failed to load inventory</span>`);
    }
}

function renderInventory(items) {
    const tbody = document.querySelector('#inventory-table tbody');
    tbody.innerHTML = '';
    items.forEach(item => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${item.item_id}</strong></td>
            <td>${item.name}</td>
            <td><span class="badge-cat">${item.category}</span></td>
            <td>${item.sales_qty}</td>
            <td>$${item.price}</td>
            <td>$${item.cost}</td>
            <td>${item.supplier || '—'}</td>
            <td>${item.shelf_location || '—'}</td>
            <td><button class="btn-danger" onclick="deleteProduct('${item.item_id}')"><i class="fa-solid fa-trash"></i></button></td>
        `;
        tbody.appendChild(tr);
    });
}

function filterInventory(query) {
    const q = query.toLowerCase();
    const filtered = inventoryData.filter(i =>
        i.name.toLowerCase().includes(q) ||
        i.category.toLowerCase().includes(q) ||
        i.item_id.toLowerCase().includes(q)
    );
    renderInventory(filtered);
}

async function deleteProduct(itemId) {
    if (!confirm(`Delete product ${itemId}?`)) return;
    try {
        const res = await fetch(`/api/sales?item_id=${itemId}`, { method: 'DELETE' });
        const data = await res.json();
        addLog(`🗑️ Deleted ${itemId} (${data.deleted} removed)`);
        loadInventory();
    } catch (e) {
        addLog(`<span style="color:#ef4444">Delete failed</span>`);
    }
}

// ====================== SEARCH ======================
let searchTimeout;
async function handleSearch(query) {
    clearTimeout(searchTimeout);
    const dropdown = document.getElementById('search-dropdown');
    if (!query || query.length < 2) {
        dropdown.classList.add('hidden');
        return;
    }

    searchTimeout = setTimeout(async () => {
        try {
            const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            const data = await res.json();
            if (data.results.length === 0) {
                dropdown.innerHTML = '<div class="search-item">No results found</div>';
            } else {
                dropdown.innerHTML = data.results.map(r => `
                    <div class="search-item">
                        <strong>${r.item_id}</strong> — ${r.name}
                        <div class="search-cat">${r.category} · $${r.price}</div>
                    </div>
                `).join('');
            }
            dropdown.classList.remove('hidden');
        } catch (e) {
            dropdown.classList.add('hidden');
        }
    }, 300);
}

// Close dropdown on click outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('.search-bar')) {
        document.getElementById('search-dropdown').classList.add('hidden');
    }
});

// ====================== EXPORT CSV ======================
function exportCSV() {
    addLog('📥 Exporting predictions to CSV...');
    window.open('/api/export', '_blank');
}

// ====================== ADD DATA FORM ======================
document.getElementById('sales-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
        item_id: document.getElementById('f_item_id').value,
        name: document.getElementById('f_name').value,
        category: document.getElementById('f_category').value,
        supplier: document.getElementById('f_supplier').value || 'Unknown',
        sales_qty: parseInt(document.getElementById('f_qty').value),
        price: parseFloat(document.getElementById('f_price').value),
        cost: parseFloat(document.getElementById('f_cost').value),
        shelf_location: document.getElementById('f_location').value || 'TBD',
    };

    addLog(`📤 Ingesting product: ${payload.item_id} — ${payload.name}`);

    try {
        const res = await fetch('/api/sales', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.status === 'success') {
            document.getElementById('form-msg').innerHTML =
                '<span style="color:#10b981"><i class="fa-solid fa-check-circle"></i> Successfully inserted to database!</span>';
            document.getElementById('sales-form').reset();
            addLog(`✅ Insert success (DB: ${data.db_type})`);
        }
    } catch (err) {
        document.getElementById('form-msg').innerHTML =
            '<span style="color:#ef4444"><i class="fa-solid fa-times-circle"></i> Insert failed.</span>';
        addLog(`<span style="color:#ef4444">Insert error: ${err.message}</span>`);
    }
});

// ====================== TRENDS (Canvas Chart) ======================
async function loadTrends() {
    addLog('Loading 30-day trend data...');
    try {
        const res = await fetch('/api/trends');
        const data = await res.json();
        if (data.status === 'success') {
            drawTrendChart(data.trends);
            addLog(`Trend data loaded: ${data.trends.dates.length} days`);
        }
    } catch (e) {
        addLog(`<span style="color:#ef4444">Failed to load trends</span>`);
    }
}

function drawTrendChart(trends) {
    const canvas = document.getElementById('trend-canvas');
    const ctx = canvas.getContext('2d');

    // Set canvas dimensions
    const container = canvas.parentElement;
    canvas.width = container.clientWidth - 48;
    canvas.height = 350;

    const W = canvas.width;
    const H = canvas.height;
    const padding = { top: 30, right: 30, bottom: 60, left: 60 };
    const chartW = W - padding.left - padding.right;
    const chartH = H - padding.top - padding.bottom;

    ctx.clearRect(0, 0, W, H);

    const dates = trends.dates;
    const totalSeries = trends.series['Total'] || [];
    if (dates.length === 0) return;

    const maxVal = Math.max(...totalSeries) * 1.1;
    const minVal = 0;

    // Colors for each category line
    const categoryColors = {
        'Beverage': '#6366f1',
        'Snacks': '#22d3ee',
        'Breakfast': '#f59e0b',
        'Dairy': '#10b981',
        'Bakery': '#ef4444',
        'Total': '#ffffff'
    };

    // Grid lines
    ctx.strokeStyle = '#1a1a3a';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 5; i++) {
        const y = padding.top + (chartH / 5) * i;
        ctx.beginPath();
        ctx.moveTo(padding.left, y);
        ctx.lineTo(W - padding.right, y);
        ctx.stroke();

        // Y-axis labels
        const val = maxVal - (maxVal / 5) * i;
        ctx.fillStyle = '#666';
        ctx.font = '11px Inter';
        ctx.textAlign = 'right';
        ctx.fillText('$' + Math.round(val), padding.left - 10, y + 4);
    }

    // X-axis labels (every 5th date)
    ctx.textAlign = 'center';
    dates.forEach((d, i) => {
        if (i % 5 === 0) {
            const x = padding.left + (chartW / (dates.length - 1)) * i;
            ctx.fillStyle = '#666';
            ctx.font = '10px Inter';
            ctx.fillText(d.slice(5), x, H - padding.bottom + 20);
        }
    });

    // Draw each category line
    const categories = Object.keys(trends.series).filter(k => k !== 'Total');

    function drawLine(seriesData, color, lineWidth, dashed) {
        ctx.beginPath();
        ctx.strokeStyle = color;
        ctx.lineWidth = lineWidth;
        if (dashed) ctx.setLineDash([6, 4]);
        else ctx.setLineDash([]);

        seriesData.forEach((val, i) => {
            const x = padding.left + (chartW / (dates.length - 1)) * i;
            const y = padding.top + chartH - ((val - minVal) / (maxVal - minVal)) * chartH;
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        });
        ctx.stroke();
        ctx.setLineDash([]);
    }

    // Draw category lines
    categories.forEach(cat => {
        if (trends.series[cat]) {
            drawLine(trends.series[cat], categoryColors[cat] || '#888', 1.5, false);
        }
    });

    // Draw total line (bold, slightly dashed)
    drawLine(totalSeries, '#ffffff', 2.5, true);

    // Add gradient under total line
    ctx.beginPath();
    totalSeries.forEach((val, i) => {
        const x = padding.left + (chartW / (dates.length - 1)) * i;
        const y = padding.top + chartH - ((val - minVal) / (maxVal - minVal)) * chartH;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.lineTo(padding.left + chartW, padding.top + chartH);
    ctx.lineTo(padding.left, padding.top + chartH);
    ctx.closePath();
    const grad = ctx.createLinearGradient(0, padding.top, 0, padding.top + chartH);
    grad.addColorStop(0, 'rgba(99, 102, 241, 0.15)');
    grad.addColorStop(1, 'rgba(99, 102, 241, 0)');
    ctx.fillStyle = grad;
    ctx.fill();

    // Legend
    let legendX = padding.left;
    const legendY = H - 15;
    const allKeys = [...categories, 'Total'];
    allKeys.forEach(key => {
        const color = categoryColors[key] || '#888';
        ctx.fillStyle = color;
        ctx.fillRect(legendX, legendY - 8, 12, 3);
        ctx.fillStyle = '#999';
        ctx.font = '10px Inter';
        ctx.textAlign = 'left';
        ctx.fillText(key, legendX + 16, legendY - 3);
        legendX += ctx.measureText(key).width + 34;
    });
}

// ====================== INIT ======================
window.addEventListener('load', () => {
    addLog('Frontend loaded. Bootstrapping...');
    checkStatus();
    // Auto-run pipeline after a short delay so the UI feels alive
    setTimeout(() => runPipeline(), 600);
});

// Re-draw trend chart on window resize
window.addEventListener('resize', () => {
    const trendView = document.getElementById('trends-view');
    if (!trendView.classList.contains('hidden')) {
        loadTrends();
    }
});
