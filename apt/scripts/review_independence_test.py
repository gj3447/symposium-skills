from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


MODULE_PATH = Path(__file__).with_name("review_independence.py")
SPEC = importlib.util.spec_from_file_location("review_independence", MODULE_PATH)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


ARTIFACT = "a" * 64
PROMPT_A = "b" * 64
PROMPT_B = "c" * 64
RECEIPT = "d" * 64
DECISION = "e" * 64


def identity(
    *,
    provider: str,
    revision: str,
    family: str,
    prompt: str,
    session: str,
    temperature: float,
) -> dict:
    return {
        "provider": provider,
        "model_revision": revision,
        "weight_family": family,
        "prompt_sha256": prompt,
        "session_id": session,
        "temperature": temperature,
    }


def request() -> dict:
    return {
        "artifact_sha256": ARTIFACT,
        "producer": identity(
            provider="anthropic",
            revision="claude-opus-4.1-202607",
            family="claude-opus-4.1",
            prompt=PROMPT_A,
            session="producer-session",
            temperature=0.2,
        ),
        "reviewer": identity(
            provider="openai",
            revision="gpt-5.2-202607",
            family="gpt-5.2",
            prompt=PROMPT_B,
            session="reviewer-session",
            temperature=0.9,
        ),
        "deterministic_oracles": [],
    }


class ReviewIndependenceTests(unittest.TestCase):
    def test_cross_family_prompt_temperature_and_session_separation_passes(self):
        receipt = module.evaluate(request())
        self.assertEqual(receipt["verdict"], "PASS")
        self.assertEqual(receipt["correlation_status"], "CROSS_FAMILY")

    def test_different_alias_same_weight_family_is_correlated(self):
        value = request()
        value["reviewer"] = identity(
            provider="anthropic",
            revision="claude-opus-alias-new",
            family="claude-opus-4.1",
            prompt=PROMPT_B,
            session="reviewer-session",
            temperature=0.9,
        )
        receipt = module.evaluate(value)
        self.assertEqual(receipt["verdict"], "BLOCK")
        self.assertEqual(receipt["correlation_status"], "CORRELATED_SAME_MODEL")

    def test_same_prompt_blocks_even_with_cross_family_models(self):
        value = request()
        value["reviewer"]["prompt_sha256"] = PROMPT_A
        receipt = module.evaluate(value)
        self.assertEqual(receipt["verdict"], "BLOCK")
        self.assertFalse(receipt["dimensions"]["different_prompt"])

    def test_temperature_value_difference_inside_same_band_is_not_diversity(self):
        value = request()
        value["producer"]["temperature"] = 0.10
        value["reviewer"]["temperature"] = 0.20
        receipt = module.evaluate(value)
        self.assertEqual(receipt["verdict"], "BLOCK")
        self.assertFalse(receipt["dimensions"]["different_temperature_band"])

    def test_lite_mode_can_only_be_conditional_with_oracle_and_human(self):
        value = request()
        value["reviewer"].update(
            provider="anthropic",
            model_revision="claude-opus-4.1-review",
            weight_family="claude-opus-4.1",
        )
        value["deterministic_oracles"] = [
            {
                "kind": "test_result",
                "verdict": "PASS",
                "artifact_sha256": ARTIFACT,
                "receipt_sha256": RECEIPT,
            }
        ]
        value["human_approval"] = {
            "actor": "sigma_oracle",
            "decision": "APPROVE",
            "artifact_sha256": ARTIFACT,
            "decision_sha256": DECISION,
        }
        receipt = module.evaluate(value)
        self.assertEqual(receipt["verdict"], "CONDITIONAL")
        self.assertNotEqual(receipt["confidence_ceiling"], "INDEPENDENT_REVIEW")

    def test_oracle_without_human_cannot_elevate_same_family(self):
        value = request()
        value["reviewer"].update(
            provider="anthropic",
            weight_family="claude-opus-4.1",
        )
        value["deterministic_oracles"] = [
            {
                "kind": "test_result",
                "verdict": "PASS",
                "artifact_sha256": ARTIFACT,
                "receipt_sha256": RECEIPT,
            }
        ]
        receipt = module.evaluate(value)
        self.assertEqual(receipt["verdict"], "BLOCK")


if __name__ == "__main__":
    unittest.main()
