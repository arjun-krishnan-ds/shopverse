/**
 * Formatters
 * 
 * Functions to format values for display.
 * 
 * @module utils/formatters
 */

import { CURRENCY } from './constants'


// =====================================================
// CURRENCY FORMATTING
// =====================================================

/**
 * Format price value
 * 
 * @param {number} price - Price to format
 * @param {object} options - Format options
 * @returns {string} Formatted price
 */
export function formatPrice(price, options = {}) {
  const {
    symbol = CURRENCY.SYMBOL,
    decimals = CURRENCY.DECIMAL_PLACES,
    separator = CURRENCY.THOUSAND_SEPARATOR,
  } = options

  if (!price && price !== 0) return symbol + '0'

  const formatted = new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: CURRENCY.CODE,
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(price)

  return formatted
}

/**
 * Format price range
 * 
 * @param {number} minPrice - Minimum price
 * @param {number} maxPrice - Maximum price
 * @returns {string} Formatted range
 */
export function formatPriceRange(minPrice, maxPrice) {
  return `${formatPrice(minPrice)} - ${formatPrice(maxPrice)}`
}

/**
 * Format discount percentage
 * 
 * @param {number} originalPrice - Original price
 * @param {number} discountedPrice - Discounted price
 * @returns {string} Discount percentage
 */
export function formatDiscount(originalPrice, discountedPrice) {
  if (originalPrice <= 0) return '0%'
  
  const discount = ((originalPrice - discountedPrice) / originalPrice) * 100
  return `${Math.round(discount)}%`
}

/**
 * Format discount amount
 * 
 * @param {number} originalPrice - Original price
 * @param {number} discountedPrice - Discounted price
 * @returns {string} Discount amount
 */
export function formatDiscountAmount(originalPrice, discountedPrice) {
  const amount = originalPrice - discountedPrice
  return formatPrice(Math.max(0, amount))
}

// =====================================================
// DATE FORMATTING
// =====================================================

/**
 * Format date
 * 
 * @param {Date|string|number} date - Date to format
 * @param {string} format - Format pattern
 * @returns {string} Formatted date
 */
export function formatDate(date) {
  try { return new Date(date).toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric' }) }
  catch { return '' }
}
/**
 * Format date as relative time
 * 
 * @param {Date|string|number} date - Date to format
 * @returns {string} Relative time
 */
export function formatRelativeTime(date) {
  try {
    const diff = Date.now() - new Date(date).getTime()
    const days = Math.floor(diff / 86400000)
    if (days === 0) return 'today'
    if (days === 1) return 'yesterday'
    return `${days} days ago`
  } catch { return '' }
}

/**
 * Format time
 * 
 * @param {Date|string|number} date - Date to format
 * @returns {string} Formatted time
 */
export function formatTime(date) {
  try {
    return formatDateFns(new Date(date), 'HH:mm')
  } catch {
    return ''
  }
}

/**
 * Format datetime
 * 
 * @param {Date|string|number} date - Date to format
 * @returns {string} Formatted datetime
 */
export function formatDateTime(date) {
  try {
    return formatDateFns(new Date(date), 'MMM d, yyyy HH:mm')
  } catch {
    return ''
  }
}

// =====================================================
// NUMBER FORMATTING
// =====================================================

/**
 * Format large number with suffix (K, M, B)
 * 
 * @param {number} num - Number to format
 * @returns {string} Formatted number
 */
export function formatCompactNumber(num) {
  if (!num || num === 0) return '0'
  
  const absNum = Math.abs(num)
  
  if (absNum >= 1e9) return (num / 1e9).toFixed(1) + 'B'
  if (absNum >= 1e6) return (num / 1e6).toFixed(1) + 'M'
  if (absNum >= 1e3) return (num / 1e3).toFixed(1) + 'K'
  
  return num.toString()
}

/**
 * Format number with thousand separator
 * 
 * @param {number} num - Number to format
 * @param {number} decimals - Decimal places
 * @returns {string} Formatted number
 */
export function formatNumber(num, decimals = 0) {
  return new Intl.NumberFormat('en-IN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(num)
}

/**
 * Format percentage
 * 
 * @param {number} value - Value
 * @param {number} decimals - Decimal places
 * @returns {string} Formatted percentage
 */
export function formatPercent(value, decimals = 1) {
  return `${formatNumber(value, decimals)}%`
}

// =====================================================
// TEXT FORMATTING
// =====================================================

/**
 * Capitalize first letter
 * 
 * @param {string} str - String to capitalize
 * @returns {string} Capitalized string
 */
export function capitalize(str) {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1)
}

/**
 * Capitalize all words
 * 
 * @param {string} str - String to capitalize
 * @returns {string} Title case string
 */
export function titleCase(str) {
  if (!str) return ''
  return str
    .split(/\s+/)
    .map(word => capitalize(word))
    .join(' ')
}

/**
 * Convert to uppercase
 * 
 * @param {string} str - String to convert
 * @returns {string} Uppercase string
 */
export function uppercase(str) {
  return str?.toUpperCase() || ''
}

/**
 * Convert to lowercase
 * 
 * @param {string} str - String to convert
 * @returns {string} Lowercase string
 */
export function lowercase(str) {
  return str?.toLowerCase() || ''
}

/**
 * Truncate text
 * 
 * @param {string} text - Text to truncate
 * @param {number} length - Max length
 * @param {string} suffix - Suffix (default '...')
 * @returns {string} Truncated text
 */
export function truncate(text, length = 100, suffix = '...') {
  if (!text || text.length <= length) return text
  return text.substring(0, length) + suffix
}

/**
 * Slugify text
 * 
 * @param {string} text - Text to slugify
 * @returns {string} Slug
 */
export function slugify(text) {
  if (!text) return ''
  
  return text
    .toString()
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-')
    .replace(/[^\w\-]/g, '')
    .replace(/\-\-+/g, '-')
}

/**
 * Highlightsearch term in text
 * 
 * @param {string} text - Text to highlight
 * @param {string} term - Search term
 * @returns {string} HTML with highlights
 */
export function highlight(text, term) {
  if (!text || !term) return text
  
  const regex = new RegExp(`(${term})`, 'gi')
  return text.replace(regex, '<mark>$1</mark>')
}

/**
 * Remove HTML tags
 * 
 * @param {string} html - HTML string
 * @returns {string} Plain text
 */
export function stripHtml(html) {
  if (!html) return ''
  
  const div = document.createElement('div')
  div.innerHTML = html
  return div.textContent || div.innerText || ''
}

/**
 * Escape HTML special characters
 * 
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
export function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;',
  }
  return text.replace(/[&<>"']/g, char => map[char])
}

/**
 * Format file size
 * 
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted size
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

/**
 * Format duration in seconds to readable format
 * 
 * @param {number} seconds - Duration in seconds
 * @returns {string} Formatted duration
 */
export function formatDuration(seconds) {
  if (!seconds || seconds <= 0) return '0s'
  
  const units = [
    { name: 'd', seconds: 86400 },
    { name: 'h', seconds: 3600 },
    { name: 'm', seconds: 60 },
    { name: 's', seconds: 1 },
  ]
  
  for (const unit of units) {
    if (seconds >= unit.seconds) {
      return Math.floor(seconds / unit.seconds) + unit.name
    }
  }
  
  return '0s'
}
