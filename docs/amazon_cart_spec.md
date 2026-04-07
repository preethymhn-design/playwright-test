# Amazon.in — Shopping Cart Specification

## URL
Cart page: https://www.amazon.in/gp/cart/view.html

## UI Elements

### Cart Items
- Cart container: `div#sc-active-cart`
- Each cart item: `div[data-asin]` inside the cart container
- Item name: `span.sc-product-title`
- Item price: `span.sc-price`
- Quantity selector: `select[name="quantity"]`
- Delete button: `input[value="Delete"]` inside each item row
- "Save for later" button: `input[value="Save for later"]`

### Cart Summary
- Subtotal: `span#sc-subtotal-amount-activecart`
- Subtotal label: `span#sc-subtotal-label-activecart`
- "Proceed to Buy" button: `input[name="proceedToRetailCheckout"]`

### Empty Cart
- Empty cart message: `div.sc-your-amazon-cart-is-empty` containing "Your Amazon Cart is empty"
- "Shop today's deals" link visible when cart is empty

## Behaviour
- Changing quantity in the dropdown auto-updates the subtotal
- Clicking "Delete" removes the item and updates the subtotal
- Cart item count in top nav (`span#nav-cart-count`) updates after add/remove
- "Proceed to Buy" is disabled when cart is empty
- Items saved for later appear in `div#sc-saved-cart`
- Clicking "Move to Cart" on a saved item moves it back to the active cart
