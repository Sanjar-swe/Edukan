from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


# --- Категории и Товары ---

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kategoriya ati")
    slug = models.SlugField(max_length=150, unique=True, verbose_name="Slug")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name="Tiykargi kategoriya")

    class Meta:
        verbose_name = 'Kategoriya'
        verbose_name_plural = 'Kategoriyalar'
        ordering = ['name']
    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Kategoriya")
    name = models.CharField(max_length=255, verbose_name="Onim ati")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="Slug")
    description = models.TextField(verbose_name="Toliq maglıwmat")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Bahası")
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Shegirmeli bahasi")
    image = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name="Ónim súwreti")
    stock = models.PositiveIntegerField(default=0, verbose_name="Qoymadaǵı sanı")
    is_active = models.BooleanField(default=True, verbose_name="Satılıwda bar")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Jaratılǵan waqtı")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ózgertilgen waqtı")

    class Meta:
        verbose_name = 'Ónim'
        verbose_name_plural = 'Ónimler'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def is_on_sale(self):
        """Returns True if the product has a valid discount."""
        return self.discount_price is not None and self.discount_price < self.price

    @property
    def calc_discount_percent(self):
        """Calculates the percentage of the discount."""
        if self.is_on_sale:
            discount_amount = self.price - self.discount_price
            return int((discount_amount / self.price) * 100)
        return 0

    def get_price(self):
        """Returns discount_price if it exists, otherwise price."""
        if self.discount_price:
            return self.discount_price
        return self.price

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.discount_price and self.discount_price >= self.price:
            raise ValidationError({
                'discount_price': "Shegirmeli baha tiykarg'i bahadan kishi boliwi shart! / Скидочная цена должна быть меньше основной!"
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

# --- Корзина (Cart) ---

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Sebet'
        verbose_name_plural = 'Sebetler'
    def __str__(self):
        return f"{self.user.username} sebeti"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    
    class Meta:
        verbose_name = 'Sebetdegi onim'
        verbose_name_plural = 'Sebetdegi onimler'
        unique_together = ['cart', 'product']
    def __str__(self):
        return f"{self.quantity} {self.product.name}"


# --- Заказы (Orders) ---
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'kutilip atir'),
        ('paid', 'tolendi'),
        ('shipped', 'jiberildi'),
        ('cancelled', 'biykar qilindi'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    total_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Ulıwma bahasi")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Jaǵdayı")
    address = models.TextField(verbose_name="Jetkerip beriw mánzili")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Buyırtpa qiling'an waqtı")

    class Meta:
        verbose_name = 'Buyırtpa'
        verbose_name_plural = 'Buyırtpalar'

    def __str__(self):
        return f"Buyırtpa #{self.id} — {self.user.username}"

# то что было заказано
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Buyırtpa")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Ónim ati")
    quantity = models.PositiveIntegerField(verbose_name="Sani")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Bahasi")
    
    class Meta:
        verbose_name = 'Buyırtpadagi onim'
        verbose_name_plural = 'Buyırtpadagi onimler'
        ordering = ['id']
    def __str__(self):
        return f"{self.quantity} {self.product.name} (Buyırtpa #{self.order.id})"
    
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name="Ónim")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews', verbose_name="Paydalanıwshı")
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="Reyting")
    comment = models.TextField(verbose_name="Kommentariya")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Jazilg'an waqtı")
    
    class Meta:
        verbose_name = 'Pikir'
        verbose_name_plural = 'Pikirler'

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating})" 



    
    