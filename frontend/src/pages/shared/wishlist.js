/**
 * Wishlist Page Module
 *
 * Handles the wishlist page: optimistic removal and
 * the "Move all to cart" bulk action.
 *
 * Registered as Alpine data component: wishlistPage()
 *
 * @module pages/shared/wishlist
 */

import { addToCart } from '../../api/cart.js'
import { getErrorMessage } from '../../api/client.js'

export function wishlistPage() {
  return {
    movingAll: false,

    /**
     * Move all in-stock wishlist items to cart.
     * Reads variant IDs from data attributes on the page.
     */
    async moveAllToCart() {
      const buttons = document.querySelectorAll('[data-add-variant]')
      if (!buttons.length) return

      this.movingAll = true
      let added = 0

      for (const btn of buttons) {
        const variantId = btn.dataset.addVariant
        if (!variantId) continue
        try {
          await addToCart(Number(variantId), 1)
          added++
        } catch (_) {
          // Skip items that fail (out of stock, etc.)
        }
      }

      if (added > 0) {
        await this.$store.cart.refresh()
        this.$store.ui.success(`${added} item${added > 1 ? 's' : ''} added to cart`)
        this.$store.ui.openCartDrawer()
      } else {
        this.$store.ui.error('No items could be added to cart')
      }

      this.movingAll = false
    },
  }
}
