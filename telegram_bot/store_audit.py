"""Read-only public storefront audit for M5mOsH Nexus. No login, checkout, or transactions."""
import html
import ipaddress
import re
import socket
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen, HTTPRedirectHandler, build_opener


class _AuditParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = False
        self.title_text = []
        self.meta = {}
        self.headings = []
        self.links = []
        self.images = 0
        self.images_without_alt = 0
        self.forms = 0
        self.inputs = 0
        self.viewport = False
        self.lang = ""
        self._h = 0
        self._h_text = []
        self._a = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang", "")
        elif tag == "title":
            self.title = True
        elif tag == "meta":
            key = (a.get("name") or a.get("property") or "").lower()
            if key:
                self.meta[key] = a.get("content", "")
            if key == "viewport":
                self.viewport = True
        elif tag in ("h1", "h2", "h3"):
            self._h = int(tag[1])
            self._h_text = []
        elif tag == "a" and a.get("href"):
            self.links.append((a.get("href", ""), a.get("aria-label", "") or a.get("title", "")))
        elif tag == "img":
            self.images += 1
            if not (a.get("alt") or "").strip():
                self.images_without_alt += 1
        elif tag == "form":
            self.forms += 1
        elif tag in ("input", "select", "textarea"):
            self.inputs += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self.title = False
        if tag in ("h1", "h2", "h3") and self._h:
            text = " ".join("".join(self._h_text).split())
            if text:
                self.headings.append((self._h, text))
            self._h = 0
            self._h_text = []

    def handle_data(self, data):
        if self.title:
            self.title_text.append(data)
        if self._h:
            self._h_text.append(data)


def _public_http_url(url):
    p = urlparse(url)
    if p.scheme not in ("http", "https") or not p.hostname or p.username or p.password:
        raise ValueError("أدخل رابطًا عامًا يبدأ بـ https:// أو http:// دون بيانات دخول.")
    host = p.hostname.lower().rstrip(".")
    if host in ("localhost",) or host.endswith((".localhost", ".local", ".internal")):
        raise ValueError("لا يمكن فحص عناوين محلية أو داخلية.")
    try:
        addresses = {ipaddress.ip_address(host)}
    except ValueError:
        try:
            addresses = {ipaddress.ip_address(x[4][0]) for x in socket.getaddrinfo(host, p.port or (443 if p.scheme == "https" else 80), type=socket.SOCK_STREAM)}
        except Exception:
            raise ValueError("تعذر التحقق من عنوان الموقع.")
    if not addresses or any(not ip.is_global for ip in addresses):
        raise ValueError("العنوان لا يبدو موقعًا عامًا آمنًا للفحص.")
    return url


class _SafeRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = urljoin(req.full_url, newurl)
        _public_http_url(target)
        return super().redirect_request(req, fp, code, msg, headers, target)


def audit_store(url, progress=None):
    """Fetch public HTML only; optional callback reports stages. No checkout or transactions."""
    def stage(percent, label, detail=""):
        if progress:
            progress(percent, label, detail)
    stage(5, "التحقق من الرابط", "التأكد من أن الوجهة عنوان عام مسموح")

    url = (url or "").strip()
    if not url:
        return "أرسل رابط المتجر بعد الأمر: /audit https://example.com"
    if "://" not in url:
        url = "https://" + url
    _public_http_url(url)
    stage(15, "الاتصال بالموقع", "طلب الصفحة العامة دون تسجيل دخول")
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; M5mOsHStoreAudit/1.0)", "Accept": "text/html"})
    opener = build_opener(_SafeRedirect())
    try:
        with opener.open(req, timeout=18) as resp:
            final_url = resp.geturl()
            _public_http_url(final_url)
            status = resp.status
            content_type = resp.headers.get("Content-Type", "")
            raw = resp.read(1_500_000)
    except Exception as exc:
        return "تعذر جلب الصفحة العامة: " + type(exc).__name__ + ". تحقق من الرابط أو جرّب لاحقًا."
    stage(35, "استلام الصفحة", "تم استلام الاستجابة؛ التحقق من نوع المحتوى")
    if "text/html" not in content_type.lower():
        return "الرابط لم يُرجع صفحة HTML قابلة للفحص (Content-Type: " + (content_type or "غير معروف") + ")."
    charset = "utf-8"
    m = re.search("charset=([A-Za-z0-9_-]+)", content_type, re.I)
    if m:
        charset = m.group(1)
    try:
        page = raw.decode(charset, errors="replace")
    except LookupError:
        page = raw.decode("utf-8", errors="replace")
    stage(50, "تحليل HTML", "استخراج العناوين والروابط والصور والبيانات الوصفية")
    parser = _AuditParser()
    parser.feed(page)
    text = html.unescape(re.sub(r"<[^>]+>", " ", page))
    text = " ".join(text.split()).lower()
    title = " ".join("".join(parser.title_text).split())
    desc = parser.meta.get("description", "").strip()
    canonical = bool(re.search("rel=.*canonical", page, re.I))
    robots = bool(re.search("name=.*robots", page, re.I))
    mobile = parser.viewport
    h1 = [x for level, x in parser.headings if level == 1]
    link_text = " ".join((urlparse(h).path + " " + label) for h, label in parser.links).lower()
    policy_terms = {
        "الشحن والتوصيل": ("الشحن", "التوصيل", "shipping", "delivery"),
        "الاستبدال والاسترجاع": ("الاسترجاع", "الاستبدال", "refund", "return", "exchange"),
        "الخصوصية": ("الخصوصية", "privacy"),
        "الشروط والأحكام": ("الشروط", "الأحكام", "terms", "conditions"),
        "التواصل": ("اتصل بنا", "تواصل معنا", "contact", "whatsapp", "واتساب")
    }
    stage(65, "فحص مؤشرات المتجر", "SEO والجوال والسياسات وطرق الدفع الظاهرة")
    findings = []
    def add(level, title, detail):
        findings.append((level, title, detail))
    if final_url.startswith("https://"):
        add("جيد", "الاتصال المشفر", "الصفحة النهائية تستخدم HTTPS؛ لم يُجرَ تدقيق شامل للشهادة أو المحتوى المختلط.")
    else:
        add("عاجل", "HTTPS", "الصفحة النهائية لا تستخدم HTTPS.")
    if title:
        add("جيد", "عنوان الصفحة", title[:140])
    else:
        add("تحسين", "عنوان الصفحة SEO", "لم يُكتشف وسم title واضح في الصفحة.")
    if desc:
        add("جيد", "الوصف التعريفي", desc[:180])
    else:
        add("تحسين", "الوصف التعريفي SEO", "لم يُكتشف meta description في الصفحة الرئيسية.")
    if h1:
        add("جيد", "العنوان الرئيسي", "تم العثور على H1: " + h1[0][:120] + (" (يوجد أكثر من H1)" if len(h1) > 1 else ""))
    else:
        add("تحسين", "العنوان الرئيسي", "لم يُكتشف عنوان H1 في HTML الأولي.")
    if mobile:
        add("جيد", "إعداد عرض الجوال", "يوجد وسم viewport؛ يلزم اختبار فعلي على أجهزة مختلفة.")
    else:
        add("تحسين", "تجربة الجوال", "لم يُكتشف وسم viewport في HTML الأولي.")
    if parser.lang:
        add("جيد", "لغة الصفحة", parser.lang)
    else:
        add("تحسين", "لغة الصفحة", "لم تُحدد لغة عنصر html بوضوح.")
    if parser.images and parser.images_without_alt:
        add("تحسين", "النص البديل للصور", f"{parser.images_without_alt} من {parser.images} صورة ظاهرة بلا alt نصي؛ راجع الصور الزخرفية يدويًا.")
    elif parser.images:
        add("جيد", "النص البديل للصور", f"كل {parser.images} صورة مكتشفة لديها alt غير فارغ؛ جودة النص لم تُراجع.")
    for label, terms in policy_terms.items():
        found = any(term in link_text or term in text for term in terms)
        if found:
            add("مؤشر موجود", label, "ظهر مصطلح مرتبط به في الصفحة أو روابطها؛ يلزم فتح الصفحة للتأكد من وجود سياسة كاملة وواضحة.")
        else:
            add("تحقق يدوي", label, "لم يظهر رابط أو نص واضح له في الصفحة الرئيسية المفحوصة؛ لا يعني ذلك أنه غير موجود في الموقع.")
    payment_terms = ("تابي", "تمارا", "مدى", "apple pay", "stc pay", "visa", "mastercard", "paypal", "mada", "tamara", "tabby", "payment")
    visible_payments = sorted({term for term in payment_terms if term in text})
    if visible_payments:
        add("تحقق", "مؤشرات الدفع", "ظهرت الكلمات: " + ", ".join(visible_payments) + ". ظهور الشعار أو الكلمة لا يثبت أن وسيلة الدفع مفعلة أو تعمل.")
    else:
        add("تحقق يدوي", "طرق الدفع", "لم تظهر كلمات طرق دفع معروفة في HTML الأولي للصفحة الرئيسية. يجب فحص صفحة الدفع أو تأكيد صاحب المتجر؛ لا يمكن الجزم بأنها غير مفعلة.")
    if canonical:
        add("جيد", "Canonical", "يوجد وسم canonical في HTML الأولي.")
    else:
        add("تحسين", "Canonical", "لم يُكتشف canonical في الصفحة الرئيسية.")
    if robots:
        add("موجود", "تعليمات robots", "يوجد meta robots؛ يلزم قراءة قيمته لتحديد أثره.")
    else:
        add("تحقق", "الفهرسة", "لم يُكتشف meta robots؛ هذا وحده لا يثبت وجود مشكلة فهرسة.")
    if parser.forms:
        add("مؤشر موجود", "النماذج", f"تم اكتشاف {parser.forms} نموذجًا و{parser.inputs} حقل إدخال في HTML الأولي؛ لم تُرسل أي بيانات.")
    else:
        add("تحقق يدوي", "النماذج والتواصل", "لم يُكتشف نموذج HTML أولي؛ قد يستخدم الموقع واجهة ديناميكية أو وسائل تواصل خارجية.")
    stage(85, "تجميع النتائج", "فصل الإشارات الظاهرة عن البنود التي تحتاج تحققًا يدويًا")
    parsed = urlparse(final_url)
    origin = parsed.scheme + "://" + parsed.netloc
    report = [
        "🧾 تقرير فحص أولي للمتجر",
        "الرابط: " + final_url,
        "HTTP: " + str(status) + " | HTML عام فقط",
        "العنوان: " + (title or "لم يُكتشف"),
        "",
        "النتائج:"
    ]
    for level, heading, detail in findings:
        report.append("• [" + level + "] " + heading + ": " + detail)
    report += [
        "",
        "حدود الفحص: راجع الصفحة الرئيسية وHTML الذي أعاده الخادم فقط. لم يتم تسجيل الدخول أو إتمام شراء أو اختبار دفع أو قياس سرعة مختبري أو الزحف لكل الصفحات. قد تخفي واجهات JavaScript عناصر مهمة.",
        "",
        "الخطوة التالية: افحص صفحات المنتجات والسلة والشحن والاسترجاع والتواصل، ثم اختبر رحلة الشراء بموافقة صاحب المتجر وبيئة اختبار بوابة الدفع.",
        "",
        "مسودة رسالة للعميل:",
        "مرحبًا، راجعت مؤشرات أولية في متجرك. أقدر أجهز لك مراجعة أوضح تشمل تجربة الجوال، الدفع، صفحات المنتجات والشحن والاسترجاع، مع ترتيب الملاحظات حسب الأولوية. وأوضح لك ما تأكد وما يحتاج اختبارًا قبل اقتراح أي تعديل.",
        "تم إعداد التقرير؛ لم يُختبر الدفع أو تسجيل الدخول"
    ]
    stage(100, "اكتمل الفحص", "تم إعداد التقرير الأولي")
    return "\\n".join(report)[:3300]
