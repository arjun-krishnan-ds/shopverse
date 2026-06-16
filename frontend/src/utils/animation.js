/**
 * Animation Utilities
 *
 * Scroll-triggered animations and imperative animation helpers.
 * Called once at app boot via setupScrollAnimations().
 *
 * @module utils/animation
 */

/**
 * Wire IntersectionObserver to all [data-animate] elements.
 * Adds `animate-in` + `animate-{value}` classes when visible.
 */
export function setupScrollAnimations(selector = '[data-animate]') {
  const elements = document.querySelectorAll(selector)
  if (!elements.length) return null

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return
        const el        = entry.target
        const animation = el.dataset.animate
        el.classList.add('animate-in', `animate-${animation}`)
        observer.unobserve(el)
      })
    },
    { threshold: 0.15, rootMargin: '0px 0px -80px 0px' }
  )

  elements.forEach((el) => observer.observe(el))
  return observer
}

/** Fade an element in over `duration` ms. */
export function fadeIn(element, duration = 300) {
  element.style.opacity    = '0'
  element.style.transition = `opacity ${duration}ms ease-in-out`
  requestAnimationFrame(() => { element.style.opacity = '1' })
  return new Promise((resolve) => setTimeout(resolve, duration))
}

/** Slide an element in from left or right. */
export function slideIn(element, direction = 'left', duration = 300) {
  const offset = direction === 'left' ? '-40px' : '40px'
  element.style.transform  = `translateX(${offset})`
  element.style.opacity    = '0'
  element.style.transition = `transform ${duration}ms ease-out, opacity ${duration}ms ease-out`
  requestAnimationFrame(() => {
    element.style.transform = 'translateX(0)'
    element.style.opacity   = '1'
  })
  return new Promise((resolve) => setTimeout(resolve, duration))
}

/** Shake an element horizontally — useful for validation errors. */
export function shake(element, intensity = 8, duration = 400) {
  const start = Date.now()
  return new Promise((resolve) => {
    const animate = () => {
      const progress = (Date.now() - start) / duration
      if (progress < 1) {
        element.style.transform = `translateX(${Math.sin(progress * 20) * intensity * (1 - progress)}px)`
        requestAnimationFrame(animate)
      } else {
        element.style.transform = 'translateX(0)'
        resolve()
      }
    }
    animate()
  })
}

export default { setupScrollAnimations, fadeIn, slideIn, shake }
