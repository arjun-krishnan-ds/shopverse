# Shopverse

A full-stack ecommerce platform built with Django 5.2, Alpine.js, and TailwindCSS — deployed on Railway with PostgreSQL, Redis, Cloudinary, and Stripe.

**Live:** [shopverse-in.up.railway.app](https://shopverse-in.up.railway.app)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Local Development](#local-development)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [Architecture Notes](#architecture-notes)

---

## Overview

Shopverse is a production-grade ecommerce application covering the complete customer journey — from product discovery through checkout, payment, and order tracking. It is built as a server-rendered Django application with a reactive Alpine.js frontend, backed by a PostgreSQL database and Redis for sessions and caching.

---

## Features

### Storefront
- Product listing with filtering, sorting, full-text search, and infinite scroll pagination
- Product detail pages with variant selection (color, size, etc.), image gallery, and zoom
- Category and brand browsing
- Responsive hero banner carousel with configurable banners
- Lazy-loaded images with blur-up transitions

### Cart
- Persistent cart for authenticated users (database-backed)
- Session-based guest cart for anonymous visitors
- Guest cart and wishlist merge on login or registration (session-key-safe implementation)
- Real-time cart drawer with quantity controls
- Coupon/discount code application

### Checkout & Payments
- Multi-step checkout: address selection → payment method → order placement
- Cash on Delivery (COD) — available for orders up to ₹5,000
- Stripe Checkout integration with hosted payment page
- COD order limit enforced server-side (tamper-proof)
- Duplicate order prevention via cart fingerprinting
- Pending Stripe order reuse on back-navigation
- Stripe webhook handler for payment confirmation, stock deduction, and cart clearance
- PDF invoice generation via ReportLab

### Orders
- Full order lifecycle: `PENDING → PAID → PROCESSING → SHIPPED → OUT FOR DELIVERY → DELIVERED`
- Order cancellation with automatic stock restoration
- Order tracking with progress indicator
- Estimated delivery via ETAService

### Accounts
- Email-based custom user model (no username)
- Registration, login, logout
- User dashboard with order history and stats
- Address book (add, edit, delete, set default)
- Wishlist (database-backed for users, session-backed for guests)

### Reviews
- Star rating + comment submission
- Photo/video media attachments on reviews
- Helpful/not-helpful voting
- Verified purchase badge
- Admin approval workflow

### Admin & Analytics
- Custom Django admin for all models
- Sales analytics dashboard (revenue, orders, top products, daily chart)
- Admin actions for bulk order status updates

### Recommendations
- Trending products (view-count based)
- Recently viewed (session-based)
- Customers also bought (order co-purchase analysis)
- Personalised recommendations for logged-in users

---

## Tech Stack

### Backend
| Package | Version | Purpose |
|---|---|---|
| Django | 5.2.12 | Web framework |
| psycopg2-binary | 2.9.11 | PostgreSQL adapter |
| Celery | 5.6.2 | Async task queue |
| redis | 7.3.0 | Cache + session backend + Celery broker |
| stripe | 14.4.1 | Payment processing |
| cloudinary | 1.44.1 | Media storage |
| django-cloudinary-storage | 0.3.0 | Cloudinary integration for Django |
| django-vite | 3.1.0 | Vite asset manifest integration |
| whitenoise | 6.12.0 | Static file serving |
| gunicorn | 26.0.0 | WSGI server |
| reportlab | 4.4.10 | PDF invoice generation |
| pillow | 12.1.1 | Image processing |
| python-decouple | 3.8 | Environment variable management |

### Frontend
| Package | Version | Purpose |
|---|---|---|
| Alpine.js | 3.14.1 | Reactive UI components |
| TailwindCSS | 3.4.4 | Utility-first CSS |
| Vite | 5.3.1 | Asset bundler |
| Axios | 1.7.2 | HTTP client |

### Infrastructure
| Service | Purpose |
|---|---|
| Railway | Hosting platform |
| PostgreSQL (Railway) | Production database |
| Redis (Railway) | Sessions, cache, Celery broker |
| Cloudinary | Product and media image storage |
| Stripe | Payment gateway |

---

## Project Structure

```
shopverse/
├── apps/
│   ├── accounts/       # Custom user model, auth, addresses
│   ├── analytics/      # Sales analytics dashboard
│   ├── cart/           # Cart model, session/DB cart, merge logic
│   ├── core/           # Base models, banners, context processors
│   ├── coupons/        # Coupon model and validation
│   ├── delivery/       # Delivery rules and fee calculation
│   ├── orders/         # Order lifecycle, checkout, invoices
│   ├── payments/       # Stripe gateway, webhook handler
│   ├── products/       # Products, variants, categories, brands
│   ├── reviews/        # Reviews, media, votes
│   └── wishlist/       # Wishlist (DB + session)
├── config/
│   ├── settings.py     # Django settings (env-driven)
│   ├── urls.py         # Root URL configuration
│   ├── wsgi.py
│   └── celery.py       # Celery app configuration
├── frontend/
│   ├── src/
│   │   ├── api/        # Axios API service layer
│   │   ├── components/ # Alpine.js components
│   │   ├── pages/      # Page-level Alpine modules
│   │   ├── stores/     # Alpine global stores (cart, wishlist, UI)
│   │   ├── styles/     # TailwindCSS entry point
│   │   └── utils/      # Helpers, formatters, validators
│   └── vite.config.js
├── templates/
│   ├── layouts/        # Base templates
│   ├── pages/          # Page templates
│   └── partials/       # Reusable template components
├── static/
│   ├── dist/           # Vite production build output
│   └── images/         # Static image assets
├── manage.py
├── requirements.txt
└── railway.toml        # Railway deployment configuration
```

---

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+ and npm 9+
- SQLite (default for local dev — no setup needed)
- A `.env` file (see [Environment Variables](#environment-variables))

### 1. Clone the repository

```bash
git clone https://github.com/arjun-krishnan-ds/shopverse.git
cd shopverse
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# macOS / Linux
source venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and build frontend assets

```bash
cd frontend
npm install
npm run build
cd ..
```

For active frontend development with hot reload:

```bash
# Terminal 1 — Django
python manage.py runserver

# Terminal 2 — Vite dev server
cd frontend && npm run dev
```

When running the Vite dev server, `base.html` automatically switches to the dev server URL via the `{% if debug %}` block.

### 5. Apply migrations and create a superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000`.

---

## Environment Variables

Create a `.env` file at the project root. This file is gitignored and must never be committed.

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000

# Database (leave unset locally to use SQLite)
# DATABASE_URL=postgresql://user:password@host:port/dbname

# Redis (leave unset locally to use in-memory cache)
# REDIS_URL=redis://localhost:6379/0

# Cloudinary
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Stripe
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email (optional for local dev — defaults to console backend)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@shopverse.com

# Frontend URL (used for Stripe success/cancel redirects)
FRONTEND_URL=http://127.0.0.1:8000
```

---

## Deployment

Shopverse is deployed on [Railway](https://railway.app) with the following service topology:

```
Railway Project
├── Web Service     (this repo, Python + Node build)
├── PostgreSQL      (Railway managed Postgres)
└── Redis           (Railway managed Redis)
```

### Railway environment variables (web service)

All variables from the `.env` section above are required in production, plus:

```env
DEBUG=False
ALLOWED_HOSTS=your-app.up.railway.app
CSRF_TRUSTED_ORIGINS=https://your-app.up.railway.app
FRONTEND_URL=https://your-app.up.railway.app
```

`DATABASE_URL` and `REDIS_URL` are injected automatically via Railway's variable reference system when you link the Postgres and Redis services to the web service — do not hardcode these.

### Build process (`railway.toml`)

Railway runs the following on each deploy:

1. `pip install -r requirements.txt` — Python dependencies
2. `cd frontend && npm install && npm run build` — Vite production build
3. `python manage.py migrate --noinput` — database migrations
4. `python manage.py collectstatic --noinput` — static file collection
5. Gunicorn starts on `$PORT` with 2 workers

### Stripe webhook

Register the following endpoint in the [Stripe Dashboard](https://dashboard.stripe.com) → Developers → Webhooks:

```
https://your-app.up.railway.app/payments/webhook/stripe/
```

Required events:
- `checkout.session.completed`
- `checkout.session.async_payment_failed`

Copy the webhook signing secret (`whsec_...`) and set it as `STRIPE_WEBHOOK_SECRET` in Railway.

---

## Architecture Notes

### Session handling and cart merge

Django's `login()` function calls `request.session.cycle_key()` to rotate the session ID (preventing session fixation attacks). This means any DB lookup by `session_id` must use the **pre-login** session key, captured *before* calling `login()`. Shopverse captures this explicitly in both `login_view` and `register_view` and passes it directly to `merge_guest_cart_to_user(session_key, user)`.

### Payment flow (Stripe)

```
User submits checkout
        ↓
Order created (status: PENDING)
        ↓
Stripe Checkout Session created
        ↓
User redirected to Stripe hosted page
        ↓
Payment confirmed by Stripe
        ↓
Stripe fires webhook → /payments/webhook/stripe/
        ↓
_handle_payment_success():
  - Stock deducted
  - Order marked PAID
  - Cart cleared
  - Confirmation email queued (Celery)
```

COD orders skip the Stripe path entirely — stock is deducted and cart is cleared immediately at order creation.

### Caching

In development (`DEBUG=True` or no `REDIS_URL`), the app falls back to Django's in-memory cache and database-backed sessions — no Redis required locally. In production, Redis handles both cache and sessions, configured automatically when `REDIS_URL` is present.

### Celery

In development or when no broker is configured, `CELERY_TASK_ALWAYS_EAGER=True` causes tasks (e.g. order confirmation emails) to execute synchronously within the request. In production with Redis available, tasks are queued and executed by a Celery worker. On Railway, a separate Celery worker service can be added pointing at the same repo with start command `celery -A config worker --loglevel=info`.

---

