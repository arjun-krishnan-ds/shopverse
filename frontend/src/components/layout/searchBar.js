/**
 * Search Bar Component
 *
 * Inline search bar used on product list / header area.
 * Debounces autocomplete calls.
 *
 * @module components/layout/searchBar
 */

import { searchProducts } from '../../api/products.js'
import { debounce } from '../../utils/helpers.js'

export function searchBar() {
  return {
    query: '',
    results: [],
    loading: false,
    showDropdown: false,

    init() {
      this._search = debounce(async (q) => {
        if (q.length < 2) { this.results = []; this.showDropdown = false; return }
        try {
          this.loading = true
          this.results = await searchProducts(q)
          this.showDropdown = this.results.length > 0
        } catch (_) {
          this.results = []
        } finally {
          this.loading = false
        }
      }, 280)
    },

    onInput() {
      this._search(this.query)
    },

    select(slug) {
      window.location.href = `/products/${slug}/`
    },

    dismiss() {
      this.showDropdown = false
    },

    submit() {
      if (!this.query.trim()) return
      window.location.href = `/products/search/?q=${encodeURIComponent(this.query)}`
    },
  }
}
