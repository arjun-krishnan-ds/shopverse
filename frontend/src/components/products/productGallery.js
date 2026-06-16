/**
 * Product Gallery Component
 *
 * Image gallery on the product detail page.
 * - Renders images from the first in-stock variant on load
 * - Supports thumbnail navigation, prev/next arrows, keyboard nav
 * - Supports click-to-zoom
 * - Exposes setImages() so variantSelector can swap images when
 *   the user picks a different variant
 *
 * Registered as Alpine data component: productGallery(variantsJson)
 *
 * @module components/products/productGallery
 */

export function productGallery(variantsJson = '[]') {
  return {
    images:      [],
    activeIndex: 0,
    zoomed:      false,

    // ── Init ──────────────────────────────────────────────────
    init() {
      let variants = []
      try {
        variants = JSON.parse(variantsJson || '[]')
      } catch (_) {
        variants = []
      }

      // Use the first in-stock variant's images, then any variant, then empty
      const first = variants.find((v) => v.stock > 0 && v.images?.length)
                 || variants.find((v) => v.images?.length)
                 || null

      this.images = first?.images || []
    },

    // ── Computed ──────────────────────────────────────────────

    get activeImage() {
      return this.images[this.activeIndex] || null
    },

    // ── Methods ───────────────────────────────────────────────

    select(i) {
      this.activeIndex = Math.max(0, Math.min(i, this.images.length - 1))
      this.zoomed = false
    },

    next() {
      if (!this.images.length) return
      this.activeIndex = (this.activeIndex + 1) % this.images.length
      this.zoomed = false
    },

    prev() {
      if (!this.images.length) return
      this.activeIndex = (this.activeIndex - 1 + this.images.length) % this.images.length
      this.zoomed = false
    },

    toggleZoom() {
      this.zoomed = !this.zoomed
    },

    onKeydown(e) {
      if (e.key === 'ArrowRight') { e.preventDefault(); this.next() }
      if (e.key === 'ArrowLeft')  { e.preventDefault(); this.prev() }
      if (e.key === 'Escape')     { this.zoomed = false }
    },

    /**
     * Called by variantSelector._syncGallery() when the user
     * picks a different variant.  Replaces the image set and resets to index 0.
     */
    setImages(newImages) {
      if (!newImages?.length) return
      this.images      = newImages
      this.activeIndex = 0
      this.zoomed      = false
    },
  }
}
