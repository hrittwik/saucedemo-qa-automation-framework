# SauceDemo QA Automation Framework

[![QA Automation Suite](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/ci.yml)

> Production-grade Selenium + Python test automation framework for [SauceDemo](https://www.saucedemo.com).  
> Runs identically on **Windows**, **macOS**, and **Linux** — no shell scripts, no Makefile, no OS-specific commands.

---

## Table of Contents

1. [Framework Choice & Rationale](#1-framework-choice--rationale)
2. [Architecture Overview](#2-architecture-overview)
3. [Setup & Run Instructions](#3-setup--run-instructions)
4. [CI/CD Pipeline](#4-cicd-pipeline)
5. [Test Coverage Summary](#5-test-coverage-summary)

---

## 1. Framework Choice & Rationale

### Stack: Python + Selenium + pytest + Allure

| Component | Choice | Rationale |
|---|---|---|
| Language | **Python 3.11** | Readable syntax, rich ecosystem, first-class Selenium support |
| Browser Automation | **Selenium 4** | Industry standard, supports Chrome / Firefox / Edge on all OS |
| Test Runner | **pytest** | Powerful fixture system, parametrize, clean plugin ecosystem |
| Reporting | **pytest-html + Allure** | HTML for quick CI review; Allure for rich stakeholder-friendly reports |
| Driver Management | **webdriver-manager** | Auto-downloads correct drivers — no manual binary setup on any OS |
| Retry | **pytest-rerunfailures** | Configurable retry for network-sensitive environments |
| Config | **pyproject.toml** | Single modern config file; cross-platform, no `.ini` files |

### Alternatives Considered

| Alternative | Why Not Chosen |
|---|---|
| **Playwright + Python** | Excellent choice with auto-waits. Selenium chosen to demonstrate explicit wait architecture. |
| **Cypress** | JavaScript-only, limited browser support. Python preferred for broader team compatibility. |
| **WebdriverIO** | Strong for JS teams. Python preferred for data-science-adjacent QA tooling. |

---

## 2. Architecture Overview

```
saucedemo-qa-framework/
├── .github/workflows/ci.yml       # GitHub Actions pipeline
├── src/
│   ├── config/settings.py         # All config — loaded from env vars
│   ├── fixtures/                  # Test data (JSON) — never hardcoded
│   │   ├── users.json
│   │   ├── products.json
│   │   └── checkout.json
│   ├── pages/                     # Page Object Model layer
│   │   ├── base_page.py           # All Selenium calls live here
│   │   ├── login_page.py
│   │   ├── inventory_page.py
│   │   ├── cart_page.py
│   │   └── checkout_page.py
│   ├── tests/                     # Test files by feature
│   │   ├── test_auth.py
│   │   ├── test_catalog.py
│   │   ├── test_cart.py
│   │   ├── test_checkout.py
│   │   └── test_performance.py
│   └── utils/
│       ├── driver_factory.py      # Chrome / Firefox / Edge — all OS
│       ├── wait_helper.py         # Smart explicit waits, zero sleep()
│       ├── screenshot_helper.py   # Auto-screenshot on failure
│       ├── data_loader.py         # JSON fixture loader
│       └── assertions.py          # Custom assertions with clear messages
├── conftest.py                    # pytest fixtures + failure hooks
├── pyproject.toml                 # Runner config (cross-platform)
├── run.py                         # Single run script — Windows/Mac/Linux
├── requirements.txt
├── .env.example
└── README.md
```

### Key Design Decisions

**Page Object Model:** All locators and UI interactions live in page classes. Tests call `login_page.login(user, password)` — never `driver.find_element()` directly. Locator changes need updating in exactly one place.

**pyproject.toml over pytest.ini:** A single modern config file that works identically on all operating systems without path-separator issues.

**run.py over shell scripts:** One Python script works on Windows, macOS, and Linux. No Bash, no PowerShell, no Makefile — just `python run.py`.

**Smart waits only:** `WaitHelper` wraps `WebDriverWait`. There is no `time.sleep()` anywhere in the framework. The `performance_glitch_user` tests demonstrate this with extended explicit waits.

---

## 3. Setup & Run Instructions

### Prerequisites

| Tool | Version | Download |
|---|---|---|
| Python | 3.11+ | [python.org](https://python.org) |
| Chrome | Latest | [google.com/chrome](https://google.com/chrome) |
| Git | Any | [git-scm.com](https://git-scm.com) |

Firefox and Edge are also supported — see [Browser Options](#browser-options).

---

### Step 1 — Get the code

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

---

### Step 2 — Create a virtual environment

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows — Command Prompt:**
```cmd
python -m venv .venv
.venv\Scripts\activate
```

**Windows — PowerShell:**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

You will see `(.venv)` at the start of your terminal prompt when active.

---

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

`webdriver-manager` automatically downloads the correct ChromeDriver for your Chrome version. No manual driver downloads needed on any OS.

---

### Step 4 — Run the tests

```bash
python run.py
```

`run.py` auto-creates your `.env` from `.env.example`, creates `reports/` and `screenshots/` directories, then runs pytest. No other setup needed.

---

### Run options

```bash
# Run all tests
python run.py

# Run a specific suite only
python run.py --suite auth
python run.py --suite catalog
python run.py --suite cart
python run.py --suite checkout
python run.py --suite performance

# Watch the browser run (great for debugging)
python run.py --headed

# Use a different browser
python run.py --browser firefox
python run.py --browser edge

# Run tests in parallel (faster)
python run.py --parallel 4

# Also generate Allure results
python run.py --allure

# Open HTML report automatically after run
python run.py --open-report

# Combine options freely
python run.py --suite checkout --headed --browser firefox
python run.py --parallel 4 --allure --open-report
```

---

### Step 5 — View the report

**HTML report** (always generated, no extra tools needed):

```bash
# macOS
open reports/report.html

# Windows
start reports/report.html

# Linux
xdg-open reports/report.html

# All OS (automatic)
python run.py --open-report
```

**Allure report** (richer UI, optional):

```bash
# Install Allure CLI first:
# macOS:       brew install allure
# Windows:     scoop install allure
# Linux:       sudo apt install allure

python run.py --allure
allure serve allure-results
```

---

### Browser Options

| Browser | Windows | macOS | Linux |
|---|---|---|---|
| `chrome` (default) | ✅ | ✅ | ✅ |
| `firefox` | ✅ | ✅ | ✅ |
| `edge` | ✅ | ✅ | ✅ |

---

### Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | Virtual environment not active — repeat Step 2 |
| `ChromeDriver version mismatch` | `pip install --upgrade webdriver-manager` |
| Tests time out on `performance_glitch_user` | Add `EXPLICIT_WAIT=30` to your `.env` |
| `allure: command not found` | Install Allure CLI (optional — see Step 5) |
| `SessionNotCreatedException` | Chrome not installed or not in PATH |
| PowerShell script blocked | Run: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |

---

## 4. CI/CD Pipeline

Defined in `.github/workflows/ci.yml`. Triggers on push and pull request to `main`.

```
Checkout → Setup Python 3.11 → Install Chrome → pip install → Run tests → Upload artifacts
```

**Viewing reports after CI:**
1. Go to **Actions** tab in your GitHub repo
2. Click the latest workflow run
3. Scroll to **Artifacts** at the bottom
4. Download `pytest-html-report` and open `report.html`

Replace `YOUR_USERNAME/YOUR_REPO` in the badge at the top of this file.

---

## 5. Test Coverage Summary

### Covered (~35 test cases)

| Module | Scenarios |
|---|---|
| **Authentication** | Valid login, wrong password, empty fields, SQL injection, locked-out user, error dismissal, session persistence, logout, post-logout redirect guard |
| **Product Catalog** | Product count, names, prices, page title, sort A→Z / Z→A / price asc / price desc, standard_user image baseline, problem_user duplicate image detection |
| **Shopping Cart** | Add single item, add multiple items, remove item, remove all (empty state), persistence after Continue Shopping, badge persistence on navigation |
| **Checkout Flow** | Complete E2E purchase, confirmation header + image + Back Home, missing field validation (3 scenarios), order total math verification |
| **Performance & Resilience** | performance_glitch_user smart-wait login, timing comparison, error_user login + cart state + checkout state documentation |

### Intentionally excluded

| Area | Reason |
|---|---|
| Product detail pages | Out of assessment scope. Easily extended with a `ProductDetailPage` class. |
| Cross-browser parallel CI | Supported locally (`--browser firefox --parallel 4`) but omitted from CI to keep pipeline fast. |
| API tests | SauceDemo has no public API. |
| Pixel-level visual regression | Assessment specifies src attribute comparison — faster and more reliable than pixel diffing. |
| Mobile / responsive | Out of scope. Extendable via Selenium Grid + mobile emulation. |

---

## Author

**Hrittwik Barua**  

