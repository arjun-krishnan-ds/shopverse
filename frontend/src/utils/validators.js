/**
 * Validators
 * 
 * Functions to validate user input and data.
 * 
 * @module utils/validators
 */

import { VALIDATION, PATTERNS } from './constants'

// =====================================================
// STRING VALIDATORS
// =====================================================

/**
 * Validate email format
 * 
 * @param {string} email - Email to validate
 * @returns {boolean}
 */
export function isValidEmail(email) {
  if (!email || typeof email !== 'string') return false
  return PATTERNS.EMAIL_REGEX.test(email)
}

/**
 * Validate password strength
 * 
 * @param {string} password - Password to validate
 * @returns {object} Validation result
 */
export function validatePassword(password) {
  const errors = []

  if (!password) {
    errors.push('Password is required')
    return { valid: false, errors }
  }

  if (password.length < VALIDATION.MIN_PASSWORD_LENGTH) {
    errors.push(`Password must be at least ${VALIDATION.MIN_PASSWORD_LENGTH} characters`)
  }

  if (password.length > VALIDATION.MAX_PASSWORD_LENGTH) {
    errors.push(`Password must be no more than ${VALIDATION.MAX_PASSWORD_LENGTH} characters`)
  }

  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain lowercase letters')
  }

  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain uppercase letters')
  }

  if (!/[0-9]/.test(password)) {
    errors.push('Password must contain numbers')
  }

  if (!/[!@#$%^&*]/.test(password)) {
    errors.push('Password must contain special characters (!@#$%^&*)')
  }

  return {
    valid: errors.length === 0,
    errors,
  }
}

/**
 * Validate phone number
 * 
 * @param {string} phone - Phone number to validate
 * @returns {boolean}
 */
export function isValidPhone(phone) {
  if (!phone || typeof phone !== 'string') return false
  return PATTERNS.PHONE_REGEX.test(phone.replace(/\s/g, ''))
}

/**
 * Validate postal code
 * 
 * @param {string} postalCode - Postal code to validate
 * @returns {boolean}
 */
export function isValidPostalCode(postalCode) {
  if (!postalCode || typeof postalCode !== 'string') return false
  return PATTERNS.POSTAL_CODE_REGEX.test(postalCode.replace(/\s/g, ''))
}

/**
 * Validate URL
 * 
 * @param {string} url - URL to validate
 * @returns {boolean}
 */
export function isValidUrl(url) {
  if (!url || typeof url !== 'string') return false
  return PATTERNS.URL.test(url)
}

/**
 * Validate slug format
 * 
 * @param {string} slug - Slug to validate
 * @returns {boolean}
 */
export function isValidSlug(slug) {
  if (!slug || typeof slug !== 'string') return false
  return PATTERNS.SLUG.test(slug)
}

/**
 * Validate username
 * 
 * @param {string} username - Username to validate
 * @returns {boolean}
 */
export function isValidUsername(username) {
  if (!username || typeof username !== 'string') return false
  return /^[a-zA-Z0-9_-]{3,30}$/.test(username)
}

// =====================================================
// LENGTH VALIDATORS
// =====================================================

/**
 * Validate string length
 * 
 * @param {string} str - String to validate
 * @param {number} min - Minimum length
 * @param {number} max - Maximum length
 * @returns {boolean}
 */
export function isValidLength(str, min = 0, max = Infinity) {
  if (!str) return min === 0
  return str.length >= min && str.length <= max
}

/**
 * Validate minimum length
 * 
 * @param {string} str - String to validate
 * @param {number} min - Minimum length
 * @returns {boolean}
 */
export function isMinLength(str, min) {
  return str && str.length >= min
}

/**
 * Validate maximum length
 * 
 * @param {string} str - String to validate
 * @param {number} max - Maximum length
 * @returns {boolean}
 */
export function isMaxLength(str, max) {
  return !str || str.length <= max
}

// =====================================================
// NUMBER VALIDATORS
// =====================================================

/**
 * Check if value is a number
 * 
 * @param {*} value - Value to check
 * @returns {boolean}
 */
export function isNumber(value) {
  return typeof value === 'number' && !isNaN(value)
}

/**
 * Validate number range
 * 
 * @param {number} num - Number to validate
 * @param {number} min - Minimum value
 * @param {number} max - Maximum value
 * @returns {boolean}
 */
export function isInRange(num, min, max) {
  return isNumber(num) && num >= min && num <= max
}

/**
 * Validate positive number
 * 
 * @param {number} num - Number to validate
 * @returns {boolean}
 */
export function isPositive(num) {
  return isNumber(num) && num > 0
}

/**
 * Validate non-negative number
 * 
 * @param {number} num - Number to validate
 * @returns {boolean}
 */
export function isNonNegative(num) {
  return isNumber(num) && num >= 0
}

// =====================================================
// ARRAY VALIDATORS
// =====================================================

/**
 * Check if array is empty
 * 
 * @param {Array} arr - Array to check
 * @returns {boolean}
 */
export function isEmpty(arr) {
  return !Array.isArray(arr) || arr.length === 0
}

/**
 * Check if array has items
 * 
 * @param {Array} arr - Array to check
 * @returns {boolean}
 */
export function isNotEmpty(arr) {
  return Array.isArray(arr) && arr.length > 0
}

/**
 * Validate array length
 * 
 * @param {Array} arr - Array to validate
 * @param {number} min - Minimum items
 * @param {number} max - Maximum items
 * @returns {boolean}
 */
export function isValidArrayLength(arr, min = 0, max = Infinity) {
  if (!Array.isArray(arr)) return min === 0
  return arr.length >= min && arr.length <= max
}

// =====================================================
// FILE VALIDATORS
// =====================================================

/**
 * Validate file type
 * 
 * @param {File} file - File to validate
 * @param {string[]} allowedTypes - Allowed MIME types
 * @returns {boolean}
 */
export function isValidFileType(file, allowedTypes = []) {
  if (!file || !file.type) return false
  if (allowedTypes.length === 0) return true
  return allowedTypes.some(type => {
    if (type.includes('*')) {
      const [mainType] = type.split('/')
      const [fileMainType] = file.type.split('/')
      return mainType === fileMainType
    }
    return file.type === type
  })
}

/**
 * Validate file size
 * 
 * @param {File} file - File to validate
 * @param {number} maxSizeMB - Maximum size in MB
 * @returns {boolean}
 */
export function isValidFileSize(file, maxSizeMB = 5) {
  if (!file || !file.size) return false
  const maxSizeBytes = maxSizeMB * 1024 * 1024
  return file.size <= maxSizeBytes
}

/**
 * Validate image file
 * 
 * @param {File} file - File to validate
 * @returns {boolean}
 */
export function isValidImage(file) {
  const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  return isValidFileType(file, validTypes) && isValidFileSize(file, 5)
}

/**
 * Get file extension
 * 
 * @param {string} filename - Filename
 * @returns {string} Extension
 */
export function getFileExtension(filename) {
  if (!filename) return ''
  return filename.substring(filename.lastIndexOf('.') + 1).toLowerCase()
}

// =====================================================
// FORM VALIDATORS
// =====================================================

/**
 * Validate form data
 * 
 * @param {object} data - Form data
 * @param {object} rules - Validation rules
 * @returns {object} Validation errors
 */
export function validateForm(data, rules) {
  const errors = {}

  Object.entries(rules).forEach(([field, fieldRules]) => {
    const value = data[field]
    const fieldErrors = []

    if (fieldRules.required && !value) {
      fieldErrors.push(`${field} is required`)
    }

    if (fieldRules.email && !isValidEmail(value)) {
      fieldErrors.push(`${field} must be a valid email`)
    }

    if (fieldRules.minLength && !isMinLength(value, fieldRules.minLength)) {
      fieldErrors.push(`${field} must be at least ${fieldRules.minLength} characters`)
    }

    if (fieldRules.maxLength && !isMaxLength(value, fieldRules.maxLength)) {
      fieldErrors.push(`${field} must be no more than ${fieldRules.maxLength} characters`)
    }

    if (fieldRules.pattern && !fieldRules.pattern.test(value)) {
      fieldErrors.push(`${field} format is invalid`)
    }

    if (fieldRules.custom) {
      const customError = fieldRules.custom(value)
      if (customError) {
        fieldErrors.push(customError)
      }
    }

    if (fieldErrors.length > 0) {
      errors[field] = fieldErrors
    }
  })

  return errors
}

/**
 * Check if form has errors
 * 
 * @param {object} errors - Validation errors object
 * @returns {boolean}
 */
export function hasErrors(errors) {
  return Object.keys(errors).length > 0
}

/**
 * Get error message for field
 * 
 * @param {object} errors - Validation errors object
 * @param {string} field - Field name
 * @returns {string} Error message
 */
export function getFieldError(errors, field) {
  if (!errors[field] || errors[field].length === 0) return ''
  return errors[field][0]
}
