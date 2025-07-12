from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from decimal import Decimal

class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(_('username'), max_length=150, unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email

class Profile(models.Model):
    EDUCATION_CHOICES = [
        ('high_school', 'High School'),
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('phd', 'PhD'),
        ('other', 'Other'),
    ]
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)
    age = models.PositiveIntegerField()
    highest_education = models.CharField(max_length=20, choices=EDUCATION_CHOICES)
    message = models.TextField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class Image(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title






class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')  # Files organized by date
    original_name = models.CharField(max_length=255)  # Store original filename
    file_size = models.PositiveIntegerField()  # In bytes
    file_type = models.CharField(max_length=100)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Uploaded File"
        verbose_name_plural = "Uploaded Files"

    def __str__(self):
        return f"{self.original_name} (Uploaded by: {self.uploaded_by.username})"






class DummyData(models.Model):
    CATEGORY_CHOICES = [
        ('tech', 'Technology'),
        ('health', 'Healthcare'),
        ('finance', 'Financial'),
        ('education', 'Education'),
        ('home', 'Home Goods')
    ]
    
    STATUS_CHOICES = [
        ('in_stock', 'In Stock'),
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('discontinued', 'Discontinued')
    ]
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    location = models.CharField(max_length=50)
    rating = models.FloatField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional methods
    def stock_status(self):
        if self.quantity == 0:
            return 'Out of Stock'
        elif self.quantity < 10:
            return 'Low Stock'
        return 'In Stock'
    

    def profit_margin(self):
        return round(self.value * Decimal('0.3'), 2)





