# Amazon.in — Orders & Account Specification

## Orders Page

### URL
`https://www.amazon.in/gp/your-account/order-history`

### UI Elements
- Orders list: `div.order` (each order is a card)
- Order date: `span.order-date-invoice-item` containing "Order placed"
- Order total: `span.order-date-invoice-item` containing "Total"
- Order number: `span.order-date-invoice-item` containing "Order #"
- "View order details" link: `a` containing "View order details"
- "Track package" button: `a` containing "Track package"
- "Return or replace items" button: `a` containing "Return or replace items"
- "Write a product review" link: `a` containing "Write a product review"
- Filter by time period: `select[name="orderFilter"]`

### Order Detail Page
- URL pattern: `https://www.amazon.in/gp/your-account/order-details?orderID=<id>`
- Shipping address shown: `div.displayAddressDiv`
- Payment method shown: `div#od-payment-info`
- Item list: `div.a-fixed-left-grid` inside order detail

## Account Settings

### URL
`https://www.amazon.in/gp/css/homepage.html`

### Sections
- "Your Orders": `a` with href containing "order-history"
- "Login & security": `a` with href containing "account-settings"
- "Your Addresses": `a` with href containing "address-book"
- "Payment options": `a` with href containing "wallet"
- "Prime membership": `a` with href containing "prime"

## Behaviour
- Orders page requires login; unauthenticated users are redirected to sign-in
- "Track package" is only visible for shipped orders
- "Return or replace items" is only visible within the return window
- Filtering by time period reloads the order list for that range
