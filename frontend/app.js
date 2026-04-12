// ===== CONFIG =====
const API_BASE = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : 'https://your-backend.onrender.com';

const DEMO_MODE = true;
const APP_VERSION = '9';

// ===== DEMO DATABASE =====
const DEMO_PRODUCTS = {
  "7290000066318": {
    product: { barcode: "7290000066318", name: "חלב תנובה 3%", brand: "תנובה", size: "1 ליטר", category: "חלב", image_url: "" },
    comparisons: [
      { store_name: "רמי לוי", store_chain: "rami_levy", price: 5.90, price_per_unit: 5.90, size: "1 ליטר", is_current: false },
      { store_name: "אושר עד", store_chain: "osher_ad", price: 5.95, price_per_unit: 5.95, size: "1 ליטר", is_current: false },
      { store_name: "חצי חינם", store_chain: "hatzi_hinam", price: 6.10, price_per_unit: 6.10, size: "1 ליטר", is_current: false },
      { store_name: "שופרסל דיל", store_chain: "shufersal_deal", price: 6.20, price_per_unit: 6.20, size: "1 ליטר", is_current: false },
      { store_name: "ויקטורי", store_chain: "victory", price: 6.20, price_per_unit: 6.20, size: "1 ליטר", is_current: false },
      { store_name: "יינות ביתן", store_chain: "yeinot_bitan", price: 6.30, price_per_unit: 6.30, size: "1 ליטר", is_current: false },
      { store_name: "מגה", store_chain: "mega", price: 6.40, price_per_unit: 6.40, size: "1 ליטר", is_current: false },
      { store_name: "שופרסל", store_chain: "shufersal", price: 6.50, price_per_unit: 6.50, size: "1 ליטר", is_current: true },
      { store_name: "טיב טעם", store_chain: "tiv_taam", price: 6.70, price_per_unit: 6.70, size: "1 ליטר", is_current: false },
    ]
  },
  "7290004131609": {
    product: { barcode: "7290004131609", name: "קוטג' תנובה 5%", brand: "תנובה", size: "250 גרם", category: "מוצרי חלב", image_url: "" },
    comparisons: [
      { store_name: "רמי לוי", store_chain: "rami_levy", price: 5.20, price_per_unit: 2.08, size: "250 גרם", is_current: false },
      { store_name: "אושר עד", store_chain: "osher_ad", price: 5.40, price_per_unit: 2.16, size: "250 גרם", is_current: false },
      { store_name: "ויקטורי", store_chain: "victory", price: 5.50, price_per_unit: 2.20, size: "250 גרם", is_current: false },
      { store_name: "חצי חינם", store_chain: "hatzi_hinam", price: 5.60, price_per_unit: 2.24, size: "250 גרם", is_current: false },
      { store_name: "שופרסל דיל", store_chain: "shufersal_deal", price: 5.70, price_per_unit: 2.28, size: "250 גרם", is_current: false },
      { store_name: "מגה", store_chain: "mega", price: 5.90, price_per_unit: 2.36, size: "250 גרם", is_current: false },
      { store_name: "שופרסל", store_chain: "shufersal", price: 6.10, price_per_unit: 2.44, size: "250 גרם", is_current: true },
      { store_name: "טיב טעם", store_chain: "tiv_taam", price: 6.30, price_per_unit: 2.52, size: "250 גרם", is_current: false },
    ]
  },
  "7290000307268": {
    product: { barcode: "7290000307268", name: "במבה אסם", brand: "אסם", size: "80 גרם", category: "חטיפים", image_url: "" },
    comparisons: [
      { store_name: "רמי לוי", store_chain: "rami_levy", price: 4.90, price_per_unit: 6.13, size: "80 גרם", is_current: false },
      { store_name: "אושר עד", store_chain: "osher_ad", price: 5.00, price_per_unit: 6.25, size: "80 גרם", is_current: false },
      { store_name: "חצי חינם", store_chain: "hatzi_hinam", price: 5.10, price_per_unit: 6.38, size: "80 גרם", is_current: false },
      { store_name: "ויקטורי", store_chain: "victory", price: 5.20, price_per_unit: 6.50, size: "80 גרם", is_current: false },
      { store_name: "שופרסל דיל", store_chain: "shufersal_deal", price: 5.30, price_per_unit: 6.63, size: "80 גרם", is_current: false },
      { store_name: "מגה", store_chain: "mega", price: 5.50, price_per_unit: 6.88, size: "80 גרם", is_current: false },
      { store_name: "יינות ביתן", store_chain: "yeinot_bitan", price: 5.60, price_per_unit: 7.00, size: "80 גרם", is_current: false },
      { store_name: "שופרסל", store_chain: "shufersal", price: 5.90, price_per_unit: 7.38, size: "80 גרם", is_current: true },
      { store_name: "טיב טעם", store_chain: "tiv_taam", price: 6.10, price_per_unit: 7.63, size: "80 גרם", is_current: false },
    ]
  },
  "7290000563534": {
    product: { barcode: "7290000563534", name: 'שמן זית שמן הבית', brand: "שמן הבית", size: '750 מ"ל', category: "שמנים", image_url: "" },
    comparisons: [
      { store_name: "רמי לוי", store_chain: "rami_levy", price: 24.90, price_per_unit: 3.32, size: '750 מ"ל', is_current: false },
      { store_name: "אושר עד", store_chain: "osher_ad", price: 25.50, price_per_unit: 3.40, size: '750 מ"ל', is_current: false },
      { store_name: "חצי חינם", store_chain: "hatzi_hinam", price: 26.20, price_per_unit: 3.49, size: '750 מ"ל', is_current: false },
      { store_name: "ויקטורי", store_chain: "victory", price: 26.90, price_per_unit: 3.59, size: '750 מ"ל', is_current: false },
      { store_name: "שופרסל דיל", store_chain: "shufersal_deal", price: 27.50, price_per_unit: 3.67, size: '750 מ"ל', is_current: false },
      { store_name: "מגה", store_chain: "mega", price: 27.50, price_per_unit: 3.67, size: '750 מ"ל', is_current: false },
      { store_name: "יינות ביתן", store_chain: "yeinot_bitan", price: 28.90, price_per_unit: 3.85, size: '750 מ"ל', is_current: false },
      { store_name: "שופרסל", store_chain: "shufersal", price: 29.90, price_per_unit: 3.99, size: '750 מ"ל', is_current: true },
      { store_name: "טיב טעם", store_chain: "tiv_taam", price: 30.90, price_per_unit: 4.12, size: '750 מ"ל', is_current: false },
    ]
  },
  "7290106809369": {
    product: { barcode: "7290106809369", name: "אבקת כביסה סנו מקסימה", brand: "סנו", size: '2.5 ק"ג', category: "ניקוי", image_url: "" },
    comparisons: [
      { store_name: "רמי לוי", store_chain: "rami_levy", price: 34.90, price_per_unit: 13.96, size: '2.5 ק"ג', is_current: false },
      { store_name: "אושר עד", store_chain: "osher_ad", price: 35.90, price_per_unit: 14.36, size: '2.5 ק"ג', is_current: false },
      { store_name: "חצי חינם", store_chain: "hatzi_hinam", price: 36.90, price_per_unit: 14.76, size: '2.5 ק"ג', is_current: false },
      { store_name: "שופרסל דיל", store_chain: "shufersal_deal", price: 37.90, price_per_unit: 15.16, size: '2.5 ק"ג', is_current: false },
      { store_name: "ויקטורי", store_chain: "victory", price: 37.90, price_per_unit: 15.16, size: '2.5 ק"ג', is_current: false },
      { store_name: "יינות ביתן", store_chain: "yeinot_bitan", price: 39.90, price_per_unit: 15.96, size: '2.5 ק"ג', is_current: false },
      { store_name: "מגה", store_chain: "mega", price: 40.90, price_per_unit: 16.36, size: '2.5 ק"ג', is_current: false },
      { store_name: "שופרסל", store_chain: "shufersal", price: 42.90, price_per_unit: 17.16, size: '2.5 ק"ג', is_current: true },
      { store_name: "טיב טעם", store_chain: "tiv_taam", price: 43.90, price_per_unit: 17.56, size: '2.5 ק"ג', is_current: false },
    ]
  },
  "7290000197067": {
    product: { barcode: "7290000197067", name: "קפה עלית נמס", brand: "עלית", size: "200 גרם", category: "קפה", image_url: "" },
    comparisons: [
      { store_name: "רמי לוי", store_chain: "rami_levy", price: 18.90, price_per_unit: 9.45, size: "200 גרם", is_current: false },
      { store_name: "אושר עד", store_chain: "osher_ad", price: 19.50, price_per_unit: 9.75, size: "200 גרם", is_current: false },
      { store_name: "חצי חינם", store_chain: "hatzi_hinam", price: 19.90, price_per_unit: 9.95, size: "200 גרם", is_current: false },
      { store_name: "ויקטורי", store_chain: "victory", price: 19.90, price_per_unit: 9.95, size: "200 גרם", is_current: false },
      { store_name: "שופרסל דיל", store_chain: "shufersal_deal", price: 20.90, price_per_unit: 10.45, size: "200 גרם", is_current: false },
      { store_name: "יינות ביתן", store_chain: "yeinot_bitan", price: 21.50, price_per_unit: 10.75, size: "200 גרם", is_current: false },
      { store_name: "מגה", store_chain: "mega", price: 21.90, price_per_unit: 10.95, size: "200 גרם", is_current: false },
      { store_name: "שופרסל", store_chain: "shufersal", price: 22.90, price_per_unit: 11.45, size: "200 גרם", is_current: true },
      { store_name: "טיב טעם", store_chain: "tiv_taam", price: 23.50, price_per_unit: 11.75, size: "200 גרם", is_current: false },
    ]
  },
  "7290000100517": {
    product: { barcode: "7290000100517", name: "סבון כלים פיירי", brand: "Fairy", size: '500 מ"ל', category: "ניקוי", image_url: "" },
    comparisons: [
      { store_name: "רמי לוי", store_chain: "rami_levy", price: 9.90, price_per_unit: 1.98, size: '500 מ"ל', is_current: false },
      { store_name: "אושר עד", store_chain: "osher_ad", price: 10.20, price_per_unit: 2.04, size: '500 מ"ל', is_current: false },
      { store_name: "חצי חינם", store_chain: "hatzi_hinam", price: 10.50, price_per_unit: 2.10, size: '500 מ"ל', is_current: false },
      { store_name: "ויקטורי", store_chain: "victory", price: 10.90, price_per_unit: 2.18, size: '500 מ"ל', is_current: false },
      { store_name: "שופרסל דיל", store_chain: "shufersal_deal", price: 11.20, price_per_unit: 2.24, size: '500 מ"ל', is_current: false },
      { store_name: "יינות ביתן", store_chain: "yeinot_bitan", price: 11.90, price_per_unit: 2.38, size: '500 מ"ל', is_current: false },
      { store_name: "מגה", store_chain: "mega", price: 12.50, price_per_unit: 2.50, size: '500 מ"ל', is_current: false },
      { store_name: "שופרסל", store_chain: "shufersal", price: 12.90, price_per_unit: 2.58, size: '500 מ"ל', is_current: true },
      { store_name: "טיב טעם", store_chain: "tiv_taam", price: 13.20, price_per_unit: 2.64, size: '500 מ"ל', is_current: false },
    ]
  },
};

// ===== SCREEN MANAGER =====
function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById('screen-' + id).classList.add('active');
}

function goHome() {
  stopScanner();
  showScreen('home');
  loadRecentScans();
}

function setStatus(msg, color) {
  const el = document.getElementById('api-status');
  el.style.display = 'block';
  el.style.background = color === 'green' ? '#e8f5e9' : color === 'red' ? '#fce4ec' : '#fff3e0';
  el.style.color = color === 'green' ? '#2e7d32' : color === 'red' ? '#c62828' : '#e65100';
  el.textContent = msg.substring(0, 100);
  setTimeout(() => { el.style.display = 'none'; }, 5000);
}

// ===== BARCODE SCANNER =====
let scannerRunning = false;
let lastDetectedCode = null;
let detectionHits = 0;
const REQUIRED_MATCHES = 3;

// בדיקת checksum של EAN-13
function validateEAN13(code) {
  if (!/^\d{13}$/.test(code)) return false;
  let sum = 0;
  for (let i = 0; i < 12; i++) {
    sum += parseInt(code[i]) * (i % 2 === 0 ? 1 : 3);
  }
  const check = (10 - (sum % 10)) % 10;
  return check === parseInt(code[12]);
}

function onBarcodeDetected(result) {
  const code = result?.codeResult?.code;
  const format = result?.codeResult?.format;

  if (!code) return;
  if (format !== 'ean_13' && !/^\d{13}$/.test(code)) return;
  if (!validateEAN13(code)) {
    console.log(`Barcode rejected (bad checksum): ${code}`);
    return;
  }

  if (code === lastDetectedCode) {
    detectionHits += 1;
  } else {
    lastDetectedCode = code;
    detectionHits = 1;
  }

  console.log(`Barcode: ${code} (${detectionHits}/${REQUIRED_MATCHES})`);
  const status = document.getElementById('scanner-status');
  status.textContent = `מזהה: ${code} (${detectionHits}/${REQUIRED_MATCHES})`;

  if (detectionHits >= REQUIRED_MATCHES) {
    if (navigator.vibrate) navigator.vibrate(200);
    status.textContent = `נמצא: ${code}`;
    lastDetectedCode = null;
    detectionHits = 0;
    stopScanner();
    searchProduct(code);
  }
}

function startBarcodeScanner() {
  showScreen('scanner');
  const status = document.getElementById('scanner-status');
  status.textContent = 'מפעיל מצלמה...';
  lastDetectedCode = null;
  detectionHits = 0;

  Quagga.offDetected(onBarcodeDetected);

  Quagga.init({
    inputStream: {
      type: 'LiveStream',
      target: document.getElementById('interactive'),
      constraints: {
        facingMode: 'environment',
        width: { ideal: 1280 },
        height: { ideal: 720 },
      },
      area: {
        top: '25%',
        right: '10%',
        left: '10%',
        bottom: '25%',
      },
    },
    decoder: {
      readers: ['ean_reader'],
      multiple: false,
    },
    locate: true,
    numOfWorkers: navigator.hardwareConcurrency || 4,
    frequency: 10,
    locator: {
      patchSize: 'small',
      halfSample: true,
    },
  }, (err) => {
    if (err) {
      status.textContent = 'שגיאה בגישה למצלמה. נסה ידנית.';
      console.error('Quagga init error:', err);
      return;
    }
    Quagga.start();
    scannerRunning = true;
    status.textContent = 'כוון את הברקוד למסגרת';
  });

  Quagga.onDetected(onBarcodeDetected);
}

function stopScanner() {
  if (scannerRunning) {
    Quagga.stop();
    scannerRunning = false;
  }
}

// ===== MANUAL SEARCH =====
function searchManual() {
  const val = document.getElementById('manual-barcode').value.trim();
  if (!val) return;
  searchProduct(val);
}

// ===== MAIN SEARCH FLOW =====
async function searchProduct(barcode) {
  showScreen('loading');
  const steps = ['step-identify', 'step-prices', 'step-compare'];
  const loadingText = document.getElementById('loading-text');
  steps.forEach(s => { document.getElementById(s).classList.remove('active', 'done'); });

  try {
    document.getElementById(steps[0]).classList.add('active');
    loadingText.textContent = `מחפש ברקוד: ${barcode}`;

    const result = await fetchPrices(barcode);

    document.getElementById(steps[0]).classList.replace('active', 'done');
    document.getElementById(steps[1]).classList.add('active');
    loadingText.textContent = 'בודק מחירים...';
    await delay(300);

    document.getElementById(steps[1]).classList.replace('active', 'done');
    document.getElementById(steps[2]).classList.add('active');
    loadingText.textContent = 'מחשב השוואה...';
    await delay(300);
    document.getElementById(steps[2]).classList.replace('active', 'done');

    if (!result || !result.product) {
      showError('המוצר לא נמצא', `ברקוד ${barcode} לא נמצא במאגרים. נסה ברקוד אחר.`);
      return;
    }

    saveToRecent(result.product, barcode);
    displayResults(result);

  } catch (err) {
    console.error('Search error:', err);
    showError('שגיאה', err.message || 'שגיאה לא צפויה');
  }
}

// ===== FETCH PRICES =====
async function fetchPrices(barcode) {
  if (DEMO_MODE) return fetchDemoPrices(barcode);

  const response = await fetch(`${API_BASE}/api/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ barcode }),
  });
  if (!response.ok) throw new Error(`Server error: ${response.status}`);
  return response.json();
}

async function fetchDemoPrices(barcode) {
  // 1. חפש ב-DB מקומי
  if (DEMO_PRODUCTS[barcode]) {
    const data = DEMO_PRODUCTS[barcode];
    return {
      product: data.product,
      current_store: "שופרסל",
      current_price: data.comparisons.find(c => c.is_current)?.price || data.comparisons[0].price,
      comparisons: data.comparisons,
    };
  }

  // 2. חפש ב-Open Food Facts (מידע אמיתי על המוצר)
  const offProduct = await lookupBarcode(barcode);
  const product = offProduct || {
    barcode: barcode,
    name: `מוצר (${barcode})`,
    brand: '',
    size: '',
    category: '',
    image_url: '',
  };
  const gen = generateDemoComparisons(product);
  return {
    product,
    current_store: "שופרסל",
    current_price: gen.find(c => c.is_current)?.price || gen[0].price,
    comparisons: gen,
  };
}

// ===== OPEN FOOD FACTS API =====
async function lookupBarcode(barcode) {
  try {
    const loadingText = document.getElementById('loading-text');
    loadingText.textContent = `מחפש מידע על ברקוד ${barcode}...`;

    const resp = await fetch(`https://world.openfoodfacts.org/api/v0/product/${barcode}.json`);
    const data = await resp.json();

    if (data.status !== 1) {
      console.log('Open Food Facts: product not found for', barcode);
      return null;
    }

    const p = data.product;
    const product = {
      barcode: barcode,
      name: p.product_name_he || p.product_name || 'מוצר',
      brand: p.brands || '',
      size: p.quantity || '',
      category: (p.categories_tags || [''])[0].replace('en:', ''),
      image_url: p.image_front_small_url || p.image_front_url || '',
    };

    console.log('Open Food Facts found:', product.name);
    loadingText.textContent = `נמצא: ${product.name}`;
    return product;
  } catch (err) {
    console.error('Open Food Facts error:', err);
    return null;
  }
}

// ===== HELPERS =====
function generateDemoComparisons(product) {
  const stores = [
    { name: "רמי לוי", chain: "rami_levy", factor: 0.88 },
    { name: "אושר עד", chain: "osher_ad", factor: 0.90 },
    { name: "חצי חינם", chain: "hatzi_hinam", factor: 0.92 },
    { name: "שופרסל דיל", chain: "shufersal_deal", factor: 0.93 },
    { name: "יינות ביתן", chain: "yeinot_bitan", factor: 0.95 },
    { name: "ויקטורי", chain: "victory", factor: 0.96 },
    { name: "מגה", chain: "mega", factor: 0.98 },
    { name: "שופרסל", chain: "shufersal", factor: 1.00 },
    { name: "טיב טעם", chain: "tiv_taam", factor: 1.02 },
  ];

  const categoryPrices = {
    'חלב': 6.5, 'מוצרי חלב': 7, 'חטיפים': 5.5, 'שמנים': 28,
    'ניקוי': 15, 'קפה': 22, 'לחם': 8, 'שתייה': 7, 'ירקות': 5,
    'בשר': 45, 'דגים': 35, 'פירות': 8, 'ממתקים': 10, 'תבלינים': 8,
  };
  const basePrice = categoryPrices[product.category] || 12;

  return stores.map((store) => {
    const jitter = 1 + (Math.random() - 0.5) * 0.10;
    const price = Math.round(basePrice * store.factor * jitter * 100) / 100;
    const sizeVal = parseFloat(product.size) || 1;
    return {
      store_name: store.name,
      store_chain: store.chain,
      price,
      price_per_unit: Math.round((price / sizeVal) * 100) / 100,
      size: product.size || "יחידה",
      is_current: store.chain === 'shufersal',
    };
  });
}

// ===== DISPLAY RESULTS =====
function displayResults(data) {
  const { product, current_store, current_price, comparisons } = data;

  document.getElementById('result-product-name').textContent = product.name;
  document.getElementById('result-product-brand').textContent = product.brand || '';
  document.getElementById('result-product-size').textContent = product.size || '';

  const img = document.getElementById('result-product-img');
  const placeholder = document.getElementById('product-img-placeholder');
  if (product.image_url) {
    img.src = product.image_url;
    img.style.display = '';
    placeholder.style.display = 'none';
  } else {
    img.style.display = 'none';
    placeholder.style.display = '';
  }

  document.getElementById('current-store').textContent = current_store || 'הסופר הנוכחי';
  document.getElementById('current-price').textContent = formatPrice(current_price);

  const sorted = [...comparisons].sort((a, b) => a.price - b.price);
  const best = sorted[0];

  document.getElementById('deal-title').textContent = `${best.store_name} - ${best.size}`;
  document.getElementById('deal-subtitle').textContent = best.price_per_unit ? `${formatPrice(best.price_per_unit)} ליחידה` : '';
  document.getElementById('deal-price').textContent = formatPrice(best.price);

  const table = document.getElementById('comparison-table');
  table.innerHTML = '';

  sorted.forEach((item, index) => {
    const isBest = index === 0;
    const isCurrent = item.is_current;
    const savings = current_price - item.price;
    const row = document.createElement('div');
    row.className = `comp-row ${isBest ? 'best' : ''} ${isCurrent ? 'current-row' : ''}`;

    let badge = '';
    if (isBest && !isCurrent) badge = '<span class="comp-badge badge-best">הכי זול</span>';
    if (isCurrent) badge = '<span class="comp-badge badge-here">אתה כאן</span>';
    if (!isBest && !isCurrent && savings > 0) badge = `<span class="comp-badge badge-save">חסכון ${formatPrice(savings)}</span>`;

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
        <div class="comp-per-unit">${item.price_per_unit ? formatPrice(item.price_per_unit) + ' ליחידה' : ''}</div>
      </div>
    `;
    table.appendChild(row);
  });

  const maxSavings = current_price - best.price;
  if (maxSavings > 0) {
    document.getElementById('savings-amount').textContent = formatPrice(maxSavings);
    document.getElementById('savings-desc').textContent = `לעומת ${current_store}`;
    document.getElementById('savings-card').style.display = '';
  } else {
    document.getElementById('savings-card').style.display = 'none';
  }

  showScreen('results');
}

// ===== RECENT SCANS =====
function saveToRecent(product, barcode) {
  let recent = JSON.parse(localStorage.getItem('recent_scans') || '[]');
  recent = recent.filter(r => r.barcode !== barcode);
  recent.unshift({ product, barcode, ts: Date.now() });
  recent = recent.slice(0, 10);
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
      <div style="flex:1">
        <div style="font-weight:600;font-size:0.95rem">${item.product?.name || 'מוצר'}</div>
        <div style="font-size:0.75rem;color:#777">${item.barcode} &middot; ${timeAgo(item.ts)}</div>
      </div>
    `;
    el.onclick = () => searchProduct(item.barcode);
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
  return '\u20AA' + parseFloat(n).toFixed(2);
}

function delay(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }

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
  console.log(`קנה חכם v${APP_VERSION} loaded`);
  loadRecentScans();
  document.getElementById('manual-barcode').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') searchManual();
  });
});
