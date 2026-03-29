const $ = (sel, el = document) => el.querySelector(sel);

// ─── Category placeholder SVG art ────────────────────────────────────────────
const _CAT_SVG = {
  gpu: `<svg viewBox="0 0 160 90" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><rect x="6" y="28" width="148" height="48" rx="4"/><circle cx="48" cy="52" r="17"/><circle cx="48" cy="52" r="6"/><circle cx="104" cy="52" r="17"/><circle cx="104" cy="52" r="6"/><rect x="6" y="18" width="148" height="13" rx="2"/><rect x="14" y="76" width="52" height="7" rx="1"/><rect x="118" y="15" width="22" height="8" rx="1"/></svg>`,

  cpu: `<svg viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><rect x="22" y="22" width="56" height="56" rx="3"/><rect x="30" y="30" width="40" height="40" rx="2"/><line x1="34" y1="22" x2="34" y2="12"/><line x1="44" y1="22" x2="44" y2="12"/><line x1="56" y1="22" x2="56" y2="12"/><line x1="66" y1="22" x2="66" y2="12"/><line x1="34" y1="78" x2="34" y2="88"/><line x1="44" y1="78" x2="44" y2="88"/><line x1="56" y1="78" x2="56" y2="88"/><line x1="66" y1="78" x2="66" y2="88"/><line x1="22" y1="34" x2="12" y2="34"/><line x1="22" y1="44" x2="12" y2="44"/><line x1="22" y1="56" x2="12" y2="56"/><line x1="22" y1="66" x2="12" y2="66"/><line x1="78" y1="34" x2="88" y2="34"/><line x1="78" y1="44" x2="88" y2="44"/><line x1="78" y1="56" x2="88" y2="56"/><line x1="78" y1="66" x2="88" y2="66"/></svg>`,

  ram: `<svg viewBox="0 0 80 120" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><rect x="12" y="14" width="56" height="88" rx="2"/><line x1="12" y1="96" x2="68" y2="96"/><rect x="20" y="24" width="8" height="10" rx="1"/><rect x="36" y="24" width="8" height="10" rx="1"/><rect x="52" y="24" width="8" height="10" rx="1"/><rect x="20" y="42" width="8" height="10" rx="1"/><rect x="36" y="42" width="8" height="10" rx="1"/><rect x="52" y="42" width="8" height="10" rx="1"/><rect x="20" y="60" width="8" height="10" rx="1"/><rect x="36" y="60" width="8" height="10" rx="1"/><rect x="52" y="60" width="8" height="10" rx="1"/><line x1="20" y1="102" x2="20" y2="112"/><line x1="30" y1="102" x2="30" y2="112"/><line x1="40" y1="102" x2="40" y2="112"/><line x1="50" y1="102" x2="50" y2="112"/><line x1="60" y1="102" x2="60" y2="112"/></svg>`,

  ssd: `<svg viewBox="0 0 160 80" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><rect x="8" y="22" width="144" height="40" rx="5"/><rect x="18" y="30" width="32" height="22" rx="2"/><circle cx="75" cy="41" r="11"/><circle cx="75" cy="41" r="4"/><rect x="98" y="32" width="38" height="10" rx="1"/><rect x="98" y="48" width="26" height="6" rx="1"/><line x1="14" y1="62" x2="14" y2="72"/><line x1="22" y1="62" x2="22" y2="72"/><line x1="30" y1="62" x2="30" y2="72"/><line x1="38" y1="62" x2="38" y2="72"/><line x1="46" y1="62" x2="46" y2="72"/></svg>`,

  monitor: `<svg viewBox="0 0 160 110" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><rect x="10" y="8" width="140" height="78" rx="6"/><rect x="18" y="16" width="124" height="62" rx="2"/><line x1="80" y1="86" x2="80" y2="100"/><rect x="52" y="100" width="56" height="7" rx="3"/></svg>`,

  mouse: `<svg viewBox="0 0 80 120" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><path d="M40 10 C16 10 10 38 10 65 C10 92 22 110 40 110 C58 110 70 92 70 65 C70 38 64 10 40 10Z"/><line x1="40" y1="10" x2="40" y2="56"/><rect x="31" y="32" width="18" height="24" rx="9"/><line x1="40" y1="32" x2="40" y2="56"/></svg>`,

  keyboard: `<svg viewBox="0 0 160 80" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><rect x="8" y="15" width="144" height="52" rx="6"/><rect x="18" y="25" width="10" height="10" rx="1"/><rect x="33" y="25" width="10" height="10" rx="1"/><rect x="48" y="25" width="10" height="10" rx="1"/><rect x="63" y="25" width="10" height="10" rx="1"/><rect x="78" y="25" width="10" height="10" rx="1"/><rect x="93" y="25" width="10" height="10" rx="1"/><rect x="108" y="25" width="10" height="10" rx="1"/><rect x="123" y="25" width="14" height="10" rx="1"/><rect x="18" y="41" width="14" height="10" rx="1"/><rect x="37" y="41" width="10" height="10" rx="1"/><rect x="52" y="41" width="10" height="10" rx="1"/><rect x="67" y="41" width="10" height="10" rx="1"/><rect x="82" y="41" width="10" height="10" rx="1"/><rect x="97" y="41" width="10" height="10" rx="1"/><rect x="112" y="41" width="10" height="10" rx="1"/><rect x="127" y="41" width="16" height="10" rx="1"/><rect x="30" y="55" width="100" height="8" rx="1"/></svg>`,

  laptop: `<svg viewBox="0 0 160 110" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><rect x="20" y="10" width="120" height="76" rx="4"/><rect x="28" y="18" width="104" height="60" rx="2"/><rect x="5" y="86" width="150" height="12" rx="3"/><rect x="58" y="86" width="44" height="4" rx="2"/></svg>`,

  cooler: `<svg viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="40"/><circle cx="50" cy="50" r="12"/><path d="M50 10 C62 30 72 38 50 50" stroke-linecap="round"/><path d="M90 50 C70 62 62 72 50 50" stroke-linecap="round"/><path d="M50 90 C38 70 28 62 50 50" stroke-linecap="round"/><path d="M10 50 C30 38 38 28 50 50" stroke-linecap="round"/></svg>`,

  psu: `<svg viewBox="0 0 130 100" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><rect x="8" y="12" width="114" height="72" rx="5"/><circle cx="42" cy="48" r="20"/><circle cx="42" cy="48" r="7"/><rect x="72" y="26" width="36" height="12" rx="2"/><rect x="72" y="46" width="36" height="12" rx="2"/><line x1="80" y1="84" x2="75" y2="97"/><line x1="88" y1="84" x2="88" y2="97"/><line x1="96" y1="84" x2="101" y2="97"/></svg>`,

  motherboard: `<svg viewBox="0 0 130 130" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><rect x="8" y="8" width="114" height="114" rx="3"/><rect x="18" y="18" width="40" height="40" rx="2"/><rect x="66" y="18" width="46" height="13" rx="1"/><rect x="66" y="36" width="46" height="13" rx="1"/><rect x="66" y="54" width="46" height="13" rx="1"/><rect x="18" y="66" width="40" height="15" rx="2"/><rect x="18" y="90" width="94" height="10" rx="1"/><circle cx="112" cy="112" r="6"/><circle cx="18" cy="112" r="6"/></svg>`,

  headset: `<svg viewBox="0 0 120 110" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><path d="M20 62 C20 28 100 28 100 62"/><rect x="8" y="58" width="22" height="30" rx="8"/><rect x="90" y="58" width="22" height="30" rx="8"/><line x1="90" y1="100" x2="90" y2="110"/><line x1="78" y1="110" x2="102" y2="110"/></svg>`,

  controller: `<svg viewBox="0 0 160 90" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><path d="M32 46 C20 20 10 18 8 34 C5 54 15 70 36 70 C52 68 62 55 80 55 C98 55 108 68 124 70 C145 70 155 54 152 34 C150 18 140 20 128 46 Z"/><line x1="48" y1="36" x2="48" y2="52"/><line x1="40" y1="44" x2="56" y2="44"/><circle cx="112" cy="36" r="4"/><circle cx="122" cy="45" r="4"/><circle cx="102" cy="45" r="4"/><circle cx="112" cy="54" r="4"/><rect x="68" y="36" width="10" height="9" rx="1"/><rect x="82" y="36" width="10" height="9" rx="1"/></svg>`,

  network: `<svg viewBox="0 0 130 100" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><rect x="14" y="54" width="102" height="32" rx="5"/><circle cx="30" cy="70" r="4" fill="currentColor" stroke="none"/><circle cx="46" cy="70" r="4" fill="currentColor" stroke="none"/><circle cx="62" cy="70" r="4" fill="currentColor" stroke="none"/><line x1="65" y1="54" x2="65" y2="30"/><path d="M49 36 C49 24 81 24 81 36"/><path d="M37 42 C37 16 93 16 93 42"/></svg>`,

  case: `<svg viewBox="0 0 80 130" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><rect x="12" y="8" width="56" height="116" rx="4"/><circle cx="40" cy="34" r="12"/><circle cx="40" cy="34" r="4"/><rect x="20" y="56" width="18" height="10" rx="2"/><rect x="20" y="72" width="18" height="10" rx="2"/><rect x="20" y="88" width="18" height="10" rx="2"/><line x1="62" y1="56" x2="62" y2="106"/></svg>`,

  hdd: `<svg viewBox="0 0 140 80" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><rect x="8" y="12" width="124" height="56" rx="5"/><circle cx="88" cy="40" r="22"/><circle cx="88" cy="40" r="8"/><circle cx="88" cy="20" r="3"/><rect x="18" y="26" width="38" height="8" rx="1"/><rect x="18" y="40" width="38" height="8" rx="1"/></svg>`,

  default: `<svg viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><rect x="15" y="15" width="70" height="70" rx="4"/><rect x="28" y="28" width="44" height="44" rx="2"/><line x1="28" y1="15" x2="28" y2="8"/><line x1="50" y1="15" x2="50" y2="8"/><line x1="72" y1="15" x2="72" y2="8"/><line x1="28" y1="85" x2="28" y2="92"/><line x1="50" y1="85" x2="50" y2="92"/><line x1="72" y1="85" x2="72" y2="92"/><line x1="15" y1="28" x2="8" y2="28"/><line x1="15" y1="50" x2="8" y2="50"/><line x1="15" y1="72" x2="8" y2="72"/><line x1="85" y1="28" x2="92" y2="28"/><line x1="85" y1="50" x2="92" y2="50"/><line x1="85" y1="72" x2="92" y2="72"/></svg>`,
};

function _categoryToKey(category) {
  const c = (category || "").toLowerCase();
  if (c.includes("gpu") || c.includes("graphic")) return "gpu";
  if (c.includes("cpu") || c.includes("processor")) return "cpu";
  if (c.includes("ram") || c.includes("memory")) return "ram";
  if (c.includes("ssd") || c.includes("nvme") || c.includes("storage")) return "ssd";
  if (c.includes("hdd") || c.includes("hard drive")) return "hdd";
  if (c.includes("monitor") || c.includes("display")) return "monitor";
  if (c.includes("mouse")) return "mouse";
  if (c.includes("keyboard")) return "keyboard";
  if (c.includes("laptop") || c.includes("notebook")) return "laptop";
  if (c.includes("cooler") || c.includes("cooling") || c.includes("aio") || c.includes("fan")) return "cooler";
  if (c.includes("psu") || c.includes("power supply")) return "psu";
  if (c.includes("motherboard") || c.includes("mobo")) return "motherboard";
  if (c.includes("headset") || c.includes("headphone") || c.includes("audio")) return "headset";
  if (c.includes("controller") || c.includes("gamepad")) return "controller";
  if (c.includes("network") || c.includes("wifi") || c.includes("router")) return "network";
  if (c.includes("case") || c.includes("chassis")) return "case";
  return "default";
}

function categoryPlaceholderEl(category) {
  const key = _categoryToKey(category);
  const svg = _CAT_SVG[key] || _CAT_SVG.default;
  const div = document.createElement("div");
  div.className = "curated-thumb-placeholder curated-thumb-placeholder--art";
  div.innerHTML = svg + `<span class="placeholder-cat-label">${category || "No preview available"}</span>`;
  return div;
}
// ─────────────────────────────────────────────────────────────────────────────

/** Skip re-rendering deals/curated on poll when nothing changed (avoids DOM wipe + image flash). */
let _digestCurated = "";
let _digestDeals = "";

function digestCurated(d) {
  if (!d || typeof d !== "object") return "";
  const n = Array.isArray(d.items) ? d.items.length : 0;
  return `${d.updated_at ?? ""}|${d.bookmark_mode ? "1" : "0"}|${n}`;
}

function digestDeals(feed) {
  if (!feed || typeof feed !== "object") return "";
  const items = Array.isArray(feed.items) ? feed.items : [];
  const parts = [`${feed.scan_finished_at ?? ""}|${feed.deal_count ?? ""}|${items.length}`];
  for (const it of items) {
    if (it && typeof it === "object") {
      parts.push(`${it.id}:${it.price}:${it.is_deal ? "1" : "0"}:${it.error || ""}`);
    }
  }
  return parts.join("|");
}

const PC_PARTPICKER_PRICE_SELECTOR = "#prices td.td__finalPrice";

/** Real PCPartPicker product page — verified to return a price with the selector above. */
const DEMO_WATCH = {
  id: "demo-pcpp-sample",
  name: "Demo: PCPartPicker listing (replace URL with your part)",
  url: "https://pcpartpicker.com/product/9dR48d/",
  price_selector: PC_PARTPICKER_PRICE_SELECTOR,
  max_price: 99999,
  min_drop_percent: null,
  currency: "USD",
};

function toast(msg, ok = true) {
  const t = document.createElement("div");
  t.className = `toast ${ok ? "ok" : "err"}`;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 4500);
}

function slug(s) {
  return s
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 48) || "watch";
}

function collectPayload() {
  const rows = [...document.querySelectorAll("#watch-body tr")];
  const watches = rows.map((tr) => ({
    id: tr.querySelector('[data-f="id"]')?.value?.trim() || "",
    name: tr.querySelector('[data-f="name"]')?.value?.trim() || "",
    url: tr.querySelector('[data-f="url"]')?.value?.trim() || "",
    price_selector: tr.querySelector('[data-f="price_selector"]')?.value?.trim() || "",
    max_price: numOrNull(tr.querySelector('[data-f="max_price"]')?.value),
    min_drop_percent: numOrNull(tr.querySelector('[data-f="min_drop_percent"]')?.value),
    baseline_price: numOrNull(tr.querySelector('[data-f="baseline_price"]')?.value),
    min_discount_percent_vs_baseline: numOrNull(
      tr.querySelector('[data-f="min_discount_percent_vs_baseline"]')?.value,
    ),
    currency: tr.querySelector('[data-f="currency"]')?.value?.trim() || "USD",
    alert_cooldown_hours: numOrNull(tr.querySelector('[data-f="alert_cooldown_hours"]')?.value),
  }));

  const extraRaw = $("#extra_apprise_urls")?.value || "";
  const extra_apprise_urls = extraRaw
    .split("\n")
    .map((l) => l.trim())
    .filter(Boolean);

  return {
    scan_interval_minutes: parseInt($("#scan_interval_minutes").value, 10) || 30,
    default_alert_cooldown_hours: parseFloat($("#default_alert_cooldown_hours").value) || 12,
    auto_start_scanner: $("#auto_start_scanner").checked,
    telegram_bot_token: $("#telegram_bot_token").value.trim(),
    telegram_chat_id: $("#telegram_chat_id").value.trim(),
    extra_apprise_urls,
    http: {
      timeout_seconds: parseFloat($("#http_timeout").value) || 25,
      user_agent: $("#http_ua").value.trim() || "pcFinderDealBot/1.0 (personal use)",
      verify_ssl: $("#http_verify_ssl").checked,
    },
    watches,
  };
}

function numOrNull(s) {
  if (s == null || String(s).trim() === "") return null;
  const n = Number(s);
  return Number.isFinite(n) ? n : null;
}

function applyConfig(data) {
  $("#scan_interval_minutes").value = data.scan_interval_minutes;
  $("#default_alert_cooldown_hours").value = data.default_alert_cooldown_hours;
  $("#auto_start_scanner").checked = !!data.auto_start_scanner;
  $("#telegram_bot_token").value = data.telegram_bot_token || "";
  $("#telegram_chat_id").value = data.telegram_chat_id || "";
  $("#extra_apprise_urls").value = (data.extra_apprise_urls || []).join("\n");
  $("#http_timeout").value = data.http?.timeout_seconds ?? 25;
  $("#http_ua").value = data.http?.user_agent ?? "";
  $("#http_verify_ssl").checked = data.http?.verify_ssl !== false;

  const tb = $("#watch-body");
  tb.innerHTML = "";
  (data.watches || []).forEach((w) => tb.appendChild(watchRow(w)));
  if (!data.watches?.length) {
    tb.appendChild(watchRow({}));
  }

  updateScannerUi(data);
  renderDeals(
    data.deal_feed || {
      scan_finished_at: null,
      items: [],
      deal_count: 0,
    },
  );
  renderCurated(
    data.curated_deals || {
      items: [],
      bookmark_mode: false,
      reddit_error: null,
      updated_at: null,
      source: "r/buildapcsales",
    },
  );
  _digestCurated = digestCurated(data.curated_deals);
  _digestDeals = digestDeals(data.deal_feed);
}

function isRowEmpty(tr) {
  const url = tr.querySelector('[data-f="url"]')?.value?.trim();
  const id = tr.querySelector('[data-f="id"]')?.value?.trim();
  const sel = tr.querySelector('[data-f="price_selector"]')?.value?.trim();
  return !url && !id && !sel;
}

function addDemoWatchRow() {
  const tb = $("#watch-body");
  const ids = [...tb.querySelectorAll('[data-f="id"]')].map((el) => el.value.trim());
  if (ids.includes(DEMO_WATCH.id)) {
    toast("Demo watch is already in the table");
    return;
  }
  const rows = [...tb.querySelectorAll("tr")];
  if (rows.length === 1 && isRowEmpty(rows[0])) {
    rows[0].replaceWith(watchRow(DEMO_WATCH));
  } else {
    tb.appendChild(watchRow(DEMO_WATCH));
  }
  toast("Demo row added — click Save all, then Scan once");
}

function watchRow(w) {
  const tr = document.createElement("tr");
  tr.innerHTML = `
    <td><input data-f="id" type="text" placeholder="gpu-7800xt" value="${esc(w.id || "")}" /></td>
    <td><input data-f="name" type="text" placeholder="Display name" value="${esc(w.name || "")}" /></td>
    <td><input data-f="url" class="w-url" type="text" placeholder="https://…" value="${esc(w.url || "")}" /></td>
    <td><input data-f="price_selector" class="w-sel" type="text" placeholder=".price-current" value="${esc(w.price_selector || "")}" /></td>
    <td><input data-f="max_price" type="text" placeholder="449.99" value="${w.max_price ?? ""}" /></td>
    <td><input data-f="min_drop_percent" type="text" placeholder="5" value="${w.min_drop_percent ?? ""}" /></td>
    <td><input data-f="currency" type="text" placeholder="USD" value="${esc(w.currency || "USD")}" /></td>
    <td><button type="button" class="btn btn-danger-ghost rm" title="Remove">✕</button></td>
  `;
  const nameIn = tr.querySelector('[data-f="name"]');
  const idIn = tr.querySelector('[data-f="id"]');
  nameIn?.addEventListener("blur", () => {
    if (!idIn.value.trim() && nameIn.value.trim()) {
      idIn.value = slug(nameIn.value);
    }
  });
  tr.querySelector(".rm")?.addEventListener("click", () => {
    tr.remove();
    if (!document.querySelector("#watch-body tr")) {
      $("#watch-body").appendChild(watchRow({}));
    }
  });
  return tr;
}

function esc(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;");
}

function updateScannerUi(data) {
  const on = data.scanner_running;
  $("#pill-scan").classList.toggle("on", on);
  $("#pill-text").textContent = on ? "Scanner running" : "Scanner stopped";
  $("#btn-start-scan").disabled = on;
  $("#btn-stop-scan").disabled = !on;
  const last = data.last_scan_at
    ? new Date(data.last_scan_at).toLocaleString()
    : "—";
  $("#last-scan").textContent = last;
  $("#last-err").textContent = data.last_scan_error || "";
}

function apiUrl(path) {
  const p = path.startsWith("/") ? path : `/${path}`;
  try {
    return new URL(p, window.location.origin).href;
  } catch {
    return path;
  }
}

async function api(path, opts = {}) {
  const url = apiUrl(path);
  let r;
  try {
    r = await fetch(url, {
      headers: { "Content-Type": "application/json", ...opts.headers },
      ...opts,
    });
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    throw new Error(
      `Network error (${msg}). Open the app from the pcFinder server URL (e.g. http://127.0.0.1:8765) — not a saved HTML file.`,
    );
  }
  let body = null;
  try {
    body = await r.json();
  } catch {
    body = null;
  }
  if (!r.ok) {
    const msg = body?.detail || r.statusText || "Request failed";
    throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
  }
  if (body === null || typeof body !== "object") {
    throw new Error(
      `Bad response from ${url} (expected JSON). Confirm \`python -m pcfinder --web\` is running.`,
    );
  }
  return body;
}

/** Same-origin proxy: Reddit/Slickdeals CDNs often return 403 to <img> from the browser. */
function proxiedThumbUrl(url) {
  if (!url || typeof url !== "string") return "";
  const t = url.trim();
  if (!t.startsWith("http")) return t;
  return `/api/proxy-img?u=${encodeURIComponent(t)}`;
}

let _curatedLightboxTeardown = null;

function teardownCuratedLightbox() {
  if (typeof _curatedLightboxTeardown === "function") {
    _curatedLightboxTeardown();
    _curatedLightboxTeardown = null;
  }
}

/** Full-size HD preview (same proxied URL; Reddit uses up to ~1920px width when available). */
function openCuratedImagePreview(imageUrl, title) {
  teardownCuratedLightbox();
  const backdrop = document.createElement("div");
  backdrop.className = "curated-img-lightbox";
  backdrop.setAttribute("role", "dialog");
  backdrop.setAttribute("aria-modal", "true");
  backdrop.setAttribute("aria-label", "Product image preview");

  const close = () => {
    document.removeEventListener("keydown", onKey);
    backdrop.remove();
    _curatedLightboxTeardown = null;
  };
  _curatedLightboxTeardown = close;

  const onKey = (e) => {
    if (e.key === "Escape") close();
  };
  document.addEventListener("keydown", onKey);

  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "curated-img-lightbox__close";
  btn.textContent = "Close";
  btn.addEventListener("click", close);

  const panel = document.createElement("div");
  panel.className = "curated-img-lightbox__panel";

  const img = document.createElement("img");
  img.className = "curated-img-lightbox__img";
  img.src = proxiedThumbUrl(imageUrl);
  img.alt = title ? String(title).slice(0, 240) : "Product preview";
  img.decoding = "async";

  const cap = document.createElement("p");
  cap.className = "curated-img-lightbox__cap";
  cap.textContent = title || "";

  panel.append(img, cap);
  backdrop.append(btn, panel);
  backdrop.addEventListener("click", (e) => {
    if (e.target === backdrop) close();
  });
  document.body.appendChild(backdrop);
  btn.focus();
}

function curatedCard(it, index = 0) {
  const el = document.createElement("article");
  const expired = it.is_expired && !it.is_bookmark;
  el.className = "curated-card"
    + (it.is_bookmark ? " curated-card--bookmark" : "")
    + (expired ? " curated-card--expired" : "");

  const thumbUrl = it.thumbnail && String(it.thumbnail).trim();
  if (thumbUrl) {
    const wrap = document.createElement("button");
    wrap.type = "button";
    wrap.className = "curated-media";
    wrap.setAttribute("aria-label", "View larger product image");
    wrap.addEventListener("click", () => openCuratedImagePreview(thumbUrl, it.title || ""));
    wrap.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        openCuratedImagePreview(thumbUrl, it.title || "");
      }
    });
    const img = document.createElement("img");
    img.className = "curated-thumb";
    img.src = proxiedThumbUrl(thumbUrl);
    img.alt = "";
    img.loading = index < 5 ? "eager" : "lazy";
    img.decoding = "async";
    if (index < 4) img.fetchPriority = "high";
    img.addEventListener("error", () => {
      wrap.replaceWith(categoryPlaceholderEl(it.category));
    });

    // Overlay badges on the image
    const overlays = document.createElement("div");
    overlays.className = "curated-img-overlays";
    if (!it.is_bookmark && !expired && it.score >= 200) {
      const hot = document.createElement("span");
      hot.className = "badge badge--hot";
      hot.textContent = "🔥 Hot";
      overlays.appendChild(hot);
    }
    if (expired) {
      const expBadge = document.createElement("span");
      expBadge.className = "badge badge--expired";
      expBadge.textContent = "Expired";
      overlays.appendChild(expBadge);
    }
    if (it.category && !it.is_bookmark) {
      const cat = document.createElement("span");
      cat.className = `badge badge--cat badge--cat-${it.category.toLowerCase().replace(/\s+/g, "-")}`;
      cat.textContent = it.category;
      overlays.appendChild(cat);
    }
    if (overlays.children.length) wrap.appendChild(overlays);

    wrap.appendChild(img);
    el.appendChild(wrap);
  } else {
    el.appendChild(categoryPlaceholderEl(it.category));
  }

  const inner = document.createElement("div");
  inner.className = "curated-card-inner";

  const title = document.createElement("h3");
  title.className = "curated-title";
  title.textContent = it.title || "—";

  const row = document.createElement("div");
  row.className = "curated-meta-row";

  // Score
  const score = document.createElement("span");
  score.className = "curated-score";
  if (it.is_bookmark) {
    score.textContent = "Quick link";
  } else if (it.source === "slickdeals") {
    score.textContent = it.score ? `▲ ${it.score}` : "Deal";
  } else {
    score.textContent = `▲ ${it.score ?? 0}`;
  }
  row.appendChild(score);

  // Price badge
  if (it.price && !it.is_bookmark) {
    const priceBadge = document.createElement("span");
    priceBadge.className = "curated-price";
    priceBadge.textContent = `$${it.price.toLocaleString("en-US", { minimumFractionDigits: it.price % 1 === 0 ? 0 : 2, maximumFractionDigits: 2 })}`;
    row.appendChild(priceBadge);
  }

  // Discount % badge
  if (it.discount_pct && !it.is_bookmark) {
    const disc = document.createElement("span");
    disc.className = "badge-discount";
    disc.textContent = `−${it.discount_pct}%`;
    row.appendChild(disc);
  }

  // Deal age + NEW badge
  if (it.created_utc && !it.is_bookmark) {
    const age = dealAge(it.created_utc);
    if (age) {
      const ageBadge = document.createElement("span");
      const ageHours = (Date.now() / 1000 - it.created_utc) / 3600;
      if (ageHours < 4) {
        ageBadge.className = "badge-age badge-age--new";
        ageBadge.textContent = "NEW · " + age;
      } else {
        ageBadge.className = "badge-age";
        ageBadge.textContent = age;
      }
      row.appendChild(ageBadge);
    }
  }

  // Source flair (only show if no category badge on image, or for bookmarks)
  if (it.flair && (it.is_bookmark || !it.category)) {
    const f = document.createElement("span");
    f.className = "curated-flair";
    f.textContent = it.flair;
    row.appendChild(f);
  } else if (it.source === "slickdeals" && !it.category) {
    const f = document.createElement("span");
    f.className = "curated-flair";
    f.textContent = "Slickdeals";
    row.appendChild(f);
  }

  const actions = document.createElement("div");
  actions.className = "curated-actions";
  const dealHref = it.deal_url || it.reddit_url || "#";
  const aDeal = document.createElement("a");
  aDeal.href = dealHref;
  aDeal.target = "_blank";
  aDeal.rel = "noopener noreferrer";
  aDeal.className = "btn btn-primary btn-compact";
  aDeal.textContent = it.is_bookmark ? "Open page" : it.is_self_post ? "Open thread" : "Open deal";
  actions.append(aDeal);
  if (it.source !== "slickdeals") {
    const aThread = document.createElement("a");
    aThread.href = it.reddit_url || dealHref;
    aThread.target = "_blank";
    aThread.rel = "noopener noreferrer";
    aThread.className = "btn btn-ghost btn-compact";
    aThread.textContent = "Thread";
    actions.append(aThread);
  }
  if (it.camel_url) {
    const aCamel = document.createElement("a");
    aCamel.href = it.camel_url;
    aCamel.target = "_blank";
    aCamel.rel = "noopener noreferrer";
    aCamel.className = "btn btn-ghost btn-compact btn-camel";
    aCamel.title = "Price history on CamelCamelCamel";
    aCamel.textContent = "📈 History";
    actions.append(aCamel);
  }
  inner.append(title, row, actions);
  el.appendChild(inner);
  return el;
}

// ── Deal age helper ───────────────────────────────────────────────────────────
function dealAge(created_utc) {
  if (!created_utc) return null;
  const diffSec = Math.floor(Date.now() / 1000) - created_utc;
  if (diffSec < 0) return null;
  const h = Math.floor(diffSec / 3600);
  if (h < 1) return `${Math.max(1, Math.floor(diffSec / 60))}m ago`;
  if (h < 24) return `${h}h ago`;
  const d = Math.floor(h / 24);
  return `${d}d ago`;
}

// ── State for filter/sort ─────────────────────────────────────────────────────
let _curatedFilter = "All";
let _curatedSort   = "top";   // top | new | price
let _curatedData   = null;

function applyFilterSort(items) {
  let out = [...items];
  if (_curatedFilter !== "All") {
    out = out.filter(it => it.category === _curatedFilter);
  }
  if (_curatedSort === "new") {
    out.sort((a, b) => (b.created_utc || 0) - (a.created_utc || 0));
  } else if (_curatedSort === "price") {
    const priced = out.filter(it => it.price != null);
    const rest   = out.filter(it => it.price == null);
    priced.sort((a, b) => a.price - b.price);
    out = [...priced, ...rest];
  }
  // Always push expired to back
  out.sort((a, b) => (a.is_expired ? 1 : 0) - (b.is_expired ? 1 : 0));
  return out;
}

function renderCurated(d) {
  const meta = $("#curated-meta");
  const grid = $("#curated-grid");
  if (!meta || !grid) return;
  if (!d || typeof d !== "object") {
    meta.textContent = "No deal data.";
    grid.innerHTML = "";
    return;
  }
  _curatedData = d;
  const allItems = Array.isArray(d.items) ? d.items : [];
  const when = d.updated_at ? new Date(d.updated_at).toLocaleString() : "";
  if (d.bookmark_mode) {
    const re = d.reddit_error ? String(d.reddit_error) : "";
    meta.textContent =
      (re ? `Could not load live deal feeds (${re.slice(0, 140)}). ` : "") +
      "Showing quick links — open each in your browser for current deals.";
  } else {
    const active = allItems.filter(it => !it.is_expired).length;
    const parts = [`${active} active deals (${allItems.length} total)`];
    if (when) parts.push(`Updated ${when}`);
    meta.textContent = parts.join(" · ");
  }

  // Build/update filter + sort controls
  let controls = $("#curated-controls");
  if (!controls) {
    controls = document.createElement("div");
    controls.id = "curated-controls";
    controls.className = "curated-controls";
    grid.parentElement.insertBefore(controls, grid);
  }
  controls.innerHTML = "";

  // Category filter pills
  const cats = ["All", ...new Set(allItems.map(it => it.category).filter(Boolean))].sort(
    (a, b) => a === "All" ? -1 : b === "All" ? 1 : a.localeCompare(b)
  );
  const filterGroup = document.createElement("div");
  filterGroup.className = "filter-pills";
  cats.forEach(cat => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "filter-pill" + (cat === _curatedFilter ? " filter-pill--active" : "");
    const count = cat === "All" ? allItems.length : allItems.filter(it => it.category === cat).length;
    btn.textContent = `${cat} (${count})`;
    btn.addEventListener("click", () => {
      _curatedFilter = cat;
      _reRenderGrid();
    });
    filterGroup.appendChild(btn);
  });
  controls.appendChild(filterGroup);

  // Sort tabs
  const sortGroup = document.createElement("div");
  sortGroup.className = "sort-tabs";
  [["top", "▲ Top"], ["new", "🕐 New"], ["price", "$ Price"]].forEach(([val, label]) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "sort-tab" + (val === _curatedSort ? " sort-tab--active" : "");
    btn.textContent = label;
    btn.addEventListener("click", () => {
      _curatedSort = val;
      _reRenderGrid();
    });
    sortGroup.appendChild(btn);
  });
  controls.appendChild(sortGroup);

  _reRenderGrid();
}

function _reRenderGrid() {
  const grid = $("#curated-grid");
  if (!grid || !_curatedData) return;
  const allItems = Array.isArray(_curatedData.items) ? _curatedData.items : [];
  const items = applyFilterSort(allItems);

  // Rebuild filter pill active states
  document.querySelectorAll(".filter-pill").forEach(btn => {
    const cat = btn.textContent.replace(/\s*\(\d+\)$/, "");
    btn.className = "filter-pill" + (cat === _curatedFilter ? " filter-pill--active" : "");
  });
  document.querySelectorAll(".sort-tab").forEach(btn => {
    const val = btn.textContent.includes("Top") ? "top" : btn.textContent.includes("New") ? "new" : "price";
    btn.className = "sort-tab" + (val === _curatedSort ? " sort-tab--active" : "");
  });

  grid.innerHTML = "";
  if (!items.length) {
    const empty = document.createElement("p");
    empty.className = "curated-empty";
    empty.textContent = `No ${_curatedFilter !== "All" ? _curatedFilter + " " : ""}deals found.`;
    grid.appendChild(empty);
    return;
  }
  items.forEach((it, index) => {
    if (it && typeof it === "object") grid.appendChild(curatedCard(it, index));
  });
}

async function loadConfig() {
  const data = await api("/api/config");
  applyConfig(data);
}

function dealCardEl(it) {
  if (!it || !it.url) {
    const d = document.createElement("div");
    d.className = "hint";
    d.textContent = "Invalid deal row (missing link).";
    return d;
  }
  const el = document.createElement("a");
  el.href = it.url;
  el.target = "_blank";
  el.rel = "noopener noreferrer";
  el.className = "deal-card";
  const title = document.createElement("div");
  title.className = "deal-card-title";
  title.textContent = it.name || it.id || "Product";
  const price = document.createElement("div");
  price.className = "deal-card-price";
  const pv = it.price;
  const num = pv == null || pv === "" ? NaN : Number(pv);
  price.textContent = Number.isFinite(num)
    ? `${it.currency || "USD"} ${num.toFixed(2)}`
    : `${it.currency || "USD"} —`;
  const reasons = document.createElement("ul");
  reasons.className = "deal-card-reasons";
  (it.deal_reasons || []).forEach((r) => {
    const li = document.createElement("li");
    li.textContent = r;
    reasons.appendChild(li);
  });
  const open = document.createElement("span");
  open.className = "deal-card-cta";
  open.textContent = "Open listing →";
  el.append(title, price, reasons, open);
  return el;
}

function renderDeals(d) {
  const meta = $("#deals-meta");
  if (!d || typeof d !== "object") {
    meta.textContent = "No deal data received from server.";
    return;
  }
  const when = d.scan_finished_at ? new Date(d.scan_finished_at).toLocaleString() : null;
  const items = Array.isArray(d.items) ? d.items.filter((x) => x && typeof x === "object") : [];
  if (!items.length) {
    meta.textContent = when
      ? `Last scan ${when} — no watches configured or no rows returned.`
      : "No scan yet. Save your watches, then click Scan once.";
  } else {
    meta.textContent = `${when ? `Updated ${when}` : "Updated"}${
      d.deal_count ? ` · ${d.deal_count} deal(s) match your rules` : " · no deals match your rules right now"
    }`;
  }

  const hl = $("#deals-highlight");
  hl.innerHTML = "";
  const deals = items.filter((x) => x.is_deal && x.url);
  if (!items.length) {
    hl.innerHTML = '<p class="hint">Add watches, save, then run a scan to see prices here.</p>';
  } else if (deals.length) {
    const h = document.createElement("h3");
    h.className = "deals-subtitle";
    h.textContent = `Deals matching your rules (${deals.length})`;
    hl.appendChild(h);
    deals.forEach((it) => hl.appendChild(dealCardEl(it)));
  } else {
    hl.innerHTML =
      '<p class="hint">Nothing matches max price / baseline / drop rules yet. Full prices are in the table below — tweak your targets or wait for a price move.</p>';
  }

  const th = $("#deals-table-heading");
  th.hidden = items.length === 0;
  const tb = $("#deals-all-body");
  tb.innerHTML = "";
  for (const it of items) {
    const tr = document.createElement("tr");
    if (it.error) tr.classList.add("row-err");
    else if (it.is_deal) tr.classList.add("row-deal");

    const tdP = document.createElement("td");
    if (it.url) {
      const a = document.createElement("a");
      a.href = it.url;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      a.textContent = it.name || it.id || "—";
      tdP.appendChild(a);
    } else {
      tdP.textContent = it.name || it.id || "—";
    }

    const tdPrice = document.createElement("td");
    if (it.error) {
      tdPrice.textContent = "—";
    } else {
      const p = it.price;
      const num = p == null || p === "" ? NaN : Number(p);
      tdPrice.textContent = Number.isFinite(num)
        ? `${it.currency || "USD"} ${num.toFixed(2)}`
        : "—";
    }

    const tdSt = document.createElement("td");
    const badge = document.createElement("span");
    badge.className = "badge " + (it.error ? "badge-err" : it.is_deal ? "badge-deal" : "badge-watch");
    badge.textContent = it.error ? "Error" : it.is_deal ? "Deal" : "Watching";
    tdSt.appendChild(badge);

    const tdWhy = document.createElement("td");
    if (it.error) {
      tdWhy.textContent = it.error;
      tdWhy.style.fontSize = "0.8rem";
      tdWhy.style.color = "var(--danger)";
    } else {
      tdWhy.textContent = (it.deal_reasons || []).join(" · ") || "—";
      tdWhy.style.fontSize = "0.8rem";
      tdWhy.style.color = "var(--muted)";
    }

    tr.append(tdP, tdPrice, tdSt, tdWhy);
    tb.appendChild(tr);
  }
}

async function saveConfig() {
  const payload = collectPayload();
  await api("/api/config", { method: "POST", body: JSON.stringify(payload) });
  toast("Settings saved");
  await loadConfig();
}

async function pollStatus() {
  try {
    const data = await api("/api/config");
    updateScannerUi(data);

    const feed = data.deal_feed || {
      scan_finished_at: null,
      items: [],
      deal_count: 0,
    };
    const dDeals = digestDeals(feed);
    if (dDeals !== _digestDeals) {
      _digestDeals = dDeals;
      renderDeals(feed);
    }

    const curated = data.curated_deals || {
      items: [],
      bookmark_mode: false,
      reddit_error: null,
      updated_at: null,
      source: "r/buildapcsales",
    };
    const dCur = digestCurated(curated);
    if (dCur !== _digestCurated) {
      _digestCurated = dCur;
      renderCurated(curated);
    }
  } catch {
    /* ignore */
  }
}

function init() {
  $("#btn-refresh-curated")?.addEventListener("click", () => {
    const btn = $("#btn-refresh-curated");
    const grid = $("#curated-grid");

    // Show loading state immediately
    btn.disabled = true;
    btn.textContent = "Refreshing…";

    // Overlay grid with skeleton loader
    if (grid) {
      grid.innerHTML = "";
      const loader = document.createElement("div");
      loader.id = "curated-refresh-loader";
      loader.style.cssText =
        "grid-column:1/-1;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:3rem 1rem;gap:1rem;color:var(--text-muted,#888)";
      loader.innerHTML =
        '<div style="font-size:2rem;animation:spin 1s linear infinite">⟳</div>' +
        "<p style=\"margin:0;font-size:0.95rem\">Fetching fresh deals… this takes ~15 s</p>";
      grid.appendChild(loader);

      // Add spin keyframe if not already present
      if (!document.getElementById("spin-style")) {
        const style = document.createElement("style");
        style.id = "spin-style";
        style.textContent = "@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}";
        document.head.appendChild(style);
      }
    }

    api("/api/config?refresh_curated=1")
      .then((d) => {
        const cd = d.curated_deals || {
          items: [],
          bookmark_mode: false,
          reddit_error: null,
          updated_at: null,
          source: "r/buildapcsales",
        };
        _digestCurated = digestCurated(cd);
        renderCurated(cd);
        updateScannerUi(d);
        const feed = d.deal_feed || {
          scan_finished_at: null,
          items: [],
          deal_count: 0,
        };
        _digestDeals = digestDeals(feed);
        renderDeals(feed);
        toast("Deals refreshed ✓");
      })
      .catch((e) => {
        toast(e.message, false);
        // Restore grid on error
        if (grid && grid.innerHTML.includes("curated-refresh-loader")) {
          grid.innerHTML = "";
          _reRenderGrid();
        }
      })
      .finally(() => {
        btn.disabled = false;
        btn.textContent = "Refresh";
      });
  });
  $("#btn-save")?.addEventListener("click", () => saveConfig().catch((e) => toast(e.message, false)));
  $("#btn-reload")?.addEventListener("click", () => loadConfig().catch((e) => toast(e.message, false)));
  $("#btn-add-watch")?.addEventListener("click", () => {
    $("#watch-body").appendChild(watchRow({}));
  });
  $("#btn-add-demo-watches")?.addEventListener("click", () => addDemoWatchRow());
  $("#btn-copy-pcpp-sel")?.addEventListener("click", async () => {
    const t = $("#pcpp-sel")?.textContent?.trim() || PC_PARTPICKER_PRICE_SELECTOR;
    try {
      await navigator.clipboard.writeText(t);
      toast("Selector copied");
    } catch {
      toast("Could not copy — select the text manually", false);
    }
  });
  $("#btn-scan-once")?.addEventListener(
    "click",
    () =>
      api("/api/scan-once", { method: "POST" })
        .then(() => {
          toast("Scan finished");
          return loadConfig();
        })
        .catch((e) => toast(e.message, false)),
  );
  $("#btn-test-tg")?.addEventListener("click", () => {
    const payload = collectPayload();
    api("/api/test-telegram", { method: "POST", body: JSON.stringify(payload) })
      .then(() => toast("Test message sent — check Telegram"))
      .catch((e) => toast(e.message, false));
  });
  $("#btn-start-scan")?.addEventListener("click", () =>
    api("/api/scanner/start", { method: "POST" })
      .then(() => {
        toast("Background scanner started");
        return loadConfig();
      })
      .catch((e) => toast(e.message, false)),
  );
  $("#btn-stop-scan")?.addEventListener("click", () =>
    api("/api/scanner/stop", { method: "POST" })
      .then(() => {
        toast("Background scanner stopped");
        return loadConfig();
      })
      .catch((e) => toast(e.message, false)),
  );

  loadConfig().catch((e) => toast(e.message, false));
  setInterval(pollStatus, 8000);
}

init();
