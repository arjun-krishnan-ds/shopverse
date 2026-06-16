/**
 * Cart API Service
 *
 * Handles all cart-related API calls.
 * Uses postForm (URLSearchParams) to match Django's
 * application/x-www-form-urlencoded views.
 *
 * @module api/cart
 */
 
import { get, postForm } from './client.js'
import { API_ENDPOINTS } from './endpoints.js'
 
/**
 * Get cart data (JSON endpoint for the cart drawer / store)
 */
export async function getCart() {
  try {
    const response = await get(API_ENDPOINTS.CART.json)
    return response.data
  } catch (error) {
    console.error('[Cart] Failed to fetch cart:', error)
    throw error
  }
}
 
/**
 * Add product variant to cart
 * @param {number} variantId
 * @param {number} quantity
 */
export async function addToCart(variantId, quantity = 1) {
  try {
    const response = await postForm(
      API_ENDPOINTS.CART.add(variantId),
      { quantity: Math.max(1, quantity) }
    )
    return response.data
  } catch (error) {
    console.error('[Cart] Failed to add to cart:', error)
    throw error
  }
}
 
/**
 * Update quantity of an existing cart item
 * @param {number} itemId
 * @param {number} quantity
 */
export async function updateCartItem(itemId, quantity) {
  try {
    const response = await postForm(
      API_ENDPOINTS.CART.update,
      { item_id: itemId, qty: Math.max(0, quantity) }
    )
    return response.data
  } catch (error) {
    console.error('[Cart] Failed to update cart item:', error)
    throw error
  }
}
 
/**
 * Remove an item from the cart
 * @param {number} itemId
 */
export async function removeFromCart(itemId) {
  try {
    const response = await postForm(
      API_ENDPOINTS.CART.remove,
      { item_id: itemId }
    )
    return response.data
  } catch (error) {
    console.error('[Cart] Failed to remove cart item:', error)
    throw error
  }
}
 
/**
 * Check if a variant is in the cart (local store check — no network)
 * @param {number} variantId
 * @returns {boolean}
 */
export function isInCart(variantId) {
  try {
    return Alpine.store('cart').hasVariant(variantId)
  } catch {
    return false
  }
}
 
/**
 * Get quantity of a variant in the cart (local store — no network)
 * @param {number} variantId
 * @returns {number}
 */
export function getCartQuantity(variantId) {
  try {
    return Alpine.store('cart').getQuantity(variantId)
  } catch {
    return 0
  }
}