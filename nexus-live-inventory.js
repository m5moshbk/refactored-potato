(() => {
  'use strict';

  const STATUS_URL = 'https://m5mosh-nexus-inventory-api.onrender.com/api/v1/status';
  const REFRESH_MS = 60_000;

  const style = document.createElement('style');
  style.textContent = `
    #nexusLiveInventory{width:min(1180px,92%);margin:0 auto 24px;padding:18px 20px;border:1px solid #61e4df38;border-radius:16px;background:linear-gradient(120deg,#111b2b,#101323);color:#eef3ff;font-family:system-ui,-apple-system,"Segoe UI",Tahoma,Arial,sans-serif}
    #nexusLiveInventory .nli-head{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}
    #nexusLiveInventory .nli-title{font-weight:800;font-size:15px}
    #nexusLiveInventory .nli-state{font-size:11px;border:1px solid #ffffff28;border-radius:999px;padding:6px 10px;color:#c4d3e7}
    #nexusLiveInventory .nli-state[data-state="ok"]{color:#8ce7c0;border-color:#8ce7c055}
    #nexusLiveInventory .nli-state[data-state="warn"]{color:#f4c875;border-color:#f4c87555}
    #nexusLiveInventory .nli-state[data-state="error"]{color:#ff9b9b;border-color:#ff9b9b55}
    #nexusLiveInventory .nli-details{display:flex;gap:10px 22px;flex-wrap:wrap;margin-top:12px;color:#aebbd0;font-size:12px;line-height:1.8}
    #nexusLiveInventory .nli-details strong{color:#eef3ff}
    #nexusLiveInventory .nli-foot{margin-top:8px;color:#8493aa;font-size:10px}
    @media(max-width:520px){#nexusLiveInventory{padding:15px}#nexusLiveInventory .nli-head{align-items:flex-start;flex-direction:column}}
  `;
  document.head.appendChild(style);

  const panel = document.createElement('section');
  panel.id = 'nexusLiveInventory';
  panel.setAttribute('aria-live', 'polite');
  panel.setAttribute('aria-label', 'حالة مزامنة فهرس Pythonista');
  panel.innerHTML = `
    <div class="nli-head">
      <div class="nli-title">حالة فهرس Nexus — مزامنة Pythonista</div>
      <span class="nli-state" data-state="loading">جارٍ التحقق…</span>
    </div>
    <div class="nli-details"><span>يتم فحص حالة API دون إرسال أي بيانات من المتصفح.</span></div>
    <div class="nli-foot">قراءة فقط · بيانات إجمالية · لا تُعرض مسارات الملفات أو محتوياتها</div>
  `;
  const stats = document.querySelector('.stats');
  if (stats) stats.insertAdjacentElement('afterend', panel);
  else document.body.prepend(panel);

  const stateNode = panel.querySelector('.nli-state');
  const detailsNode = panel.querySelector('.nli-details');

  function setState(state, label) {
    stateNode.dataset.state = state;
    stateNode.textContent = label;
  }

  function addDetail(label, value) {
    const item = document.createElement('span');
    const strong = document.createElement('strong');
    strong.textContent = value;
    item.append(document.createTextNode(label + ': '), strong);
    detailsNode.appendChild(item);
  }

  function formatDate(value) {
    if (!value) return 'غير متاح';
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? 'غير متاح' : date.toLocaleString('ar-SA');
  }

  async function refresh() {
    setState('loading', 'جارٍ التحقق…');
    try {
      const response = await fetch(STATUS_URL, {
        method: 'GET',
        cache: 'no-store',
        headers: { 'Accept': 'application/json' }
      });
      if (!response.ok) throw new Error('status_http_' + response.status);
      const data = await response.json();
      detailsNode.replaceChildren();

      if (data.connected === true) {
        setState('ok', 'API متصل · المزامنة مستلمة');
        addDetail('عدد الملفات المفهرسة', String(data.file_count ?? 'غير متاح'));
        addDetail('أخطاء آخر فحص', String(data.error_count ?? 'غير متاح'));
        addDetail('وقت الفحص المحلي', formatDate(data.checked_at));
        addDetail('وقت الاستلام', formatDate(data.received_at));
      } else if (data.connected === false) {
        setState('warn', 'API متصل · بانتظار أول مزامنة');
        addDetail('الحالة', 'لم تصل مزامنة Pythonista بعد');
      } else {
        setState('warn', 'استجابة غير مكتملة');
        addDetail('الحالة', 'تعذر تفسير حالة المزامنة');
      }
    } catch (_) {
      detailsNode.replaceChildren();
      setState('error', 'تعذر الوصول إلى API');
      addDetail('الحالة', 'الخدمة أو الاتصال غير متاح حالياً');
    }
  }

  refresh();
  window.setInterval(refresh, REFRESH_MS);
})();
