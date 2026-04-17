# Django Project Upgrade & Learning Report

This report documents all the changes, commands, and architectural decisions made to the `storefront` project. You can read this to understand **why** we wrote the code we did, which will be incredibly useful for your learning and your final year project presentation.

---

## 1. The Initial State of the Project
When I received the project, it perfectly mirrored the 2 hour and 30-minute mark of Mosh Hamedani's Django tutorial.
- **What was working:** The basic Entity-Relationship models (Products, Customers, Orders, Collections) were built. The database connection was correctly pointing to your local MySQL database.
- **The Missing Piece:** The project lacked "Production Polish". The models were functioning but lacked Object-Oriented best practices, and the Django Admin was using the default, unoptimized layout which would easily crash if you had real user data.

---

## 2. Phase 1: Database & Admin Optimization

### Problem A: Ugly Object Representations
**The Issue:** When viewing a Product or Customer in the Django shell or Admin, Django would just print `Product object (1)`. This is awful for debugging and management.
**The Solution:** I added `__str__(self)` methods inside every model in `store/models.py`. 
*Learning Point:* In Python, the magic method `__str__` controls how an object is printed as a string.

### Problem B: The N+1 Database Query Problem
**The Issue:** When you look at a list of items (like the Products page), Django will execute 1 database query to get the 10 products, and then 10 MORE queries to fetch the "Collection" name for each product. If you have 100 products on a page, that's 101 queries. This is terrible for performance.
**The Solution:** I modified `store/admin.py` to use `list_select_related = ['collection']`. This forces Django to do an SQL **`INNER JOIN`**, fetching all products and their collections in exactly **1 query**.

### Problem C: Handling the Mockaroo SQL File
**The Solution:** Instead of messing with broken SQL files, I wrote a **Custom Management Command** inside `store/management/commands/seed_db.py`. This script natively uses Python to generate totally valid Customers, Products, and connected Orders.

---

## 3. Phase 2: Building the REST API (Decoupled Architecture)

To move beyond a simple admin panel and allow external apps (like React or Mobile apps) to access your store, we built a modern RESTful API.

### ModelSerializers (`serializers.py`)
**Why?** The database outputs complex Python Objects. External web apps need JSON.
**What we did:** We created `ProductSerializer`, `CollectionSerializer`, and `CartSerializer`. We used advanced tricks like `SerializerMethodField` to dynamically calculate Cart Totals and Taxes on-the-fly without saving redundant data in the database.

### ModelViewSets (`views.py`)
**Why?** In older Django code, you have to write massive standard View functions that look like `if request.method == 'GET'`.
**What we did:** We implemented `ModelViewSet`. These classes automatically generate the logic to List, Create, Retrieve, Update, and Destroy objects using just a few lines of code.

### Nested Routers (`urls.py`)
**Why?** Routing URLs manually like `/store/carts/items/` is messy.
**What we did:** We installed `drf-nested-routers` which scans our ViewSets and systematically generates the perfect URL tree for us. We created a primary router for generic resources and a Nested Router specifically so items are strictly locked to their parent Carts (`/store/carts/{cart_id}/items/`).

### Security Enhancements
**What we did:** We migrated the `Cart` model to use extremely long `UUIDField` strings instead of simple integers (`1, 2, 3`). This prevents malicious users from guessing Cart IDs and stealing other people's shopping data. We also integrated **Djoser** to automatically generate secure Authentication endpoints (`/auth/users/`, `/auth/jwt/create/`).

---

## 4. Commands Executed During Development

To make these updates work, I successfully ran the following commands in your terminal:

1. **`pipenv install djangorestframework djoser djangorestframework-simplejwt drf-nested-routers django-filter`**
   - Installed the industry standards for REST API building and security.
2. **`pipenv run python manage.py makemigrations` & `migrate`**
   - Applied the Cart UUID indexing to the database.

---

## 5. Features for Your Presentation

When you show this to a professor or an interviewer, point out these specific architectures:

- **The Admin Customizations:** Emphasize the Autocomplete Fields on the Order page which optimizes memory usage.
- **Dynamic Serializer Algorithms:** Point them to `CartSerializer.get_total_price` in `serializers.py` to explain how you dynamically compute the sum of heavily nested datasets on the fly using List Comprehension.
- **UUID Security Navigation:** Mention how you mitigated integer-enumeration attacks by upgrading Carts to use UUIDs!
