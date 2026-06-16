/**
 * Toast Container Component
 *
 * Renders the global toast notification stack from $store.ui.toasts.
 *
 * @module components/ui/toast
 */

export function toastContainer() {
  return {
    get toasts() {
      return this.$store.ui.toasts
    },

    dismiss(id) {
      this.$store.ui.removeToast(id)
    },

    iconFor(type) {
      const map = {
        success: '✓',
        error:   '✕',
        warning: '⚠',
        info:    'ℹ',
      }
      return map[type] || 'ℹ'
    },
  }
}
