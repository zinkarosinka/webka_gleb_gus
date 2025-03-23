from django.contrib.auth.models import User
from django.conf import settings
from django.db import models

from django.utils.text import slugify
import uuid

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f"products/{filename}"

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
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        verbose_name='Изображение'
    )
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    description = models.TextField(blank=True, verbose_name='Описание')

    category = models.ForeignKey(
        Category,
        related_name='products',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=200, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    slug = models.SlugField(max_length=200, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)
        indexes = [models.Index(fields=['id', 'slug'])]
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
    def __str__(self):
        return self.name



class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='products/')
    image_number = models.PositiveIntegerField(editable=False)  # Автоинкрементный номер

    def save(self, *args, **kwargs):
        if not self.pk:  # Только при создании
            last_number = ProductImage.objects.filter(
                product=self.product
            ).aggregate(models.Max('image_number'))['image_number__max'] or 0
            self.image_number = last_number + 1

        # Генерация имени файла
        ext = os.path.splitext(self.image.name)[1]
        slug = slugify(self.product.name)
        filename = f"{slug}{self.image_number}{ext}"
        self.image.name = f"products/{filename}"

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
        return f"{self.user.username}'s profile"



"""class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(
        upload_to='products/',  # Убрали шаблон с датой
        verbose_name='Изображение'
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name='Главное изображение'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Порядок сортировки'
    )

    class Meta:
        ordering = ['order']
"""

class Order(models.Model):
    STATUS_CHOICES = (
        ('created', 'Создан'),
        ('waiting', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('delivering', 'В доставке'),
        ('completed', 'Завершен'),
        ('canceled', 'Отменен'),
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
        return f'{self.id}'

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

    class Meta:
        unique_together = ('user', 'product')