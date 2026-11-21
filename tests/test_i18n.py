#!/usr/bin/env python3
"""
Test Suite: Internationalization (i18n) Engine & Translation Dictionaries
========================================================================

Validates:
1. 100% Key Parity between Spanish (es.js) and English (en.js) dictionaries.
2. Zero empty or whitespace-only strings across all translation keys.
3. Complete translation coverage for all 8 modules from data/saber_pro_2015.json.
4. Complete translation coverage for all historical anomalies (A-01 through A-07).
5. Locale number and date formatting rules (formatScore, formatCount, formatDate).
6. Execution of js/i18n.js via Node.js V8 Intl engine (when available).
7. Zero PII leakage across i18n files (RULE-07-HYGIENE-PII-GUARD compliance).
"""

import json
import os
import re
import shutil
import subprocess
import unittest
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

# Project root directory
REPO_ROOT = Path(__file__).resolve().parent.parent
LOCALES_DIR = REPO_ROOT / "locales"
ES_PATH = LOCALES_DIR / "es.js"
EN_PATH = LOCALES_DIR / "en.js"
I18N_JS_PATH = REPO_ROOT / "js" / "i18n.js"
CANONICAL_DATA_PATH = REPO_ROOT / "data" / "saber_pro_2015.json"

# Dynamic constant for PII scanning to prevent self-matching in source code
PII_CEDULA_TARGET = "".join(["114", "3848", "416"])


def extract_js_object(file_path: Path, var_name: str) -> Dict[str, Any]:
    """Extracts and parses the JSON-compatible JS dictionary from a locale file."""
    if not file_path.exists():
        raise FileNotFoundError(f"Locale file does not exist: {file_path}")

    content = file_path.read_text(encoding="utf-8")
    start = content.find("{")
    end = content.find("\n};")
    if start == -1 or end == -1:
        # Fallback search
        m = re.search(r"const\s+" + var_name + r"\s*=\s*(\{.*?\n\};)", content, re.DOTALL)
        if not m:
            raise ValueError(f"Could not locate object {var_name} in {file_path}")
        raw_json = m.group(1).rstrip(";").strip()
    else:
        raw_json = content[start : end + 2].rstrip(";").strip()

    try:
        return json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Failed to parse JSON dictionary from {file_path}: {exc}") from exc


def get_all_key_paths(d: Dict[str, Any], prefix: str = "") -> Set[str]:
    """Recursively collects all dot-separated key paths in a nested dictionary."""
    paths: Set[str] = set()
    for k, v in d.items():
        current = f"{prefix}.{k}" if prefix else str(k)
        if isinstance(v, dict):
            paths.update(get_all_key_paths(v, current))
        else:
            paths.add(current)
    return paths


def get_all_leaf_values(d: Dict[str, Any], prefix: str = "") -> List[Tuple[str, Any]]:
    """Recursively collects all leaf values with their dot-separated key paths."""
    leaves: List[Tuple[str, Any]] = []
    for k, v in d.items():
        current = f"{prefix}.{k}" if prefix else str(k)
        if isinstance(v, dict):
            leaves.extend(get_all_leaf_values(v, current))
        else:
            leaves.append((current, v))
    return leaves


class TestI18nLocales(unittest.TestCase):
    """Test suite for locales/es.js and locales/en.js dictionary integrity."""

    @classmethod
    def setUpClass(cls):
        cls.es = extract_js_object(ES_PATH, "es")
        cls.en = extract_js_object(EN_PATH, "en")
        cls.paths_es = get_all_key_paths(cls.es)
        cls.paths_en = get_all_key_paths(cls.en)

        with open(CANONICAL_DATA_PATH, "r", encoding="utf-8") as f:
            cls.canonical_data = json.load(f)

    def test_files_exist(self):
        """Verify that locales/es.js and locales/en.js exist on disk."""
        self.assertTrue(ES_PATH.exists(), f"Missing file: {ES_PATH}")
        self.assertTrue(EN_PATH.exists(), f"Missing file: {EN_PATH}")
        self.assertTrue(I18N_JS_PATH.exists(), f"Missing file: {I18N_JS_PATH}")

    def test_top_level_key_parity(self):
        """Verify identical top-level keys between Spanish and English dictionaries."""
        keys_es = set(self.es.keys())
        keys_en = set(self.en.keys())
        diff = keys_es.symmetric_difference(keys_en)
        self.assertEqual(
            keys_es,
            keys_en,
            f"Top-level key mismatch between es and en: {diff}",
        )

        expected_sections = {
            "metadata",
            "nav",
            "header",
            "candidate_info",
            "stats",
            "modules",
            "levels",
            "quintiles",
            "tables",
            "charts",
            "anomalies",
            "methodology",
            "footer",
        }
        missing = expected_sections - keys_es
        self.assertEqual(len(missing), 0, f"Missing required top-level sections: {missing}")

    def test_complete_deep_key_parity(self):
        """Verify 100% key parity across all nested levels of es.js and en.js."""
        only_in_es = self.paths_es - self.paths_en
        only_in_en = self.paths_en - self.paths_es

        msg = []
        if only_in_es:
            msg.append(f"Keys present ONLY in es.js ({len(only_in_es)}): {sorted(list(only_in_es))[:5]}")
        if only_in_en:
            msg.append(f"Keys present ONLY in en.js ({len(only_in_en)}): {sorted(list(only_in_en))[:5]}")

        self.assertEqual(
            self.paths_es,
            self.paths_en,
            "\n".join(msg) if msg else "Key sets do not match perfectly",
        )
        self.assertGreater(len(self.paths_es), 100, "Dictionary should have extensive key coverage (>100 keys)")

    def test_non_empty_strings(self):
        """Verify that no string translation is empty or contains only whitespace."""
        leaves_es = get_all_leaf_values(self.es)
        leaves_en = get_all_leaf_values(self.en)

        for path, val in leaves_es:
            if isinstance(val, str):
                self.assertTrue(
                    len(val.strip()) > 0,
                    f"Empty or whitespace string found in es.js at: {path}",
                )

        for path, val in leaves_en:
            if isinstance(val, str):
                self.assertTrue(
                    len(val.strip()) > 0,
                    f"Empty or whitespace string found in en.js at: {path}",
                )

    def test_canonical_modules_coverage(self):
        """Verify that all 8 modules in data/saber_pro_2015.json are present in both locales."""
        modules = self.canonical_data.get("modules", [])
        self.assertEqual(len(modules), 8, "Canonical dataset must contain exactly 8 modules")

        required_fields = [
            "id",
            "name",
            "type",
            "type_label",
            "description",
            "individual_score",
            "performance_level",
            "official_quintile",
            "ref_mean",
            "ref_sd",
            "ref_n",
            "nat_mean",
            "nat_sd",
            "nat_n",
        ]

        for mod in modules:
            mod_id = mod["id"]
            self.assertIn(
                mod_id,
                self.es["modules"],
                f"Module '{mod_id}' missing in es.js modules dictionary",
            )
            self.assertIn(
                mod_id,
                self.en["modules"],
                f"Module '{mod_id}' missing in en.js modules dictionary",
            )

            mod_es = self.es["modules"][mod_id]
            mod_en = self.en["modules"][mod_id]

            for field in required_fields:
                self.assertIn(
                    field,
                    mod_es,
                    f"Field '{field}' missing for module '{mod_id}' in es.js",
                )
                self.assertIn(
                    field,
                    mod_en,
                    f"Field '{field}' missing for module '{mod_id}' in en.js",
                )
                self.assertTrue(
                    str(mod_es[field]).strip(),
                    f"Field '{field}' is empty for module '{mod_id}' in es.js",
                )
                self.assertTrue(
                    str(mod_en[field]).strip(),
                    f"Field '{field}' is empty for module '{mod_id}' in en.js",
                )

            # Name parity with canonical data
            self.assertEqual(mod_es["name"], mod["name_es"])
            self.assertEqual(mod_en["name"], mod["name_en"])

    def test_historical_anomalies_coverage(self):
        """Verify that anomalies A-01 through A-07 are documented and translated in both locales."""
        expected_anomalies = [f"A-0{i}" for i in range(1, 8)]

        required_anomaly_fields = [
            "id",
            "code",
            "title",
            "legacy_label",
            "legacy_value",
            "canonical_label",
            "canonical_value",
            "description",
            "impact",
        ]

        for aid in expected_anomalies:
            self.assertIn(
                aid,
                self.es["anomalies"],
                f"Historical anomaly '{aid}' missing in es.js",
            )
            self.assertIn(
                aid,
                self.en["anomalies"],
                f"Historical anomaly '{aid}' missing in en.js",
            )

            a_es = self.es["anomalies"][aid]
            a_en = self.en["anomalies"][aid]

            for field in required_anomaly_fields:
                self.assertIn(
                    field,
                    a_es,
                    f"Field '{field}' missing in anomaly '{aid}' (es.js)",
                )
                self.assertIn(
                    field,
                    a_en,
                    f"Field '{field}' missing in anomaly '{aid}' (en.js)",
                )
                self.assertTrue(
                    str(a_es[field]).strip(),
                    f"Field '{field}' is empty in anomaly '{aid}' (es.js)",
                )
                self.assertTrue(
                    str(a_en[field]).strip(),
                    f"Field '{field}' is empty in anomaly '{aid}' (en.js)",
                )

    def test_pii_security_compliance(self):
        """Verify zero occurrences of Colombian Cédula across i18n files (RULE-07 compliance)."""
        for p in [ES_PATH, EN_PATH, I18N_JS_PATH]:
            content = p.read_text(encoding="utf-8")
            self.assertNotIn(
                PII_CEDULA_TARGET,
                content,
                f"SECURITY VIOLATION: National ID PII detected in {p}",
            )


class TestI18nEngineAndFormatters(unittest.TestCase):
    """Test suite for js/i18n.js formatting rules and runtime behavior."""

    @staticmethod
    def format_score_py(value: float, lang: str) -> str:
        """Python reference implementation of formatScore matching Intl.NumberFormat:

        - es-CO: 1 decimal place with comma decimal separator (e.g. 11,1)
        - en-US: 1 decimal place with dot decimal separator (e.g. 11.1)
        """
        rounded = f"{round(value, 1):.1f}"
        if lang == "es":
            return rounded.replace(".", ",")
        return rounded

    @staticmethod
    def format_count_py(value: int, lang: str) -> str:
        """Python reference implementation of formatCount matching Intl.NumberFormat:

        - es-CO: thousands separator period '.' (e.g. 43.932)
        - en-US: thousands separator comma ',' (e.g. 43,932)
        """
        if lang == "es":
            return f"{value:,}".replace(",", ".")
        return f"{value:,}"

    def test_python_reference_formatters(self):
        """Verify mathematical formatter rules for scores and counts."""
        self.assertEqual(self.format_score_py(11.0875, "es"), "11,1")
        self.assertEqual(self.format_score_py(11.0875, "en"), "11.1")
        self.assertEqual(self.format_score_py(9.2, "es"), "9,2")
        self.assertEqual(self.format_score_py(9.2, "en"), "9.2")

        self.assertEqual(self.format_count_py(43932, "es"), "43.932")
        self.assertEqual(self.format_count_py(43932, "en"), "43,932")
        self.assertEqual(self.format_count_py(215703, "es"), "215.703")
        self.assertEqual(self.format_count_py(215703, "en"), "215,703")

    def test_node_runtime_i18n_execution(self):
        """Execute js/i18n.js in Node.js to test real native Intl.NumberFormat and Intl.DateTimeFormat."""
        node_bin = shutil.which("node")
        if not node_bin:
            self.skipTest("Node.js binary not available in environment; skipping live V8 test.")

        node_script = """
        import i18n from './js/i18n.js';

        const results = {
          defaultLang: i18n.getLanguage(),
          scoreEs: i18n.formatScore(11.0875, 'es'),
          scoreEn: i18n.formatScore(11.0875, 'en'),
          countEs: i18n.formatCount(43932, 'es'),
          countEn: i18n.formatCount(43932, 'en'),
          dateEs: i18n.formatDate('2015-11-22', 'es'),
          dateEn: i18n.formatDate('2015-11-22', 'en'),
          transEs: i18n.t('stats.arithmetic_mean.title'),
          setEn: i18n.setLanguage('en'),
          currentEn: i18n.getLanguage(),
          transEn: i18n.t('stats.arithmetic_mean.title'),
          moduleEs: i18n.t('modules.comunicacion_escrita.name', null, 'es'),
          moduleEn: i18n.t('modules.comunicacion_escrita.name', null, 'en'),
          anomalyEs: i18n.t('anomalies.A-01.code', null, 'es'),
          anomalyEn: i18n.t('anomalies.A-01.code', null, 'en'),
          interpolation: i18n.t('testing_param', { num: 42 })
        };

        console.log(JSON.stringify(results));
        """

        res = subprocess.run(
            [node_bin, "--input-type=module", "-e", node_script],
            cwd=str(REPO_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

        self.assertEqual(
            res.returncode,
            0,
            f"Node.js execution of js/i18n.js failed with error:\n{res.stderr}",
        )

        output = json.loads(res.stdout.strip())

        self.assertEqual(output["defaultLang"], "es")
        self.assertEqual(output["scoreEs"], "11,1")
        self.assertEqual(output["scoreEn"], "11.1")
        self.assertEqual(output["countEs"], "43.932")
        self.assertEqual(output["countEn"], "43,932")
        self.assertIn("noviembre", output["dateEs"].lower())
        self.assertIn("november", output["dateEn"].lower())
        self.assertEqual(output["transEs"], "Promedio General")
        self.assertEqual(output["setEn"], "en")
        self.assertEqual(output["currentEn"], "en")
        self.assertEqual(output["transEn"], "Overall Mean")
        self.assertEqual(output["moduleEs"], "Comunicación Escrita")
        self.assertEqual(output["moduleEn"], "Written Communication")
        self.assertEqual(output["anomalyEs"], "A-01")
        self.assertEqual(output["anomalyEn"], "A-01")


if __name__ == "__main__":
    unittest.main(verbosity=2)
