/**
 * Home Page Module
 *
 * Controls the hero banner auto-play slider and
 * any deferred initialisation specific to the home page.
 *
 * Registered as Alpine data component: heroSlider()
 *
 * @module pages/home/home
 */

/**
 * Hero banner slider.
 * Usage: <div x-data="heroSlider(totalSlides)">
 *
 * @param {number} total - number of banner slides
 * @param {number} [interval=5000] - autoplay delay in ms
 */
export function heroSlider(total = 1, interval = 5000) {
  return {
    total,
    current: 0,
    timer: null,

    init() {
      if (this.total > 1) this._startAutoplay()
    },

    destroy() {
      this._stopAutoplay()
    },

    next() {
      this.current = (this.current + 1) % this.total
      this._resetAutoplay()
    },

    prev() {
      this.current = (this.current - 1 + this.total) % this.total
      this._resetAutoplay()
    },

    goTo(index) {
      this.current = index
      this._resetAutoplay()
    },

    isActive(index) {
      return this.current === index
    },

    _startAutoplay() {
      this.timer = setInterval(() => this.next(), interval)
    },

    _stopAutoplay() {
      if (this.timer) { clearInterval(this.timer); this.timer = null }
    },

    _resetAutoplay() {
      this._stopAutoplay()
      this._startAutoplay()
    },
  }
}