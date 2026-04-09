# Sauce Demo — Shopping Cart Specification

## URL
Cart page: https://www.saucedemo.com/cart.html

## Access Requirements
- User must be logged in
- Accessible from any page via cart icon in header

## UI Elements

### Header
- Page title: "Your Cart"
- Continue Shopping button: `button[data-test="continue-shopping"]`
- Checkout button: `button[data-test="checkout"]` or `button#checkout`

### Cart Items
- Cart list container: `div.cart_list`
- Cart item: `div.cart_item`
- Item quantity: `div.cart_quantity`
- Item name: `div.inventory_item_name` or `[data-test="inventory-item-name"]`
- Item description: `div.inventory_item_desc` or `[data-test="inventory-item-desc"]`
- Item price: `div.inventory_item_price` or `[data-test="inventory-item-price"]`
- Remove button: `button[data-test="remove-{product-name}"]`

### Empty Cart
- When cart is empty, cart_list may show no items
- Checkout button still visible

## Behaviour
- Cart persists items across page navigation
- Clicking "Remove" removes item from cart immediately
- Cart badge in header updates when items removed
- "Continue Shopping" returns to `/inventory.html`
- "Checkout" proceeds to `/checkout-step-one.html`
- Cannot proceed to checkout without items (button may be disabled or allow empty checkout)

## Cart Item Examples
- Each item shows:
  - Quantity (always 1, no quantity adjustment available)
  - Product name (clickable, links to product detail)
  - Product description
  - Price
  - Remove button

## Navigation
- Back to products: Click "Continue Shopping" or use browser back
- Forward to checkout: Click "Checkout" button
- Remove items: Click individual "Remove" buttons
