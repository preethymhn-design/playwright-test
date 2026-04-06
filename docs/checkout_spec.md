# Checkout Flow Specification

## URL
Checkout starts at `/cart` and proceeds through `/checkout/shipping`, `/checkout/payment`, `/checkout/review`, then `/order-confirmation`.

## Cart Page (`/cart`)
- **Cart items list**: `div.cart-item` — each item shows name, quantity, price
- **Quantity input**: `input.item-quantity` — update quantity on change
- **Remove button**: `button.remove-item` — removes item from cart
- **Subtotal**: `span.subtotal` — updates dynamically
- **Proceed to Checkout button**: `button#checkout-btn`
- Empty cart shows: "Your cart is empty" with a "Continue Shopping" link

## Shipping Page (`/checkout/shipping`)
- Fields: Full Name, Address Line 1, Address Line 2 (optional), City, State, ZIP, Country
- **Continue button**: `button#continue-shipping`
- Validation: all required fields must be filled

## Payment Page (`/checkout/payment`)
- **Card number**: `input[name="cardNumber"]`
- **Expiry**: `input[name="expiry"]` format MM/YY
- **CVV**: `input[name="cvv"]`
- **Pay Now button**: `button#pay-now`
- Invalid card shows: "Invalid card number"
- Expired card shows: "Card has expired"

## Order Confirmation (`/order-confirmation`)
- Shows order number: `span.order-number`
- Shows "Thank you for your order!" heading
- Sends confirmation email to the registered address
