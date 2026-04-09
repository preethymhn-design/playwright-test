import { test, expect } from '@playwright/test';

test.describe('Sauce Demo — Checkout', () => {
  test.beforeEach(async ({ page }) => {
    // Login and add item to cart before each test
    await page.goto('https://www.saucedemo.com/');
    await page.fill('#user-name', 'standard_user');
    await page.fill('#password', 'secret_sauce');
    await page.click('#login-button');
    await page.click('[data-test="add-to-cart-sauce-labs-backpack"]');
    await page.click('.shopping_cart_link');
    await page.click('[data-test="checkout"]');
  });

  test('Checkout step 1 displays form', async ({ page }) => {
    await expect(page).toHaveURL('https://www.saucedemo.com/checkout-step-one.html');
    await expect(page.locator('.title')).toContainText('Checkout: Your Information');
    await expect(page.locator('#first-name')).toBeVisible();
    await expect(page.locator('#last-name')).toBeVisible();
    await expect(page.locator('#postal-code')).toBeVisible();
  });

  test('Cannot continue without first name', async ({ page }) => {
    await page.fill('#last-name', 'Doe');
    await page.fill('#postal-code', '12345');
    await page.click('[data-test="continue"]');
    await expect(page.locator('[data-test="error"]')).toContainText('First Name is required');
  });

  test('Cannot continue without last name', async ({ page }) => {
    await page.fill('#first-name', 'John');
    await page.fill('#postal-code', '12345');
    await page.click('[data-test="continue"]');
    await expect(page.locator('[data-test="error"]')).toContainText('Last Name is required');
  });

  test('Cannot continue without postal code', async ({ page }) => {
    await page.fill('#first-name', 'John');
    await page.fill('#last-name', 'Doe');
    await page.click('[data-test="continue"]');
    await expect(page.locator('[data-test="error"]')).toContainText('Postal Code is required');
  });

  test('Can proceed to overview with valid information', async ({ page }) => {
    await page.fill('#first-name', 'John');
    await page.fill('#last-name', 'Doe');
    await page.fill('#postal-code', '12345');
    await page.click('[data-test="continue"]');
    await expect(page).toHaveURL('https://www.saucedemo.com/checkout-step-two.html');
    await expect(page.locator('.title')).toContainText('Checkout: Overview');
  });

  test('Cancel returns to cart', async ({ page }) => {
    await page.click('[data-test="cancel"]');
    await expect(page).toHaveURL('https://www.saucedemo.com/cart.html');
  });

  test('Overview displays order summary', async ({ page }) => {
    await page.fill('#first-name', 'John');
    await page.fill('#last-name', 'Doe');
    await page.fill('#postal-code', '12345');
    await page.click('[data-test="continue"]');
    
    await expect(page.locator('.inventory_item_name >> text=Sauce Labs Backpack')).toBeVisible();
    await expect(page.locator('.inventory_item_price >> text=$29.99')).toBeVisible();
    await expect(page.locator('.summary_subtotal_label')).toContainText('Item total: $29.99');
    await expect(page.locator('.summary_tax_label')).toContainText('Tax:');
    await expect(page.locator('[data-test="total-label"]')).toBeVisible();
  });

  test('Overview shows payment and shipping info', async ({ page }) => {
    await page.fill('#first-name', 'John');
    await page.fill('#last-name', 'Doe');
    await page.fill('#postal-code', '12345');
    await page.click('[data-test="continue"]');
    
    await expect(page.locator('[data-test="payment-info-label"]')).toContainText('Payment Information');
    await expect(page.locator('[data-test="shipping-info-label"]')).toContainText('Shipping Information');
  });

  test('Can complete checkout', async ({ page }) => {
    await page.fill('#first-name', 'John');
    await page.fill('#last-name', 'Doe');
    await page.fill('#postal-code', '12345');
    await page.click('[data-test="continue"]');
    await page.click('[data-test="finish"]');
    
    await expect(page).toHaveURL('https://www.saucedemo.com/checkout-complete.html');
    await expect(page.locator('.complete-header')).toContainText('Thank you for your order');
  });

  test('Checkout complete shows success message', async ({ page }) => {
    await page.fill('#first-name', 'John');
    await page.fill('#last-name', 'Doe');
    await page.fill('#postal-code', '12345');
    await page.click('[data-test="continue"]');
    await page.click('[data-test="finish"]');
    
    await expect(page.locator('.complete-header')).toBeVisible();
    await expect(page.locator('.complete-text')).toBeVisible();
    await expect(page.locator('[data-test="back-to-products"]')).toBeVisible();
  });

  test('Back home returns to products page', async ({ page }) => {
    await page.fill('#first-name', 'John');
    await page.fill('#last-name', 'Doe');
    await page.fill('#postal-code', '12345');
    await page.click('[data-test="continue"]');
    await page.click('[data-test="finish"]');
    await page.click('[data-test="back-to-products"]');
    
    await expect(page).toHaveURL('https://www.saucedemo.com/inventory.html');
  });

  test('Cart is cleared after checkout', async ({ page }) => {
    await page.fill('#first-name', 'John');
    await page.fill('#last-name', 'Doe');
    await page.fill('#postal-code', '12345');
    await page.click('[data-test="continue"]');
    await page.click('[data-test="finish"]');
    await page.click('[data-test="back-to-products"]');
    
    await expect(page.locator('.shopping_cart_badge')).not.toBeVisible();
  });

  test('Complete checkout flow with multiple items', async ({ page }) => {
    // Go back and add more items
    await page.click('[data-test="cancel"]');
    await page.click('[data-test="continue-shopping"]');
    await page.click('[data-test="add-to-cart-sauce-labs-bike-light"]');
    await page.click('[data-test="add-to-cart-sauce-labs-bolt-t-shirt"]');
    await page.click('.shopping_cart_link');
    await page.click('[data-test="checkout"]');
    
    await page.fill('#first-name', 'John');
    await page.fill('#last-name', 'Doe');
    await page.fill('#postal-code', '12345');
    await page.click('[data-test="continue"]');
    
    const cartItems = page.locator('.cart_item');
    await expect(cartItems).toHaveCount(3);
    
    await page.click('[data-test="finish"]');
    await expect(page).toHaveURL('https://www.saucedemo.com/checkout-complete.html');
  });
});
