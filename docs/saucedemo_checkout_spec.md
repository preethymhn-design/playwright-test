# Sauce Demo — Checkout Specification

## URLs
- Step 1 (Information): https://www.saucedemo.com/checkout-step-one.html
- Step 2 (Overview): https://www.saucedemo.com/checkout-step-two.html
- Complete: https://www.saucedemo.com/checkout-complete.html

## Access Requirements
- User must be logged in
- Typically accessed from cart page

## Checkout Step 1: Your Information

### UI Elements
- Page title: "Checkout: Your Information"
- First Name input: `input#first-name` or `input[data-test="firstName"]`
- Last Name input: `input#last-name` or `input[data-test="lastName"]`
- Postal Code input: `input#postal-code` or `input[data-test="postalCode"]`
- Cancel button: `button[data-test="cancel"]` or `button#cancel`
- Continue button: `input[data-test="continue"]` or `input#continue`

### Error Messages
- Error container: `h3[data-test="error"]` or `div[data-test="error"]`
- Missing first name: "Error: First Name is required"
- Missing last name: "Error: Last Name is required"
- Missing postal code: "Error: Postal Code is required"
- Error close button: `button.error-button`

### Behaviour
- All three fields are required
- Cancel returns to cart page
- Continue validates fields and proceeds to overview
- Error messages appear above the form

## Checkout Step 2: Overview

### UI Elements
- Page title: "Checkout: Overview"
- Cart items list: `div.cart_list`
- Item details: Same structure as cart page
- Payment Information: `div[data-test="payment-info-label"]` and value
- Shipping Information: `div[data-test="shipping-info-label"]` and value
- Price Total: `div.summary_info`
  - Item total: `div.summary_subtotal_label` (e.g., "Item total: $29.99")
  - Tax: `div.summary_tax_label` (e.g., "Tax: $2.40")
  - Total: `div.summary_total_label` or `div[data-test="total-label"]` (e.g., "Total: $32.39")
- Cancel button: `button[data-test="cancel"]`
- Finish button: `button[data-test="finish"]` or `button#finish`

### Behaviour
- Shows summary of order with all items
- Displays payment method (usually "SauceCard #31337")
- Displays shipping method (usually "Free Pony Express Delivery!")
- Calculates and shows tax
- Cancel returns to products page
- Finish completes the order

## Checkout Complete

### UI Elements
- Page title: "Checkout: Complete!"
- Success icon: `img.pony_express`
- Success header: `h2.complete-header` containing "Thank you for your order!"
- Success message: `div.complete-text` containing "Your order has been dispatched..."
- Back Home button: `button[data-test="back-to-products"]` or `button#back-to-products`

### Behaviour
- Order is complete
- Cart is cleared (badge removed)
- "Back Home" returns to products page
- Cannot navigate back to previous checkout steps

## Complete Checkout Flow
1. Add items to cart from products page
2. Click cart icon → Click "Checkout"
3. Fill in: First Name, Last Name, Postal Code → Click "Continue"
4. Review order details and total → Click "Finish"
5. See confirmation → Click "Back Home"

## Validation Rules
- Step 1: All fields required (First Name, Last Name, Postal Code)
- Step 2: No validation, review only
- Cannot skip steps (direct URL access may redirect)
