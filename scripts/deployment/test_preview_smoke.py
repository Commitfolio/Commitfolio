from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


MODULE_PATH = Path(__file__).with_name("preview_smoke.py")
SPEC = importlib.util.spec_from_file_location("preview_smoke", MODULE_PATH)
assert SPEC and SPEC.loader
preview_smoke = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = preview_smoke
SPEC.loader.exec_module(preview_smoke)


class PreviewSmokeTests(unittest.TestCase):
    def test_validate_mode_requirements_for_release(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires --frontend-url"):
            preview_smoke.validate_mode_requirements("release", frontend_url=None, expected_api_base=None)

        with self.assertRaisesRegex(ValueError, "requires --expected-frontend-api-base"):
            preview_smoke.validate_mode_requirements(
                "release",
                frontend_url="https://frontend.example.com",
                expected_api_base=None,
            )

        preview_smoke.validate_mode_requirements(
            "release",
            frontend_url="https://frontend.example.com",
            expected_api_base="https://backend.example.com",
        )

    def test_build_followup_steps_includes_failure_specific_guidance(self) -> None:
        results = [
            preview_smoke.CheckResult("backend health", False, "backend down"),
            preview_smoke.CheckResult("frontend api base", False, "localhost reference remained"),
        ]

        steps = preview_smoke.build_followup_steps("release", results)

        self.assertTrue(any("public/private/org 저장소 샘플 검증" in step for step in steps))
        self.assertTrue(any("Render deploy 로그" in step for step in steps))
        self.assertTrue(any("VITE_API_BASE_URL" in step for step in steps))

    def test_write_json_report_contains_summary_and_next_steps(self) -> None:
        results = [
            preview_smoke.CheckResult("backend health", True, "ok"),
            preview_smoke.CheckResult("oauth start", False, "missing redirect"),
        ]

        with tempfile.TemporaryDirectory() as tempdir:
            output_path = Path(tempdir) / "reports" / "release-smoke.json"
            preview_smoke.write_json_report(
                str(output_path),
                mode="release",
                backend_url="https://backend.example.com",
                frontend_url="https://frontend.example.com",
                expected_api_base="https://backend.example.com",
                results=results,
            )

            payload = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(payload["mode"], "release")
        self.assertEqual(payload["summary"]["failed"], 1)
        self.assertFalse(payload["summary"]["ok"])
        self.assertEqual(len(payload["results"]), 2)
        self.assertTrue(payload["next_steps"])
        self.assertIn("generated_at", payload)


if __name__ == "__main__":
    unittest.main()
