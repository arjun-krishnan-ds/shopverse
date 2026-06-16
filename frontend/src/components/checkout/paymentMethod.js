/**
 * Payment Method Component
 *
 * Manages payment method selection (COD / Stripe).
 *
 * @module components/checkout/paymentMethod
 */

export function paymentMethod(initial = 'cod') {
  return {
    selected: initial,

    select(method) {
      this.selected = method
    },

    get isCod() { return this.selected === 'cod' },
    get isStripe() { return this.selected === 'stripe' },
  }
}
