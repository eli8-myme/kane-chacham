// ===== CONFIG =====
const API_BASE = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : 'https://your-backend.onrender.com'; // יתעדכן בהעלאה

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
  const response = await fetch(`${API_BASE}/api/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) throw new Error(`Server error: ${response.status}`);
  return response.json();
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
