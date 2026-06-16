/**
 * Carousel Component
 *
 * Touch-enabled carousel for product galleries and sliders.
 * Auto-plays by default, pauses on interaction.
 *
 * @module components/ui/carousel
 */

export function carousel(autoplay = true, autoplaySpeed = 5000) {
  return {
    current: 0,
    autoplayEnabled: autoplay,
    autoplaySpeed,
    autoplayInterval: null,
    slides: [],

    init() {
      this.slides = this.$el.querySelectorAll('[data-slide]')
      if (this.autoplayEnabled) this.startAutoplay()
    },

    goToSlide(index) {
      this.current = Math.max(0, Math.min(index, this.slides.length - 1))
      this.resetAutoplay()
    },

    next() {
      this.current = this.current < this.slides.length - 1 ? this.current + 1 : 0
      this.resetAutoplay()
    },

    prev() {
      this.current = this.current > 0 ? this.current - 1 : this.slides.length - 1
      this.resetAutoplay()
    },

    startAutoplay() {
      if (!this.autoplayEnabled) return
      this.autoplayInterval = setInterval(() => this.next(), this.autoplaySpeed)
    },

    stopAutoplay() {
      if (this.autoplayInterval) { clearInterval(this.autoplayInterval); this.autoplayInterval = null }
    },

    resetAutoplay() {
      this.stopAutoplay()
      if (this.autoplayEnabled) this.startAutoplay()
    },

    get hasPrev()     { return this.current > 0 },
    get hasNext()     { return this.current < this.slides.length - 1 },
    get totalSlides() { return this.slides.length },
  }
}
