# Salla Merchant API — Initial Scope Matrix

> Evidence snapshot: 2026-11-12. Scopes are copied from the current endpoint pages linked below.
> Policy: read-only first. Do not request write scopes in the first installation.

| Control Center module | Endpoint | HTTP | Minimum documented scope | Initial release |
|---|---|---:|---|---|
| Orders | `/orders` | GET | `orders.read` | Include |
| Order detail | `/orders/{order_id}` | GET | `orders.read` | Include |
| Products | `/products` | GET | `products.read` | Include |
| Product detail | `/products/{product}` | GET | `products.read` | Include |
| Stock quantities | `/products/quantities` | GET | `products.read` | Include |
| Customers | `/customers` | GET | `customers.read` | Restricted read; minimize PII |
| Customer detail | `/customers/{customer}` | GET | `customers.read` | Restricted read; minimize PII |
| Shipments | `/shipments` | GET | `shipping.read` | Include after privacy review |
| Transactions | `/transactions` | GET | `transactions.read` | Include after finance-data review |
| Active webhooks | `/webhooks` | GET | `webhooks.read` | Include for diagnostics |

## First-install scope set

Candidate least-privilege read-only set, subject to checking the actual Partner Portal scope picker before authorization:

- `orders.read`
- `products.read`
- `customers.read`
- `shipping.read`
- `transactions.read`
- `webhooks.read`
- `offline_access` (required for the documented refresh-token lifecycle)

Do not request any `*.read_write` scope in the first installation. The candidate set is not yet configured in Salla Partners and does not mean the merchant has granted it.

## Data minimization

- Orders and shipments may contain names, phone numbers, email addresses, and delivery addresses. Restrict these fields to authorized screens and avoid copying full payloads into logs.
- Customer search must not enable bulk export by default.
- Transactions may expose masked card metadata and customer references. Never collect full payment-card data.
- Keep pagination bounded; do not synchronize the entire store by default.
- Use sequential order pagination, `per_page=30`, date filters, and complete page traversal within Salla's documented 15-minute pagination cache window.
- Products endpoint supports `format=light` for a reduced response; use it where the dashboard does not need full product details.

## Write capabilities — separate future approval

Salla documents write scopes on some resource endpoints, but write permissions are excluded from the initial install. Before adding any write action:
1. Identify the exact endpoint, method, and documented scope.
2. Define a server-side allow-listed operation (no arbitrary API proxy).
3. Add preview, actor authentication, explicit confirmation, idempotency, audit record, and negative tests.
4. Request only the one write scope needed.
5. Keep refunds, order cancellation, bulk pricing/stock, customer deletion, and shipment cancellation as high-risk operations.

Do not infer a refund permission from `transactions.read_write`; verify the exact refund endpoint and current scope requirement before implementation.

## Official endpoint evidence

- Orders list/detail: https://docs.salla.dev/5394146e0 and https://docs.salla.dev/5394147e0
- Products list/detail: https://docs.salla.dev/5394168e0 and https://docs.salla.dev/product/product-details
- Product quantities: https://docs.salla.dev/9612796e0
- Customers list/detail: https://docs.salla.dev/5394121e0 and https://docs.salla.dev/customer/details
- Shipments list: https://docs.salla.dev/5394232e0
- Transactions list: https://docs.salla.dev/transactions/list
- Active webhooks: https://docs.salla.dev/webhooks/active
- OAuth and `offline_access`: https://docs.salla.dev/421118m0

## Rights

© M5mOsH All Rights Reserved
