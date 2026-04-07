# Amazon.in — Product Detail Page Specification

## URL Pattern
`https://www.amazon.in/dp/<ASIN>`

## UI Elements

### Product Information
- Product title: `span#productTitle`
- Brand: `a#bylineInfo`
- Star rating: `span#acrPopover` (title attribute contains "out of 5 stars")
- Review count: `span#acrCustomerReviewText`
- Price: `span.a-price-whole` inside `div#corePrice_feature_div`
- "About this item" section: `div#feature-bullets ul`
- Product images: `div#imgTagWrapperId img` (main image)
- Image thumbnails: `div#altImages li`

### Purchase Options
- Quantity selector: `select#quantity`
- "Add to Cart" button: `input#add-to-cart-button`
- "Buy Now" button: `input#buy-now-button`
- "Add to Wish List" button: `input#add-to-wishlist-button-submit`

### Availability
- In stock message: `div#availability span` containing "In stock"
- Out of stock message: `div#availability span` containing "Currently unavailable"
- Delivery estimate: `div#mir-layout-DELIVERY_BLOCK`

### Seller Info
- Sold by: `div#merchant-info a`
- Fulfilled by Amazon badge: text "Fulfilled by Amazon" in `div#merchant-info`

## Behaviour
- Clicking "Add to Cart" adds the item and shows a confirmation: `div#NATC_SMART_WAGON_CONF_MSG_SUCCESS`
- Clicking "Buy Now" redirects to checkout directly
- Changing quantity updates the cart count in `span#nav-cart-count`
- Clicking a thumbnail updates the main product image
- Out-of-stock products disable the "Add to Cart" and "Buy Now" buttons
