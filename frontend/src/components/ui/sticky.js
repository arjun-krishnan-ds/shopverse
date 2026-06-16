/**
 * Sticky Component
 *
 * Tracks scroll position and sets `isSticky` when past threshold.
 * Usage: <header x-data="sticky(60)">
 *
 * @module components/ui/sticky
 */

export function sticky(scrollThreshold = 100) {
  return {
    isSticky: false,
    scrollY: 0,

    init() {
      const onScroll = () => {
        this.scrollY  = window.scrollY
        this.isSticky = this.scrollY > scrollThreshold
      }
      window.addEventListener('scroll', onScroll, { passive: true })
      this.$cleanup(() => window.removeEventListener('scroll', onScroll))
    },
  }
}

/**
 * Back to Top Button
 *
 * Reveals a floating button once user scrolls past threshold.
 * Usage: <div x-data="backToTop(300)">
 *
 * @module components/ui/backToTop
 */
export function backToTop(scrollThreshold = 300) {
  return {
    visible: false,

    init() {
      const onScroll = () => {
        this.visible = window.scrollY > scrollThreshold
      }
      window.addEventListener('scroll', onScroll, { passive: true })
      this.$cleanup(() => window.removeEventListener('scroll', onScroll))
    },

    scrollToTop() {
      window.scrollTo({ top: 0, behavior: 'smooth' })
    },
  }
}
