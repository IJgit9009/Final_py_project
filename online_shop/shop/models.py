from django.db import models
from django.db.models import CASCADE
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.formfields import PhoneNumberField


class UserProfile(AbstractUser):
    age = models.PositiveSmallIntegerField(default=0, null=True, blank=True,
                        validators=[MinValueValidator(18), MaxValueValidator(90)])
    date_registered = models.DateField(auto_now=True, null=True, blank=True)
    phone_number = PhoneNumberField(region='KG')
    STATUS_CHOICES = (
        ("gold", "Gold"),
        ("silver", "Silver"),
        ("bronze", "Bronze"),
        ("simple", "Simple"),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES,
                              default="simple", null=True, blank=True)

    def __str__(self):
        return f" {self.first_name} - {self.last_name}"


class Category(models.Model):
    category_name = models.CharField(max_length=16, unique=True)

    def __str__(self):
        return self.category_name


class Product(models.Model):
    product_name = models.CharField(max_length=32)
    category = models.ForeignKey(Category, related_name="products", on_delete=CASCADE)
    price = models.PositiveIntegerField(default=0)
    description = models.TextField()
    date = models.DateField(auto_now=True)
    active = models.BooleanField(default=True)
    product_video = models.FileField(verbose_name="Видео", null=True, blank=True)

    def __str__(self):
        return self.product_name

    def get_average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return round(sum(rating.stars for rating in ratings) / ratings.count(), 1)
        return 0


class ProductPhotos(models.Model):
    product = models.ForeignKey(Product, related_name="product", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="product_images/")


class Ratings(models.Model):
    product = models.ForeignKey(Product, related_name="ratings", on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    stars = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], verbose_name="Рейтинг")

    def __str__(self):
        return f" {self.product} - {self.user} - {self.stars} stars"


class Reviews(models.Model):
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    text = models.TextField()
    product = models.ForeignKey(Product, related_name="review", on_delete=models.CASCADE)
    parent_review = models.ForeignKey("self", related_name="replies",
                                null=True, blank=True, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author} - {self.product}"


class Cart(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='cart')
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}"

    def get_total_price(self):
        total_price = sum(item.get_total_price() for item in self.items.all())
        discount = 0

        if self.user.status == 'gold':
            discount = 0.75
        elif self.user.status == 'silver':
            discount = 0.50
        elif self.user.status == 'bronze':
            discount = 0.25

        final_price = total_price * (1 - discount)
        return final_price


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)

    def get_total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.cart}"

