/**
 * Coupon Form Component
 *
 * Applies / removes coupon codes during checkout.
 * Calls /coupon/apply-coupon/ and /coupon/remove-coupon/ endpoints.
 *
 * @module components/checkout/couponForm
 */

import { post } from '../../api/client.js'
import { API_ENDPOINTS } from '../../api/endpoints.js'

export function couponForm(initialCode = '', initialDiscount = 0) {
  return {
    code: initialCode,
    discount: Number(initialDiscount),
    applied: !!initialCode,
    loading: false,
    error: '',
    message: '',

    async apply() {
      if (!this.code.trim()) return
      this.error = ''
      this.message = ''
      try {
        this.loading = true
        const res = await post(API_ENDPOINTS.COUPONS.apply, { coupon_code: this.code })
        const data = res.data
        if (data.success) {
          this.applied = true
          this.discount = data.discount
          this.message = data.message
          this.$dispatch('coupon-applied', { discount: data.discount, code: this.code })
          this.$store.ui.success(data.message)
        } else {
          this.error = data.message
        }
      } catch (_) {
        this.error = 'Could not apply coupon. Try again.'
      } finally {
        this.loading = false
      }
    },

    async remove() {
      this.error = ''
      this.message = ''
      try {
        this.loading = true
        await post(API_ENDPOINTS.COUPONS.remove, {})
        this.applied = false
        this.discount = 0
        this.code = ''
        this.$dispatch('coupon-removed')
        this.$store.ui.info('Coupon removed')
      } catch (_) {
        this.error = 'Could not remove coupon.'
      } finally {
        this.loading = false
      }
    },
  }
}
