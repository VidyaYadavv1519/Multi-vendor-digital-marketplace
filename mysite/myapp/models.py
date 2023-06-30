from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class ProductCategory(models.Model):
    category = models.CharField(max_length=200,blank=True,null=True)

    def __str__(self):
        return self.category


class Product(models.Model):
    seller = models.ForeignKey(User,on_delete=models.CASCADE)
    product_category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE,null=True,blank=True)
    name = models.CharField(max_length=200,null=True,blank=True)
    description = models.CharField(max_length=200,null=True,blank=True)
    price = models.FloatField(null=True,blank=True)
    product_image = models.FileField(upload_to='uploads',null=True,blank=True)
    total_sales_amount = models.IntegerField(default=0)
    total_sales = models.IntegerField(default=0)


    def __str__(self):
        return self.name


class OrderDetail(models.Model):
    customer_email = models.EmailField(null=True,blank=True)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    amount = models.IntegerField()
    stripe_payment_intent = models.CharField(max_length=200,null=True,blank=True)
    has_paid = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)


