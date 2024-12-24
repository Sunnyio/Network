document.addEventListener('DOMContentLoaded', function() {
    const followButton = document.getElementById('follow-button');
    if (followButton) {
        followButton.onclick = function() {
            const userId = this.dataset.userId;
            
            fetch('/toggle_follow', {
                method: 'POST',
                body: JSON.stringify({
                    user_id: userId
                }),
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error(data.error);
                    return;
                }
                
                // Update button text and style
                this.innerHTML = data.is_following ? 'Unfollow' : 'Follow';
                this.classList.toggle('btn-primary');
                this.classList.toggle('btn-secondary');
                
                // Update followers count
                document.getElementById('followers-count').textContent = data.followers_count;
            })
            .catch(error => {
                console.error('Error:', error);
            });
        };
    }
});

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