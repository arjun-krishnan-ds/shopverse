/**
 * Search Overlay Component
 *
 * Full-screen search with autocomplete via /products/api/search/
 *
 * @module components/layout/searchOverlay
 */

import { searchProducts } from '../../api/products.js'
import { debounce } from '../../utils/helpers.js'

export function searchOverlay() {
  return {
    query: '',
    results: [],
    loading: false,
    focused: false,

    get isOpen() {
      return this.$store.ui.searchOpen
    },

    init() {
      this._search = debounce(async (q) => {
        if (q.length < 2) { this.results = []; return }
        try {
          this.loading = true
          this.results = await searchProducts(q)
        } catch (_) {
          this.results = []
        } finally {
          this.loading = false
        }
      }, 280)

      // Auto-focus input when overlay opens
      this.$watch('isOpen', (val) => {
        if (val) {
          this.$nextTick(() => this.$refs.searchInput?.focus())
        } else {
          this.query = ''
          this.results = []
        }
      })
    },

    onInput() {
      this._search(this.query)
    },

    close() {
      this.$store.ui.closeSearch()
    },

    submit() {
      if (!this.query.trim()) return
      window.location.href = `/products/search/?q=${encodeURIComponent(this.query)}`
    },
  }
}
