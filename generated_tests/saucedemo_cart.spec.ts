import { test, expect } from '@playwright/test';

test.describe('Sauce Demo — Shopping Cart', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('https://www.saucedemo.com/');
    await page.fill('#user-name', 'standard_user');
    await page.fill('#password', 'secret_sauce');
    await page.click('#login-button');
    await expect(page).toHaveURL('https://www.saucedemo.com/inventory.html');
  });

  test('Can navigate to cart page', async ({ page }) => {
    await page.click('.shopping_cart_link');
    await expect(page).toHaveURL('https://www.saucedemo.com/cart.html');
    await expect(page.locator('.title')).toContainText('Your Cart');
  });

  test('Empty cart shows no items', async ({ page }) => {
    await page.click('.shopping_cart_link');
    const cartItems = page.locator('.cart_item');
    await expect(cartItems).toHaveCount(0);
  });

  test('Cart displays added items', async ({ page }) => {
    await page.click('[data-test="add-to-cart-sauce-labs-backpack"]');
    await page.click('[data-test="add-to-cart-sauce-labs-bike-light"]');
    await page.click('.shopping_cart_link');
    
    const cartItems = page.locator('.cart_item');
    await expect(cartItems).toHaveCount(2);
    await expect(page.locator('.inventory_item_name >> text=Sauce Labs Backpack')).toBeVisible();
    await expect(page.locator('.inventory_item_name >> text=Sauce Labs Bike Light')).toBeVisible();
  });

  test('Can remove item from cart', async ({ page }) => {
    await page.click('[data-test="add-to-cart-sauce-labs-backpack"]');
    await page.click('[data-test="add-to-cart-sauce-labs-bike-light"]');
    await page.click('.shopping_cart_link');
    
    await page.click('[data-test="remove-sauce-labs-backpack"]');
    const cartItems = page.locator('.cart_item');
    await expect(cartItems).toHaveCount(1);
    await expect(page.locator('.inventory_item_name >> text=Sauce Labs Bike Light')).toBeVisible();
  });

  test('Cart badge updates when removing items', async ({ page }) => {
    await page.click('[data-test="add-to-cart-sauce-labs-backpack"]');
    await page.click('[data-test="add-to-cart-sauce-labs-bike-light"]');
    await expect(page.locator('.shopping_cart_badge')).toHaveText('2');
    
    await page.click('.shopping_cart_link');
    await page.click('[data-test="remove-sauce-labs-backpack"]');
    await expect(page.locator('.shopping_cart_badge')).toHaveText('1');
  });

  test('Continue shopping returns to products page', async ({ page }) => {
    await page.click('.shopping_cart_link');
    await page.click('[data-test="continue-shopping"]');
    await expect(page).toHaveURL('https://www.saucedemo.com/inventory.html');
  });

  test('Can proceed to checkout with items', async ({ page }) => {
    await page.click('[data-test="add-to-cart-sauce-labs-backpack"]');
    await page.click('.shopping_cart_link');
    await page.click('[data-test="checkout"]');
    await expect(page).toHaveURL('https://www.saucedemo.com/checkout-step-one.html');
  });

  test('Cart persists items across navigation', async ({ page }) => {
    await page.click('[data-test="add-to-cart-sauce-labs-backpack"]');
    await page.click('.shopping_cart_link');
    await page.click('[data-test="continue-shopping"]');
    await page.click('.shopping_cart_link');
    
    const cartItems = page.locator('.cart_item');
    await expect(cartItems).toHaveCount(1);
  });

  test('Item details shown in cart', async ({ page }) => {
    await page.click('[data-test="add-to-cart-sauce-labs-backpack"]');
    await page.click('.shopping_cart_link');
    
    await expect(page.locator('.inventory_item_name >> text=Sauce Labs Backpack')).toBeVisible();
    await expect(page.locator('.inventory_item_price >> text=$29.99')).toBeVisible();
    await expect(page.locator('.cart_quantity >> text=1')).toBeVisible();
  });
});
