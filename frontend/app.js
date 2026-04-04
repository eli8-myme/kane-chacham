// ===== CONFIG =====
const API_BASE = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : 'https://your-backend.onrender.com'; // יתעדכן בהעלאה

// Demo mode: עובד בלי backend עם נתונים מקומיים
const DEMO_MODE = true;

// ===== DEMO DATABASE =====
// מוצרים אמיתיים לדוגמה מסופרמרקטים ישראליים
const DEMO_PRODUCTS = {
  "7290000066318": {
    product: { barcode: "7290000066318", name: "חלב תנובה 3%", brand: "תנובה", size: "1 ליטר", category: "חלב", image_url: "" },
    comparisons: [
      { store_name: "רמי לוי", store_chain: "rami_levy", price: 5.90, price_per_unit: 0.59, size: "1 ליטר", is_current: false },
      { store_name: "שופרסל", store_chain: "shufersal", price: 6.50, price_per_unit: 0.65, size: "1 ליטר", is_current: true },
      { store_name: "ויקטורי", store_chain: "victory", price: 6.20, price_per_unit: 0.62, size: "1 ליטר", is_current: false },
      { store_name: "מגה", store_chain: "mega", price: 6.40, price_per_unit: 0.64, size: "1 ליטר", is_current: false },
      { store_name: "יינות ביתן", store_chain: "yeinot_bitan", price: 6.30, price_per_unit: 0.63, size: "1 ליטר", is_current: false },
    ]
  },
  "7290004131609": {
    product: { barcode: "7290004131609", name: "קוטג' תנובה 5%", brand: "תנובה", size: "250 גרם", category: "מוצרי חלב", image_url: "" },
    comparisons: [
      { store_name: "רמי לוי", store_chain: "rami_levy", price: 5.20, price_per_unit: 2.08, size: "250 גרם", is_current: false },
      { store_name: "שופרסל", store_chain: "shufersal", price: 6.10, price_per_unit: 2.44, size: "250 גרם", is_current: true },
      { store_name: "ויקטורי", store_chain: "victory", price: 5.50, price_per_unit: 2.20, size: "250 גרם", is_current: false },
      { store_name: "רמי לוי", store_chain: "rami_levy", price: 9.90, price_per_unit: 1.98, size: "500 גרם", is_current: false },
      { store_name: "שופרסל", store_chain: "shufersal", price: 11.50, price_per_unit: 2.30, size: "500 גרם", is_current: false },
    ]
  },
  "7290000307268": {
    product: { barcode: "7290000307268", name: "במבה אסם", brand: "אסם", size: "80 גרם", category: "חטיפים", image_url: "" },
    comparisons: [
      { store_name: "רמי לוי", store_chain: "rami_levy", price: 4.90, price_per_unit: 6.13, size: "80 גרם", is_current: false },
      { store_name: "שופרסל", store_chain: "shufersal", price: 5.90, price_per_unit: 7.38, size: "80 גרם", is_current: true },
      { store_name: "ויקטורי", store_chain: "victory", price: 5.20, price_per_unit: 6.50, size: "80 גרם", is_current: false },
      { store_name: "מגה", store_chain: "mega", price: 5.50, price_per_unit: 6.88, size: "80 גרם", is_current: false },
      { store_name: "רמי לוי", store_chain: "rami_levy", price: 11.90, price_per_unit: 4.96, size: "240 גרם (מארז)", is_current: false },
      { store_name: "שופרסל", store_chain: "shufersal", price: 13.90, price_per_unit: 5.79, size: "240 גרם (מארז)", is_current: false },
    ]
  },
  "7290000563534": {
    product: { barcode: "7290000563534", name: "שמן זית שמן הבית", brand: "שמן הבית", size: "750 מ\"ל", category: "שמנים", image_url: "" },
    comparisons: [
      { store_name: "רמי לוי", store_chain: "rami_levy", price: 24.90, price_per_unit: 3.32, size: "750 מ\"ל", is_current: false },
      { store_name: "שופרסל", store_chain: "shufersal", price: 29.90, price_per_unit: 3.99, size: "750 מ\"ל", is_current: true },
      { store_name: "ויקטורי", store_chain: "victory", price: 26.90, price_per_unit: 3.59, size: "750 מ\"ל", is_current: false },
      { store_name: "מגה", store_chain: "mega", price: 27.50, price_per_unit: 3.67, size: "750 מ\"ל", is_current: false },
    ]
  },
  "7290106809369": {
    product: { barcode: "7290106809369", name: "אבקת כביסה סנו מקסימה", brand: "סנו", size: "2.5 ק\"ג", category: "ניקוי", image_url: "" },
    comparisons: [
      { store_name: "רמי לוי", store_chain: "rami_levy", price: 34.90, price_per_unit: 1.40, size: "2.5 ק\"ג", is_current: false },
      { store_name: "שופרסל", store_chain: "shufersal", price: 42.90, price_per_unit: 1.72, size: "2.5 ק\"ג", is_current: true },
      { store_name: "ויקטורי", store_chain: "victory", price: 37.90, price_per_unit: 1.52, size: "2.5 ק\"ג", is_current: false },
      { store_name: "אושר עד", store_chain: "osher_ad", price: 35.90, price_per_unit: 1.44, size: "2.5 ק\"ג", is_current: false },
      { store_name: "רמי לוי", store_chain: "rami_levy", price: 54.90, price_per_unit: 1.10, size: "5 ק\"ג", is_current: false },
      { store_name: "שופרסל", store_chain: "shufersal", price: 64.90, price_per_unit: 1.30, size: "5 ק\"ג", is_current: false },
    ]
  },
  "7290000197067": {
    product: { barcode: "7290000197067", name: "קפה עלית נמס", brand: "עלית", size: "200 גרם", category: "קפה", image_url: "" },
    comparisons: [
      { store_name: "רמי לוי", store_chain: "rami_levy", price: 18.90, price_per_unit: 9.45, size: "200 גרם", is_current: false },
      { store_name: "שופרסל", store_chain: "shufersal", price: 22.90, price_per_unit: 11.45, size: "200 גרם", is_current: true },
      { store_name: "ויקטורי", store_chain: "victory", price: 19.90, price_per_unit: 9.95, size: "200 גרם", is_current: false },
      { store_name: "מגה", store_chain: "mega", price: 21.90, price_per_unit: 10.95, size: "200 גרם", is_current: false },
    ]
  },
  "7290000100517": {
    product: { barcode: "7290000100517", name: "סבון כלים פיירי", brand: "Fairy", size: "500 מ\"ל", category: "ניקוי", image_url: "" },
    comparisons: [
      { store_name: "רמי לוי", store_chain: "rami_levy", price: 9.90, price_per_unit: 1.98, size: "500 מ\"ל", is_current: false },
      { store_name: "שופרסל", store_chain: "shufersal", price: 12.90, price_per_unit: 2.58, size: "500 מ\"ל", is_current: true },
      { store_name: "ויקטורי", store_chain: "victory", price: 10.90, price_per_unit: 2.18, size: "500 מ\"ל", is_current: false },
      { store_name: "שופרסל", store_chain: "shufersal", price: 19.90, price_per_unit: 1.99, size: "1 ליטר", is_current: false },
      { store_name: "רמי לוי", store_chain: "rami_levy", price: 16.90, price_per_unit: 1.69, size: "1 ליטר", is_current: false },
    ]
  },
};

// דמו דינמי: מייצר נתונים למוצרים שלא ב-DB
function generateDemoForBarcode(barcode) {
  const names = ["מוצר לדוגמה", "פריט סופרמרקט", "מוצר מזון", "מוצר ניקוי"];
  const stores = ["שופרסל", "רמי לוי", "ויקטורי", "מגה", "יינות ביתן"];
  const basePrice = 8 + Math.random() * 35;

  const comparisons = stores.map((store, i) => ({
    store_name: store,
    store_chain: store,
    price: Math.round((basePrice * (0.85 + Math.random() * 0.35)) * 100) / 100,
    price_per_unit: Math.round((basePrice * (0.85 + Math.random() * 0.35) / 5) * 100) / 100,
    size: "500 גרם",
    is_current: i === 0,
  }));

  return {
    product: { barcode, name: `מוצר ${barcode.slice(-4)}`, brand: "כללי", size: "500 גרם", category: "כללי", image_url: "" },
    comparisons,
  };
}

// ===== SCREEN MANAGER =====
function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById('screen-' + id).classList.add('active');
}

function goHome() {
  stopScanner();
  stopCamera();
  showScreen('home');
  loadRecentScans();
}

// ===== BARCODE SCANNER =====
let scannerRunning = false;

function startBarcodeScanner() {
  showScreen('scanner');

  const status = document.getElementById('scanner-status');
  status.textContent = 'מפעיל מצלמה...';

  Quagga.init({
    inputStream: {
      type: 'LiveStream',
      target: document.getElementById('interactive'),
      constraints: {
        facingMode: 'environment',
        width: { ideal: 1280 },
        height: { ideal: 720 },
      },
    },
    decoder: {
      readers: ['ean_reader', 'ean_8_reader', 'upc_reader', 'code_128_reader'],
    },
    locate: true,
    numOfWorkers: 2,
    frequency: 10,
  }, (err) => {
    if (err) {
      status.textContent = 'שגיאה בגישה למצלמה. נסה ידנית.';
      console.error(err);
      return;
    }
    Quagga.start();
    scannerRunning = true;
    status.textContent = 'מחפש ברקוד...';
  });

  let lastCode = null;
  let lastTime = 0;

  Quagga.onDetected((result) => {
    const code = result.codeResult.code;
    const now = Date.now();
    // debounce: אותו ברקוד לפחות 2 שניות פרידה
    if (code === lastCode && now - lastTime < 2000) return;
    lastCode = code;
    lastTime = now;

    // ויברציה אם נתמכת
    if (navigator.vibrate) navigator.vibrate(100);

    document.getElementById('scanner-status').textContent = `זוהה: ${code}`;
    stopScanner();
    searchProduct(code, 'barcode');
  });
}

function stopScanner() {
  if (scannerRunning) {
    Quagga.stop();
    scannerRunning = false;
  }
}

// ===== IMAGE CAPTURE =====
let cameraStream = null;

function startImageCapture() {
  showScreen('image');
  document.getElementById('captured-preview').style.display = 'none';
  document.querySelector('.camera-container').style.display = '';
  document.querySelector('.camera-controls').style.display = '';

  navigator.mediaDevices.getUserMedia({
    video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } }
  }).then(stream => {
    cameraStream = stream;
    const video = document.getElementById('camera-video');
    video.srcObject = stream;
  }).catch(err => {
    console.error(err);
    showError('לא ניתן לגשת למצלמה', err.message);
  });
}

function captureImage() {
  const video = document.getElementById('camera-video');
  const canvas = document.getElementById('camera-canvas');
  canvas.width  = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);

  const dataUrl = canvas.toDataURL('image/jpeg', 0.85);
  document.getElementById('captured-img').src = dataUrl;
  document.getElementById('captured-preview').style.display = 'flex';
  document.querySelector('.camera-container').style.display = 'none';
  document.querySelector('.camera-controls').style.display = 'none';
}

function retakePhoto() {
  document.getElementById('captured-preview').style.display = 'none';
  document.querySelector('.camera-container').style.display = '';
  document.querySelector('.camera-controls').style.display = '';
}

function stopCamera() {
  if (cameraStream) {
    cameraStream.getTracks().forEach(t => t.stop());
    cameraStream = null;
  }
}

function analyzeImage() {
  const imgData = document.getElementById('captured-img').src;
  stopCamera();
  searchProduct(imgData, 'image');
}

// ===== MANUAL SEARCH =====
function searchManual() {
  const val = document.getElementById('manual-barcode').value.trim();
  if (!val) return;
  searchProduct(val, 'barcode');
}

// ===== MAIN SEARCH FLOW =====
async function searchProduct(data, type) {
  showScreen('loading');
  const steps = ['step-identify', 'step-prices', 'step-compare'];

  // אנימציית צעדים
  for (let i = 0; i < steps.length; i++) {
    if (i > 0) document.getElementById(steps[i-1]).classList.replace('active', 'done');
    document.getElementById(steps[i]).classList.add('active');
    await delay(600);
  }

  try {
    let result;

    if (type === 'barcode') {
      result = await fetchPrices({ barcode: data });
    } else {
      // image: שלח base64 לבקאנד
      const base64 = data.split(',')[1];
      result = await fetchPrices({ image_base64: base64 });
    }

    document.getElementById(steps[2]).classList.replace('active', 'done');
    await delay(300);

    if (!result || !result.product) {
      showError('המוצר לא נמצא', 'לא הצלחנו למצוא מידע על המוצר הזה');
      return;
    }

    saveToRecent(result.product, data, type);
    displayResults(result);

  } catch (err) {
    console.error(err);
    showError('שגיאה בחיבור לשרת', err.message || 'אנא נסה שוב');
  }
}

// ===== API CALL =====
async function fetchPrices(payload) {
  // Demo mode: שימוש בנתונים מקומיים
  if (DEMO_MODE) {
    await delay(300); // סימולציה של חיפוש
    return fetchDemoPrices(payload);
  }

  const response = await fetch(`${API_BASE}/api/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) throw new Error(`Server error: ${response.status}`);
  return response.json();
}

function fetchDemoPrices(payload) {
  if (payload.barcode) {
    const data = DEMO_PRODUCTS[payload.barcode];
    if (data) {
      return {
        product: data.product,
        current_store: "שופרסל",
        current_price: data.comparisons.find(c => c.is_current)?.price || data.comparisons[0].price,
        comparisons: data.comparisons,
      };
    }
    // ברקוד לא מוכר - צור דמו דינמי
    const gen = generateDemoForBarcode(payload.barcode);
    return {
      product: gen.product,
      current_store: gen.comparisons[0].store_name,
      current_price: gen.comparisons[0].price,
      comparisons: gen.comparisons,
    };
  }

  if (payload.image_base64) {
    // בדמו: מחזיר מוצר אקראי מה-DB
    const keys = Object.keys(DEMO_PRODUCTS);
    const key = keys[Math.floor(Math.random() * keys.length)];
    const data = DEMO_PRODUCTS[key];
    return {
      product: { ...data.product, name: data.product.name + " (זוהה מתמונה)" },
      current_store: "שופרסל",
      current_price: data.comparisons.find(c => c.is_current)?.price || data.comparisons[0].price,
      comparisons: data.comparisons,
    };
  }

  return null;
}

// ===== DISPLAY RESULTS =====
function displayResults(data) {
  const { product, current_store, current_price, comparisons } = data;

  // Product card
  document.getElementById('result-product-name').textContent = product.name;
  document.getElementById('result-product-brand').textContent = product.brand || '';
  document.getElementById('result-product-size').textContent = product.size || '';

  if (product.image_url) {
    document.getElementById('result-product-img').src = product.image_url;
    document.getElementById('result-product-img').style.display = '';
    document.getElementById('product-img-placeholder').style.display = 'none';
  }

  // Current price
  document.getElementById('current-store').textContent = current_store || 'הסופר הנוכחי';
  document.getElementById('current-price').textContent = formatPrice(current_price);

  // Sort comparisons by unit price
  const sorted = [...comparisons].sort((a, b) => a.price_per_unit - b.price_per_unit);
  const best = sorted[0];
  const current = comparisons.find(c => c.is_current) || { price: current_price };

  // Best deal banner
  document.getElementById('deal-title').textContent = `${best.store_name} - ${best.size}`;
  document.getElementById('deal-subtitle').textContent = `${formatPrice(best.price_per_unit)} ל-100 גרם/מ"ל`;
  document.getElementById('deal-price').textContent = formatPrice(best.price);

  // Comparison table
  const table = document.getElementById('comparison-table');
  table.innerHTML = '';

  sorted.forEach((item, index) => {
    const isBest = index === 0;
    const isCurrent = item.is_current;
    const savings = current_price - item.price;

    const row = document.createElement('div');
    row.className = `comp-row ${isBest ? 'best' : ''} ${isCurrent ? 'current-row' : ''}`;

    let badge = '';
    if (isBest && !isCurrent) badge = `<span class="comp-badge badge-best">הכי זול</span>`;
    if (isCurrent) badge = `<span class="comp-badge badge-here">אתה כאן</span>`;
    if (!isBest && !isCurrent && savings > 0) {
      badge = `<span class="comp-badge badge-save">חסכון ${formatPrice(savings)}</span>`;
    }

    const rankClass = index < 3 ? `rank-${index + 1}` : 'rank-other';

    row.innerHTML = `
      <div class="comp-rank ${rankClass}">${index + 1}</div>
      <div class="comp-store">
        <div class="comp-store-name">${item.store_name}</div>
        <div class="comp-store-size">${item.size || ''}</div>
        ${badge}
      </div>
      <div class="comp-price-wrap">
        <div class="comp-price">${formatPrice(item.price)}</div>
        <div class="comp-per-unit">${formatPrice(item.price_per_unit)} ל-100 יח'</div>
      </div>
    `;
    table.appendChild(row);
  });

  // Savings
  const maxSavings = current_price - best.price;
  if (maxSavings > 0) {
    document.getElementById('savings-amount').textContent = formatPrice(maxSavings);
    document.getElementById('savings-desc').textContent =
      `לעומת ${best.store_name} (${best.size})`;
    document.getElementById('savings-card').style.display = '';
  } else {
    document.getElementById('savings-card').style.display = 'none';
  }

  showScreen('results');
}

// ===== RECENT SCANS =====
function saveToRecent(product, data, type) {
  let recent = JSON.parse(localStorage.getItem('recent_scans') || '[]');
  recent.unshift({ product, data: type === 'barcode' ? data : null, type, ts: Date.now() });
  recent = recent.slice(0, 5);
  localStorage.setItem('recent_scans', JSON.stringify(recent));
}

function loadRecentScans() {
  const recent = JSON.parse(localStorage.getItem('recent_scans') || '[]');
  const section = document.getElementById('recent-section');
  const list = document.getElementById('recent-list');

  if (recent.length === 0) { section.style.display = 'none'; return; }
  section.style.display = '';
  list.innerHTML = '';

  recent.forEach(item => {
    const el = document.createElement('div');
    el.className = 'recent-item';
    el.innerHTML = `
      <span style="font-size:1.5rem">🛍️</span>
      <div style="flex:1">
        <div style="font-weight:600;font-size:0.95rem">${item.product?.name || 'מוצר'}</div>
        <div style="font-size:0.75rem;color:#777">${timeAgo(item.ts)}</div>
      </div>
    `;
    if (item.type === 'barcode' && item.data) {
      el.onclick = () => searchProduct(item.data, 'barcode');
    }
    list.appendChild(el);
  });
}

// ===== ERROR =====
function showError(title, message) {
  document.getElementById('error-title').textContent = title;
  document.getElementById('error-message').textContent = message;
  showScreen('error');
}

// ===== UTILS =====
function formatPrice(n) {
  if (!n && n !== 0) return '-';
  return '₪' + parseFloat(n).toFixed(2);
}

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function timeAgo(ts) {
  const diff = Date.now() - ts;
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'עכשיו';
  if (mins < 60) return `לפני ${mins} דקות`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `לפני ${hrs} שעות`;
  return `לפני ${Math.floor(hrs / 24)} ימים`;
}

// ===== INIT =====
document.addEventListener('DOMContentLoaded', () => {
  loadRecentScans();

  // Enter key on manual input
  document.getElementById('manual-barcode').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') searchManual();
  });
});
