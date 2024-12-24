document.addEventListener('DOMContentLoaded', function() {
    // Initialize like buttons
    document.querySelectorAll('.like-button').forEach(button => {
        button.onclick = function() {
            toggleLike(this);
        };
    });
});

async function toggleLike(button) {
    const postId = button.dataset.postId;
    try {
        const response = await fetch(`/post/${postId}/like`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Update the like count
            const likeCount = button.querySelector('.like-count');
            likeCount.textContent = data.likes_count;
            
            // Toggle the button appearance
            button.classList.toggle('liked', data.liked);
            
            // Update the heart icon
            const heartIcon = button.querySelector('i');
            heartIcon.className = data.liked ? 'fas fa-heart' : 'far fa-heart';
            
            // Update the like text
            const likeText = data.likes_count === 1 ? 'like' : 'likes';
            likeCount.textContent = `${data.likes_count} ${likeText}`;
        } else {
            throw new Error(data.error || 'Failed to toggle like');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to update like status');
    }
}

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
} 