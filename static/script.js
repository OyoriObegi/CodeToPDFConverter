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

    let currentFile = null;

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
        hideError();
    }

    // Convert file
    convertBtn.addEventListener('click', async () => {
        if (!currentFile) return;

        const formData = new FormData();
        formData.append('file', currentFile);

        loadingOverlay.classList.remove('hidden');
        hideError();

        try {
            const response = await fetch('/convert', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Conversion failed.');
            }

            // Handle the file download
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            
            // Set suggested filename based on original
            const originalName = currentFile.name;
            const newName = originalName.substring(0, originalName.lastIndexOf('.')) + '.pdf';
            
            a.style.display = 'none';
            a.href = downloadUrl;
            a.download = newName;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(downloadUrl);
            document.body.removeChild(a);
            
            // Optional: reset after successful download
            // resetUpload();

        } catch (error) {
            showError(error.message);
        } finally {
            loadingOverlay.classList.add('hidden');
        }
    });

    function showError(message) {
        errorText.textContent = message;
        errorMessage.classList.remove('hidden');
        // Shake effect gets re-triggered by removing and re-adding class
        errorMessage.style.animation = 'none';
        errorMessage.offsetHeight; /* trigger reflow */
        errorMessage.style.animation = null;
    }

    function hideError() {
        errorMessage.classList.add('hidden');
    }
});
