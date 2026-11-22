# ICFES SABER PRO 2015 — Modernización, Verificación Estadística & Despliegue Público
## Modernization, Independent Statistical Verification & Public Digital Artifact

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](LICENSE)
[![Verification Engine: PASS](https://img.shields.io/badge/Verification_Engine-8%2F8_PASS-brightgreen.svg)](VERIFICATION_REPORT.md)
[![E2E Test Battery: PASS](https://img.shields.io/badge/E2E_Tests-186%2F186_PASS-brightgreen.svg)](TEST_READY.md)
[![Accessibility: WCAG 2.1 AA](https://img.shields.io/badge/Accessibility-WCAG_2.1_AA-blue.svg)](docs/index.html)
[![i18n: es / en](https://img.shields.io/badge/i18n-Espa%C3%B1ol_%7C_English-blue.svg)](locales/)
[![GitHub Pages](https://img.shields.io/badge/Deploy-GitHub_Pages-success.svg)](https://willkwolf.github.io/ICFES-saberPro2015/)

---

## 1. 📋 Descripción del Proyecto e Institucionalidad / Project Overview

Este repositorio contiene la modernización técnica integral, auditoría estadística y publicación en acceso abierto de los resultados oficiales de las pruebas de Estado **ICFES Saber Pro 2015** (registro oficial **EK201532097061**).

El proyecto transforma un sitio web estático tradicional en un **artefacto digital moderno, soberano, bilingüe (español/inglés), accesible (WCAG 2.1 AA), responsive (mobile-first)** y respaldado por un **motor independiente de verificación matemática y trazabilidad estadística**.

### Principios Institucionales y Metodológicos
1. **Neutralidad Institucional**: Presentación técnica, objetiva y rigurosa de los resultados. Se eliminan interpretaciones valorativas o sesgadas, enfatizando el carácter psicométrico estandarizado de la prueba.
2. **Diferenciación de Datos**: Separación arquitectónica estricta entre:
   - *Datos Oficiales de Origen*: Extraídos del certificado oficial emitido por el ICFES (`assets/EK201532097061.pdf`).
   - *Datos Canónicos Estructurados*: Formato interoperable JSON (`data/saber_pro_2015.json`).
   - *Indicadores Calculados*: Recomputación matemática verificable de medias, proporciones y percentiles.
   - *Visualizaciones Derivadas*: Gráficos estadísticos e interfaces reactivas.
3. **Privacidad y Soberanía**: Salvaguarda estricta de datos personales sensibles (Cédula de Ciudadanía anonimizada según la Ley 1581 de 2012; número de registro público preservado: `EK201532097061`). Independencia total de CDNs externas o dependencias privativas.

---

## 2. 📄 Metadatos Oficiales del Examen / Official Exam Metadata

- **Examinado / Examinee:** William Camilo Artunduaga Viana
- **Código de Registro / Registration Code:** `EK201532097061`
- **Programa Académico / Academic Program:** Ingeniería Industrial
- **Institución de Educación Superior / Institution:** Universidad ICESI (Cali, Colombia)
- **Grupo de Referencia / Reference Group:** Ingeniería
- **Fecha del Examen / Exam Date:** 22 de Noviembre de 2015
- **Fuente Oficial Primaria / Official Primary Source:** ICFES (*Instituto Colombiano para la Evaluación de la Educación*) — `assets/EK201532097061.pdf`

---

## 3. 📊 Resultados Resumidos y Métricas / Executive Results Summary

### Competencias Genéricas (5 Módulos Obligatorios)
$$\bar{X}_{gen} = \frac{9.2 + 11.5 + 11.6 + 10.6 + 11.7}{5} = \mathbf{10.9200}$$

| Módulo Oficial | Puntaje | Nivel | Quintil | Media Ref. ($\mu_{ref}$) | Desv. Ref. ($\sigma_{ref}$) | Media Nac. ($\mu_{nac}$) | Desv. Nac. ($\sigma_{nac}$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Comunicación Escrita** | **9.2** | 3 | **Q1** | 10.0 | 1.0 | 10.0 | 1.0 |
| **Razonamiento Cuantitativo** | **11.5** | 3 | **Q4** | 10.8 | 1.2 | 10.1 | 1.2 |
| **Lectura Crítica** | **11.6** | 3 | **Q5** | 10.6 | 1.0 | 10.5 | 1.0 |
| **Competencias Ciudadanas** | **10.6** | N/D | **Q4** | 10.2 | 1.0 | 10.1 | 1.0 |
| **Inglés** | **11.7** | B1 | **Q4** | 10.7 | 1.5 | 10.2 | 1.3 |

### Competencias Específicas de Ingeniería (3 Módulos de Área)
$$\bar{X}_{esp} = \frac{10.1 + 12.9 + 11.1}{3} = \mathbf{11.3667}$$

| Módulo Oficial | Puntaje | Nivel | Quintil | Media Ref. ($\mu_{ref}$) | Desv. Ref. ($\sigma_{ref}$) | Media Nac. ($\mu_{nac}$) | Desv. Nac. ($\sigma_{nac}$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Formulación de Proyectos de Ingeniería** | **10.1** | N/D | **Q3** | 10.0 | 1.0 | 10.0 | 1.0 |
| **Pensamiento Científico (Matemáticas y Estadística)** | **12.9** | N/D | **Q5** | 10.0 | 1.1 | 10.1 | 1.1 |
| **Diseño de Sistemas Productivos y Logísticos** | **11.1** | N/D | **Q5** | 10.0 | 1.0 | 10.0 | 1.0 |

### Indicadores Globales Auditados
- **Media Aritmética Global Exacta**: **`11.0875`** (redondeo estándar: `11.1`; reconciliación de la discrepancia histórica legacy de `11.2`).
- **Módulos en Quintiles Superiores (Q4 o Q5)**: **`6 / 8`** (**75.0%**).
- **Módulos Superiores a la Media Nacional**: **`7 / 8`** (**87.5%**).
- **Módulos Superiores al Grupo de Referencia (Ingeniería)**: **`7 / 8`** (**87.5%**).

---

## 4. 📁 Estructura del Repositorio Modernizado / Repository Architecture

El repositorio implementa una estricta separación de responsabilidades:

```text
ICFES-SaberPro 2015/
├── .gitignore                      # Soberanía del repo y exclusión de cachés/agentes
├── .nojekyll                       # Bypass del procesador Jekyll para GitHub Pages
├── LICENSE                         # Licencia abierta Creative Commons CC BY 4.0
├── README.md                       # Documentación técnica, arquitectónica y operativa
├── VERIFICATION_REPORT.md          # Reporte generado por el motor de auditoría estadística
├── TEST_READY.md                   # Documentación formal de la batería de pruebas E2E
├── index.html                      # Punto de entrada frontend principal (100% estático)
├── assets/
│   ├── EK201532097061.pdf          # Certificado oficial original emitido por el ICFES
│   ├── interpretacion_estadistica.md # Fundamentos estadísticos y psicométricos
│   └── metodologia_icfes.md        # Marco metodológico oficial del examen ICFES
├── css/
│   ├── variables.css               # Design tokens: colores, contraste WCAG, escalas
│   ├── typography.css              # Tipografía fluida (clamp), legibilidad y ritmo
│   ├── layout.css                  # Grillas adaptables, contenedores y diseño responsivo
│   ├── components.css              # Tarjetas KPI, quintiles, controles y filtros
│   └── accessibility.css           # Focus indicators, modo alto contraste, skip link
├── data/
│   ├── saber_pro_2015.json         # Dataset canónico estructurado y normalizado
│   └── verification_report.json    # Resultados estructurados de la auditoría estadística
├── docs/
│   └── index.html                  # Paridad 100% bitstream con index.html para GitHub Pages
├── js/
│   ├── app.js                      # Controlador reactivo de la aplicación y ciclo de vida
│   ├── i18n.js                     # Motor de internacionalización y formateo con Intl nativo
│   ├── charts.js                   # Visualizaciones estadísticas (Barras, Gauss, Radar)
│   └── tables.js                   # Renderizado y responsividad de tablas (@container)
├── locales/
│   ├── es.js                       # Diccionario de traducción y glosario en Español
│   └── en.js                       # Diccionario de traducción y glosario en Inglés
├── scripts/
│   ├── verify_statistics.py        # Motor independiente de verificación matemática (8 reglas)
│   └── test_verify_statistics.py   # Suite de pruebas unitarias del motor de verificación (28 tests)
├── tests/
│   ├── e2e_runner.py               # Ejecutor CLI y generador de reportes de pruebas E2E
│   ├── test_e2e_suite.py           # Batería completa E2E de 4 niveles (186 pruebas)
│   ├── test_frontend.py            # Pruebas unitarias de estructura DOM y frontend (13 tests)
│   └── test_i18n.py                # Pruebas de paridad i18n y formateadores nativos (9 tests)
└── vendor/
    └── chart.umd.min.js            # Bundle local de Chart.js v4.4.x (100% autónomo, sin CDN)
```

---

## 5. 🔬 Motor Independiente de Verificación Estadística / Verification Engine

Para garantizar la integridad matemática y la trazabilidad de los datos, el repositorio incluye un motor de validación en Python estándar (`scripts/verify_statistics.py`) que opera de forma totalmente desacoplada de la interfaz gráfica.

### Reglas de Validación Auditadas (`RULE-01` a `RULE-08`)
1. **`RULE-01-SOURCE-PARITY`**: Descomprime los flujos binarios `FlateDecode` del PDF oficial (`assets/EK201532097061.pdf`) mediante `zlib` y verifica la paridad exacta al 100% de puntajes, niveles, quintiles y censos contra `data/saber_pro_2015.json`.
2. **`RULE-02-CARD-ARITHMETIC`**: Recomputa la sumatoria ($88.7000$) y la media aritmética global ($11.0875$). Audita y documenta la discrepancia histórica A-01 frente al valor heredado ($11.2$).
3. **`RULE-03-SUBGROUP-MEANS`**: Valida las medias de subgrupos modulares: genéricas ($10.9200$) y específicas de ingeniería ($11.3667$).
4. **`RULE-04-PROPORTION-CHECKS`**: Valida las proporciones de rendimiento (6/8 en Q4/Q5, 7/8 sobre media nacional y de referencia).
5. **`RULE-05-TABLE-CHART-PARITY`**: Verifica paridad con cero derivas entre el dataset JSON, las filas de las tablas HTML y las series numéricas de Chart.js.
6. **`RULE-06-POPULATION-BOUNDS`**: Verifica que $N_{ref} \le N_{nac}$ en todos los módulos y audita la divergencia poblacional en Inglés (A-04).
7. **`RULE-07-HYGIENE-PII-GUARD`**: Escanea exhaustivamente todos los archivos de texto del repositorio garantizando **cero apariciones** de la Cédula de Ciudadanía colombiana.
8. **`RULE-08-LINK-INTEGRITY`**: Valida la integridad de todos los hipervínculos internos y descarta dominios de plantilla (`TU_USUARIO`).

### Cómo Ejecutar la Verificación Estadística
```bash
# Ejecutar verificación formal con reporte detallado en consola
python scripts/verify_statistics.py --verbose

# Ejecutar suite de pruebas unitarias del motor de verificación (28 tests)
python scripts/test_verify_statistics.py
```

*Los resultados completos se actualizan automáticamente en `VERIFICATION_REPORT.md` y `data/verification_report.json`.*

---

## 6. 🔍 Registro de Anomalías Históricas Reconciliadas / Audit Anomalies

En cumplimiento del principio de trazabilidad y no alteración silenciosa de datos, las discrepancias identificadas en el sitio web original han sido formalmente categorizadas y documentadas:

| ID | Categoría | Valor Publicado Heredado | Valor Canónico Verificado | Explicación Técnica y Dictamen de Auditoría |
| :---: | :--- | :---: | :---: | :--- |
| **`A-01`** | Aritmética de Tarjeta | `11.2` | `11.0875` | Error tipográfico o de redondeo manual intermedio en la tarjeta principal. El promedio matemático exacto de los 8 puntajes es $88.7 / 8 = 11.0875$ (redondeo estándar $11.1$). |
| **`A-02`** | Parámetros Psicométricos | $\sigma = 1.0$ | Rango empírico: $1.0$ a $1.5$ | Omisión de las desviaciones estándar empíricas en las tablas web originales y afirmación simplista de $\sigma=1.0$ global (p. ej. Razonamiento Cuantitativo tiene $\sigma=1.2$; Inglés $\sigma=1.5 / 1.3$; Pensamiento Científico $\sigma=1.1$). |
| **`A-03`** | Distribución de Percentil | $Q1$ | Empírico: $Q1$ vs Gauss: $Q2$ ($21.2\%$) | En Comunicación Escrita ($9.2$), la distribución normal teórica continua $\Phi(-0.8) = 21.19\%$ caería en Quintil II, pero el reporte oficial asigna Quintil I debido a la distribución empírica discreta acumulada (ECDF) de la rúbrica holística del ICFES. |
| **`A-04`** | Tamaño de Muestra | $N = 216,501$ | $N = 310,468$ | Divergencia en la muestra nacional de Inglés ($+93,967$ estudiantes evaluados respecto a la cohorte universitaria estándar) explicada por la administración conjunta de la prueba con el nivel técnico y tecnológico (Saber TyT). |
| **`A-05`** | Niveles de Desempeño | Ausentes | Oficiales en 4 de 8 módulos | En 2015, el ICFES solo definió niveles de desempeño para 4 competencias (Comunicación Escrita, Razonamiento Cuantitativo, Lectura Crítica e Inglés). En Competencias Ciudadanas y módulos específicos de ingeniería la escala no contempla niveles. |
| **`A-06`** | Enlaces Rotos | Rutas con guiones / `TU_USUARIO` | Nombres normalizados con guion bajo / repo canónico | Reparación de referencias rotas en enlaces internos (`interpretacion-estadistica.md` $\rightarrow$ `interpretacion_estadistica.md`) y reemplazo del URL genérico de plantilla por el repositorio canónico. |
| **`A-07`** | Privacidad (PII) | Documento expuesto | Anonimizado | Anonimización estricta del número de Cédula de Ciudadanía en todas las capas del repositorio público, preservando únicamente el número de registro oficial `EK201532097061`. |

---

## 7. 🧪 Batería de Pruebas Automatizadas / Automated Test Battery

El repositorio cuenta con una infraestructura de pruebas de **caja opaca** exhaustiva (236 pruebas en total), ejecutables sin dependencias externas usando la librería estándar de Python (`unittest`, `html.parser`, `subprocess`, `json`, `math`, `zlib`):

```bash
# 1. Batería completa End-to-End (E2E) - 186 pruebas en 4 niveles
python tests/e2e_runner.py

# 2. Pruebas de paridad i18n y formateadores nativos (9 pruebas)
python tests/test_i18n.py

# 3. Pruebas de accesibilidad, layout y componentes frontend (13 pruebas)
python tests/test_frontend.py

# 4. Pruebas unitarias del motor de verificación estadística (28 pruebas)
python scripts/test_verify_statistics.py
```

### Arquitectura de la Suite E2E (`tests/e2e_runner.py`)
- **Nivel 1 (Tier 1: Feature Coverage — 80 pruebas)**: Cobertura exhaustiva de funcionalidad básica a través de las 16 áreas de características (F1 a F17).
- **Nivel 2 (Tier 2: Boundary & Corner Cases — 80 pruebas)**: Análisis de valores límite (BVA), entradas vacías/nulas, rutas con caracteres especiales, denominadores cero y puntajes extremos.
- **Nivel 3 (Tier 3: Cross-Feature Integration — 16 pruebas)**: Pruebas de integración por pares (paridad datos-tablas, gráficos-i18n, tokens CSS-accesibilidad, enlaces-rutas de despliegue).
- **Nivel 4 (Tier 4: Real-World Scenarios — 10 recorridos completos)**:
  1. *Mobile Student Journey*: Navegación completa en viewport de 375x667 px sin desbordamiento horizontal.
  2. *International Recruiter*: Conmutación a inglés y verificación de títulos y descriptores traducidos.
  3. *Statistical Auditor*: Descompresión de streams PDF binarios y recálculo matemático de medias y proporciones.
  4. *Screen-Reader User*: Navegación accesible por teclado, skip-links, encabezados con `scope` y atributos ARIA.
  5. *Static Crawler*: Rastreo sin enlaces rotos 404 y verificación de `.nojekyll`.
  6. *Data Scientist Audit*: Reconciliación empírica vs teórica gaussiana ($\mu=10, \sigma=1$).
  7. *Security & Privacy Audit*: Barrido regex confirmando 0 filtraciones de documento de identidad.
  8. *Airgapped Visitor*: Carga 100% offline sin peticiones externas de red.
  9. *Faculty Evaluator*: Verificación del subgrupo de ingeniería (media 11.3667).
  10. *Open Source Contributor*: Clonación, validación de licencia CC BY 4.0 y ejecución de CLI.

---

## 8. 🌐 Accesibilidad, Diseño Responsivo e i18n / UI, Accessibility & i18n

### Accesibilidad (WCAG 2.1 Nivel AA)
- **Contraste Tipográfico**: Ratios de contraste superiores a 4.5:1 para texto normal y 3.0:1 para elementos de interfaz y gráficos. La etiqueta de Quintil I (Q1) implementa un contraste accesible optimizado (`#8c2020` sobre `#fdf2f2`).
- **Navegación por Teclado**: Enlace de salto rápido al contenido principal (`#main-content`), indicadores de foco visibles (`:focus-visible` con outline de 2px y contraste compensado) y orden semántico de tabulación.
- **Diseño Responsivo Fluido**: Tipografía adaptativa mediante `clamp()`, grillas fluidas y tablas adaptables mediante CSS `@container` queries, garantizando visualización sin desbordamiento horizontal desde viewports de **320px** hasta monitores de alta resolución.

### Internacionalización Desacoplada (i18n)
- **Arquitectura**: Separación total entre cadenas de texto (`locales/es.js`, `locales/en.js`) y la lógica de la interfaz (`js/i18n.js`).
- **Conmutador Reactivo**: Cambio de idioma instantáneo entre Español e Inglés sin recarga de página, con sincronización dinámica del atributo `<html lang="...">` y regiones `aria-live`.
- **Formateadores Nativos `Intl`**: Adaptación cultural de formatos numéricos y fechas:
  - *Español (`es-CO`)*: Separador decimal con coma (`11,1`), miles con punto (`43.932`).
  - *Inglés (`en-US`)*: Separador decimal con punto (`11.1`), miles con coma (`43,932`).

### Visualizaciones Estadísticas Autónomas
- Implementadas con **Chart.js v4.4.x** alojado localmente en `vendor/chart.umd.min.js` (cero llamadas a CDN externas).
- **Gráfico de Barras Agrupadas**: Comparación interactiva (Puntaje vs Media de Referencia vs Media Nacional), adaptable a orientación horizontal en pantallas móviles.
- **Curva Normal Estándar ($\mu=10, \sigma=1$)**: Visualización continua de la campana de Gauss con indicación de percentiles y desviación del examinado.
- **Perfil Radar de Competencias**: Diagrama radial que proyecta el equilibrio de habilidades evaluadas.

---

## 9. 🚀 Despliegue en GitHub Pages / GitHub Pages Deployment

La aplicación web está diseñada para desplegarse de manera 100% estática en **GitHub Pages**:

1. **Rutas Estrictamente Relativas**: Todos los recursos (hojas de estilo, scripts, fuentes, datos JSON, PDF) se referencian mediante rutas relativas (`css/`, `js/`, `vendor/`, `data/`, `assets/`), lo cual garantiza funcionamiento idéntico en la raíz de un dominio o en subdirectorios de proyectos (`/ICFES-saberPro2015/`).
2. **Compatibilidad Dual (Root y `/docs`)**:
   - El archivo `index.html` en la raíz y `docs/index.html` mantienen **100% de paridad binaria (bitstream SHA-256)**.
   - El sitio puede configurarse en GitHub Pages tanto desde la rama `feat/modernization-ghpages` en `/` (raíz) como desde `/docs`.
3. **Bypass de Jekyll (`.nojekyll`)**:
   - La presencia del archivo `.nojekyll` en la raíz evita que el procesador estático de GitHub Pages descarte u oculte archivos o directorios con prefijos especiales.

Para explorar el sitio en un servidor web local:
```bash
# Iniciar servidor estático local en el puerto 8000
python -m http.server 8000

# Abrir en el navegador:
# http://localhost:8000/
# o http://localhost:8000/docs/
```

---

## 10. 📜 Licencia y Atribución / License & Attribution

Este repositorio, su código fuente, arquitectura y documentación se distribuyen bajo la licencia **[Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE)**.

### Atribución Institucional
- Los resultados oficiales del examen y las metodologías de evaluación son propiedad intelectual del **Instituto Colombiano para la Evaluación de la Educación (ICFES)**.
- El certificado oficial adjunto (`assets/EK201532097061.pdf`) corresponde al registro público **`EK201532097061`** presentado el 22 de noviembre de 2015.
- La divulgación y modernización de este contenido se realiza con fines estrictamente académicos, de transparencia pedagógica y reproducibilidad estadística, en concordancia con la legislación colombiana de protección de datos personales (Ley 1581 de 2012).

---

**Última actualización de modernización:** Noviembre 2026  
**Rama de desarrollo y despliegue:** `feat/modernization-ghpages`  
**Estado de aceptación:** ✅ Aprobado para integración y despliegue final (Milestones 1–5 completados)
