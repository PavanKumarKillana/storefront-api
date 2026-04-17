from decimal import Decimal
from store.models import Product, Collection, Cart, CartItem
from rest_framework import serializers


class CollectionSerializer(serializers.ModelSerializer):
    """
    Serializes Collection Model to JSON.
    We add a products_count field that we will annotate in our ViewSet's query.
    """
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']

    products_count = serializers.IntegerField(read_only=True)


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializes Product Model to JSON.
    Demonstrating ModelSerializer which automatically wires up basic fields.
    """
    class Meta:
        model = Product
        # We explicitly list the fields we want to expose to the public API
        fields = ['id', 'title', 'description', 'slug', 'inventory', 'unit_price', 'price_with_tax', 'collection']

    # We can create custom fields that look like properties on the JSON
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)


class SimpleProductSerializer(serializers.ModelSerializer):
    """
    A simplified version of the ProductSerializer to use inside other serializers (like CartItem).
    """
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializes Items in a Cart, bringing in the nested Product.
    """
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.product.unit_price

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']


class CartSerializer(serializers.ModelSerializer):
    """
    Serializes the overall Shopping Cart, nesting the items and calculating the grand total.
    """
    id = serializers.UUIDField(read_only=True) # Assuming using UUID for carts usually, but sticking to int if defined that way in models. Wait, Mosh converts Cart ID to UUID in Part 2. We didn't change models yet. 
    # For now, we will leave it as standard representation.
    items = CartItemSerializer(many=True, read_only=True, source='cartitem_set')
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart: Cart):
        # We sum up the total_price of all items
        return sum([item.quantity * item.product.unit_price for item in cart.cartitem_set.all()])

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
            
        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']
