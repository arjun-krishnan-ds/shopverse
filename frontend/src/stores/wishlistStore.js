/**
 * Wishlist Store
 *
 * Global Alpine store for wishlist state.
 * Supports both guest (session) and authenticated users.
 *
 * @module stores/wishlistStore
 */

import { toggleWishlist } from '../api/wishlist.js'
import { getErrorMessage } from '../api/client.js'

export function registerWishlistStore(Alpine) {
  Alpine.store('wishlist', {
    // product IDs in wishlist — injected from Django context
    items: [],
    loading: false,
    error: null,

    get count() {
      return this.items.length
    },

    get isEmpty() {
      return this.items.length === 0
    },

    init(initialIds = []) {
      // Called from template with Django-rendered wishlist_product_ids
      this.items = initialIds.map(Number)
    },

    has(productId) {
      return this.items.includes(Number(productId))
    },

    async toggle(productId) {
      const id = Number(productId)
      try {
        this.loading = true
        const data = await toggleWishlist(id)
        if (data.in_wishlist) {
          if (!this.items.includes(id)) this.items.push(id)
        } else {
          this.items = this.items.filter((i) => i !== id)
        }
        return data
      } catch (err) {
        this.error = getErrorMessage(err)
        throw err
      } finally {
        this.loading = false
      }
    },

    clear() {
      this.items = []
    },
  })
}
