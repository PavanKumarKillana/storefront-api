from django.core.management.base import BaseCommand
from store.models import Collection, Product, Customer, Order, OrderItem
from tags.models import Tag, TaggedItem
from django.contrib.contenttypes.models import ContentType
import random
from decimal import Decimal

class Command(BaseCommand):
    help = 'Seeds the database with thousands of dummy records for testing.'

    def handle(self, *args, **options):
        self.stdout.write('Deleting old data...')
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Customer.objects.all().delete()
        Product.objects.all().delete()
        Collection.objects.all().delete()
        Tag.objects.all().delete()

        self.stdout.write('Creating Collections...')
        collections = []
        for name in ['Electronics', 'Books', 'Home & Garden', 'Sports', 'Toys', 'Clothing', 'Groceries', 'Automotive', 'Health', 'Beauty']:
            c = Collection.objects.create(title=name)
            collections.append(c)

        self.stdout.write('Creating Products...')
        products = []
        for i in range(1, 401): # 400 Products
            title = f'Product Sample {i}'
            p = Product.objects.create(
                title=title,
                slug=f'product-sample-{i}',
                description=f'This is a generated description for perfectly amazing product {i}.',
                unit_price=Decimal(random.randint(10, 500)) + Decimal('0.99'),
                inventory=random.choice([0, random.randint(1, 5), random.randint(20, 100)]),
                collection=random.choice(collections)
            )
            products.append(p)

        self.stdout.write('Creating Customers...')
        customers = []
        for i in range(1, 101): # 100 Customers
            c = Customer.objects.create(
                first_name=f'UserFirst{i}',
                last_name=f'UserLast{i}',
                email=f'user{i}@example.com',
                phone=f'+1-555-01{str(i).zfill(2)}',
                membership=random.choice(['B', 'S', 'G'])
            )
            customers.append(c)

        self.stdout.write('Creating Orders...')
        for _ in range(250): # 250 orders
            customer = random.choice(customers)
            order = Order.objects.create(
                customer=customer,
                payment_status=random.choice(['P', 'C', 'F'])
            )
            # Add 1 to 5 items per order
            for _ in range(random.randint(1, 5)):
                product = random.choice(products)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=random.randint(1, 3),
                    unit_price=product.unit_price
                )

        self.stdout.write('Creating Generic Tags...')
        product_content_type = ContentType.objects.get_for_model(Product)
        tag_promoted = Tag.objects.create(label='Promoted')
        tag_sale = Tag.objects.create(label='Clearance Sale')

        for _ in range(50):
            TaggedItem.objects.create(
                tag=random.choice([tag_promoted, tag_sale]),
                content_type=product_content_type,
                object_id=random.choice(products).id
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))
