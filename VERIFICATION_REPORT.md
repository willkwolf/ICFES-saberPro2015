# Informe Independiente de Verificación Estadística y Trazabilidad
## Independent Statistical Verification & Data Traceability Report

> **Marco Institucional y Metodológico**: Este informe constituye la auditoría estadística formal e independiente de los resultados de las pruebas de Estado **ICFES Saber Pro 2015** para el registro oficial **EK201532097061**. Aplica las directrices de verificación matemática, trazabilidad de fuentes primarias, soberanía de datos y protección estricta de privacidad (PII).

---

## 1. Metadatos de la Ejecución y Entorno de Verificación

- **Fecha y Hora de Auditoría (UTC)**: `2026-11-22T05:08:51.826997+00:00`
- **Veredicto Global**: **`PASS`** (8 de 8 reglas satisfechas)
- **Candidato Evaluado**: `ARTUNDUAGA VIANA WILLIAM CAMILO`
- **Código de Registro ICFES**: `EK201532097061`
- **Institución de Educación Superior**: `UNIVERSIDAD ICESI`
- **Programa Académico**: `INGENIERIA INDUSTRIAL`
- **Grupo de Referencia**: `INGENIERÍA`
- **Municipio y Fecha del Examen**: `CALI - 2015-11-22`
- **Fuentes Primarias Auditadas**:
  - Certificado binario oficial: `assets/EK201532097061.pdf` (FlateDecode streams 0, 1, 2)
  - Dataset canónico estructurado: `data/saber_pro_2015.json`
  - Presentación estática web: `docs/index.html`

---

## 2. Matriz Resumen de Reglas de Verificación (PROJECT.md)

| Código de Regla | Nombre de Regla | Criterio de Aceptación | Estado | Resultado Cuantitativo / Resumen |
| :--- | :--- | :--- | :---: | :--- |
| `RULE-01-SOURCE-PARITY` | **Paridad de Fuente Primaria** | Exactitud 100% contra streams descomprimidos del PDF | ✅ **PASS** | Exact 100% bitstream parity confirmed across all 8 modules (scores, levels, quintiles, Ns, means, SDs) and metadata between PDF and JSON. |
| `RULE-02-CARD-ARITHMETIC` | **Aritmética de Tarjeta KPI** | Recomputación de media (11.0875) y auditoría de anomalía A-01 | ✅ **PASS** | Arithmetic mean recomputed: sum=88.7000, mean=11.0875 (rounds to 11.1). Historical anomaly A-01 audited: published legacy KPI card (11.2) formally reconciled against canonical mathematical value (11.0875). |
| `RULE-03-SUBGROUP-MEANS` | **Medias de Subgrupos Modulares** | Media genérica (10.9200) y media específica (11.3667) | ✅ **PASS** | Subgroup means verified: Generic competencies sum=54.6, mean=10.9200 (54.6/5=10.9200); Specific engineering competencies sum=34.1, mean=11.3667 (34.1/3=11.3667). Mean of sub-averages=11.1433. |
| `RULE-04-PROPORTION-CHECKS` | **Chequeo de Proporciones** | Quintiles altos Q4/Q5 (6/8) y módulos sobre media nacional (7/8) | ✅ **PASS** | Proportions verified: High quintiles (Q4/Q5) = 6/8 (75.0%); Above national mean = 7/8 (87.5%, only Comunicación Escrita below); Above reference group mean = 7/8 (87.5%). |
| `RULE-05-TABLE-CHART-PARITY` | **Paridad Tabla - Gráfico** | Cero deriva entre tablas HTML, arrays Chart.js y JSON | ✅ **PASS** | Zero-drift parity confirmed between data tables, Chart.js visual arrays, and canonical JSON across all 8 modules (8 table rows, 3 Chart datasets: scores, ref means, nac means). |
| `RULE-06-POPULATION-BOUNDS` | **Límites Poblacionales** | N_ref <= N_nac y documentación de divergencia TyT Inglés | ✅ **PASS** | Population bounds strictly satisfied (N_ref <= N_nac) across all 8 modules. English national sample divergence (N_nac=310,468 vs standard undergraduate cohort N=216,501, +93,967 students) audited and formally documented as historical anomaly A-04 (joint administration with Saber TyT technical cohort). |
| `RULE-07-HYGIENE-PII-GUARD` | **Guarda de Privacidad PII** | 0 apariciones de Cédula de Ciudadanía en archivos de texto | ✅ **PASS** | Repository hygiene verified: Scanned 43 text files across root, docs/, data/, assets/, and scripts/. Zero occurrences of Colombian National ID detected. PII redaction strictly enforced; candidate registration EK201532097061 preserved as public reference. |
| `RULE-08-LINK-INTEGRITY` | **Integridad de Enlaces** | 0 enlaces rotos o dominios de plantilla (TU_USUARIO) | ✅ **PASS** | Link integrity verified: 36 references validated across 7 documents. 100% of internal links resolve to valid disk assets. Zero broken links and zero placeholder domains detected. |

---

## 3. Desglose Técnico Detallado por Regla

### RULE-01: Paridad de Fuente Primaria (`RULE-01-SOURCE-PARITY`)
Se descompiló el flujo binario número 2 del certificado oficial `assets/EK201532097061.pdf` utilizando algoritmos de descompresión `zlib` / `FlateDecode` en Python puro. Se confrontaron los valores extraídos contra el archivo canónico `data/saber_pro_2015.json`:

| Módulo Oficial ICFES | Tipo | Puntaje Indiv. | Nivel | Quintil | $N_{ref}$ | $\mu_{ref}$ | $\sigma_{ref}$ | $N_{nac}$ | $\mu_{nac}$ | $\sigma_{nac}$ | Paridad |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Comunicación Escrita** | generic | `9.2` | `3` | `I` | 43,932 | 10.0 | 1.0 | 215,703 | 10.0 | 1.0 | ✅ 100% |
| **Razonamiento Cuantitativo** | generic | `11.5` | `3` | `IV` | 44,063 | 10.8 | 1.2 | 216,501 | 10.1 | 1.2 | ✅ 100% |
| **Lectura Crítica** | generic | `11.6` | `3` | `V` | 44,063 | 10.6 | 1.0 | 216,501 | 10.5 | 1.0 | ✅ 100% |
| **Competencias Ciudadanas** | generic | `10.6` | `N/D` | `IV` | 44,063 | 10.2 | 1.0 | 216,501 | 10.1 | 1.0 | ✅ 100% |
| **Inglés** | generic | `11.7` | `B1` | `IV` | 44,063 | 10.7 | 1.5 | 310,468 | 10.2 | 1.3 | ✅ 100% |
| **Formulación de Proyectos de Ingeniería** | specific | `10.1` | `N/D` | `III` | 44,006 | 10.0 | 1.0 | 44,019 | 10.0 | 1.0 | ✅ 100% |
| **Pensamiento Científico - Matemáticas y Estadística** | specific | `12.9` | `N/D` | `V` | 22,028 | 10.0 | 1.1 | 22,375 | 10.1 | 1.1 | ✅ 100% |
| **Diseño de Sistemas Productivos y Logísticos** | specific | `11.1` | `N/D` | `V` | 10,849 | 10.0 | 1.0 | 10,849 | 10.0 | 1.0 | ✅ 100% |

### RULE-02: Aritmética de Tarjeta y Discrepancia Histórica A-01 (`RULE-02-CARD-ARITHMETIC`)
La sumatoria exacta de los 8 puntajes individuales certificados es:
$$\sum_{i=1}^{8} X_i = 9.2 + 11.5 + 11.6 + 10.6 + 11.7 + 10.1 + 12.9 + 11.1 = 88.7000$$
$$\bar{X}_{global} = \frac{88.7000}{8} = 11.0875$$
- **Valor matemático exacto**: `11.0875`
- **Redondeo estándar a 1 decimal**: `11.1`
- **Redondeo estándar a 2 decimales**: `11.09`
- **Valor histórico publicado en la tarjeta heredada (`docs/index.html` l.381)**: `11.2`
- **Dictamen institucional de auditoría (A-01)**: La cifra `11.2` exhibida en el sitio original corresponde a un sesgo de transcripción o redondeo intermedio manual. La arquitectura modernizada registra formalmente la discrepancia como incidencia verificable A-01 y preserva el valor canónico exacto `11.0875`.

### RULE-03: Medias Modulares por Subgrupo (`RULE-03-SUBGROUP-MEANS`)
Se evaluaron por separado las competencias genéricas obligatorias y las competencias específicas de Ingeniería:
- **Competencias Genéricas (5 módulos)**:
  $$\bar{X}_{gen} = \frac{9.2 + 11.5 + 11.6 + 10.6 + 11.7}{5} = \frac{54.6000}{5} = \mathbf{10.9200}$$
- **Competencias Específicas (3 módulos)**:
  $$\bar{X}_{esp} = \frac{10.1 + 12.9 + 11.1}{3} = \frac{34.1000}{3} = \mathbf{11.3667}$$
- **Promedio de los dos sub-promedios**: $\frac{10.9200 + 11.3667}{2} = 11.1433$ (redondea a 11.1).

### RULE-04: Proporciones de Rendimiento y Benchmarks (`RULE-04-PROPORTION-CHECKS`)
- **Módulos en Quintiles Superiores (Q4 o Q5)**: **`6/8`** (75.0%). Módulos: Razonamiento Cuantitativo (Q4), Lectura Crítica (Q5), Competencias Ciudadanas (Q4), Inglés (Q4), Pensamiento Científico (Q5), Diseño de Sistemas (Q5).
- **Módulos Superiores a la Media Nacional**: **`7/8`** (87.5%). Solo Comunicación Escrita ($9.2 < 10.0$) se sitúa por debajo.
- **Módulos Superiores a la Media del Grupo de Referencia (Ingeniería)**: **`7/8`** (87.5%).

### RULE-05: Paridad Visual y Tabular (`RULE-05-TABLE-CHART-PARITY`)
Se inspeccionaron las etiquetas HTML y las estructuras de arrays en `docs/index.html`:
- Filas de tablas genéricas y específicas: 8 filas confrontadas contra JSON.
- Arrays en configuración Chart.js (`Puntaje Individual`, `Promedio Grupo Referencia`, `Promedio Nacional`): Cero discrepancias cuantitativas detectadas.

### RULE-06: Límites Poblacionales y Cohorte de Inglés (`RULE-06-POPULATION-BOUNDS`)
- La condición $N_{ref} \le N_{nac}$ se cumple estrictamente en los 8 módulos.
- **Divergencia de Inglés (A-04)**: El módulo de Inglés reporta $N_{nac} = 310,468$, superando en 93,967 estudiantes al censo universitario estándar ($N = 216,501$). Esta diferencia responde a la administración conjunta de la prueba de Inglés a estudiantes de nivel tecnológico y técnico (Saber TyT).

### RULE-07: Salvaguarda de Datos Personales Sensibles (`RULE-07-HYGIENE-PII-GUARD`)
- Se ejecutó un rastreo recursivo en el repositorio excluyendo metadatos Git y el PDF binario original.
- **Resultado**: 0 apariciones del número de documento nacional de identidad en archivos de texto públicos.

### RULE-08: Integridad Referencial de Enlaces y Recursos (`RULE-08-LINK-INTEGRITY`)
- Se verificaron todos los hipervínculos internos relativos en archivos Markdown y HTML.
- **Resultado**: 100% de los archivos destino existen en el disco local; sin enlaces rotos ni dominios plantilla (`TU_USUARIO`).

---

## 4. Registro Oficial de Discrepancias e Incidencias Históricas Auditadas

| ID | Categoría | Valor Publicado Histórico | Valor Verificado Canónico | Explicación Técnica y Dictamen |
| :---: | :--- | :--- | :--- | :--- |
| **`A-01`** | Auditoría Estadística | `11.2` | `11.0875` | Arithmetic mean typo: exact 11.0875 (11.1) vs published legacy 11.2 |
| **`A-02`** | Auditoría Estadística | `1.0` | `Empirical standard deviations range from 1.0 to 1.5 across modules (e.g., Razonamiento Cuantitativo: 1.2, Inglés: 1.5/1.3, Pensamiento Científico: 1.1)` | Omission of empirical standard deviations in web tables and false claim that sigma=1.0 globally |
| **`A-03`** | Auditoría Estadística | `I` | `Empirical cohort distribution places score 9.2 in Quintil I (bottom 20%), whereas continuous Gaussian Phi(-0.8)=21.2% would theoretically lie in Q2` | Empirical quintile I vs Gaussian normal percentile (21.2% / Q2) in Comunicación Escrita due to discrete rubric scoring and empirical ECDF |
| **`A-04`** | Auditoría Estadística | `216501` | `310468` | National sample size divergence for English module (N=310,468 vs N=216,501) due to joint administration with Saber TyT cohorts |
| **`A-05`** | Auditoría Estadística | `None` | `Levels were officially defined only for Comunicación Escrita (3), Razonamiento Cuantitativo (3), Lectura Crítica (3), and Inglés (B1)` | Missing performance levels for Competencias Ciudadanas and all specific engineering modules in 2015 ICFES certification |
| **`A-06`** | Auditoría Estadística | `assets/interpretacion-estadistica.md, assets/metodologia-icfes.md, https://github.com/TU_USUARIO/saber-pro-2015-reflexion` | `assets/interpretacion_estadistica.md, assets/metodologia_icfes.md, https://github.com/willkwolf/ICFES-saberPro2015` | Broken internal links in documentation and HTML (hyphens vs underscores in asset paths, and placeholder repository URL) |
| **`A-07`** | Auditoría Estadística | `[REDACTED_PII]` | `REDACTED across all JSON exports and web presentations; only registration EK201532097061 is retained` | Personally Identifiable Information (Colombian National ID / Cédula de Ciudadanía) present in raw PDF certificate |

---

## 5. Instrucciones para Reproducibilidad Independiente

Para reproducir de forma 100% independiente esta auditoría en cualquier terminal con Python 3:

```bash
# Ejecutar suite de pruebas unitarias del motor de verificación
python -m unittest discover -s scripts

# Ejecutar la herramienta CLI de verificación estadística
python scripts/verify_statistics.py --verbose
```

*Reporte certificado emitido de conformidad con las especificaciones de PROJECT.md para ICFES Saber Pro 2015.*