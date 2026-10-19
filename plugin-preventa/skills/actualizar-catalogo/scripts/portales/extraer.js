// Extraccion de productos de los portales de proveedor, con la sesion de GV.
// Se pega en el navegador (pestana del portal, con la sesion ya abierta por la
// persona) y se lanza la funcion del portal: gvTectel(), gvSekunet(),
// gvIntcomex() o gvSyscom(). Corre en segundo plano; el avance queda en
// window.__job. Al terminar aparece un boton rojo "GV: bajar datos": un clic
// real en ese boton baja <portal>_productos.json (el navegador no deja bajar
// archivos sin un clic de una persona o del agente).
// Solo LEE lo que el portal ya le muestra a la cuenta de GV. Nunca inicia
// sesion, nunca compra, nunca llena formularios.

window.__gvBoton = function (nombre) {
  const b = document.createElement('button');
  b.id = 'gv-bajar'; b.textContent = 'GV: bajar datos';
  b.style.cssText = 'position:fixed;top:140px;left:20px;z-index:2147483647;padding:16px 24px;font-size:18px;background:#c00;color:#fff;border:0;border-radius:8px';
  b.onclick = () => {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([window.__datos], { type: 'application/json' }));
    a.download = nombre; document.body.appendChild(a); a.click(); a.remove();
  };
  document.body.appendChild(b);
};
window.__gvFin = function (proveedor, fuente, productos, extra) {
  window.__datos = JSON.stringify(Object.assign({ proveedor, fecha: new Date().toISOString().slice(0, 10), fuente, productos }, extra || {}));
  window.__gvBoton(proveedor.toLowerCase() + '_productos.json');
  window.__job.estado = 'listo'; window.__job.n = productos.length;
};
const __dormir = ms => new Promise(r => setTimeout(r, ms));
const __txt = s => { const d = document.createElement('div'); d.innerHTML = s || ''; return d.textContent.trim().replace(/\s+/g, ' '); };

// Tectel (WooCommerce). Con sesion, la Store API devuelve en "price" el precio
// de GV y en "regular_price" el de lista; sin sesion el sitio oculta precios.
window.gvTectel = function () {
  window.__job = { estado: 'corriendo', n: 0 };
  (async () => { try {
    const out = []; let pg = 1, tot = 1;
    while (pg <= tot) {
      const r = await fetch('/wp-json/wc/store/v1/products?per_page=100&page=' + pg, { credentials: 'include' });
      tot = +r.headers.get('X-WP-TotalPages') || tot;
      for (const p of await r.json()) {
        const m = +(p.prices.currency_minor_unit || 0), f = v => (v === '' || v == null) ? null : (+v) / Math.pow(10, m);
        out.push({ sku: (p.sku || '').trim(), nombre: __txt(p.name), precio_gv: f(p.prices.price), precio_lista: f(p.prices.regular_price),
          moneda: p.prices.currency_code, en_stock: p.is_in_stock, stock: (p.stock_availability || {}).text || null,
          categorias: (p.categories || []).map(c => __txt(c.name)), descripcion: __txt(p.short_description).slice(0, 400), url: p.permalink });
      }
      window.__job.n = out.length; pg++; await __dormir(400);
    }
    window.__gvFin('Tectel', 'tectelcr.com con sesion de GV (WooCommerce Store API)', out);
  } catch (e) { window.__job.estado = 'error'; window.__job.err = String(e); } })();
  return 'lanzado';
};

// Sekunet (Odoo). Con sesion, cada tarjeta de /shop trae "$ 880.00 + IVA".
// Se recorren todas las paginas y despues las categorias (no las de marca)
// para saber la categoria de cada producto.
window.gvSekunet = function () {
  window.__job = { estado: 'corriendo', n: 0, fase: 'paginas' };
  (async () => { try {
    const T = e => e ? e.textContent.trim().replace(/\s+/g, ' ') : null;
    const traer = async u => new DOMParser().parseFromString(await (await fetch(u, { credentials: 'include' })).text(), 'text/html');
    const tarjetas = d => [...d.querySelectorAll('div.oe_product')].map(c => {
      const v = T(c.querySelector('.oe_currency_value'));
      return { tid: (c.querySelector('input[name=product_template_id]') || {}).value, nombre: T(c.querySelector('.o_wsale_products_item_title')),
        marca: T(c.querySelector('.sk-brand')), sku: (T(c.querySelector('.sk-model')) || '').replace(/^.*Sku:\s*/i, '').trim(),
        precio_gv: v ? +v.replace(/,/g, '') : null, precio_texto: T(c.querySelector('.product_price')),
        existencias: [...c.querySelectorAll('.sk-whs-i')].map(T).join(' | ') };
    });
    const ultima = d => Math.max(1, ...[...d.querySelectorAll('a[href*="/page/"]')].map(a => +(a.getAttribute('href').match(/page\/(\d+)/) || [0, 0])[1]));
    const d1 = await traer('/shop'); const prods = new Map();
    for (const p of tarjetas(d1)) prods.set(p.tid, p);
    for (let i = 2; i <= ultima(d1); i++) { for (const p of tarjetas(await traer('/shop/page/' + i))) prods.set(p.tid, p); window.__job.n = prods.size; await __dormir(250); }
    window.__job.fase = 'categorias';
    const cats = [...new Map([...d1.querySelectorAll('a[href*="/shop/category/"]')].map(a => [a.getAttribute('href').replace(/\?.*/, ''), T(a)])).entries()].filter(([h]) => !/marcas/i.test(h));
    const catDe = {}; let k = 0;
    for (const [h, nom] of cats) {
      let d = await traer(h); const u2 = ultima(d);
      for (let i = 1; i <= u2; i++) { if (i > 1) { d = await traer(h + '/page/' + i); await __dormir(200); } for (const p of tarjetas(d)) (catDe[p.tid] = catDe[p.tid] || []).push(nom.slice(0, 60)); }
      window.__job.cats = (++k) + '/' + cats.length; await __dormir(200);
    }
    const out = [...prods.values()].map(p => Object.assign({}, p, { categorias: catDe[p.tid] || [], moneda: 'USD' }));
    window.__gvFin('Sekunet', 'sekunet.com/shop con sesion de GV (Odoo)', out);
  } catch (e) { window.__job.estado = 'error'; window.__job.err = String(e); } })();
  return 'lanzado';
};

// Intcomex (portal myservices). La pagina consulta ecomm-front .../get-products;
// sin sesion el precio viene vacio. Se bajan las categorias de Seguridad,
// Redes > Redes y Computo > Almacenamiento / Proteccion de Poder / Monitores.
window.gvIntcomex = function () {
  window.__job = { estado: 'corriendo', n: 0 };
  (async () => { try {
    const E = 'https://ecomm-front.intcomex.com/api/ecommerce/';
    const recursos = performance.getEntriesByType('resource').map(e => e.name);
    const conUser = recursos.find(n => /[?&]userId=/.test(n));
    if (!conUser) throw new Error('no encuentro el userId de la sesion: recargar la pagina de la tienda');
    const uid = new URL(conUser).searchParams.get('userId'), sub = new URL(conUser).searchParams.get('companyId') || 'XCR';
    const post = async (u, b) => { const r = await fetch(E + u, { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(b) }); if (!r.ok) throw new Error(u + ' ' + r.status); return r.json(); };
    const m = await post('get-menu', { subsidiary: sub, language: 'Es', authenticated: true });
    const hojas = (c, ruta) => (c.children && c.children.length) ? c.children.flatMap(x => hojas(x, ruta + ' > ' + x.labelEs)) : [{ code: c.categoryCode, ruta }];
    const sel = [];
    for (const top of m.menu) for (const c of (top.categories || [])) {
      const ok = top.labelEs === 'Seguridad' || (top.labelEs === 'Redes' && c.labelEs === 'Redes') || (top.labelEs === 'Computo' && ['Almacenamiento', 'Protección de Poder', 'Monitores'].includes(c.labelEs));
      if (ok) sel.push(...hojas(c, top.labelEs + ' > ' + c.labelEs));
    }
    const vistos = new Set(); const hs = sel.filter(h => h.code && !vistos.has(h.code) && vistos.add(h.code));
    const prods = new Map(); let k = 0;
    for (const h of hs) {
      let pg = 1, tot = 1;
      while ((pg - 1) * 100 < tot) {
        const j = await post('get-products', { subsidiary: sub, category: h.code, sortDirection: 'asc', page: pg, pageSize: 100, userID: uid, currency: 'us', language: 'Es', authenticated: true, typeSearch: 'category', search: '', sortBy: { code: 'Best_match', type: 'text' }, filterCriteria: { brands: [], attributes: [] }, locId: sub.toLowerCase() + '1' });
        tot = j.total || 0;
        for (const p of (j.products || [])) {
          const pr = p.price || {}; const otros = (pr.afs_other_location || []).reduce((s, x) => s + (+x.afs_loc || 0), 0);
          if (!prods.has(p.localSku)) prods.set(p.localSku, { sku: p.localSku, mpn: p.mpn, nombre: p.nameEs || p.labelEs, marca: (p.brand || {}).labelEs, categoria: h.ruta,
            precio_gv: pr.unitPrice ?? null, descuento_pct: pr.discountPercentage, existencias_coyol: pr.afs, existencias_otras: otros, moneda: 'USD' });
        }
        pg++; await __dormir(300);
      }
      window.__job.hojas = (++k) + '/' + hs.length; window.__job.n = prods.size;
    }
    window.__gvFin('Intcomex', 'myservices.intcomex.com con sesion de GV', [...prods.values()], { categorias: hs });
  } catch (e) { window.__job.estado = 'error'; window.__job.err = String(e); } })();
  return 'lanzado';
};

// Syscom (Next.js + Algolia). La pagina de busqueda trae los productos en un
// arreglo "hits" dentro del payload; con sesion cada uno trae precios de lista,
// especial y el de GV (precio_unitario_usd). El catalogo de Syscom es enorme:
// se baja por busquedas de productos pequenos (R21), 50 por pagina, hasta 6
// paginas por termino.
window.gvSyscom = function (terminos) {
  terminos = terminos || ['bateria 12v', 'bateria respaldo', 'fuente de poder', 'cerradura electromagnetica', 'electroiman', 'boton de salida', 'contacto magnetico', 'sirena', 'boton de panico', 'detector de humo', 'estacion manual', 'estrobo', 'modulo direccionable', 'base detector', 'inyector poe', 'switch poe', 'gabinete', 'rack', 'supresor de picos', 'ups', 'tarjeta de proximidad', 'disco duro videovigilancia', 'memoria microsd', 'cable utp', 'cable para alarma', 'tuberia conduit', 'patch cord', 'conector rj45', 'cierrapuertas'];
  const hits = h => {
    const partes = []; const re = /self\.__next_f\.push\(\[1,("(?:[^"\\]|\\.)*")\]\)/g; let m;
    while ((m = re.exec(h))) { try { partes.push(JSON.parse(m[1])); } catch (e) { } }
    const t = partes.join(''); const k = t.indexOf('"hits":['); if (k < 0) return [];
    let i = k + 7, d = 0, inS = false, esc = false;
    for (; i < t.length; i++) { const ch = t[i]; if (inS) { if (esc) esc = false; else if (ch === '\\') esc = true; else if (ch === '"') inS = false; } else { if (ch === '"') inS = true; else if (ch === '[') d++; else if (ch === ']') { d--; if (d === 0) break; } } }
    try { return JSON.parse(t.slice(k + 7, i + 1)); } catch (e) { return []; }
  };
  window.__job = { estado: 'corriendo', n: 0 };
  (async () => { try {
    const prods = new Map();
    for (const q of terminos) {
      window.__job.termino = q;
      for (let pg = 1; pg <= 6; pg++) {
        const arr = hits(await (await fetch('/products?query=' + encodeURIComponent(q) + '&page=' + pg, { credentials: 'include' })).text());
        for (const p of arr) {
          if (!p || !p.precios) continue; const id = p.objectID || p.id_producto, pr = p.precios;
          if (!prods.has(id)) prods.set(id, { id, sku: p.modelo_alias || p.modelo_limpio, nombre: p.titulo, marca: p.marca, precio_lista: pr.precio_lista_usd ?? null,
            precio_especial: pr.precio_especial_usd ?? null, precio_gv: pr.precio_unitario_usd ?? null, moneda: 'USD', tiene_stock: p.tiene_stock,
            bajo_pedido: p.es_bajo_pedido, solo_exportacion: p.erp_solo_exportacion, obsoleto: p.obsoleto, terminos: [q] });
          else if (!prods.get(id).terminos.includes(q)) prods.get(id).terminos.push(q);
        }
        window.__job.n = prods.size; if (arr.length < 50) break; await __dormir(700);
      }
    }
    window.__gvFin('Syscom', 'syscom.mx con sesion de GV (busquedas de productos pequenos, R21)', [...prods.values()], { terminos });
  } catch (e) { window.__job.estado = 'error'; window.__job.err = String(e); } })();
  return 'lanzado';
};
