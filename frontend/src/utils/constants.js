/**
 * Application Constants
 * 
 * Centralized constants for consistent values across the app.
 * 
 * @module utils/constants
 */

// =====================================================
// PAGINATION
// =====================================================
export const PAGINATION = {
  PRODUCTS_PER_PAGE: 12,
  REVIEWS_PER_PAGE: 5,
  ORDERS_PER_PAGE: 10,
  AUTOCOMPLETE_RESULTS: 8,
}

// =====================================================
// TIMEOUTS & DELAYS
// =====================================================
export const TIMING = {
  DEBOUNCE_SEARCH: 300,
  DEBOUNCE_FILTER: 500,
  TOAST_DURATION: 3000,
  MODAL_ANIMATION: 200,
  SKELETON_ANIMATION: 2000,
}

// =====================================================
// STOCK STATUS
// =====================================================
export const STOCK_STATUS = {
  IN_STOCK: 'in_stock',
  LOW_STOCK: 'low_stock',
  OUT_OF_STOCK: 'out_of_stock',
}

// =====================================================
// ORDER STATUS
// =====================================================
export const ORDER_STATUS = {
  PENDING: 'pending',
  PAID: 'paid',
  PROCESSING: 'processing',
  SHIPPED: 'shipped',
  OUT_FOR_DELIVERY: 'out_for_delivery',
  DELIVERED: 'delivered',
  CANCELLED: 'cancelled',
  REFUNDED: 'refunded',
}

// =====================================================
// PAYMENT METHODS
// =====================================================
export const PAYMENT_METHODS = {
  COD: 'cod',
  STRIPE: 'stripe',
  RAZORPAY: 'razorpay',
}

// =====================================================
// REVIEW RATINGS
// =====================================================
export const REVIEW_RATINGS = [
  { value: 5, label: 'Excellent' },
  { value: 4, label: 'Good' },
  { value: 3, label: 'Average' },
  { value: 2, label: 'Poor' },
  { value: 1, label: 'Terrible' },
]

// =====================================================
// SORTING OPTIONS
// =====================================================
export const SORT_OPTIONS = [
  { value: 'newest', label: 'Newest' },
  { value: 'price_low', label: 'Price: Low to High' },
  { value: 'price_high', label: 'Price: High to Low' },
  { value: 'rating', label: 'Best Rating' },
  { value: 'popular', label: 'Most Popular' },
]

// =====================================================
// VALIDATION
// =====================================================
export const VALIDATION = {
  MIN_PASSWORD_LENGTH: 8,
  MAX_PASSWORD_LENGTH: 128,
  
  PHONE_REGEX: /^\+?[\d\s\-()]{10,}$/,
  EMAIL_REGEX: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  POSTAL_CODE_REGEX: /^[0-9]{6}$/,
  
  PRODUCT_NAME_MIN: 3,
  PRODUCT_NAME_MAX: 255,
  
  REVIEW_TITLE_MIN: 5,
  REVIEW_TITLE_MAX: 255,
  REVIEW_COMMENT_MIN: 10,
  REVIEW_COMMENT_MAX: 5000,
  
  COUPON_CODE_MIN: 3,
  COUPON_CODE_MAX: 50,
}

// =====================================================
// LIMITS
// =====================================================
export const LIMITS = {
  MAX_IMAGES_PER_REVIEW: 5,
  MAX_FILE_SIZE_MB: 5,
  MAX_CART_ITEMS: 100,
  MAX_WISHLIST_ITEMS: 1000,
  MAX_RECENTLY_VIEWED: 20,
}

// =====================================================
// COLORS
// =====================================================
export const COLORS = {
  PRIMARY: '#8b5cf6',
  PRIMARY_DARK: '#7c3aed',
  SUCCESS: '#22c55e',
  WARNING: '#f59e0b',
  DANGER: '#ef4444',
  INFO: '#3b82f6',
  LIGHT: '#f3f4f6',
  DARK: '#111827',
}

// =====================================================
// BREAKPOINTS
// =====================================================
export const BREAKPOINTS = {
  XS: 320,
  SM: 640,
  MD: 768,
  LG: 1024,
  XL: 1280,
  '2XL': 1536,
}

// =====================================================
// LOCAL STORAGE KEYS
// =====================================================
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  USER_ID: 'user_id',
  RECENTLY_VIEWED: 'recently_viewed_products',
  CART_DRAFT: 'cart_draft',
  FILTERS_CACHE: 'product_filters',
  USER_PREFERENCES: 'user_preferences',
}

// =====================================================
// ERROR MESSAGES
// =====================================================
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  SERVER_ERROR: 'Server error. Please try again later.',
  NOT_FOUND: 'Requested resource not found.',
  UNAUTHORIZED: 'Please log in to continue.',
  FORBIDDEN: 'You do not have permission to access this.',
  VALIDATION_ERROR: 'Please check the form and try again.',
  PRODUCT_OUT_OF_STOCK: 'This product is out of stock.',
  INSUFFICIENT_STOCK: 'Not enough stock available.',
  INVALID_COUPON: 'Invalid coupon code.',
  EXPIRED_COUPON: 'This coupon has expired.',
}

// =====================================================
// SUCCESS MESSAGES
// =====================================================
export const SUCCESS_MESSAGES = {
  ADDED_TO_CART: 'Added to cart successfully.',
  REMOVED_FROM_CART: 'Removed from cart.',
  ADDED_TO_WISHLIST: 'Added to wishlist.',
  REMOVED_FROM_WISHLIST: 'Removed from wishlist.',
  ORDER_PLACED: 'Order placed successfully.',
  REVIEW_SUBMITTED: 'Review submitted. Thank you!',
  PROFILE_UPDATED: 'Profile updated successfully.',
  ADDRESS_ADDED: 'Address added successfully.',
  ADDRESS_UPDATED: 'Address updated successfully.',
  COUPON_APPLIED: 'Coupon applied successfully.',
}

// =====================================================
// CURRENCY
// =====================================================
export const CURRENCY = {
  SYMBOL: '₹',
  CODE: 'INR',
  DECIMAL_PLACES: 2,
  THOUSAND_SEPARATOR: ',',
  DECIMAL_SEPARATOR: '.',
}

// =====================================================
// REGEX PATTERNS
// =====================================================
export const PATTERNS = {
  SLUG: /^[a-z0-9]+(?:-[a-z0-9]+)*$/,
  HASHTAG: /^#[a-zA-Z0-9_]{1,139}$/,
  MENTION: /^@[a-zA-Z0-9_]{1,30}$/,
  URL: /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/,
}
