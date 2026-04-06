# Login Page Specification

## URL
The login page is accessible at `/login`.

## UI Elements
- **Email input**: `input[name="email"]` — accepts a valid email address
- **Password input**: `input[name="password"]` — accepts a password (min 8 chars)
- **Login button**: `button[type="submit"]` with text "Sign In"
- **Forgot password link**: `a[href="/forgot-password"]` with text "Forgot Password?"
- **Error message**: `div.error-message` — shown on invalid credentials
- **Remember me checkbox**: `input[name="remember"]`

## Behaviour
- Successful login with valid credentials redirects to `/dashboard`
- Invalid email format shows inline validation: "Please enter a valid email"
- Wrong password shows error: "Invalid email or password"
- Empty form submission shows: "Email is required" and "Password is required"
- After 5 failed attempts the account is locked and shows: "Account locked. Try again in 15 minutes."
- "Remember me" keeps the session alive for 30 days
- Forgot password link navigates to `/forgot-password`
