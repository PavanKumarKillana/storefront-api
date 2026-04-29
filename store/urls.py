from rest_framework_nested import routers
from . import views

# Standard DRF Router handles standard models automatically (products, collections, carts)
router = routers.DefaultRouter()
router.register('products', views.ProductViewSet, basename='products')
router.register('collections', views.CollectionViewSet, basename='collections')
router.register('carts', views.CartViewSet, basename='carts')

# Nested Router specifically builds the /carts/{uuid}/items/ hierarchy
carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', views.CartItemViewSet, basename='cart-items')

# Nested Router specifically builds the /products/{id}/images/ hierarchy
products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('images', views.ProductImageViewSet, basename='product-images')

# Expose the generated paths dynamically
urlpatterns = router.urls + carts_router.urls + products_router.urls
