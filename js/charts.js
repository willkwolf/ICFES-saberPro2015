/**
 * ICFES Saber Pro 2015 - Data Visualization Suite
 * ===============================================
 * Production-ready, accessible Chart.js 4.4.x visualizations:
 * 1. Grouped Bar Comparison Chart (with responsive mobile horizontal layout)
 * 2. Standard Normal Bell Curve (mu=10, sigma=1 with z-scores)
 * 3. Radar Competency Profile (8 dimensions vs reference group)
 * 4. Visual Quintile Scale
 */

import i18n from './i18n.js';

// Chart instances store for clean re-renders
const chartInstances = {
  bar: null,
  bell: null,
  radar: null
};

/**
 * Helper to get active theme colors
 * @returns {object}
 */
function getThemeColors() {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark' ||
    (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches &&
     document.documentElement.getAttribute('data-theme') !== 'light');

  return {
    textColor: isDark ? '#f8fafc' : '#1e293b',
    gridColor: isDark ? 'rgba(51, 65, 85, 0.4)' : 'rgba(226, 232, 240, 0.8)',
    indBg: isDark ? '#818cf8' : '#4338ca',
    indBorder: isDark ? '#6366f1' : '#312e81',
    refBg: isDark ? '#38bdf8' : '#0284c7',
    refBorder: isDark ? '#0ea5e9' : '#0369a1',
    nacBg: isDark ? '#94a3b8' : '#64748b',
    nacBorder: isDark ? '#64748b' : '#334155'
  };
}

/**
 * 1. Grouped Bar Comparison Chart
 * @param {object} dataset - Canonical dataset
 * @param {string} lang - 'es' or 'en'
 * @param {string} filter - 'all', 'generic', or 'specific'
 */
export function initComparisonChart(dataset, lang = 'es', filter = 'all') {
  const canvas = document.getElementById('comparisonChart');
  if (!canvas || typeof Chart === 'undefined') return;

  if (chartInstances.bar) {
    chartInstances.bar.destroy();
    chartInstances.bar = null;
  }

  let modules = dataset.modules || [];
  if (filter === 'generic') {
    modules = modules.filter(m => m.type === 'generic');
  } else if (filter === 'specific') {
    modules = modules.filter(m => m.type === 'specific');
  }

  const isMobile = window.innerWidth < 640;
  const colors = getThemeColors();

  // Multi-line labels for mobile vertical charts or single-line for horizontal
  const labels = modules.map(m => {
    const name = lang === 'en' ? (m.name_en || m.name_es) : m.name_es;
    if (isMobile) {
      // Split words into array for multi-line rendering on mobile
      const words = name.split(' ');
      if (words.length > 2) {
        return [words.slice(0, 2).join(' '), words.slice(2).join(' ')];
      }
      return name;
    }
    return name;
  });

  const individualScores = modules.map(m => m.individual_score);
  const refMeans = modules.map(m => m.reference_group.mean);
  const nacMeans = modules.map(m => m.national_group.mean);

  const labelInd = i18n.t ? i18n.t('charts.legends.individual_score', null, lang) : (lang === 'en' ? 'Individual Score' : 'Puntaje Individual');
  const labelRef = i18n.t ? i18n.t('charts.legends.reference_mean', null, lang) : (lang === 'en' ? 'Reference Group Mean' : 'Promedio Grupo Referencia');
  const labelNac = i18n.t ? i18n.t('charts.legends.national_mean', null, lang) : (lang === 'en' ? 'National Mean' : 'Promedio Nacional');

  const chartData = {
    labels: labels,
    datasets: [
      {
        label: labelInd,
        data: individualScores,
        backgroundColor: colors.indBg,
        borderColor: colors.indBorder,
        borderWidth: 2,
        borderRadius: 4
      },
      {
        label: labelRef,
        data: refMeans,
        backgroundColor: colors.refBg,
        borderColor: colors.refBorder,
        borderWidth: 2,
        borderRadius: 4
      },
      {
        label: labelNac,
        data: nacMeans,
        backgroundColor: colors.nacBg,
        borderColor: colors.nacBorder,
        borderWidth: 2,
        borderRadius: 4
      }
    ]
  };

  chartInstances.bar = new Chart(canvas, {
    type: 'bar',
    data: chartData,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: {
            color: colors.textColor,
            font: { size: 12, weight: '600' },
            padding: 15,
            usePointStyle: true
          }
        },
        tooltip: {
          backgroundColor: 'rgba(15, 23, 42, 0.9)',
          padding: 10,
          titleFont: { size: 13, weight: 'bold' },
          bodyFont: { size: 12 },
          callbacks: {
            label: function(ctx) {
              const val = ctx.parsed.y !== null && ctx.parsed.y !== undefined ? ctx.parsed.y : ctx.parsed.x;
              const formatted = i18n.formatScore ? i18n.formatScore(val, lang) : val.toFixed(1);
              return `${ctx.dataset.label}: ${formatted}`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { color: colors.gridColor },
          ticks: {
            color: colors.textColor,
            font: { size: isMobile ? 10 : 11 }
          }
        },
        y: {
          min: 8.0,
          max: 14.0,
          grid: { color: colors.gridColor },
          ticks: {
            color: colors.textColor,
            stepSize: 1.0,
            callback: function(v) {
              return i18n.formatScore ? i18n.formatScore(v, lang) : v.toFixed(1);
            }
          }
        }
      }
    }
  });
}

/**
 * 2. Standard Normal Bell Curve (\mu=10, \sigma=1)
 * @param {object} dataset - Canonical dataset
 * @param {string} lang - 'es' or 'en'
 */
export function initBellCurveChart(dataset, lang = 'es') {
  const canvas = document.getElementById('bellCurveChart');
  if (!canvas || typeof Chart === 'undefined') return;

  if (chartInstances.bell) {
    chartInstances.bell.destroy();
    chartInstances.bell = null;
  }

  const colors = getThemeColors();

  // Generate Normal distribution curve (\mu=10, \sigma=1) from 6.0 to 14.0
  const points = [];
  for (let x = 6.0; x <= 14.001; x += 0.25) {
    const z = x - 10.0;
    const y = (1.0 / Math.sqrt(2 * Math.PI)) * Math.exp(-0.5 * z * z);
    points.push({ x: Number(x.toFixed(2)), y: Number(y.toFixed(4)) });
  }

  // Highlight candidate scores as scatter points on the bell curve
  const modules = dataset.modules || [];
  const candidateScatter = modules.map(m => {
    const score = m.individual_score;
    const z = score - 10.0;
    const y = (1.0 / Math.sqrt(2 * Math.PI)) * Math.exp(-0.5 * z * z);
    const name = lang === 'en' ? (m.name_en || m.name_es) : m.name_es;
    return {
      x: score,
      y: Number(y.toFixed(4)),
      name: name,
      score: score,
      z: z.toFixed(2)
    };
  });

  const curveLabel = lang === 'en' ? 'Normal Curve (μ=10, σ=1)' : 'Curva Normal Teórica (μ=10, σ=1)';
  const candidateLabel = lang === 'en' ? 'Candidate Modular Scores' : 'Puntajes Individuales Examinado';

  chartInstances.bell = new Chart(canvas, {
    type: 'line',
    data: {
      datasets: [
        {
          label: curveLabel,
          data: points,
          borderColor: colors.refBg,
          backgroundColor: 'rgba(2, 132, 199, 0.12)',
          fill: true,
          tension: 0.4,
          pointRadius: 0,
          borderWidth: 2
        },
        {
          label: candidateLabel,
          data: candidateScatter,
          type: 'scatter',
          backgroundColor: colors.indBg,
          borderColor: '#ffffff',
          borderWidth: 2,
          pointRadius: 6,
          pointHoverRadius: 9
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: {
            color: colors.textColor,
            font: { size: 12, weight: '600' },
            usePointStyle: true
          }
        },
        tooltip: {
          backgroundColor: 'rgba(15, 23, 42, 0.9)',
          padding: 10,
          callbacks: {
            label: function(ctx) {
              const raw = ctx.raw;
              if (raw && raw.name) {
                const sFormatted = i18n.formatScore ? i18n.formatScore(raw.score, lang) : raw.score.toFixed(1);
                return `${raw.name}: ${sFormatted} (z = ${raw.z > 0 ? '+' : ''}${raw.z}σ)`;
              }
              const xVal = i18n.formatScore ? i18n.formatScore(raw.x, lang) : raw.x.toFixed(1);
              return `x = ${xVal}, f(x) = ${raw.y}`;
            }
          }
        }
      },
      scales: {
        x: {
          type: 'linear',
          min: 6.0,
          max: 14.0,
          grid: { color: colors.gridColor },
          ticks: {
            stepSize: 1.0,
            color: colors.textColor,
            callback: function(v) {
              const z = v - 10;
              const sign = z > 0 ? '+' : '';
              return `${v} (${sign}${z}σ)`;
            }
          }
        },
        y: {
          min: 0,
          max: 0.45,
          grid: { color: colors.gridColor },
          ticks: {
            color: colors.textColor,
            stepSize: 0.1
          }
        }
      }
    }
  });
}

/**
 * 3. Radar Competency Profile (8 dimensions)
 * @param {object} dataset - Canonical dataset
 * @param {string} lang - 'es' or 'en'
 */
export function initRadarChart(dataset, lang = 'es') {
  const canvas = document.getElementById('radarChart');
  if (!canvas || typeof Chart === 'undefined') return;

  if (chartInstances.radar) {
    chartInstances.radar.destroy();
    chartInstances.radar = null;
  }

  const colors = getThemeColors();
  const modules = dataset.modules || [];

  const labels = modules.map(m => {
    const name = lang === 'en' ? (m.name_en || m.name_es) : m.name_es;
    const words = name.split(' ');
    if (words.length > 2) {
      return [words.slice(0, 2).join(' '), words.slice(2).join(' ')];
    }
    return name;
  });

  const indScores = modules.map(m => m.individual_score);
  const refScores = modules.map(m => m.reference_group.mean);

  const labelInd = i18n.t ? i18n.t('charts.legends.individual_score', null, lang) : (lang === 'en' ? 'Individual Score' : 'Puntaje Individual');
  const labelRef = i18n.t ? i18n.t('charts.legends.reference_mean', null, lang) : (lang === 'en' ? 'Reference Group Mean' : 'Promedio Grupo Referencia');

  chartInstances.radar = new Chart(canvas, {
    type: 'radar',
    data: {
      labels: labels,
      datasets: [
        {
          label: labelInd,
          data: indScores,
          backgroundColor: 'rgba(67, 56, 202, 0.25)',
          borderColor: colors.indBg,
          borderWidth: 2,
          pointBackgroundColor: colors.indBg,
          pointBorderColor: '#ffffff',
          pointRadius: 4
        },
        {
          label: labelRef,
          data: refScores,
          backgroundColor: 'rgba(2, 132, 199, 0.2)',
          borderColor: colors.refBg,
          borderWidth: 2,
          pointBackgroundColor: colors.refBg,
          pointBorderColor: '#ffffff',
          pointRadius: 4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: {
            color: colors.textColor,
            font: { size: 12, weight: '600' }
          }
        },
        tooltip: {
          callbacks: {
            label: function(ctx) {
              const val = ctx.parsed.r;
              const formatted = i18n.formatScore ? i18n.formatScore(val, lang) : val.toFixed(1);
              return `${ctx.dataset.label}: ${formatted}`;
            }
          }
        }
      },
      scales: {
        r: {
          min: 8.0,
          max: 13.5,
          ticks: {
            stepSize: 1.0,
            color: colors.textColor,
            backdropColor: 'transparent'
          },
          grid: { color: colors.gridColor },
          angleLines: { color: colors.gridColor },
          pointLabels: {
            color: colors.textColor,
            font: { size: 11, weight: '600' }
          }
        }
      }
    }
  });
}

/**
 * 4. Render Interactive Visual Quintile Scale
 * @param {object} dataset - Canonical dataset
 * @param {string} lang - 'es' or 'en'
 */
export function renderQuintileScale(dataset, lang = 'es') {
  const container = document.getElementById('quintileScaleDisplay');
  if (!container) return;

  const modules = dataset.modules || [];
  const qCounts = { Q1: 0, Q2: 0, Q3: 0, Q4: 0, Q5: 0 };
  const qModules = { Q1: [], Q2: [], Q3: [], Q4: [], Q5: [] };

  modules.forEach(m => {
    const qKey = `Q${m.official_quintile === 'I' ? '1' : m.official_quintile === 'II' ? '2' : m.official_quintile === 'III' ? '3' : m.official_quintile === 'IV' ? '4' : '5'}`;
    if (qCounts[qKey] !== undefined) {
      qCounts[qKey]++;
      const name = lang === 'en' ? (m.name_en || m.name_es) : m.name_es;
      qModules[qKey].push(`${name} (${m.individual_score})`);
    }
  });

  const labels = {
    q1: lang === 'en' ? 'Q1 (0-20%)' : 'Q1 (0-20%)',
    q2: lang === 'en' ? 'Q2 (21-40%)' : 'Q2 (21-40%)',
    q3: lang === 'en' ? 'Q3 (41-60%)' : 'Q3 (41-60%)',
    q4: lang === 'en' ? 'Q4 (61-80%)' : 'Q4 (61-80%)',
    q5: lang === 'en' ? 'Q5 (81-100%)' : 'Q5 (81-100%)',
    modsLabel: lang === 'en' ? 'Modules' : 'Módulos'
  };

  container.innerHTML = `
    <div class="quintile-scale-container" role="region" aria-label="${lang === 'en' ? 'Quintile Distribution' : 'Distribución por Quintiles'}">
      <div class="quintile-scale-bar">
        <div class="scale-segment q1" style="flex: 1;" title="${qModules.Q1.join(', ') || '0'}">Q1 (${qCounts.Q1})</div>
        <div class="scale-segment q2" style="flex: 1;" title="${qModules.Q2.join(', ') || '0'}">Q2 (${qCounts.Q2})</div>
        <div class="scale-segment q3" style="flex: 1;" title="${qModules.Q3.join(', ') || '0'}">Q3 (${qCounts.Q3})</div>
        <div class="scale-segment q4" style="flex: 1;" title="${qModules.Q4.join(', ') || '0'}">Q4 (${qCounts.Q4})</div>
        <div class="scale-segment q5" style="flex: 1;" title="${qModules.Q5.join(', ') || '0'}">Q5 (${qCounts.Q5})</div>
      </div>
      <div class="scale-markers">
        <span>${labels.q1}: ${qCounts.Q1} ${labels.modsLabel}</span>
        <span>${labels.q3}: ${qCounts.Q3} ${labels.modsLabel}</span>
        <span>${labels.q4}/${labels.q5}: ${qCounts.Q4 + qCounts.Q5} ${labels.modsLabel} (75%)</span>
      </div>
    </div>
  `;
}

/**
 * Initializes or re-renders all charts with active language and dataset
 * @param {object} dataset
 * @param {string} lang
 */
export function renderAllCharts(dataset, lang = 'es') {
  initComparisonChart(dataset, lang);
  initBellCurveChart(dataset, lang);
  initRadarChart(dataset, lang);
  renderQuintileScale(dataset, lang);
}

export default {
  initComparisonChart,
  initBellCurveChart,
  initRadarChart,
  renderQuintileScale,
  renderAllCharts
};
