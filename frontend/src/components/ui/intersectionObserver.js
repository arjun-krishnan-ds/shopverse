/**
 * Intersection Observer Component
 *
 * Generic scroll-triggered visibility tracker.
 * Dispatches 'visible' event when element enters viewport.
 *
 * Usage:
 *   <section x-data="intersectionObserver({ once: true })"
 *            :class="isVisible ? 'opacity-100' : 'opacity-0'"
 *            class="transition-opacity duration-700">
 *
 * @module components/ui/intersectionObserver
 */

export function intersectionObserver(options = {}) {
  return {
    isVisible:      false,
    hasBeenVisible: false,

    init() {
      const opts = { threshold: 0.1, rootMargin: '0px', ...options }

      const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            this.isVisible      = true
            this.hasBeenVisible = true
            this.$dispatch('visible')
            if (options.once) observer.unobserve(entry.target)
          } else {
            if (!options.once) this.isVisible = false
          }
        })
      }, opts)

      observer.observe(this.$el)
      this.$cleanup(() => observer.disconnect())
    },
  }
}
