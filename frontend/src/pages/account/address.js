/**
 * Address Page Module
 *
 * Handles address form validation and submission state.
 *
 * Registered as Alpine data component: addressForm()
 *
 * @module pages/account/address
 */

export function addressForm(editing = false) {
  return {
    editing,
    submitting: false,

    validatePhone(phone) {
      if (!phone) return true
      return /^\+?[\d\s\-()]{10,}$/.test(phone.trim())
    },

    validate(form) {
      const phone = form.querySelector('[name="phone"]')?.value

      if (!this.validatePhone(phone)) {
        this.$store.ui.error('Please enter a valid phone number.')
        return false
      }

      return true
    },

    handleSubmit(event) {
      const form = event.target

      if (!this.validate(form)) {
        event.preventDefault()
        return
      }

      this.submitting = true
    },
  }
}