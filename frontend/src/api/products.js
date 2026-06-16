/**
 * Products API Service
 * 
 * Handles all product-related API calls:
 * - List with filters
 * - Detail views
 * - Search & autocomplete
 * - Quick view
 * 
 * @module api/products
 */

import { get, post } from './client'
import { API_ENDPOINTS } from './endpoints'

/**
 * Get products with filters and pagination
 * 
 * @param {object} filters - Filter options
 * @param {string} filters.q - Search query
 * @param {string} filters.category - Category slug
 * @param {string} filters.brand - Brand slug
 * @param {number} filters.min_price - Minimum price
 * @param {number} filters.max_price - Maximum price
 * @param {string} filters.sort - Sort option
 * @param {number} filters.rating - Minimum rating
 * @param {boolean} filters.in_stock - In stock only
 * @param {number} filters.page - Page number
 * @returns {Promise} Products list response
 */
export async function getProducts(filters = {}) {
  const params = new URLSearchParams()

  Object.entries(filters).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      params.append(key, value)
    }
  })

  const queryString = params.toString()
  const url = `${API_ENDPOINTS.PRODUCTS.api}?${queryString}`

  try {
    const response = await get(url, {
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
      },
    })
    return response.data
  } catch (error) {
    console.error('[Products] Failed to fetch products:', error)
    throw error
  }
}

/**
 * Get product by slug
 * 
 * @param {string} slug - Product slug
 * @returns {Promise} Product detail response
 */
export async function getProductBySlug(slug) {
  const url = API_ENDPOINTS.PRODUCTS.detail(slug)

  try {
    const response = await get(url)
    return response.data
  } catch (error) {
    console.error(`[Products] Failed to fetch product ${slug}:`, error)
    throw error
  }
}

/**
 * Search products with autocomplete
 * 
 * @param {string} query - Search query
 * @param {number} limit - Result limit
 * @returns {Promise} Search results
 */
export async function searchProducts(query, limit = 8) {
  const params = new URLSearchParams({ q: query })
  const url = `${API_ENDPOINTS.PRODUCTS.search}?${params}`

  try {
    const response = await get(url)
    return response.data.products || []
  } catch (error) {
    console.error('[Products] Search failed:', error)
    throw error
  }
}

/**
 * Get product quick view data
 * 
 * @param {number} productId - Product ID
 * @returns {Promise} Quick view data
 */
export async function getProductQuickview(productId) {
  const url = API_ENDPOINTS.PRODUCTS.quickview(productId)

  try {
    const response = await get(url)
    return response.data
  } catch (error) {
    console.error(`[Products] Quick view failed for ${productId}:`, error)
    throw error
  }
}

/**
 * Get products by category
 * 
 * @param {string} categorySlug - Category slug
 * @param {object} options - Filter options
 * @returns {Promise} Products list
 */
export async function getProductsByCategory(categorySlug, options = {}) {
  const filters = {
    category: categorySlug,
    ...options,
  }
  return getProducts(filters)
}

/**
 * Get products by brand
 * 
 * @param {string} brandSlug - Brand slug
 * @param {object} options - Filter options
 * @returns {Promise} Products list
 */
export async function getProductsByBrand(brandSlug, options = {}) {
  const filters = {
    brand: brandSlug,
    ...options,
  }
  return getProducts(filters)
}

/**
 * Get trending products
 * 
 * @param {number} limit - Number of products
 * @returns {Promise} Trending products
 */
export async function getTrendingProducts(limit = 8) {
  return getProducts({
    sort: 'popular',
    page: 1,
  })
}

/**
 * Get featured products
 * 
 * @param {number} limit - Number of products
 * @returns {Promise} Featured products
 */
export async function getFeaturedProducts(limit = 8) {
  return getProducts({
    sort: 'newest',
    page: 1,
  })
}

/**
 * Get products on sale
 * 
 * @param {number} limit - Number of products
 * @returns {Promise} Sale products
 */
export async function getSaleProducts(limit = 8) {
  return getProducts({
    sort: 'price_low',
    page: 1,
  })
}
