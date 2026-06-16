/**
 * Review Form Component
 *
 * Handles star rating + comment submission for product reviews.
 * Submits to /reviews/submit/<product_id>/
 *
 * @module components/account/reviewForm
 */

import { postFormData } from '../../api/client.js'

export function reviewForm(productId) {
  return {
    productId,
    rating: 0,
    title: '',
    comment: '',
    files: [],
    submitting: false,
    submitted: false,
    error: '',

    setRating(value) {
      this.rating = Number(value)
    },

    onFileChange(event) {
      this.files = Array.from(event.target.files).slice(0, 5)
    },

    async submit() {
      if (!this.rating) { this.error = 'Please select a rating'; return }
      this.error = ''
      try {
        this.submitting = true
        const fd = new FormData()
        fd.append('rating', this.rating)
        fd.append('title', this.title)
        fd.append('comment', this.comment)
        this.files.forEach((f) => fd.append('media', f))

        const res = await postFormData(`/reviews/submit/${this.productId}/`, fd)
        if (res.data.success) {
          this.submitted = true
          this.$store.ui.success('Review submitted! It will appear after approval.')
        } else {
          this.error = res.data.error || 'Submission failed'
        }
      } catch (_) {
        this.error = 'Could not submit review. Please try again.'
      } finally {
        this.submitting = false
      }
    },
  }
}
