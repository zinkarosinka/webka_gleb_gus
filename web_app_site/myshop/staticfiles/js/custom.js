// static\js\custom.js
document.addEventListener('DOMContentLoaded', function() {
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
    const csrftoken = getCookie('csrftoken');

    function updateCartItem(productId, quantity) {
        fetch(`/cart/update/${productId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken
            },
            body: `quantity=${quantity}&override=True`
        })
        .then(response => response.redirected ? window.location.href = response.url : response.text())
        .then(data => {
            // Обновляем общую цену на странице
            location.reload();
        })
        .catch(error => console.error('Error:', error));
    }
});