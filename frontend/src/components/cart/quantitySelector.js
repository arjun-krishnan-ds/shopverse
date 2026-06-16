/**
 * Quantity Selector Component
 *
 * Reusable +/- quantity input.
 * Props: initial, min, max, cartItemId (optional for cart updates)
 *
 * @module components/cart/quantitySelector
 */

export function quantitySelector(initial = 1, min = 1, max = 99, cartItemId = null) {
  return {
    qty: Number(initial),
    min: Number(min),
    max: Number(max),
    cartItemId,
    updating: false,

    get canDecrease() { return this.qty > this.min },
    get canIncrease() { return this.qty < this.max },

    decrease() {
      if (this.canDecrease) {
        this.qty--
        this._syncCart()
      }
    },

    increase() {
      if (this.canIncrease) {
        this.qty++
        this._syncCart()
      }
    },

    set(value) {
      const n = Math.max(this.min, Math.min(this.max, Number(value)))
      this.qty = isNaN(n) ? this.min : n
      this._syncCart()
    },

    async _syncCart() {
      if (!this.cartItemId) return
      try {
        this.updating = true
        await this.$store.cart.update(this.cartItemId, this.qty)
      } catch (_) {
        this.$store.ui.error('Could not update quantity')
      } finally {
        this.updating = false
      }
    },
  }
}
