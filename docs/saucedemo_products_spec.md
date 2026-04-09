# Sauce Demo — Products/Inventory Specification

## URL
Products page: https://www.saucedemo.com/inventory.html

## Access Requirements
- User must be logged in
- Redirects to login page if not authenticated

## UI Elements

### Header
- App logo: `div.app_logo` containing "Swag Labs"
- Shopping cart: `a.shopping_cart_link` or `[data-test="shopping-cart-link"]`
- Cart badge (when items added): `span.shopping_cart_badge`
- Hamburger menu: `button#react-burger-menu-btn`

### Product Sorting
- Sort dropdown: `select.product_sort_container` or `[data-test="product-sort-container"]`
- Sort options:
  - "Name (A to Z)" - `az`
  - "Name (Z to A)" - `za`
  - "Price (low to high)" - `lohi`
  - "Price (high to low)" - `hilo`

### Product Grid
- Product container: `div.inventory_list`
- Individual product: `div.inventory_item`
- Product image: `img.inventory_item_img`
- Product name: `div.inventory_item_name` or `[data-test="inventory-item-name"]`
- Product description: `div.inventory_item_desc` or `[data-test="inventory-item-desc"]`
- Product price: `div.inventory_item_price` or `[data-test="inventory-item-price"]`
- Add to cart button: `button[data-test="add-to-cart-{product-name}"]`
- Remove button (after adding): `button[data-test="remove-{product-name}"]`

### Available Products
1. Sauce Labs Backpack - $29.99
2. Sauce Labs Bike Light - $9.99
3. Sauce Labs Bolt T-Shirt - $15.99
4. Sauce Labs Fleece Jacket - $49.99
5. Sauce Labs Onesie - $7.99
6. Test.allTheThings() T-Shirt (Red) - $15.99

### Hamburger Menu (Sidebar)
- Menu container: `div.bm-menu`
- All Items link: `a#inventory_sidebar_link`
- About link: `a#about_sidebar_link`
- Logout link: `a#logout_sidebar_link`
- Reset App State link: `a#reset_sidebar_link`
- Close menu button: `button#react-burger-cross-btn`

## Behaviour
- Clicking product name or image navigates to product detail page
- "Add to cart" button changes to "Remove" after clicking
- Cart badge updates with item count
- Sorting reorders products immediately
- Logout clears session and returns to login page
- Reset App State clears cart and resets application

## Product Detail Page
- URL pattern: `/inventory-item.html?id={product-id}`
- Back button: `button[data-test="back-to-products"]`
- Product image: `img.inventory_details_img`
- Product name: `div[data-test="inventory-item-name"]`
- Product description: `div[data-test="inventory-item-desc"]`
- Product price: `div[data-test="inventory-item-price"]`
- Add to cart: `button[data-test="add-to-cart"]`
- Remove: `button[data-test="remove"]`
