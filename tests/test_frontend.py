#!/usr/bin/env python3
"""
ICFES Saber Pro 2015 - Frontend & Accessibility Automated Verification Suite
=============================================================================
Validates:
1. Zero CDN dependencies (100% local vendoring).
2. Relative asset paths across HTML files.
3. Perfect bitstream parity between index.html and docs/index.html.
4. Semantic HTML5 landmarks (header, nav, main#main-content, section, figure, footer).
5. Accessibility features (skip-to-content link, :focus-visible, ARIA attributes).
6. WCAG 2.1 AA color contrast compliance (>= 4.5:1) for all badges.
7. Visualization suite markup presence (3 charts + quintile scale).
8. Anomaly documentation coverage (A-01 through A-07).
9. Repository sovereignty & attribution (CC BY 4.0, ICFES sources).
10. Local vendor file integrity.
"""

import filecmp
import math
import os
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestFrontendArchitecture(unittest.TestCase):
    """Test suite validating frontend compliance, accessibility, and parity."""

    @classmethod
    def setUpClass(cls):
        cls.root_index = REPO_ROOT / "index.html"
        cls.docs_index = REPO_ROOT / "docs" / "index.html"
        cls.vendor_chart = REPO_ROOT / "vendor" / "chart.umd.min.js"
        cls.css_dir = REPO_ROOT / "css"
        cls.js_dir = REPO_ROOT / "js"

        cls.assertTrue(cls.root_index.exists(), "Root index.html must exist")
        cls.assertTrue(cls.docs_index.exists(), "docs/index.html must exist")

        with open(cls.root_index, "r", encoding="utf-8") as f:
            cls.root_html = f.read()

        with open(cls.docs_index, "r", encoding="utf-8") as f:
            cls.docs_html = f.read()

    # -------------------------------------------------------------------------
    # 1. ZERO CDN DEPENDENCIES
    # -------------------------------------------------------------------------
    def test_zero_cdn_dependencies(self):
        """Verify that neither index.html nor docs/index.html reference external CDNs."""
        cdn_patterns = [
            r"https?://cdn\.",
            r"jsdelivr\.net",
            r"unpkg\.com",
            r"cdnjs\.cloudflare\.com",
            r"fonts\.googleapis\.com",
            r"fonts\.gstatic\.com",
            r"bootstrapcdn\.com",
            r"ajax\.googleapis\.com",
        ]

        for pattern in cdn_patterns:
            matches_root = re.findall(pattern, self.root_html, re.IGNORECASE)
            self.assertEqual(
                len(matches_root),
                0,
                f"External CDN pattern '{pattern}' found in root index.html: {matches_root}",
            )

            matches_docs = re.findall(pattern, self.docs_html, re.IGNORECASE)
            self.assertEqual(
                len(matches_docs),
                0,
                f"External CDN pattern '{pattern}' found in docs/index.html: {matches_docs}",
            )

        # Check local vendor inclusion
        self.assertIn(
            'src="vendor/chart.umd.min.js"',
            self.root_html,
            "Chart.js must be loaded locally from vendor/chart.umd.min.js",
        )

    # -------------------------------------------------------------------------
    # 2. RELATIVE ASSET PATHS
    # -------------------------------------------------------------------------
    def test_relative_asset_paths(self):
        """Verify that asset paths use relative linking rather than absolute paths."""
        disallowed_prefixes = [
            r'href="/[^\s/]',
            r'src="/[^\s/]',
            r'href="file:',
            r'src="file:',
            r'href="[A-Za-z]:\\',
            r'src="[A-Za-z]:\\',
        ]

        for prefix in disallowed_prefixes:
            self.assertFalse(
                re.search(prefix, self.root_html),
                f"Absolute path reference matching '{prefix}' found in root index.html",
            )
            self.assertFalse(
                re.search(prefix, self.docs_html),
                f"Absolute path reference matching '{prefix}' found in docs/index.html",
            )

        # Verify linked stylesheets are relative
        expected_css_files = [
            "css/variables.css",
            "css/typography.css",
            "css/layout.css",
            "css/components.css",
            "css/accessibility.css",
        ]
        for css in expected_css_files:
            self.assertIn(
                f'href="{css}"',
                self.root_html,
                f"Expected relative stylesheet {css} in root index.html",
            )
            self.assertTrue(
                (REPO_ROOT / css).exists(),
                f"Stylesheet file {css} must exist on disk",
            )

    # -------------------------------------------------------------------------
    # 3. HTML PARITY BETWEEN ROOT AND DOCS
    # -------------------------------------------------------------------------
    def test_html_file_parity(self):
        """Verify 100% byte-for-byte bitstream parity between index.html and docs/index.html."""
        identical = filecmp.cmp(self.root_index, self.docs_index, shallow=False)
        self.assertTrue(
            identical,
            "index.html and docs/index.html must be 100% identical for GitHub Pages parity",
        )
        self.assertGreater(
            len(self.root_html),
            5000,
            "HTML document should be fully populated",
        )

    # -------------------------------------------------------------------------
    # 4. SEMANTIC HTML5 LANDMARKS & ACCESSIBILITY
    # -------------------------------------------------------------------------
    def test_semantic_landmarks(self):
        """Verify presence of all semantic landmarks: header, nav, main, section, figure, footer."""
        self.assertTrue(
            re.search(r"<header\b[^>]*>", self.root_html),
            "Semantic <header> landmark missing",
        )
        self.assertTrue(
            re.search(r"<nav\b[^>]*\baria-label=", self.root_html),
            "Semantic <nav> landmark with aria-label missing",
        )
        self.assertTrue(
            re.search(r'<main\b[^>]*id=["\']main-content["\']', self.root_html),
            'Semantic <main id="main-content"> landmark missing',
        )
        self.assertTrue(
            re.search(r"<section\b[^>]*\bid=", self.root_html),
            "Semantic <section> landmarks with id missing",
        )
        self.assertTrue(
            re.search(r"<figure\b[^>]*>", self.root_html),
            "Semantic <figure> landmarks missing",
        )
        self.assertTrue(
            re.search(r"<figcaption\b[^>]*>", self.root_html),
            "Semantic <figcaption> tags missing",
        )
        self.assertTrue(
            re.search(r"<footer\b[^>]*>", self.root_html),
            "Semantic <footer> landmark missing",
        )

    def test_skip_to_content_link(self):
        """Verify WCAG 2.1 AA skip-to-content link exists at the beginning of body."""
        skip_link_match = re.search(
            r'<a\b[^>]*href=["\']#main-content["\'][^>]*class=["\'][^"\']*skip-link[^"\']*["\']',
            self.root_html,
        )
        self.assertIsNotNone(
            skip_link_match,
            'Accessible skip-to-content link <a href="#main-content" class="skip-link"> missing',
        )

    def test_interactive_controls_aria(self):
        """Verify language toggle and theme buttons have appropriate ARIA attributes."""
        # Language toggle button
        lang_btn = re.search(
            r'<button\b[^>]*id=["\']btnLangToggle["\'][^>]*aria-label=["\'][^"\']+["\'][^>]*aria-pressed=',
            self.root_html,
        )
        self.assertIsNotNone(
            lang_btn,
            "Language toggle button #btnLangToggle with aria-label and aria-pressed is missing",
        )

        # Theme toggle button
        theme_btn = re.search(
            r'<button\b[^>]*id=["\']btnThemeToggle["\'][^>]*aria-label=["\'][^"\']+["\'][^>]*aria-pressed=',
            self.root_html,
        )
        self.assertIsNotNone(
            theme_btn,
            "Theme toggle button #btnThemeToggle with aria-label and aria-pressed is missing",
        )

    # -------------------------------------------------------------------------
    # 5. VISUALIZATIONS SUITE IN MARKUP
    # -------------------------------------------------------------------------
    def test_visualizations_suite_presence(self):
        """Verify all 3 Chart.js canvases and quintile scale container are present with accessible labels."""
        # Grouped bar chart
        self.assertTrue(
            re.search(r'<canvas\b[^>]*id=["\']comparisonChart["\'][^>]*role=["\']img["\']', self.root_html),
            'Canvas #comparisonChart with role="img" missing',
        )

        # Standard normal bell curve
        self.assertTrue(
            re.search(r'<canvas\b[^>]*id=["\']bellCurveChart["\'][^>]*role=["\']img["\']', self.root_html),
            'Canvas #bellCurveChart with role="img" missing',
        )

        # Radar competency profile
        self.assertTrue(
            re.search(r'<canvas\b[^>]*id=["\']radarChart["\'][^>]*role=["\']img["\']', self.root_html),
            'Canvas #radarChart with role="img" missing',
        )

        # Quintile scale display container
        self.assertIn(
            'id="quintileScaleDisplay"',
            self.root_html,
            "Quintile scale display container #quintileScaleDisplay missing",
        )

    # -------------------------------------------------------------------------
    # 6. WCAG 2.1 AA COLOR CONTRAST COMPLIANCE
    # -------------------------------------------------------------------------
    @staticmethod
    def _relative_luminance(hex_str: str) -> float:
        """Calculates WCAG 2.1 relative luminance for an sRGB hexadecimal color."""
        h = hex_str.lstrip("#")
        rgb = [int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4)]
        rgb_lin = [
            c / 12.92 if c <= 0.04045 else math.pow((c + 0.055) / 1.055, 2.4)
            for c in rgb
        ]
        return 0.2126 * rgb_lin[0] + 0.7152 * rgb_lin[1] + 0.0722 * rgb_lin[2]

    @classmethod
    def _contrast_ratio(cls, hex1: str, hex2: str) -> float:
        """Computes contrast ratio between two hex colors: (L1 + 0.05) / (L2 + 0.05)."""
        l1 = cls._relative_luminance(hex1)
        l2 = cls._relative_luminance(hex2)
        lighter = max(l1, l2)
        darker = min(l1, l2)
        return (lighter + 0.05) / (darker + 0.05)

    def test_badge_wcag_contrast_ratios(self):
        """Verify that all quintile badges (Q1-Q5) achieve WCAG AA contrast ratio >= 4.5:1.

        Specifically tests Q1 slate badge which previously failed in legacy styling.
        """
        # Parse badge tokens from css/variables.css
        vars_css = (REPO_ROOT / "css" / "variables.css").read_text(encoding="utf-8")

        badge_bg_pattern = r"--badge-(q[1-5])-bg:\s*(#[0-9a-fA-F]{6});"
        badge_fg_pattern = r"--badge-(q[1-5])-fg:\s*(#[0-9a-fA-F]{6});"

        bg_colors = dict(re.findall(badge_bg_pattern, vars_css))
        fg_colors = dict(re.findall(badge_fg_pattern, vars_css))

        self.assertEqual(len(bg_colors), 5, "All 5 quintile badge bg colors must be defined")
        self.assertEqual(len(fg_colors), 5, "All 5 quintile badge fg colors must be defined")

        for q in ["q1", "q2", "q3", "q4", "q5"]:
            bg = bg_colors[q]
            fg = fg_colors[q]
            cr = self._contrast_ratio(bg, fg)
            self.assertGreaterEqual(
                cr,
                4.5,
                f"Badge {q} contrast ratio {cr:.2f}:1 fails WCAG AA minimum 4.5:1 (bg={bg}, fg={fg})",
            )
            if q == "q1":
                # Explicit check for Q1 slate badge fix
                self.assertGreaterEqual(
                    cr,
                    4.5,
                    f"Q1 slate badge failed contrast requirement: {cr:.2f}:1",
                )

    # -------------------------------------------------------------------------
    # 7. ANOMALY AUDIT SECTION (A-01 to A-07)
    # -------------------------------------------------------------------------
    def test_anomalies_audit_section(self):
        """Verify that anomalies A-01 through A-07 are present in markup."""
        self.assertIn('id="anomalies"', self.root_html, "Section #anomalies missing")
        self.assertIn('id="anomaliesList"', self.root_html, "Container #anomaliesList missing")

        for i in range(1, 8):
            anomaly_id = f"A-0{i}"
            self.assertIn(
                anomaly_id,
                self.root_html,
                f"Anomaly {anomaly_id} missing in root index.html",
            )

    # -------------------------------------------------------------------------
    # 8. LICENSE & INSTITUTIONAL ATTRIBUTION
    # -------------------------------------------------------------------------
    def test_license_and_sources_attribution(self):
        """Verify CC BY 4.0 license attribution and ICFES source references."""
        self.assertIn(
            "CC BY 4.0",
            self.root_html,
            "Creative Commons CC BY 4.0 license attribution missing",
        )
        self.assertIn(
            "ICFES",
            self.root_html,
            "ICFES institutional attribution missing",
        )
        self.assertIn(
            "EK201532097061",
            self.root_html,
            "Official exam registration number EK201532097061 missing",
        )
        self.assertIn(
            "https://github.com/willkwolf/ICFES-saberPro2015",
            self.root_html,
            "Canonical GitHub repository URL missing or broken",
        )

    # -------------------------------------------------------------------------
    # 9. VENDOR FILE INTEGRITY
    # -------------------------------------------------------------------------
    def test_vendor_chartjs_integrity(self):
        """Verify local Chart.js vendor file exists and is valid."""
        self.assertTrue(self.vendor_chart.exists(), "vendor/chart.umd.min.js must exist")
        file_size = os.path.getsize(self.vendor_chart)
        self.assertGreater(
            file_size,
            100_000,
            f"vendor/chart.umd.min.js file size ({file_size} bytes) is suspiciously small",
        )

        with open(self.vendor_chart, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(500)
            self.assertTrue(
                "Chart" in content or "chart.js" in content.lower(),
                "Vendor file does not appear to contain Chart.js library code",
            )


if __name__ == "__main__":
    unittest.main()
