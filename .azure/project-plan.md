# Project Plan

**Status**: In Progress
**Created**: 2026-11-24
**Mode**: NEW

---

## 1. Project Overview

**Goal**: Build a course MMQS web application that imports and tracks MIMIT fuel prices, with an Italian-language Jinja interface for searching stations, filtering prices, viewing station details, and managing price-related data.

**App Type**: API only

**API Login**: No

**Mode**: NEW

**Deployment Plan**: No deployment plan found

---

## 2. Backend - FastAPI

| Component | Technology |
|-----------|-----------|
| **Language** | Python |
| **Runtime** | CPython |
| **Framework** | FastAPI |
| **Package Manager** | pip |
| **Test Runner** | pytest |
| **Mocking Library** | unittest.mock |
| **Test Command** | python -m pytest |
| **Orchestration** | docker-compose |

The backend is a Python 3.11+ application served with Uvicorn. FastAPI serves Italian Jinja templates and JSON-oriented application routes, while SQLAlchemy and SQLite provide persistent storage for stations, prices, users, reports, and favorites.

Core behavior includes:
- Importing MIMIT station and price CSV or JSON records.
- Filtering stations by municipality, province, brand, fuel type, and service mode.
- Presenting station details, communicated prices, weather context, reports, and favorites.
- Providing administrative station, price, report, and import workflows.
- Keeping station and price updates deterministic and independently testable.

---

## 3. Services Required

| Azure Service | Role in App | Environment Variable | Default Value (Local) | Classification |
|---------------|------------|---------------------|----------------------|----------------|
| SQLite | Primary relational data store for stations, prices, users, reports, and favorites | `DATABASE_URL` | `sqlite:///./benzina_chiara.db` | Essential |

---

## 4. Prerequisites

### Run

| Tool | Service(s) | Installed | Version |
|------|------------|-----------|---------|
| Python 3.11+ | mmqs-fuel-tracker | ✅ | CPython 3.13.0 |
| pip | mmqs-fuel-tracker | ✅ | pip 24.2 |
| Uvicorn | mmqs-fuel-tracker | ✅ | 0.54.0 |

### Debug

| Tool | Service(s) | Installed | Version |
|------|------------|-----------|---------|
| `ms-python.python` | mmqs-fuel-tracker | ✅ | 2026.10.0 |
| `ms-python.debugpy` | mmqs-fuel-tracker | ✅ | 2026.6.0 |

All confirmed tool detections used the local Windows environment. Python 3.13.0 satisfies the requested Python 3.11+ minimum and has pip available through the same interpreter.

---

## 5. Project Structure

```text
.
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   ├── main.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── impianti.py
│   │   └── admin.py
│   └── services/
│       ├── mimit.py
│       └── weather.py
├── templates/
├── static/
├── tests/
├── .azure/
│   └── project-plan.md
└── requirements.txt
```

---

## 6. Route Definitions

| # | Method | Path | Description | Request Body | Response Body | Status Codes |
|---|--------|------|-------------|-------------|--------------|-------------|
| 1 | GET | `/` | Render the fuel-station search page | — | Italian Jinja HTML | 200 |
| 2 | GET | `/impianti` | Search stations by municipality, province, brand, fuel, and service mode | — | Italian Jinja HTML | 200 |
| 3 | GET | `/impianti/{impianto_id}` | Show station details, prices, weather, reports, and actions | — | Italian Jinja HTML | 200, 404 |
| 4 | POST | `/impianti/{impianto_id}/preferiti` | Add or remove a station favorite | — | Redirect | 303 |
| 5 | POST | `/impianti/{impianto_id}/segnalazioni` | Submit a station report | `testo_libero` | Redirect or validation error | 303, 422 |
| 6 | POST | `/segnalazioni/{report_id}/modifica` | Edit an existing report | `testo_libero` | Redirect | 303, 403, 404 |
| 7 | POST | `/segnalazioni/{report_id}/elimina` | Delete an existing report | — | Redirect | 303, 404 |
| 8 | GET | `/auth/login` | Render the login page | — | Italian Jinja HTML | 200 |
| 9 | POST | `/auth/login` | Authenticate a user | `email`, `password` | Redirect or login HTML | 303, 400 |
| 10 | GET | `/auth/registrazione` | Render the registration page | — | Italian Jinja HTML | 200 |
| 11 | POST | `/auth/registrazione` | Register a user | `display_name`, `email`, `password` | Redirect or registration HTML | 303, 400, 422 |
| 12 | POST | `/auth/logout` | End the current session | — | Redirect | 303 |
| 13 | GET | `/admin/` | Render the administration dashboard | — | Italian Jinja HTML | 200 |
| 14 | POST | `/admin/impianti` | Create a station | Station fields | Redirect | 303, 409, 422 |
| 15 | POST | `/admin/impianti/{station_id}/modifica` | Update a station | Station fields | Redirect | 303, 404 |
| 16 | POST | `/admin/impianti/{station_id}/elimina` | Delete a station | — | Redirect | 303, 404 |
| 17 | POST | `/admin/impianti/{station_id}/prezzi` | Create a station price | `carburante`, `prezzo`, `is_self` | Redirect | 303, 422 |
| 18 | POST | `/admin/prezzi/{price_id}/modifica` | Update a price | `carburante`, `prezzo`, `is_self` | Redirect | 303, 404 |
| 19 | POST | `/admin/prezzi/{price_id}/elimina` | Delete a price | — | Redirect | 303, 404 |
| 20 | POST | `/admin/segnalazioni/{report_id}/moderazione` | Approve, reject, or reset a report | `stato` | Redirect | 303, 404 |
| 21 | GET | `/admin/importazione` | Render the MIMIT import page | — | Italian Jinja HTML | 200 |
| 22 | POST | `/admin/importazione` | Import station prices from CSV or JSON | `file` | Italian Jinja HTML | 200, 400, 413 |

---

## 7. Next Steps

1. Run **azure-project-scaffold** to execute this plan
2. Run **azure-project-integrate** to wire the frontend to live data, smoke-test the backend, and create the migrations
3. Run **azure-debug-plan** → **azure-debug-generate** for Docker emulators and VS Code debugging
4. Run the **azure-deploy** agent when ready; it uses **azure-app-onboard** for architecture, cost estimation, IaC generation, provisioning, and health verification
