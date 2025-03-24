from django.contrib import admin
from .models import Category, Product, Order, OrderItem
from django.contrib import admin
from .models import Product

from django.contrib import admin
from .models import Product, Category, ProductImage
from django.contrib import admin
from .models import Product, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3

@admin.register(Product)  # ✅ Только один способ регистрации
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ['name', 'price', 'stock']
    search_fields = ['name', 'description']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']


"""
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price', 'stock', 'available', 'created', 'updated']
    list_filter = ['available', 'created', 'updated']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('name',)}"""

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']

class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'first_name',  # Было 'customer'
        'last_name',
        'email',
        'paid',  # Теперь поле существует
        'status',
        'created',
        'updated'
    ]
    list_filter = [
        'paid',  # Теперь поле существует
        'status',
        'created',
        'updated'
    ]



admin.site.register(Order, OrderAdmin)
