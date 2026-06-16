/**
 * Wishlist Toggle Component
 *
 * Standalone heart-button component for use anywhere on the page.
 *
 * @module components/products/wishlistToggle
 */

export function wishlistToggle(productId) {
  return {
    productId: Number(productId),
    loading: false,

    get active() {
      return this.$store.wishlist.has(this.productId)
    },

    async toggle() {
      if (this.loading) return
      try {
        this.loading = true
        await this.$store.wishlist.toggle(this.productId)
        this.$store.ui.success(
          this.active ? 'Added to wishlist' : 'Removed from wishlist'
        )
      } catch (_) {
        this.$store.ui.error('Could not update wishlist')
      } finally {
        this.loading = false
      }
    },
  }
}
