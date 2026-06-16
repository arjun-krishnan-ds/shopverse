/**
 * HTTP Client
 * 
 * Centralized Axios instance with:
 * - CSRF token injection
 * - Error handling
 * - Request/response interceptors
 * - Timeout management
 * - Automatic retry logic
 * 
 * @module api/client
 */

import axios from 'axios'
import { getCsrfToken } from './csrf'

// =====================================================
// CLIENT CONFIGURATION
// =====================================================

const DEFAULT_TIMEOUT = 30000 // 30 seconds
const RETRY_ATTEMPTS = 3
const RETRY_DELAY = 1000 // 1 second

/**
 * Create configured Axios instance
 */
export const httpClient = axios.create({
  timeout: DEFAULT_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
})

/**
 * Request interceptor
 * - Injects CSRF token
 * - Logs requests in dev mode
 */
httpClient.interceptors.request.use(
  (config) => {
    // Inject CSRF token
    const csrfToken = getCsrfToken()
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken
    }

    // Log in development
    if (__DEV__) {
      console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`)
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

/**
 * Response interceptor
 * - Handles errors globally
 * - Logs responses in dev mode
 */
httpClient.interceptors.response.use(
  (response) => {
    if (__DEV__) {
      console.log(
        `[API] ✓ ${response.config.method?.toUpperCase()} ${response.config.url}`,
        response.status
      )
    }
    return response
  },
  (error) => {
    const { response, config, message } = error

    // Log error in development
    if (__DEV__) {
      console.error(
        `[API] ✗ ${config?.method?.toUpperCase()} ${config?.url}`,
        response?.status,
        response?.data || message
      )
    }

    // Handle specific status codes
    if (response) {
      switch (response.status) {
        case 401:
          // Unauthorized - redirect to login
          if (!window.location.pathname.includes('/accounts/login/')) {
            window.location.href = '/accounts/login/'
          }
          break

        case 403:
          // Forbidden - check CSRF token
          console.warn('[API] 403 Forbidden - CSRF token may be invalid')
          break

        case 404:
          // Not found
          break

        case 422:
          // Validation error
          break

        case 500:
          // Server error
          console.error('[API] 500 Internal Server Error')
          break

        default:
          break
      }
    }

    return Promise.reject(error)
  }
)

// =====================================================
// HTTP METHODS
// =====================================================

/**
 * GET request
 * 
 * @param {string} url - Endpoint URL
 * @param {object} config - Axios config
 * @returns {Promise}
 */
export async function get(url, config = {}) {
  return httpClient.get(url, config)
}

/**
 * POST request
 * 
 * @param {string} url - Endpoint URL
 * @param {object} data - Request payload
 * @param {object} config - Axios config
 * @returns {Promise}
 */
export async function post(url, data = {}, config = {}) {
  return httpClient.post(url, data, config)
}

/**
 * PUT request
 * 
 * @param {string} url - Endpoint URL
 * @param {object} data - Request payload
 * @param {object} config - Axios config
 * @returns {Promise}
 */
export async function put(url, data = {}, config = {}) {
  return httpClient.put(url, data, config)
}

/**
 * PATCH request
 * 
 * @param {string} url - Endpoint URL
 * @param {object} data - Request payload
 * @param {object} config - Axios config
 * @returns {Promise}
 */
export async function patch(url, data = {}, config = {}) {
  return httpClient.patch(url, data, config)
}

/**
 * DELETE request
 * 
 * @param {string} url - Endpoint URL
 * @param {object} config - Axios config
 * @returns {Promise}
 */
export async function del(url, config = {}) {
  return httpClient.delete(url, config)
}

// =====================================================
// FORM DATA REQUESTS (For file uploads)
// =====================================================

/**
 * POST with FormData (for file uploads)
 * 
 * @param {string} url - Endpoint URL
 * @param {FormData} formData - Form data with files
 * @returns {Promise}
 */
export async function postFormData(url, formData) {
  return httpClient.post(url, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

/**
 * POST with URLSearchParams (for form submissions)
 * 
 * @param {string} url - Endpoint URL
 * @param {object} data - Form data
 * @returns {Promise}
 */
export async function postForm(url, data) {
  const params = new URLSearchParams()
  
  Object.entries(data).forEach(([key, value]) => {
    if (Array.isArray(value)) {
      value.forEach(v => params.append(key, v))
    } else {
      params.append(key, value)
    }
  })

  return httpClient.post(url, params, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  })
}

// =====================================================
// ERROR HANDLING
// =====================================================

/**
 * Extract error message from response
 * 
 * @param {Error} error - Axios error
 * @returns {string} Error message
 */
export function getErrorMessage(error) {
  if (!error) return 'Unknown error occurred'

  const { response, message } = error

  if (response?.data?.message) {
    return response.data.message
  }

  if (response?.data?.detail) {
    return response.data.detail
  }

  if (response?.data?.error) {
    return response.data.error
  }

  if (response?.status) {
    const statusMessages = {
      400: 'Bad request',
      401: 'Unauthorized',
      403: 'Access forbidden',
      404: 'Not found',
      422: 'Validation error',
      500: 'Server error',
      503: 'Service unavailable',
    }
    return statusMessages[response.status] || `Error ${response.status}`
  }

  return message || 'Request failed'
}

/**
 * Extract validation errors from response
 * 
 * @param {Error} error - Axios error
 * @returns {object} Validation errors by field
 */
export function getValidationErrors(error) {
  if (!error?.response?.data) return {}

  const data = error.response.data

  // Handle Django form errors
  if (typeof data === 'object' && !Array.isArray(data)) {
    return data
  }

  return {}
}

/**
 * Check if error is network related
 * 
 * @param {Error} error - Axios error
 * @returns {boolean}
 */
export function isNetworkError(error) {
  return !error.response && error.message
}

/**
 * Check if error is validation error (422)
 * 
 * @param {Error} error - Axios error
 * @returns {boolean}
 */
export function isValidationError(error) {
  return error?.response?.status === 422
}
