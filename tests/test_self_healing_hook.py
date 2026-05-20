import unittest
from unittest.mock import patch, MagicMock
import os
from observability.self_heal_hook import attempt_self_healing


class TestSelfHealingHook(unittest.TestCase):
    @patch("subprocess.run")
    def test_preflight_pass(self, mock_run):
        # Mock pre-flight check returning 0 (success)
        # Mock healing engine returning 0 (success)
        mock_run.side_effect = [
            MagicMock(returncode=0),  # Pre-flight
            MagicMock(returncode=0),  # Healing
        ]

        result = attempt_self_healing("error", os.getcwd(), health_check_cmd="true")

        self.assertTrue(result)
        # Should have called subprocess.run twice (pre-flight and healing,
        # but the code says if pre-flight passes, it returns True and skips healing)
        # Let's check the code:
        # if check_result.returncode == 0:
        #     print("[Self-Healing] Pre-flight check passed. Service appears healthy. Skipping healing.")
        #     return True

        self.assertEqual(mock_run.call_count, 1)

    @patch("subprocess.run")
    def test_preflight_fail(self, mock_run):
        # Mock pre-flight check returning non-zero (failure)
        # Mock healing engine returning 0 (success)
        mock_run.side_effect = [
            MagicMock(returncode=1),  # Pre-flight
            MagicMock(returncode=0),  # Healing
        ]

        result = attempt_self_healing("error", os.getcwd(), health_check_cmd="false")

        self.assertTrue(result)
        self.assertEqual(mock_run.call_count, 2)

    @patch("subprocess.run")
    def test_healing_fail(self, mock_run):
        # Mock pre-flight check returning non-zero (failure)
        # Mock healing engine returning 1 (failure)
        mock_run.side_effect = [
            MagicMock(returncode=1),  # Pre-flight
            MagicMock(returncode=1, stderr="error message"),  # Healing
        ]

        result = attempt_self_healing("error", os.getcwd(), health_check_cmd="false")

        self.assertFalse(result)
        self.assertEqual(mock_run.call_count, 2)

    @patch("subprocess.run")
    def test_preflight_exception(self, mock_run):
        # Mock pre-flight check raising exception, but second call (healing) succeeding
        mock_run.side_effect = [
            Exception("Pre-flight crash"),
            MagicMock(returncode=0),
        ]

        result = attempt_self_healing("error", os.getcwd(), health_check_cmd="true")

        self.assertTrue(result)
        self.assertEqual(mock_run.call_count, 2)


if __name__ == "__main__":
    unittest.main()
