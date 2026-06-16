/**
 * Address Selector Component
 *
 * Manages delivery address selection during checkout.
 *
 * @module components/checkout/addressSelector
 */

export function addressSelector(selectedId = null) {
  return {
    selectedId: selectedId ? Number(selectedId) : null,

    select(id) {
      this.selectedId = Number(id)
    },

    isSelected(id) {
      return this.selectedId === Number(id)
    },
  }
}
