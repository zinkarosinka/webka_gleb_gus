from django.db.models import Sum, F
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import Product, Category, Order, OrderItem, CartItem
from .forms import CartAddProductForm, OrderCreateForm
from django.http import JsonResponse
# views.py (Django)
from django.http import JsonResponse
from django.http import JsonResponse
from django.db import transaction
import json

from django.views.decorators.http import require_POST
from django.db import transaction
import json
import requests

import uuid
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from .models import Order

from myshop.settings import CDEK_ACCOUNT, CDEK_PASSWORD
from decimal import Decimal
from django.conf import settings
from .cart import Cart

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .cart import Cart
from .models import Product
from .forms import CartAddProductForm


@login_required
@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    # Обработка формы
    form = CartAddProductForm(request.POST, product=product)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(
            product=product,
            quantity=cd['quantity'],
            override_quantity=cd['override']
        )
    else:
        # Обработка невалидных данных формы
        cart.add(product=product, quantity=1)

    return redirect('cart_detail')


@login_required
@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')

@login_required
@require_POST
def cart_bulk_update(request):
    try:
        data = json.loads(request.body)
        updated_items = []
        total_price = 0

        with transaction.atomic():
            for item_data in data.get('items', []):
                product = get_object_or_404(Product, id=item_data['product_id'])
                quantity = int(item_data['quantity'])

                if quantity < 1 or quantity > product.stock:
                    raise ValueError(f"Некорректное количество для товара {product.name}")

                cart_item, created = CartItem.objects.get_or_create(
                    user=request.user,
                    product=product
                )
                cart_item.quantity = quantity
                cart_item.save()

                item_total = product.price * quantity
                updated_items.append({
                    'product_id': product.id,
                    'item_total': item_total
                })
                total_price += item_total

        return JsonResponse({
            'status': 'success',
            'updated_items': updated_items,
            'total_price': total_price
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
@require_POST
def cart_update(request, product_id):
    try:
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))

        cart_item = CartItem.objects.get(
            user=request.user,  # Заменили customer на request.user
            product=product
        )
        cart_item.quantity = quantity
        cart_item.save()

        total_price = CartItem.objects.filter(
            user=request.user  # Заменили customer на request.user
        ).aggregate(
            total=Sum(F('product__price') * F('quantity'))
        )['total'] or 0

        return JsonResponse({
            'status': 'success',
            'item_total': product.price * quantity,
            'total_price': total_price
        })

    except CartItem.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Товар не найден в корзине'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def home(request):
    return render(request, 'catalog/home.html')

def product_list(request, category_slug=None):
    products = Product.objects.filter(available=True)
    return render(request,
                  'catalog/product/list.html',
                  {'products': products})

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    return render(request,
                 'catalog/product/detail.html',  # Проверьте путь к шаблону
                 {'product': product})

"""@login_required
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = CartAddProductForm(request.POST, product=product)
        if form.is_valid():
            cd = form.cleaned_data
            quantity = cd['quantity']
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                product=product
            )
            if not created:
                if cd['override']:
                    cart_item.quantity = quantity
                else:
                    cart_item.quantity += quantity
            else:
                cart_item.quantity = quantity
            cart_item.save()
    else:
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product
        )
        if not created:
            cart_item.quantity += 1
        else:
            cart_item.quantity = 1
        cart_item.save()
    return redirect('cart_detail')

@login_required
def cart_remove(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(user=request.user, product=product)
        cart_item.delete()
    except CartItem.DoesNotExist:
        pass
    return redirect('cart_detail')"""

@login_required
def cart_detail(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'catalog/cart/detail.html', {'cart_items': cart_items, 'total_price': total_price})


@login_required
def order_create(request):
    cart_items = CartItem.objects.filter(user=request.user)  # Заменили customer на request.user

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,  # Заменили customer на request.user
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                address=form.cleaned_data['address'],
                postal_code=form.cleaned_data['postal_code'],
                city=form.cleaned_data['city']
            )
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=item.product.price,
                    quantity=item.quantity
                )
            cart_items.delete()  # Очистка корзины
            return redirect('order_created', order_id=order.id)
    else:
        form = OrderCreateForm(instance=request.user)

    return render(request, 'catalog/orders/create.html', {
        'cart_items': cart_items,
        'form': form,
        'total_price': sum(item.product.price * item.quantity for item in cart_items)
    })

@login_required
def order_created(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'catalog/orders/order_created.html', {'order': order})
@login_required
def account_dashboard(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'catalog/account/dashboard.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer__user=request.user)
    return render(request, 'catalog/orders/order_detail.html', {'order': order})

@login_required
def cart_update_with_button(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        if quantity and quantity.isdigit():
            try:
                # Changed: Use user directly instead of customer
                cart_item = CartItem.objects.get(user=request.user, product=product)
                cart_item.quantity = int(quantity)
                cart_item.save()
            except CartItem.DoesNotExist:
                pass
    return redirect('cart_detail')


def cdek_points(request):
    # Запрос к API СДЭК
    response = requests.get(
        'https://api.cdek.ru/v2/deliverypoints',
        params={'city_code': request.GET.get('city')},
        auth=(settings.CDEK_ACCOUNT, settings.CDEK_PASSWORD)
    )
    return JsonResponse({'points': response.json()})

def cdek_calculate(request):
    data = json.loads(request.body)
    # Запрос тарифов к API СДЭК
    response = requests.post(
        'https://api.cdek.ru/v2/calculator/tariff',
        json={
            "type": 1,
            "from_location": {"code": 270},  # Ваш город
            "to_location": {"code": data['postal_code']},
            "packages": [{"weight": data['weight']}]
        },
        auth=(CDEK_ACCOUNT, CDEK_PASSWORD)
    )
    return JsonResponse(response.json())

@login_required
def order_detail(request, order_id):
    # Changed: Use user directly instead of customer__user
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'catalog/orders/order_detail.html', {'order': order})


def create_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    payment_data = {
        "amount": {
            "value": f"{order.total_cost:.2f}",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "embedded",
            "return_url": settings.YOOKASSA_RETURN_URL
        },
        "capture": True,
        "description": f"Оплата заказа №{order.id}",
        "metadata": {
            "order_id": order.id
        }
    }

    response = requests.post(
        'https://api.yookassa.ru/v3/payments',
        auth=(settings.YOOKASSA_SHOP_ID, settings.YOOKASSA_SECRET_KEY),
        headers={'Idempotence-Key': str(uuid.uuid4())},
        json=payment_data
    )

    payment = response.json()
    order.payment_id = payment['id']
    order.save()

    return render(request, 'catalog/payment.html', {
        'order': order,
        'payment': payment
    })
