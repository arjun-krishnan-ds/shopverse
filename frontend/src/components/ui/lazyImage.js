/**
 * Lazy Image Component
 *
 * Progressive image loading with blur-up transition.
 * Uses IntersectionObserver — no layout shift.
 *
 * Usage:
 *   <div x-data="lazyImage()">
 *     <img x-ref="image" data-src="/real.jpg" src="/placeholder.jpg"
 *          :class="loaded ? 'blur-none' : 'blur-sm'" class="transition-all duration-500">
 *   </div>
 *
 * @module components/ui/lazyImage
 */

export function lazyImage() {
  return {
    loaded: false,
    error:  false,

    init() {
      const img = this.$refs.image
      if (!img) return

      const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return
          const src = img.dataset.src
          if (!src) return

          img.src = src
          img.onload  = () => { this.loaded = true;  observer.unobserve(img) }
          img.onerror = () => { this.error  = true;  observer.unobserve(img) }
        })
      })

      observer.observe(img)
      this.$cleanup(() => observer.disconnect())
    },
  }
}
