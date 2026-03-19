document.addEventListener('DOMContentLoaded', function() {
    const sessionId = window.sessionId;
    const tableHead = document.getElementById('spreadsheetHead');
    const tableBody = document.getElementById('spreadsheetBody');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const statusIndicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');
    const statusDot = document.getElementById('statusDot');

    let currentData = null;
    let editingCell = null;

    // Load Data
    async function loadData() {
        try {
            const response = await fetch(`/api/spreadsheet/data/${sessionId}`);
            const data = await response.json();
            
            if (data.error) throw new Error(data.error);
            
            currentData = data;
            renderSpreadsheet(data);
            loadingOverlay.style.display = 'none';
        } catch (error) {
            console.error('Failed to load data:', error);
            statusText.textContent = 'Error loading data';
            statusDot.className = 'status-dot error';
            showStatus();
        }
    }

    function renderSpreadsheet(data) {
        // Render Header
        let headHtml = '<tr>';
        headHtml += '<th>#</th>'; // Index column
        data.columns.forEach(col => {
            headHtml += `<th>${col}</th>`;
        });
        headHtml += '</tr>';
        tableHead.innerHTML = headHtml;

        // Render Body
        let bodyHtml = '';
        data.data.forEach((row, idx) => {
            bodyHtml += `<tr>`;
            bodyHtml += `<td class="row-index">${idx + 1}</td>`;
            data.columns.forEach(col => {
                const val = row[col] === null ? '' : row[col];
                bodyHtml += `<td contenteditable="true" data-row="${row.index}" data-column="${col}">${val}</td>`;
            });
            bodyHtml += `</tr>`;
        });
        tableBody.innerHTML = bodyHtml;

        setupEditableCells();
    }

    function setupEditableCells() {
        const cells = tableBody.querySelectorAll('td[contenteditable="true"]');
        
        cells.forEach(cell => {
            cell.addEventListener('focus', function() {
                editingCell = {
                    value: this.innerText,
                    row: this.dataset.row,
                    column: this.dataset.column
                };
            });

            cell.addEventListener('blur', function() {
                if (this.innerText !== editingCell.value) {
                    saveCell(this.dataset.row, this.dataset.column, this.innerText);
                }
            });

            cell.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.blur();
                }
                if (e.key === 'Escape') {
                    this.innerText = editingCell.value;
                    this.blur();
                }
            });
        });
    }

    async function saveCell(rowIdx, column, value) {
        statusText.textContent = 'Saving...';
        statusDot.className = 'status-dot saving';
        showStatus();

        try {
            const response = await fetch('/api/spreadsheet/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    row_idx: rowIdx,
                    column: column,
                    value: value
                })
            });

            const result = await response.json();
            
            if (result.success) {
                statusText.textContent = 'Changes saved';
                statusDot.className = 'status-dot success';
                setTimeout(hideStatus, 2000);
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Save failed:', error);
            statusText.textContent = 'Save failed';
            statusDot.className = 'status-dot error';
        }
    }

    function showStatus() {
        statusIndicator.classList.add('visible');
    }

    function hideStatus() {
        statusIndicator.classList.remove('visible');
    }

    // Save button — persist all changes to the original file on disk
    document.getElementById('saveBtn').addEventListener('click', async function() {
        const btn = this;
        btn.disabled = true;
        btn.classList.add('saving');
        statusText.textContent = 'Saving to file...';
        statusDot.className = 'status-dot saving';
        showStatus();

        try {
            const response = await fetch(`/api/spreadsheet/save/${sessionId}`, {
                method: 'POST'
            });
            const result = await response.json();

            if (result.success) {
                statusText.textContent = 'File saved successfully!';
                statusDot.className = 'status-dot success';
                setTimeout(hideStatus, 3000);
            } else {
                throw new Error(result.message || 'Save failed');
            }
        } catch (error) {
            console.error('Save failed:', error);
            statusText.textContent = 'Save failed: ' + error.message;
            statusDot.className = 'status-dot error';
        } finally {
            btn.disabled = false;
            btn.classList.remove('saving');
        }
    });

    // Download button — download the current data as a file
    document.getElementById('downloadBtn').addEventListener('click', function() {
        window.location.href = `/api/spreadsheet/download/${sessionId}`;
    });

    loadData();
});
