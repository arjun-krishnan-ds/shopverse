/**
 * Accounts API Service
 *
 * Handles authentication-adjacent API calls (addresses, profile).
 * Login/register/logout are standard Django form POSTs, not JSON.
 *
 * @module api/accounts
 */

import { get, post } from './client.js'
import { API_ENDPOINTS } from './endpoints.js'

/**
 * Fetch saved addresses for the current user.
 * @returns {Promise<object[]>}
 */
export async function getAddresses() {
  const res = await get(API_ENDPOINTS.ACCOUNTS.addresses.list)
  return res.data
}

/**
 * Set an address as the default.
 * @param {number} id
 * @returns {Promise<object>}
 */
export async function setDefaultAddress(id) {
  const res = await post(API_ENDPOINTS.ACCOUNTS.addresses.setDefault(id), {})
  return res.data
}

/**
 * Delete an address.
 * @param {number} id
 * @returns {Promise<object>}
 */
export async function deleteAddress(id) {
  const res = await post(API_ENDPOINTS.ACCOUNTS.addresses.delete(id), {})
  return res.data
}
