/**
 * Lazy Loading Utilities
 *
 * Call these once at app boot for non-Alpine images/videos/content.
 * Alpine-managed images should use the lazyImage component instead.
 *
 * @module utils/lazyLoading
 */

/** Lazy-load all img[data-src] with blur-up transition. */
export function setupImageLazyLoading(selector = 'img[data-src]') {
  const images = document.querySelectorAll(selector)
  if (!images.length) return null

  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return
      const img = entry.target
      img.src = img.dataset.src
      img.onload = () => { img.classList.remove('blur-sm'); img.classList.add('blur-none') }
      obs.unobserve(img)
    })
  })

  images.forEach((img) => observer.observe(img))
  return observer
}

/** Lazy-load video[data-src] elements. */
export function setupVideoLazyLoading(selector = 'video[data-src]') {
  const videos = document.querySelectorAll(selector)
  if (!videos.length) return null

  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return
      const video = entry.target
      video.src = video.dataset.src
      video.load()
      obs.unobserve(video)
    })
  })

  videos.forEach((v) => observer.observe(v))
  return observer
}

/**
 * Optimise a Cloudinary URL to a given display width.
 * Falls back to original URL for non-Cloudinary sources.
 */
export function getResponsiveImageUrl(baseUrl, width = null) {
  if (!baseUrl || !width) return baseUrl ?? null
  if (baseUrl.includes('cloudinary')) {
    return baseUrl.replace('/upload/', `/upload/w_${width},q_auto,f_auto/`)
  }
  return baseUrl
}

export default { setupImageLazyLoading, setupVideoLazyLoading, getResponsiveImageUrl }
