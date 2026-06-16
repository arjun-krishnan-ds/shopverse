/**
 * Application Entry Point
 *
 * Bootstraps Alpine.js with all global stores,
 * reusable components, and page-level modules.
 * No business logic lives here — only wiring.
 *
 * @module main
 */

import Alpine from 'alpinejs'
import './styles/main.css'

// ── Stores ────────────────────────────────────────────────────
import { registerCartStore } from './stores/cartStore.js'
import { registerWishlistStore } from './stores/wishlistStore.js'
import { registerUiStore } from './stores/uiStore.js'

// ── Layout components ─────────────────────────────────────────
import { navbar } from './components/layout/navbar.js'
import { searchOverlay } from './components/layout/searchOverlay.js'
import { searchBar } from './components/layout/searchBar.js'

// ── Cart components ───────────────────────────────────────────
import { cartDrawer } from './components/cart/cartDrawer.js'
import { quantitySelector } from './components/cart/quantitySelector.js'

// ── Product components ────────────────────────────────────────
import { productCard } from './components/products/productCard.js'
import { variantSelector } from './components/products/variantSelector.js'
import { productGallery } from './components/products/productGallery.js'
import { wishlistToggle } from './components/products/wishlistToggle.js'
import { filterSidebar } from './components/products/filterSidebar.js'


// ── Checkout components ───────────────────────────────────────
import { couponForm } from './components/checkout/couponForm.js'
import { addressSelector } from './components/checkout/addressSelector.js'
import { paymentMethod } from './components/checkout/paymentMethod.js'

// ── Account components ────────────────────────────────────────
import { reviewForm } from './components/review/reviewForm.js'

// ── UI components ─────────────────────────────────────────────
import { toastContainer } from './components/ui/toast.js'

// ── Page modules ──────────────────────────────────────────────
import { heroSlider } from './pages/home/home.js'
import { productList } from './pages/products/productList.js'
import { productDetail } from './pages/products/productDetail.js'
import { cartPage } from './pages/cart/cart.js'
import { checkoutPage } from './pages/checkout/checkout.js'
import { accountDashboard } from './pages/account/dashboard.js'
import { addressForm } from './pages/account/address.js'
import { searchPage } from './pages/shared/search.js'
import { wishlistPage } from './pages/shared/wishlist.js'
import { analyticsDashboard } from './pages/admin/analytics.js'
// ── Register stores ───────────────────────────────────────────
registerCartStore(Alpine)
registerWishlistStore(Alpine)
registerUiStore(Alpine)

// ── Register layout components ────────────────────────────────
Alpine.data('navbar', navbar)
Alpine.data('searchOverlay', searchOverlay)
Alpine.data('searchBar', searchBar)

// ── Register cart components ──────────────────────────────────
Alpine.data('cartDrawer', cartDrawer)
Alpine.data('quantitySelector', quantitySelector)

// ── Register product components ───────────────────────────────
Alpine.data('productCard', productCard)
Alpine.data('variantSelector', variantSelector)
Alpine.data('productGallery', productGallery)
Alpine.data('wishlistToggle', wishlistToggle)
Alpine.data('filterSidebar', filterSidebar)

// ── Register checkout components ──────────────────────────────
Alpine.data('couponForm', couponForm)
Alpine.data('addressSelector', addressSelector)
Alpine.data('paymentMethod', paymentMethod)

// ── Register account components ───────────────────────────────
Alpine.data('reviewForm', reviewForm)

// ── Register UI components ────────────────────────────────────
Alpine.data('toastContainer', toastContainer)

// ── Register page modules ─────────────────────────────────────
Alpine.data('heroSlider', heroSlider)
Alpine.data('productList', productList)
Alpine.data('productDetail', productDetail)
Alpine.data('cartPage', cartPage)
Alpine.data('checkoutPage', checkoutPage)
Alpine.data('accountDashboard', accountDashboard)
Alpine.data('addressForm', addressForm)
Alpine.data('searchPage', searchPage)
Alpine.data('wishlistPage', wishlistPage)
Alpine.data('analyticsDashboard', analyticsDashboard)
// ── Global escape handler ─────────────────────────────────────
document.addEventListener('keydown', (e) => {
  if (e.key !== 'Escape') return
  Alpine.store('ui').closeSearch()
  Alpine.store('ui').closeCartDrawer()
  Alpine.store('ui').closeMobileMenu()
})

// ── Expose Alpine for devtools ────────────────────────────────
window.Alpine = Alpine

document.addEventListener('alpine:init', () => {
  // Alpine fully initialized
})

Alpine.start()