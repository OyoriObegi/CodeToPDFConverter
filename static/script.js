document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.querySelector('.drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileDetails = document.getElementById('file-details');
    const fileNameDisplay = document.getElementById('file-name');
    const removeBtn = document.getElementById('remove-file');
    const convertBtn = document.getElementById('convert-btn');
    const loadingOverlay = document.getElementById('loading-overlay');
    const errorMessage = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');

    const successOverlay = document.getElementById('success-overlay');
    const downloadLink = document.getElementById('download-link');
    const convertAnotherBtn = document.getElementById('convert-another-btn');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');

    let currentFile = null;
    let progressInterval = null;

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Highlight drop zone when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    // Handle dropped files
    dropZone.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    // Handle click to browse
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        if (files.length === 0) return;
        
        const file = files[0];
        const ext = file.name.split('.').pop().toLowerCase();
        
        if (ext !== 'py' && ext !== 'ipynb') {
            showError('Invalid file type. Please upload a .py or .ipynb file.');
            return;
        }

        currentFile = file;
        fileNameDisplay.textContent = file.name;
        
        // Hide upload section content, show file details
        dropZone.style.display = 'none';
        fileDetails.classList.remove('hidden');
        hideError();
    }

    // Remove file
    removeBtn.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent triggering dropZone click
        resetUpload();
    });

    function resetUpload() {
        currentFile = null;
        fileInput.value = '';
        dropZone.style.display = 'block';
        fileDetails.classList.add('hidden');
        successOverlay.classList.add('hidden');
        if (downloadLink.href) {
            window.URL.revokeObjectURL(downloadLink.href);
            downloadLink.href = '';
        }
        hideError();
    }

    convertAnotherBtn.addEventListener('click', resetUpload);

    // Simulated progress function
    function startProgress() {
        let progress = 0;
        progressBar.style.width = '0%';
        progressText.textContent = '0%';
        
        // Typical conversion takes 5-15 seconds. We'll simulate progress up to 95%
        progressInterval = setInterval(() => {
            if (progress < 90) {
                // Slower as it gets higher
                const increment = Math.random() * (90 - progress) * 0.1 + 1;
                progress += increment;
                progressBar.style.width = `${Math.min(95, progress)}%`;
                progressText.textContent = `${Math.floor(progress)}%`;
            }
        }, 300);
    }

    function finishProgress() {
        clearInterval(progressInterval);
        progressBar.style.width = '100%';
        progressText.textContent = '100%';
    }

    // Convert file
    convertBtn.addEventListener('click', async () => {
        if (!currentFile) return;

        const formData = new FormData();
        formData.append('file', currentFile);

        loadingOverlay.classList.remove('hidden');
        hideError();
        startProgress();

        try {
            const response = await fetch('/convert', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Conversion failed.');
            }

            finishProgress();

            // Wait a tiny bit for the 100% to render, then show success screen
            setTimeout(async () => {
                const blob = await response.blob();
                const downloadUrl = window.URL.createObjectURL(blob);
                
                const originalName = currentFile.name;
                const newName = originalName.substring(0, originalName.lastIndexOf('.')) + '.pdf';
                
                downloadLink.href = downloadUrl;
                downloadLink.download = newName;
                downloadLink.classList.remove('hidden');
                
                loadingOverlay.classList.add('hidden');
                successOverlay.classList.remove('hidden');
            }, 500);

        } catch (error) {
            clearInterval(progressInterval);
            loadingOverlay.classList.add('hidden');
            showError(error.message);
        }
    });

    function showError(message) {
        errorText.textContent = message;
        errorMessage.classList.remove('hidden');
        errorMessage.style.animation = 'none';
        errorMessage.offsetHeight; /* trigger reflow */
        errorMessage.style.animation = null;
    }

    function hideError() {
        errorMessage.classList.add('hidden');
    }
});
