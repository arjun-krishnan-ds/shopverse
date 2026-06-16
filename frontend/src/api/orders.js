/**
 * Orders API Service
 *
 * Handles all order-related API communication.
 *
 * @module api/orders
 */

import { get, post } from './client.js'
import { API_ENDPOINTS } from './endpoints.js'

/**
 * Fetch the authenticated user's order list.
 * @returns {Promise<object>}
 */
export async function getOrders() {
  const res = await get(API_ENDPOINTS.ORDERS.list)
  return res.data
}

/**
 * Fetch a single order by order number.
 * @param {string} orderNumber
 * @returns {Promise<object>}
 */
export async function getOrder(orderNumber) {
  const res = await get(API_ENDPOINTS.ORDERS.detail(orderNumber))
  return res.data
}

/**
 * Cancel an order by order number.
 * @param {string} orderNumber
 * @returns {Promise<object>}
 */
export async function cancelOrder(orderNumber) {
  const res = await post(API_ENDPOINTS.ORDERS.cancel(orderNumber), {})
  return res.data
}

/**
 * Get delivery fee estimate for a given cart total.
 * @param {number} cartTotal
 * @param {string} [pincode]
 * @returns {Promise<object>}
 */
export async function getDeliveryFee(cartTotal, pincode = '') {
  const params = new URLSearchParams({ cart_total: cartTotal, pincode })
  const res = await get(`${API_ENDPOINTS.DELIVERY.fee}?${params}`)
  return res.data
}
