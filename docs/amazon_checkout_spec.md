# Amazon.in — Checkout Specification

## URL Flow
1. Cart: `https://www.amazon.in/gp/cart/view.html`
2. Checkout start: `https://www.amazon.in/gp/buy/spc/handlers/display.html`
3. Address step: `https://www.amazon.in/gp/buy/addressselect/handlers/display.html`
4. Payment step: `https://www.amazon.in/gp/buy/payselect/handlers/display.html`
5. Order review: `https://www.amazon.in/gp/buy/spc/handlers/display.html`
6. Order confirmation: `https://www.amazon.in/gp/buy/thankyou/handlers/display.html`

## Address Step

### UI Elements
- Existing address cards: `div.address-ui-widgets-AddressLineUI`
- "Deliver to this address" button: `input[name="shipToThisAddress"]`
- "Add a new address" link: `a` containing "Add a new address"

### Add New Address Form
- Full name: `input[name="address-ui-widgets-enterAddressFullName"]`
- Mobile number: `input[name="address-ui-widgets-enterAddressPhoneNumber"]`
- Pincode: `input[name="address-ui-widgets-enterAddressPostalCode"]`
- Flat/House/Building: `input[name="address-ui-widgets-enterAddressLine1"]`
- Area/Street: `input[name="address-ui-widgets-enterAddressLine2"]`
- Landmark: `input[name="address-ui-widgets-enterAddressLine3"]`
- City: `input[name="address-ui-widgets-enterAddressCity"]`
- State dropdown: `select[name="address-ui-widgets-enterAddressStateOrRegion"]`
- "Use this address" button: `input[name="address-ui-widgets-submit-button"]`

### Validation
- Empty pincode shows: "Please enter a valid pincode"
- Invalid pincode shows: "Please enter a valid pincode"
- Empty name shows: "Please enter your name"
- Empty mobile shows: "Please enter a valid mobile number"

## Payment Step

### UI Elements
- Credit/Debit card option: `input[value="CC"]` or `input[value="DC"]`
- Card number: `input[name="addCreditCardNumber"]`
- Expiry month: `select[name="addCreditCardExpirationMonth"]`
- Expiry year: `select[name="addCreditCardExpirationYear"]`
- CVV: `input[name="addCreditCardVerificationNumber"]`
- Name on card: `input[name="addCreditCardHolderName"]`
- UPI option: `input[value="UPI"]`
- UPI ID input: `input[name="upiId"]`
- Net banking option: `input[value="NB"]`
- Cash on delivery option: `input[value="COD"]` (where available)
- "Use this payment method" button: `input[name="ppw-widgetEvent:SetPaymentPlanSelectAction"]`

## Order Review Step

### UI Elements
- Order items list: `div#spc-orders`
- Total amount: `span#subtotals-marketplace-table` or `td.grand-total-price`
- "Place your order" button: `input[name="placeYourOrder1"]`
- Estimated delivery date: `div.spc-delivery-promise`

## Order Confirmation

### UI Elements
- Confirmation heading: `h4` containing "Order placed, thank you!"
- Order number: `span.a-color-success` or text near "Your order number is"
- Confirmation email note: text containing "A confirmation email has been sent"

## Behaviour
- Must be logged in to proceed to checkout
- "Place your order" button is only enabled when address and payment are both selected
- Clicking "Place your order" charges the selected payment method and creates the order
- Order confirmation page shows the order number and estimated delivery
