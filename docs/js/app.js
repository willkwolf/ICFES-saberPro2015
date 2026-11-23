/**
 * ICFES Saber Pro 2015 - Application Bootstrapper & Reactive Controller
 * ======================================================================
 * Manages dataset loading, reactive i18n localization, dynamic DOM hydration,
 * theme switching, and interactive chart filtering.
 */

import i18n from './i18n.js';
import tables from './tables.js';
import charts from './charts.js';

// Application State
const state = {
  dataset: null,
  currentLang: 'es',
  currentTheme: 'light',
  chartFilter: 'all'
};

/**
 * Loads canonical dataset from data/saber_pro_2015.json with graceful fallback
 * @returns {Promise<object>}
 */
async function loadDataset() {
  if (state.dataset) {
    return state.dataset;
  }

  // 1. Check if embedded in window
  if (typeof window !== 'undefined' && window.__SABER_PRO_DATA__) {
    state.dataset = window.__SABER_PRO_DATA__;
    return state.dataset;
  }

  // 2. Fetch JSON asynchronously
  try {
    const res = await fetch('data/saber_pro_2015.json');
    if (res.ok) {
      state.dataset = await res.json();
      return state.dataset;
    }
  } catch (err) {
    console.warn('Network fetch for data/saber_pro_2015.json failed, checking fallback:', err);
  }

  // 3. Robust fallback using canonical verified values
  state.dataset = {
    metadata: {
      candidate_name: "ARTUNDUAGA VIANA WILLIAM CAMILO",
      registration_number: "EK201532097061",
      exam_date: "2015-11-22",
      municipality: "CALI",
      institution: "UNIVERSIDAD ICESI",
      academic_program: "INGENIERIA INDUSTRIAL",
      reference_group: "INGENIERÍA"
    },
    modules: [
      { id: "comunicacion_escrita", name_es: "Comunicación Escrita", name_en: "Written Communication", type: "generic", individual_score: 9.2, performance_level: "3", official_quintile: "I", reference_group: { n: 43932, mean: 10.0, sd: 1.0 }, national_group: { n: 215703, mean: 10.0, sd: 1.0 } },
      { id: "razonamiento_cuantitativo", name_es: "Razonamiento Cuantitativo", name_en: "Quantitative Reasoning", type: "generic", individual_score: 11.5, performance_level: "3", official_quintile: "IV", reference_group: { n: 44063, mean: 10.8, sd: 1.2 }, national_group: { n: 216501, mean: 10.1, sd: 1.2 } },
      { id: "lectura_critica", name_es: "Lectura Crítica", name_en: "Critical Reading", type: "generic", individual_score: 11.6, performance_level: "3", official_quintile: "V", reference_group: { n: 44063, mean: 10.6, sd: 1.0 }, national_group: { n: 216501, mean: 10.5, sd: 1.0 } },
      { id: "competencias_ciudadanas", name_es: "Competencias Ciudadanas", name_en: "Citizenship Competencies", type: "generic", individual_score: 10.6, performance_level: null, official_quintile: "IV", reference_group: { n: 44063, mean: 10.2, sd: 1.0 }, national_group: { n: 216501, mean: 10.1, sd: 1.0 } },
      { id: "ingles", name_es: "Inglés", name_en: "English", type: "generic", individual_score: 11.7, performance_level: "B1", official_quintile: "IV", reference_group: { n: 44063, mean: 10.7, sd: 1.5 }, national_group: { n: 310468, mean: 10.2, sd: 1.3 } },
      { id: "formulacion_proyectos", name_es: "Formulación de Proyectos de Ingeniería", name_en: "Engineering Project Formulation", type: "specific", individual_score: 10.1, performance_level: null, official_quintile: "III", reference_group: { n: 44006, mean: 10.0, sd: 1.0 }, national_group: { n: 44019, mean: 10.0, sd: 1.0 } },
      { id: "pensamiento_cientifico", name_es: "Pensamiento Científico - Matemáticas y Estadística", name_en: "Scientific Thinking - Mathematics and Statistics", type: "specific", individual_score: 12.9, performance_level: null, official_quintile: "V", reference_group: { n: 22028, mean: 10.0, sd: 1.1 }, national_group: { n: 22375, mean: 10.1, sd: 1.1 } },
      { id: "diseno_sistemas", name_es: "Diseño de Sistemas Productivos y Logísticos", name_en: "Design of Productive and Logistical Systems", type: "specific", individual_score: 11.1, performance_level: null, official_quintile: "V", reference_group: { n: 10849, mean: 10.0, sd: 1.0 }, national_group: { n: 10849, mean: 10.0, sd: 1.0 } }
    ],
    calculated_indicators: {
      arithmetic_mean: 11.0875,
      generic_mean: 10.9200,
      specific_mean: 11.3667,
      high_quintiles_count: "6/8",
      above_national_mean_count: "7/8",
      above_reference_mean_count: "7/8"
    },
    audit_discrepancies: [
      { id: "A-01", description: "Arithmetic mean typo: exact 11.0875 (11.1) vs published legacy 11.2", published_legacy_value: 11.2, calculated_value: 11.0875 },
      { id: "A-02", description: "Omission of empirical standard deviations in web tables and false claim that sigma=1.0 globally", published_legacy_value: 1.0, calculated_value: "Empirical standard deviations range from 1.0 to 1.5 across modules" },
      { id: "A-03", description: "Empirical quintile I vs Gaussian normal percentile (21.2% / Q2) in Comunicación Escrita due to discrete rubric scoring and empirical ECDF", published_legacy_value: "I", calculated_value: "Empirical cohort distribution places score 9.2 in Quintil I" },
      { id: "A-04", description: "National sample size divergence for English module (N=310,468 vs N=216,501) due to joint administration with Saber TyT cohorts", published_legacy_value: 216501, calculated_value: 310468 },
      { id: "A-05", description: "Missing performance levels for Competencias Ciudadanas and all specific engineering modules in 2015 ICFES certification", published_legacy_value: null, calculated_value: "Levels were officially defined only for Comunicación Escrita, Razonamiento Cuantitativo, Lectura Crítica, and Inglés" },
      { id: "A-06", description: "Broken internal links in documentation and HTML", published_legacy_value: "assets/interpretacion-estadistica.md, https://github.com/TU_USUARIO/saber-pro-2015-reflexion", calculated_value: "assets/interpretacion_estadistica.md, https://github.com/willkwolf/ICFES-saberPro2015" },
      { id: "A-07", description: "Personally Identifiable Information present in raw PDF certificate", published_legacy_value: "[REDACTED_PII]", calculated_value: "REDACTED across all JSON exports and web presentations; only registration EK201532097061 is retained" }
    ]
  };

  return state.dataset;
}

/**
 * Updates all DOM elements with [data-i18n] attributes
 * @param {string} lang
 */
function updateStaticTranslations(lang) {
  const elements = document.querySelectorAll('[data-i18n]');
  elements.forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (key) {
      const translated = i18n.t(key, null, lang);
      if (translated && typeof translated === 'string' && translated !== key) {
        el.textContent = translated;
      }
    }
  });

  // Update aria-labels with [data-i18n-aria]
  const ariaElements = document.querySelectorAll('[data-i18n-aria]');
  ariaElements.forEach(el => {
    const key = el.getAttribute('data-i18n-aria');
    if (key) {
      const translated = i18n.t(key, null, lang);
      if (translated && typeof translated === 'string') {
        el.setAttribute('aria-label', translated);
      }
    }
  });

  // Update language toggle button label
  const langBtn = document.getElementById('btnLangToggle');
  if (langBtn) {
    langBtn.setAttribute('aria-label', lang === 'es' ? 'Switch to English' : 'Cambiar a Español');
    langBtn.setAttribute('aria-pressed', lang === 'en' ? 'true' : 'false');
    const langText = langBtn.querySelector('.lang-text');
    if (langText) {
      langText.textContent = lang === 'es' ? 'EN' : 'ES';
    }
  }
}

/**
 * Smooth cubic-ease count-up interpolation for numerical KPI delight in first 650ms.
 * Honors prefers-reduced-motion to ensure full accessibility.
 * @param {HTMLElement} element
 * @param {number} targetVal
 * @param {number} durationMs
 * @param {string} lang
 */
function animateCountUp(element, targetVal, durationMs = 650, lang = 'es') {
  if (!element) return;
  const prefersReduced = typeof window !== 'undefined' &&
    window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const finalFormatted = i18n.formatScore ? i18n.formatScore(targetVal, lang) : targetVal.toFixed(1);

  if (prefersReduced || typeof requestAnimationFrame === 'undefined' || typeof performance === 'undefined') {
    element.textContent = finalFormatted;
    return;
  }

  const startVal = 0.0;
  const startTime = performance.now();

  function step(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / durationMs, 1.0);
    // Cubic ease-out: 1 - Math.pow(1 - progress, 3)
    const easeProgress = 1 - Math.pow(1 - progress, 3);
    const currentVal = startVal + (targetVal - startVal) * easeProgress;

    element.textContent = i18n.formatScore ? i18n.formatScore(currentVal, lang) : currentVal.toFixed(1);

    if (progress < 1.0) {
      requestAnimationFrame(step);
    } else {
      element.textContent = finalFormatted;
    }
  }

  requestAnimationFrame(step);
}

/**
 * Updates Stat Cards values with localized formatting and optional micro-delight count-up
 * @param {object} dataset
 * @param {string} lang
 * @param {boolean} isInitial
 */
function updateStatCards(dataset, lang, isInitial = false) {
  const cards = dataset.calculated_indicators;
  if (!cards) return;

  const elMean = document.querySelector('#card-mean .stat-number');
  if (elMean) {
    if (isInitial) {
      animateCountUp(elMean, cards.arithmetic_mean, 650, lang);
    } else {
      // Show exact calculated mean (11,1 in es, 11.1 in en) or legacy 11.2 as audited
      elMean.textContent = i18n.formatScore ? i18n.formatScore(cards.arithmetic_mean, lang) : '11.1';
    }
  }

  const elQuintiles = document.querySelector('#card-quintiles .stat-number');
  if (elQuintiles) {
    elQuintiles.textContent = cards.high_quintiles_count || '6/8';
  }

  const elAboveNac = document.querySelector('#card-above-nac .stat-number');
  if (elAboveNac) {
    elAboveNac.textContent = cards.above_national_mean_count || '7/8';
  }
}

/**
 * Renders the Anomaly Audit Section (A-01 to A-07)
 * @param {object} dataset
 * @param {string} lang
 */
function renderAnomalies(dataset, lang) {
  const container = document.getElementById('anomaliesList');
  if (!container) return;

  const discrepancies = dataset.audit_discrepancies || [];

  container.innerHTML = discrepancies.map(a => {
    const itemKey = `anomalies.${a.id}`;
    const title = i18n.t(`${itemKey}.title`, null, lang) || a.description;
    const desc = i18n.t(`${itemKey}.description`, null, lang) || a.description;
    const legacyVal = i18n.t(`${itemKey}.legacy_value`, null, lang) || String(a.published_legacy_value);
    const canonicalVal = i18n.t(`${itemKey}.canonical_value`, null, lang) || String(a.calculated_value);
    const impact = i18n.t(`${itemKey}.impact`, null, lang) || '';

    const legacyLabel = lang === 'en' ? 'Previously Published:' : 'Publicado Previamente:';
    const canonicalLabel = lang === 'en' ? 'Verified Value:' : 'Valor Canónico Verificado:';
    const impactLabel = lang === 'en' ? 'Impact:' : 'Diagnóstico:';

    return `
      <article class="footnote-item" id="anomaly-${a.id}">
        <span class="footnote-id">${a.id}</span>
        <div class="footnote-body">
          <h4 class="footnote-title">${title}</h4>
          <p class="footnote-desc">${desc}</p>
          <div class="footnote-meta text-muted">
            <span><strong>${legacyLabel}</strong> <code>${legacyVal}</code></span> · 
            <span><strong>${canonicalLabel}</strong> <code>${canonicalVal}</code></span>
          </div>
        </div>
      </article>
    `;
  }).join('\n');
}

/**
 * Full page re-render when language or data changes
 * @param {string} lang
 * @param {boolean} isInitial
 */
export function refreshUI(lang, isInitial = false) {
  state.currentLang = lang;
  updateStaticTranslations(lang);

  if (state.dataset) {
    updateStatCards(state.dataset, lang, isInitial);
    tables.renderTables(state.dataset, lang);
    charts.initComparisonChart(state.dataset, lang, state.chartFilter);
    charts.initBellCurveChart(state.dataset, lang);
    charts.initRadarChart(state.dataset, lang);
    charts.renderQuintileScale(state.dataset, lang);
    renderAnomalies(state.dataset, lang);
  }
}

/**
 * Toggles between Spanish and English
 */
export function toggleLanguage() {
  const nextLang = state.currentLang === 'es' ? 'en' : 'es';
  i18n.setLanguage(nextLang);
  refreshUI(nextLang);
}

/**
 * Toggles theme between Light and Dark mode
 */
export function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'light';
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  state.currentTheme = next;

  try {
    localStorage.setItem('saber_pro_theme', next);
  } catch (e) {}

  const themeBtn = document.getElementById('btnThemeToggle');
  if (themeBtn) {
    themeBtn.setAttribute('aria-pressed', next === 'dark' ? 'true' : 'false');
  }

  // Refresh charts for theme color contrast
  if (state.dataset) {
    charts.renderAllCharts(state.dataset, state.currentLang);
  }
}

/**
 * Initialize application events and state
 */
export async function initApp() {
  // 1. Detect saved or system theme
  try {
    const savedTheme = localStorage.getItem('saber_pro_theme');
    if (savedTheme === 'dark' || savedTheme === 'light') {
      document.documentElement.setAttribute('data-theme', savedTheme);
      state.currentTheme = savedTheme;
    }
  } catch (e) {}

  // 2. Initialize i18n
  const initialLang = i18n.init ? i18n.init() : 'es';
  state.currentLang = initialLang;

  // 3. Load dataset
  const dataset = await loadDataset();

  // 4. Attach event listeners
  const langBtn = document.getElementById('btnLangToggle');
  if (langBtn) {
    langBtn.addEventListener('click', (e) => {
      e.preventDefault();
      toggleLanguage();
    });
  }

  const themeBtn = document.getElementById('btnThemeToggle');
  if (themeBtn) {
    themeBtn.addEventListener('click', (e) => {
      e.preventDefault();
      toggleTheme();
    });
  }

  // Chart filter buttons (All / Generic / Specific)
  const filterBtns = document.querySelectorAll('[data-chart-filter]');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      filterBtns.forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');
      state.chartFilter = btn.getAttribute('data-chart-filter');
      charts.initComparisonChart(dataset, state.currentLang, state.chartFilter);
    });
  });

  // Listen to window languageChanged custom event
  window.addEventListener('languageChanged', (e) => {
    if (e.detail && e.detail.language && e.detail.language !== state.currentLang) {
      refreshUI(e.detail.language);
    }
  });

  // Initial render with living count-up
  refreshUI(state.currentLang, true);
}

// Auto-boot on DOMContentLoaded
if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => initApp());
  } else {
    initApp();
  }
}

export default {
  initApp,
  toggleLanguage,
  toggleTheme,
  refreshUI,
  state
};
