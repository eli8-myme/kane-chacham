// ===== CONFIG =====
const API_BASE = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : 'https://your-backend.onrender.com';

const DEMO_MODE = true;
const APP_VERSION = '6';

// Gemini Vision API
const GEMINI_API_KEY = 'AIzaSyDsCxzuc1T31IsCkPq1wlz7YSxaLCmuqDs';
const GEMINI_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent';
let geminiAvailable = false;

// ===== DEMO DATABASE =====
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
    product: { barcode: "7290000563534", name: 'שמן זית שמן הבית', brand: "שמן הבית", size: '750 מ"ל', category: "שמנים", image_url: "" },
    comparisons: [
      { store_name: "רמי לוי", store_chain: "rami_levy", price: 24.90, price_per_unit: 3.32, size: '750 מ"ל', is_current: false },
      { store_name: "שופרסל", store_chain: "shufersal", price: 29.90, price_per_unit: 3.99, size: '750 מ"ל', is_current: true },
      { store_name: "ויקטורי", store_chain: "victory", price: 26.90, price_per_unit: 3.59, size: '750 מ"ל', is_current: false },
      { store_name: "מגה", store_chain: "mega", price: 27.50, price_per_unit: 3.67, size: '750 מ"ל', is_current: false },
    ]
  },
  "7290106809369": {
    product: { barcode: "7290106809369", name: "אבקת כביסה סנו מקסימה", brand: "סנו", size: '2.5 ק"ג', category: "ניקוי", image_url: "" },
    comparisons: [
      { store_name: "רמי לוי", store_chain: "rami_levy", price: 34.90, price_per_unit: 1.40, size: '2.5 ק"ג', is_current: false },
      { store_name: "שופרסל", store_chain: "shufersal", price: 42.90, price_per_unit: 1.72, size: '2.5 ק"ג', is_current: true },
      { store_name: "ויקטורי", store_chain: "victory", price: 37.90, price_per_unit: 1.52, size: '2.5 ק"ג', is_current: false },
      { store_name: "אושר עד", store_chain: "osher_ad", price: 35.90, price_per_unit: 1.44, size: '2.5 ק"ג', is_current: false },
      { store_name: "רמי לוי", store_chain: "rami_levy", price: 54.90, price_per_unit: 1.10, size: '5 ק"ג', is_current: false },
      { store_name: "שופרסל", store_chain: "shufersal", price: 64.90, price_per_unit: 1.30, size: '5 ק"ג', is_current: false },
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
    product: { barcode: "7290000100517", name: "סבון כלים פיירי", brand: "Fairy", size: '500 מ"ל', category: "ניקוי", image_url: "" },
    comparisons: [
      { store_name: "רמי לוי", store_chain: "rami_levy", price: 9.90, price_per_unit: 1.98, size: '500 מ"ל', is_current: false },
      { store_name: "שופרסל", store_chain: "shufersal", price: 12.90, price_per_unit: 2.58, size: '500 מ"ל', is_current: true },
      { store_name: "ויקטורי", store_chain: "victory", price: 10.90, price_per_unit: 2.18, size: '500 מ"ל', is_current: false },
      { store_name: "שופרסל", store_chain: "shufersal", price: 19.90, price_per_unit: 1.99, size: "1 ליטר", is_current: false },
      { store_name: "רמי לוי", store_chain: "rami_levy", price: 16.90, price_per_unit: 1.69, size: "1 ליטר", is_current: false },
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
  stopCamera();
  showScreen('home');
  loadRecentScans();
}

function setStatus(msg, color) {
  const el = document.getElementById('api-status');
  el.style.display = 'block';
  el.style.background = color === 'green' ? '#e8f5e9' : color === 'red' ? '#fce4ec' : '#fff3e0';
  el.style.color = color === 'green' ? '#2e7d32' : color === 'red' ? '#c62828' : '#e65100';
  el.textContent = msg.substring(0, 100); // חסום הודעות ארוכות
  setTimeout(() => { el.style.display = 'none'; }, 5000);
}

// ===== BARCODE SCANNER =====
let scannerRunning = false;

// גלובלי - מונע handlers כפולים
let barcodeDetections = {};
const REQUIRED_MATCHES = 3;

function onBarcodeDetected(result) {
  const code = result.codeResult.code;
  if (!code || code.length < 8) return;

  barcodeDetections[code] = (barcodeDetections[code] || 0) + 1;
  console.log(`Barcode: ${code} (${barcodeDetections[code]}/${REQUIRED_MATCHES})`);

  const status = document.getElementById('scanner-status');
  status.textContent = `מזהה: ${code} (${barcodeDetections[code]}/${REQUIRED_MATCHES})`;

  if (barcodeDetections[code] >= REQUIRED_MATCHES) {
    if (navigator.vibrate) navigator.vibrate(200);
    status.textContent = `אומת: ${code}`;
    barcodeDetections = {};
    stopScanner();
    searchProduct(code, 'barcode');
  }
}

function startBarcodeScanner() {
  showScreen('scanner');
  const status = document.getElementById('scanner-status');
  status.textContent = 'מפעיל מצלמה...';
  barcodeDetections = {};

  // הסר handlers ישנים לפני הוספת חדש
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
    },
    decoder: {
      readers: ['ean_reader', 'ean_8_reader'],
      multiple: false,
    },
    locate: true,
    numOfWorkers: 2,
    frequency: 10,
    locator: { patchSize: 'medium', halfSample: true },
  }, (err) => {
    if (err) {
      status.textContent = 'שגיאה בגישה למצלמה. נסה ידנית.';
      console.error('Quagga init error:', err);
      return;
    }
    Quagga.start();
    scannerRunning = true;
    status.textContent = 'מחפש ברקוד... כוון את הברקוד למסגרת';
  });

  Quagga.onDetected(onBarcodeDetected);
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
    document.getElementById('camera-video').srcObject = stream;
  }).catch(err => {
    console.error('Camera error:', err);
    showError('לא ניתן לגשת למצלמה', err.message);
  });
}

function captureImage() {
  const video = document.getElementById('camera-video');
  const canvas = document.getElementById('camera-canvas');
  canvas.width = video.videoWidth;
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
  const loadingText = document.getElementById('loading-text');
  steps.forEach(s => { document.getElementById(s).classList.remove('active', 'done'); });

  try {
    document.getElementById(steps[0]).classList.add('active');
    loadingText.textContent = type === 'image' ? 'שולח תמונה ל-AI...' : `מחפש ברקוד: ${data}`;

    let result;
    if (type === 'barcode') {
      result = await fetchPrices({ barcode: data });
    } else {
      const base64 = data.split(',')[1];
      if (!base64) { showError('שגיאה בתמונה', 'נסה לצלם שוב.'); return; }
      result = await fetchPrices({ image_base64: base64 });
    }

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
      const detail = type === 'image'
        ? 'לא הצלחנו לזהות את המוצר בתמונה. נסה לסרוק את הברקוד במקום, או הכנס ברקוד ידנית.'
        : `ברקוד ${data} לא נמצא במאגרים. נסה לצלם את המוצר או הכנס ברקוד אחר.`;
      showError('המוצר לא נמצא', detail);
      return;
    }

    saveToRecent(result.product, data, type);
    displayResults(result);

  } catch (err) {
    console.error('Search error:', err);
    showError('שגיאה', err.message || 'שגיאה לא צפויה');
  }
}

// ===== FETCH PRICES =====
async function fetchPrices(payload) {
  if (DEMO_MODE) return fetchDemoPrices(payload);

  const response = await fetch(`${API_BASE}/api/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error(`Server error: ${response.status}`);
  return response.json();
}

async function fetchDemoPrices(payload) {
  if (payload.barcode) {
    // 1. חפש ב-DB מקומי
    if (DEMO_PRODUCTS[payload.barcode]) {
      const data = DEMO_PRODUCTS[payload.barcode];
      return {
        product: data.product,
        current_store: "שופרסל",
        current_price: data.comparisons.find(c => c.is_current)?.price || data.comparisons[0].price,
        comparisons: data.comparisons,
      };
    }

    // 2. חפש ב-Open Food Facts (מידע אמיתי על המוצר)
    const offProduct = await lookupBarcode(payload.barcode);
    const product = offProduct || {
      barcode: payload.barcode,
      name: `מוצר (${payload.barcode})`,
      brand: '',
      size: '',
      category: '',
      image_url: '',
    };
    const gen = generateDemoComparisons(product);
    return {
      product,
      current_store: gen[0].store_name,
      current_price: gen[0].price,
      comparisons: gen,
    };
  }

  if (payload.image_base64) {
    const identified = await identifyWithGemini(payload.image_base64);

    if (!identified) {
      // Gemini לא זמין או לא זיהה - החזר מוצר גנרי במקום שגיאה
      const product = {
        barcode: null,
        name: 'מוצר שצולם (לא זוהה)',
        brand: '',
        size: '',
        category: '',
        image_url: '',
      };
      const gen = generateDemoComparisons(product);
      return { product, current_store: gen[0].store_name, current_price: gen[0].price, comparisons: gen };
    }

    // חפש ב-DB
    if (identified.barcode && DEMO_PRODUCTS[identified.barcode]) {
      const data = DEMO_PRODUCTS[identified.barcode];
      return {
        product: data.product,
        current_store: "שופרסל",
        current_price: data.comparisons.find(c => c.is_current)?.price || data.comparisons[0].price,
        comparisons: data.comparisons,
      };
    }

    const match = findProductByName(identified.name);
    if (match) {
      return {
        product: { ...match.product, name: identified.name || match.product.name },
        current_store: "שופרסל",
        current_price: match.comparisons.find(c => c.is_current)?.price || match.comparisons[0].price,
        comparisons: match.comparisons,
      };
    }

    // מוצר זוהה - צור השוואה עם הנתונים שזוהו
    const product = {
      barcode: identified.barcode || null,
      name: identified.name || 'מוצר שזוהה',
      brand: identified.brand || '',
      size: identified.size || '',
      category: identified.category || '',
      image_url: '',
    };
    const gen = generateDemoComparisons(product);
    return { product, current_store: gen[0].store_name, current_price: gen[0].price, comparisons: gen };
  }

  return null;
}

// ===== OPEN FOOD FACTS API - חיפוש ברקוד חינמי =====
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

// ===== GEMINI VISION =====
async function identifyWithGemini(base64Image) {
  const loadingText = document.getElementById('loading-text');

  if (!GEMINI_API_KEY) {
    loadingText.textContent = 'מפתח Gemini לא מוגדר - זיהוי תמונה לא זמין';
    return null;
  }
  if (!geminiAvailable) {
    loadingText.textContent = 'Gemini API לא זמין כרגע - נסה סריקת ברקוד';
    return null;
  }

  try {
    loadingText.textContent = 'שולח תמונה ל-AI לזיהוי...';
    console.log('Sending image to Gemini, size:', Math.round(base64Image.length / 1024) + 'KB');

    const response = await fetch(`${GEMINI_URL}?key=${GEMINI_API_KEY}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{
          parts: [
            { text: `You are an expert at identifying Israeli supermarket products.
Look at the image and identify the product.
Return ONLY valid JSON (no markdown, no backticks, no extra text) in this format:
{"name":"product name in Hebrew","brand":"brand name","size":"size description","size_value":500,"size_unit":"g","barcode":"barcode if visible or null","category":"category in Hebrew","price":"price if visible on tag or null"}
If you cannot identify the product return: {"error":"cannot identify"}` },
            { inline_data: { mime_type: 'image/jpeg', data: base64Image } }
          ]
        }],
        generationConfig: { temperature: 0.1, maxOutputTokens: 512 }
      })
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      const errMsg = errData.error?.message || `status ${response.status}`;
      console.error('Gemini API error:', errMsg);
      if (errMsg.includes('quota') || errMsg.includes('Quota')) {
        geminiAvailable = false;
        loadingText.textContent = 'מכסת AI חינמית נגמרה. נסה סריקת ברקוד.';
      } else {
        loadingText.textContent = 'שגיאת זיהוי תמונה';
      }
      return null;
    }

    const data = await response.json();
    let text = data.candidates?.[0]?.content?.parts?.[0]?.text || '';
    console.log('Gemini raw:', text);

    if (!text) { loadingText.textContent = 'AI לא החזיר תשובה'; return null; }

    text = text.trim();
    if (text.startsWith('```')) {
      text = text.replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/, '');
    }

    const result = JSON.parse(text);
    if (result.error) {
      loadingText.textContent = 'AI לא הצליח לזהות את המוצר';
      return null;
    }

    loadingText.textContent = `זוהה: ${result.name || 'מוצר'}`;
    console.log('Gemini identified:', result);
    return result;

  } catch (err) {
    console.error('Gemini error:', err);
    loadingText.textContent = `שגיאת זיהוי: ${err.message}`;
    return null;
  }
}

// ===== HELPERS =====
function findProductByName(name) {
  if (!name) return null;
  const lower = name.toLowerCase();
  for (const key of Object.keys(DEMO_PRODUCTS)) {
    const p = DEMO_PRODUCTS[key].product;
    if (lower.includes(p.name.toLowerCase()) || p.name.toLowerCase().includes(lower) ||
        (p.brand && lower.includes(p.brand.toLowerCase()))) {
      return DEMO_PRODUCTS[key];
    }
  }
  const words = lower.split(/\s+/).filter(w => w.length > 2);
  for (const key of Object.keys(DEMO_PRODUCTS)) {
    const p = DEMO_PRODUCTS[key].product;
    const txt = `${p.name} ${p.brand} ${p.category}`.toLowerCase();
    if (words.filter(w => txt.includes(w)).length >= 2) return DEMO_PRODUCTS[key];
  }
  return null;
}

function generateDemoComparisons(product) {
  const stores = ["שופרסל", "רמי לוי", "ויקטורי", "מגה", "יינות ביתן"];
  const basePrice = 8 + Math.random() * 35;
  return stores.map((store, i) => {
    const price = Math.round((basePrice * (0.85 + Math.random() * 0.35)) * 100) / 100;
    return {
      store_name: store, store_chain: store, price,
      price_per_unit: Math.round((price / 5) * 100) / 100,
      size: product.size || "יחידה", is_current: i === 0,
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

  const sorted = [...comparisons].sort((a, b) => (a.price_per_unit || a.price) - (b.price_per_unit || b.price));
  const best = sorted[0];

  document.getElementById('deal-title').textContent = `${best.store_name} - ${best.size}`;
  document.getElementById('deal-subtitle').textContent = best.price_per_unit ? `${formatPrice(best.price_per_unit)} ל-100 יח'` : '';
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
        <div class="comp-per-unit">${item.price_per_unit ? formatPrice(item.price_per_unit) + " ל-100 יח'" : ''}</div>
      </div>
    `;
    table.appendChild(row);
  });

  const maxSavings = current_price - best.price;
  if (maxSavings > 0) {
    document.getElementById('savings-amount').textContent = formatPrice(maxSavings);
    document.getElementById('savings-desc').textContent = `לעומת ${best.store_name}`;
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
    if (item.type === 'barcode' && item.data) el.onclick = () => searchProduct(item.data, 'barcode');
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

// ===== TEST & INIT =====
async function testGeminiAPI() {
  const banner = document.querySelector('.demo-banner');
  // לא מבזבזים quota על טסט - רק בודקים בפעם הראשונה שמשתמשים
  geminiAvailable = !!GEMINI_API_KEY;
  if (banner) banner.textContent = 'גרסת הדגמה - סרוק ברקוד או צלם מוצר';
  console.log('Gemini key present:', geminiAvailable);
}

document.addEventListener('DOMContentLoaded', () => {
  console.log(`קנה חכם v${APP_VERSION} loaded`);
  loadRecentScans();
  testGeminiAPI();
  document.getElementById('manual-barcode').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') searchManual();
  });
});
