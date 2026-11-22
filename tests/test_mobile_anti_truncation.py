#!/usr/bin/env python3
"""
Test Suite: Mobile Anti-Truncation, MECE Cards & Responsive Layout Verification
================================================================================
Validates:
1. All 4 KPI Stat Cards follow the MECE framework (magnitude, peer, nation, peak).
2. Zero unrendered or missing i18n keys across all [data-i18n] DOM elements in es and en.
3. Zero literal dot-syntax keys in rendered DOM (e.g. 'stats.top_performance.title').
4. Mobile anti-truncation CSS guards (min-width: 0, overflow-wrap, word-break).
5. Responsive grid track sizing preventing horizontal overflow on 320px viewports.
6. Mobile media queries for narrow viewports (<= 640px and <= 360px).
7. Parity between root and docs/ deployment trees.
"""

import filecmp
import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def extract_js_object(file_path: Path) -> dict:
    content = file_path.read_text(encoding="utf-8")
    start = content.find("{")
    end = content.find("\n};")
    raw_json = content[start : end + 2].rstrip(";").strip()
    return json.loads(raw_json)


def resolve_path(d: dict, key: str):
    parts = key.split(".")
    cur = d
    for p in parts:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return None
    return cur


class TestMobileAntiTruncationAndMECE(unittest.TestCase):
    """Test suite ensuring mobile readability, zero truncation, and MECE cards."""

    @classmethod
    def setUpClass(cls):
        cls.html_path = REPO_ROOT / "index.html"
        cls.docs_html_path = REPO_ROOT / "docs" / "index.html"
        cls.es_dict = extract_js_object(REPO_ROOT / "locales" / "es.js")
        cls.en_dict = extract_js_object(REPO_ROOT / "locales" / "en.js")
        cls.components_css = (REPO_ROOT / "css" / "components.css").read_text(encoding="utf-8")
        cls.layout_css = (REPO_ROOT / "css" / "layout.css").read_text(encoding="utf-8")
        cls.html_content = cls.html_path.read_text(encoding="utf-8")

    def test_bitstream_parity(self):
        """Verify 100% bitstream parity between index.html and docs/index.html."""
        self.assertTrue(filecmp.cmp(self.html_path, self.docs_html_path, shallow=False))

    def test_all_data_i18n_keys_resolve_in_both_locales(self):
        """Verify that every single data-i18n attribute in index.html resolves in es and en."""
        keys = re.findall(r'data-i18n=["\']([^"\']+)["\']', self.html_content)
        self.assertGreater(len(keys), 50, "Should have over 50 i18n keys in DOM")

        missing_es = []
        missing_en = []
        for k in set(keys):
            v_es = resolve_path(self.es_dict, k)
            v_en = resolve_path(self.en_dict, k)
            if v_es is None or not str(v_es).strip():
                missing_es.append(k)
            if v_en is None or not str(v_en).strip():
                missing_en.append(k)

        self.assertEqual(len(missing_es), 0, f"Unresolved keys in es.js: {missing_es}")
        self.assertEqual(len(missing_en), 0, f"Unresolved keys in en.js: {missing_en}")

    def test_top_performance_keys_specifically_resolved(self):
        """Verify stats.top_performance.title and subtitle are resolved with clear, concise copy."""
        title_es = resolve_path(self.es_dict, "stats.top_performance.title")
        sub_es = resolve_path(self.es_dict, "stats.top_performance.subtitle")
        title_en = resolve_path(self.en_dict, "stats.top_performance.title")
        sub_en = resolve_path(self.en_dict, "stats.top_performance.subtitle")

        self.assertIsNotNone(title_es)
        self.assertIsNotNone(sub_es)
        self.assertIsNotNone(title_en)
        self.assertIsNotNone(sub_en)

        # Ensure no dot-syntax key leakage
        for text in [title_es, sub_es, title_en, sub_en]:
            self.assertNotIn("stats.", text, f"Key path leaked into translation value: {text}")
            self.assertGreater(len(text), 3, "Translation must have meaningful content")

        # Verify semantic content
        self.assertIn("Máximo Desempeño", title_es)
        self.assertIn("Peak Performance", title_en)

    def test_mece_cards_structure(self):
        """Verify that the 4 KPI stat cards embody the MECE framework (no overlap, complete)."""
        card_ids = ["card-mean", "card-quintiles", "card-above-nac", "card-top-performance"]
        for cid in card_ids:
            self.assertIn(f'id="{cid}"', self.html_content, f"Stat card #{cid} missing in HTML")

        # Card 1: Absolute magnitude (Mean)
        mean_match = re.search(r'id="card-mean".*?<div class="stat-number">([\d\.]+)</div>', self.html_content, re.DOTALL)
        self.assertIsNotNone(mean_match)
        self.assertIn(mean_match.group(1), ["11.1", "11.2"])

        # Card 2: Peer reference standing (Quintiles in engineering)
        q_match = re.search(r'id="card-quintiles".*?<div class="stat-number">([^<]+)</div>', self.html_content, re.DOTALL)
        self.assertIsNotNone(q_match)
        self.assertEqual(q_match.group(1).strip(), "6/8")

        # Card 3: National benchmark standing (Surpassing country average)
        nac_match = re.search(r'id="card-above-nac".*?<div class="stat-number">([^<]+)</div>', self.html_content, re.DOTALL)
        self.assertIsNotNone(nac_match)
        self.assertEqual(nac_match.group(1).strip(), "7/8")

        # Card 4: Peak excellence outlier (Top 20% national ceiling)
        top_match = re.search(r'id="card-top-performance".*?<div class="stat-number">([^<]+)</div>', self.html_content, re.DOTALL)
        self.assertIsNotNone(top_match)
        self.assertEqual(top_match.group(1).strip(), "Q5")

    def test_mobile_anti_truncation_css_guards(self):
        """Verify CSS contains defensive rules against text truncation on mobile."""
        # 1. min-width: 0 on stat-card
        self.assertIn("min-width: 0", self.components_css, "Missing 'min-width: 0' guard in components.css")

        # 2. overflow-wrap / word-break on stat-card and hero
        self.assertIn("overflow-wrap: break-word", self.components_css, "Missing 'overflow-wrap: break-word'")
        self.assertIn("word-break: break-word", self.components_css, "Missing 'word-break: break-word'")

        # 3. hero-chip allows wrapping on narrow viewports
        chip_rules = re.search(r'\.hero-chip\s*\{([^}]+)\}', self.components_css)
        self.assertIsNotNone(chip_rules, ".hero-chip rule block not found")
        self.assertIn("white-space: normal", chip_rules.group(1), ".hero-chip must allow text wrapping")
        self.assertIn("max-width: 100%", chip_rules.group(1), ".hero-chip must not exceed container width")

        # 4. Fluid mobile-ready grid tracks in layout.css
        stats_grid_match = re.search(r'\.stats-grid\s*\{([^}]+)\}', self.layout_css)
        self.assertIsNotNone(stats_grid_match, ".stats-grid rule block not found")
        self.assertIn("minmax(min(100%", stats_grid_match.group(1), ".stats-grid must use min(100%, ...) track bounds")

        # 5. Mobile media queries presence
        self.assertIn("@media (max-width: 640px)", self.components_css, "Missing 640px mobile media query")
        self.assertIn("@media (max-width: 360px)", self.components_css, "Missing 360px small mobile media query")

    def test_radar_chart_labels_anti_clipping(self):
        """Verify that all radar chart labels have concise lines (<= 14 chars) preventing canvas edge clipping."""
        charts_js = (REPO_ROOT / "js" / "charts.js").read_text(encoding="utf-8")
        self.assertIn("function getModuleChartLabel", charts_js)

        map_match = re.search(r"const labelsMap = ({[\s\S]+?\n  };)", charts_js)
        self.assertIsNotNone(map_match, "labelsMap not found in js/charts.js")
        raw_map = map_match.group(1)

        required_modules = [
            "comunicacion_escrita",
            "razonamiento_cuantitativo",
            "lectura_critica",
            "competencias_ciudadanas",
            "ingles",
            "formulacion_proyectos",
            "pensamiento_cientifico",
            "diseno_sistemas",
        ]
        for mod_id in required_modules:
            self.assertIn(mod_id, raw_map, f"Module {mod_id} missing from labelsMap")

        # Check line length constraints for every label
        lines_found = re.findall(r"['\"]([^'\"]+)['\"]", raw_map)
        for line in lines_found:
            if line in required_modules or line in ["es", "en"]:
                continue
            self.assertLessEqual(
                len(line),
                14,
                f"Label line '{line}' exceeds 14 chars ({len(line)} chars) and risks canvas clipping on mobile",
            )

    def test_radar_chart_layout_padding_and_tooltips(self):
        """Verify radar chart uses layout padding safety margins and full-name tooltip titles."""
        charts_js = (REPO_ROOT / "js" / "charts.js").read_text(encoding="utf-8")

        # Verify layout padding buffer
        self.assertIn(
            "padding: isMobile ? 16 : 22",
            charts_js,
            "Radar chart must configure layout padding buffer",
        )

        # Verify tooltip title callback displays full official module name
        self.assertIn(
            "title: function(context)",
            charts_js,
            "Tooltips must provide title callback for full module names",
        )
        self.assertIn(
            "mod.name_en || mod.name_es",
            charts_js,
            "Tooltip title callback must support bilingual module names",
        )

        # Verify radar typography scaling
        self.assertIn(
            "font: { size: isMobile ? 9 : 11",
            charts_js,
            "Radar pointLabels font size must be responsive",
        )
        self.assertIn(
            "padding: isMobile ? 4 : 8",
            charts_js,
            "Radar pointLabels padding must be responsive",
        )

    def test_radar_chart_responsive_css(self):
        """Verify CSS contains responsive sizing for .chart-wrapper-radar and chart figure padding."""
        # 1. Base height
        radar_match = re.search(r"\.chart-wrapper-radar\s*\{([^}]+)\}", self.components_css)
        self.assertIsNotNone(radar_match)
        self.assertIn("height: 420px", radar_match.group(1))

        # 2. 768px query
        m768 = re.search(r"@media \(max-width:\s*768px\)\s*\{([\s\S]+?)\n\}", self.components_css)
        self.assertIsNotNone(m768)
        self.assertIn(".chart-wrapper-radar", m768.group(1))
        self.assertIn("height: 380px", m768.group(1))

        # 3. 640px query
        m640 = re.search(r"@media \(max-width:\s*640px\)\s*\{([\s\S]+?)\n\}", self.components_css)
        self.assertIsNotNone(m640)
        self.assertIn(".chart-wrapper-radar", m640.group(1))
        self.assertIn("height: 350px", m640.group(1))
        self.assertIn("figure.chart-figure", m640.group(1))

        # 4. 360px query
        m360 = re.search(r"@media \(max-width:\s*360px\)\s*\{([\s\S]+?)\n\}", self.components_css)
        self.assertIsNotNone(m360)
        self.assertIn(".chart-wrapper-radar", m360.group(1))
        self.assertIn("height: 310px", m360.group(1))
        self.assertIn("figure.chart-figure", m360.group(1))

    def test_full_site_bitstream_parity_with_docs(self):
        """Verify all critical assets have exact bitstream parity between / and docs/."""
        critical_files = [
            ("index.html", "docs/index.html"),
            ("css/accessibility.css", "docs/css/accessibility.css"),
            ("css/components.css", "docs/css/components.css"),
            ("css/layout.css", "docs/css/layout.css"),
            ("css/typography.css", "docs/css/typography.css"),
            ("css/variables.css", "docs/css/variables.css"),
            ("js/app.js", "docs/js/app.js"),
            ("js/charts.js", "docs/js/charts.js"),
            ("js/i18n.js", "docs/js/i18n.js"),
            ("locales/es.js", "docs/locales/es.js"),
            ("locales/en.js", "docs/locales/en.js"),
            ("data/saber_pro_2015.json", "docs/data/saber_pro_2015.json"),
        ]
        for src, dst in critical_files:
            src_path = REPO_ROOT / src
            dst_path = REPO_ROOT / dst
            self.assertTrue(src_path.exists(), f"Source file missing: {src}")
            self.assertTrue(dst_path.exists(), f"Target file missing: {dst}")
            self.assertTrue(
                filecmp.cmp(src_path, dst_path, shallow=False),
                f"Bitstream mismatch between {src} and {dst}",
            )


if __name__ == "__main__":
    unittest.main()
