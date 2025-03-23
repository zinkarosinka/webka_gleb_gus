# catalog\signals.py

# signals.py
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .cart import Cart
from .models import CartItem


@receiver(user_logged_in)
def merge_carts(sender, user, request, **kwargs):
    session_cart = Cart(request)
    if session_cart:
        # Перенос товаров в модель CartItem (если используется БД)
        for item in session_cart:
            CartItem.objects.update_or_create(
                user=user,
                product=item['product'],
                defaults={'quantity': item['quantity']}
            )
        session_cart.clear()
