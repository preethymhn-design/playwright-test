# Amazon.in — Search & Product Listing Specification

## Search Bar
- Search input: `input#twotabsearchtextbox`
- Search submit button: `input#nav-search-submit-button`
- Search dropdown (category selector): `select#searchDropdownBox`

## Search Results Page
- URL pattern: `https://www.amazon.in/s?k=<query>`
- Results container: `div[data-component-type="s-search-result"]`
- Each product card contains:
  - Product title: `h2 a span` (inside each result card)
  - Price whole: `span.a-price-whole`
  - Price fraction: `span.a-price-fraction`
  - Star rating: `span.a-icon-alt` (e.g. "4.2 out of 5 stars")
  - Review count: `span.a-size-base` inside `span[aria-label*="ratings"]`
  - "Add to Cart" button (where available): `button.a-button-text` containing "Add to cart"
  - Sponsored label: `span.a-color-secondary` containing "Sponsored"

## Filters (left sidebar)
- Department filter: `div#departments`
- Brand filter: `div[aria-label="Brand"]`
- Price range: `div[aria-label="Price"]`
- Customer reviews filter: `section[aria-label="Customer reviews"]`
- "4 Stars & Up" filter: `li` containing "4 Stars & Up"

## Behaviour
- Searching an empty string does nothing (button disabled or page reloads)
- No results shows: `span.a-size-medium` containing "No results for"
- Results are paginated; next page button: `a.s-pagination-next`
- Clicking a product title navigates to the product detail page
