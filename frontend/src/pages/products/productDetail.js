/**
 * Product Detail Page Module
 *
 * Bridges variantSelector ↔ productGallery so image set
 * updates when the user picks a different variant.
 *
 * Also controls the sticky add-to-cart bar that appears
 * once the main CTA scrolls out of view.
 *
 * Registered as Alpine data component: productDetail()
 *
 * @module pages/products/productDetail
 */

export function productDetail() {
  return {
    stickyBarVisible: false,
    _observer: null,

    init() {
      this._watchCta()
    },

    destroy() {
      if (this._observer) this._observer.disconnect()
    },

    // Watch the primary "Add to Cart" button; show sticky bar when it leaves viewport
    _watchCta() {
      const cta = document.getElementById('primary-add-to-cart')
      if (!cta) return

      this._observer = new IntersectionObserver(
        ([entry]) => { this.stickyBarVisible = !entry.isIntersecting },
        { threshold: 0 }
      )
      this._observer.observe(cta)
      this.$cleanup(() => this._observer?.disconnect())
    },

    // Called from template when variant changes; pushes new images to gallery
    syncGallery(variantImages) {
      const gallery = Alpine.$data(document.getElementById('product-gallery'))
      if (gallery && typeof gallery.setImages === 'function') {
        gallery.setImages(variantImages)
      }
    },
  }
}
