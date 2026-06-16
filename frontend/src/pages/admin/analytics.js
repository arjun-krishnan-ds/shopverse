/**
 * Analytics Dashboard Module
 *
 * Drives the admin analytics dashboard at /analytics/dashboard/.
 * Reads JSON injected by Django into <script type="application/json"> tags
 * to avoid unsafe template interpolation inside JS.
 *
 * Registered as Alpine data component: analyticsDashboard()
 *
 * @module pages/admin/analytics
 */

export function analyticsDashboard() {
  return {
    salesData: [],
    topProducts: [],

    // ── Lifecycle ──────────────────────────────────────────

    init() {
      this._parseSalesData()
      this._parseTopProducts()
    },

    // ── Parsers ────────────────────────────────────────────

    _parseSalesData() {
      try {
        const el = document.getElementById('analytics-daily-sales')
        if (el) {
          this.salesData = JSON.parse(el.textContent || '[]').map((d) => ({
            date:    d.date,
            revenue: parseFloat(d.revenue) || 0,
            orders:  parseInt(d.orders,  10) || 0,
          }))
        }
      } catch (e) {
        console.error('[Analytics] Failed to parse sales data:', e)
        this.salesData = []
      }
    },

    _parseTopProducts() {
      try {
        const el = document.getElementById('analytics-top-products')
        if (el) {
          this.topProducts = JSON.parse(el.textContent || '[]')
        }
      } catch (e) {
        console.error('[Analytics] Failed to parse product data:', e)
        this.topProducts = []
      }
    },

    // ── Computed ───────────────────────────────────────────

    get maxRevenue() {
      return Math.max(...this.salesData.map((d) => d.revenue), 1)
    },

    get maxOrders() {
      return Math.max(...this.salesData.map((d) => d.orders), 1)
    },

    get totalRevenue() {
      return Math.round(this.salesData.reduce((sum, d) => sum + d.revenue, 0))
    },

    get totalOrders() {
      return this.salesData.reduce((sum, d) => sum + d.orders, 0)
    },

    // ── Helpers for bar sizing (0–100 scale) ───────────────

    barHeight(revenue) {
      return Math.round((revenue / this.maxRevenue) * 100)
    },

    orderBarWidth(orders) {
      return Math.round((orders / this.maxOrders) * 100)
    },
  }
}