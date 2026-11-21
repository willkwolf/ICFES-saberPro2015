#!/usr/bin/env python3
"""
Unit Test Suite for Independent Statistical Verification Engine
================================================================

Comprehensive unit tests verifying all 8 rules individually:
  - Both passing cases and simulated mutation / error cases.
  - PDF stream extraction tests.
  - CLI argument parsing, execution, and exit codes.
  - JSON schema conformance and Markdown report generation.
"""

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Add repo root and scripts directory to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from verify_statistics import (
    PDFDataExtractor,
    StatisticalVerificationEngine,
    ReportGenerator,
    PII_CEDULA_TARGET,
)


class TestStatisticalVerificationEngine(unittest.TestCase):
    """Test cases for StatisticalVerificationEngine rules and mutations."""

    @classmethod
    def setUpClass(cls):
        cls.data_path = REPO_ROOT / "data" / "saber_pro_2015.json"
        cls.pdf_path = REPO_ROOT / "assets" / "EK201532097061.pdf"
        cls.html_path = REPO_ROOT / "docs" / "index.html"

        with open(cls.data_path, "r", encoding="utf-8") as f:
            cls.canonical_data = json.load(f)

        if cls.html_path.exists():
            with open(cls.html_path, "r", encoding="utf-8") as f:
                cls.html_content = f.read()
        else:
            cls.html_content = ""

        cls.engine = StatisticalVerificationEngine(repo_root=REPO_ROOT)
        cls.pdf_data = PDFDataExtractor.extract_from_pdf(cls.pdf_path)

    # -------------------------------------------------------------------------
    # RULE-01: SOURCE PARITY
    # -------------------------------------------------------------------------
    def test_rule_01_source_parity_pass(self):
        """Verify that genuine canonical JSON matches 100% of extracted PDF data."""
        res = self.engine.verify_rule_01_source_parity(
            self.canonical_data, self.pdf_data
        )
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(len(res["discrepancies"]), 0)
        self.assertEqual(res["checked_modules_count"], 8)

    def test_rule_01_source_parity_score_mutation_fails(self):
        """Simulate a mutated score in JSON; verify Rule 1 detects discrepancy and fails."""
        mutated_data = copy.deepcopy(self.canonical_data)
        mutated_data["modules"][0]["individual_score"] = 99.9  # altered score

        res = self.engine.verify_rule_01_source_parity(mutated_data, self.pdf_data)
        self.assertEqual(res["status"], "FAIL")
        self.assertTrue(any("score mismatch" in d for d in res["discrepancies"]))

    def test_rule_01_source_parity_missing_module_fails(self):
        """Simulate a missing module; verify Rule 1 detects failure."""
        mutated_data = copy.deepcopy(self.canonical_data)
        mutated_data["modules"] = mutated_data["modules"][:-1]  # only 7 modules

        res = self.engine.verify_rule_01_source_parity(mutated_data, self.pdf_data)
        self.assertEqual(res["status"], "FAIL")
        self.assertTrue(any("Expected 8 modules" in d or "missing" in d for d in res["discrepancies"]))

    def test_rule_01_source_parity_metadata_mismatch_fails(self):
        """Simulate corrupted metadata; verify Rule 1 flags it."""
        mutated_data = copy.deepcopy(self.canonical_data)
        mutated_data["metadata"]["registration_number"] = "EK999999999999"

        res = self.engine.verify_rule_01_source_parity(mutated_data, self.pdf_data)
        self.assertEqual(res["status"], "FAIL")
        self.assertTrue(any("Registration mismatch" in d for d in res["discrepancies"]))

    # -------------------------------------------------------------------------
    # RULE-02: CARD ARITHMETIC
    # -------------------------------------------------------------------------
    def test_rule_02_card_arithmetic_pass(self):
        """Verify sum=88.7000 and mean=11.0875 recomputation and A-01 documentation."""
        res = self.engine.verify_rule_02_card_arithmetic(
            self.canonical_data, self.html_content
        )
        self.assertEqual(res["status"], "PASS")
        self.assertAlmostEqual(res["calculated_sum"], 88.7000, places=4)
        self.assertAlmostEqual(res["calculated_mean"], 11.0875, places=4)
        self.assertEqual(res["rounded_1dec"], 11.1)
        self.assertEqual(res["rounded_2dec"], 11.09)
        self.assertTrue(res["anomaly_A01_documented"])

    def test_rule_02_card_arithmetic_wrong_indicator_fails(self):
        """Simulate wrong arithmetic mean in JSON indicators; verify failure."""
        mutated_data = copy.deepcopy(self.canonical_data)
        mutated_data["calculated_indicators"]["arithmetic_mean"] = 12.5

        res = self.engine.verify_rule_02_card_arithmetic(mutated_data, self.html_content)
        self.assertEqual(res["status"], "FAIL")

    def test_rule_02_card_arithmetic_missing_a01_fails(self):
        """Simulate missing anomaly A-01 in audit log; verify failure."""
        mutated_data = copy.deepcopy(self.canonical_data)
        mutated_data["audit_discrepancies"] = [
            a for a in mutated_data["audit_discrepancies"] if a.get("id") != "A-01"
        ]

        res = self.engine.verify_rule_02_card_arithmetic(mutated_data, self.html_content)
        self.assertEqual(res["status"], "FAIL")

    # -------------------------------------------------------------------------
    # RULE-03: SUBGROUP MODULAR MEANS
    # -------------------------------------------------------------------------
    def test_rule_03_subgroup_means_pass(self):
        """Verify generic (10.9200) and specific (11.3667) sub-averages."""
        res = self.engine.verify_rule_03_subgroup_means(self.canonical_data)
        self.assertEqual(res["status"], "PASS")
        self.assertAlmostEqual(res["generic_mean"], 10.9200, places=4)
        self.assertAlmostEqual(res["specific_mean"], 11.3667, places=3)

    def test_rule_03_subgroup_means_wrong_generic_mean_fails(self):
        """Simulate incorrect generic mean in indicators; verify failure."""
        mutated_data = copy.deepcopy(self.canonical_data)
        mutated_data["calculated_indicators"]["generic_mean"] = 15.0

        res = self.engine.verify_rule_03_subgroup_means(mutated_data)
        self.assertEqual(res["status"], "FAIL")

    def test_rule_03_subgroup_means_wrong_specific_mean_fails(self):
        """Simulate incorrect specific mean in indicators; verify failure."""
        mutated_data = copy.deepcopy(self.canonical_data)
        mutated_data["calculated_indicators"]["specific_mean"] = 9.0

        res = self.engine.verify_rule_03_subgroup_means(mutated_data)
        self.assertEqual(res["status"], "FAIL")

    # -------------------------------------------------------------------------
    # RULE-04: PROPORTION CHECKS
    # -------------------------------------------------------------------------
    def test_rule_04_proportion_checks_pass(self):
        """Verify high quintiles (6/8) and above benchmark means (7/8)."""
        res = self.engine.verify_rule_04_proportion_checks(
            self.canonical_data, self.html_content
        )
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["high_quintiles_count"], "6/8")
        self.assertEqual(res["above_national_mean_count"], "7/8")
        self.assertEqual(res["above_reference_mean_count"], "7/8")

    def test_rule_04_proportion_checks_wrong_ratio_fails(self):
        """Simulate changed quintile to alter 6/8 count; verify failure."""
        mutated_data = copy.deepcopy(self.canonical_data)
        # Downgrade two modules from V/IV to I
        mutated_data["modules"][1]["official_quintile"] = "I"
        mutated_data["modules"][2]["official_quintile"] = "I"

        res = self.engine.verify_rule_04_proportion_checks(mutated_data, self.html_content)
        self.assertEqual(res["status"], "FAIL")

    # -------------------------------------------------------------------------
    # RULE-05: TABLE - CHART PARITY
    # -------------------------------------------------------------------------
    def test_rule_05_table_chart_parity_pass(self):
        """Verify zero drift between table rows, Chart.js datasets, and JSON."""
        res = self.engine.verify_rule_05_table_chart_parity(
            self.canonical_data, self.html_content
        )
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["table_rows_extracted"], 8)

    def test_rule_05_table_chart_parity_mismatch_fails(self):
        """Simulate corrupted Chart.js array in HTML; verify failure."""
        mutated_html = self.html_content.replace(
            "data: [9.2, 11.5, 11.6, 10.6, 11.7, 10.1, 12.9, 11.1]",
            "data: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]",
        )
        res = self.engine.verify_rule_05_table_chart_parity(
            self.canonical_data, mutated_html
        )
        self.assertEqual(res["status"], "FAIL")
        self.assertTrue(any("individual scores" in d for d in res["discrepancies"]))

    def test_rule_05_table_chart_parity_none_html_graceful(self):
        """Verify graceful pass when HTML is absent or None."""
        res = self.engine.verify_rule_05_table_chart_parity(self.canonical_data, None)
        self.assertEqual(res["status"], "PASS")

    # -------------------------------------------------------------------------
    # RULE-06: POPULATION BOUNDS
    # -------------------------------------------------------------------------
    def test_rule_06_population_bounds_pass(self):
        """Verify N_ref <= N_nac for all modules and English TyT cohort documentation."""
        res = self.engine.verify_rule_06_population_bounds(self.canonical_data)
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["bounds_verified_count"], 8)
        self.assertTrue(res["english_tyt_divergence_verified"])
        self.assertTrue(res["anomaly_A04_documented"])

    def test_rule_06_population_bounds_violation_fails(self):
        """Simulate inverted population bound (N_ref > N_nac); verify failure."""
        mutated_data = copy.deepcopy(self.canonical_data)
        mutated_data["modules"][0]["reference_group"]["n"] = 999999
        mutated_data["modules"][0]["national_group"]["n"] = 100

        res = self.engine.verify_rule_06_population_bounds(mutated_data)
        self.assertEqual(res["status"], "FAIL")

    def test_rule_06_population_bounds_wrong_english_n_fails(self):
        """Simulate incorrect English national N; verify failure."""
        mutated_data = copy.deepcopy(self.canonical_data)
        for m in mutated_data["modules"]:
            if m["id"] == "ingles":
                m["national_group"]["n"] = 200000

        res = self.engine.verify_rule_06_population_bounds(mutated_data)
        self.assertEqual(res["status"], "FAIL")

    # -------------------------------------------------------------------------
    # RULE-07: HYGIENE PII GUARD
    # -------------------------------------------------------------------------
    def test_rule_07_hygiene_pii_guard_pass(self):
        """Verify repo has zero PII leaks."""
        res = self.engine.verify_rule_07_hygiene_pii_guard()
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(len(res["leaks_detected"]), 0)
        self.assertGreater(res["scanned_files_count"], 0)

    def test_rule_07_hygiene_pii_guard_detected_leak_fails(self):
        """Simulate a temporary text file with PII; verify scanner flags and fails."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            # Create a clean subfolder and dummy file
            leak_file = tmp_root / "leaked_info.txt"
            # Write PII target
            leak_file.write_text(f"Examinee ID: {PII_CEDULA_TARGET}", encoding="utf-8")

            tmp_engine = StatisticalVerificationEngine(repo_root=tmp_root)
            res = tmp_engine.verify_rule_07_hygiene_pii_guard()
            self.assertEqual(res["status"], "FAIL")
            self.assertEqual(len(res["leaks_detected"]), 1)
            self.assertIn("leaked_info.txt", res["leaks_detected"][0])

    # -------------------------------------------------------------------------
    # RULE-08: LINK INTEGRITY
    # -------------------------------------------------------------------------
    def test_rule_08_link_integrity_pass(self):
        """Verify all internal links in repo exist on disk and no placeholders exist."""
        res = self.engine.verify_rule_08_link_integrity()
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(len(res["broken_links"]), 0)
        self.assertEqual(len(res["placeholder_links"]), 0)
        self.assertGreater(res["checked_links_count"], 0)

    def test_rule_08_link_integrity_broken_link_fails(self):
        """Simulate broken local link in markdown file; verify failure."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            md_file = tmp_root / "test.md"
            md_file.write_text("[Broken Link](non_existent_file.pdf)", encoding="utf-8")

            tmp_engine = StatisticalVerificationEngine(repo_root=tmp_root)
            res = tmp_engine.verify_rule_08_link_integrity()
            self.assertEqual(res["status"], "FAIL")
            self.assertEqual(len(res["broken_links"]), 1)

    def test_rule_08_link_integrity_placeholder_link_fails(self):
        """Simulate template placeholder link (TU_USUARIO); verify failure."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            html_file = tmp_root / "index.html"
            html_file.write_text(
                '<a href="https://github.com/TU_USUARIO/repo">GitHub</a>',
                encoding="utf-8",
            )

            tmp_engine = StatisticalVerificationEngine(repo_root=tmp_root)
            res = tmp_engine.verify_rule_08_link_integrity()
            self.assertEqual(res["status"], "FAIL")
            self.assertEqual(len(res["placeholder_links"]), 1)


class TestPDFDataExtractor(unittest.TestCase):
    """Test cases for PDFDataExtractor binary decompression and extraction."""

    def test_extract_pdf_live(self):
        pdf_path = REPO_ROOT / "assets" / "EK201532097061.pdf"
        data = PDFDataExtractor.extract_from_pdf(pdf_path)

        # Verify metadata
        meta = data["metadata"]
        self.assertEqual(meta["registration_number"], "EK201532097061")
        self.assertEqual(meta["candidate_name"], "ARTUNDUAGA VIANA WILLIAM CAMILO")
        self.assertEqual(meta["institution"], "UNIVERSIDAD ICESI")
        self.assertEqual(meta["academic_program"], "INGENIERIA INDUSTRIAL")
        self.assertEqual(meta["municipality"], "CALI")
        self.assertEqual(meta["reference_group"], "INGENIERÍA")

        # Verify 8 modules
        modules = data["modules"]
        self.assertEqual(len(modules), 8)
        self.assertEqual(modules["comunicacion_escrita"]["individual_score"], 9.2)
        self.assertEqual(modules["comunicacion_escrita"]["performance_level"], "3")
        self.assertEqual(modules["comunicacion_escrita"]["official_quintile"], "I")
        self.assertEqual(modules["pensamiento_cientifico"]["individual_score"], 12.9)
        self.assertIsNone(modules["pensamiento_cientifico"]["performance_level"])
        self.assertEqual(modules["pensamiento_cientifico"]["official_quintile"], "V")

    def test_extract_pdf_nonexistent_raises(self):
        with self.assertRaises(FileNotFoundError):
            PDFDataExtractor.extract_from_pdf(Path("non_existent.pdf"))


class TestReportGeneratorAndCLI(unittest.TestCase):
    """Test cases for report generation and CLI execution."""

    def test_report_generator_schema(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            json_out = Path(tmp_dir) / "report.json"
            md_out = Path(tmp_dir) / "report.md"

            engine = StatisticalVerificationEngine(repo_root=REPO_ROOT)
            report = engine.run_all(
                data_path=REPO_ROOT / "data" / "saber_pro_2015.json",
                pdf_path=REPO_ROOT / "assets" / "EK201532097061.pdf",
            )

            ReportGenerator.write_json_report(report, json_out)
            canonical = json.loads((REPO_ROOT / "data" / "saber_pro_2015.json").read_text(encoding="utf-8"))
            ReportGenerator.write_markdown_report(report, canonical, md_out)

            self.assertTrue(json_out.exists())
            self.assertTrue(md_out.exists())

            # Verify JSON schema matches PROJECT.md
            with open(json_out, "r", encoding="utf-8") as f:
                saved_json = json.load(f)

            self.assertIn("timestamp", saved_json)
            self.assertIn("overall_verdict", saved_json)
            self.assertIn("rules", saved_json)
            self.assertEqual(saved_json["overall_verdict"], "PASS")

            expected_rules = [
                "RULE-01-SOURCE-PARITY",
                "RULE-02-CARD-ARITHMETIC",
                "RULE-03-SUBGROUP-MEANS",
                "RULE-04-PROPORTION-CHECKS",
                "RULE-05-TABLE-CHART-PARITY",
                "RULE-06-POPULATION-BOUNDS",
                "RULE-07-HYGIENE-PII-GUARD",
                "RULE-08-LINK-INTEGRITY",
            ]
            for r in expected_rules:
                self.assertIn(r, saved_json["rules"])
                self.assertIn("status", saved_json["rules"][r])
                self.assertIn("details", saved_json["rules"][r])

            # Verify Markdown content
            md_content = md_out.read_text(encoding="utf-8")
            self.assertIn("Informe Independiente de Verificación", md_content)
            self.assertIn("RULE-01-SOURCE-PARITY", md_content)
            self.assertIn("A-01", md_content)
            self.assertIn("A-07", md_content)

    def test_cli_execution_pass(self):
        """Test running scripts/verify_statistics.py via subprocess returns code 0."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_json = Path(tmp_dir) / "out.json"
            out_md = Path(tmp_dir) / "out.md"
            cmd = [
                sys.executable,
                str(SCRIPT_DIR / "verify_statistics.py"),
                "--output-json",
                str(out_json),
                "--output-md",
                str(out_md),
            ]
            result = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
            self.assertTrue(out_json.exists())
            self.assertTrue(out_md.exists())

    def test_cli_execution_missing_data_fails(self):
        """Test running scripts/verify_statistics.py with missing file returns code 1."""
        cmd = [
            sys.executable,
            str(SCRIPT_DIR / "verify_statistics.py"),
            "--data",
            "non_existent.json",
        ]
        result = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
