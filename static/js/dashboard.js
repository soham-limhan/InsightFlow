// Dashboard functionality and data rendering

let insightsData = null;
let visualizationsData = null;
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
                margin: { l: 50, r: 30, t: 50, b: 50 }
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
            margin: { l: 50, r: 30, t: 50, b: 50 }
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
                margin: { l: 50, r: 30, t: 50, b: 50 }
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
                margin: { l: 50, r: 30, t: 50, b: 50 }
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
            margin: { l: 50, r: 30, t: 50, b: 50 }
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
        document.getElementById('predictionRecommendations').innerHTML = '<p class="text-muted">No prediction recommendations available</p>';
        return;
    }

    let html = '<div class="prediction-cards">';

    recommendations.forEach((rec, index) => {
        html += `
            <div class="card glass" style="margin-bottom: 1rem;">
                <h4>${rec.type.replace(/_/g, ' ').toUpperCase()}</h4>
                <p>${rec.description}</p>
                <button class="btn-primary" onclick="runPrediction(${index}, ${JSON.stringify(rec).replace(/"/g, '&quot;')})">
                    Run Prediction
                </button>
            </div>
        `;
    });

    html += '</div>';
    document.getElementById('predictionRecommendations').innerHTML = html;
}

// Run a prediction
async function runPrediction(index, recommendation) {
    const payload = {
        session_id: SESSION_ID,
        type: recommendation.type,
        ...recommendation
    };

    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (result.error) {
            alert('Error: ' + result.error);
            return;
        }

        displayPredictionResult(result);
    } catch (error) {
        console.error('Error running prediction:', error);
        alert('Failed to run prediction');
    }
}

// Display prediction result
function displayPredictionResult(result) {
    document.getElementById('predictionResults').classList.remove('hidden');

    let html = '<pre>' + JSON.stringify(result, null, 2) + '</pre>';
    document.getElementById('predictionOutput').innerHTML = html;
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
