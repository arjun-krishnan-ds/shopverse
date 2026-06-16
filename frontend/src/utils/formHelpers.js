/**
 * Form Helpers Utility
 *
 * Client-side validation and form submission utilities.
 * Used by page modules and Alpine components.
 *
 * @module utils/formHelpers
 */

export function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

/**
 * Validate password and return strength score (0-5) + per-check results.
 */
export function validatePassword(password) {
  const checks = {
    length:    password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number:    /[0-9]/.test(password),
    special:   /[!@#$%^&*]/.test(password),
  }
  return {
    isValid:  Object.values(checks).every(Boolean),
    checks,
    strength: Object.values(checks).filter(Boolean).length,
  }
}

/**
 * Rule-based form validation.
 *
 * rules format:
 *   { email: [{ type: 'required' }, { type: 'email' }] }
 *
 * Supported types: required | email | minLength | maxLength | pattern | match
 */
export function validateForm(data, rules) {
  const errors = {}

  Object.entries(rules).forEach(([field, fieldRules]) => {
    const value = data[field]
    for (const rule of fieldRules) {
      if (rule.type === 'required' && (!value || String(value).trim() === '')) {
        errors[field] = rule.message ?? `${field} is required`; break
      }
      if (rule.type === 'email' && value && !isValidEmail(value)) {
        errors[field] = rule.message ?? `${field} must be a valid email`; break
      }
      if (rule.type === 'minLength' && value && value.length < rule.value) {
        errors[field] = rule.message ?? `${field} must be at least ${rule.value} characters`; break
      }
      if (rule.type === 'maxLength' && value && value.length > rule.value) {
        errors[field] = rule.message ?? `${field} must not exceed ${rule.value} characters`; break
      }
      if (rule.type === 'pattern' && value && !rule.value.test(value)) {
        errors[field] = rule.message ?? `${field} format is invalid`; break
      }
      if (rule.type === 'match' && value !== data[rule.value]) {
        errors[field] = rule.message ?? `${field} does not match`; break
      }
    }
  })

  return { hasErrors: Object.keys(errors).length > 0, errors }
}

/** Serialise a <form> element to a plain object. */
export function getFormData(formElement) {
  const obj = {}
  new FormData(formElement).forEach((value, key) => { obj[key] = value })
  return obj
}

/**
 * Mark a named field as invalid and inject an error message below it.
 * Idempotent — reuses existing `.field-error` element if present.
 */
export function displayFieldError(name, message) {
  const el = document.querySelector(`[name="${name}"]`)
  if (!el) return
  el.classList.add('border-danger-500')
  el.classList.remove('border-neutral-300')
  let err = el.parentElement.querySelector('.field-error')
  if (!err) {
    err = document.createElement('p')
    err.className = 'field-error text-xs text-danger-600 mt-1'
    el.insertAdjacentElement('afterend', err)
  }
  err.textContent = message
}

/** Clear a field's error state. */
export function clearFieldError(name) {
  const el = document.querySelector(`[name="${name}"]`)
  if (!el) return
  el.classList.remove('border-danger-500')
  el.classList.add('border-neutral-300')
  el.parentElement.querySelector('.field-error')?.remove()
}

export default {
  isValidEmail, validatePassword, validateForm,
  getFormData, displayFieldError, clearFieldError,
}
