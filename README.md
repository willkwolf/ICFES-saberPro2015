# ICFES Saber Pro 2015 — Digital Transparency & Verification Artifact

[![Live Website](https://img.shields.io/badge/GitHub_Pages-Live_Site-success?style=flat-square&logo=github)](https://willkwolf.github.io/ICFES-saberPro2015/)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-blue?style=flat-square)](LICENSE)
[![Verification Engine](https://img.shields.io/badge/Verification_Engine-8%2F8_PASS-brightgreen?style=flat-square)](VERIFICATION_REPORT.md)
[![E2E Tests](https://img.shields.io/badge/E2E_Tests-186%2F186_PASS-brightgreen?style=flat-square)](TEST_READY.md)
[![Accessibility](https://img.shields.io/badge/Accessibility-WCAG_2.1_AA-informational?style=flat-square)](docs/index.html)
[![i18n](https://img.shields.io/badge/i18n-Español_|_English-informational?style=flat-square)](locales/)

> **Live Deployment:** [https://willkwolf.github.io/ICFES-saberPro2015/](https://willkwolf.github.io/ICFES-saberPro2015/)  
> **Source Repository:** [https://github.com/willkwolf/ICFES-saberPro2015](https://github.com/willkwolf/ICFES-saberPro2015)

---

## Overview / Resumen

This repository hosts the modernized public digital artifact, data visualization suite, and independent statistical verification engine for the official Colombian State Examination **SABER PRO 2015** (Registration Code: `EK201532097061`) for **William Camilo Artunduaga Viana** (*Industrial Engineering, Universidad ICESI, Cali, Colombia*).

*Este repositorio contiene el artefacto digital público, conjunto de visualizaciones interactivas y motor de verificación matemática independiente para los resultados oficiales de las pruebas de Estado **Saber Pro 2015**.*

### Core Principles
- **Institutional Neutrality & Integrity:** Objective, verifiable psicometric data presentation without speculative or judgmental interpretations.
- **Digital Sovereignty:** 100% local self-contained code and assets with **zero external CDN dependencies**.
- **Independent Verification:** Decoupled mathematical audit engine confirming zero data drift against official primary source streams.
- **Accessible & Responsive UX:** Mobile-first architecture compliant with **WCAG 2.1 Level AA** and Edward Tufte's high data-to-ink ratio principles.
- **Bilingual Architecture (i18n):** Real-time, decoupled localization supporting both English and Spanish with native `Intl` number and date formatters.

---

## Official Examination Metadata

| Dimension | Specification |
| :--- | :--- |
| **Examinee** | William Camilo Artunduaga Viana |
| **Registration Number** | `EK201532097061` |
| **Academic Program** | Industrial Engineering (*Ingeniería Industrial*) |
| **Higher Education Institution** | Universidad ICESI (Cali, Colombia) |
| **Reference Group** | Engineering (*Ingeniería*) |
| **Examination Date** | November 22, 2015 |
| **Primary Source** | ICFES Official Certificate (`assets/EK201532097061.pdf`) |

---

## Executive Results Summary

The Saber Pro examination evaluates standardized competencies with an item-response-theory (IRT) scale standardized to mean $\mu = 10.0$ and standard deviation $\sigma = 1.0$.

### Modular Scores & Reference Benchmarks

| Module | Type | Score | Level | Quintile | Ref. Mean ($\mu_{ref}$) | Nat. Mean ($\mu_{nac}$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Written Communication** | Generic | **9.2** | 3 | **Q1** | 10.0 | 10.0 |
| **Quantitative Reasoning** | Generic | **11.5** | 3 | **Q4** | 10.8 | 10.1 |
| **Critical Reading** | Generic | **11.6** | 3 | **Q5** | 10.6 | 10.5 |
| **Citizenship Competencies** | Generic | **10.6** | — | **Q4** | 10.2 | 10.1 |
| **English** | Generic | **11.7** | B1 | **Q4** | 10.7 | 10.2 |
| **Project Formulation** | Specific | **10.1** | — | **Q3** | 10.0 | 10.0 |
| **Scientific Thinking (Math & Stats)** | Specific | **12.9** | — | **Q5** | 10.0 | 10.1 |
| **Production & Logistics Systems** | Specific | **11.1** | — | **Q5** | 10.0 | 10.0 |

### Audited Global Performance
- **Exact Overall Mean:** **`11.0875`** (Standard rounded: `11.1`; reconciles historical legacy typo of `11.2`).
- **Generic Modules Mean:** **`10.9200`**
- **Specific Engineering Mean:** **`11.3667`**
- **Top Quintiles (Q4 / Q5):** **`6 / 8` modules (75.0%)** in the top 40% of the engineering reference group.
- **Above National Mean:** **`7 / 8` modules (87.5%)** exceed country-wide averages.

---

## Project Architecture

```text
├── index.html                      # Root public entrypoint (GitHub Pages root)
├── docs/index.html                 # Dual deployment target (100% bit-parity)
├── .nojekyll                       # Bypasses Jekyll on GitHub Pages
├── LICENSE                         # Creative Commons CC BY 4.0
├── VERIFICATION_REPORT.md          # Generated statistical audit report (PASS 8/8)
├── TEST_READY.md                   # Full test certification report (186/186 PASS)
├── assets/                         # Official PDF certificate & methodology guides
├── css/                            # Modular WCAG AA & Tufte styling
│   ├── variables.css               # Design tokens, palette, and dark mode
│   ├── typography.css              # International sans-serif font stack & clamp()
│   ├── layout.css                  # Fluid grids & responsive landmarks
│   ├── components.css              # Cards, Tufte tables, and accessible badges
│   └── accessibility.css           # Focus rings, skip links, and ARIA rules
├── data/                           # Canonical structured JSON & audit outputs
│   ├── saber_pro_2015.json         # Normalized dataset
│   └── verification_report.json    # Machine-readable verification output
├── js/                             # Decoupled ES Modules
│   ├── app.js                      # Application bootstrap & lifecycle
│   ├── i18n.js                     # Localization engine with native Intl formatters
│   ├── charts.js                   # Chart.js visualizations (Bars, Gauss, Radar)
│   └── tables.js                   # Responsive tables with container queries
├── locales/                        # Bilingual translation dictionaries
│   ├── en.js                       # English dictionary
│   └── es.js                       # Spanish dictionary
├── scripts/                        # Statistical verification engine
│   ├── verify_statistics.py        # Independent validator (8 mathematical rules)
│   └── test_verify_statistics.py   # Unit test suite (28 tests)
├── tests/                          # Automated quality assurance
│   ├── e2e_runner.py               # 4-tier E2E runner (186 tests)
│   ├── test_e2e_suite.py           # Opaque-box test battery
│   ├── test_frontend.py            # DOM, CSS & accessibility tests
│   └── test_i18n.py                # Locale parity & Intl format tests
└── vendor/                         # Self-contained libraries (zero CDN)
    └── chart.umd.min.js            # Locally bundled Chart.js v4.4.x
```

---

## Quick Start & Local Reproduction

The entire platform runs without third-party services or package managers.

### 1. View the Web Application Locally
```bash
# Start local static server
python -m http.server 8000

# Open in browser:
# http://localhost:8000/
```

### 2. Run the Independent Statistical Verification Engine
```bash
# Validates 8 formal mathematical rules against raw PDF stream
python scripts/verify_statistics.py --verbose
```

### 3. Run the Automated Test Suite (244 Tests)
```bash
# Full 4-tier E2E test suite (186 tests)
python tests/e2e_runner.py

# Verification engine unit tests (28 tests)
python scripts/test_verify_statistics.py

# Frontend and accessibility tests (13 tests)
python tests/test_frontend.py

# Internationalization tests (9 tests)
python tests/test_i18n.py
```

---

## Reconciliation of Historical Anomalies

In accordance with institutional transparency principles, legacy website discrepancies were audited and formally documented:

1. **A-01 (Arithmetic Mean):** Canonical mean is $88.7 / 8 = \mathbf{11.0875}$ (rounded to `11.1`). Corrects legacy card showing `11.2`.
2. **A-02 (Standard Deviations):** Empirical standard deviations vary per module ($1.0$ to $1.5$), superseding the simplistic legacy claim of constant $\sigma = 1.0$.
3. **A-03 (Written Communication Quintile):** Score $9.2$ falls in empirical Quintile I ($0-20\%$) based on discrete rubric calibration, despite theoretical continuous normal cutoff at $21.2\%$.
4. **A-04 (English Sample Cohort):** National sample size is $N = 310,468$ (vs $216,501$ for other modules) due to joint administration with Saber TyT cohorts.
5. **A-05 (Performance Levels):** Official levels exist only for 4 modules (Writing: 3, Quant: 3, Reading: 3, English: B1). Specific modules do not define levels.
6. **A-06 (Link Integrity):** Fixed broken filenames and removed placeholder URLs in favor of canonical repository paths.
7. **A-07 (Privacy & PII Protection):** National ID number (Cédula) redacted in compliance with Colombian Law 1581 of 2012; public registration code `EK201532097061` retained.

---

## Deployment on GitHub Pages

The application is deployed to **GitHub Pages** from the repository:

- **Bypass Jekyll (`.nojekyll`):** Ensures directory structures and dot-files are served accurately.
- **Strictly Relative Paths:** Enables identical execution at root domains or project subdirectories.
- **Bit-by-Bit Parity:** Root `index.html` and `docs/index.html` are identical to support both root (`/`) and docs (`/docs`) publishing configurations.

---

## License & Attribution

- **Source Code & Documentation:** Distributed under the **[Creative Commons Attribution 4.0 International License (CC BY 4.0)](LICENSE)**.
- **Official Data & Methodology:** Intellectual property of the **Instituto Colombiano para la Evaluación de la Educación (ICFES)**.
- **Purpose:** Academic consultation, pedagogical transparency, and independent statistical verification.
