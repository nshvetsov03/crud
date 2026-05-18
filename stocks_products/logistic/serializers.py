from rest_framework import serializers
from .models import Product, Stock, StockProduct


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор для продукта"""

    class Meta:
        model = Product
        fields = ['id', 'title', 'description']


class ProductPositionSerializer(serializers.ModelSerializer):
    """Сериализатор для позиции товара на складе"""
    product_title = serializers.CharField(source='product.title', read_only=True)

    class Meta:
        model = StockProduct
        fields = ['product', 'product_title', 'quantity', 'price']


class StockSerializer(serializers.ModelSerializer):
    """Сериализатор для склада с вложенными позициями"""
    positions = ProductPositionSerializer(many=True, required=False)

    class Meta:
        model = Stock
        fields = ['id', 'address', 'positions']

    def create(self, validated_data):

        positions_data = validated_data.pop('positions', [])


        stock = super().create(validated_data)


        for position_data in positions_data:
            StockProduct.objects.create(
                stock=stock,
                **position_data
            )
        return stock

    def update(self, instance, validated_data):

        positions_data = validated_data.pop('positions', [])

        stock = super().update(instance, validated_data)


        for position_data in positions_data:
            StockProduct.objects.update_or_create(
                stock=instance,
                product=position_data['product'],
                defaults={
                    'quantity': position_data.get('quantity', 1),
                    'price': position_data['price']
                }
            )
        return stock