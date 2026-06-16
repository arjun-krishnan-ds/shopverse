/**
 * Cart Store
 *
 * Global Alpine store for shopping cart state.
 * Syncs with backend on init and after mutations.
 *
 * @module stores/cartStore
 */

import { getCart, addToCart, updateCartItem, removeFromCart } from '../api/cart.js'
import { getErrorMessage } from '../api/client.js'

export function registerCartStore(Alpine) {
  Alpine.store('cart', {
    items: [],
    count: 0,
    subtotal: 0,
    loading: false,
    error: null,

    get isEmpty() {
      return this.items.length === 0
    },

    get total() {
      return this.subtotal
    },

    async init() {
      await this.refresh()
    },

    async refresh() {
      try {
        this.loading = true
        const data = await getCart()
        this.items = data.items || []
        this.subtotal = data.subtotal || 0
        this.count = this.items.reduce((sum, item) => sum + item.qty, 0)
      } catch (err) {
        this.error = getErrorMessage(err)
      } finally {
        this.loading = false
      }
    },

    async add(variantId, quantity = 1) {
      try {
        this.loading = true
        const data = await addToCart(variantId, quantity)
        this.count = data.cart_count || this.count
        this.subtotal = data.cart_subtotal || this.subtotal
        await this.refresh()
        return data
      } catch (err) {
        this.error = getErrorMessage(err)
        throw err
      } finally {
        this.loading = false
      }
    },

    async update(itemId, quantity) {
      try {
        this.loading = true
        const data = await updateCartItem(itemId, quantity)
        this.count = data.cart_count || 0
        this.subtotal = data.cart_subtotal || 0
        await this.refresh()
        return data
      } catch (err) {
        this.error = getErrorMessage(err)
        throw err
      } finally {
        this.loading = false
      }
    },

    async remove(itemId) {
      try {
        this.loading = true
        const data = await removeFromCart(itemId)
        this.count = data.cart_count || 0
        this.subtotal = data.cart_subtotal || 0
        await this.refresh()
        return data
      } catch (err) {
        this.error = getErrorMessage(err)
        throw err
      } finally {
        this.loading = false
      }
    },

    findItem(variantId) {
      return this.items.find((i) => i.variant_id === variantId) || null
    },

    hasVariant(variantId) {
      return this.items.some((i) => i.variant_id === variantId)
    },

    getQuantity(variantId) {
      const item = this.findItem(variantId)
      return item ? item.qty : 0
    },

    clear() {
      this.items = []
      this.count = 0
      this.subtotal = 0
    },
  })
}
