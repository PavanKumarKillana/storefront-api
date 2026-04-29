from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Product, Collection, Cart, CartItem, ProductImage
from .serializers import ProductSerializer, CollectionSerializer, CartSerializer, CartItemSerializer, ProductImageSerializer

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

@method_decorator(cache_page(60 * 5), name='dispatch')
class ProductViewSet(ModelViewSet):
    """
    A unified ViewSet that handles Listing, Retrieving, Creating, Updating, and Deleting Products!
    """
    queryset = Product.objects.prefetch_related('images').select_related('collection').all()
    serializer_class = ProductSerializer
    
    # We add DjangoFilterBackend for perfect search and filtering
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['collection_id', 'unit_price']
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']


class CollectionViewSet(ModelViewSet):
    """
    Handles operations on Collections.
    """
    # Note: We reuse the exact same get_queryset from our CollectionManager 
    # to avoid N+1 queries everywhere!
    queryset = Collection.objects.all() 
    serializer_class = CollectionSerializer
    # Or typically Mosh overrides get_queryset to annotate if not done in Manager.
    # We did it inside CollectionManager earlier, so Collection.objects.all() works perfectly!


class CartViewSet(CreateModelMixin, 
                  RetrieveModelMixin, 
                  DestroyModelMixin, 
                  GenericViewSet):
    """
    Handles Carts. A Cart shouldn't be 'listed' or 'updated' traditionally.
    You create them (Get a UUID back), fetch them, or Destroy them (checkout/abandon).
    """
    queryset = Cart.objects.prefetch_related('cartitem_set__product').all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
    """
    Nested ViewSet to manage Items inside a specific Cart.
    """
    # We only want items strictly for this specific cart
    def get_queryset(self):
        return CartItem.objects \
            .filter(cart_id=self.kwargs['cart_pk']) \
            .select_related('product')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            from .serializers import AddCartItemSerializer
            return AddCartItemSerializer
        return CartItemSerializer

    # We need to make sure when an item is created, we attach it to the parent Cart
    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}


class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}

    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])
