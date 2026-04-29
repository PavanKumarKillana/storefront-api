from django.contrib import admin
from django.db.models.aggregates import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse
from . import models

# ---------------------------------------------------------
# Admin Dashboard Customizations (The "Interview Impresser")
# ---------------------------------------------------------


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    """
    By creating a Custom ModelAdmin, we change how "Collections" look in the Admin panel.
    """
    list_display = ['title', 'products_count']
    # search_fields is REQUIRED if another model wants to use `autocomplete_fields` 
    # to search for a Collection.
    search_fields = ['title']

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        """
        We inject a calculated column into the admin list view.
        We also make it clickable to filter the Product page by this collection!
        """
        # We generate a URL to the Product change list filtered by this collection
        url = (
            reverse('admin:store_product_changelist')
            + '?'
            + urlencode({
                'collection__id': str(collection.id)
            })
        )
        return format_html('<a href="{}">{} Products</a>', url, collection.products_count)

    def get_queryset(self, request):
        # We override the base queryset to always annotate the product count
        # This prevents an N+1 query problem!
        return super().get_queryset(request).annotate(
            products_count=Count('product')
        )


class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    readonly_fields = ['thumbnail']

    def thumbnail(self, instance):
        if instance.image.name != '':
            return format_html('<img src="{}" class="thumbnail" />', instance.image.url)
        return ''

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    """
    This is what makes the admin panel powerful: customizing the UI without frontend code.
    """
    # Columns to show in the list view
    list_display = ['title', 'unit_price', 'inventory_status', 'collection_title']
    
    # Fields you can edit directly from the list page
    list_editable = ['unit_price']
    
    # Items per page
    list_per_page = 10
    
    # We add search_fields so that the OrderItemInline autocomplete can search for Products!
    search_fields = ['title']

    # This prevents the admin from loading ALL collections into a huge dropdown,
    # instead it gives us a nice search bar! (Requires search_fields in CollectionAdmin)
    autocomplete_fields = ['collection']

    # Performance optimization:
    # Use select_related when you have a ForeignKey to prevent N+1 queries.
    list_select_related = ['collection']

    # Here we define a custom Bulk Action
    actions = ['clear_inventory']
    
    inlines = [ProductImageInline]

    def collection_title(self, product):
        return product.collection.title

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        """
        A custom method to display dynamically calculated/formatted text in the Django Admin.
        """
        if product.inventory < 10:
            return format_html('<span style="color: red; font-weight: bold;">Low ({} left)</span>', product.inventory)
        return format_html('<span style="color: green;">{}</span>', 'OK')

    @admin.action(description='Clear inventory')
    def clear_inventory(self, request, queryset):
        """
        We can apply actions to multiple selected items at once.
        This updates multiple rows in the database efficiently.
        """
        updated_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f'{updated_count} products were successfully marked as out of stock.',
            # messages.ERROR or messages.SUCCESS could be used if imported
        )


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership']
    list_editable = ['membership']
    list_per_page = 10
    # Enable a search bar that looks across both first and last name
    search_fields = ['first_name__istartswith', 'last_name__istartswith']


class OrderItemInline(admin.TabularInline):
    """
    Inlines allow us to edit related objects on the same page.
    Here, we can edit OrderItems inside the Order edit page!
    """
    model = models.OrderItem
    autocomplete_fields = ['product']
    extra = 0 # Don't show extra empty rows by default
    min_num = 1


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'placed_at', 'customer']
    # When loading orders, also grab the customer in the same query
    list_select_related = ['customer']
    autocomplete_fields = ['customer']
    inlines = [OrderItemInline]
