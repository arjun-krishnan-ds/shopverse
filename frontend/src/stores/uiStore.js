/**
 * UI Store
 *
 * Global Alpine store for application-wide UI state:
 * modals, toasts, loading overlay, mobile menu, search, theme.
 *
 * @module stores/uiStore
 */

let _toastId = 0

export function registerUiStore(Alpine) {
  Alpine.store('ui', {
    // ── Mobile menu ──────────────────────────────────────────
    mobileMenuOpen: false,

    openMobileMenu() { this.mobileMenuOpen = true },
    closeMobileMenu() { this.mobileMenuOpen = false },
    toggleMobileMenu() { this.mobileMenuOpen = !this.mobileMenuOpen },

    // ── Search overlay ────────────────────────────────────────
    searchOpen: false,

    openSearch() { this.searchOpen = true },
    closeSearch() { this.searchOpen = false },
    toggleSearch() { this.searchOpen = !this.searchOpen },

    // ── Cart drawer ───────────────────────────────────────────
    cartDrawerOpen: false,

    openCartDrawer() { this.cartDrawerOpen = true },
    closeCartDrawer() { this.cartDrawerOpen = false },
    toggleCartDrawer() { this.cartDrawerOpen = !this.cartDrawerOpen },

    // ── Modals ────────────────────────────────────────────────
    modals: {},

    openModal(name) { this.modals[name] = true },
    closeModal(name) { this.modals[name] = false },
    toggleModal(name) { this.modals[name] = !this.modals[name] },
    isModalOpen(name) { return !!this.modals[name] },

    // ── Toasts ────────────────────────────────────────────────
    toasts: [],

    toast(message, type = 'info', duration = 3500) {
      const id = ++_toastId
      this.toasts.push({ id, message, type })
      if (duration > 0) {
        setTimeout(() => this.removeToast(id), duration)
      }
      return id
    },

    success(message, duration) { return this.toast(message, 'success', duration) },
    error(message, duration)   { return this.toast(message, 'error', duration ?? 5000) },
    warning(message, duration) { return this.toast(message, 'warning', duration) },
    info(message, duration)    { return this.toast(message, 'info', duration) },

    removeToast(id) {
      this.toasts = this.toasts.filter((t) => t.id !== id)
    },

    clearToasts() { this.toasts = [] },

    // ── Loading overlay ───────────────────────────────────────
    loading: false,
    loadingMessage: '',

    startLoading(msg = '') { this.loading = true; this.loadingMessage = msg },
    stopLoading()          { this.loading = false; this.loadingMessage = '' },

    // ── Quick-view product id ─────────────────────────────────
    quickViewProductId: null,

    openQuickView(id) { this.quickViewProductId = id; this.openModal('quickView') },
    closeQuickView()  { this.closeModal('quickView'); this.quickViewProductId = null },
  })
}
