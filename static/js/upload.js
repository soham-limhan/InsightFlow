// File upload handling with drag & drop

const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
const uploadProgress = document.getElementById('uploadProgress');
const progressFill = document.getElementById('progressFill');
const progressPercent = document.getElementById('progressPercent');
const fileName = document.getElementById('fileName');
const errorMessage = document.getElementById('errorMessage');

// Drag and drop handlers
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    uploadZone.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    uploadZone.addEventListener(eventName, () => {
        uploadZone.classList.add('drag-over');
    }, false);
});

['dragleave', 'drop'].forEach(eventName => {
    uploadZone.addEventListener(eventName, () => {
        uploadZone.classList.remove('drag-over');
    }, false);
});

uploadZone.addEventListener('drop', (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

function handleFile(file) {
    // Validate file type
    const allowedTypes = ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
    const allowedExtensions = ['.csv', '.xls', '.xlsx'];

    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();

    if (!allowedExtensions.includes(fileExtension)) {
        showError('Invalid file type. Please upload a CSV or Excel file.');
        return;
    }

    // Validate file size (100MB max)
    const maxSize = 100 * 1024 * 1024;
    if (file.size > maxSize) {
        showError('File is too large. Maximum size is 100MB.');
        return;
    }

    uploadFile(file);
}

function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    // Hide error message
    errorMessage.classList.add('hidden');

    // Show progress
    uploadZone.style.display = 'none';
    uploadProgress.classList.remove('hidden');
    fileName.textContent = file.name;

    const xhr = new XMLHttpRequest();

    // Upload progress
    xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
            const percent = Math.round((e.loaded / e.total) * 100);
            progressFill.style.width = percent + '%';
            progressPercent.textContent = percent + '%';
        }
    });

    // Upload complete
    xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
            const response = JSON.parse(xhr.responseText);
            if (response.success) {
                // Redirect to dashboard
                window.location.href = response.redirect;
            } else {
                showError(response.error || 'Upload failed');
                resetUpload();
            }
        } else {
            const response = JSON.parse(xhr.responseText);
            showError(response.error || 'Upload failed');
            resetUpload();
        }
    });

    // Upload error
    xhr.addEventListener('error', () => {
        showError('Network error occurred. Please try again.');
        resetUpload();
    });

    xhr.open('POST', '/upload');
    xhr.send(formData);
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
}

function resetUpload() {
    uploadZone.style.display = 'block';
    uploadProgress.classList.add('hidden');
    progressFill.style.width = '0%';
    progressPercent.textContent = '0%';
    fileInput.value = '';
}
