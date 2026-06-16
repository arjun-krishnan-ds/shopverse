/**
 * Product Card Component
 *
 * Used on product grids across home, list, and recommendation sections.
 * Receives product data via x-data attribute from Django template.
 *
 * @module components/products/productCard
 */

export function productCard(productData = {}) {
  return {
    product: productData,
    selectedVariantId: null,
    adding: false,
    added: false,

    init() {
      // Pre-select the first active in-stock variant
      const variants = this.product.variants || []
      const inStock = variants.find((v) => v.stock > 0)
      this.selectedVariantId = inStock ? inStock.id : (variants[0]?.id ?? null)
    },

    get isInWishlist() {
      return this.$store.wishlist.has(this.product.id)
    },

    get currentVariant() {
      const variants = this.product.variants || []
      return variants.find((v) => v.id === this.selectedVariantId) || variants[0] || null
    },

    get price() {
      return this.currentVariant?.price ?? this.product.price ?? 0
    },

    get inStock() {
      return (this.currentVariant?.stock ?? 0) > 0
    },

    async addToCart() {
      if (!this.selectedVariantId || !this.inStock || this.adding) return
      try {
        this.adding = true
        await this.$store.cart.add(this.selectedVariantId, 1)
        this.added = true
        this.$store.ui.success('Added to cart')
        this.$store.ui.openCartDrawer()
        setTimeout(() => { this.added = false }, 2000)
      } catch (_) {
        this.$store.ui.error('Could not add to cart')
      } finally {
        this.adding = false
      }
    },

    async toggleWishlist() {
      try {
        await this.$store.wishlist.toggle(this.product.id)
        const inWl = this.$store.wishlist.has(this.product.id)
        this.$store.ui.success(inWl ? 'Added to wishlist' : 'Removed from wishlist')
      } catch (_) {
        this.$store.ui.error('Could not update wishlist')
      }
    },

    openQuickView() {
      this.$store.ui.openQuickView(this.product.id)
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
