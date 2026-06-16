/**
 * Variant Selector Component
 *
 * Manages attribute selection (Color, Size, etc.) on the product detail page.
 * Finds the matching variant, updates price/stock, syncs gallery images
 * when the user picks a different variant.
 *
 * Registered as Alpine data component: variantSelector(variantsJson)
 *
 * @module components/products/variantSelector
 */

export function variantSelector(variantsJson = '[]') {
  return {
    variants: [],
    selected: {},
    quantity: 1,
    adding: false,
    added: false,

    // ─────────────────────────────────────────────────────
    // INIT
    // ─────────────────────────────────────────────────────

    init() {
      try {
        this.variants = JSON.parse(variantsJson || '[]')
      } catch (_) {
        this.variants = []
      }

      if (!this.variants.length) return

      // Prefer first in-stock variant
      const first =
        this.variants.find((v) => v.stock > 0) ||
        this.variants[0]

      if (!first) return

      // Preselect attributes
      Object.entries(first.attributes || {}).forEach(
        ([key, attr]) => {
          this.selected[key] = attr?.value
        }
      )

      // Initial gallery sync
      this._syncVariantGallery(first)
    },

    // ─────────────────────────────────────────────────────
    // COMPUTED
    // ─────────────────────────────────────────────────────

    get attributeKeys() {
      const keys = new Set()

      this.variants.forEach((variant) => {
        Object.keys(variant.attributes || {}).forEach((key) => {
          keys.add(key)
        })
      })

      return [...keys]
    },

    valuesFor(key) {
      const seen = new Set()
      const result = []

      this.variants.forEach((variant) => {

        const attr = variant.attributes?.[key]

        if (!attr?.value) return

        if (seen.has(attr.value)) return

        seen.add(attr.value)

        result.push(attr)
      })

      return result
    },

    get currentVariant() {

      if (!this.variants.length) return null

      return (
        this.variants.find((variant) => {

          return Object.entries(this.selected).every(
            ([key, value]) => {
              return (
                variant.attributes?.[key]?.value === value
              )
            }
          )
        }) || null
      )
    },

    get price() {
      return (
        this.currentVariant?.price ??
        this.variants[0]?.price ??
        0
      )
    },

    get stock() {
      return this.currentVariant?.stock ?? 0
    },

    get inStock() {
      return this.stock > 0
    },

    // ─────────────────────────────────────────────────────
    // SELECTION
    // ─────────────────────────────────────────────────────

    select(key, value) {

      this.selected = {
        ...this.selected,
        [key]: value,
      }

      // Reset qty if needed
      if (!this.inStock) {
        this.quantity = 1
      }

      // Sync gallery
      if (this.currentVariant) {
        this._syncVariantGallery(this.currentVariant)
      }
    },

    isSelected(key, value) {
      return this.selected[key] === value
    },

    isAvailable(key, value) {

      return this.variants.some((variant) => {

        const attr = variant.attributes?.[key]

        if (!attr || attr.value !== value) {
          return false
        }

        const matches = Object.entries(this.selected)
          .every(([selectedKey, selectedValue]) => {

            if (selectedKey === key) {
              return true
            }

            return (
              variant.attributes?.[selectedKey]?.value ===
              selectedValue
            )
          })

        return matches && variant.stock > 0
      })
    },

    // ─────────────────────────────────────────────────────
    // QUANTITY
    // ─────────────────────────────────────────────────────

    decreaseQty() {
      if (this.quantity > 1) {
        this.quantity--
      }
    },

    increaseQty() {
      if (this.quantity < Math.min(this.stock, 10)) {
        this.quantity++
      }
    },

    // ─────────────────────────────────────────────────────
    // ADD TO CART
    // ─────────────────────────────────────────────────────

    async addToCart() {

      if (
        !this.currentVariant ||
        !this.inStock ||
        this.adding
      ) {
        return
      }

      try {

        this.adding = true

        await this.$store.cart.add(
          this.currentVariant.id,
          this.quantity
        )

        this.added = true

        this.$store.ui.success('Added to cart!')

        this.$store.ui.openCartDrawer()

        setTimeout(() => {
          this.added = false
        }, 2500)

      } catch (_) {

        this.$store.ui.error(
          'Could not add to cart'
        )

      } finally {

        this.adding = false
      }
    },

    // ─────────────────────────────────────────────────────
    // PRICE FORMAT
    // ─────────────────────────────────────────────────────

    formatPrice(val) {
      return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 0,
      }).format(val || 0)
    },

    // ─────────────────────────────────────────────────────
    // PRIVATE
    // ─────────────────────────────────────────────────────

    _syncVariantGallery(variant) {

      if (!variant) return

      const galleryEl =
        document.getElementById('product-gallery')

      if (!galleryEl || typeof Alpine === 'undefined') {
        return
      }

      const gallery = Alpine.$data(galleryEl)

      if (
        !gallery ||
        typeof gallery.setImages !== 'function'
      ) {
        return
      }

      // Variant-specific images
      if (
        Array.isArray(variant.images) &&
        variant.images.length
      ) {

        gallery.setImages(variant.images)

        return
      }

      // Fallback image
      if (variant.image) {

        gallery.setImages([
          {
            url: variant.image,
            alt: variant.name || '',
          },
        ])
      }
    },
  }
}