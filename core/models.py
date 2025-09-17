from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.contrib.postgres.fields import ArrayField
from django.conf import settings

class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("user email is required")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user

class User(AbstractBaseUser, PermissionsMixin):
    """Custom user"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

class Entity(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='+')

    class Meta:
        # add abstract so that it wont add table for entity model
        abstract = True


class Shop(Entity):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class Product(Entity):
    name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='uploads/', blank=True, null=True)
    variations = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    category = models.CharField(max_length=50, blank=True)


class Cart(Entity):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)


class Review(Entity):
    message = models.TextField(blank=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    product = models.ForeignKey(Product, related_name="reviews", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class Transaction(Entity):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item_price_at_purchase = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
