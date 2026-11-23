/**
 * ICFES Saber Pro 2015 - Internationalization (i18n) Engine
 * =========================================================
 * Production-grade, decoupled bilingual localization engine using native Web APIs:
 * - Intl.NumberFormat for locale-accurate decimal and thousand formatting
 * - Intl.DateTimeFormat for locale-accurate date rendering
 * - Nested translation key resolution with variable interpolation
 * - Reactive language switching with document.documentElement.lang sync and CustomEvent dispatch
 * - Universal compatibility: ES Module, Browser Global (window.i18n), and Node.js
 */

import esDefault from '../locales/es.js';
import enDefault from '../locales/en.js';

// Internal state
const state = {
  currentLang: 'es',
  fallbackLang: 'es',
  locales: {
    es: esDefault,
    en: enDefault
  }
};

/**
 * Normalizes locale code for Intl APIs ('es' -> 'es-CO', 'en' -> 'en-US')
 * @param {string} lang
 * @returns {string}
 */
function getIntlLocale(lang) {
  const normalized = (lang || state.currentLang).toLowerCase();
  if (normalized.startsWith('es')) {
    return 'es-CO';
  }
  return 'en-US';
}

/**
 * Returns the currently active language ('es' or 'en')
 * @returns {string}
 */
export function getLanguage() {
  return state.currentLang;
}

/**
 * Sets the active language, updates <html lang="...">, persists to localStorage,
 * and dispatches a 'languageChanged' custom event.
 * @param {string} lang - 'es' or 'en'
 * @returns {string} active language
 */
export function setLanguage(lang) {
  const target = (lang && typeof lang === 'string') ? lang.toLowerCase().trim() : 'es';
  const validated = (target === 'en' || target.startsWith('en')) ? 'en' : 'es';

  state.currentLang = validated;

  // Synchronize HTML root element
  if (typeof document !== 'undefined' && document.documentElement) {
    document.documentElement.setAttribute('lang', validated);
  }

  // Persist preference to localStorage
  try {
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('saber_pro_lang', validated);
    }
  } catch (e) {
    // Graceful degradation when localStorage is restricted
  }

  // Dispatch custom event for reactive UI re-renders
  if (typeof window !== 'undefined' && typeof window.dispatchEvent === 'function') {
    try {
      const event = new CustomEvent('languageChanged', {
        detail: { language: validated }
      });
      window.dispatchEvent(event);
    } catch (e) {
      // Fallback for older event models
      if (typeof document !== 'undefined' && document.dispatchEvent) {
        const ev = document.createEvent('CustomEvent');
        ev.initCustomEvent('languageChanged', true, true, { language: validated });
        document.dispatchEvent(ev);
      }
    }
  }

  return validated;
}

/**
 * Registers or updates a locale dictionary
 * @param {string} lang - 'es' or 'en'
 * @param {object} dictionary
 */
export function registerLocale(lang, dictionary) {
  if (lang && dictionary && typeof dictionary === 'object') {
    state.locales[lang] = {
      ...(state.locales[lang] || {}),
      ...dictionary
    };
  }
}

/**
 * Returns current dictionary object for active or specified language
 * @param {string} [lang]
 * @returns {object}
 */
export function getCurrentLocale(lang) {
  const target = lang || state.currentLang;
  return state.locales[target] || state.locales[state.fallbackLang] || {};
}

/**
 * Resolves a nested key in an object (e.g. 'stats.arithmetic_mean.title')
 * @param {object} obj
 * @param {string} path
 * @returns {*}
 */
function resolvePath(obj, path) {
  if (!obj || typeof obj !== 'object' || !path) {
    return undefined;
  }
  const parts = path.split('.');
  let current = obj;
  for (let i = 0; i < parts.length; i++) {
    if (current === null || current === undefined || typeof current !== 'object') {
      return undefined;
    }
    current = current[parts[i]];
  }
  return current;
}

/**
 * Interpolates parameters into string template ({param} or {{param}})
 * @param {string} template
 * @param {object} params
 * @returns {string}
 */
function interpolate(template, params) {
  if (typeof template !== 'string' || !params || typeof params !== 'object') {
    return template;
  }
  return template.replace(/\{{1,2}\s*([\w\.\-]+)\s*\}{1,2}/g, (match, key) => {
    return Object.prototype.hasOwnProperty.call(params, key) ? String(params[key]) : match;
  });
}

/**
 * Main translation function with nested key resolution, placeholder interpolation, and fallback.
 * @param {string} key - Dot-separated key path (e.g. 'stats.arithmetic_mean.title')
 * @param {object} [params] - Key-value parameters for placeholder interpolation
 * @param {string} [lang] - Optional locale override ('es' or 'en')
 * @returns {string|*} Translated string or resolved object
 */
export function t(key, params = null, lang = null) {
  if (!key || typeof key !== 'string') {
    return '';
  }

  const activeLang = lang || state.currentLang;
  const currentDict = state.locales[activeLang] || {};
  let value = resolvePath(currentDict, key);

  // Fallback to secondary language if missing in primary
  if (value === undefined) {
    const fallback = activeLang === 'es' ? 'en' : 'es';
    const fallbackDict = state.locales[fallback] || {};
    value = resolvePath(fallbackDict, key);
  }

  // Fallback to key itself if not found anywhere
  if (value === undefined) {
    return key;
  }

  // If it's a string, interpolate parameters
  if (typeof value === 'string' && params && typeof params === 'object') {
    return interpolate(value, params);
  }

  return value;
}

/**
 * Formats a decimal score using native Intl.NumberFormat:
 * - es: '11,1' (minimumFractionDigits: 1, maximumFractionDigits: 1, es-CO)
 * - en: '11.1' (minimumFractionDigits: 1, maximumFractionDigits: 1, en-US)
 * @param {number|string} value - Numerical score
 * @param {string} [lang] - 'es' or 'en' (defaults to active language)
 * @param {object} [customOptions] - Optional override options for Intl.NumberFormat
 * @returns {string} Formatted score string
 */
export function formatScore(value, lang = null, customOptions = null) {
  if (value === null || value === undefined || value === '') {
    return '-';
  }
  const num = Number(value);
  if (Number.isNaN(num)) {
    return String(value);
  }

  const locale = getIntlLocale(lang);
  const options = {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
    ...(customOptions || {})
  };

  return new Intl.NumberFormat(locale, options).format(num);
}

/**
 * Formats an integer count/population using native Intl.NumberFormat:
 * - es: '43.932' (thousands separator '.', es-CO)
 * - en: '43,932' (thousands separator ',', en-US)
 * @param {number|string} value - Count or population size
 * @param {string} [lang] - 'es' or 'en' (defaults to active language)
 * @param {object} [customOptions] - Optional override options for Intl.NumberFormat
 * @returns {string} Formatted count string
 */
export function formatCount(value, lang = null, customOptions = null) {
  if (value === null || value === undefined || value === '') {
    return '-';
  }
  const num = Number(value);
  if (Number.isNaN(num)) {
    return String(value);
  }

  const locale = getIntlLocale(lang);
  const options = {
    maximumFractionDigits: 0,
    ...(customOptions || {})
  };

  return new Intl.NumberFormat(locale, options).format(num);
}

/**
 * Formats a date string using native Intl.DateTimeFormat
 * @param {string|Date} dateVal - Date string (e.g. '2015-11-22') or Date instance
 * @param {string} [lang] - 'es' or 'en' (defaults to active language)
 * @param {object} [customOptions] - Optional override options for Intl.DateTimeFormat
 * @returns {string} Formatted date string
 */
export function formatDate(dateVal, lang = null, customOptions = null) {
  if (!dateVal) {
    return '';
  }

  let d;
  if (dateVal instanceof Date) {
    d = dateVal;
  } else if (typeof dateVal === 'string') {
    // Avoid local timezone shift for YYYY-MM-DD
    if (/^\d{4}-\d{2}-\d{2}$/.test(dateVal)) {
      const parts = dateVal.split('-').map(Number);
      d = new Date(Date.UTC(parts[0], parts[1] - 1, parts[2]));
    } else {
      d = new Date(dateVal);
    }
  } else {
    d = new Date(dateVal);
  }

  if (Number.isNaN(d.getTime())) {
    return String(dateVal);
  }

  const locale = getIntlLocale(lang);
  const options = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    timeZone: 'UTC',
    ...(customOptions || {})
  };

  return new Intl.DateTimeFormat(locale, options).format(d);
}

/**
 * Initializes the i18n engine with auto-detection and environment setup
 * @param {object} [options]
 * @returns {string} active language
 */
export function init(options = {}) {
  // Check for pre-registered window.locales
  if (typeof window !== 'undefined' && window.locales) {
    if (window.locales.es) registerLocale('es', window.locales.es);
    if (window.locales.en) registerLocale('en', window.locales.en);
  } else if (typeof globalThis !== 'undefined' && globalThis.locales) {
    if (globalThis.locales.es) registerLocale('es', globalThis.locales.es);
    if (globalThis.locales.en) registerLocale('en', globalThis.locales.en);
  }

  if (options.locales) {
    if (options.locales.es) registerLocale('es', options.locales.es);
    if (options.locales.en) registerLocale('en', options.locales.en);
  }

  let detectedLang = options.defaultLang || 'es';

  // 1. Browser language auto-detection: if user has English, switch to English
  if (typeof navigator !== 'undefined') {
    const navLangs = navigator.languages || [navigator.language || navigator.userLanguage || ''];
    for (const l of navLangs) {
      if (l && typeof l === 'string') {
        const clean = l.toLowerCase().trim();
        if (clean.startsWith('en')) {
          detectedLang = 'en';
          break;
        }
        if (clean.startsWith('es')) {
          detectedLang = 'es';
          break;
        }
      }
    }
  }

  // 2. Try localStorage (if explicitly set by user via manual toggle)
  try {
    if (typeof localStorage !== 'undefined') {
      const stored = localStorage.getItem('saber_pro_lang');
      if (stored === 'es' || stored === 'en') {
        detectedLang = stored;
      }
    }
  } catch (e) {
    // Ignore restricted localStorage
  }

  // 3. Set language
  setLanguage(detectedLang);
  return detectedLang;
}

// Auto-initialize when executing in browser environment
if (typeof window !== 'undefined' || typeof document !== 'undefined') {
  init();
}

// Build consolidated API object
const i18n = {
  t,
  formatScore,
  formatCount,
  formatDate,
  setLanguage,
  getLanguage,
  registerLocale,
  getCurrentLocale,
  init,
  locales: state.locales
};

// Global browser window attachment
if (typeof window !== 'undefined') {
  window.i18n = i18n;
}

// GlobalThis attachment for universal runtimes
if (typeof globalThis !== 'undefined') {
  globalThis.i18n = i18n;
}

// CommonJS support
if (typeof module !== 'undefined' && module.exports) {
  module.exports = i18n;
}

export default i18n;
