/**
 * Cart Page Module
 *
 * Manages the /cart/ page with fully reactive Alpine state.
 *
 * Key fix: Per-item totals and summary totals now derive from live
 * Alpine state (items array) instead of static Django-rendered HTML.
 * updateQuantity() now sends the correct POST key ("qty") that the
 * Django view expects.
 *
 * Registered as Alpine data component: cartPage()
 *
 * @module pages/cart/cart
 */

export function cartPage(initialSubtotal = 0, initialDiscount = 0) {
  return {
    // ── State ──────────────────────────────────────────────
    items: [],
    discount: Number(initialDiscount),
    loading: false,

    // ── Lifecycle ──────────────────────────────────────────

    /**
     * Parse the cart items JSON that the Django template embeds
     * in a <script type="application/json"> tag.
     * This gives us reactive state without an extra API round-trip.
     */
    initItems() {
      try {
        const el = document.getElementById('cart-items-data')
        if (el) {
          this.items = JSON.parse(el.textContent || '[]')
        }
      } catch (e) {
        console.error('[Cart] Failed to parse cart items JSON:', e)
        this.items = []
      }
    },

    // ── Computed totals ────────────────────────────────────

    /**
     * Live subtotal — derived from the reactive items array.
     * Updates instantly when qty changes, before the server responds.
     */
    get computedSubtotal() {
      return this.items.reduce((sum, item) => sum + item.price * item.qty, 0)
    },

    /**
     * Live total after discount.
     */
    get computedTotal() {
      return Math.max(0, this.computedSubtotal - this.discount)
    },

    // ── Quantity controls ──────────────────────────────────

    increaseQty(item) {
      item.qty++
      this._syncQty(item)
    },

    decreaseQty(item) {
      if (item.qty <= 1) return
      item.qty--
      this._syncQty(item)
    },

    /**
     * Persist the new quantity to the backend.
     *
     * BUG FIX: The Django view (update_cart_item_view) reads
     * request.POST.get("qty") — not "quantity". Previous code
     * sent "quantity" which caused the update to silently fail,
     * always defaulting to qty=1 server-side.
     */
    async _syncQty(item) {
      try {
        this.loading = true

        const csrfToken = document
          .querySelector('[name=csrfmiddlewaretoken]')
          ?.value || ''

        const response = await fetch('/cart/update/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
          },
          // ✅ FIXED: key must be "qty" to match Django view
          body: new URLSearchParams({
            item_id: item.id,
            qty: item.qty,       // was "quantity" — wrong key
          }),
        })

        const data = await response.json()

        if (!data.success) {
          console.error('[Cart] Update failed:', data)
          return
        }

        // Dispatch so navbar cart count badge stays in sync
        window.dispatchEvent(
          new CustomEvent('cart-updated', { detail: data })
        )

        // Refresh Alpine cart store so drawer count stays accurate
        if (window.Alpine?.store?.('cart')?.refresh) {
          window.Alpine.store('cart').refresh()
        }

      } catch (err) {
        console.error('[Cart] Sync quantity error:', err)
      } finally {
        this.loading = false
      }
    },

    // ── Remove item ────────────────────────────────────────

    async removeItem(itemId) {
      try {
        this.loading = true

        const csrfToken = document
          .querySelector('[name=csrfmiddlewaretoken]')
          ?.value || ''

        const response = await fetch('/cart/remove/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
          },
          body: new URLSearchParams({ item_id: itemId }),
        })

        const data = await response.json()

        if (!data.success) {
          console.error('[Cart] Remove failed:', data)
          return
        }

        // Remove from reactive items array — UI updates instantly
        this.items = this.items.filter((i) => i.id !== itemId)

        window.dispatchEvent(
          new CustomEvent('cart-updated', { detail: data })
        )

        // Refresh global cart store
        if (window.Alpine?.store?.('cart')?.refresh) {
          window.Alpine.store('cart').refresh()
        }

      } catch (err) {
        console.error('[Cart] Remove error:', err)
      } finally {
        this.loading = false
      }
    },

    // ── Formatting ─────────────────────────────────────────

    formatPrice(value) {
      return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0,
      }).format(value || 0)
    },
  }
}