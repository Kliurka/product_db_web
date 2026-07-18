# Stone Factory ERP - Permissions

## Roles

- Admin
- Manager
- Worker
- Viewer

---

# Dashboard

| Action | Admin | Manager | Worker | Viewer |
|--------|:-----:|:-------:|:------:|:------:|
| View Dashboard | ✅ | ✅ | ✅ | ✅ |

---

# Products

| Action | Admin | Manager | Worker | Viewer |
|--------|:-----:|:-------:|:------:|:------:|
| List | ✅ | ✅ | ✅ | ✅ |
| Detail | ✅ | ✅ | ✅ | ✅ |
| Add | ✅ | ✅ | ✅ | ❌ |
| Edit | ✅ | ✅ | ✅ | ❌ |
| Delete | ✅ | ✅ | ✅ | ❌ |
| Photos | ✅ | ✅ | ✅ | 👁 View only |
| QR | ✅ | ✅ | ✅ | ✅ |

---

# Orders

| Action | Admin | Manager | Worker | Viewer |
|--------|:-----:|:-------:|:------:|:------:|
| List | ✅ | ✅ | ✅ | ❌ |
| Detail | ✅ | ✅ | ✅ | ❌ |
| Add | ✅ | ✅ | ❌ | ❌ |
| Edit | ✅ | ✅ | ❌ | ❌ |
| Delete | ✅ | ✅ | ❌ | ❌ |

---

# Customers

| Action | Admin | Manager | Worker | Viewer |
|--------|:-----:|:-------:|:------:|:------:|
| List | ✅ | ✅ | ❌ | ❌ |
| Detail | ✅ | ✅ | ❌ | ❌ |
| Add | ✅ | ✅ | ❌ | ❌ |
| Edit | ✅ | ✅ | ❌ | ❌ |
| Delete | ✅ | ✅ | ❌ | ❌ |

---

# Textures

| Action | Admin | Manager | Worker | Viewer |
|--------|:-----:|:-------:|:------:|:------:|
| List | ✅ | ✅ | ✅ | ✅ |
| Detail | ✅ | ✅ | ✅ | ✅ |
| Add | ✅ | ✅ | ✅ | ❌ |
| Edit | ✅ | ✅ | ✅ | ❌ |
| Delete | ✅ | ✅ | ✅ | ❌ |

---

# Storage

| Action | Admin | Manager | Worker | Viewer |
|--------|:-----:|:-------:|:------:|:------:|
| List | ✅ | ✅ | ✅ | ✅ |
| Detail | ✅ | ✅ | ✅ | ✅ |
| Add | ✅ | ✅ | ✅ | ❌ |
| Edit | ✅ | ✅ | ✅ | ❌ |
| Delete | ✅ | ✅ | ✅ | ❌ |

---

# Reports

| Action | Admin | Manager | Worker | Viewer |
|--------|:-----:|:-------:|:------:|:------:|
| View | ✅ | ✅ | ❌ | ❌ |
| Export PDF | ✅ | ✅ | ❌ | ❌ |

---

# Users

| Action | Admin | Manager | Worker | Viewer |
|--------|:-----:|:-------:|:------:|:------:|
| List | ✅ | ❌ | ❌ | ❌ |
| Detail | ✅ | ❌ | ❌ | ❌ |
| Add | ✅ | ❌ | ❌ | ❌ |
| Edit | ✅ | ❌ | ❌ | ❌ |
| Delete | ✅ | ❌ | ❌ | ❌ |

---

# Future modules

- Invoices
- Delivery Notes
- Suppliers
- Payments
- Reservations
- Machine Jobs
- Production Planning

Permissions will follow the same architecture:
List → Detail → Add/Edit
