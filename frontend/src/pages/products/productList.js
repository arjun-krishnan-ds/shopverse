/**
 * Product List Page Module
 *
 * Handles AJAX infinite-scroll / load-more pagination
 * on the product listing page.
 *
 * Registered as Alpine data component: productList()
 *
 * @module pages/products/productList
 */

import Alpine from 'alpinejs'
import { getErrorMessage } from '../../api/client.js'

/**
 * productList component.
 *
 * Usage:
 *   <div x-data="productList()" x-init="init()">
 *
 * Relies on the server rendering the first page normally.
 * This handles subsequent pages via AJAX append.
 */
export function productList() {
  return {
    page: 1,
    hasNext: false,
    loading: false,
    error: '',
    observer: null,

    init() {
      // Read has_next from Django-rendered meta tag injected by template
      const meta = document.getElementById('js-has-next')

      this.hasNext = meta
        ? meta.dataset.value === 'true'
        : false

      this._setupIntersectionObserver()

      // Cleanup observer when page unloads
      window.addEventListener('beforeunload', () => {
        if (this.observer) {
          this.observer.disconnect()
        }
      })
    },

    async loadMore() {
      if (this.loading || !this.hasNext) return

      this.loading = true
      this.error = ''

      try {
        this.page++

        const url = new URL(window.location.href)
        url.searchParams.set('page', this.page)

        const res = await fetch(url.toString(), {
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
          },
        })

        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`)
        }

        const data = await res.json()

        const grid = document.getElementById('product-grid')

        if (grid && data.html) {
          const wrapper = document.createElement('div')
          wrapper.innerHTML = data.html

          while (wrapper.firstChild) {
            const node = wrapper.firstChild

            grid.appendChild(node)

            // Initialize Alpine on appended node
            Alpine.initTree(node)
          }
        }

        this.hasNext = !!data.has_next

        // Disconnect observer if no more pages
        if (!this.hasNext && this.observer) {
          this.observer.disconnect()
        }

      } catch (err) {
        this.page--

        this.error =
          getErrorMessage?.(err)
          || 'Failed to load more products. Please try again.'

        console.error('[ProductList] Load more failed:', err)

      } finally {
        this.loading = false
      }
    },

    _setupIntersectionObserver() {
      const sentinel = document.getElementById('load-more-sentinel')

      if (!sentinel) return

      this.observer = new IntersectionObserver(
        (entries) => {
          const entry = entries[0]

          if (entry?.isIntersecting) {
            this.loadMore()
          }
        },
        {
          rootMargin: '200px',
        }
      )

      this.observer.observe(sentinel)
    },
  }
}