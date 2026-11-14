"""
PriorityX - Database initializer
Run this once (or delete priorityx.db and re-run) to create/reset the database
with schema + seed data.

Usage:
    python database/init_db.py
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "priorityx.db")


def init_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ---------- USERS ----------
    cur.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ---------- CATEGORIES ----------
    cur.execute("""
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            icon TEXT,
            description TEXT,
            express INTEGER DEFAULT 0
        )
    """)

    # ---------- PRODUCTS ----------
    cur.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            category TEXT NOT NULL,
            express INTEGER DEFAULT 0,
            image TEXT,
            stock INTEGER DEFAULT 100
        )
    """)

    # ---------- ORDERS ----------
    cur.execute("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT NOT NULL,
            total REAL NOT NULL,
            status TEXT DEFAULT 'Placed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # ---------- ORDER ITEMS ----------
    cur.execute("""
        CREATE TABLE order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY(order_id) REFERENCES orders(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    """)

    # ---------- SEED: CATEGORIES ----------
    categories = [
        ("Medical",     "💊", "Health & wellness essentials",        1),
        ("Essentials",  "🧴", "Everyday household must-haves",       1),
        ("Food",        "🍔", "Groceries & gourmet food",            1),
        ("Dresses",     "👗", "Fashion & apparel",                   0),
        ("Jewelry",     "💍", "Fine jewelry & accessories",          0),
        ("Watches",     "⌚", "Premium timepieces",                  0),
        ("Skincare",    "🧴", "Skincare & beauty",                   1),
        ("Electronics", "🔌", "Gadgets & devices",                   0),
        ("Toys",        "🧸", "Toys & games",                        0),
        ("Print",       "🖨️", "Printing & stationery",               0),
    ]
    cur.executemany(
        "INSERT INTO categories (name, icon, description, express) VALUES (?,?,?,?)",
        categories,
    )

    # ---------- SEED: PRODUCTS ----------
    products = [
        # Medical (express)
        ("Paracetamol",        30,   "Pain relief medicine, 10 tablet strip",              "Medical", 1, "medical/paracetamol.png"),
        ("Cough Syrup",        85,   "Relieves cough and throat irritation, 100ml",        "Medical", 1, "medical/cough_syrup.png"),
        ("Dettol",             120,  "Antiseptic liquid disinfectant, 250ml",              "Medical", 1, "medical/dettol.png"),
        ("Hello Kitty Bandaid",45,   "Fun printed bandages for kids, pack of 20",          "Medical", 1, "medical/hellokitty_bandaid.png"),
        ("Generic Bandaid",    25,   "Standard adhesive bandages, pack of 20",             "Medical", 1, "medical/generic_bandaid.png"),
        ("Spiderman Bandaid",  45,   "Superhero themed bandages, pack of 20",              "Medical", 1, "medical/spiderman_bandaid.png"),
        ("Vicks Inhaler",      60,   "Nasal decongestant inhaler stick",                   "Medical", 1, "medical/vicks_inhaler.png"),
        ("Vicks VapoRub",      95,   "Topical vapor rub for cold relief, 50ml",            "Medical", 1, "medical/vicks_vaporub.png"),
        ("Volini Gel",         140,  "Pain relief gel for muscle & joint pain, 50g",       "Medical", 1, "medical/volini_gel.png"),
        ("Volini Spray",       190,  "Fast acting pain relief spray, 55ml",                "Medical", 1, "medical/volini_spray.png"),

        # Essentials (express)
        ("Hand Sanitizer",     80,   "70% alcohol based sanitizer, 200ml",                 "Essentials", 1, "essentials/sanitizer.png"),
        ("Tissue Box",         55,   "Soft 2-ply facial tissues, 100 pulls",               "Essentials", 1, "essentials/tissue.png"),
        ("Laundry Detergent",  199,  "Concentrated liquid detergent, 1L",                  "Essentials", 0, "essentials/detergent.png"),
        ("Trash Bags",         99,   "Biodegradable trash bags, pack of 30",               "Essentials", 0, "essentials/trashbags.png"),

        # Food (express)
        ("Margherita Pizza",   249,  "Classic cheese & tomato pizza, 10 inch",             "Food", 1, "food/pizza.png"),
        ("Cold Brew Coffee",   149,  "Smooth cold brew coffee, 350ml bottle",              "Food", 1, "food/coldbrew.png"),
        ("Organic Honey",      299,  "Pure organic honey, 500g jar",                       "Food", 0, "food/honey.png"),
        ("Chocolate Cake",     399,  "Rich Belgian chocolate cake, 500g",                  "Food", 1, "food/cake.png"),

        # Dresses
        ("Floral Summer Dress",1299, "Lightweight floral print midi dress",                "Dresses", 0, "dresses/floral.png"),
        ("Denim Jacket",       1899, "Classic unisex denim jacket",                        "Dresses", 0, "dresses/denim.png"),
        ("Evening Gown",       3499, "Elegant satin evening gown",                         "Dresses", 0, "dresses/gown.png"),

        # Jewelry
        ("Gold Plated Necklace",2499,"22K gold plated statement necklace",                 "Jewelry", 0, "jewelry/necklace.png"),
        ("Diamond Stud Earrings",4999,"Certified diamond stud earrings",                   "Jewelry", 0, "jewelry/earrings.png"),

        # Watches
        ("PriorityX Chrono Steel",  6999, "Stainless steel chronograph watch",                  "Watches", 0, "watches/chrono.png"),
        ("Minimalist Leather Watch",3499,"Slim leather strap analog watch",                "Watches", 0, "watches/leather.png"),

        # Skincare (express)
        ("Vitamin C Serum",    599,  "Brightening vitamin C face serum, 30ml",             "Skincare", 1, "skincare/vitc.png"),
        ("Hydrating Face Wash",349,  "Gentle daily hydrating cleanser, 150ml",             "Skincare", 1, "skincare/facewash.png"),
        ("SPF 50 Sunscreen",   499,  "Broad spectrum sunscreen, 100ml",                    "Skincare", 1, "skincare/sunscreen.png"),

        # Electronics
        ("Wireless Earbuds",   2999, "Active noise cancelling wireless earbuds",           "Electronics", 0, "electronics/earbuds.png"),
        ("Smart Fitness Band", 1999, "Heart-rate & sleep tracking fitness band",           "Electronics", 0, "electronics/fitband.png"),
        ("Portable Power Bank",1299, "20000mAh fast charging power bank",                  "Electronics", 0, "electronics/powerbank.png"),

        # Toys
        ("Building Blocks Set",899,  "250 piece creative building block set",              "Toys", 0, "toys/blocks.png"),
        ("RC Racing Car",      1499, "Remote controlled racing car, 1:16 scale",           "Toys", 0, "toys/rccar.png"),

        # Print
        ("Custom Photo Frame", 349,  "Personalized wooden photo frame, A4",                "Print", 0, "print/photoframe.png"),
        ("Custom T-Shirt Print",449, "Your design printed on premium cotton tee",          "Print", 0, "print/tshirt.png"),
    ]
    cur.executemany(
        "INSERT INTO products (name, price, description, category, express, image) VALUES (?,?,?,?,?,?)",
        products,
    )

    # ---------- SEED: DEMO USER ----------
    cur.execute(
        "INSERT INTO users (username, email, password) VALUES (?,?,?)",
        ("demo", "demo@priorityx.com", generate_password_hash("demo1234")),
    )

    conn.commit()
    conn.close()
    print(f"✅ PriorityX database created at {DB_PATH}")
    print("   Demo login -> username: demo | password: demo1234")


if __name__ == "__main__":
    init_db()
