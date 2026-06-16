/**
 * API Endpoints Configuration
 * 
 * Centralized endpoint definitions for all backend services.
 * Ensures consistency across the application.
 * 
 * @module api/endpoints
 */

const BASE_URL = import.meta.env.VITE_API_URL || '/api'

export const API_ENDPOINTS = {
  // =====================================================
  // PRODUCTS
  // =====================================================
  PRODUCTS: {
    list: '/products/',
    detail: (slug) => `/products/${slug}/`,
    search: '/products/api/search/',
    quickview: (id) => `/products/quickview/${id}/`,
    api: '/products/api/',
  },

  // =====================================================
  // CART
  // =====================================================
  CART: {
    detail: '/cart/',
    json: '/cart/json/',
    add: (variantId) => `/cart/add/${variantId}/`,
    update: '/cart/update/',
    remove: '/cart/remove/',
  },

  // =====================================================
  // WISHLIST
  // =====================================================
  WISHLIST: {
    list: '/wishlist/',
    add: (productId) => `/wishlist/add/${productId}/`,
    remove: (productId) => `/wishlist/remove/${productId}/`,
    toggle: (productId) => `/wishlist/toggle/${productId}/`,
  },

  // =====================================================
  // ORDERS
  // =====================================================
  ORDERS: {
    list: '/orders/my-orders/',
    detail: (orderNumber) => `/orders/my-orders/${orderNumber}/`,
    checkout: '/orders/checkout/',
    success: '/orders/success/',
    cancel: (orderNumber) => `/orders/cancel/${orderNumber}/`,
    invoice: (orderId) => `/orders/invoice/${orderId}/`,
  },

  // =====================================================
  // PAYMENTS
  // =====================================================
  PAYMENTS: {
    webhook: '/payments/webhook/stripe/',
  },

  // =====================================================
  // REVIEWS
  // =====================================================
  REVIEWS: {
    submit: (productId) => `/reviews/submit/${productId}/`,
    vote: (reviewId) => `/reviews/vote/${reviewId}/`,
    filter: (productId) => `/reviews/filter/${productId}/`,
  },

  // =====================================================
  // DELIVERY
  // =====================================================
  DELIVERY: {
    fee: '/delivery/fee/',
  },

  // =====================================================
  // COUPONS
  // =====================================================
  COUPONS: {
    apply: '/coupons/apply-coupon/',
    remove: '/coupons/remove-coupon/',
  },

  // =====================================================
  // ACCOUNTS
  // =====================================================
  ACCOUNTS: {
    register: '/accounts/register/',
    login: '/accounts/login/',
    logout: '/accounts/logout/',
    dashboard: '/accounts/dashboard/',
    addresses: {
      list: '/accounts/addresses/',
      add: '/accounts/addresses/add/',
      edit: (id) => `/accounts/addresses/${id}/edit/`,
      delete: (id) => `/accounts/addresses/${id}/delete/`,
      setDefault: (id) => `/accounts/addresses/${id}/default/`,
    },
  },

  // =====================================================
  // CORE
  // =====================================================
  CORE: {
    home: '/',
  },
}

/**
 * Build full URL for API endpoint
 * 
 * @param {string} endpoint - API endpoint path
 * @returns {string} Full API URL
 */
export function getApiUrl(endpoint) {
  if (endpoint.startsWith('http')) {
    return endpoint
  }
  return `${BASE_URL}${endpoint}`
}

/**
 * Get absolute URL from relative path
 * 
 * @param {string} path - Relative path
 * @returns {string} Absolute URL
 */
export function getAbsoluteUrl(path) {
  if (path.startsWith('http')) {
    return path
  }
  
  const origin = window.location.origin
  return `${origin}${path}`
}
