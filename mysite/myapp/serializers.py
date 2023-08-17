from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    product_image = serializers.ImageField(max_length=None,use_url = True)
    class Meta:
        model = Product
        fields = ['id','name','description','price','product_image']