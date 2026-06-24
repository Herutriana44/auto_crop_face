const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const selectedFile = document.getElementById('selected-file');
const fileName = document.getElementById('file-name');
const fileType = document.getElementById('file-type');
const btnClear = document.getElementById('btn-clear');
const btnUpload = document.getElementById('btn-upload');
const uploadSection = document.getElementById('upload-section');
const progressSection = document.getElementById('progress-section');
const resultsSection = document.getElementById('results-section');
const errorSection = document.getElementById('error-section');
const progressFill = document.getElementById('progress-fill');
const progressText = document.getElementById('progress-text');
const resultsGrid = document.getElementById('results-grid');
const facesCount = document.getElementById('faces-count');
const btnDownloadAll = document.getElementById('btn-download-all');
const btnNew = document.getElementById('btn-new');
const btnRetry = document.getElementById('btn-retry');
const errorMessage = document.getElementById('error-message');

let currentFile = null;
let zipUrl = null;

dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

btnClear.addEventListener('click', clearFile);
btnUpload.addEventListener('click', uploadFile);
btnNew.addEventListener('click', reset);
btnRetry.addEventListener('click', reset);
btnDownloadAll.addEventListener('click', downloadAll);

function handleFileSelect(file) {
    const validImageTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    const validVideoTypes = ['video/mp4', 'video/avi', 'video/x-msvideo', 'video/quicktime', 'video/x-matroska', 'video/webm'];

    if (!validImageTypes.includes(file.type) && !validVideoTypes.includes(file.type)) {
        alert('Format file tidak didukung. Gunakan JPG, PNG, WebP, MP4, AVI, MOV, MKV, atau WebM.');
        return;
    }

    const maxSize = validImageTypes.includes(file.type) ? 50 * 1024 * 1024 : 200 * 1024 * 1024;
    if (file.size > maxSize) {
        alert(`File terlalu besar. Max ${validImageTypes.includes(file.type) ? '50MB' : '200MB'}.`);
        return;
    }

    currentFile = file;
    fileName.textContent = file.name;

    const type = validImageTypes.includes(file.type) ? 'Gambar' : 'Video';
    const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
    fileType.textContent = `${type} • ${sizeMB} MB`;

    selectedFile.style.display = 'flex';
    btnUpload.disabled = false;
}

function clearFile() {
    currentFile = null;
    fileInput.value = '';
    selectedFile.style.display = 'none';
    btnUpload.disabled = true;
}

async function uploadFile() {
    if (!currentFile) return;

    const formData = new FormData();
    formData.append('file', currentFile);

    uploadSection.style.display = 'none';
    progressSection.style.display = 'block';
    progressFill.style.width = '30%';
    progressText.textContent = 'Mengupload file...';

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        progressFill.style.width = '60%';
        progressText.textContent = 'Memproses wajah...';

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Terjadi kesalahan');
        }

        progressFill.style.width = '100%';
        progressText.textContent = 'Selesai!';

        setTimeout(() => {
            showResults(data);
        }, 500);

    } catch (error) {
        showError(error.message);
    }
}

function showResults(data) {
    progressSection.style.display = 'none';
    resultsSection.style.display = 'block';

    facesCount.textContent = data.faces_found;
    zipUrl = data.zip_url;

    resultsGrid.innerHTML = '';

    if (data.faces_found === 0) {
        resultsGrid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: #718096; padding: 40px;">Tidak ada wajah terdeteksi dalam file.</p>';
        btnDownloadAll.style.display = 'none';
        return;
    }

    btnDownloadAll.style.display = 'block';

    data.preview_urls.forEach((url, index) => {
        const result = data.results[index];
        const item = document.createElement('div');
        item.className = 'result-item';
        item.innerHTML = `
            <img src="${url}" alt="Face ${index + 1}" loading="lazy">
            <div class="result-info">
                Face ${index + 1} • Score: ${result.score}
            </div>
        `;
        resultsGrid.appendChild(item);
    });

    if (data.faces_found > data.preview_urls.length) {
        const moreInfo = document.createElement('p');
        moreInfo.style.gridColumn = '1/-1';
        moreInfo.style.textAlign = 'center';
        moreInfo.style.color = '#718096';
        moreInfo.style.padding = '20px';
        moreInfo.textContent = `+ ${data.faces_found - data.preview_urls.length} wajah lainnya (download ZIP untuk melihat semua)`;
        resultsGrid.appendChild(moreInfo);
    }
}

function showError(message) {
    progressSection.style.display = 'none';
    errorSection.style.display = 'block';
    errorMessage.textContent = message;
}

function downloadAll() {
    if (zipUrl) {
        window.location.href = zipUrl;
    }
}

function reset() {
    uploadSection.style.display = 'block';
    progressSection.style.display = 'none';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
    clearFile();
    zipUrl = null;
}
