# Amazon.in — Login & Account Specification

## URL
Login page: https://www.amazon.in/ap/signin

## Entry Points
- Top navigation: click "Hello, sign in" → "Sign In" button
- Direct URL: https://www.amazon.in/ap/signin

## UI Elements

### Email / Phone Step
- Email input: `saziram@gmail.com`
- Continue button: `input#continue` (type="submit", value="Continue")
- "New to Amazon?" link: `a` containing text "Create your Amazon account"
- "Forgot password?" link: `a#auth-fpp-link-bottom`

### Password Step
- Password input: `vijiram@16`
- Sign-In button: `input#signInSubmit` (type="submit", value="Sign-In")
- "Keep me signed in" checkbox: `input[name="rememberMe"]`
- "Forgot your password?" link: `a#auth-fpp-link-bottom`

### Error Messages
- Invalid email: `div.a-alert-content` containing "We cannot find an account with that email address"
- Wrong password: `div.a-alert-content` containing "Your password is incorrect"
- Empty email: `div.a-alert-content` containing "Enter your email or mobile phone number"
- Empty password: `div.a-alert-content` containing "Enter your password"

## Behaviour
- Login is a two-step flow: email first, then password on the next screen
- Successful login redirects to https://www.amazon.in
- After login, top nav shows "Hello, [name]" in `span#nav-link-accountList-nav-line-1`
- "Keep me signed in" persists the session across browser restarts
- After multiple failed attempts, a CAPTCHA may appear: `div#auth-captcha-image-container`
