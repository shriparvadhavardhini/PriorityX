"""
PriorityX E-Commerce - Flask backend
Run:
    pip install -r requirements.txt
    python database/init_db.py      (first time only, creates the DB)
    python app.py
Then open http://127.0.0.1:5000
"""

import os
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

from flask import (
    Flask, render_template, request, jsonify, session, redirect,
    url_for, send_from_directory
)
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "priorityx.db")

app = Flask(__name__, template_folder="template", static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY", "priorityx-dev-secret-key-change-me")

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "shriparvadhavardhini@gmail.com"
app.config["MAIL_PASSWORD"] = "vfid hhyd cpve wtzm"
app.config["ADMIN_EMAIL"] = os.environ.get("ADMIN_EMAIL", app.config["MAIL_USERNAME"])


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------
def get_db():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            "priorityx.db not found. Run: python database/init_db.py"
        )
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def row_to_dict(row):
    return dict(row) if row else None


def current_user():
    if "user_id" not in session:
        return None
    conn = get_db()
    user = conn.execute(
        "SELECT id, username, email FROM users WHERE id = ?",
        (session["user_id"],),
    ).fetchone()
    conn.close()
    return row_to_dict(user)


# ---------------------------------------------------------------------------
# PAGE ROUTES (render templates)
# ---------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html", user=current_user())


@app.route("/products")
@app.route("/products.html")
def products_page():
    category = request.args.get("category", "")
    return render_template("products.html", category=category, user=current_user())


@app.route("/product/<int:product_id>")
def product_page(product_id):
    return render_template("product.html", product_id=product_id, user=current_user())


@app.route("/cart")
def cart_page():
    return render_template("cart.html", user=current_user())


@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html", user=current_user())


@app.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html", user=current_user())


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/profile")
def profile_page():
    user = current_user()
    if not user:
        return redirect(url_for("login_page"))

    conn = get_db()
    orders = conn.execute(
        "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC",
        (user["id"],),
    ).fetchall()
    orders_list = []
    for o in orders:
        items = conn.execute(
            "SELECT * FROM order_items WHERE order_id = ?", (o["id"],)
        ).fetchall()
        od = row_to_dict(o)
        od["line_items"] = [row_to_dict(i) for i in items]
        orders_list.append(od)
    conn.close()

    return render_template("profile.html", user=user, orders=orders_list)


@app.route("/checkout")
def checkout_page():
    return render_template("checkout.html", user=current_user())


@app.route("/ar_preview/<int:product_id>")
def ar_preview(product_id):
    return render_template("ar_preview.html", product_id=product_id, user=current_user())


@app.route("/images/<path:filename>")
def images(filename):
    return send_from_directory(os.path.join(app.static_folder, "images"), filename)


# ---------------------------------------------------------------------------
# API ROUTES (JSON, called from script.js)
# ---------------------------------------------------------------------------
@app.route("/api/categories")
def api_categories():
    conn = get_db()
    rows = conn.execute("SELECT * FROM categories ORDER BY id").fetchall()
    conn.close()
    return jsonify([row_to_dict(r) for r in rows])


@app.route("/api/products")
def api_products():
    category = request.args.get("category")
    conn = get_db()
    if category:
        rows = conn.execute(
            "SELECT * FROM products WHERE category = ? ORDER BY id", (category,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM products ORDER BY id").fetchall()
    conn.close()
    return jsonify([row_to_dict(r) for r in rows])


@app.route("/api/product/<int:product_id>")
def api_product(product_id):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM products WHERE id = ?", (product_id,)
    ).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Product not found"}), 404

    product = row_to_dict(row)
    if product["express"]:
        eta = datetime.now() + timedelta(hours=4)
        product["delivery_date"] = eta.strftime("%d %B %Y")
        product["delivery_time"] = eta.strftime("%I:%M %p")
    return jsonify(product)


@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json(force=True)
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not username or not email or not password:
        return jsonify({"success": False, "message": "All fields are required"}), 400
    if len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters"}), 400

    conn = get_db()
    existing = conn.execute(
        "SELECT id FROM users WHERE username = ? OR email = ?", (username, email)
    ).fetchone()
    if existing:
        conn.close()
        return jsonify({"success": False, "message": "Username already exists"}), 409

    conn.execute(
        "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
        (username, email, generate_password_hash(password)),
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Account created successfully. Please login."})


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(force=True)
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ? OR email = ?", (username, username)
    ).fetchone()
    conn.close()

    if not user or not check_password_hash(user["password"], password):
        return jsonify({"success": False, "message": "Invalid username or password"}), 401

    session["user_id"] = user["id"]
    return jsonify({
        "success": True,
        "user": {"id": user["id"], "username": user["username"], "email": user["email"]},
    })


@app.route("/api/me")
def api_me():
    user = current_user()
    if not user:
        return jsonify({"logged_in": False})
    return jsonify({"logged_in": True, "user": user})


@app.route("/place_order", methods=["POST"])
def place_order():
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    phone = (data.get("phone") or "").strip()
    email = (data.get("email") or "").strip()
    address = (data.get("address") or "").strip()
    items = data.get("items") or []

    if not name or not phone or not email or not address:
        return jsonify({"success": False, "message": "Please fill in all customer details"}), 400
    if not items:
        return jsonify({"success": False, "message": "Your cart is empty"}), 400

    conn = get_db()

    # Validate products & compute total server-side (never trust client price)
    total = 0.0
    validated_items = []
    for it in items:
        product = conn.execute(
            "SELECT * FROM products WHERE id = ?", (it.get("id"),)
        ).fetchone()
        if not product:
            conn.close()
            return jsonify({"success": False, "message": "Product not found"}), 404
        qty = max(1, int(it.get("quantity", 1)))
        line_total = product["price"] * qty
        total += line_total
        validated_items.append({
            "product_id": product["id"],
            "name": product["name"],
            "quantity": qty,
            "price": product["price"],
        })

    user = current_user()
    user_id = user["id"] if user else None

    cur = conn.execute(
        "INSERT INTO orders (user_id, name, phone, email, address, total) VALUES (?,?,?,?,?,?)",
        (user_id, name, phone, email, address, total),
    )
    order_id = cur.lastrowid

    for it in validated_items:
        conn.execute(
            "INSERT INTO order_items (order_id, product_id, product_name, quantity, price) "
            "VALUES (?,?,?,?,?)",
            (order_id, it["product_id"], it["name"], it["quantity"], it["price"]),
        )

    conn.commit()
    conn.close()

    # Fire-and-forget email to admin; order still succeeds if email fails
    email_sent = send_order_email(order_id, name, phone, email, address, validated_items, total)

    return jsonify({
        "success": True,
        "order_id": order_id,
        "total": total,
        "email_sent": email_sent,
    })


# ---------------------------------------------------------------------------
# EMAIL
# ---------------------------------------------------------------------------
def send_order_email(order_id, name, phone, email, address, items, total):
    mail_username = app.config["MAIL_USERNAME"]
    mail_password = app.config["MAIL_PASSWORD"]
    if not mail_username or not mail_password:
        app.logger.warning(
            "MAIL_USERNAME / MAIL_PASSWORD not set - skipping order email. "
            "Set them as environment variables to enable email notifications."
        )
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = mail_username
        msg["To"] = app.config["ADMIN_EMAIL"]
        msg["Subject"] = "New PriorityX Order"

        lines = "\n".join(
            f"  - {i['name']}  x{i['quantity']}  @ ₹{i['price']}  = ₹{i['quantity'] * i['price']}"
            for i in items
        )

        body = f"""A new order has been placed on PriorityX.

Order ID: #{order_id}

Customer Details
-----------------
Name:    {name}
Phone:   {phone}
Email:   {email}
Address: {address}

Order Items
-----------------
{lines}

Total Amount: ₹{total}

-- PriorityX Order System
"""
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]) as server:
            if app.config["MAIL_USE_TLS"]:
                server.starttls()
            server.login(mail_username, mail_password)
            server.sendmail(mail_username, app.config["ADMIN_EMAIL"], msg.as_string())
        return True
    except Exception as exc:
        app.logger.error(f"Failed to send order email: {exc}")
        return False


# ---------------------------------------------------------------------------
# ERROR HANDLERS
# ---------------------------------------------------------------------------
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print("⚠️  Database not found. Run 'python database/init_db.py' first.")
    app.run(debug=True, port=5000)
