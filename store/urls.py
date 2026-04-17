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

# Expose the generated paths dynamically
urlpatterns = router.urls + carts_router.urls
