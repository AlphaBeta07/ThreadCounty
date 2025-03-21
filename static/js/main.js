// main.js - Client-side JavaScript for ThreadCounty app

document.addEventListener('DOMContentLoaded', function() {
  // Initialize tooltips
  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

  // File input preview functionality
  const fileInput = document.getElementById('file');
  if (fileInput) {
    fileInput.addEventListener('change', function(e) {
      const file = e.target.files[0];
      if (file) {
        // Validate file type
        const validImageTypes = ['image/jpeg', 'image/png', 'image/tiff', 'image/bmp'];
        if (!validImageTypes.includes(file.type)) {
          showAlert('Please select a valid image file (JPG, PNG, TIFF, or BMP)', 'danger');
          fileInput.value = ''; // Clear the file input
          return;
        }

        // Validate file size
        const maxSize = 16 * 1024 * 1024; // 16MB
        if (file.size > maxSize) {
          showAlert('File is too large. Maximum size is 16MB', 'danger');
          fileInput.value = ''; // Clear the file input
          return;
        }

        // Show file preview
        const reader = new FileReader();
        reader.onload = function(e) {
          const previewContainer = document.getElementById('preview-container');
          if (previewContainer) {
            previewContainer.innerHTML = `
              <div class="mt-3">
                <h5>Preview:</h5>
                <div class="text-center">
                  <img src="${e.target.result}" class="img-fluid img-thumbnail" style="max-height: 300px;">
                  <p class="mt-2 text-muted">${file.name} (${formatFileSize(file.size)})</p>
                </div>
              </div>
            `;
          }
        };
        reader.readAsDataURL(file);
      }
    });
  }

  // Form submission with loading indicator
  const analysisForm = document.getElementById('analysis-form');
  if (analysisForm) {
    analysisForm.addEventListener('submit', function(e) {
      const submitBtn = this.querySelector('button[type="submit"]');
      if (submitBtn) {
        // Save original button text
        const originalText = submitBtn.innerHTML;
        
        // Show loading spinner
        submitBtn.innerHTML = `
          <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
          Processing...
        `;
        submitBtn.disabled = true;
        
        // Add event listener to restore button after page reload attempt
        window.addEventListener('beforeunload', function() {
          submitBtn.innerHTML = originalText;
          submitBtn.disabled = false;
        });
      }
    });
  }

  // Function to show bootstrap alerts
  function showAlert(message, type = 'info') {
    const alertsContainer = document.getElementById('alerts-container');
    if (alertsContainer) {
      const alert = document.createElement('div');
      alert.className = `alert alert-${type} alert-dismissible fade show`;
      alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      `;
      alertsContainer.appendChild(alert);
      
      // Auto-dismiss after 5 seconds
      setTimeout(() => {
        if (alert) {
          const bsAlert = new bootstrap.Alert(alert);
          bsAlert.close();
        }
      }, 5000);
    }
  }

  // Format file size in KB, MB
  function formatFileSize(bytes) {
    if (bytes < 1024) {
      return bytes + ' bytes';
    } else if (bytes < 1024 * 1024) {
      return (bytes / 1024).toFixed(1) + ' KB';
    } else {
      return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }
  }
});
