function adjustQuantity(productId, delta) {
    const quantityElement = document.getElementById(`quantity_${productId}`);
    const currentQuantity = parseInt(quantityElement.innerText);
    const maxQuantity = parseInt(quantityElement.dataset.maxQuantity);
    const newQuantity = currentQuantity + delta;
    
    if (newQuantity < 1 || newQuantity > maxQuantity) return;
    
    updateCartItem(productId, newQuantity);
}

function updateQuantity(productId, quantity) {
    fetch(`/cart/update/${productId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrftoken
        },
        body: `quantity=${quantity}`
    })
    .then(response => {
        if (response.status === 400) {
            return response.json().then(data => {
                alert(data.message);
                // Восстановите предыдущее значение
                document.querySelector(`#quantity_${productId}`).value =
                    document.querySelector(`#quantity_${productId}`).defaultValue;
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            document.getElementById(`total_price_${productId}`).textContent =
                `${data.item_total} руб.`;
            document.getElementById('total_price').textContent =
                `${data.total_price} руб.`;
        }
    })
    .catch(error => console.error('Error:', error));
}