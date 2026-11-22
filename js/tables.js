/**
 * ICFES Saber Pro 2015 - Accessible Dynamic Tables Module
 * ========================================================
 * Ingests canonical JSON dataset, formats data with i18n, and generates accessible responsive tables.
 */

import i18n from './i18n.js';

/**
 * Maps roman quintile string to CSS badge class
 * @param {string} quintile - 'I', 'II', 'III', 'IV', 'V', 'Q1'..'Q5'
 * @returns {string} class name ('q1'..'q5')
 */
export function getQuintileClass(quintile) {
  if (!quintile) return 'q1';
  const q = String(quintile).toUpperCase().trim();
  if (q === 'I' || q === 'Q1' || q === '1') return 'q1';
  if (q === 'II' || q === 'Q2' || q === '2') return 'q2';
  if (q === 'III' || q === 'Q3' || q === '3') return 'q3';
  if (q === 'IV' || q === 'Q4' || q === '4') return 'q4';
  if (q === 'V' || q === 'Q5' || q === '5') return 'q5';
  return 'q1';
}

/**
 * Formats quintile display text
 * @param {string} quintile
 * @param {string} lang
 * @returns {string}
 */
export function formatQuintileText(quintile, lang = 'es') {
  if (!quintile) return '-';
  const q = String(quintile).toUpperCase().trim();
  if (q.startsWith('Q')) return q;
  return `Q${q === 'I' ? '1' : q === 'II' ? '2' : q === 'III' ? '3' : q === 'IV' ? '4' : '5'}`;
}

/**
 * Builds HTML row for a Generic Competency module
 * @param {object} mod - module object from canonical JSON
 * @param {string} lang - 'es' or 'en'
 * @returns {string} HTML <tr> string
 */
export function createGenericRow(mod, lang = 'es') {
  const modName = lang === 'en' ? (mod.name_en || mod.name_es) : mod.name_es;
  const score = i18n.formatScore ? i18n.formatScore(mod.individual_score, lang) : mod.individual_score.toFixed(1);
  const level = mod.performance_level || '-';
  const qClass = getQuintileClass(mod.official_quintile);
  const qText = formatQuintileText(mod.official_quintile, lang);
  const refMean = i18n.formatScore ? i18n.formatScore(mod.reference_group.mean, lang) : mod.reference_group.mean.toFixed(1);
  const natMean = i18n.formatScore ? i18n.formatScore(mod.national_group.mean, lang) : mod.national_group.mean.toFixed(1);
  const refN = i18n.formatCount ? i18n.formatCount(mod.reference_group.n, lang) : mod.reference_group.n.toLocaleString();
  const natN = i18n.formatCount ? i18n.formatCount(mod.national_group.n, lang) : mod.national_group.n.toLocaleString();

  const delta = Number((mod.individual_score - mod.national_group.mean).toFixed(1));
  const isPositive = delta > 0;
  const deltaFormatted = (isPositive ? '+' : '') + (i18n.formatScore ? i18n.formatScore(delta, lang) : delta.toFixed(1));
  const deltaBadge = isPositive
    ? ` <span class="score-delta positive" title="${lang === 'en' ? 'Above national average' : 'Supera la media nacional'}">${deltaFormatted}</span>`
    : '';

  const levelMarkup = level !== '-' && level !== 'N/A'
    ? `<span class="level-pill ${level.toLowerCase()}">${level}</span>`
    : `<span class="text-muted">-</span>`;

  const labels = {
    mod: lang === 'en' ? 'Module' : 'Módulo',
    score: lang === 'en' ? 'Score' : 'Puntaje',
    level: lang === 'en' ? 'Level' : 'Nivel',
    quintile: lang === 'en' ? 'Quintile' : 'Quintil',
    refMean: lang === 'en' ? 'Ref. Group Mean' : 'Promedio Grupo Ref.',
    natMean: lang === 'en' ? 'National Mean' : 'Promedio Nacional',
    refN: lang === 'en' ? 'Ref. Sample (N)' : 'Muestra Grupo Ref. (N)',
    natN: lang === 'en' ? 'National Sample (N)' : 'Muestra Nacional (N)'
  };

  return `<tr class="table-row-${qClass}">
    <td data-label="${labels.mod}">${modName}</td>
    <td data-label="${labels.score}"><strong>${score}</strong>${deltaBadge}</td>
    <td data-label="${labels.level}">${levelMarkup}</td>
    <td data-label="${labels.quintile}" class="cell-quintil"><span class="quintil-badge ${qClass}">${qText}</span></td>
    <td data-label="${labels.refMean}">${refMean}</td>
    <td data-label="${labels.natMean}">${natMean}</td>
    <td data-label="${labels.refN}">${refN}</td>
    <td data-label="${labels.natN}">${natN}</td>
</tr>`;
}

/**
 * Builds HTML row for a Specific Engineering Competency module
 * @param {object} mod - module object from canonical JSON
 * @param {string} lang - 'es' or 'en'
 * @returns {string} HTML <tr> string
 */
export function createSpecificRow(mod, lang = 'es') {
  const modName = lang === 'en' ? (mod.name_en || mod.name_es) : mod.name_es;
  const score = i18n.formatScore ? i18n.formatScore(mod.individual_score, lang) : mod.individual_score.toFixed(1);
  const qClass = getQuintileClass(mod.official_quintile);
  const qText = formatQuintileText(mod.official_quintile, lang);
  const refMean = i18n.formatScore ? i18n.formatScore(mod.reference_group.mean, lang) : mod.reference_group.mean.toFixed(1);
  const natMean = i18n.formatScore ? i18n.formatScore(mod.national_group.mean, lang) : mod.national_group.mean.toFixed(1);
  const refN = i18n.formatCount ? i18n.formatCount(mod.reference_group.n, lang) : mod.reference_group.n.toLocaleString();
  const natN = i18n.formatCount ? i18n.formatCount(mod.national_group.n, lang) : mod.national_group.n.toLocaleString();

  const delta = Number((mod.individual_score - mod.national_group.mean).toFixed(1));
  const isPositive = delta > 0;
  const deltaFormatted = (isPositive ? '+' : '') + (i18n.formatScore ? i18n.formatScore(delta, lang) : delta.toFixed(1));
  const deltaBadge = isPositive
    ? ` <span class="score-delta positive" title="${lang === 'en' ? 'Above national average' : 'Supera la media nacional'}">${deltaFormatted}</span>`
    : '';

  const labels = {
    mod: lang === 'en' ? 'Module' : 'Módulo',
    score: lang === 'en' ? 'Score' : 'Puntaje',
    quintile: lang === 'en' ? 'Quintile' : 'Quintil',
    refMean: lang === 'en' ? 'Ref. Group Mean' : 'Promedio Grupo Ref.',
    natMean: lang === 'en' ? 'National Mean' : 'Promedio Nacional',
    refN: lang === 'en' ? 'Ref. Sample (N)' : 'Muestra Grupo Ref. (N)',
    natN: lang === 'en' ? 'National Sample (N)' : 'Muestra Nacional (N)'
  };

  return `<tr class="table-row-${qClass}">
    <td data-label="${labels.mod}">${modName}</td>
    <td data-label="${labels.score}"><strong>${score}</strong>${deltaBadge}</td>
    <td data-label="${labels.quintile}" class="cell-quintil"><span class="quintil-badge ${qClass}">${qText}</span></td>
    <td data-label="${labels.refMean}">${refMean}</td>
    <td data-label="${labels.natMean}">${natMean}</td>
    <td data-label="${labels.refN}">${refN}</td>
    <td data-label="${labels.natN}">${natN}</td>
</tr>`;
}

/**
 * Ingests canonical JSON dataset and populates the table DOM elements
 * @param {object} dataset - Canonical JSON dataset
 * @param {string} [lang] - 'es' or 'en'
 */
export function renderTables(dataset, lang = 'es') {
  if (!dataset || !Array.isArray(dataset.modules)) {
    return;
  }

  const genericBody = document.querySelector('#table-generic tbody');
  const specificBody = document.querySelector('#table-specific tbody');

  const genericMods = dataset.modules.filter(m => m.type === 'generic');
  const specificMods = dataset.modules.filter(m => m.type === 'specific');

  if (genericBody) {
    genericBody.innerHTML = genericMods.map(m => createGenericRow(m, lang)).join('\n');
  }

  if (specificBody) {
    specificBody.innerHTML = specificMods.map(m => createSpecificRow(m, lang)).join('\n');
  }
}

export default {
  renderTables,
  createGenericRow,
  createSpecificRow,
  getQuintileClass,
  formatQuintileText
};
