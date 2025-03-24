#from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
import os
from django.utils.text import slugify
import uuid
from django.core.validators import MinValueValidator

class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name
#thus vers works
class Product(models.Model):
    category = models.ForeignKey(
        Category,
        related_name='products',
        on_delete=models.CASCADE,
        verbose_name='Категория'
    )
    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=200,
        db_index=True,
        unique=True
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Цена'
    )
    stock = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Остаток'
    )
    available = models.BooleanField(
        default=True,
        verbose_name='Доступен'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создан'
    )
    updated = models.DateTimeField(
        auto_now=True,
        verbose_name='Обновлен'
    )
    #image = models.ImageField(upload_to='products/')
    class Meta:
        ordering = ('name',)
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
            models.Index(fields=['-created']),
        ]
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='products/')
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Порядок сортировки'
    )

    class Meta:
        ordering = ['order']
        unique_together = ('product', 'order')

    def __str__(self):
        return f"Image for {self.product.name}"

    def save(self, *args, **kwargs):
        if not self.pk:
            max_order = ProductImage.objects.filter(
                product=self.product
            ).aggregate(models.Max('order'))['order__max'] or 0
            self.order = max_order + 1

        """ext = os.path.splitext(self.image.name)[1]
        slug = slugify(self.product.name)
        filename = f"{slug}-{self.order}{ext}"
        self.image.name = f"products/{filename}"""

        super().save(*args, **kwargs)



class Customer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer'
    )
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        def __str__(self):
            return f"Customer {self.user.username}" if self.user else "Anonymous Customer"




class Order(models.Model):
    STATUS_CHOICES = (
        ('created', 'Создан'),
        ('waiting', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('delivering', 'В доставке'),
        ('completed', 'Завершен'),
        ('canceled', 'Отменен'),
    )
    DELIVERY_METHODS = (
        ('self', 'Самовывоз'),
        ('courier', 'Курьер'),
        ('post', 'Почта'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders'
    )
    first_name = models.CharField(max_length=50, default='Egor')
    last_name = models.CharField(max_length=50, default='Zon')
    email = models.EmailField(default="")
    address = models.CharField(max_length=250, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='created'
    )
    paid = models.BooleanField(default=False)
    delivery_method = models.CharField(max_length=20, default='self')
    cdek_point = models.CharField(max_length=100, blank=True)
    payment_data = models.JSONField(null=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    delivery_method = models.CharField(
        max_length=10,
        choices=DELIVERY_METHODS,
        default='self'
    )
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0  # Исправить с '0' на 0
    )

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f'Order {self.id}'

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        related_name='order_items',
        on_delete=models.CASCADE
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity}x {self.product.name} (Order {self.order.id})'

    def get_cost(self):
        return self.price * self.quantity

class CartItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='cart_items',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        related_name='cart_items',
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_cost(self):
        return self.product.price * self.quantity

    class Meta:
        unique_together = ('user', 'product')