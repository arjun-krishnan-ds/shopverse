/**
 * CSRF Token Management
 * 
 * Handles retrieval and attachment of Django CSRF tokens
 * to API requests for secure communication.
 * 
 * @module api/csrf
 */

/**
 * Get CSRF token from DOM or cookies
 * 
 * Priority:
 * 1. Hidden input element (fastest)
 * 2. Cookie (fallback)
 * 
 * @returns {string} CSRF token
 */
export function getCsrfToken() {
  // Try to get from hidden input first
  const csrfInput = document.querySelector('[name="csrfmiddlewaretoken"]')
  if (csrfInput?.value) {
    return csrfInput.value
  }

  // Fallback to cookie
  const csrfCookie = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
  
  if (csrfCookie) {
    return csrfCookie.split('=')[1]
  }

  return ''
}

/**
 * Get CSRF token for API calls
 * Includes fallback for missing tokens
 * 
 * @returns {string} CSRF token or empty string
 */
export function getApiCsrfToken() {
  const token = getCsrfToken()
  
  if (!token && __DEV__) {
    console.warn(
      'CSRF token not found. Make sure csrfmiddlewaretoken is included in templates.'
    )
  }

  return token
}
