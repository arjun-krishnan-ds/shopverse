/**
 * Navbar Component
 *
 * Handles mobile menu, sticky behaviour, and scroll detection.
 *
 * @module components/layout/navbar
 */

export function navbar() {
  return {
    scrolled: false,
    onScroll: null,

    init() {
      this.onScroll = () => {
        this.scrolled = window.scrollY > 60
      }

      // Initial state
      this.onScroll()

      window.addEventListener('scroll', this.onScroll, {
        passive: true,
      })
    },

    destroy() {
      if (this.onScroll) {
        window.removeEventListener('scroll', this.onScroll)
      }
    },

    get mobileMenuOpen() {
      return this.$store.ui.mobileMenuOpen
    },

    toggleMobileMenu() {
      this.$store.ui.toggleMobileMenu()
    },

    closeMobileMenu() {
      this.$store.ui.closeMobileMenu()
    },

    openSearch() {
      this.$store.ui.openSearch()
    },

    get cartCount() {
      return this.$store.cart.count
    },

    get wishlistCount() {
      return this.$store.wishlist.count
    },
  }
}