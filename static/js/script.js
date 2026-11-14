/* ==========================================================================
   PriorityX — Frontend logic
   Cart is kept in localStorage (client-side), everything else talks to the
   Flask JSON API.
   ========================================================================== */

const CART_KEY = "argo_cart";

/* ------------------------------- Cart helpers ---------------------------- */

function getCart() {
  try {
    return JSON.parse(localStorage.getItem(CART_KEY)) || [];
  } catch (e) {
    return [];
  }
}

function saveCart(cart) {
  localStorage.setItem(CART_KEY, JSON.stringify(cart));
  updateCartCount();
}

function addToCart(product, qty = 1) {
  const cart = getCart();
  const existing = cart.find((i) => i.id === product.id);
  if (existing) {
    existing.quantity += qty;
  } else {
    cart.push({
      id: product.id,
      name: product.name,
      price: product.price,
      image: product.image,
      express: product.express,
      quantity: qty,
    });
  }
  saveCart(cart);
}

function removeFromCart(productId) {
  const cart = getCart().filter((i) => i.id !== productId);
  saveCart(cart);
}

function updateCartItemQty(productId, qty) {
  const cart = getCart();
  const item = cart.find((i) => i.id === productId);
  if (!item) return;
  item.quantity = Math.max(1, qty);
  saveCart(cart);
}

function cartTotal(cart) {
  return cart.reduce((sum, i) => sum + i.price * i.quantity, 0);
}

function cartCount(cart) {
  return cart.reduce((sum, i) => sum + i.quantity, 0);
}

function updateCartCount() {
  const count = cartCount(getCart());
  const el = document.getElementById("cartCount");
  const elMobile = document.getElementById("cartCountMobile");
  if (el) el.textContent = count;
  if (elMobile) elMobile.textContent = count;
}

/* --------------------------------- Toast --------------------------------- */

let toastTimer;
function showToast(message) {
  const toast = document.getElementById("toast");
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("show"), 2200);
}

/* ------------------------------ Currency ---------------------------------- */

function formatPrice(value) {
  return "₹" + Number(value).toLocaleString("en-IN");
}

/* --------------------------------- Nav ------------------------------------ */

function initNav() {
  updateCartCount();

  const hamburger = document.getElementById("hamburgerBtn");
  const mobileMenu = document.getElementById("mobileMenu");
  if (hamburger && mobileMenu) {
    hamburger.addEventListener("click", () => {
      mobileMenu.classList.toggle("open");
    });
  }

  const navbar = document.getElementById("navbar");
  if (navbar) {
    window.addEventListener("scroll", () => {
      if (window.scrollY > 10) {
        navbar.style.paddingTop = "8px";
      } else {
        navbar.style.paddingTop = "16px";
      }
    });
  }
}

document.addEventListener("DOMContentLoaded", initNav);

/* ------------------------------- API helper -------------------------------- */

async function api(url, options = {}) {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  let data = {};
  try {
    data = await res.json();
  } catch (e) {
    /* no body */
  }
  if (!res.ok) {
    const err = new Error(data.message || "Request failed");
    err.status = res.status;
    err.data = data;
    throw err;
  }
  return data;
}

/* ------------------------------- Home page --------------------------------- */

const CATEGORY_ICONS = {
  Medical: "💊", Essentials: "🧴", Food: "🍔", Dresses: "👗", Jewelry: "💍",
  Watches: "⌚", Skincare: "🧴", Electronics: "🔌", Toys: "🧸", Print: "🖨️",
};

async function loadCategories() {
  const grid = document.getElementById("categoryGrid");
  if (!grid) return;
  try {
    const categories = await api("/api/categories");
    grid.innerHTML = categories
      .map(
        (c) => `
      <a class="category-card" href="/products?category=${encodeURIComponent(c.name)}">
        ${c.express ? '<span class="category-express">⚡ EXPRESS</span>' : ""}
        <span class="category-icon">${c.icon || "🛍️"}</span>
        <h3>${c.name}</h3>
        <p>${c.description || ""}</p>
        <span class="category-arrow">→</span>
      </a>`
      )
      .join("");
    attachTiltEffect(grid.querySelectorAll(".category-card"));
  } catch (e) {
    grid.innerHTML = "<p class='muted'>Unable to load categories right now.</p>";
  }
}

/* ----------------------------- Products page -------------------------------- */

async function initProductsPage(initialCategory) {
  const grid = document.getElementById("productGrid");
  const emptyState = document.getElementById("emptyState");
  const chipGroup = document.getElementById("filterChips");
  const categoryTitle = document.getElementById("categoryTitle");
  const categoryLabel = document.getElementById("categoryLabel");

  let categories = [];
  try {
    categories = await api("/api/categories");
  } catch (e) {
    categories = [];
  }

  chipGroup.innerHTML = categories
    .map((c) => `<button class="filter-chip" data-cat="${c.name}">${c.icon || ""} ${c.name}</button>`)
    .join("");

  function setActiveChip(cat) {
    document.querySelectorAll(".filter-chip").forEach((chip) => {
      chip.classList.toggle("active", chip.dataset.cat === cat);
    });
  }

  async function loadProducts(category) {
    setActiveChip(category || "");
    categoryTitle.textContent = category || "All Products";
    categoryLabel.textContent = category || "Products";

    try {
      const url = category ? `/api/products?category=${encodeURIComponent(category)}` : "/api/products";
      const products = await api(url);
      renderProductGrid(products, grid);
      emptyState.style.display = products.length ? "none" : "block";
    } catch (e) {
      grid.innerHTML = "";
      emptyState.style.display = "block";
    }
  }

  document.querySelectorAll(".filter-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const cat = chip.dataset.cat;
      const url = new URL(window.location);
      if (cat) url.searchParams.set("category", cat);
      else url.searchParams.delete("category");
      window.history.pushState({}, "", url);
      loadProducts(cat);
    });
  });

  loadProducts(initialCategory);
}

function renderProductGrid(products, grid) {
  if (!products.length) {
    grid.innerHTML = "";
    return;
  }
  grid.innerHTML = products
    .map(
      (p) => `
    <div class="product-card" data-id="${p.id}">
      <div class="product-image">
        ${p.express ? '<span class="product-express-badge">⚡ EXPRESS</span>' : ""}
        ${p.image ? `<img src="/static/images/${p.image}" alt="${p.name}" style="width: 100%; height: 100%; object-fit: contain;">` : '📦'}
      </div>
      <div class="product-body">
        <div class="product-name">${p.name}</div>
        <div class="product-price">${formatPrice(p.price)}</div>
        <div class="product-desc">${p.description || ""}</div>
        <div class="product-actions">
          <button class="btn btn-glass" data-action="add" data-id="${p.id}">Add to Cart</button>
          <button class="btn btn-primary" data-action="buy" data-id="${p.id}">Buy Now</button>
        </div>
      </div>
    </div>`
    )
    .join("");

  attachTiltEffect(grid.querySelectorAll(".product-card"));

  grid.querySelectorAll(".product-card").forEach((card) => {
    card.addEventListener("click", (e) => {
      if (e.target.closest("[data-action]")) return;
      window.location.href = `/product/${card.dataset.id}`;
    });
  });

  grid.querySelectorAll('[data-action="add"]').forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      e.stopPropagation();
      const product = products.find((p) => p.id == btn.dataset.id);
      addToCart(product, 1);
      showToast("✓ Added to Cart");
    });
  });

  grid.querySelectorAll('[data-action="buy"]').forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const product = products.find((p) => p.id == btn.dataset.id);
      addToCart(product, 1);
      window.location.href = "/checkout";
    });
  });
}

/* ------------------------------ 3D tilt effect ------------------------------- */

function attachTiltEffect(cards) {
  cards.forEach((card) => {
    card.addEventListener("mousemove", (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const rotateX = ((y / rect.height) - 0.5) * -10;
      const rotateY = ((x / rect.width) - 0.5) * 10;
      card.style.transform = `perspective(900px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
    });
    card.addEventListener("mouseleave", () => {
      card.style.transform = "";
    });
  });
}

/* --------------------------- Product detail page ------------------------------ */

async function initProductDetailPage(productId) {
  let product;
  try {
    product = await api(`/api/product/${productId}`);
  } catch (e) {
    document.getElementById("pdName").textContent = "Product not found";
    return;
  }

  document.getElementById("pdName").textContent = product.name;
  document.getElementById("pdPrice").textContent = formatPrice(product.price);
  document.getElementById("pdDescription").textContent = product.description || "";
  document.getElementById("arLink").href = `/ar_preview/${product.id}`;
  
  // Display product image
  if (product.image) {
    const imgSrc = `/static/images/${product.image}`;
    document.getElementById("pdImage").src = imgSrc;
    console.log("Loading image:", imgSrc);
  } else {
    console.log("No image data for product", productId);
  }

  if (product.express) {
    document.getElementById("pdExpress").style.display = "inline-flex";
    document.getElementById("pdDelivery").style.display = "flex";
    document.getElementById("pdDeliveryDate").textContent = product.delivery_date;
    document.getElementById("pdDeliveryTime").textContent = "by " + product.delivery_time;
  }

  let qty = 1;
  const qtyValue = document.getElementById("qtyValue");
  document.getElementById("qtyMinus").addEventListener("click", () => {
    qty = Math.max(1, qty - 1);
    qtyValue.textContent = qty;
  });
  document.getElementById("qtyPlus").addEventListener("click", () => {
    qty += 1;
    qtyValue.textContent = qty;
  });

  document.getElementById("addToCartBtn").addEventListener("click", () => {
    addToCart(product, qty);
    showToast("✓ Added to Cart");
  });

  document.getElementById("buyNowBtn").addEventListener("click", () => {
    addToCart(product, qty);
    window.location.href = "/checkout";
  });
}

/* -------------------------------- Cart page ---------------------------------- */

function initCartPage() {
  const container = document.getElementById("cartItems");
  const emptyState = document.getElementById("cartEmptyState");
  const layout = document.querySelector(".cart-layout");

  function render() {
    const cart = getCart();

    if (!cart.length) {
      layout.style.display = "none";
      emptyState.style.display = "block";
      return;
    }
    layout.style.display = "grid";
    emptyState.style.display = "none";

    container.innerHTML = cart
      .map(
        (item) => `
      <div class="cart-item" data-id="${item.id}">
        <div class="cart-item-image">${item.image ? `<img src="/static/images/${item.image}" alt="${item.name}" style="width: 100%; height: 100%; object-fit: contain;">` : '📦'}</div>
        <div class="cart-item-info">
          <h4>${item.name}</h4>
          <div class="cart-item-price">${formatPrice(item.price)}</div>
        </div>
        <div class="cart-item-qty">
          <button data-action="dec">−</button>
          <span>${item.quantity}</span>
          <button data-action="inc">+</button>
        </div>
        <button class="cart-item-remove" data-action="remove">✕</button>
      </div>`
      )
      .join("");

    document.getElementById("cartSubtotal").textContent = formatPrice(cartTotal(cart));
    document.getElementById("cartTotal").textContent = formatPrice(cartTotal(cart));

    container.querySelectorAll(".cart-item").forEach((row) => {
      const id = Number(row.dataset.id);
      row.querySelector('[data-action="inc"]').addEventListener("click", () => {
        const item = getCart().find((i) => i.id === id);
        updateCartItemQty(id, item.quantity + 1);
        render();
      });
      row.querySelector('[data-action="dec"]').addEventListener("click", () => {
        const item = getCart().find((i) => i.id === id);
        if (item.quantity <= 1) return;
        updateCartItemQty(id, item.quantity - 1);
        render();
      });
      row.querySelector('[data-action="remove"]').addEventListener("click", () => {
        row.classList.add("removing");
        setTimeout(() => {
          removeFromCart(id);
          render();
        }, 250);
      });
    });
  }

  render();

  document.getElementById("cartCheckoutBtn").addEventListener("click", () => {
    if (!getCart().length) {
      showToast("Your cart is empty");
      return;
    }
    window.location.href = "/checkout";
  });
}

/* -------------------------------- Login page ---------------------------------- */

function initLoginPage() {
  const form = document.getElementById("loginForm");
  const errorEl = document.getElementById("loginError");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorEl.textContent = "";
    const username = document.getElementById("loginUsername").value.trim();
    const password = document.getElementById("loginPassword").value;

    try {
      await api("/api/login", {
        method: "POST",
        body: JSON.stringify({ username, password }),
      });
      window.location.href = "/profile";
    } catch (err) {
      errorEl.textContent = err.data?.message || "Invalid username or password";
    }
  });
}

/* ------------------------------- Register page --------------------------------- */

function initRegisterPage() {
  const form = document.getElementById("registerForm");
  const errorEl = document.getElementById("registerError");
  const successEl = document.getElementById("registerSuccess");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorEl.textContent = "";
    successEl.textContent = "";

    const username = document.getElementById("regUsername").value.trim();
    const email = document.getElementById("regEmail").value.trim();
    const password = document.getElementById("regPassword").value;

    try {
      const data = await api("/api/register", {
        method: "POST",
        body: JSON.stringify({ username, email, password }),
      });
      successEl.textContent = data.message || "Account created successfully. Please login.";
      setTimeout(() => (window.location.href = "/login"), 1200);
    } catch (err) {
      errorEl.textContent = err.data?.message || "Username already exists";
    }
  });
}

/* ------------------------------- Checkout page ---------------------------------- */

function initCheckoutPage() {
  const cart = getCart();
  const itemsContainer = document.getElementById("checkoutItems");
  const totalEl = document.getElementById("checkoutTotal");
  const form = document.getElementById("checkoutForm");
  const errorEl = document.getElementById("checkoutError");
  const placeOrderBtn = document.getElementById("placeOrderBtn");

  if (!cart.length) {
    itemsContainer.innerHTML = "<p class='muted'>Your cart is empty</p>";
    totalEl.textContent = formatPrice(0);
    placeOrderBtn.disabled = true;
    return;
  }

  itemsContainer.innerHTML = cart
    .map(
      (i) => `<div class="checkout-line"><span>${i.name} × ${i.quantity}</span><span>${formatPrice(i.price * i.quantity)}</span></div>`
    )
    .join("");
  totalEl.textContent = formatPrice(cartTotal(cart));

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorEl.textContent = "";

    const payload = {
      name: document.getElementById("custName").value.trim(),
      phone: document.getElementById("custPhone").value.trim(),
      email: document.getElementById("custEmail").value.trim(),
      address: document.getElementById("custAddress").value.trim(),
      items: getCart().map((i) => ({ id: i.id, quantity: i.quantity })),
    };

    if (!payload.name || !payload.phone || !payload.email || !payload.address) {
      errorEl.textContent = "Please fill in all customer details";
      return;
    }
    if (!getCart().length) {
      errorEl.textContent = "Your cart is empty";
      return;
    }

    placeOrderBtn.disabled = true;
    placeOrderBtn.textContent = "PLACING ORDER…";

    try {
      const data = await api("/place_order", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      localStorage.removeItem(CART_KEY);
      updateCartCount();
      document.getElementById("successOrderId").textContent = data.order_id;
      document.getElementById("successOverlay").classList.add("show");
    } catch (err) {
      errorEl.textContent = err.data?.message || "Unable to place order. Please try again.";
      placeOrderBtn.disabled = false;
      placeOrderBtn.textContent = "PLACE ORDER";
    }
  });
}

/* -------------------------------- AR preview ------------------------------------ */

function initArPreview(productId) {
  api(`/api/product/${productId}`)
    .then((product) => {
      const face = document.getElementById("arFace");
      if (face) face.textContent = "📦";
    })
    .catch(() => {});

  const rotator = document.getElementById("arRotator");
  if (!rotator) return;

  let isDragging = false;
  let startX = 0, startY = 0;
  let rotX = -10, rotY = 20;

  function applyRotation() {
    rotator.style.transform = `rotateX(${rotX}deg) rotateY(${rotY}deg)`;
  }
  applyRotation();

  rotator.addEventListener("mousedown", (e) => {
    isDragging = true;
    startX = e.clientX;
    startY = e.clientY;
    rotator.style.cursor = "grabbing";
  });
  window.addEventListener("mouseup", () => {
    isDragging = false;
    rotator.style.cursor = "grab";
  });
  window.addEventListener("mousemove", (e) => {
    if (!isDragging) return;
    rotY += (e.clientX - startX) * 0.5;
    rotX -= (e.clientY - startY) * 0.5;
    startX = e.clientX;
    startY = e.clientY;
    applyRotation();
  });
}
