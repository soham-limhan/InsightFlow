// Dashboard functionality and data rendering

let insightsData = null;
let visualizationsData = null;
let predictionsData = [];
let currentPage = 1;
let cleaningHistory = [];

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    initializeNavigation();
    loadInsights();
    loadVisualizations();
    loadPredictions();
    loadCleaningSuggestions();
    initializeDataExplorer();
});

// Navigation between sections
function initializeNavigation() {
    const menuItems = document.querySelectorAll('.menu-item');
    const sections = document.querySelectorAll('.content-section');

    menuItems.forEach(item => {
        item.addEventListener('click', () => {
            const sectionId = item.dataset.section;

            // Update active states
            menuItems.forEach(mi => mi.classList.remove('active'));
            item.classList.add('active');

            sections.forEach(section => {
                section.classList.remove('active');
                if (section.id === sectionId) {
                    section.classList.add('active');
                }
            });
        });
    });

    // Tab navigation
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;

            // Update active tab button
            btn.parentElement.querySelectorAll('.tab-btn').forEach(tb => tb.classList.remove('active'));
            btn.classList.add('active');

            // Show corresponding tab content
            const tabContents = document.querySelectorAll('.tab-content');
            tabContents.forEach(tc => tc.classList.remove('active'));
            document.getElementById(tabName + 'Tab').classList.add('active');
        });
    });
}

// Load insights
async function loadInsights() {
    try {
        const response = await fetch(`/api/insights/${SESSION_ID}`);
        const data = await response.json();

        if (data.error) {
            console.error(data.error);
            return;
        }

        insightsData = data;
        renderOverview(data);
        renderInsights(data);

        document.getElementById('loadingScreen').classList.add('hidden');
    } catch (error) {
        console.error('Error loading insights:', error);
    }
}

// Render overview section
function renderOverview(data) {
    const { basic_info, missing_values, data_quality_score } = data;

    document.getElementById('totalRows').textContent = basic_info.rows.toLocaleString();
    document.getElementById('totalColumns').textContent = basic_info.columns;
    document.getElementById('memoryUsage').textContent = basic_info.memory_usage_mb.toFixed(2) + ' MB';
    document.getElementById('qualityScore').textContent = data_quality_score + '%';

    // Column information table
    const columnInfo = data.column_info;
    let tableHTML = `
        <table>
            <thead>
                <tr>
                    <th>Column Name</th>
                    <th>Type</th>
                    <th>Non-Null</th>
                    <th>Null</th>
                    <th>Unique</th>
                </tr>
            </thead>
            <tbody>
    `;

    columnInfo.forEach(col => {
        tableHTML += `
            <tr>
                <td><strong>${col.name}</strong></td>
                <td>${col.dtype}</td>
                <td>${col.non_null.toLocaleString()}</td>
                <td>${col.null.toLocaleString()}</td>
                <td>${col.unique.toLocaleString()}</td>
            </tr>
        `;
    });

    tableHTML += '</tbody></table>';
    document.getElementById('columnInfo').innerHTML = tableHTML;

    // Data quality issues
    let issuesHTML = '';

    if (missing_values.total_missing > 0) {
        issuesHTML += `
            <div class="issue-item">
                <span class="issue-icon">⚠️</span>
                <div>
                    <strong>Missing Values:</strong> ${missing_values.total_missing.toLocaleString()} cells (${missing_values.columns_with_missing} columns affected)
                </div>
            </div>
        `;
    }

    if (basic_info.duplicates > 0) {
        issuesHTML += `
            <div class="issue-item">
                <span class="issue-icon">⚠️</span>
                <div>
                    <strong>Duplicate Rows:</strong> ${basic_info.duplicates.toLocaleString()} duplicates found
                </div>
            </div>
        `;
    }

    const outlierCount = Object.keys(data.outliers || {}).length;
    if (outlierCount > 0) {
        issuesHTML += `
            <div class="issue-item">
                <span class="issue-icon">⚠️</span>
                <div>
                    <strong>Outliers:</strong> Detected in ${outlierCount} columns
                </div>
            </div>
        `;
    }

    if (issuesHTML === '') {
        issuesHTML = '<p class="text-muted">No major data quality issues detected! ✨</p>';
    }

    document.getElementById('qualityIssues').innerHTML = issuesHTML;
}

// Render insights section
function renderInsights(data) {
    const { statistical_summary, correlations } = data;

    // Numerical summary
    if (statistical_summary.numerical) {
        let numHTML = '<div class="table-container"><table><thead><tr><th>Column</th><th>Mean</th><th>Median</th><th>Std Dev</th><th>Min</th><th>Max</th></tr></thead><tbody>';

        for (const [colName, stats] of Object.entries(statistical_summary.numerical)) {
            numHTML += `
                <tr>
                    <td><strong>${colName}</strong></td>
                    <td>${stats.mean?.toFixed(2) || 'N/A'}</td>
                    <td>${stats['50%']?.toFixed(2) || 'N/A'}</td>
                    <td>${stats.std?.toFixed(2) || 'N/A'}</td>
                    <td>${stats.min?.toFixed(2) || 'N/A'}</td>
                    <td>${stats.max?.toFixed(2) || 'N/A'}</td>
                </tr>
            `;
        }

        numHTML += '</tbody></table></div>';
        document.getElementById('numericalSummary').innerHTML = numHTML;
    } else {
        document.getElementById('numericalSummary').innerHTML = '<p class="text-muted">No numerical columns found</p>';
    }

    // Categorical summary
    if (statistical_summary.categorical) {
        let catHTML = '';

        for (const [colName, stats] of Object.entries(statistical_summary.categorical)) {
            catHTML += `
                <div class="card glass" style="margin-bottom: 1rem;">
                    <h4>${colName}</h4>
                    <p><strong>Unique Values:</strong> ${stats.unique_values}</p>
                    <p><strong>Most Common:</strong></p>
                    <ul>
            `;

            for (const [value, count] of Object.entries(stats.most_common)) {
                catHTML += `<li>${value}: ${count}</li>`;
            }

            catHTML += '</ul></div>';
        }

        document.getElementById('categoricalSummary').innerHTML = catHTML;
    } else {
        document.getElementById('categoricalSummary').innerHTML = '<p class="text-muted">No categorical columns found</p>';
    }

    // Correlations
    if (correlations && correlations.high_correlations.length > 0) {
        let corrHTML = '<div class="correlation-list">';

        correlations.high_correlations.forEach(corr => {
            const strength = Math.abs(corr.correlation);
            const color = corr.correlation > 0 ? 'var(--success)' : 'var(--error)';

            corrHTML += `
                <div class="correlation-item" style="border-left: 3px solid ${color}; padding-left: 1rem; margin-bottom: 1rem;">
                    <strong>${corr.var1}</strong> ↔️ <strong>${corr.var2}</strong>
                    <span style="color: ${color}; font-weight: bold;">${corr.correlation.toFixed(3)}</span>
                    <p class="text-muted">${strength > 0.9 ? 'Very strong' : 'Strong'} ${corr.correlation > 0 ? 'positive' : 'negative'} correlation</p>
                </div>
            `;
        });

        corrHTML += '</div>';
        document.getElementById('correlationInsights').innerHTML = corrHTML;
    } else {
        document.getElementById('correlationInsights').innerHTML = '<p class="text-muted">No strong correlations detected</p>';
    }
}

// Load visualizations
async function loadVisualizations() {
    try {
        const response = await fetch(`/api/visualizations/${SESSION_ID}`);
        const data = await response.json();

        if (data.error) {
            console.error(data.error);
            return;
        }

        visualizationsData = data;
        renderVisualizations(data);
    } catch (error) {
        console.error('Error loading visualizations:', error);
    }
}

// Render visualizations
function renderVisualizations(data) {
    // Distribution plots
    if (data.distribution_plots && data.distribution_plots.length > 0) {
        const container = document.getElementById('distributionCharts');
        container.innerHTML = '';

        data.distribution_plots.forEach(chart => {
            const chartDiv = document.createElement('div');
            chartDiv.className = 'chart-container';
            chartDiv.id = `dist-${chart.column}-${chart.type}`;
            container.appendChild(chartDiv);

            const plotData = JSON.parse(chart.data);
            const layout = {
                ...plotData.layout,
                autosize: true,
                margin: { l: 60, r: 60, t: 70, b: 70 },
                xaxis: { ...plotData.layout.xaxis, automargin: true },
                yaxis: { ...plotData.layout.yaxis, automargin: true }
            };
            Plotly.newPlot(chartDiv.id, plotData.data, layout, { responsive: true });
        });
    }

    // Correlation heatmap
    if (data.correlation_heatmap) {
        const chartDiv = document.createElement('div');
        chartDiv.className = 'chart-container';
        chartDiv.id = 'correlation-heatmap';
        document.getElementById('correlationChart').appendChild(chartDiv);

        const plotData = JSON.parse(data.correlation_heatmap);
        const layout = {
            ...plotData.layout,
            autosize: true,
            margin: { l: 60, r: 60, t: 70, b: 70 },
            xaxis: { ...plotData.layout.xaxis, automargin: true },
            yaxis: { ...plotData.layout.yaxis, automargin: true }
        };
        Plotly.newPlot('correlation-heatmap', plotData.data, layout, { responsive: true });
    }

    // Categorical charts
    if (data.categorical_charts && data.categorical_charts.length > 0) {
        const container = document.getElementById('categoricalCharts');
        container.innerHTML = '';

        data.categorical_charts.forEach(chart => {
            const chartDiv = document.createElement('div');
            chartDiv.className = 'chart-container';
            chartDiv.id = `cat-${chart.column}-${chart.type}`;
            container.appendChild(chartDiv);

            const plotData = JSON.parse(chart.data);
            const layout = {
                ...plotData.layout,
                autosize: true,
                margin: { l: 60, r: 60, t: 70, b: 70 },
                xaxis: { ...plotData.layout.xaxis, automargin: true },
                yaxis: { ...plotData.layout.yaxis, automargin: true }
            };
            Plotly.newPlot(chartDiv.id, plotData.data, layout, { responsive: true });
        });
    }

    // Time series plots
    if (data.time_series_plots && data.time_series_plots.length > 0) {
        const container = document.getElementById('timeseriesCharts');
        container.innerHTML = '';

        data.time_series_plots.forEach(chart => {
            const chartDiv = document.createElement('div');
            chartDiv.className = 'chart-container';
            chartDiv.id = `ts-${chart.datetime_column}-${chart.value_column}`;
            container.appendChild(chartDiv);

            const plotData = JSON.parse(chart.data);
            const layout = {
                ...plotData.layout,
                autosize: true,
                margin: { l: 60, r: 60, t: 70, b: 70 },
                xaxis: { ...plotData.layout.xaxis, automargin: true },
                yaxis: { ...plotData.layout.yaxis, automargin: true }
            };
            Plotly.newPlot(chartDiv.id, plotData.data, layout, { responsive: true });
        });
    }

    // Scatter matrix
    if (data.scatter_matrix) {
        const chartDiv = document.createElement('div');
        chartDiv.className = 'chart-container';
        chartDiv.id = 'scatter-matrix';
        document.getElementById('scatterMatrix').appendChild(chartDiv);

        const plotData = JSON.parse(data.scatter_matrix);
        const layout = {
            ...plotData.layout,
            autosize: true,
            margin: { l: 60, r: 60, t: 70, b: 70 },
            xaxis: { ...plotData.layout.xaxis, automargin: true },
            yaxis: { ...plotData.layout.yaxis, automargin: true }
        };
        Plotly.newPlot('scatter-matrix', plotData.data, layout, { responsive: true });
    }
}

// Load predictions
async function loadPredictions() {
    try {
        const response = await fetch(`/api/predictions/${SESSION_ID}`);
        const data = await response.json();

        if (data.error) {
            console.error(data.error);
            return;
        }

        renderPredictionRecommendations(data.recommendations);
    } catch (error) {
        console.error('Error loading predictions:', error);
    }
}

// Render prediction recommendations
function renderPredictionRecommendations(recommendations) {
    if (!recommendations || recommendations.length === 0) {
        document.getElementById('predictionRecommendations').innerHTML = '<p class="text-muted">No prediction recommendations available for this dataset</p>';
        return;
    }

    // Store recommendations for safe lookup by index
    predictionsData = recommendations;

    const typeIcons = {
        time_series_forecast: '📈',
        regression: '📉',
        classification: '🏷️',
        trend: '🔍'
    };

    let html = '<div class="prediction-cards">';

    recommendations.forEach((rec, index) => {
        const icon = typeIcons[rec.type] || '🔮';
        html += `
            <div class="card glass" style="margin-bottom: 1rem;">
                <h4>${icon} ${rec.type.replace(/_/g, ' ').toUpperCase()}</h4>
                <p>${rec.description}</p>
                <button class="btn-primary" onclick="runPrediction(${index})">
                    ▶ Run Prediction
                </button>
            </div>
        `;
    });

    html += '</div>';
    document.getElementById('predictionRecommendations').innerHTML = html;
}

// Run a prediction
async function runPrediction(index) {
    const recommendation = predictionsData[index];
    if (!recommendation) {
        alert('Prediction not found. Please reload the page.');
        return;
    }

    const payload = {
        session_id: SESSION_ID,
        type: recommendation.type,
        ...recommendation
    };

    // Show loading state
    const btn = document.querySelector(`#predictionRecommendations .prediction-cards .card:nth-child(${index + 1}) .btn-primary`);
    const originalText = btn ? btn.textContent : '';
    if (btn) { btn.textContent = '⏳ Running...'; btn.disabled = true; }

    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (btn) { btn.textContent = originalText; btn.disabled = false; }

        if (result.error) {
            alert('Prediction Error: ' + result.error);
            return;
        }

        displayPredictionResult(result, recommendation);
    } catch (error) {
        if (btn) { btn.textContent = originalText; btn.disabled = false; }
        console.error('Error running prediction:', error);
        alert('Failed to run prediction. Check the console for details.');
    }
}

// Display prediction result with rich charts and tables
function displayPredictionResult(result, recommendation) {
    const container = document.getElementById('predictionResults');
    const output = document.getElementById('predictionOutput');
    container.classList.remove('hidden');
    output.innerHTML = '';

    // Scroll to results
    container.scrollIntoView({ behavior: 'smooth', block: 'start' });

    const type = recommendation ? recommendation.type : 'unknown';

    if (type === 'time_series_forecast') {
        renderTimeSeriesResult(result, output);
    } else if (type === 'regression') {
        renderRegressionResult(result, output);
    } else if (type === 'classification') {
        renderClassificationResult(result, output);
    } else if (type === 'trend') {
        renderTrendResult(result, output);
    } else {
        // Fallback: styled JSON view
        output.innerHTML = `<pre style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; overflow: auto; font-size: 0.85rem;">${JSON.stringify(result, null, 2)}</pre>`;
    }
}

// Render time series forecast chart
function renderTimeSeriesResult(result, container) {
    const chartId = 'ts-forecast-chart';
    container.innerHTML = `
        <div style="margin-bottom: 1rem;">
            <p><strong>Trend:</strong> ${result.trend} &nbsp; <strong>R² Score:</strong> ${result.r2_score?.toFixed(4) ?? 'N/A'}</p>
        </div>
        <div id="${chartId}" style="width:100%; height:420px;"></div>
    `;

    const historical = result.historical || [];
    const forecast = result.forecast || [];

    const histTrace = {
        x: historical.map(p => p.date),
        y: historical.map(p => p.value),
        mode: 'lines+markers',
        name: 'Historical',
        line: { color: '#6366f1', width: 2 },
        marker: { size: 4 }
    };

    const forecastTrace = {
        x: forecast.map(p => p.date),
        y: forecast.map(p => p.value),
        mode: 'lines',
        name: 'Forecast',
        line: { color: '#f59e0b', width: 2, dash: 'dash' }
    };

    const layout = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: '#e2e8f0' },
        xaxis: { title: 'Date', gridcolor: 'rgba(255,255,255,0.1)' },
        yaxis: { title: 'Value', gridcolor: 'rgba(255,255,255,0.1)' },
        legend: { orientation: 'h', y: -0.2 },
        margin: { l: 60, r: 40, t: 30, b: 60 },
        shapes: [{
            type: 'line',
            x0: historical.length > 0 ? historical[historical.length - 1].date : 0,
            x1: historical.length > 0 ? historical[historical.length - 1].date : 0,
            y0: 0, y1: 1, yref: 'paper',
            line: { color: '#64748b', dash: 'dot', width: 1 }
        }]
    };

    Plotly.newPlot(chartId, [histTrace, forecastTrace], layout, { responsive: true });
}

// Render regression result: metrics table + feature importance chart
function renderRegressionResult(result, container) {
    const chartId = 'reg-importance-chart';
    const lr = result.linear_regression || {};
    const rf = result.random_forest || {};
    const best = result.best_model || 'N/A';

    let predTableHTML = '';
    if (result.sample_predictions && result.sample_predictions.length > 0) {
        predTableHTML = `
            <h4 style="margin-top:1.5rem;">Sample Predictions (${best})</h4>
            <div class="table-container">
            <table>
                <thead><tr><th>#</th><th>Actual</th><th>Predicted</th><th>Error</th></tr></thead>
                <tbody>
                ${result.sample_predictions.map((p, i) => `
                    <tr>
                        <td>${i + 1}</td>
                        <td>${p.actual.toFixed(2)}</td>
                        <td>${p.predicted.toFixed(2)}</td>
                        <td style="color:${Math.abs(p.actual - p.predicted) / (Math.abs(p.actual) || 1) < 0.1 ? 'var(--success)' : 'var(--warning)'}">
                            ${((p.predicted - p.actual) / (Math.abs(p.actual) || 1) * 100).toFixed(1)}%
                        </td>
                    </tr>
                `).join('')}
                </tbody>
            </table>
            </div>
        `;
    }

    container.innerHTML = `
        <h4>📊 Model Comparison — Target: <em>${result.target}</em></h4>
        <div class="table-container">
        <table>
            <thead><tr><th>Model</th><th>R² Score</th><th>RMSE</th><th>Winner?</th></tr></thead>
            <tbody>
                <tr>
                    <td>Linear Regression</td>
                    <td>${lr.r2_score?.toFixed(4) ?? 'N/A'}</td>
                    <td>${lr.rmse?.toFixed(2) ?? 'N/A'}</td>
                    <td>${best === 'Linear Regression' ? '🏆' : ''}</td>
                </tr>
                <tr>
                    <td>Random Forest</td>
                    <td>${rf.r2_score?.toFixed(4) ?? 'N/A'}</td>
                    <td>${rf.rmse?.toFixed(2) ?? 'N/A'}</td>
                    <td>${best === 'Random Forest' ? '🏆' : ''}</td>
                </tr>
            </tbody>
        </table>
        </div>
        <div id="${chartId}" style="width:100%; height:280px; margin-top:1rem;"></div>
        ${predTableHTML}
    `;

    // Feature importance chart
    const importance = rf.feature_importance || [];
    if (importance.length > 0) {
        Plotly.newPlot(chartId, [{
            type: 'bar', orientation: 'h',
            x: importance.map(f => f.importance),
            y: importance.map(f => f.feature),
            marker: { color: '#6366f1' },
            name: 'Feature Importance'
        }], {
            paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#e2e8f0' },
            title: { text: 'Feature Importance (Random Forest)', font: { color: '#e2e8f0' } },
            xaxis: { title: 'Importance', gridcolor: 'rgba(255,255,255,0.1)' },
            yaxis: { gridcolor: 'rgba(255,255,255,0.1)' },
            margin: { l: 140, r: 40, t: 50, b: 50 }
        }, { responsive: true });
    }
}

// Render classification result: metrics table + feature importance chart
function renderClassificationResult(result, container) {
    const chartId = 'cls-importance-chart';
    const lr = result.logistic_regression || {};
    const rf = result.random_forest || {};
    const best = result.best_model || 'N/A';
    const classes = (result.classes || []).join(', ');

    container.innerHTML = `
        <h4>🏷️ Classification — Target: <em>${result.target}</em></h4>
        <p><strong>Classes:</strong> ${classes}</p>
        <div class="table-container">
        <table>
            <thead><tr><th>Model</th><th>Accuracy</th><th>Winner?</th></tr></thead>
            <tbody>
                <tr>
                    <td>Logistic Regression</td>
                    <td>${lr.accuracy !== undefined ? (lr.accuracy * 100).toFixed(1) + '%' : 'N/A'}</td>
                    <td>${best === 'Logistic Regression' ? '🏆' : ''}</td>
                </tr>
                <tr>
                    <td>Random Forest</td>
                    <td>${rf.accuracy !== undefined ? (rf.accuracy * 100).toFixed(1) + '%' : 'N/A'}</td>
                    <td>${best === 'Random Forest' ? '🏆' : ''}</td>
                </tr>
            </tbody>
        </table>
        </div>
        <div id="${chartId}" style="width:100%; height:280px; margin-top:1rem;"></div>
    `;

    const importance = rf.feature_importance || [];
    if (importance.length > 0) {
        Plotly.newPlot(chartId, [{
            type: 'bar', orientation: 'h',
            x: importance.map(f => f.importance),
            y: importance.map(f => f.feature),
            marker: { color: '#10b981' },
            name: 'Feature Importance'
        }], {
            paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#e2e8f0' },
            title: { text: 'Feature Importance (Random Forest)', font: { color: '#e2e8f0' } },
            xaxis: { title: 'Importance', gridcolor: 'rgba(255,255,255,0.1)' },
            yaxis: { gridcolor: 'rgba(255,255,255,0.1)' },
            margin: { l: 160, r: 40, t: 50, b: 50 }
        }, { responsive: true });
    }
}

// Render trend analysis result as a styled metrics card
function renderTrendResult(result, container) {
    const directionEmoji = result.trend_direction === 'upward' ? '📈' : '📉';
    const changeColor = result.change_from_mean > 0 ? 'var(--success)' : 'var(--error)';
    container.innerHTML = `
        <h4>${directionEmoji} Trend Analysis — Column: <em>${result.column}</em></h4>
        <div class="stats-grid" style="margin-top: 1rem;">
            <div class="stat-card glass">
                <div class="stat-icon">${directionEmoji}</div>
                <div class="stat-content">
                    <div class="stat-value">${result.trend_direction?.toUpperCase()}</div>
                    <div class="stat-label">Trend Direction</div>
                </div>
            </div>
            <div class="stat-card glass">
                <div class="stat-icon">📐</div>
                <div class="stat-content">
                    <div class="stat-value">${result.trend_slope?.toFixed(4)}</div>
                    <div class="stat-label">Slope (per row)</div>
                </div>
            </div>
            <div class="stat-card glass">
                <div class="stat-icon">〰️</div>
                <div class="stat-content">
                    <div class="stat-value">${result.volatility?.toFixed(2)}</div>
                    <div class="stat-label">Volatility (Std Dev)</div>
                </div>
            </div>
            <div class="stat-card glass">
                <div class="stat-icon">🎯</div>
                <div class="stat-content">
                    <div class="stat-value" style="color:${changeColor}">${result.change_from_mean?.toFixed(2)}</div>
                    <div class="stat-label">Current vs Mean</div>
                </div>
            </div>
        </div>
        <div class="table-container" style="margin-top: 1.5rem;">
        <table>
            <thead><tr><th>Metric</th><th>Value</th></tr></thead>
            <tbody>
                <tr><td>Mean</td><td>${result.mean?.toFixed(4)}</td></tr>
                <tr><td>Median</td><td>${result.median?.toFixed(4)}</td></tr>
                <tr><td>Current Value</td><td>${result.current_value?.toFixed(4)}</td></tr>
            </tbody>
        </table>
        </div>
    `;
}

// Initialize data explorer
function initializeDataExplorer() {
    loadData();

    document.getElementById('searchInput').addEventListener('input', debounce(() => {
        currentPage = 1;
        loadData();
    }, 500));

    document.getElementById('sortColumn').addEventListener('change', () => {
        currentPage = 1;
        loadData();
    });

    document.getElementById('sortOrder').addEventListener('change', () => {
        currentPage = 1;
        loadData();
    });
}

// Load data table
async function loadData(page = 1) {
    const search = document.getElementById('searchInput').value;
    const sortBy = document.getElementById('sortColumn').value;
    const sortOrder = document.getElementById('sortOrder').value;

    try {
        const params = new URLSearchParams({
            page,
            per_page: 50,
            search,
            sort_by: sortBy,
            sort_order: sortOrder
        });

        const response = await fetch(`/api/data/${SESSION_ID}?${params}`);
        const data = await response.json();

        renderDataTable(data);
        renderPagination(data);

        // Populate sort column dropdown (first time)
        if (data.data.length > 0 && document.getElementById('sortColumn').options.length === 1) {
            const columns = Object.keys(data.data[0]);
            columns.forEach(col => {
                const option = document.createElement('option');
                option.value = col;
                option.textContent = col;
                document.getElementById('sortColumn').appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

// Render data table
function renderDataTable(data) {
    if (!data.data || data.data.length === 0) {
        document.getElementById('dataTable').innerHTML = '<p class="text-muted">No data found</p>';
        return;
    }

    const columns = Object.keys(data.data[0]);

    let html = '<table><thead><tr>';
    columns.forEach(col => {
        html += `<th>${col}</th>`;
    });
    html += '</tr></thead><tbody>';

    data.data.forEach(row => {
        html += '<tr>';
        columns.forEach(col => {
            const value = row[col] !== null && row[col] !== undefined ? row[col] : '-';
            html += `<td>${value}</td>`;
        });
        html += '</tr>';
    });

    html += '</tbody></table>';
    document.getElementById('dataTable').innerHTML = html;
}

// Render pagination
function renderPagination(data) {
    const { page, total_pages } = data;

    let html = '';

    if (page > 1) {
        html += `<button class="page-btn" onclick="loadData(${page - 1})">Previous</button>`;
    }

    for (let i = Math.max(1, page - 2); i <= Math.min(total_pages, page + 2); i++) {
        html += `<button class="page-btn ${i === page ? 'active' : ''}" onclick="loadData(${i})">${i}</button>`;
    }

    if (page < total_pages) {
        html += `<button class="page-btn" onclick="loadData(${page + 1})">Next</button>`;
    }

    document.getElementById('pagination').innerHTML = html;
    currentPage = page;
}

// Load cleaning suggestions
async function loadCleaningSuggestions() {
    try {
        const response = await fetch(`/api/cleaning/suggestions/${SESSION_ID}`);
        const data = await response.json();

        if (data.error) {
            console.error(data.error);
            return;
        }

        renderCleaningSuggestions(data.suggestions);
    } catch (error) {
        console.error('Error loading cleaning suggestions:', error);
    }
}

// Render cleaning suggestions
function renderCleaningSuggestions(suggestions) {
    if (!suggestions || suggestions.length === 0) {
        document.getElementById('cleaningSuggestions').innerHTML = '<p class="text-muted">No cleaning suggestions. Your data looks good! ✨</p>';
        return;
    }

    let html = '';

    suggestions.forEach((sug, index) => {
        const severityColors = {
            high: 'var(--error)',
            medium: 'var(--warning)',
            low: 'var(--success)'
        };

        html += `
            <div class="card glass" style="border-left: 3px solid ${severityColors[sug.severity]}; margin-bottom: 1rem;">
                <h4>${sug.type.replace(/_/g, ' ').toUpperCase()}</h4>
                <p>${sug.reason}</p>
                ${sug.column ? `<p><strong>Column:</strong> ${sug.column}</p>` : ''}
                <button class="btn-primary" onclick="applyCleaningAction(${index}, ${JSON.stringify(sug).replace(/"/g, '&quot;')})">
                    Apply Fix
                </button>
            </div>
        `;
    });

    document.getElementById('cleaningSuggestions').innerHTML = html;
}

// Apply cleaning action
async function applyCleaningAction(index, suggestion) {
    const payload = {
        session_id: SESSION_ID,
        ...suggestion
    };

    try {
        const response = await fetch('/api/cleaning/apply', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (result.success) {
            cleaningHistory.push(result.message);
            updateCleaningHistory();

            // Reload data
            loadInsights();
            loadData();
            loadCleaningSuggestions();

            alert('Cleaning action applied successfully!');
        } else {
            alert('Error: ' + result.message);
        }
    } catch (error) {
        console.error('Error applying cleaning:', error);
        alert('Failed to apply cleaning action');
    }
}

// Update cleaning history
function updateCleaningHistory() {
    if (cleaningHistory.length === 0) {
        return;
    }

    let html = '<ul>';
    cleaningHistory.forEach(action => {
        html += `<li>${action}</li>`;
    });
    html += '</ul>';

    document.getElementById('cleaningHistory').innerHTML = html;
}

// Export data
function exportData() {
    window.location.href = `/export/${SESSION_ID}`;
}

// Utility: Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
