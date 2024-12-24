document.addEventListener('DOMContentLoaded', function() {
    initializePagination();
});

function initializePagination() {
    document.querySelectorAll('.pagination-container .page-link').forEach(link => {
        link.onclick = function(e) {
            e.preventDefault();
            const page = this.dataset.page;
            const postsSection = document.querySelector('.posts-section');
            
            // Add loading class
            postsSection.classList.add('loading');
            
            loadPage(page).finally(() => {
                // Remove loading class
                postsSection.classList.remove('loading');
            });
        };
    });
}

async function loadPage(page) {
    const currentUrl = new URL(window.location);
    currentUrl.searchParams.set('page', page);
    
    try {
        const response = await fetch(currentUrl);
        const html = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        
        // Update posts section
        const postsSection = document.querySelector('.posts-section');
        postsSection.innerHTML = doc.querySelector('.posts-section').innerHTML;
        
        // Update URL without reload
        window.history.pushState({}, '', currentUrl);
        
        // Reinitialize event listeners
        initializeEventListeners();
        
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to load page. Please try again.');
    }
}

function initializeEventListeners() {
    initializePagination();
    if (typeof initializeLikeButtons === 'function') {
        initializeLikeButtons();
    }
    if (typeof initializeEditButtons === 'function') {
        initializeEditButtons();
    }
}

// Helper function to get URL parameters
function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
} 