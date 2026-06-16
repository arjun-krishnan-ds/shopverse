/**
 * Wishlist API Service
 * 
 * Handles all wishlist-related API calls:
 * - Toggle wishlist
 * - Get wishlist
 * - Add/remove items
 * 
 * @module api/wishlist
 */

import { post } from './client'
import { API_ENDPOINTS } from './endpoints'

/**
 * Toggle product in wishlist
 * 
 * @param {number} productId - Product ID
 * @returns {Promise} Response with in_wishlist status
 */
export async function toggleWishlist(productId) {
  const url = API_ENDPOINTS.WISHLIST.toggle(productId)

  try {
    const response = await post(url, {}, {
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
      },
    })
    return response.data
  } catch (error) {
    console.error('[Wishlist] Failed to toggle:', error)
    throw error
  }
}

/**
 * Add product to wishlist
 * 
 * @param {number} productId - Product ID
 * @returns {Promise} Response
 */
export async function addToWishlist(productId) {
  const url = API_ENDPOINTS.WISHLIST.toggle(productId)

  try {
    const response = await post(url, {})
    if (response.data.in_wishlist) {
      return response.data
    }
    
    // If not added, try POST again
    return await post(url, {})
  } catch (error) {
    console.error('[Wishlist] Failed to add:', error)
    throw error
  }
}

/**
 * Remove product from wishlist
 * 
 * @param {number} productId - Product ID
 * @returns {Promise} Response
 */
export async function removeFromWishlist(productId) {
  const url = API_ENDPOINTS.WISHLIST.toggle(productId)

  try {
    const response = await post(url, {})
    if (!response.data.in_wishlist) {
      return response.data
    }
    
    // If still in wishlist, try POST again
    return await post(url, {})
  } catch (error) {
    console.error('[Wishlist] Failed to remove:', error)
    throw error
  }
}

/**
 * Check if product is in wishlist
 * 
 * @param {number} productId - Product ID
 * @returns {Promise<boolean>}
 */
export async function isInWishlist(productId) {
  try {
    const wishlistStore = Alpine.store('wishlist')
    if (wishlistStore?.items) {
      return wishlistStore.items.includes(productId)
    }
    return false
  } catch {
    return false
  }
}

/**
 * Get wishlist item count
 * 
 * @returns {Promise<number>}
 */
export async function getWishlistCount() {
  try {
    const wishlistStore = Alpine.store('wishlist')
    return (wishlistStore?.items || []).length
  } catch {
    return 0
  }
}

/**
 * Get wishlist items
 * 
 * @returns {Promise<Array>}
 */
export async function getWishlistItems() {
  try {
    const wishlistStore = Alpine.store('wishlist')
    return wishlistStore?.items || []
  } catch {
    return []
  }
}

/**
 * Clear wishlist
 * 
 * Note: Implemented via local state management
 * Backend doesn't have dedicated endpoint
 * 
 * @returns {Promise}
 */
export async function clearWishlist() {
  try {
    const wishlistStore = Alpine.store('wishlist')
    if (wishlistStore) {
      wishlistStore.items = []
    }
    return { success: true }
  } catch (error) {
    console.error('[Wishlist] Failed to clear:', error)
    throw error
  }
}
