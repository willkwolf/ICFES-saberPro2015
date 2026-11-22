#!/usr/bin/env python3
"""
ICFES Saber Pro 2015 - Modernization & Verification E2E Test Runner
===================================================================

Runner for the 4-tier E2E test suite covering:
  - Tier 1: Feature Coverage (>= 5 tests per feature area across F1-F17, >= 80 tests)
  - Tier 2: Boundary & Corner Cases (>= 5 tests per feature area across F1-F17, >= 80 tests)
  - Tier 3: Cross-Feature Combinations (>= 16 pairwise integration tests)
  - Tier 4: Real-World Scenarios (>= 10 end-to-end user journeys)
  Total: >= 186 test cases.

Usage:
  python tests/e2e_runner.py                     # Run all tiers (186+ tests)
  python tests/e2e_runner.py --tier 1             # Run Tier 1 only
  python tests/e2e_runner.py --tier 2             # Run Tier 2 only
  python tests/e2e_runner.py --tier 3             # Run Tier 3 only
  python tests/e2e_runner.py --tier 4             # Run Tier 4 only
  python tests/e2e_runner.py --feature F3         # Filter by feature code
  python tests/e2e_runner.py --json-output report.json
"""

import argparse
import datetime
import json
import os
import sys
import time
import unittest
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


# Add project root and tests directory to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
TESTS_DIR = REPO_ROOT / "tests"
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))


class E2ETestResult(unittest.TextTestResult):
    """Custom test result collector tracking tier and feature execution details."""

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.test_records: List[Dict[str, Any]] = []
        self.start_times: Dict[str, float] = {}

    def startTest(self, test):
        self.start_times[test.id()] = time.perf_counter()
        super().startTest(test)

    def addSuccess(self, test):
        super().addSuccess(test)
        elapsed = time.perf_counter() - self.start_times.get(test.id(), 0.0)
        self._record(test, "PASS", None, elapsed)

    def addFailure(self, test, err):
        super().addFailure(test, err)
        elapsed = time.perf_counter() - self.start_times.get(test.id(), 0.0)
        self._record(test, "FAIL", self._exc_info_to_string(err, test), elapsed)

    def addError(self, test, err):
        super().addError(test, err)
        elapsed = time.perf_counter() - self.start_times.get(test.id(), 0.0)
        self._record(test, "ERROR", self._exc_info_to_string(err, test), elapsed)

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        elapsed = time.perf_counter() - self.start_times.get(test.id(), 0.0)
        self._record(test, "SKIP", reason, elapsed)

    def _record(self, test, status: str, details: Optional[str], elapsed: float):
        test_id = test.id()
        method_name = test_id.split(".")[-1]
        class_name = test_id.split(".")[-2]
        doc = test.shortDescription() or ""

        # Determine Tier
        tier = "Unknown"
        if "Tier1" in class_name or "tier1" in method_name:
            tier = "Tier 1: Feature Coverage"
        elif "Tier2" in class_name or "tier2" in method_name:
            tier = "Tier 2: Boundary & Corner Cases"
        elif "Tier3" in class_name or "tier3" in method_name:
            tier = "Tier 3: Cross-Feature Integration"
        elif "Tier4" in class_name or "tier4" in method_name:
            tier = "Tier 4: Real-World Scenarios"

        # Determine Feature if applicable
        feature = "Cross-Cutting"
        for f_num in [
            "F17", "F16", "F14", "F13", "F12", "F11", "F10",
            "F9", "F8", "F7", "F6", "F5", "F4", "F3", "F2", "F1",
        ]:
            if f"_{f_num.lower()}_" in method_name.lower() or f"{f_num.lower()}_" in method_name.lower():
                feature = f_num
                break

        self.test_records.append({
            "id": test_id,
            "class": class_name,
            "method": method_name,
            "doc": doc,
            "tier": tier,
            "feature": feature,
            "status": status,
            "details": details,
            "elapsed_ms": round(elapsed * 1000, 2),
        })


def filter_test_suite(
    suite: unittest.TestSuite,
    target_tier: Optional[int] = None,
    target_feature: Optional[str] = None,
) -> unittest.TestSuite:
    """Filter test cases by specified tier (1..4) and/or feature code (F1..F17)."""
    filtered = unittest.TestSuite()

    for test in _flatten_suite(suite):
        method_name = test.id().split(".")[-1].lower()
        class_name = test.id().split(".")[-2].lower()

        # Check Tier filter
        if target_tier is not None:
            tier_match = False
            tier_str = f"tier{target_tier}"
            if tier_str in class_name or tier_str in method_name:
                tier_match = True
            if not tier_match:
                continue

        # Check Feature filter
        if target_feature is not None:
            feat_lower = target_feature.lower()
            feat_token = f"_{feat_lower}_"
            feat_prefix = f"test_{feat_lower}_"
            if feat_token not in method_name and not method_name.startswith(feat_prefix):
                # Also check cross-feature naming e.g. test_tier3_f3_f4
                if feat_lower not in method_name:
                    continue

        filtered.addTest(test)

    return filtered


def _flatten_suite(suite: unittest.TestSuite) -> List[unittest.TestCase]:
    cases = []
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            cases.extend(_flatten_suite(item))
        elif isinstance(item, unittest.TestCase):
            cases.append(item)
    return cases


def print_summary_table(records: List[Dict[str, Any]], total_duration_s: float):
    """Print an ANSI / UTF-8 formatted summary of test results by tier and feature."""
    print("\n" + "=" * 80)
    print("  ICFES SABER PRO 2015 - E2E TEST EXECUTION SUMMARY")
    print("=" * 80)

    # Group by Tier
    tiers = [
        "Tier 1: Feature Coverage",
        "Tier 2: Boundary & Corner Cases",
        "Tier 3: Cross-Feature Integration",
        "Tier 4: Real-World Scenarios",
    ]

    tier_counts: Dict[str, Dict[str, int]] = {
        t: {"PASS": 0, "FAIL": 0, "ERROR": 0, "SKIP": 0, "TOTAL": 0} for t in tiers
    }

    for r in records:
        t = r["tier"]
        st = r["status"]
        if t in tier_counts:
            tier_counts[t][st] = tier_counts[t].get(st, 0) + 1
            tier_counts[t]["TOTAL"] += 1

    print(f"\n{'Tier Architecture':<38} {'Total':>7} {'Pass':>7} {'Fail':>7} {'Error':>7} {'Status':>8}")
    print("-" * 80)

    all_passed = True
    total_run = 0
    total_passed = 0
    total_failed = 0
    total_errors = 0

    for t in tiers:
        counts = tier_counts[t]
        tot = counts["TOTAL"]
        p = counts["PASS"]
        f = counts["FAIL"]
        e = counts["ERROR"]
        total_run += tot
        total_passed += p
        total_failed += f
        total_errors += e

        tier_status = "PASS" if (tot > 0 and f == 0 and e == 0) else ("FAIL" if (f > 0 or e > 0) else "EMPTY")
        if tier_status != "PASS":
            all_passed = False

        print(f"{t:<38} {tot:>7} {p:>7} {f:>7} {e:>7} {tier_status:>8}")

    print("-" * 80)
    overall_status = "PASS" if (all_passed and total_run > 0) else "FAIL"
    print(f"{'OVERALL SUITE VERDICT':<38} {total_run:>7} {total_passed:>7} {total_failed:>7} {total_errors:>7} {overall_status:>8}")
    print("=" * 80)

    # Print Feature matrix for Tier 1 & 2
    print("\nFeature Area Breakdown (Tiers 1 & 2):")
    features = [
        ("F1", "Repo Baseline & Git Tracking"),
        ("F2", "Repo Sovereignty & Privacy Guard"),
        ("F3", "Canonical Dataset Structure"),
        ("F4", "Statistical Verification Rules"),
        ("F5", "Discrepancy & Anomaly Audit"),
        ("F6", "Verification Engine Automation"),
        ("F7", "i18n Content Decoupling"),
        ("F8", "Locale Number & Date Formatting"),
        ("F9", "Interactive Language Switching"),
        ("F10", "Semantic UI & Fluid Layout"),
        ("F11", "WCAG AA Accessibility & Focus"),
        ("F12", "Responsive Mobile Tables"),
        ("F13", "Complete Visualization Suite"),
        ("F14", "Local Asset Vendoring (No CDN)"),
        ("F16", "GitHub Pages Static Deployability"),
        ("F17", "Clean Commit History on Branch"),
    ]

    print(f"{'#':<4} {'Feature Area':<36} {'Tier 1':>8} {'Tier 2':>8} {'Total':>8} {'Status':>8}")
    print("-" * 76)

    for code, name in features:
        t1_count = sum(1 for r in records if r["feature"] == code and "Tier 1" in r["tier"] and r["status"] == "PASS")
        t2_count = sum(1 for r in records if r["feature"] == code and "Tier 2" in r["tier"] and r["status"] == "PASS")
        t_fail = sum(1 for r in records if r["feature"] == code and r["status"] in ("FAIL", "ERROR"))
        f_status = "PASS" if (t1_count >= 5 and t2_count >= 5 and t_fail == 0) else "INCOMPLETE"
        print(f"{code:<4} {name:<36} {t1_count:>8} {t2_count:>8} {t1_count + t2_count:>8} {f_status:>8}")

    print("-" * 76)
    print(f"Total Execution Time: {total_duration_s:.3f} seconds\n")


def run_e2e_suite(
    target_tier: Optional[int] = None,
    target_feature: Optional[str] = None,
    json_output_path: Optional[str] = None,
    verbosity: int = 1,
) -> int:
    """Load test_e2e_suite, execute tests, print report, and return exit code."""
    # Import suite dynamically
    try:
        import test_e2e_suite
    except ImportError:
        from tests import test_e2e_suite

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(test_e2e_suite)

    # Filter suite if requested
    filtered_suite = filter_test_suite(suite, target_tier, target_feature)
    total_selected = len(_flatten_suite(filtered_suite))

    if total_selected == 0:
        print(f"WARNING: No tests matched filter (tier={target_tier}, feature={target_feature})")
        return 1

    runner = unittest.TextTestRunner(
        verbosity=verbosity,
        resultclass=E2ETestResult,
    )

    start_time = time.perf_counter()
    result = runner.run(filtered_suite)
    duration = time.perf_counter() - start_time

    # Cast to our custom result class
    custom_result: E2ETestResult = result  # type: ignore

    # Print summary
    print_summary_table(custom_result.test_records, duration)

    # Export JSON report if requested
    if json_output_path:
        out_p = Path(json_output_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        report_data = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "duration_seconds": round(duration, 3),
            "total_executed": len(custom_result.test_records),
            "passed": sum(1 for r in custom_result.test_records if r["status"] == "PASS"),
            "failed": len(custom_result.failures),
            "errors": len(custom_result.errors),
            "skipped": len(custom_result.skipped),
            "overall_verdict": "PASS" if custom_result.wasSuccessful() else "FAIL",
            "tests": custom_result.test_records,
        }
        out_p.write_text(json.dumps(report_data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Saved machine-readable report to: {out_p}")

    return 0 if result.wasSuccessful() else 1


def main():
    parser = argparse.ArgumentParser(
        description="ICFES Saber Pro 2015 Modernization E2E Test Runner"
    )
    parser.add_argument(
        "--tier",
        type=int,
        choices=[1, 2, 3, 4],
        default=None,
        help="Run tests only for the specified Tier (1, 2, 3, or 4)",
    )
    parser.add_argument(
        "--feature",
        type=str,
        default=None,
        help="Filter tests by feature code (e.g. F1, F3, F10)",
    )
    parser.add_argument(
        "--json-output",
        type=str,
        default=None,
        help="Path to export structured JSON execution report",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=1,
        help="Increase verbosity level",
    )
    args = parser.parse_args()

    exit_code = run_e2e_suite(
        target_tier=args.tier,
        target_feature=args.feature,
        json_output_path=args.json_output,
        verbosity=args.verbose,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
