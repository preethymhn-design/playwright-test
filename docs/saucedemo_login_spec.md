# Sauce Demo — Login Specification

## URL
Login page: https://www.saucedemo.com/

## Test Credentials

### Valid Users
- `standard_user` - Standard user with full access
- `problem_user` - User experiencing UI issues
- `performance_glitch_user` - User with performance delays
- `error_user` - User triggering error states
- `visual_user` - User with visual differences

### Locked User
- `locked_out_user` - User account is locked

### Password (for all users)
- `secret_sauce`

## UI Elements

### Login Form
- Username input: `input#user-name` or `input[data-test="username"]`
- Password input: `input#password` or `input[data-test="password"]`
- Login button: `input#login-button` or `input[data-test="login-button"]`

### Error Messages
- Error container: `div[data-test="error"]` or `h3[data-test="error"]`
- Locked out error: "Epic sadface: Sorry, this user has been locked out."
- Invalid credentials: "Epic sadface: Username and password do not match any user in this service"
- Empty username: "Epic sadface: Username is required"
- Empty password: "Epic sadface: Password is required"
- Error close button: `button.error-button` or `button[data-test="error-button"]`

## Behaviour
- Successful login redirects to `/inventory.html`
- Failed login shows error message above the form
- Error messages can be dismissed by clicking the X button
- Session persists across page refreshes
- Logout returns to login page
- Different users may experience different UI behaviors (problem_user, visual_user)
- performance_glitch_user may have delayed responses

## Post-Login Verification
- URL changes to: https://www.saucedemo.com/inventory.html
- Page title: "Swag Labs"
- Header shows: "Swag Labs" logo
- Shopping cart icon visible: `a.shopping_cart_link` or `[data-test="shopping-cart-link"]`
- Hamburger menu visible: `button#react-burger-menu-btn`
