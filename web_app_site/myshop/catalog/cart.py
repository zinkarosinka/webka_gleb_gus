from decimal import Decimal
from urllib import request

from django.conf import settings
from django.shortcuts import redirect

from .models import Product
from django.contrib import messages

class Cart(object):

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        try:
            product_id = str(product.id)
            if product.stock <= 0:
                raise ValueError("Товар отсутствует на складе")

            if product_id not in self.cart:
                max_qty = min(quantity, product.stock)
                self.cart[product_id] = {'quantity': max_qty, 'price': str(product.price)}
            else:
                new_qty = self.cart[product_id]['quantity'] + quantity
                self.cart[product_id]['quantity'] = min(new_qty, product.stock)

            self.save()
            #messages.success(request, f"Товар {product.name} добавлен в корзину")
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('cart_detail')


    def update(self, product, quantity=1):
        product_id = str(product.id)
        if product_id in self.cart:
            self.cart[product_id]['quantity'] = quantity
            self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(item['price'] * item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()