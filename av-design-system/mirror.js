/**
 * AV Design System · mirror.js
 * Captura um site (inclusive SPA) como {slug}.html + assets/ locais, autossuficiente.
 *
 * Estratégia:
 *  1. Shim de IntersectionObserver injetado ANTES do load → toda animação de
 *     reveal (blur/fade/slide/AOS) dispara na hora, nada congela invisível.
 *  2. Render headless (Chromium) + scroll para disparar lazy-load.
 *  3. Finaliza animações Web Animations API e neutraliza estados de hidden.
 *  4. Baixa assets em PARALELO (pool de concorrência) → rápido.
 *  5. Reescreve URLs para ./assets/ e remove scripts (evita re-hidratação da SPA).
 */
const { chromium } = require('playwright');
const fs     = require('fs');
const path   = require('path');
const https  = require('https');
const http   = require('http');
const crypto = require('crypto');

const [,, siteUrl, outputDir, slug] = process.argv;
if (!siteUrl || !outputDir || !slug) {
  console.error('Uso: node mirror.js <url> <output-dir> <slug>'); process.exit(1);
}

const assetsDir = path.join(outputDir, 'assets');
fs.mkdirSync(assetsDir, { recursive: true });

const origin     = new URL(siteUrl).origin;
const downloaded = {};   // url → local rel path (./assets/x)
const inflight   = {};   // url → Promise (dedup de downloads concorrentes)

// Trackers/ads que não devem ser baixados
const SKIP = ['googletagmanager','google-analytics','facebook.net','facebook.com/tr',
              'hotjar','clarity.ms','doubleclick','googlesyndication','googleadservices',
              'connect.facebook','twitter.com/i/','analytics.','/gtag/'];

const CONCURRENCY = 12;            // downloads simultâneos
const MAX_BYTES   = 25 * 1024 * 1024; // ignora assets individuais > 25MB

function safeFilename(u) {
  try {
    const p    = new URL(u).pathname;
    const ext  = path.extname(p);
    const base = path.basename(p, ext).replace(/[^a-z0-9_\-]/gi, '_').slice(0, 60);
    let name = (base || 'asset') + ext;
    let dest = path.join(assetsDir, name);
    let i = 1;
    while (fs.existsSync(dest) && downloaded[dest] !== u) {
      name = `${base || 'asset'}_${i++}${ext}`;
      dest = path.join(assetsDir, name);
    }
    return name;
  } catch (_) {
    return crypto.randomBytes(4).toString('hex') + '.bin';
  }
}

function fetchBuf(url) {
  return new Promise(resolve => {
    const lib = url.startsWith('https') ? https : http;
    try {
      const req = lib.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' }, timeout: 12000 }, res => {
        if (res.statusCode !== 200) { res.resume(); resolve(null); return; }
        const len = parseInt(res.headers['content-length'] || '0', 10);
        if (len && len > MAX_BYTES) { res.destroy(); resolve(null); return; }
        const buf = []; let total = 0;
        res.on('data', c => {
          total += c.length;
          if (total > MAX_BYTES) { res.destroy(); resolve(null); return; }
          buf.push(c);
        });
        res.on('end', () => resolve({ buf: Buffer.concat(buf), ct: res.headers['content-type'] || '' }));
        res.on('error', () => resolve(null));
      });
      req.on('error', () => resolve(null));
      req.on('timeout', () => { req.destroy(); resolve(null); });
    } catch (_) { resolve(null); }
  });
}

// Dedup: chamadas concorrentes para a mesma URL compartilham a mesma Promise
function saveAsset(assetUrl) {
  if (inflight[assetUrl] !== undefined) return inflight[assetUrl];
  inflight[assetUrl] = _saveAsset(assetUrl);
  return inflight[assetUrl];
}

async function _saveAsset(assetUrl) {
  if (SKIP.some(s => assetUrl.includes(s))) return null;
  if (assetUrl.startsWith('data:')) return null;

  const result = await fetchBuf(assetUrl);
  if (!result) return null;

  const filename = safeFilename(assetUrl);
  const dest     = path.join(assetsDir, filename);
  fs.writeFileSync(dest, result.buf);
  const local = `./assets/${filename}`;
  downloaded[assetUrl] = local;

  // Se é CSS, resolve url() internas (absolutas e relativas) em paralelo
  if (result.ct.includes('css') || filename.endsWith('.css')) {
    let css = result.buf.toString('utf8');
    const absRe = /url\(["']?(https?:\/\/[^"')]+)["']?\)/g;
    const relRe = /url\(["']?((?:\.\.?\/|\/)[^"')]+)["']?\)/g;
    const abs = [...css.matchAll(absRe)].map(m => m[1]);
    const rel = [...css.matchAll(relRe)].map(m => m[1]);
    await Promise.all(abs.map(async u => {
      const nested = await saveAsset(u);
      if (nested) css = css.split(u).join(nested);
    }));
    await Promise.all(rel.map(async r => {
      try {
        const absUrl = r.startsWith('/') ? origin + r : new URL(r, assetUrl).href;
        const nested = await saveAsset(absUrl);
        if (nested) css = css.split(r).join(nested);
      } catch (_) {}
    }));
    fs.writeFileSync(dest, css);
  }

  return local;
}

// Pool de concorrência: processa `items` com no máx `n` workers simultâneos
async function pool(items, worker, n = CONCURRENCY) {
  const arr = [...items];
  let idx = 0;
  async function run() {
    while (idx < arr.length) {
      const i = idx++;
      try { await worker(arr[i]); } catch (_) {}
    }
  }
  await Promise.all(Array.from({ length: Math.min(n, arr.length) }, run));
}

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport:  { width: 1440, height: 900 },
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
  });

  // ── FIX UNIVERSAL DE REVEAL ──────────────────────────────────────────
  // Substitui IntersectionObserver para reportar tudo como visível na hora.
  // Faz qualquer lib de reveal (blur/fade/slide/AOS/scroll) disparar de imediato,
  // independente de scroll → nenhuma dobra congela borrada/invisível.
  await context.addInitScript(() => {
    const Real = window.IntersectionObserver;
    window.IntersectionObserver = class {
      constructor(cb, opts) { this._cb = cb; this._opts = opts; this._els = new Set(); }
      observe(el) {
        this._els.add(el);
        const cb = this._cb, self = this;
        Promise.resolve().then(() => {
          try {
            const r = el.getBoundingClientRect ? el.getBoundingClientRect() : {};
            cb([{ isIntersecting: true, intersectionRatio: 1, target: el,
                  boundingClientRect: r, intersectionRect: r, rootBounds: r, time: 0 }], self);
          } catch (_) {}
        });
      }
      unobserve(el) { this._els.delete(el); }
      disconnect() { this._els.clear(); }
      takeRecords() { return []; }
    };
    window.__RealIO = Real;
  });

  const page = await context.newPage();

  // Intercepta assets via respostas de rede
  const assetQueue = new Set();
  page.on('response', resp => {
    try {
      const u  = resp.url();
      const ct = resp.headers()['content-type'] || '';
      if (resp.status() !== 200) return;
      if (ct.includes('text/html')) return;
      if (u.startsWith('data:')) return;
      if (SKIP.some(s => u.includes(s))) return;
      assetQueue.add(u);
    } catch (_) {}
  });

  console.error(`Renderizando ${siteUrl} ...`);
  await page.goto(siteUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});

  // Scroll para disparar lazy-loads (rápido)
  await page.evaluate(async () => {
    await new Promise(resolve => {
      let y = 0;
      const t = setInterval(() => {
        window.scrollBy(0, 400);
        y += 400;
        if (y >= document.body.scrollHeight) { clearInterval(t); resolve(); }
      }, 16);
    });
    window.scrollTo(0, 0);
  });
  await page.waitForLoadState('networkidle', { timeout: 8000 }).catch(() => {});

  // Finaliza animações WAAPI + neutraliza hidden remanescente direto no DOM
  await page.evaluate(() => {
    try { document.getAnimations().forEach(a => { try { a.finish(); } catch (_) {} }); } catch (_) {}
    // Força elementos ainda invisíveis (opacity 0 ou blur de reveal) ao estado final
    document.querySelectorAll('*').forEach(el => {
      const s = getComputedStyle(el);
      if (parseFloat(s.opacity) === 0) el.style.setProperty('opacity', '1', 'important');
      if (s.filter && s.filter.includes('blur') && parseFloat(s.opacity) < 1)
        el.style.setProperty('filter', 'none', 'important');
      if (s.visibility === 'hidden') el.style.setProperty('visibility', 'visible', 'important');
    });
  });
  await page.waitForTimeout(300);

  let html = await page.content();
  await browser.close();

  // Baixa assets interceptados EM PARALELO
  console.error(`Baixando ${assetQueue.size} assets...`);
  await pool(assetQueue, saveAsset);

  // Assets extras referenciados no HTML (caminhos relativos à raiz)
  const srcRe = /(?:src|href)=["'](\/[^"'?#\s]+\.(?:png|jpg|jpeg|gif|webp|svg|ico|avif|css|js|woff2?|ttf))["']/gi;
  const extra = new Set();
  let m;
  while ((m = srcRe.exec(html)) !== null) {
    const full = origin + m[1];
    if (!downloaded[full]) extra.add(full);
  }
  if (extra.size) {
    console.error(`Baixando ${extra.size} assets adicionais...`);
    await pool(extra, saveAsset);
  }

  // ── Reescreve URLs no HTML ───────────────────────────────────────────
  for (const [orig, local] of Object.entries(downloaded)) {
    html = html.split(orig).join(local);
  }
  for (const [orig, local] of Object.entries(downloaded)) {
    try {
      const pathname = new URL(orig).pathname;
      const esc = pathname.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      html = html.replace(new RegExp(`(src|href)="${esc}"`, 'g'), `$1="${local}"`);
      html = html.replace(new RegExp(`(src|href)='${esc}'`, 'g'), `$1='${local}'`);
    } catch (_) {}
  }

  // Remove scripts (evita router/re-hidratação da SPA brigar com o snapshot)
  html = html.replace(/<script\b[^>]*>([\s\S]*?)<\/script>/gi, '');
  html = html.replace(/<script\b[^>]*>/gi, '');

  // Remove crossorigin de tags que apontam para assets locais
  html = html.replace(/(<(?:link|script)[^>]*\.\/assets\/[^>]*?)\s+crossorigin(?:="[^"]*"|='[^']*'|="")?/gi, '$1');

  // Fallback CSS: garante estado visível mesmo se algo escapou
  html = html.replace('</head>', `<style>
[style*="opacity: 0"],[style*="opacity:0"]{opacity:1!important}
[style*="visibility: hidden"],[style*="visibility:hidden"]{visibility:visible!important}
</style></head>`);

  const outFile = path.join(outputDir, `${slug}.html`);
  fs.writeFileSync(outFile, html, 'utf8');

  const nAssets = fs.readdirSync(assetsDir).length;
  const sizekb  = Math.round(fs.statSync(outFile).size / 1024);
  console.log(`OK:${outFile}`);
  console.log(`ASSETS:${nAssets}`);
  console.log(`SIZE:${sizekb}KB`);
})().catch(err => { console.error(err && err.stack || err); process.exit(1); });
