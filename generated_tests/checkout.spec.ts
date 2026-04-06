import { test, expect } from '@playwright/test';

test.describe('Checkout Flow', () => {
  test('Checkout starts at /cart and proceeds through /checkout/shipping, /checkout/payment, /checkout/review, then /order-confirmation', async ({ page }) => {
    await page.goto('/cart');
    await expect(page.locator('div.cart-item')).toBeVisible();
    await expect(page.locator('span.subtotal')).toBeVisible();
    await page.locator('button#checkout-btn').click();
    await expect(page.locator('div.shipping-form')).toBeVisible();
    await page.locator('input[name="fullName"]').fill('John Doe');
    await page.locator('input[name="addressLine1"]').fill('123 Main St');
    await page.locator('input[name="city"]').fill('Anytown');
    await page.locator('input[name="state"]').fill('CA');
    await page.locator('input[name="zip"]').fill('12345');
    await page.locator('input[name="country"]').fill('USA');
    await page.locator('button#continue-shipping').click();
    await expect(page.locator('div.payment-form')).toBeVisible();
    await page.locator('input[name="cardNumber"]').fill('4111111111111111');
    await page.locator('input[name="expiry"]').fill('12/25');
    await page.locator('input[name="cvv"]').fill('123');
    await page.locator('button#pay-now').click();
    await expect(page.locator('div.order-review')).toBeVisible();
    await page.locator('button#place-order').click();
    await expect(page.locator('div.order-confirmation')).toBeVisible();
    await expect(page.locator('span.order-number')).toBeVisible();
  });

  test('Empty cart shows "Your cart is empty" with a "Continue Shopping" link', async ({ page }) => {
    await page.goto('/cart');
    await expect(page.locator('div.cart-item')).not.toBeVisible();
    await expect(page.locator('span.subtotal')).not.toBeVisible();
    await expect(page.locator('div.empty-cart')).toBeVisible();
    await expect(page.locator('a.continue-shopping')).toBeVisible();
  });

  test('Invalid card shows "Invalid card number"', async ({ page }) => {
    await page.goto('/cart');
    await page.locator('button#checkout-btn').click();
    await page.locator('div.shipping-form').waitFor();
    await page.locator('button#continue-shipping').click();
    await page.locator('div.payment-form').waitFor();
    await page.locator('input[name="cardNumber"]').fill('1234567890123456');
    await page.locator('button#pay-now').click();
    await expect(page.locator('div.error-message')).toBeVisible();
    await expect(page.locator('div.error-message')).toHaveText('Invalid card number');
  });

  test('Expired card shows "Card has expired"', async ({ page }) => {
    await page.goto('/cart');
    await page.locator('button#checkout-btn').click();
    await page.locator('div.shipping-form').waitFor();
    await page.locator('button#continue-shipping').click();
    await page.locator('div.payment-form').waitFor();
    await page.locator('input[name="cardNumber"]').fill('4111111111111111');
    await page.locator('input[name="expiry"]').fill('02/25');
    await page.locator('button#pay-now').click();
    await expect(page.locator('div.error-message')).toBeVisible();
    await expect(page.locator('div.error-message')).toHaveText('Card has expired');
  });

  test('Login and checkout', async ({ page }) => {
    await page.goto('/login');
    await page.locator('input[name="email"]').fill('john.doe@example.com');
    await page.locator('input[name="password"]').fill('password123');
    await page.locator('button[type="submit"]').click();
    await expect(page.locator('div.shipping-form')).toBeVisible();
    await page.locator('button#continue-shipping').click();
    await expect(page.locator('div.payment-form')).toBeVisible();
    await page.locator('input[name="cardNumber"]').fill('4111111111111111');
    await page.locator('input[name="expiry"]').fill('12/25');
    await page.locator('input[name="cvv"]').fill('123');
    await page.locator('button#pay-now').click();
    await expect(page.locator('div.order-review')).toBeVisible();
    await page.locator('button#place-order').click();
    await expect(page.locator('div.order-confirmation')).toBeVisible();
    await expect(page.locator('span.order-number')).toBeVisible();
  });
});