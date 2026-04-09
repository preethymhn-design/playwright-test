import { test, expect } from '@playwright/test';

test.describe('Sauce Demo — Products', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('https://www.saucedemo.com/');
    await page.fill('#user-name', 'standard_user');
    await page.fill('#password', 'secret_sauce');
    await page.click('#login-button');
    await expect(page).toHaveURL('https://www.saucedemo.com/inventory.html');
  });

  test('Products page displays all items', async ({ page }) => {
    const products = page.locator('.inventory_item');
    await expect(products).toHaveCount(6);
    await expect(page.locator('.app_logo')).toContainText('Swag Labs');
  });

  test('Can add product to cart', async ({ page }) => {
    await page.click('[data-test="add-to-cart-sauce-labs-backpack"]');
    await expect(page.locator('.shopping_cart_badge')).toHaveText('1');
    await expect(page.locator('[data-test="remove-sauce-labs-backpack"]')).toBeVisible();
  });

  test('Can remove product from cart', async ({ page }) => {
    await page.click('[data-test="add-to-cart-sauce-labs-backpack"]');
    await expect(page.locator('.shopping_cart_badge')).toHaveText('1');
    await page.click('[data-test="remove-sauce-labs-backpack"]');
    await expect(page.locator('.shopping_cart_badge')).not.toBeVisible();
  });

  test('Can add multiple products to cart', async ({ page }) => {
    await page.click('[data-test="add-to-cart-sauce-labs-backpack"]');
    await page.click('[data-test="add-to-cart-sauce-labs-bike-light"]');
    await page.click('[data-test="add-to-cart-sauce-labs-bolt-t-shirt"]');
    await expect(page.locator('.shopping_cart_badge')).toHaveText('3');
  });

  test('Can sort products by name A to Z', async ({ page }) => {
    await page.selectOption('[data-test="product-sort-container"]', 'az');
    const firstProduct = page.locator('.inventory_item').first().locator('.inventory_item_name');
    await expect(firstProduct).toContainText('Sauce Labs Backpack');
  });

  test('Can sort products by name Z to A', async ({ page }) => {
    await page.selectOption('[data-test="product-sort-container"]', 'za');
    const firstProduct = page.locator('.inventory_item').first().locator('.inventory_item_name');
    await expect(firstProduct).toContainText('Test.allTheThings()');
  });

  test('Can sort products by price low to high', async ({ page }) => {
    await page.selectOption('[data-test="product-sort-container"]', 'lohi');
    const firstProduct = page.locator('.inventory_item').first().locator('.inventory_item_name');
    await expect(firstProduct).toContainText('Sauce Labs Onesie');
  });

  test('Can sort products by price high to low', async ({ page }) => {
    await page.selectOption('[data-test="product-sort-container"]', 'hilo');
    const firstProduct = page.locator('.inventory_item').first().locator('.inventory_item_name');
    await expect(firstProduct).toContainText('Sauce Labs Fleece Jacket');
  });

  test('Can navigate to product detail page', async ({ page }) => {
    await page.click('.inventory_item_name >> text=Sauce Labs Backpack');
    await expect(page).toHaveURL(/.*inventory-item\.html\?id=\d+/);
    await expect(page.locator('[data-test="inventory-item-name"]')).toContainText('Sauce Labs Backpack');
    await expect(page.locator('[data-test="inventory-item-price"]')).toContainText('$29.99');
  });

  test('Can add to cart from product detail page', async ({ page }) => {
    await page.click('.inventory_item_name >> text=Sauce Labs Backpack');
    await page.click('[data-test="add-to-cart"]');
    await expect(page.locator('.shopping_cart_badge')).toHaveText('1');
    await expect(page.locator('[data-test="remove"]')).toBeVisible();
  });

  test('Can navigate back from product detail page', async ({ page }) => {
    await page.click('.inventory_item_name >> text=Sauce Labs Backpack');
    await page.click('[data-test="back-to-products"]');
    await expect(page).toHaveURL('https://www.saucedemo.com/inventory.html');
  });

  test('Can logout from hamburger menu', async ({ page }) => {
    await page.click('#react-burger-menu-btn');
    await page.click('#logout_sidebar_link');
    await expect(page).toHaveURL('https://www.saucedemo.com/');
    await expect(page.locator('#login-button')).toBeVisible();
  });
});
