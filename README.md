# PriorityX — Premium 3D E-Commerce Website

Full-stack e-commerce site: **Flask + SQLite** backend, **HTML/CSS/vanilla JS**
frontend with a dark glassmorphism / 3D UI.

Every feature is wired end-to-end: browse categories → view products →
product details → add to cart / buy now → cart → checkout → place order →
order confirmation → admin email notification, plus register/login/profile
with order history.

---

## 1. Project structure

```
PriorityX/
├── app.py                 Flask app (all routes + API)
├── requirements.txt
├── .env.example            Copy to .env and fill in your values
├── database/
│   └── init_db.py          Creates database/priorityx.db (schema + seed data)
├── template/                Jinja2 templates (Flask looks in "template/")
│   ├── base.html
│   ├── index.html
│   ├── products.html
│   ├── product.html
│   ├── cart.html
│   ├── checkout.html
│   ├── login.html
│   ├── register.html
│   ├── profile.html
│   └── ar_preview.html
└── static/
    ├── css/style.css        3D glassmorphism theme
    ├── js/script.js         cart, API calls, 3D tilt effects, page logic
    ├── images/               (optional real product images)
    └── models/                (optional .glb models for AR/Three.js)
```

## 2. Setup (VS Code / terminal)

```bash
# 1. Open the PriorityX folder in VS Code
cd PriorityX

# 2. Create & activate a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
copy .env.example .env       # Windows
cp .env.example .env         # macOS / Linux
# then edit .env and set SECRET_KEY / MAIL_USERNAME / MAIL_PASSWORD

# 5. Create the database (creates database/priorityx.db)
python database/init_db.py

# 6. Run the app
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

Demo account: **username** `demo` · **password** `demo1234`

Re-running `python database/init_db.py` at any time wipes and recreates the
database with fresh seed data.

## 3. Email notifications (Gmail SMTP)

Order emails to the admin ("New PriorityX Order") are sent through Gmail SMTP.
Credentials are read from environment variables — **never hard-coded**:

- `MAIL_USERNAME` — the Gmail address that sends the email
- `MAIL_PASSWORD` — a Gmail **App Password** (not your normal password):
  create one at https://myaccount.google.com/apppasswords
- `ADMIN_EMAIL` — where order notifications are delivered (defaults to
  `MAIL_USERNAME` if not set)

If these variables aren't set, orders still place successfully — the app
just logs a warning and skips the email instead of crashing.

## 4. How each part works

- **Cart** — stored in `localStorage` on the client (per the original
  concept) and reconciled/priced server-side at checkout so totals can't be
  tampered with.
- **Auth** — Flask sessions + Werkzeug password hashing (`/api/register`,
  `/api/login`, `/logout`).
- **Products/Categories** — served from SQLite via `/api/categories`,
  `/api/products`, `/api/product/<id>`; nothing is hard-coded in the HTML.
- **Checkout** — `/place_order` validates products against the DB,
  recomputes the total, stores the order + line items, and emails the
  admin.
- **Express Delivery** — categories/products flagged `express` show the
  green ⚡ badge and a dynamically generated delivery date/time on the
  product page.

## 5. Notes

- Product "images" render as styled emoji/icon placeholders by default —
  drop real files into `static/images/<category>/<name>.png` and update the
  `image` column / `<img>` markup if you want photos instead.
- All error states from the spec are implemented: invalid login, duplicate
  username, empty cart, failed order, product not found.
# PriorityX
