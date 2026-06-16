/**
 * Utility Helpers
 * 
 * Common utility functions used across the application.
 * 
 * @module utils/helpers
 */

/**
 * Delay execution for specified milliseconds
 * 
 * @param {number} ms - Milliseconds to delay
 * @returns {Promise}
 */
export function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * Throttle function execution
 * 
 * @param {Function} func - Function to throttle
 * @param {number} limit - Time limit in milliseconds
 * @returns {Function} Throttled function
 */
export function throttle(func, limit) {
  let inThrottle
  return function (...args) {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

/**
 * Debounce function execution
 * 
 * @param {Function} func - Function to debounce
 * @param {number} wait - Debounce delay in milliseconds
 * @returns {Function} Debounced function
 */
export function debounce(func, wait) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

/**
 * Check if element is in viewport
 * 
 * @param {Element} element - DOM element
 * @param {object} options - Intersection observer options
 * @returns {Promise<boolean>}
 */
export function isInViewport(element, options = {}) {
  return new Promise((resolve) => {
    if (!element) {
      resolve(false)
      return
    }

    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        resolve(true)
        observer.unobserve(element)
      }
    }, options)

    observer.observe(element)

    setTimeout(() => {
      observer.disconnect()
      resolve(false)
    }, 5000)
  })
}

/**
 * Get element height
 * 
 * @param {Element} element - DOM element
 * @returns {number} Height in pixels
 */
export function getHeight(element) {
  return element?.offsetHeight || 0
}

/**
 * Get element width
 * 
 * @param {Element} element - DOM element
 * @returns {number} Width in pixels
 */
export function getWidth(element) {
  return element?.offsetWidth || 0
}

/**
 * Get scroll position
 * 
 * @returns {object} Scroll position {x, y}
 */
export function getScrollPosition() {
  return {
    x: window.scrollX || window.pageXOffset,
    y: window.scrollY || window.pageYOffset,
  }
}

/**
 * Check if at bottom of page
 * 
 * @param {number} threshold - Pixels from bottom
 * @returns {boolean}
 */
export function isAtBottom(threshold = 100) {
  const scrollPosition = getScrollPosition().y
  const windowHeight = window.innerHeight
  const documentHeight = document.documentElement.scrollHeight

  return scrollPosition + windowHeight >= documentHeight - threshold
}

/**
 * Smooth scroll to element
 * 
 * @param {Element} element - Target element
 * @param {object} options - Scroll options
 */
export function smoothScroll(element, options = {}) {
  const {
    behavior = 'smooth',
    block = 'start',
    inline = 'nearest',
  } = options

  element?.scrollIntoView({
    behavior,
    block,
    inline,
  })
}

/**
 * Smooth scroll to top
 * 
 * @param {object} options - Scroll options
 */
export function scrollToTop(options = {}) {
  window.scrollTo({
    top: 0,
    behavior: options.behavior || 'smooth',
  })
}

/**
 * Copy text to clipboard
 * 
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>}
 */
export async function copyToClipboard(text) {
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text)
      return true
    } else {
      // Fallback for older browsers
      const textarea = document.createElement('textarea')
      textarea.value = text
      document.body.appendChild(textarea)
      textarea.select()
      document.execCommand('copy')
      document.body.removeChild(textarea)
      return true
    }
  } catch {
    return false
  }
}

/**
 * Get query parameter from URL
 * 
 * @param {string} param - Parameter name
 * @param {string} url - URL (defaults to current)
 * @returns {string|null} Parameter value
 */
export function getQueryParam(param, url = window.location.href) {
  const regex = new RegExp(`[?&]${param}=([^&#]*)`)
  const match = regex.exec(url)
  return match ? decodeURIComponent(match[1]) : null
}

/**
 * Set query parameter in URL
 * 
 * @param {string} key - Parameter key
 * @param {string} value - Parameter value
 * @returns {string} Updated URL
 */
export function setQueryParam(key, value) {
  const url = new URL(window.location)
  url.searchParams.set(key, value)
  return url.toString()
}

/**
 * Remove query parameter from URL
 * 
 * @param {string} key - Parameter key
 * @returns {string} Updated URL
 */
export function removeQueryParam(key) {
  const url = new URL(window.location)
  url.searchParams.delete(key)
  return url.toString()
}

/**
 * Build query string from object
 * 
 * @param {object} params - Parameters object
 * @returns {string} Query string
 */
export function buildQueryString(params) {
  const filtered = Object.entries(params).filter(
    ([, v]) => v !== null && v !== undefined && v !== ''
  )
  return new URLSearchParams(filtered).toString()
}

/**
 * Check if object is empty
 * 
 * @param {object} obj - Object to check
 * @returns {boolean}
 */
export function isEmpty(obj) {
  return Object.keys(obj).length === 0
}

/**
 * Deep clone object
 * 
 * @param {object} obj - Object to clone
 * @returns {object} Cloned object
 */
export function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') return obj
  if (obj instanceof Date) return new Date(obj.getTime())
  if (obj instanceof Array) return obj.map(item => deepClone(item))
  if (obj instanceof Object) {
    const clonedObj = {}
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = deepClone(obj[key])
      }
    }
    return clonedObj
  }
  return obj
}

/**
 * Merge objects deeply
 * 
 * @param {object} target - Target object
 * @param {object} source - Source object
 * @returns {object} Merged object
 */
export function deepMerge(target, source) {
  const output = { ...target }
  
  if (isObject(target) && isObject(source)) {
    Object.keys(source).forEach((key) => {
      if (isObject(source[key])) {
        if (!(key in target))
          Object.assign(output, { [key]: source[key] })
        else
          output[key] = deepMerge(target[key], source[key])
      } else {
        Object.assign(output, { [key]: source[key] })
      }
    })
  }
  
  return output
}

/**
 * Check if value is object
 * 
 * @param {*} item - Value to check
 * @returns {boolean}
 */
export function isObject(item) {
  return item && typeof item === 'object' && !Array.isArray(item)
}

/**
 * Wait for condition to be true
 * 
 * @param {Function} condition - Condition function
 * @param {number} timeout - Timeout in milliseconds
 * @param {number} interval - Check interval in milliseconds
 * @returns {Promise<boolean>}
 */
export async function waitFor(condition, timeout = 10000, interval = 100) {
  const startTime = Date.now()
  
  while (Date.now() - startTime < timeout) {
    if (condition()) {
      return true
    }
    await delay(interval)
  }
  
  return false
}

/**
 * Retry async function
 * 
 * @param {Function} func - Async function to retry
 * @param {number} attempts - Number of attempts
 * @param {number} delayMs - Delay between attempts
 * @returns {Promise}
 */
export async function retry(func, attempts = 3, delayMs = 1000) {
  for (let i = 0; i < attempts; i++) {
    try {
      return await func()
    } catch (error) {
      if (i === attempts - 1) throw error
      await delay(delayMs)
    }
  }
}
