from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),  # Новый маршрут для обновления
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('order/create/', views.order_create, name='order_create'),
    path('cart/bulk_update/', views.cart_bulk_update, name='cart_bulk_update'),
    path('order/created/<int:order_id>/', views.order_created, name='order_created'),  # Маршрут для успешного оформления заказа
    path('account/dashboard/', views.account_dashboard, name='account_dashboard'),  # Маршрут для личного кабинета
    path('order/detail/<int:order_id>/', views.order_detail, name='order_detail'),  # Маршрут для деталей заказа
    path('account/dashboard/', views.account_dashboard, name='account_dashboard'),
    path('order/detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('cart/update-with-button/<int:product_id>/', views.cart_update_with_button, name='cart_update_with_button'),
    path('api/cdek/points/', views.cdek_points),
    path('api/cdek/calculate/', views.cdek_calculate),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)