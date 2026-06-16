/**
 * Cart Drawer Component
 *
 * Slide-over panel showing cart items.
 * Reads from $store.cart; exposes remove / update handlers.
 *
 * @module components/cart/cartDrawer
 */

export function cartDrawer() {
  return {
    get isOpen() {
      return this.$store.ui.cartDrawerOpen
    },

    get items() {
      return this.$store.cart.items
    },

    get subtotal() {
      return this.$store.cart.subtotal
    },

    get count() {
      return this.$store.cart.count
    },

    get loading() {
      return this.$store.cart.loading
    },

    get isEmpty() {
      return this.$store.cart.isEmpty
    },

    close() {
      this.$store.ui.closeCartDrawer()
    },

    async removeItem(itemId) {
      try {
        await this.$store.cart.remove(itemId)
        this.$store.ui.success('Item removed')
      } catch (_) {
        this.$store.ui.error('Could not remove item')
      }
    },

    async updateQty(itemId, qty) {
      if (qty < 1) { return this.removeItem(itemId) }
      try {
        await this.$store.cart.update(itemId, qty)
      } catch (_) {
        this.$store.ui.error('Could not update quantity')
      }
    },

    formatPrice(value) {
      return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 0,
      }).format(value)
    },
  }
}
