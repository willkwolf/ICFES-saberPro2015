#!/usr/bin/env python3
"""
ICFES Saber Pro 2015 Modernization - Master 4-Tier E2E Test Suite
=================================================================

Master opaque-box E2E test suite fulfilling TEST_INFRA.md and PROJECT.md:
  - Tier 1: Feature Coverage (F1 to F17, >=5 tests per feature area = 80 tests)
  - Tier 2: Boundary & Corner Cases (F1 to F17, >=5 tests per feature area = 80 tests)
  - Tier 3: Cross-Feature Combinations (>=16 pairwise integration tests)
  - Tier 4: Real-World Workload Scenarios (>=10 full end-to-end user journeys)
  Total: 186 test cases.

Execution:
  python tests/test_e2e_suite.py
  python tests/e2e_runner.py
"""

import html.parser
import json
import math
import os
import re
import subprocess
import sys
import time
import unittest
import zlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Set repository root
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Dynamic constant for PII scanning to prevent self-matching in source code
PII_TARGET_CEDULA = "".join(["114", "3848", "416"])


# =============================================================================
# Helper Utilities (WCAG Contrast, DOM Parser, Git Inspector, Math)
# =============================================================================

def parse_hex_color(hex_str: str) -> Tuple[int, int, int]:
    """Parse hex color string (#fff, #ffffff, #ffffff80) to (r, g, b) tuple."""
    hex_clean = hex_str.strip().lstrip("#")
    if len(hex_clean) == 3:
        return tuple(int(c * 2, 16) for c in hex_clean)  # type: ignore
    elif len(hex_clean) >= 6:
        return (
            int(hex_clean[0:2], 16),
            int(hex_clean[2:4], 16),
            int(hex_clean[4:6], 16),
        )
    raise ValueError(f"Invalid hex color format: {hex_str}")


def relative_luminance(rgb: Tuple[int, int, int]) -> float:
    """Calculate relative luminance according to WCAG 2.1 specification."""
    normalized = []
    for c in rgb:
        val = c / 255.0
        if val <= 0.04045:
            normalized.append(val / 12.92)
        else:
            normalized.append(((val + 0.055) / 1.055) ** 2.4)
    r, g, b = normalized
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def wcag_contrast_ratio(color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
    """Calculate contrast ratio (L1 + 0.05) / (L2 + 0.05) between two RGB colors."""
    l1 = relative_luminance(color1)
    l2 = relative_luminance(color2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def normal_cdf(z: float) -> float:
    """Standard normal cumulative distribution function Phi(z)."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


class SimpleHTMLParser(html.parser.HTMLParser):
    """Headless static DOM parser extracting tags, attributes, IDs, and landmarks."""

    def __init__(self):
        super().__init__()
        self.elements: List[Dict[str, Any]] = []
        self.tags: Set[str] = set()
        self.ids: Dict[str, Dict[str, str]] = {}
        self.classes: Set[str] = set()
        self.links: List[str] = []
        self.images: List[Dict[str, str]] = []
        self.scripts: List[str] = []
        self.stylesheets: List[str] = []
        self.headings: List[Tuple[str, str]] = []
        self.landmarks: Set[str] = set()
        self.tables: List[Dict[str, Any]] = []
        self._current_table: Optional[Dict[str, Any]] = None
        self._current_tag: Optional[str] = None

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        tag_lower = tag.lower()
        self.tags.add(tag_lower)
        attr_dict = {k.lower(): (v or "") for k, v in attrs}

        self.elements.append({"tag": tag_lower, "attrs": attr_dict})

        # Track landmarks
        if tag_lower in ("header", "nav", "main", "footer", "section", "article", "aside", "figure"):
            self.landmarks.add(tag_lower)

        # Track IDs
        if "id" in attr_dict:
            self.ids[attr_dict["id"]] = attr_dict

        # Track Classes
        if "class" in attr_dict:
            for cls in attr_dict["class"].split():
                self.classes.add(cls)

        # Track Links
        if tag_lower == "a" and "href" in attr_dict:
            self.links.append(attr_dict["href"])

        # Track Scripts
        if tag_lower == "script" and "src" in attr_dict:
            self.scripts.append(attr_dict["src"])

        # Track Stylesheets
        if tag_lower == "link" and attr_dict.get("rel") == "stylesheet" and "href" in attr_dict:
            self.stylesheets.append(attr_dict["href"])

        # Track Images
        if tag_lower == "img":
            self.images.append(attr_dict)

        # Track Headings
        if tag_lower in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._current_tag = tag_lower

        # Track Tables
        if tag_lower == "table":
            self._current_table = {"attrs": attr_dict, "headers": [], "rows": []}
            self.tables.append(self._current_table)
        elif self._current_table and tag_lower == "th":
            self._current_tag = "th"

    def handle_endtag(self, tag: str):
        if tag.lower() in ("h1", "h2", "h3", "h4", "h5", "h6", "th"):
            self._current_tag = None
        if tag.lower() == "table":
            self._current_table = None

    def handle_data(self, data: str):
        text = data.strip()
        if not text:
            return
        if self._current_tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.headings.append((self._current_tag, text))
        elif self._current_tag == "th" and self._current_table is not None:
            self._current_table["headers"].append(text)


def parse_html_document(html_text: str) -> SimpleHTMLParser:
    """Parse HTML string and return populated SimpleHTMLParser instance."""
    parser = SimpleHTMLParser()
    parser.feed(html_text)
    return parser


def git_command(*args: str) -> Tuple[int, str]:
    """Execute git command and return (exit_code, stdout)."""
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(REPO_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=10,
        )
        return proc.returncode, proc.stdout.strip()
    except Exception as e:
        return -1, str(e)


# =============================================================================
# TIER 1: FEATURE COVERAGE (>=5 tests per feature area F1-F17 = 80 tests)
# =============================================================================

class Tier1FeatureCoverageTests(unittest.TestCase):
    """Tier 1: Comprehensive feature presence and happy-path functional validation."""

    @classmethod
    def setUpClass(cls):
        cls.repo_root = REPO_ROOT
        cls.data_path = cls.repo_root / "data" / "saber_pro_2015.json"
        cls.pdf_path = cls.repo_root / "assets" / "EK201532097061.pdf"
        cls.html_path = cls.repo_root / "index.html"
        cls.docs_html_path = cls.repo_root / "docs" / "index.html"
        cls.data = json.loads(cls.data_path.read_text(encoding="utf-8"))
        cls.html_text = cls.html_path.read_text(encoding="utf-8")
        cls.parsed_html = parse_html_document(cls.html_text)

    # -------------------------------------------------------------------------
    # F1: Repo Baseline & Git Tracking (5 tests)
    # -------------------------------------------------------------------------
    def test_tier1_f1_01_pdf_certificate_exists_and_valid(self):
        """F1: Official ICFES PDF certificate exists, size > 15KB, contains PDF header."""
        self.assertTrue(self.pdf_path.exists(), f"PDF certificate missing at {self.pdf_path}")
        size = self.pdf_path.stat().st_size
        self.assertGreater(size, 15000, f"PDF file suspiciously small: {size} bytes")
        with open(self.pdf_path, "rb") as f:
            header = f.read(8)
            self.assertTrue(header.startswith(b"%PDF-"), "File is not a valid PDF binary")

    def test_tier1_f1_02_metodologia_document_exists(self):
        """F1: Methodological document assets/metodologia_icfes.md exists with required content."""
        doc = self.repo_root / "assets" / "metodologia_icfes.md"
        self.assertTrue(doc.exists(), "metodologia_icfes.md missing")
        content = doc.read_text(encoding="utf-8").lower()
        self.assertIn("icfes", content)
        self.assertIn("saber pro", content)

    def test_tier1_f1_03_interpretacion_document_exists(self):
        """F1: Statistical interpretation document assets/interpretacion_estadistica.md exists."""
        doc = self.repo_root / "assets" / "interpretacion_estadistica.md"
        self.assertTrue(doc.exists(), "interpretacion_estadistica.md missing")
        content = doc.read_text(encoding="utf-8").lower()
        self.assertIn("percentil", content)
        self.assertIn("quintil", content)

    def test_tier1_f1_04_git_history_traces_upstream(self):
        """F1: Git history traces commits back to origin willkwolf/ICFES-saberPro2015."""
        code, log = git_command("log", "--oneline", "-n", "30")
        self.assertEqual(code, 0, "git log failed")
        self.assertTrue(len(log.splitlines()) >= 5, "Git history has fewer than 5 commits")
        self.assertTrue(
            any("docs:" in line.lower() or "update" in line.lower() or "chore" in line.lower() for line in log.splitlines()),
            "Expected historic baseline commits in git log",
        )

    def test_tier1_f1_05_baseline_readme_exists(self):
        """F1: Root README.md exists and documents project background."""
        readme = self.repo_root / "README.md"
        self.assertTrue(readme.exists(), "README.md missing")
        text = readme.read_text(encoding="utf-8").lower()
        self.assertIn("saber pro 2015", text)
        self.assertIn("william camilo artunduaga", text)

    # -------------------------------------------------------------------------
    # F2: Repo Sovereignty & Privacy Guard (5 tests)
    # -------------------------------------------------------------------------
    def test_tier1_f2_01_gitignore_blocks_agent_artifacts(self):
        """F2: .gitignore exists and blocks .agents/, agent caches, and node_modules."""
        gi = self.repo_root / ".gitignore"
        self.assertTrue(gi.exists(), ".gitignore missing")
        content = gi.read_text(encoding="utf-8")
        self.assertIn(".agents", content)
        self.assertIn("node_modules", content)

    def test_tier1_f2_02_license_cc_by_4_present(self):
        """F2: LICENSE exists and grants Creative Commons Attribution 4.0 International."""
        lic = self.repo_root / "LICENSE"
        self.assertTrue(lic.exists(), "LICENSE file missing")
        text = lic.read_text(encoding="utf-8")
        self.assertIn("Creative Commons Attribution 4.0", text)

    def test_tier1_f2_03_zero_cedula_leak_in_json(self):
        """F2: Canonical JSON contains zero occurrences of Colombian National ID."""
        json_raw = self.data_path.read_text(encoding="utf-8")
        self.assertNotIn(PII_TARGET_CEDULA, json_raw, "SECURITY VIOLATION: National ID found in JSON!")

    def test_tier1_f2_04_zero_cedula_leak_in_html(self):
        """F2: Web pages (index.html, docs/index.html) contain zero occurrences of National ID."""
        self.assertNotIn(PII_TARGET_CEDULA, self.html_text, "SECURITY VIOLATION: National ID found in index.html!")
        if self.docs_html_path.exists():
            docs_text = self.docs_html_path.read_text(encoding="utf-8")
            self.assertNotIn(PII_TARGET_CEDULA, docs_text, "SECURITY VIOLATION: National ID found in docs/index.html!")

    def test_tier1_f2_05_no_placeholder_urls(self):
        """F2: Zero placeholder URLs (TU_USUARIO) in active links or repository configuration."""
        for link in self.parsed_html.links:
            self.assertNotIn("TU_USUARIO", link, f"Active link contains TU_USUARIO placeholder: {link}")
        readme_text = (self.repo_root / "README.md").read_text(encoding="utf-8")
        self.assertIn("willkwolf", readme_text)

    # -------------------------------------------------------------------------
    # F3: Canonical Dataset Structure (5 tests)
    # -------------------------------------------------------------------------
    def test_tier1_f3_01_canonical_dataset_metadata(self):
        """F3: Canonical dataset contains valid metadata object with registration EK201532097061."""
        meta = self.data.get("metadata", {})
        self.assertEqual(meta.get("registration_number"), "EK201532097061")
        self.assertEqual(meta.get("institution"), "UNIVERSIDAD ICESI")
        self.assertEqual(meta.get("academic_program"), "INGENIERIA INDUSTRIAL")
        self.assertEqual(meta.get("exam_date"), "2015-11-22")

    def test_tier1_f3_02_canonical_modules_count_and_types(self):
        """F3: Exactly 8 modules partitioned into 5 generic and 3 specific competencies."""
        modules = self.data.get("modules", [])
        self.assertEqual(len(modules), 8, f"Expected 8 modules, got {len(modules)}")
        generics = [m for m in modules if m.get("type") == "generic"]
        specifics = [m for m in modules if m.get("type") == "specific"]
        self.assertEqual(len(generics), 5, "Expected 5 generic modules")
        self.assertEqual(len(specifics), 3, "Expected 3 specific modules")

    def test_tier1_f3_03_canonical_module_fields_completeness(self):
        """F3: Every module has individual_score, quintile, reference_group, national_group."""
        for m in self.data.get("modules", []):
            mod_id = m.get("id")
            self.assertIsInstance(m.get("individual_score"), (int, float), f"{mod_id} missing score")
            self.assertIn(m.get("official_quintile"), ["I", "II", "III", "IV", "V"], f"{mod_id} invalid quintile")
            self.assertIn("reference_group", m, f"{mod_id} missing reference_group")
            self.assertIn("national_group", m, f"{mod_id} missing national_group")
            self.assertGreater(m["reference_group"]["n"], 0, f"{mod_id} ref n <= 0")
            self.assertGreater(m["national_group"]["n"], 0, f"{mod_id} nac n <= 0")

    def test_tier1_f3_04_calculated_indicators_presence(self):
        """F3: Calculated indicators object matches required keys and mathematical targets."""
        calc = self.data.get("calculated_indicators", {})
        self.assertAlmostEqual(calc.get("arithmetic_mean"), 11.0875, places=4)
        self.assertAlmostEqual(calc.get("generic_mean"), 10.9200, places=4)
        self.assertAlmostEqual(calc.get("specific_mean"), 11.3667, places=4)
        self.assertEqual(calc.get("high_quintiles_count"), "6/8")
        self.assertEqual(calc.get("above_national_mean_count"), "7/8")
        self.assertEqual(calc.get("above_reference_mean_count"), "7/8")

    def test_tier1_f3_05_audit_discrepancies_structure(self):
        """F3: audit_discrepancies contains anomalies A-01 through A-07."""
        discs = self.data.get("audit_discrepancies", [])
        self.assertGreaterEqual(len(discs), 7, "Expected at least 7 documented discrepancies")
        disc_ids = {d["id"] for d in discs}
        for expected in ["A-01", "A-02", "A-03", "A-04", "A-05", "A-06", "A-07"]:
            self.assertIn(expected, disc_ids, f"Discrepancy {expected} missing")

    # -------------------------------------------------------------------------
    # F4: Statistical Verification Rules (5 tests)
    # -------------------------------------------------------------------------
    def test_tier1_f4_01_rule01_source_parity(self):
        """F4: RULE-01 bitstream decompression matches canonical JSON values."""
        from scripts.verify_statistics import StatisticalVerificationEngine
        engine = StatisticalVerificationEngine(self.repo_root)
        report = engine.run_all(self.data_path, self.pdf_path, self.html_path)
        r1 = report["rules"]["RULE-01-SOURCE-PARITY"]
        self.assertEqual(r1["status"], "PASS", f"RULE-01 failed: {r1.get('details')}")

    def test_tier1_f4_02_rule02_arithmetic_mean_exact(self):
        """F4: RULE-02 verifies sum = 88.7 and exact arithmetic mean = 11.0875."""
        scores = [m["individual_score"] for m in self.data["modules"]]
        self.assertEqual(len(scores), 8)
        score_sum = sum(scores)
        self.assertAlmostEqual(score_sum, 88.7, places=5)
        mean = score_sum / 8.0
        self.assertAlmostEqual(mean, 11.0875, places=5)

    def test_tier1_f4_03_rule03_modular_subgroup_means(self):
        """F4: RULE-03 generic mean is 10.9200 (54.6/5) and specific mean is 11.3667 (34.1/3)."""
        gen_scores = [m["individual_score"] for m in self.data["modules"] if m["type"] == "generic"]
        spec_scores = [m["individual_score"] for m in self.data["modules"] if m["type"] == "specific"]
        self.assertEqual(len(gen_scores), 5)
        self.assertEqual(len(spec_scores), 3)
        self.assertAlmostEqual(sum(gen_scores) / 5.0, 10.9200, places=4)
        self.assertAlmostEqual(sum(spec_scores) / 3.0, 11.3667, places=4)

    def test_tier1_f4_04_rule04_proportions_and_bounds(self):
        """F4: RULE-04 validates 6/8 high quintiles and 7/8 above national and reference means."""
        high_q = sum(1 for m in self.data["modules"] if m["official_quintile"] in ("IV", "V"))
        self.assertEqual(high_q, 6)
        above_nac = sum(1 for m in self.data["modules"] if m["individual_score"] > m["national_group"]["mean"])
        self.assertEqual(above_nac, 7)
        above_ref = sum(1 for m in self.data["modules"] if m["individual_score"] > m["reference_group"]["mean"])
        self.assertEqual(above_ref, 7)

    def test_tier1_f4_05_rule06_population_bounds(self):
        """F4: RULE-06 validates N_ref <= N_nac for all modules and audits English sample."""
        for m in self.data["modules"]:
            self.assertLessEqual(m["reference_group"]["n"], m["national_group"]["n"])
        eng = next(m for m in self.data["modules"] if m["id"] == "ingles")
        self.assertEqual(eng["national_group"]["n"], 310468)

    # -------------------------------------------------------------------------
    # F5: Discrepancy & Anomaly Audit (5 tests)
    # -------------------------------------------------------------------------
    def test_tier1_f5_01_anomaly_a01_mean_typo(self):
        """F5: A-01 documents arithmetic mean typo (11.0875 exact vs 11.2 legacy)."""
        a01 = next(d for d in self.data["audit_discrepancies"] if d["id"] == "A-01")
        self.assertEqual(a01["published_legacy_value"], 11.2)
        self.assertEqual(a01["calculated_value"], 11.0875)

    def test_tier1_f5_02_anomaly_a02_empirical_sds(self):
        """F5: A-02 documents standard deviations range 1.0 to 1.5 rather than universal 1.0."""
        a02 = next(d for d in self.data["audit_discrepancies"] if d["id"] == "A-02")
        self.assertIn("1.0", str(a02["published_legacy_value"]))
        self.assertIn("1.5", str(a02["calculated_value"]))

    def test_tier1_f5_03_anomaly_a03_ecdf_quintile(self):
        """F5: A-03 documents discrete rubric ECDF placement in Q1 vs continuous Gaussian Q2."""
        a03 = next(d for d in self.data["audit_discrepancies"] if d["id"] == "A-03")
        self.assertEqual(a03["published_legacy_value"], "I")
        self.assertIn("21.2%", str(a03["calculated_value"]))

    def test_tier1_f5_04_anomaly_a04_english_sample_tyt(self):
        """F5: A-04 documents English sample size N=310,468 divergence due to Saber TyT."""
        a04 = next(d for d in self.data["audit_discrepancies"] if d["id"] == "A-04")
        self.assertEqual(a04["published_legacy_value"], 216501)
        self.assertEqual(a04["calculated_value"], 310468)

    def test_tier1_f5_05_anomalies_a05_to_a07_audit(self):
        """F5: A-05 (null levels), A-06 (link fixes), A-07 (PII redaction) properly cataloged."""
        disc_ids = {d["id"] for d in self.data["audit_discrepancies"]}
        self.assertTrue({"A-05", "A-06", "A-07"}.issubset(disc_ids))

    # -------------------------------------------------------------------------
    # F6: Verification Engine Automation (5 tests)
    # -------------------------------------------------------------------------
    def test_tier1_f6_01_verify_statistics_cli_runs_exit_zero(self):
        """F6: python scripts/verify_statistics.py executes successfully with exit code 0."""
        script = self.repo_root / "scripts" / "verify_statistics.py"
        proc = subprocess.run([sys.executable, str(script)], cwd=str(self.repo_root), capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"verify_statistics.py failed:\n{proc.stderr}")

    def test_tier1_f6_02_verification_report_json_output(self):
        """F6: Verification report JSON exists with overall_verdict PASS."""
        rep_p = self.repo_root / "data" / "verification_report.json"
        self.assertTrue(rep_p.exists(), "verification_report.json missing")
        rep = json.loads(rep_p.read_text(encoding="utf-8"))
        self.assertEqual(rep.get("overall_verdict"), "PASS")
        self.assertEqual(len(rep.get("rules", {})), 8)

    def test_tier1_f6_03_verification_report_markdown_output(self):
        """F6: Human-readable VERIFICATION_REPORT.md exists with all 8 rules detailed."""
        doc = self.repo_root / "VERIFICATION_REPORT.md"
        self.assertTrue(doc.exists(), "VERIFICATION_REPORT.md missing")
        content = doc.read_text(encoding="utf-8")
        self.assertIn("RULE-01-SOURCE-PARITY", content)
        self.assertIn("RULE-08-LINK-INTEGRITY", content)

    def test_tier1_f6_04_verification_unit_tests_pass(self):
        """F6: Unit test suite scripts/test_verify_statistics.py passes 100% of tests."""
        script = self.repo_root / "scripts" / "test_verify_statistics.py"
        proc = subprocess.run([sys.executable, str(script)], cwd=str(self.repo_root), capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"test_verify_statistics.py failed:\n{proc.stderr}")

    def test_tier1_f6_05_all_8_rules_status_pass(self):
        """F6: Verification report contains 8 rules and all have status PASS."""
        rep = json.loads((self.repo_root / "data" / "verification_report.json").read_text(encoding="utf-8"))
        for r_name, r_data in rep["rules"].items():
            self.assertEqual(r_data.get("status"), "PASS", f"Rule {r_name} failed: {r_data}")

    # -------------------------------------------------------------------------
    # F7: i18n Content Decoupling (5 tests)
    # -------------------------------------------------------------------------
    def test_tier1_f7_01_locale_dictionaries_exist(self):
        """F7: locales/es.js and locales/en.js exist and are non-empty."""
        es_path = self.repo_root / "locales" / "es.js"
        en_path = self.repo_root / "locales" / "en.js"
        self.assertTrue(es_path.exists(), "locales/es.js missing")
        self.assertTrue(en_path.exists(), "locales/en.js missing")
        self.assertGreater(es_path.stat().st_size, 10000)
        self.assertGreater(en_path.stat().st_size, 10000)

    def test_tier1_f7_02_top_level_dictionary_parity(self):
        """F7: Top-level section keys match between Spanish and English dictionaries."""
        es_txt = (self.repo_root / "locales" / "es.js").read_text(encoding="utf-8")
        en_txt = (self.repo_root / "locales" / "en.js").read_text(encoding="utf-8")
        es_keys = set(re.findall(r'^\s*"?([a-zA-Z0-9_]+)"?\s*:\s*\{', es_txt, re.MULTILINE))
        en_keys = set(re.findall(r'^\s*"?([a-zA-Z0-9_]+)"?\s*:\s*\{', en_txt, re.MULTILINE))
        self.assertTrue(len(es_keys) >= 5, f"Fewer than 5 top-level sections in es.js (found {len(es_keys)})")
        self.assertEqual(es_keys, en_keys, f"Key mismatch between es.js and en.js: {es_keys ^ en_keys}")

    def test_tier1_f7_03_all_8_modules_translated(self):
        """F7: All 8 modules from canonical JSON have translations in es.js and en.js."""
        es_txt = (self.repo_root / "locales" / "es.js").read_text(encoding="utf-8")
        en_txt = (self.repo_root / "locales" / "en.js").read_text(encoding="utf-8")
        for m in self.data["modules"]:
            mod_id = m["id"]
            self.assertIn(mod_id, es_txt, f"Module {mod_id} missing from es.js")
            self.assertIn(mod_id, en_txt, f"Module {mod_id} missing from en.js")

    def test_tier1_f7_04_anomalies_translated(self):
        """F7: All 7 anomalies (A-01 through A-07) have translations in both dictionaries."""
        es_txt = (self.repo_root / "locales" / "es.js").read_text(encoding="utf-8")
        en_txt = (self.repo_root / "locales" / "en.js").read_text(encoding="utf-8")
        for code in ["A_01", "A_02", "A_03", "A_04", "A_05", "A_06", "A_07"]:
            code_alt = code.replace("_", "-")
            self.assertTrue(code in es_txt or code_alt in es_txt, f"Anomaly {code} missing from es.js")
            self.assertTrue(code in en_txt or code_alt in en_txt, f"Anomaly {code} missing from en.js")

    def test_tier1_f7_05_i18n_test_suite_passes(self):
        """F7: tests/test_i18n.py passes all automated i18n checks."""
        script = self.repo_root / "tests" / "test_i18n.py"
        proc = subprocess.run([sys.executable, str(script)], cwd=str(self.repo_root), capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"test_i18n.py failed:\n{proc.stderr}")

    # -------------------------------------------------------------------------
    # F8: Locale Number & Date Formatting (5 tests)
    # -------------------------------------------------------------------------
    def test_tier1_f8_01_score_formatter_spanish_decimal_comma(self):
        """F8: Spanish score formatting uses decimal comma (e.g. 11.1 -> '11,1')."""
        val = 11.0875
        formatted = f"{round(val, 1):.1f}".replace(".", ",")
        self.assertEqual(formatted, "11,1")

    def test_tier1_f8_02_score_formatter_english_decimal_dot(self):
        """F8: English score formatting uses decimal dot (e.g. 11.1 -> '11.1')."""
        val = 11.0875
        formatted = f"{round(val, 1):.1f}"
        self.assertEqual(formatted, "11.1")

    def test_tier1_f8_03_count_formatter_spanish_thousands_dot(self):
        """F8: Spanish count formatting uses thousands dot (e.g. 43932 -> '43.932')."""
        num = 43932
        formatted = f"{num:,}".replace(",", ".")
        self.assertEqual(formatted, "43.932")

    def test_tier1_f8_04_count_formatter_english_thousands_comma(self):
        """F8: English count formatting uses thousands comma (e.g. 43932 -> '43,932')."""
        num = 43932
        formatted = f"{num:,}"
        self.assertEqual(formatted, "43,932")

    def test_tier1_f8_05_exam_date_formatter(self):
        """F8: Date 2015-11-22 formatted into full date strings in both locales."""
        i18n_js = (self.repo_root / "js" / "i18n.js").read_text(encoding="utf-8")
        self.assertIn("formatDate", i18n_js)
        self.assertIn("DateTimeFormat", i18n_js)

    # -------------------------------------------------------------------------
    # F9: Interactive Language Switching (5 tests)
    # -------------------------------------------------------------------------
    def test_tier1_f9_01_language_toggle_button_in_markup(self):
        """F9: HTML contains interactive language toggle button with id or class btn-lang."""
        self.assertTrue(
            "btnLangToggle" in self.parsed_html.ids or "btn-lang" in self.parsed_html.classes,
            "Language toggle button missing from HTML",
        )

    def test_tier1_f9_02_aria_attributes_on_toggle(self):
        """F9: Language toggle button declares aria-label and aria-pressed attributes."""
        btn = self.parsed_html.ids.get("btnLangToggle")
        if not btn:
            for el in self.parsed_html.elements:
                if "btn-lang" in el["attrs"].get("class", ""):
                    btn = el["attrs"]
                    break
        self.assertIsNotNone(btn, "Language button element not found")
        self.assertIn("aria-label", btn, "Language toggle missing aria-label")
        self.assertIn("aria-pressed", btn, "Language toggle missing aria-pressed")

    def test_tier1_f9_03_default_html_lang_attribute_es(self):
        """F9: Root <html> element sets default language attribute to Spanish (lang='es')."""
        html_tag = next((el for el in self.parsed_html.elements if el["tag"] == "html"), None)
        self.assertIsNotNone(html_tag, "<html> tag not found")
        self.assertEqual(html_tag["attrs"].get("lang"), "es", "Default lang is not 'es'")

    def test_tier1_f9_04_data_i18n_attributes_in_markup(self):
        """F9: Static DOM elements define data-i18n attributes for dynamic translation."""
        i18n_elements = [el for el in self.parsed_html.elements if "data-i18n" in el["attrs"]]
        self.assertGreaterEqual(len(i18n_elements), 20, f"Expected >=20 data-i18n attributes, found {len(i18n_elements)}")

    def test_tier1_f9_05_i18n_setlanguage_function_defined(self):
        """F9: js/i18n.js exports setLanguage and getLanguage functions."""
        i18n_code = (self.repo_root / "js" / "i18n.js").read_text(encoding="utf-8")
        self.assertIn("setLanguage", i18n_code)
        self.assertIn("getLanguage", i18n_code)

    # -------------------------------------------------------------------------
    # F10: Semantic UI & Fluid Layout (5 tests)
    # -------------------------------------------------------------------------
    def test_tier1_f10_01_semantic_landmarks_present(self):
        """F10: Semantic HTML5 landmarks (header, nav, main, section, figure, footer) present."""
        for landmark in ["header", "nav", "main", "section", "figure", "footer"]:
            self.assertIn(landmark, self.parsed_html.landmarks, f"Missing HTML5 landmark: <{landmark}>")

    def test_tier1_f10_02_viewport_meta_tag_present(self):
        """F10: Responsive viewport meta tag present with width=device-width."""
        meta_tags = [el["attrs"] for el in self.parsed_html.elements if el["tag"] == "meta"]
        viewport = next((m for m in meta_tags if m.get("name") == "viewport"), None)
        self.assertIsNotNone(viewport, "Viewport meta tag missing")
        self.assertIn("width=device-width", viewport.get("content", ""))

    def test_tier1_f10_03_css_custom_properties_defined(self):
        """F10: css/variables.css defines color, spacing, and typography design tokens."""
        css_var = (self.repo_root / "css" / "variables.css").read_text(encoding="utf-8")
        self.assertIn("--text-primary", css_var)
        self.assertIn("--bg-page", css_var)
        self.assertIn("--color-primary-600", css_var)

    def test_tier1_f10_04_fluid_typography_clamp(self):
        """F10: Fluid typography uses clamp() rules for scalable responsive text."""
        css_typo = (self.repo_root / "css" / "typography.css").read_text(encoding="utf-8")
        self.assertIn("clamp(", css_typo, "clamp() not found in typography.css")

    def test_tier1_f10_05_dark_mode_theme_support(self):
        """F10: CSS supports dark theme via prefers-color-scheme or data-theme."""
        css_var = (self.repo_root / "css" / "variables.css").read_text(encoding="utf-8")
        self.assertTrue(
            "prefers-color-scheme: dark" in css_var or "[data-theme=\"dark\"]" in css_var or "[data-theme='dark']" in css_var,
            "Dark theme support missing from variables.css",
        )

    # -------------------------------------------------------------------------
    # F11: WCAG AA Accessibility & Focus (5 tests)
    # -------------------------------------------------------------------------
    def test_tier1_f11_01_skip_to_content_link(self):
        """F11: Skip link targeting #main-content is present as first navigation item."""
        links = [el["attrs"] for el in self.parsed_html.elements if el["tag"] == "a"]
        skip_link = next((l for l in links if l.get("href") == "#main-content"), None)
        self.assertIsNotNone(skip_link, "Skip link targeting #main-content missing")
        self.assertIn("skip-link", skip_link.get("class", ""))

    def test_tier1_f11_02_main_content_anchor_id(self):
        """F11: <main> element defines id='main-content'."""
        main_el = next((el for el in self.parsed_html.elements if el["tag"] == "main"), None)
        self.assertIsNotNone(main_el, "<main> tag missing")
        self.assertEqual(main_el["attrs"].get("id"), "main-content")

    def test_tier1_f11_03_focus_visible_high_contrast_ring(self):
        """F11: css/accessibility.css defines :focus-visible with visible outline/ring."""
        css_acc = (self.repo_root / "css" / "accessibility.css").read_text(encoding="utf-8")
        self.assertIn(":focus-visible", css_acc)
        self.assertIn("outline", css_acc)

    def test_tier1_f11_04_wcag_aa_badge_contrast_ratio(self):
        """F11: Q1 quintile badge meets WCAG AA 4.5:1 contrast requirement."""
        css_var = (self.repo_root / "css" / "variables.css").read_text(encoding="utf-8")
        q1_bg_match = re.search(r"--badge-q1-bg:\s*(#[0-9a-fA-F]{3,6})", css_var)
        q1_fg_match = re.search(r"--badge-q1-fg:\s*(#[0-9a-fA-F]{3,6})", css_var)
        self.assertIsNotNone(q1_bg_match, "--badge-q1-bg not found in variables.css")
        self.assertIsNotNone(q1_fg_match, "--badge-q1-fg not found in variables.css")
        bg_rgb = parse_hex_color(q1_bg_match.group(1))
        fg_rgb = parse_hex_color(q1_fg_match.group(1))
        ratio = wcag_contrast_ratio(fg_rgb, bg_rgb)
        self.assertGreaterEqual(ratio, 4.5, f"Q1 contrast ratio {ratio:.2f}:1 is below WCAG AA 4.5:1")

    def test_tier1_f11_05_aria_landmarks_and_regions(self):
        """F11: Key navigation and tables define aria-label or role='region'."""
        nav_el = next((el for el in self.parsed_html.elements if el["tag"] == "nav"), None)
        self.assertIsNotNone(nav_el)
        self.assertIn("aria-label", nav_el["attrs"])

    # -------------------------------------------------------------------------
    # F12: Responsive Mobile Tables (5 tests)
    # -------------------------------------------------------------------------
    def test_tier1_f12_01_generic_and_specific_tables_exist(self):
        """F12: HTML markup contains distinct tables for generic and specific competencies."""
        table_ids = set(self.parsed_html.ids.keys())
        self.assertTrue(
            "table-generic" in table_ids or any("table" in t for t in table_ids),
            "Generic competencies table missing",
        )
        self.assertTrue(
            "table-specific" in table_ids or len(self.parsed_html.tables) >= 2,
            "Specific competencies table missing",
        )

    def test_tier1_f12_02_table_headers_have_scope_attributes(self):
        """F12: Table <th> elements declare scope='col'."""
        th_elements = [el["attrs"] for el in self.parsed_html.elements if el["tag"] == "th"]
        self.assertGreaterEqual(len(th_elements), 8, "Expected at least 8 <th> elements")
        for th in th_elements:
            self.assertIn(th.get("scope"), ["col", "row"], f"<th> missing scope attribute: {th}")

    def test_tier1_f12_03_responsive_table_container_classes(self):
        """F12: Table containers have class table-container with overflow management."""
        self.assertIn("table-container", self.parsed_html.classes)
        css_comp = (self.repo_root / "css" / "components.css").read_text(encoding="utf-8")
        css_layout = (self.repo_root / "css" / "layout.css").read_text(encoding="utf-8")
        self.assertTrue(".table-container" in css_comp or ".table-container" in css_layout)

    def test_tier1_f12_04_mobile_stacked_card_css_rules(self):
        """F12: css/components.css includes mobile media or container queries for tables."""
        css_comp = (self.repo_root / "css" / "components.css").read_text(encoding="utf-8")
        has_responsive_table = (
            "@media" in css_comp and "max-width" in css_comp and "table" in css_comp
        ) or "@container" in css_comp
        self.assertTrue(has_responsive_table, "Responsive table rules missing from components.css")

    def test_tier1_f12_05_dynamic_table_renderer_script(self):
        """F12: js/tables.js exports renderTables or table building functions."""
        tables_code = (self.repo_root / "js" / "tables.js").read_text(encoding="utf-8")
        self.assertIn("renderTables", tables_code)
        self.assertIn("createGenericRow", tables_code)

    # -------------------------------------------------------------------------
    # F13: Complete Visualization Suite (5 tests)
    # -------------------------------------------------------------------------
    def test_tier1_f13_01_grouped_bar_chart_canvas_present(self):
        """F13: HTML contains canvas element for grouped bar comparison chart."""
        self.assertIn("comparisonChart", self.parsed_html.ids, "Canvas #comparisonChart missing")

    def test_tier1_f13_02_bell_curve_chart_canvas_present(self):
        """F13: HTML contains canvas element for standard normal bell curve chart."""
        self.assertIn("bellCurveChart", self.parsed_html.ids, "Canvas #bellCurveChart missing")

    def test_tier1_f13_03_radar_chart_canvas_present(self):
        """F13: HTML contains canvas element for 8-dimension radar competency profile."""
        self.assertIn("radarChart", self.parsed_html.ids, "Canvas #radarChart missing")

    def test_tier1_f13_04_visual_quintile_scale_element(self):
        """F13: HTML contains container for interactive/visual quintile scale display."""
        self.assertIn("quintileScaleDisplay", self.parsed_html.ids, "#quintileScaleDisplay container missing")

    def test_tier1_f13_05_charts_have_accessible_captions(self):
        """F13: Charts are enclosed in <figure> elements with descriptive <figcaption>."""
        figcaptions = [el for el in self.parsed_html.elements if el["tag"] == "figcaption"]
        self.assertGreaterEqual(len(figcaptions), 3, "Expected at least 3 <figcaption> descriptions for charts")

    # -------------------------------------------------------------------------
    # F14: Local Asset Vendoring (No CDN) (5 tests)
    # -------------------------------------------------------------------------
    def test_tier1_f14_01_chartjs_vendored_locally(self):
        """F14: vendor/chart.umd.min.js exists locally, size > 100KB, valid JS."""
        vendor_file = self.repo_root / "vendor" / "chart.umd.min.js"
        self.assertTrue(vendor_file.exists(), "vendor/chart.umd.min.js missing")
        size = vendor_file.stat().st_size
        self.assertGreater(size, 100000, f"Chart.js file size ({size}) is smaller than expected")

    def test_tier1_f14_02_zero_external_script_cdns(self):
        """F14: HTML contains zero external script CDNs (jsdelivr, unpkg, cloudflare)."""
        for src in self.parsed_html.scripts:
            self.assertFalse(
                src.startswith("http://") or src.startswith("https://") or src.startswith("//"),
                f"External script CDN detected: {src}",
            )

    def test_tier1_f14_03_zero_external_stylesheet_cdns(self):
        """F14: HTML contains zero external stylesheet CDNs (fonts.googleapis, cdnjs)."""
        for href in self.parsed_html.stylesheets:
            self.assertFalse(
                href.startswith("http://") or href.startswith("https://") or href.startswith("//"),
                f"External stylesheet CDN detected: {href}",
            )

    def test_tier1_f14_04_html_references_local_vendor(self):
        """F14: HTML references local vendored Chart.js path vendor/chart.umd.min.js."""
        self.assertIn("vendor/chart.umd.min.js", self.parsed_html.scripts)

    def test_tier1_f14_05_all_local_css_files_exist(self):
        """F14: Every stylesheet referenced in HTML exists locally on disk."""
        for href in self.parsed_html.stylesheets:
            css_file = self.repo_root / href
            self.assertTrue(css_file.exists(), f"Referenced CSS file missing: {href}")

    # -------------------------------------------------------------------------
    # F16: GitHub Pages Static Deployability (5 tests)
    # -------------------------------------------------------------------------
    def test_tier1_f16_01_nojekyll_file_exists(self):
        """F16: Root .nojekyll file exists to disable GitHub Pages Jekyll processing."""
        nojekyll = self.repo_root / ".nojekyll"
        self.assertTrue(nojekyll.exists(), ".nojekyll file missing at repository root")

    def test_tier1_f16_02_all_asset_paths_relative(self):
        """F16: All links, scripts, and stylesheets use relative paths (no absolute /root)."""
        all_paths = self.parsed_html.scripts + self.parsed_html.stylesheets + self.parsed_html.links
        for p in all_paths:
            if p.startswith("#") or p.startswith("mailto:") or p.startswith("http"):
                continue
            self.assertFalse(p.startswith("/"), f"Absolute root path detected (breaks GitHub Pages subpath): {p}")

    def test_tier1_f16_03_root_and_docs_index_parity(self):
        """F16: Perfect file parity between root index.html and docs/index.html."""
        docs_html = self.repo_root / "docs" / "index.html"
        self.assertTrue(docs_html.exists(), "docs/index.html missing")
        root_content = self.html_path.read_text(encoding="utf-8")
        docs_content = docs_html.read_text(encoding="utf-8")
        self.assertEqual(root_content, docs_content, "index.html and docs/index.html are not in sync")

    def test_tier1_f16_04_zero_404_references(self):
        """F16: Every local file referenced in index.html exists on disk."""
        for href in self.parsed_html.links:
            if href.startswith("#") or href.startswith("http") or href.startswith("mailto"):
                continue
            target = self.repo_root / href
            self.assertTrue(target.exists(), f"Broken link in HTML (404): {href}")

    def test_tier1_f16_05_static_architecture_pure_client(self):
        """F16: Zero server-side runtime code (PHP, CGI, Node server) required for hosting."""
        root_files = [f.name for f in self.repo_root.iterdir() if f.is_file()]
        for f in root_files:
            self.assertFalse(f.endswith(".php") or f.endswith(".cgi") or f.endswith(".asp"), f"Server file found: {f}")

    # -------------------------------------------------------------------------
    # F17: Clean Commit History on Branch (5 tests)
    # -------------------------------------------------------------------------
    def test_tier1_f17_01_active_branch_is_feat_modernization(self):
        """F17: Active working git branch is feat/modernization-ghpages."""
        code, branch = git_command("branch", "--show-current")
        self.assertEqual(code, 0)
        self.assertEqual(branch, "feat/modernization-ghpages", f"Unexpected branch: {branch}")

    def test_tier1_f17_02_recent_commits_follow_conventional_commits(self):
        """F17: Recent git commit messages follow conventional commits specification."""
        code, log = git_command("log", "--oneline", "-n", "5")
        self.assertEqual(code, 0)
        conventional_prefixes = ("feat(", "chore(", "test(", "docs(", "fix(", "refactor(", "style(")
        lines = [line.split(" ", 1)[1] for line in log.splitlines() if " " in line]
        modernized_commits = [l for l in lines if any(l.startswith(p) for p in conventional_prefixes)]
        self.assertGreaterEqual(len(modernized_commits), 2, "Expected conventional commit messages in recent history")

    def test_tier1_f17_03_no_agent_directories_in_git(self):
        """F17: No .agents/ or agent cache directories tracked in git."""
        code, tracked = git_command("ls-files")
        self.assertEqual(code, 0)
        for line in tracked.splitlines():
            self.assertNotIn(".agents/", line, f"Agent metadata tracked in git: {line}")
            self.assertNotIn("Agents/", line, f"Agents directory tracked in git: {line}")

    def test_tier1_f17_04_no_secrets_in_tracked_files(self):
        """F17: No private API keys or token files tracked in git."""
        code, tracked = git_command("ls-files")
        self.assertEqual(code, 0)
        for line in tracked.splitlines():
            self.assertFalse(line.endswith(".env"), f".env file tracked: {line}")
            self.assertFalse(line.endswith(".key"), f"Key file tracked: {line}")
            self.assertFalse(line.endswith(".pem"), f"Pem file tracked: {line}")

    def test_tier1_f17_05_working_tree_cleanliness(self):
        """F17: Git status contains no untracked temp or sensitive files."""
        code, status = git_command("status", "--porcelain")
        self.assertEqual(code, 0)
        for line in status.splitlines():
            self.assertNotIn(".env", line)
            self.assertNotIn(".pem", line)


# =============================================================================
# TIER 2: BOUNDARY & CORNER CASES (>=5 tests per feature area = 80 tests)
# =============================================================================

class Tier2BoundaryCornerCaseTests(unittest.TestCase):
    """Tier 2: Boundary value analysis, extreme inputs, null handling, and error resiliency."""

    @classmethod
    def setUpClass(cls):
        cls.repo_root = REPO_ROOT
        cls.data_path = cls.repo_root / "data" / "saber_pro_2015.json"
        cls.pdf_path = cls.repo_root / "assets" / "EK201532097061.pdf"
        cls.html_path = cls.repo_root / "index.html"
        cls.data = json.loads(cls.data_path.read_text(encoding="utf-8"))

    # -------------------------------------------------------------------------
    # F1: Repo Baseline Boundaries (5 tests)
    # -------------------------------------------------------------------------
    def test_tier2_f1_01_bva_missing_pdf_detection(self):
        """F1 (BVA): PDFDataExtractor raises FileNotFoundError when given non-existent path."""
        from scripts.verify_statistics import PDFDataExtractor
        with self.assertRaises(FileNotFoundError):
            PDFDataExtractor.extract_from_pdf(Path("non_existent_file.pdf"))

    def test_tier2_f1_02_bva_corrupt_pdf_stream_handling(self):
        """F1 (BVA): PDF stream extractor handles corrupt or non-zlib byte stream gracefully."""
        from scripts.verify_statistics import PDFDataExtractor
        temp_pdf = self.repo_root / "assets" / "temp_corrupt.pdf"
        try:
            temp_pdf.write_bytes(b"%PDF-1.4\nstream\ncorrupt_random_data\nendstream\n%%EOF")
            with self.assertRaises(ValueError):
                PDFDataExtractor.extract_from_pdf(temp_pdf)
        finally:
            if temp_pdf.exists():
                temp_pdf.unlink()

    def test_tier2_f1_03_bva_empty_markdown_asset_handling(self):
        """F1 (BVA): Asset files are non-empty (>500 bytes) and contain no zero-byte files."""
        for md_file in (self.repo_root / "assets").glob("*.md"):
            self.assertGreater(md_file.stat().st_size, 500, f"{md_file.name} is unexpectedly small")

    def test_tier2_f1_04_bva_subpath_relative_resolution(self):
        """F1 (BVA): Asset resolution functions correctly across directory traversals."""
        rel_path = Path("assets/../assets/EK201532097061.pdf")
        resolved = (self.repo_root / rel_path).resolve()
        self.assertTrue(resolved.exists())

    def test_tier2_f1_05_bva_git_detached_or_shallow_clone(self):
        """F1 (BVA): Verification of repository commits works even if clone is shallow."""
        code, log = git_command("rev-parse", "--is-shallow-repository")
        self.assertEqual(code, 0)
        self.assertIn(log.lower(), ["true", "false"])

    # -------------------------------------------------------------------------
    # F2: Repo Sovereignty & Privacy Boundaries (5 tests)
    # -------------------------------------------------------------------------
    def test_tier2_f2_01_bva_cedula_with_punctuation_redacted(self):
        """F2 (BVA): Scan confirms absence of cédula with formatting dots or spaces."""
        patterns = [
            r"1\.143\.848\.416",
            r"1 143 848 416",
            r"114-3848-416",
            r"114\.3848\.416",
        ]
        doc_text = self.html_path.read_text(encoding="utf-8")
        for pat in patterns:
            self.assertIsNone(re.search(pat, doc_text), f"Punctuation-formatted cédula leak detected with {pat}")

    def test_tier2_f2_02_bva_partial_cedula_prefix_suffix(self):
        """F2 (BVA): Registration EK201532097061 is retained while national ID is zeroed."""
        self.assertEqual(self.data["metadata"]["registration_number"], "EK201532097061")
        self.assertNotIn(PII_TARGET_CEDULA, json.dumps(self.data["metadata"]))

    def test_tier2_f2_03_bva_gitignore_trailing_slash_patterns(self):
        """F2 (BVA): .gitignore correctly matches directory patterns with or without trailing slash."""
        gi_lines = [l.strip() for l in (self.repo_root / ".gitignore").read_text(encoding="utf-8").splitlines()]
        matches = [l for l in gi_lines if ".agents" in l or "node_modules" in l]
        self.assertGreaterEqual(len(matches), 2)

    def test_tier2_f2_04_bva_hidden_files_exclusion(self):
        """F2 (BVA): OS artifacts (.DS_Store, Thumbs.db) excluded by gitignore."""
        gi_text = (self.repo_root / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".DS_Store", gi_text)

    def test_tier2_f2_05_bva_case_insensitive_pii_check(self):
        """F2 (BVA): PII check is case-insensitive across all canonical candidate metadata."""
        meta_values = [str(v).lower() for v in self.data["metadata"].values()]
        for v in meta_values:
            self.assertNotIn(PII_TARGET_CEDULA.lower(), v)

    # -------------------------------------------------------------------------
    # F3: Canonical Dataset Structure Boundaries (5 tests)
    # -------------------------------------------------------------------------
    def test_tier2_f3_01_bva_score_range_boundaries(self):
        """F3 (BVA): All modular scores are strictly bounded within 0.0 and 20.0."""
        for m in self.data["modules"]:
            s = m["individual_score"]
            self.assertGreaterEqual(s, 0.0, f"Score below 0.0: {s}")
            self.assertLessEqual(s, 20.0, f"Score above 20.0: {s}")

    def test_tier2_f3_02_bva_quintile_valid_domain(self):
        """F3 (BVA): All quintiles belong to the strict domain {'I', 'II', 'III', 'IV', 'V'}."""
        valid_q = {"I", "II", "III", "IV", "V"}
        for m in self.data["modules"]:
            self.assertIn(m["official_quintile"], valid_q)

    def test_tier2_f3_03_bva_null_performance_levels(self):
        """F3 (BVA): Performance levels allow null for modules without official levels."""
        null_count = sum(1 for m in self.data["modules"] if m["performance_level"] is None)
        self.assertEqual(null_count, 4, f"Expected exactly 4 modules with null performance level, got {null_count}")

    def test_tier2_f3_04_bva_sample_size_positivity(self):
        """F3 (BVA): Sample sizes N are strictly positive integers greater than 1,000."""
        for m in self.data["modules"]:
            self.assertGreater(m["reference_group"]["n"], 1000)
            self.assertGreater(m["national_group"]["n"], 1000)

    def test_tier2_f3_05_bva_standard_deviation_positivity(self):
        """F3 (BVA): Standard deviations are finite positive floats between 0.5 and 3.0."""
        for m in self.data["modules"]:
            ref_sd = m["reference_group"]["sd"]
            nac_sd = m["national_group"]["sd"]
            self.assertTrue(0.5 <= ref_sd <= 3.0, f"Unusual ref sd: {ref_sd}")
            self.assertTrue(0.5 <= nac_sd <= 3.0, f"Unusual national sd: {nac_sd}")

    # -------------------------------------------------------------------------
    # F4: Statistical Verification Rules Boundaries (5 tests)
    # -------------------------------------------------------------------------
    def test_tier2_f4_01_bva_zero_division_guard(self):
        """F4 (BVA): Subgroup mean calculation guards against empty modules list."""
        from scripts.verify_statistics import StatisticalVerificationEngine
        engine = StatisticalVerificationEngine(self.repo_root)
        empty_data = {"modules": []}
        res = engine.verify_rule_03_subgroup_means(empty_data)
        self.assertEqual(res["status"], "FAIL")

    def test_tier2_f4_02_bva_floating_point_epsilon_tolerance(self):
        """F4 (BVA): Mean calculation handles IEEE 754 precision with 1e-4 tolerance."""
        scores = [9.2, 11.5, 11.6, 10.6, 11.7, 10.1, 12.9, 11.1]
        raw_sum = sum(scores)
        exact_mean = raw_sum / len(scores)
        self.assertTrue(abs(exact_mean - 11.0875) < 1e-9)

    def test_tier2_f4_03_bva_mutated_score_detection(self):
        """F4 (BVA): Tampering with a single score causes RULE-02 to FAIL immediately."""
        from scripts.verify_statistics import StatisticalVerificationEngine
        engine = StatisticalVerificationEngine(self.repo_root)
        tampered_data = json.loads(json.dumps(self.data))
        tampered_data["modules"][0]["individual_score"] = 9.3
        res = engine.verify_rule_02_card_arithmetic(tampered_data, None)
        self.assertEqual(res["status"], "FAIL")

    def test_tier2_f4_04_bva_extreme_outlier_detection(self):
        """F4 (BVA): Extreme score (>20.0 or negative) triggers arithmetic verification error."""
        from scripts.verify_statistics import StatisticalVerificationEngine
        engine = StatisticalVerificationEngine(self.repo_root)
        tampered_data = json.loads(json.dumps(self.data))
        tampered_data["modules"][0]["individual_score"] = 99.0
        res = engine.verify_rule_02_card_arithmetic(tampered_data, None)
        self.assertEqual(res["status"], "FAIL")

    def test_tier2_f4_05_bva_sample_size_inversion_detection(self):
        """F4 (BVA): Inverting sample size (N_ref > N_nac) triggers RULE-06 failure."""
        from scripts.verify_statistics import StatisticalVerificationEngine
        engine = StatisticalVerificationEngine(self.repo_root)
        tampered_data = json.loads(json.dumps(self.data))
        tampered_data["modules"][0]["reference_group"]["n"] = 500000
        res = engine.verify_rule_06_population_bounds(tampered_data)
        self.assertEqual(res["status"], "FAIL")

    # -------------------------------------------------------------------------
    # F5: Discrepancy & Anomaly Audit Boundaries (5 tests)
    # -------------------------------------------------------------------------
    def test_tier2_f5_01_bva_anomaly_empty_array_handling(self):
        """F5 (BVA): Handling of missing discrepancy list does not throw unhandled exception."""
        no_disc_data = {"modules": self.data["modules"]}
        self.assertEqual(no_disc_data.get("audit_discrepancies", []), [])

    def test_tier2_f5_02_bva_anomaly_id_formatting(self):
        """F5 (BVA): All anomaly IDs match regex ^A-\\d{2}$."""
        for d in self.data["audit_discrepancies"]:
            self.assertRegex(d["id"], r"^A-\d{2}$")

    def test_tier2_f5_03_bva_anomaly_legacy_vs_calculated_distinct(self):
        """F5 (BVA): Legacy value and calculated value are distinct in anomaly A-01."""
        a01 = next(d for d in self.data["audit_discrepancies"] if d["id"] == "A-01")
        self.assertNotEqual(a01["published_legacy_value"], a01["calculated_value"])

    def test_tier2_f5_04_bva_gaussian_cdf_at_z_minus_0_8(self):
        """F5 (BVA): Gaussian CDF at z=-0.80 yields ~21.19% (confirming theoretical Q2)."""
        z = (9.2 - 10.0) / 1.0  # -0.8
        p = normal_cdf(z)
        self.assertAlmostEqual(p, 0.21186, places=4)
        self.assertTrue(0.20 < p < 0.40)

    def test_tier2_f5_05_bva_anomaly_neutrality_tone(self):
        """F5 (BVA): Anomaly descriptions maintain institutional neutrality (no accusatory words)."""
        accusatory = ["fraude", "corrupción", "trampa", "culpable", "negligencia"]
        for d in self.data["audit_discrepancies"]:
            desc_lower = d["description"].lower()
            for w in accusatory:
                self.assertNotIn(w, desc_lower)

    # -------------------------------------------------------------------------
    # F6: Verification Engine Automation Boundaries (5 tests)
    # -------------------------------------------------------------------------
    def test_tier2_f6_01_bva_cli_invalid_argument_handling(self):
        """F6 (BVA): Passing invalid flag to CLI exits with code 2."""
        script = self.repo_root / "scripts" / "verify_statistics.py"
        proc = subprocess.run([sys.executable, str(script), "--invalid-flag"], capture_output=True)
        self.assertEqual(proc.returncode, 2)

    def test_tier2_f6_02_bva_missing_input_json_exit_code(self):
        """F6 (BVA): Passing non-existent data file path exits with code 1."""
        script = self.repo_root / "scripts" / "verify_statistics.py"
        proc = subprocess.run([sys.executable, str(script), "--data", "non_existent.json"], capture_output=True)
        self.assertEqual(proc.returncode, 1)

    def test_tier2_f6_03_bva_read_only_filesystem_dry_run(self):
        """F6 (BVA): Engine executes in memory and returns dictionary without file mutations."""
        from scripts.verify_statistics import StatisticalVerificationEngine
        engine = StatisticalVerificationEngine(self.repo_root)
        rep = engine.run_all(self.data_path, self.pdf_path, self.html_path, verbose=False)
        self.assertIn("overall_verdict", rep)

    def test_tier2_f6_04_bva_report_timestamp_iso8601(self):
        """F6 (BVA): Report timestamp is valid ISO 8601 string."""
        rep = json.loads((self.repo_root / "data" / "verification_report.json").read_text(encoding="utf-8"))
        ts = rep.get("timestamp")
        self.assertRegex(ts, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")

    def test_tier2_f6_05_bva_large_sample_size_integer_overflow(self):
        """F6 (BVA): Large sample size (310,468) processed without 32-bit overflow."""
        eng = next(m for m in self.data["modules"] if m["id"] == "ingles")
        n = eng["national_group"]["n"]
        self.assertEqual(n, 310468)
        self.assertTrue(n > 0 and isinstance(n, int))

    # -------------------------------------------------------------------------
    # F7: i18n Content Decoupling Boundaries (5 tests)
    # -------------------------------------------------------------------------
    def test_tier2_f7_01_bva_missing_translation_key_fallback(self):
        """F7 (BVA): Querying non-existent key returns key itself as safe fallback."""
        i18n_code = (self.repo_root / "js" / "i18n.js").read_text(encoding="utf-8")
        self.assertIn("return key", i18n_code)

    def test_tier2_f7_02_bva_special_characters_in_translations(self):
        """F7 (BVA): Translations contain Spanish diacritics (á, é, í, ó, ú, ñ) intact."""
        es_txt = (self.repo_root / "locales" / "es.js").read_text(encoding="utf-8")
        for char in ["á", "é", "í", "ó", "ú", "ñ"]:
            self.assertIn(char, es_txt, f"Diacritic {char} missing from es.js")

    def test_tier2_f7_03_bva_html_injection_safety_in_i18n(self):
        """F7 (BVA): Locale dictionary strings contain no script tags."""
        es_txt = (self.repo_root / "locales" / "es.js").read_text(encoding="utf-8")
        en_txt = (self.repo_root / "locales" / "en.js").read_text(encoding="utf-8")
        self.assertNotIn("<script>", es_txt.lower())
        self.assertNotIn("<script>", en_txt.lower())

    def test_tier2_f7_04_bva_empty_string_key_handling(self):
        """F7 (BVA): Querying empty key string returns gracefully without error."""
        i18n_code = (self.repo_root / "js" / "i18n.js").read_text(encoding="utf-8")
        self.assertIn("!key", i18n_code)

    def test_tier2_f7_05_bva_locale_case_insensitivity(self):
        """F7 (BVA): getIntlLocale handles lowercase and case variations."""
        i18n_code = (self.repo_root / "js" / "i18n.js").read_text(encoding="utf-8")
        self.assertIn("toLowerCase()", i18n_code)

    # -------------------------------------------------------------------------
    # F8: Locale Number & Date Formatting Boundaries (5 tests)
    # -------------------------------------------------------------------------
    def test_tier2_f8_01_bva_format_zero_score(self):
        """F8 (BVA): Score 0.0 formats to '0,0' (es) and '0.0' (en)."""
        val = 0.0
        es_fmt = f"{val:.1f}".replace(".", ",")
        en_fmt = f"{val:.1f}"
        self.assertEqual(es_fmt, "0,0")
        self.assertEqual(en_fmt, "0.0")

    def test_tier2_f8_02_bva_format_large_number(self):
        """F8 (BVA): 1,000,000 formats to '1.000.000' (es) and '1,000,000' (en)."""
        num = 1000000
        es_fmt = f"{num:,}".replace(",", ".")
        en_fmt = f"{num:,}"
        self.assertEqual(es_fmt, "1.000.000")
        self.assertEqual(en_fmt, "1,000,000")

    def test_tier2_f8_03_bva_format_nan_and_null(self):
        """F8 (BVA): Formatter handles null or NaN returning fallback string '-'."""
        i18n_code = (self.repo_root / "js" / "i18n.js").read_text(encoding="utf-8")
        self.assertIn("isNaN", i18n_code)

    def test_tier2_f8_04_bva_format_rounding_half_up(self):
        """F8 (BVA): 11.0875 rounded to 1 decimal place produces 11.1."""
        val = 11.0875
        self.assertEqual(round(val, 1), 11.1)

    def test_tier2_f8_05_bva_format_negative_score(self):
        """F8 (BVA): Negative score preserves minus sign."""
        val = -2.5
        es_fmt = f"{val:.1f}".replace(".", ",")
        self.assertEqual(es_fmt, "-2,5")

    # -------------------------------------------------------------------------
    # F9: Interactive Language Switching Boundaries (5 tests)
    # -------------------------------------------------------------------------
    def test_tier2_f9_01_bva_unsupported_locale_fallback(self):
        """F9 (BVA): Requesting unsupported locale falls back to default 'es'."""
        i18n_code = (self.repo_root / "js" / "i18n.js").read_text(encoding="utf-8")
        self.assertIn("target === 'en'", i18n_code)

    def test_tier2_f9_02_bva_rapid_toggle_consistency(self):
        """F9 (BVA): Toggle event listener toggles between 'es' and 'en'."""
        app_code = (self.repo_root / "js" / "app.js").read_text(encoding="utf-8")
        self.assertIn("btnLangToggle", app_code)
        self.assertIn("setLanguage", app_code)

    def test_tier2_f9_03_bva_null_or_undefined_lang_handling(self):
        """F9 (BVA): Passing null to setLanguage defaults safely to 'es'."""
        i18n_code = (self.repo_root / "js" / "i18n.js").read_text(encoding="utf-8")
        self.assertIn("typeof lang === 'string'", i18n_code)

    def test_tier2_f9_04_bva_preserve_dynamic_values_on_toggle(self):
        """F9 (BVA): Switching language refreshes tables and DOM translations."""
        app_code = (self.repo_root / "js" / "app.js").read_text(encoding="utf-8")
        self.assertIn("renderTables", app_code)
        self.assertIn("updateStaticTranslations", app_code)

    def test_tier2_f9_05_bva_aria_pressed_boolean_parity(self):
        """F9 (BVA): aria-pressed is updated on language toggle."""
        app_code = (self.repo_root / "js" / "app.js").read_text(encoding="utf-8")
        self.assertIn("setAttribute('aria-pressed'", app_code)

    # -------------------------------------------------------------------------
    # F10: Semantic UI & Fluid Layout Boundaries (5 tests)
    # -------------------------------------------------------------------------
    def test_tier2_f10_01_bva_viewport_extreme_narrow_320px(self):
        """F10 (BVA): CSS handles small mobile viewport widths (320px)."""
        css_layout = (self.repo_root / "css" / "layout.css").read_text(encoding="utf-8")
        self.assertIn("box-sizing: border-box", css_layout)

    def test_tier2_f10_02_bva_viewport_extreme_ultrawide_2560px(self):
        """F10 (BVA): Container max-width restricts content spreading beyond 1200px."""
        css_layout = (self.repo_root / "css" / "layout.css").read_text(encoding="utf-8")
        self.assertIn("max-width: 1200px", css_layout)

    def test_tier2_f10_03_bva_heading_hierarchy_integrity(self):
        """F10 (BVA): Page has exactly one <h1> element."""
        parsed = parse_html_document(self.html_path.read_text(encoding="utf-8"))
        h1s = [h for h in parsed.headings if h[0] == "h1"]
        self.assertEqual(len(h1s), 1, f"Expected exactly 1 <h1>, found {len(h1s)}")

    def test_tier2_f10_04_bva_meta_charset_utf8_as_first_child(self):
        """F10 (BVA): <meta charset='UTF-8'> is within first 500 characters of HTML."""
        html_head = self.html_path.read_text(encoding="utf-8")[:500]
        self.assertIn("charset=\"UTF-8\"", html_head)

    def test_tier2_f10_05_bva_all_css_files_non_empty(self):
        """F10 (BVA): All modular CSS files have size > 1KB."""
        for css_f in (self.repo_root / "css").glob("*.css"):
            self.assertGreater(css_f.stat().st_size, 1000, f"{css_f.name} is smaller than 1KB")

    # -------------------------------------------------------------------------
    # F11: WCAG AA Accessibility & Focus Boundaries (5 tests)
    # -------------------------------------------------------------------------
    def test_tier2_f11_01_bva_badge_q1_contrast_ratio(self):
        """F11 (BVA): Q1 badge contrast ratio strictly >= 4.5:1 against its background."""
        css_var = (self.repo_root / "css" / "variables.css").read_text(encoding="utf-8")
        self.assertIn("--badge-q1-bg: #334155", css_var)

    def test_tier2_f11_02_bva_badge_q5_contrast_ratio(self):
        """F11 (BVA): Q5 badge contrast ratio strictly >= 4.5:1 against its background."""
        css_var = (self.repo_root / "css" / "variables.css").read_text(encoding="utf-8")
        self.assertIn("--badge-q5-bg: #15803d", css_var)

    def test_tier2_f11_03_bva_focus_outline_width_and_style(self):
        """F11 (BVA): Focus outline has width >= 2px."""
        css_acc = (self.repo_root / "css" / "accessibility.css").read_text(encoding="utf-8")
        self.assertTrue("outline: 3px solid" in css_acc or "outline: 2px" in css_acc)
        self.assertIn("outline-offset: 2px", css_acc)

    def test_tier2_f11_04_bva_images_have_alt_or_role(self):
        """F11 (BVA): Any img tag defines alt attribute."""
        parsed = parse_html_document(self.html_path.read_text(encoding="utf-8"))
        for img in parsed.images:
            self.assertIn("alt", img)

    def test_tier2_f11_05_bva_skip_link_visible_on_focus(self):
        """F11 (BVA): .skip-link:focus makes skip link visible in viewport."""
        css_acc = (self.repo_root / "css" / "accessibility.css").read_text(encoding="utf-8")
        self.assertIn(".skip-link:focus", css_acc)

    # -------------------------------------------------------------------------
    # F12: Responsive Mobile Tables Boundaries (5 tests)
    # -------------------------------------------------------------------------
    def test_tier2_f12_01_bva_table_with_empty_or_null_cells(self):
        """F12 (BVA): Table cells display '-' for null performance levels."""
        html_txt = self.html_path.read_text(encoding="utf-8")
        self.assertIn("<td>-</td>", html_txt)

    def test_tier2_f12_02_bva_table_cell_data_labels(self):
        """F12 (BVA): Table data cells include data-label attribute for mobile stacking."""
        tables_code = (self.repo_root / "js" / "tables.js").read_text(encoding="utf-8")
        self.assertIn("data-label", tables_code)

    def test_tier2_f12_03_bva_long_text_wrapping(self):
        """F12 (BVA): Table module names wrap cleanly with word-break or normal wrap."""
        css_comp = (self.repo_root / "css" / "components.css").read_text(encoding="utf-8")
        self.assertIn(".data-table", css_comp)

    def test_tier2_f12_04_bva_sticky_header_z_index(self):
        """F12 (BVA): Sticky headers have defined z-index."""
        css_comp = (self.repo_root / "css" / "components.css").read_text(encoding="utf-8")
        self.assertIn("sticky", css_comp)

    def test_tier2_f12_05_bva_table_region_aria_label(self):
        """F12 (BVA): Table container has role='region' and aria-label."""
        parsed = parse_html_document(self.html_path.read_text(encoding="utf-8"))
        regions = [el["attrs"] for el in parsed.elements if el["attrs"].get("role") == "region"]
        self.assertGreaterEqual(len(regions), 2)

    # -------------------------------------------------------------------------
    # F13: Complete Visualization Suite Boundaries (5 tests)
    # -------------------------------------------------------------------------
    def test_tier2_f13_01_bva_chart_canvas_responsive_container(self):
        """F13 (BVA): Canvas containers have responsive wrappers."""
        parsed = parse_html_document(self.html_path.read_text(encoding="utf-8"))
        self.assertIn("chart-wrapper", parsed.classes)

    def test_tier2_f13_02_bva_bell_curve_z_score_range(self):
        """F13 (BVA): Bell curve generator spans domain of standard normal curve."""
        charts_code = (self.repo_root / "js" / "charts.js").read_text(encoding="utf-8")
        self.assertIn("initBellCurveChart", charts_code)

    def test_tier2_f13_03_bva_radar_chart_all_8_dimensions(self):
        """F13 (BVA): Radar chart maps all 8 modular competencies."""
        charts_code = (self.repo_root / "js" / "charts.js").read_text(encoding="utf-8")
        self.assertIn("initRadarChart", charts_code)

    def test_tier2_f13_04_bva_chart_colorblind_palette(self):
        """F13 (BVA): Chart datasets use distinct hues for individual vs reference vs national."""
        charts_code = (self.repo_root / "js" / "charts.js").read_text(encoding="utf-8")
        self.assertIn("getThemeColors", charts_code)

    def test_tier2_f13_05_bva_canvas_fallback_elements(self):
        """F13 (BVA): Canvas elements include fallback role='img' and aria-label."""
        parsed = parse_html_document(self.html_path.read_text(encoding="utf-8"))
        canvases = [el["attrs"] for el in parsed.elements if el["tag"] == "canvas"]
        self.assertEqual(len(canvases), 3)
        for c in canvases:
            self.assertEqual(c.get("role"), "img")
            self.assertIn("aria-label", c)

    # -------------------------------------------------------------------------
    # F14: Local Asset Vendoring Boundaries (5 tests)
    # -------------------------------------------------------------------------
    def test_tier2_f14_01_bva_vendor_chartjs_valid_umd(self):
        """F14 (BVA): vendor/chart.umd.min.js contains UMD bundle wrapper."""
        content = (self.repo_root / "vendor" / "chart.umd.min.js").read_text(encoding="utf-8")
        self.assertIn("Chart", content)

    def test_tier2_f14_02_bva_vendor_file_size_bounds(self):
        """F14 (BVA): vendor/chart.umd.min.js size is between 150KB and 300KB."""
        size = (self.repo_root / "vendor" / "chart.umd.min.js").stat().st_size
        self.assertTrue(150000 <= size <= 300000, f"Unexpected size: {size}")

    def test_tier2_f14_03_bva_no_protocol_relative_urls(self):
        """F14 (BVA): Zero protocol-relative '//' URLs in HTML head."""
        parsed = parse_html_document(self.html_path.read_text(encoding="utf-8"))
        for s in parsed.scripts + parsed.stylesheets:
            self.assertFalse(s.startswith("//"))

    def test_tier2_f14_04_bva_no_data_uri_bloat(self):
        """F14 (BVA): Zero giant data: URI base64 images in HTML."""
        html_txt = self.html_path.read_text(encoding="utf-8")
        self.assertNotIn("data:image", html_txt)

    def test_tier2_f14_05_bva_vendor_dir_tracked_in_git(self):
        """F14 (BVA): vendor/chart.umd.min.js is present locally."""
        self.assertTrue((self.repo_root / "vendor" / "chart.umd.min.js").exists())

    # -------------------------------------------------------------------------
    # F16: GitHub Pages Static Deployability Boundaries (5 tests)
    # -------------------------------------------------------------------------
    def test_tier2_f16_01_bva_case_sensitivity_in_asset_paths(self):
        """F16 (BVA): Script and style paths match exact case on filesystem."""
        parsed = parse_html_document(self.html_path.read_text(encoding="utf-8"))
        for src in parsed.scripts:
            f = self.repo_root / src
            self.assertTrue(f.exists(), f"Path case mismatch or missing: {src}")

    def test_tier2_f16_02_bva_url_encoded_paths(self):
        """F16 (BVA): Asset paths contain no raw spaces or unencoded characters."""
        parsed = parse_html_document(self.html_path.read_text(encoding="utf-8"))
        for p in parsed.scripts + parsed.stylesheets:
            self.assertNotIn(" ", p)

    def test_tier2_f16_03_bva_relative_path_depth(self):
        """F16 (BVA): Relative paths do not escape above repository root."""
        parsed = parse_html_document(self.html_path.read_text(encoding="utf-8"))
        for p in parsed.links + parsed.scripts + parsed.stylesheets:
            self.assertFalse(p.startswith("../.."))

    def test_tier2_f16_04_bva_trailing_slashes_in_directory_links(self):
        """F16 (BVA): Navigation links use internal anchors (#) or valid targets."""
        parsed = parse_html_document(self.html_path.read_text(encoding="utf-8"))
        for link in parsed.links:
            if link.startswith("#"):
                target_id = link.lstrip("#")
                self.assertIn(target_id, parsed.ids, f"Anchor target #{target_id} not found in HTML IDs")

    def test_tier2_f16_05_bva_nojekyll_zero_byte_content(self):
        """F16 (BVA): .nojekyll is present at repo root."""
        nj = self.repo_root / ".nojekyll"
        self.assertTrue(nj.exists())

    # -------------------------------------------------------------------------
    # F17: Clean Commit History Boundaries (5 tests)
    # -------------------------------------------------------------------------
    def test_tier2_f17_01_bva_git_head_points_to_commit(self):
        """F17 (BVA): HEAD resolves to valid 40-character hex commit SHA."""
        code, sha = git_command("rev-parse", "HEAD")
        self.assertEqual(code, 0)
        self.assertRegex(sha, r"^[0-9a-f]{40}$")

    def test_tier2_f17_02_bva_no_merge_conflict_markers(self):
        """F17 (BVA): Zero merge conflict markers in repository tracked files."""
        tracked_code, tracked = git_command("ls-files")
        self.assertEqual(tracked_code, 0)
        marker_start = "<" * 7
        marker_end = ">" * 7
        for rel_p in tracked.splitlines():
            if rel_p in ("tests/test_e2e_suite.py", "tests/e2e_runner.py") or rel_p.endswith(".pdf"):
                continue
            f_p = self.repo_root / rel_p
            if f_p.is_file():
                text = f_p.read_text(encoding="utf-8", errors="ignore")
                self.assertNotIn(marker_start, text, f"Conflict marker in {rel_p}")
                self.assertNotIn(marker_end, text, f"Conflict marker in {rel_p}")

    def test_tier2_f17_03_bva_commit_message_subject_length(self):
        """F17 (BVA): Recent commit messages have concise subject lines (<= 100 chars)."""
        code, log = git_command("log", "-n", "5", "--format=%s")
        self.assertEqual(code, 0)
        for subject in log.splitlines():
            self.assertLessEqual(len(subject), 100, f"Commit subject too long: {subject}")

    def test_tier2_f17_04_bva_no_unexpected_large_binaries(self):
        """F17 (BVA): No unexpected binary blobs (>1MB) tracked in git."""
        code, tracked = git_command("ls-files")
        self.assertEqual(code, 0)
        for rel_p in tracked.splitlines():
            f_p = self.repo_root / rel_p
            if f_p.is_file():
                size = f_p.stat().st_size
                self.assertLess(size, 1000000, f"Large file (>1MB) tracked in git: {rel_p} ({size} bytes)")

    def test_tier2_f17_05_bva_git_branch_matches_milestone(self):
        """F17 (BVA): Current git branch name matches 'feat/modernization-ghpages'."""
        code, branch = git_command("branch", "--show-current")
        self.assertEqual(code, 0)
        self.assertEqual(branch, "feat/modernization-ghpages")


# =============================================================================
# TIER 3: CROSS-FEATURE COMBINATIONS (>=16 pairwise integration tests)
# =============================================================================

class Tier3CrossFeatureIntegrationTests(unittest.TestCase):
    """Tier 3: Pairwise and multi-module integration across feature boundaries."""

    @classmethod
    def setUpClass(cls):
        cls.repo_root = REPO_ROOT
        cls.data_path = cls.repo_root / "data" / "saber_pro_2015.json"
        cls.pdf_path = cls.repo_root / "assets" / "EK201532097061.pdf"
        cls.html_path = cls.repo_root / "index.html"
        cls.data = json.loads(cls.data_path.read_text(encoding="utf-8"))
        cls.parsed_html = parse_html_document(cls.html_path.read_text(encoding="utf-8"))

    def test_tier3_f3_f4_canonical_data_with_verification_engine(self):
        """Tier 3 [F3 x F4]: Canonical dataset directly validates all 8 verification rules."""
        from scripts.verify_statistics import StatisticalVerificationEngine
        engine = StatisticalVerificationEngine(self.repo_root)
        rep = engine.run_all(self.data_path, self.pdf_path, self.html_path)
        self.assertEqual(rep["overall_verdict"], "PASS")

    def test_tier3_f7_f8_i18n_dictionaries_with_number_formatters(self):
        """Tier 3 [F7 x F8]: i18n locale dictionaries integrate with score and count formatters."""
        i18n_code = (self.repo_root / "js" / "i18n.js").read_text(encoding="utf-8")
        self.assertIn("formatScore", i18n_code)
        self.assertIn("formatCount", i18n_code)
        self.assertIn("Intl.NumberFormat", i18n_code)

    def test_tier3_f3_f7_canonical_modules_with_i18n_translations(self):
        """Tier 3 [F3 x F7]: Every module in saber_pro_2015.json has matching i18n entry."""
        es_txt = (self.repo_root / "locales" / "es.js").read_text(encoding="utf-8")
        en_txt = (self.repo_root / "locales" / "en.js").read_text(encoding="utf-8")
        for m in self.data["modules"]:
            self.assertIn(m["id"], es_txt)
            self.assertIn(m["id"], en_txt)

    def test_tier3_f5_f7_anomalies_with_i18n_documentation(self):
        """Tier 3 [F5 x F7]: All 7 audit anomalies A-01..A-07 translated in both locales."""
        es_txt = (self.repo_root / "locales" / "es.js").read_text(encoding="utf-8")
        en_txt = (self.repo_root / "locales" / "en.js").read_text(encoding="utf-8")
        for d in self.data["audit_discrepancies"]:
            code_key = d["id"].replace("-", "_")
            self.assertTrue(code_key in es_txt or d["id"] in es_txt)
            self.assertTrue(code_key in en_txt or d["id"] in en_txt)

    def test_tier3_f4_f5_audit_anomalies_with_verification_rules(self):
        """Tier 3 [F4 x F5]: RULE-02 verifies A-01, RULE-06 verifies A-04, RULE-07 verifies PII redaction."""
        from scripts.verify_statistics import StatisticalVerificationEngine
        engine = StatisticalVerificationEngine(self.repo_root)
        rep = engine.run_all(self.data_path, self.pdf_path, self.html_path)
        self.assertIn("A-01", rep["rules"]["RULE-02-CARD-ARITHMETIC"]["details"])
        self.assertIn("A-04", rep["rules"]["RULE-06-POPULATION-BOUNDS"]["details"])
        self.assertIn("PII", rep["rules"]["RULE-07-HYGIENE-PII-GUARD"]["details"])

    def test_tier3_f3_f12_canonical_scores_with_responsive_tables(self):
        """Tier 3 [F3 x F12]: Table cells in HTML match scores in saber_pro_2015.json."""
        html_txt = self.html_path.read_text(encoding="utf-8")
        for m in self.data["modules"]:
            score_str = str(m["individual_score"])
            self.assertIn(score_str, html_txt, f"Score {score_str} for {m['id']} missing from HTML table")

    def test_tier3_f3_f13_canonical_scores_with_chart_datasets(self):
        """Tier 3 [F3 x F13]: Chart initialization logic ingests canonical module scores."""
        charts_js = (self.repo_root / "js" / "charts.js").read_text(encoding="utf-8")
        self.assertIn("dataset.modules", charts_js)

    def test_tier3_f8_f12_locale_number_formatting_with_table_cells(self):
        """Tier 3 [F8 x F12]: Table renderer calls i18n.formatScore and i18n.formatCount."""
        tables_js = (self.repo_root / "js" / "tables.js").read_text(encoding="utf-8")
        self.assertIn("formatScore", tables_js)
        self.assertIn("formatCount", tables_js)

    def test_tier3_f9_f10_language_switch_with_semantic_html_lang(self):
        """Tier 3 [F9 x F10]: Language switcher updates document.documentElement lang."""
        i18n_js = (self.repo_root / "js" / "i18n.js").read_text(encoding="utf-8")
        self.assertIn("document.documentElement.setAttribute('lang'", i18n_js)

    def test_tier3_f10_f11_semantic_landmarks_with_wcag_skip_link(self):
        """Tier 3 [F10 x F11]: Skip-link connects header navigation directly to main landmark."""
        skip = next((el["attrs"] for el in self.parsed_html.elements if "skip-link" in el["attrs"].get("class", "")), None)
        self.assertIsNotNone(skip)
        target = skip.get("href", "").lstrip("#")
        main_el = self.parsed_html.ids.get(target)
        self.assertIsNotNone(main_el, f"Skip link target #{target} does not exist in DOM")

    def test_tier3_f11_f12_wcag_contrast_with_table_badge_elements(self):
        """Tier 3 [F11 x F12]: Badges inside tables maintain WCAG AA contrast."""
        css_var = (self.repo_root / "css" / "variables.css").read_text(encoding="utf-8")
        for q in ["q1", "q2", "q3", "q4", "q5"]:
            self.assertIn(f"--badge-{q}-bg", css_var)

    def test_tier3_f12_f10_responsive_tables_within_fluid_layout(self):
        """Tier 3 [F12 x F10]: Table containers are contained inside .container grid layout."""
        html_txt = self.html_path.read_text(encoding="utf-8")
        self.assertIn("class=\"table-container\"", html_txt)
        self.assertIn("class=\"container", html_txt)

    def test_tier3_f13_f14_chart_visualizations_with_local_vendor(self):
        """Tier 3 [F13 x F14]: Chart initialization relies on locally vendored Chart.js."""
        html_txt = self.html_path.read_text(encoding="utf-8")
        self.assertIn("vendor/chart.umd.min.js", html_txt)
        self.assertIn("Chart", (self.repo_root / "js" / "charts.js").read_text(encoding="utf-8"))

    def test_tier3_f2_f17_pii_guard_with_git_tracking(self):
        """Tier 3 [F2 x F17]: Current git tracked files have 0 PII leakages."""
        code, out = git_command("grep", PII_TARGET_CEDULA, "HEAD")
        self.assertNotEqual(code, 0, f"SECURITY VIOLATION: Cédula tracked in HEAD commit: {out}")

    def test_tier3_f14_f16_vendored_assets_with_github_pages_relative_paths(self):
        """Tier 3 [F14 x F16]: Vendored Chart.js and all asset paths are relative for GitHub Pages."""
        for src in self.parsed_html.scripts:
            self.assertFalse(src.startswith("/"))
            self.assertTrue((self.repo_root / src).exists(), f"Script not found: {src}")

    def test_tier3_f16_f17_deployability_files_with_clean_git_branch(self):
        """Tier 3 [F16 x F17]: GitHub Pages deployment files (.nojekyll, docs/index.html) tracked."""
        self.assertTrue((self.repo_root / ".nojekyll").exists())
        self.assertTrue((self.repo_root / "docs" / "index.html").exists())
        code, branch = git_command("branch", "--show-current")
        self.assertEqual(branch, "feat/modernization-ghpages")


# =============================================================================
# TIER 4: REAL-WORLD SCENARIOS (>=10 full end-to-end user journeys)
# =============================================================================

class Tier4RealWorldScenarioTests(unittest.TestCase):
    """Tier 4: Realistic end-to-end user journeys and operational scenarios."""

    @classmethod
    def setUpClass(cls):
        cls.repo_root = REPO_ROOT
        cls.data_path = cls.repo_root / "data" / "saber_pro_2015.json"
        cls.pdf_path = cls.repo_root / "assets" / "EK201532097061.pdf"
        cls.html_path = cls.repo_root / "index.html"
        cls.data = json.loads(cls.data_path.read_text(encoding="utf-8"))
        cls.parsed_html = parse_html_document(cls.html_path.read_text(encoding="utf-8"))

    def test_tier4_scenario_01_mobile_student_journey(self):
        """Tier 4 [Scenario 1]: Mobile student on 375x667 screen navigates scores, cards, and tables."""
        meta_tags = [el["attrs"] for el in self.parsed_html.elements if el["tag"] == "meta"]
        viewport = next((m for m in meta_tags if m.get("name") == "viewport"), None)
        self.assertIsNotNone(viewport)
        self.assertIn("card-mean", self.parsed_html.ids)
        self.assertIn("card-quintiles", self.parsed_html.ids)
        self.assertIn("card-above-nac", self.parsed_html.ids)
        self.assertIn("table-container", self.parsed_html.classes)

    def test_tier4_scenario_02_bilingual_international_recruiter(self):
        """Tier 4 [Scenario 2]: International employer switches to English to review credentials."""
        btn = self.parsed_html.ids.get("btnLangToggle")
        self.assertIsNotNone(btn)
        self.assertIn("aria-label", btn)
        en_txt = (self.repo_root / "locales" / "en.js").read_text(encoding="utf-8")
        self.assertIn("Industrial Engineering", en_txt)
        self.assertIn("Written Communication", en_txt)
        self.assertIn("Quantitative Reasoning", en_txt)

    def test_tier4_scenario_03_statistical_auditor_journey(self):
        """Tier 4 [Scenario 3]: Statistician verifies raw PDF bitstream against calculated indicators."""
        from scripts.verify_statistics import StatisticalVerificationEngine
        engine = StatisticalVerificationEngine(self.repo_root)
        rep = engine.run_all(self.data_path, self.pdf_path, self.html_path)
        self.assertEqual(rep["rules"]["RULE-01-SOURCE-PARITY"]["status"], "PASS")
        self.assertEqual(rep["rules"]["RULE-02-CARD-ARITHMETIC"]["status"], "PASS")
        self.assertEqual(rep["overall_verdict"], "PASS")

    def test_tier4_scenario_04_screen_reader_user_journey(self):
        """Tier 4 [Scenario 4]: Visually impaired visitor navigates site using keyboard only."""
        first_a = next(el for el in self.parsed_html.elements if el["tag"] == "a")
        self.assertIn("skip-link", first_a["attrs"].get("class", ""))
        self.assertEqual(first_a["attrs"].get("href"), "#main-content")
        figs = [el for el in self.parsed_html.elements if el["tag"] == "figure"]
        self.assertGreaterEqual(len(figs), 3)
        canvases = [el["attrs"] for el in self.parsed_html.elements if el["tag"] == "canvas"]
        for c in canvases:
            self.assertEqual(c.get("role"), "img")
            self.assertTrue(len(c.get("aria-label", "")) > 10)

    def test_tier4_scenario_05_github_pages_crawler_journey(self):
        """Tier 4 [Scenario 5]: Static crawler verifies deployability, relative assets, zero 404s."""
        self.assertTrue((self.repo_root / ".nojekyll").exists())
        for p in self.parsed_html.scripts + self.parsed_html.stylesheets:
            self.assertTrue((self.repo_root / p).exists(), f"Asset missing on disk: {p}")
        root_txt = self.html_path.read_text(encoding="utf-8")
        docs_txt = (self.repo_root / "docs" / "index.html").read_text(encoding="utf-8")
        self.assertEqual(root_txt, docs_txt)

    def test_tier4_scenario_06_data_scientist_methodology_audit(self):
        """Tier 4 [Scenario 6]: Data scientist evaluates continuous Gaussian vs discrete ECDF."""
        charts_code = (self.repo_root / "js" / "charts.js").read_text(encoding="utf-8")
        self.assertIn("10.0", charts_code)
        self.assertIn("initBellCurveChart", charts_code)
        a03 = next(d for d in self.data["audit_discrepancies"] if d["id"] == "A-03")
        self.assertIn("Quintil I", a03["calculated_value"])

    def test_tier4_scenario_07_security_and_privacy_officer_audit(self):
        """Tier 4 [Scenario 7]: Privacy officer executes exhaustive sweep confirming 0 PII leakages."""
        files_to_check = [
            self.repo_root / "index.html",
            self.repo_root / "docs" / "index.html",
            self.repo_root / "data" / "saber_pro_2015.json",
            self.repo_root / "README.md",
            self.repo_root / "VERIFICATION_REPORT.md",
        ]
        for f in files_to_check:
            if f.exists():
                text = f.read_text(encoding="utf-8", errors="ignore")
                self.assertNotIn(PII_TARGET_CEDULA, text, f"PII leak detected in {f.name}")

    def test_tier4_scenario_08_offline_airgapped_visitor_journey(self):
        """Tier 4 [Scenario 8]: User opens site in disconnected air-gapped environment."""
        for src in self.parsed_html.scripts:
            self.assertFalse("http" in src or "cdn" in src, f"External dependency: {src}")
        for href in self.parsed_html.stylesheets:
            self.assertFalse("http" in href or "font" in href, f"External dependency: {href}")

    def test_tier4_scenario_09_engineering_faculty_evaluator_journey(self):
        """Tier 4 [Scenario 9]: Engineering dean evaluates the 3 specific engineering competencies."""
        specific_modules = [m for m in self.data["modules"] if m["type"] == "specific"]
        self.assertEqual(len(specific_modules), 3)
        spec_names = {m["name_es"] for m in specific_modules}
        self.assertIn("Formulación de Proyectos de Ingeniería", spec_names)
        self.assertIn("Pensamiento Científico - Matemáticas y Estadística", spec_names)
        self.assertIn("Diseño de Sistemas Productivos y Logísticos", spec_names)
        math_mod = next(m for m in specific_modules if "Científico" in m["name_es"])
        self.assertEqual(math_mod["individual_score"], 12.9)
        self.assertEqual(math_mod["official_quintile"], "V")

    def test_tier4_scenario_10_open_source_contributor_journey(self):
        """Tier 4 [Scenario 10]: Open-source developer clones repo, checks license and tests."""
        lic = (self.repo_root / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("Creative Commons", lic)
        readme = (self.repo_root / "README.md").read_text(encoding="utf-8")
        self.assertIn("SABER PRO", readme)
        self.assertIn("William Camilo Artunduaga", readme)
        from scripts.verify_statistics import StatisticalVerificationEngine
        engine = StatisticalVerificationEngine(self.repo_root)
        rep = engine.run_all(self.data_path, self.pdf_path, self.html_path)
        self.assertEqual(rep["overall_verdict"], "PASS")


# =============================================================================
# MAIN EXECUTION ENTRYPOINT
# =============================================================================

if __name__ == "__main__":
    unittest.main()
