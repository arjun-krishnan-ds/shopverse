export function filterSidebar(initialFilters = {}) {
  return {
    filters: {
      category: initialFilters.category || '',
      brand: initialFilters.brand || '',
      min_price: initialFilters.min_price || '',
      max_price: initialFilters.max_price || '',
      sort: initialFilters.sort || '',
      rating: initialFilters.rating || '',
      in_stock: initialFilters.in_stock === true,
    },

    mobileOpen: false,

    sections: {
      sort: true,
      category: true,
      brand: true,
      price: true,
      rating: true,
      stock: true,
    },

    toggleMobile() {
      this.mobileOpen = !this.mobileOpen
    },

    closeMobile() {
      this.mobileOpen = false
    },

    toggleSection(section) {
      this.sections[section] = !this.sections[section]
    },

    apply() {
      const params = new URLSearchParams()

      Object.entries(this.filters).forEach(([key, value]) => {
        if (
          value !== '' &&
          value !== null &&
          value !== false &&
          value !== undefined
        ) {
          params.set(key, value)
        }
      })

      window.location.href = `/products/?${params.toString()}`
    },

    reset() {
      window.location.href = '/products/'
    },

    clearFilter(name) {
      if (name === 'in_stock') {
        this.filters.in_stock = false
      } else {
        this.filters[name] = ''
      }

      this.apply()
    },

    isActive(type, value) {
      return String(this.filters[type]) === String(value)
    },

    setPrice(min, max) {
      this.filters.min_price = min
      this.filters.max_price = max
      this.apply()
    },

    get activeFilterCount() {
      let count = 0

      if (this.filters.category) count++
      if (this.filters.brand) count++
      if (this.filters.min_price || this.filters.max_price) count++
      if (this.filters.rating) count++
      if (this.filters.in_stock) count++

      return count
    },
  }
}