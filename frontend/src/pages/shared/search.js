/**
 * Search Page Module
 *
 * Manages filter state and sort on the product search results page.
 * Applies filters via URL navigation (server-side filtering).
 *
 * Registered as Alpine data component: searchPage()
 *
 * @module pages/shared/search
 */

export function searchPage(initialQuery = '') {
  return {
    query: initialQuery,
    sort: '',
    loading: false,

    init() {
      const params = new URLSearchParams(window.location.search)
      this.query = params.get('q') || initialQuery
      this.sort  = params.get('sort') || ''
    },

    submit() {
      if (!this.query.trim()) return
      const params = new URLSearchParams({ q: this.query })
      if (this.sort) params.set('sort', this.sort)
      window.location.href = `/products/search/?${params}`
    },

    applySort(value) {
      this.sort = value
      const params = new URLSearchParams(window.location.search)
      params.set('sort', value)
      window.location.href = `${window.location.pathname}?${params}`
    },
  }
}
