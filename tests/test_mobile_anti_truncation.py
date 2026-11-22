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


if __name__ == "__main__":
    unittest.main()
