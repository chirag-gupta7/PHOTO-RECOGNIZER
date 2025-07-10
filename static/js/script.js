document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    const submitBtn = document.getElementById('submit-btn');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
    const resultsContainer = document.getElementById('results-container');
    const resultsContent = document.getElementById('results-content');
    const errorContainer = document.getElementById('error-container');
    const errorMessage = document.getElementById('error-message');
    const themeToggle = document.getElementById('theme-toggle');
    const metadataContainer = document.getElementById('metadata-container');
    const metadataDropdown = document.getElementById('metadata-dropdown');
    const currentDateEl = document.getElementById('current-date');

    // Set current date
    if (currentDateEl) {
        currentDateEl.textContent = new Date().toISOString().split('T')[0];
    }
    
    // Theme toggle functionality
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    const currentTheme = localStorage.getItem('theme');
    
    if (currentTheme === 'dark' || (!currentTheme && prefersDarkScheme.matches)) {
        document.body.classList.add('dark-mode');
        themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    }
    
    themeToggle.addEventListener('click', function() {
        document.body.classList.toggle('dark-mode');
        
        if (document.body.classList.contains('dark-mode')) {
            localStorage.setItem('theme', 'dark');
            themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        } else {
            localStorage.setItem('theme', 'light');
            themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        }
    });

    // File upload functionality
    uploadArea.addEventListener('click', function() {
        fileInput.click();
    });

    // Drag and drop functionality
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight() {
        uploadArea.classList.add('dragover');
    }
    
    function unhighlight() {
        uploadArea.classList.remove('dragover');
    }
    
    uploadArea.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length) {
            handleFiles(files);
        }
    }
    
    fileInput.addEventListener('change', function() {
        if (fileInput.files.length) {
            handleFiles(fileInput.files);
        }
    });
    
    function handleFiles(files) {
        const file = files[0];
        
        // Check if file is an image
        if (!file.type.match('image.*')) {
            showError('Please select an image file');
            resetUI();
            return;
        }
        
        // Check file size (max 16MB)
        if (file.size > 16 * 1024 * 1024) {
            showError('File too large. Maximum size is 16MB.');
            resetUI();
            return;
        }
        
        // Add file selected state
        uploadArea.classList.add('file-selected');
        
        // Display file info
        fileName.textContent = file.name;
        fileInfo.style.display = 'flex';
        
        // Enable submit button
        submitBtn.disabled = false;
        
        // Show image preview
        previewFile(file);
        
        // Hide any previous errors
        hideError();
        
        // Hide any previous results
        resultsContainer.style.display = 'none';
        if (metadataDropdown) {
            metadataDropdown.classList.remove('open');
            metadataDropdown.classList.add('closed');
            metadataDropdown.style.display = 'none';
        }
    }
    
    function previewFile(file) {
        const reader = new FileReader();
        
        reader.onload = function() {
            imagePreview.src = reader.result;
            previewContainer.style.display = 'block';
            previewContainer.classList.add('animate__fadeIn');
        }
        
        if (file) {
            reader.readAsDataURL(file);
        }
    }
    
    function resetUI() {
        fileInput.value = '';
        fileInfo.style.display = 'none';
        submitBtn.disabled = true;
        previewContainer.style.display = 'none';
        resultsContainer.style.display = 'none';
        if (metadataDropdown) {
            metadataDropdown.classList.remove('open');
            metadataDropdown.classList.add('closed');
            metadataDropdown.style.display = 'none';
        }
        uploadArea.classList.remove('file-selected');
    }
    
    function showError(message) {
        errorMessage.textContent = message;
        errorContainer.style.display = 'block';
        
        // Scroll to error message
        errorContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    function hideError() {
        errorContainer.style.display = 'none';
    }
    
    // Submit image for analysis
    submitBtn.addEventListener('click', submitImage);
    
    function submitImage() {
        if (!fileInput.files.length) {
            showError('Please select an image first');
            return;
        }
        
        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file1', file);
        
        // Change button state to loading
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="loader"></span>Analyzing...';
        
        // Hide any previous errors
        hideError();
        
        // Hide previous results
        resultsContainer.style.display = 'none';
        if (metadataDropdown) {
            metadataDropdown.style.display = 'none';
        }
        
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok && response.status !== 200) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Reset button state
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-search"></i>Analyze Image';
            
            // Check if our backend sent a structured error
            if (data.error) {
                // Show error but still display metadata if available
                showError(data.error);
                
                // If we have metadata despite the error, still show it
                if (data.metadata) {
                    displayPartialResults(data);
                }
                
                return;
            }
            
            // Display results
            displayResults(data);
        })
        .catch(error => {
            console.error('Error:', error);
            
            // Reset button state
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-search"></i>Analyze Image';
            
            // Show detailed error message
            let errorMsg = 'An error occurred while processing your request.';
            if (error.message) {
                errorMsg += ' ' + error.message;
            }
            errorMsg += ' Please check your API key and try again.';
            
            showError(errorMsg);
        });
    }
    
    // New function to display partial results when we have metadata but API failed
    function displayPartialResults(data) {
        // Check if we have metadata
        if (!data.metadata) return;
        
        // Start building results HTML
        let resultsHTML = `
            <div class="error-banner">
                <i class="fas fa-exclamation-circle"></i>
                <p>API classification failed, but we've analyzed the image metadata.</p>
            </div>
        `;
        
        // Add metadata toggle button
        if (Object.keys(data.metadata).length > 0) {
            resultsHTML += `
                <div class="btn-container">
                    <button class="metadata-toggle" id="metadata-toggle">
                        <i class="fas fa-info-circle"></i> Show Image Information
                    </button>
                </div>`;
        }
        
        resultsContent.innerHTML = resultsHTML;
        resultsContainer.style.display = 'block';
        resultsContainer.classList.add('animate__fadeInUp');
        
        // Display metadata in the tabbed layout
        if (data.metadata && Object.keys(data.metadata).length > 0) {
            displayMetadata(data.metadata);
            setupMetadataTabs();
        }
        
        // Set up metadata toggle button
        const metadataToggle = document.getElementById('metadata-toggle');
        if (metadataToggle && metadataDropdown) {
            metadataToggle.addEventListener('click', function() {
                const isOpen = metadataDropdown.classList.contains('open');
                
                if (isOpen) {
                    // Close dropdown
                    metadataDropdown.classList.remove('open');
                    metadataDropdown.classList.add('closed');
                    metadataToggle.classList.remove('open');
                    metadataToggle.innerHTML = '<i class="fas fa-chevron-down"></i> Show Image Information';
                } else {
                    // Open dropdown
                    metadataDropdown.style.display = 'block';
                    metadataDropdown.classList.remove('closed');
                    metadataDropdown.classList.add('open');
                    metadataToggle.classList.add('open');
                    metadataToggle.innerHTML = '<i class="fas fa-chevron-up"></i> Hide Image Information';
                    
                    // Smooth scroll to dropdown after animation starts
                    setTimeout(() => {
                        metadataDropdown.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }, 200);
                }
            });
        }
        
        // Scroll to results
        setTimeout(() => {
            resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 200);
    }
    
    function displayResults(data) {
        let predictions;
        let metadata;
        let insights = [];
        
        // Extract predictions and metadata based on response structure
        if (data.predictions) {
            predictions = data.predictions;
            metadata = data.metadata || {};
            insights = data.insights || [];
        } else if (Array.isArray(data)) {
            predictions = data;
            metadata = {};
        } else {
            showError('Invalid response format from server');
            return;
        }
        
        // Check if we have valid predictions
        if (!Array.isArray(predictions) || predictions.length === 0) {
            resultsContent.innerHTML = '<p class="no-results">Could not identify any specific objects. The model may not be suitable for this image type.</p>';
            
            // Still show metadata if available
            if (metadata && Object.keys(metadata).length > 0) {
                resultsContent.innerHTML += `
                    <div class="btn-container">
                        <button class="metadata-toggle" id="metadata-toggle">
                            <i class="fas fa-info-circle"></i> Show Image Information
                        </button>
                    </div>`;
            }
            
            resultsContainer.style.display = 'block';
            
            // Display metadata if available
            if (metadata && Object.keys(metadata).length > 0) {
                displayMetadata(metadata);
                setupMetadataTabs();
                
                // Set up metadata toggle
                const metadataToggle = document.getElementById('metadata-toggle');
                if (metadataToggle && metadataDropdown) {
                    metadataToggle.addEventListener('click', function() {
                        const isOpen = metadataDropdown.classList.contains('open');
                        
                        if (isOpen) {
                            // Close dropdown
                            metadataDropdown.classList.remove('open');
                            metadataDropdown.classList.add('closed');
                            metadataToggle.classList.remove('open');
                            metadataToggle.innerHTML = '<i class="fas fa-chevron-down"></i> Show Image Information';
                        } else {
                            // Open dropdown
                            metadataDropdown.style.display = 'block';
                            metadataDropdown.classList.remove('closed');
                            metadataDropdown.classList.add('open');
                            metadataToggle.classList.add('open');
                            metadataToggle.innerHTML = '<i class="fas fa-chevron-up"></i> Hide Image Information';
                        }
                    });
                }
            }
            
            return;
        }
        
        // Start building results HTML
        let resultsHTML = '';
        
        // Add insights section if available
        if (insights && insights.length > 0) {
            resultsHTML += `
                <div class="insights-section">
                    <h3><i class="fas fa-lightbulb"></i> Image Insights</h3>
                    <div class="insights-content">
                        ${insights.map(insight => `<p>${insight}</p>`).join('')}
                    </div>
                </div>
            `;
        }
        
        // Display prediction results
        resultsHTML += '<h3 class="results-subtitle">Classification Results</h3>';
        resultsHTML += '<ul class="result-list">';
        
        // Check if we have object detection results (with boxes)
        const hasObjectDetection = predictions.some(item => item.box);
        
        if (hasObjectDetection) {
            // For object detection, show results and visualize boxes
            predictions.forEach((item, index) => {
                const label = item.label || 'Unknown';
                const score = item.score || 0;
                const percentage = (score * 100).toFixed(2);
                
                resultsHTML += `
                    <li class="result-item">
                        <div class="result-info">
                            <span class="category-badge">${label}</span>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: 0%" data-score="${percentage}"></div>
                            </div>
                        </div>
                        <div class="result-score">${percentage}%</div>
                    </li>
                `;
            });
        } else {
            // Regular classification results
            predictions.forEach((item, index) => {
                const label = item.label || 'Unknown';
                const score = item.score || 0;
                const percentage = (score * 100).toFixed(2);
                
                resultsHTML += `
                    <li class="result-item">
                        <div class="result-info">
                            <span class="category-badge">${label}</span>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: 0%" data-score="${percentage}"></div>
                            </div>
                        </div>
                        <div class="result-score">${percentage}%</div>
                    </li>
                `;
            });
        }
        
        resultsHTML += `</ul>`;
        
        // Add metadata toggle button
        if (metadata && Object.keys(metadata).length > 0) {
            resultsHTML += `
                <div class="btn-container">
                    <button class="metadata-toggle" id="metadata-toggle">
                        <i class="fas fa-info-circle"></i> Show Detailed Information
                    </button>
                </div>`;
        }
        
        resultsContent.innerHTML = resultsHTML;
        resultsContainer.style.display = 'block';
        resultsContainer.classList.add('animate__fadeInUp');
        
        // Display metadata in the tabbed layout
        if (metadata && Object.keys(metadata).length > 0) {
            displayMetadata(metadata);
            setupMetadataTabs();
        }
        
        // Set up metadata toggle button
        const metadataToggle = document.getElementById('metadata-toggle');
        if (metadataToggle && metadataDropdown) {
            metadataToggle.addEventListener('click', function() {
                const isOpen = metadataDropdown.classList.contains('open');
                
                if (isOpen) {
                    // Close dropdown
                    metadataDropdown.classList.remove('open');
                    metadataDropdown.classList.add('closed');
                    metadataToggle.classList.remove('open');
                    metadataToggle.innerHTML = '<i class="fas fa-chevron-down"></i> Show Detailed Information';
                } else {
                    // Open dropdown
                    metadataDropdown.style.display = 'block';
                    metadataDropdown.classList.remove('closed');
                    metadataDropdown.classList.add('open');
                    metadataToggle.classList.add('open');
                    metadataToggle.innerHTML = '<i class="fas fa-chevron-up"></i> Hide Detailed Information';
                    
                    // Smooth scroll to dropdown after animation starts
                    setTimeout(() => {
                        metadataDropdown.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }, 200);
                }
            });
        }
        
        // Animate progress bars
        setTimeout(() => {
            const progressBars = document.querySelectorAll('.progress-fill');
            progressBars.forEach(bar => {
                const score = bar.dataset.score || 0;
                bar.style.width = `${score}%`;
            });
        }, 300);
        
        // Scroll to results
        setTimeout(() => {
            resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 200);
    }
    
    function setupMetadataTabs() {
        const tabs = document.querySelector('.metadata-tabs');
        const tabContents = document.querySelectorAll('.tab-content');
        const tabLinks = document.querySelectorAll('.tab-link');

        if (tabs) {
            tabs.addEventListener('click', (e) => {
                const clicked = e.target.closest('.tab-link');
                if (!clicked) return;

                e.preventDefault();

                tabLinks.forEach(link => link.classList.remove('active'));
                clicked.classList.add('active');

                const tabId = clicked.dataset.tab;
                tabContents.forEach(content => {
                    content.classList.remove('active');
                    if (content.id === `tab-${tabId}`) {
                        content.classList.add('active');
                    }
                });
            });
        }
    }
    
    function displayMetadata(metadata) {
        // Get metadata container elements
        const basicMetadata = document.getElementById('basic-metadata');
        const cameraMetadata = document.getElementById('camera-metadata');
        const technicalMetadata = document.getElementById('technical-metadata');
        const colorAnalysisContent = document.getElementById('color-analysis-content');
        const exifMetadata = document.getElementById('exif-metadata');
        
        // Show the metadata dropdown container
        if (metadataDropdown) {
            metadataDropdown.style.display = 'block';
        }
        
        // Reset content
        if (basicMetadata) basicMetadata.innerHTML = '';
        if (cameraMetadata) cameraMetadata.innerHTML = '';
        if (technicalMetadata) technicalMetadata.innerHTML = '';
        if (colorAnalysisContent) colorAnalysisContent.innerHTML = '';
        if (exifMetadata) exifMetadata.innerHTML = '';
        
        // Helper to create metadata items
        const createMetadataItem = (label, value, title = '') => {
            if (value === undefined || value === null || value === '') return '';
            return `
                <div class="metadata-item">
                    <div class="metadata-label">${label}</div>
                    <div class="metadata-value" title="${title || value}">${value}</div>
                </div>
            `;
        };

        // Basic Information
        if (basicMetadata) {
            let basicHTML = '';
            basicHTML += createMetadataItem('File Name', metadata.filename);
            basicHTML += createMetadataItem('File Size', metadata.file_size);
            basicHTML += createMetadataItem('Dimensions', `${metadata.width} x ${metadata.height}px`);
            basicHTML += createMetadataItem('Aspect Ratio', metadata.aspect_ratio);
            basicHTML += createMetadataItem('Image Hash (MD5)', metadata.hash, metadata.hash);
            basicMetadata.innerHTML = basicHTML || '<p>No basic information available.</p>';
        }

        // Camera Information
        if (cameraMetadata) {
            let cameraHTML = '';
            cameraHTML += createMetadataItem('Camera', metadata.camera);
            cameraHTML += createMetadataItem('Lens', metadata.lens);
            cameraHTML += createMetadataItem('Exposure', metadata.exposure_formatted);
            cameraHTML += createMetadataItem('Aperture', metadata.aperture);
            cameraHTML += createMetadataItem('ISO', metadata.iso);
            cameraHTML += createMetadataItem('Focal Length', metadata.focal_length);
            cameraHTML += createMetadataItem('Date Taken', metadata.date_taken_formatted);
            if (metadata.has_location) {
                cameraHTML += createMetadataItem('Location', 'GPS data present');
            }
            cameraMetadata.innerHTML = cameraHTML || '<p>No camera information available in EXIF data.</p>';
        }

        // Technical Information
        if (technicalMetadata) {
            let technicalHTML = '';
            technicalHTML += createMetadataItem('Format', metadata.format);
            technicalHTML += createMetadataItem('Color Mode', metadata.mode);
            technicalHTML += createMetadataItem('Total Processing Time', metadata.total_processing_time);
            if (metadata.request_time) {
                technicalHTML += createMetadataItem('API Request Time', `${metadata.request_time.toFixed(2)} seconds`);
            }
            technicalMetadata.innerHTML = technicalHTML || '<p>No technical details available.</p>';
        }

        // Color Analysis
        if (colorAnalysisContent) {
            let colorHTML = '';
            
            if (metadata.avg_color_hex) {
                colorHTML += `
                    <div class="metadata-item">
                        <div class="metadata-label">Average Color</div>
                        <div style="display: flex; align-items: center;">
                            <div class="color-swatch" style="background-color: ${metadata.avg_color_hex}"></div>
                            <div class="metadata-value">
                                <span>${metadata.avg_color_hex}</span><br>
                                <span>${metadata.avg_color}</span>
                            </div>
                        </div>
                    </div>
                `;
            }
            
            if (metadata.dominant_colors && metadata.dominant_colors.length > 0) {
                colorHTML += `
                    <div class="metadata-item">
                        <div class="metadata-label">Dominant Colors</div>
                        <div class="color-palette">
                            ${metadata.dominant_colors.map(c => `<div class="color-chip" style="background-color: ${c.hex};" title="${c.hex}"></div>`).join('')}
                        </div>
                    </div>
                `;
            }
            
            if (metadata.brightness_category) {
                colorHTML += createMetadataItem('Brightness', `${metadata.brightness}% (${metadata.brightness_category})`);
            }
            
            if (metadata.contrast) {
                colorHTML += createMetadataItem('Contrast', `${metadata.contrast.toFixed(0)}%`);
            }
            
            colorAnalysisContent.innerHTML = colorHTML || '<p>No color analysis available.</p>';
        }

        // EXIF Data
        if (exifMetadata && metadata.exif && Object.keys(metadata.exif).length > 0) {
            let exifHTML = '';
            const sortedKeys = Object.keys(metadata.exif).sort();
            
            for (const key of sortedKeys) {
                const value = metadata.exif[key];
                exifHTML += `
                    <div class="metadata-item">
                        <div class="metadata-label">${key}</div>
                        <div class="metadata-value">${value}</div>
                    </div>
                `;
            }
            exifMetadata.innerHTML = exifHTML;
        } else if (exifMetadata) {
            exifMetadata.innerHTML = '<p>No EXIF data available for this image.</p>';
        }
    }
    
    // Easter egg - clicking the logo plays a fun animation
    document.querySelector('.logo').addEventListener('click', function() {
        this.classList.add('animate__animated', 'animate__flip');
        setTimeout(() => {
            this.classList.remove('animate__animated', 'animate__flip');
        }, 1000);
    });
    
    // --- On Load Animations ---
    // Show upload animation on page load
    setTimeout(() => {
        uploadArea.classList.add('animate__animated', 'animate__fadeInUp');
    }, 300);
    
    // Add special CSS for error banner
    const style = document.createElement('style');
    style.textContent = `
        .error-banner {
            display: flex;
            align-items: center;
            background-color: rgba(234, 67, 53, 0.1);
            border-left: 4px solid var(--accent-red);
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .error-banner i {
            color: var(--accent-red);
            font-size: 1.5em;
            margin-right: 10px;
        }
        .error-banner p {
            margin: 0;
            color: var(--text-dark);
        }
        body.dark-mode .error-banner {
            background-color: rgba(234, 67, 53, 0.2);
        }
    `;
    document.head.appendChild(style);
});