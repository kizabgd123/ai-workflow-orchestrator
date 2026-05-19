import subprocess
import os
import logging
from typing import Optional

logger = logging.getLogger("SelfHealer")

def attempt_self_healing(
    error_message: str, working_dir: str, health_check_cmd: Optional[str] = None
) -> bool:
    """
    Triggers an automated self-healing loop for identified production failures.
    Integrates with the specialized diagnosis engine.
    """
    engine_path = os.path.abspath(
        "/home/kizabgd/.gemini/extensions/pickle-rick/skills/self-healer/scripts/diagnosis_engine.py"
    )

    print(f"\n[Self-Healing] TRACE: {error_message[:200]}...")

    # 1. Pre-flight Verification (Circuit Breaker)
    if health_check_cmd:
        try:
            check_result = subprocess.run(
                health_check_cmd, shell=True, capture_output=True, text=True, timeout=30
            )
            if check_result.returncode == 0:
                print("[Self-Healing] System reports healthy state. Aborting redundant healing.")
                return True
        except subprocess.TimeoutExpired:
            print("[Self-Healing] Health check timed out. Proceeding with emergency healing.")
        except Exception as e:
            print(f"[Self-Healing] Error during health check: {e}")

    # 2. Execute Diagnosis & Healing
    try:
        if not os.path.exists(engine_path):
            logger.error(f"Self-healer engine not found at {engine_path}")
            return False

        # Run diagnosis in auto-heal mode with a 5-minute timeout
        result = subprocess.run(
            [
                "python3",
                engine_path,
                "--error",
                error_message,
                "--auto-heal",
                "--working-dir",
                working_dir,
            ],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            print("[Self-Healing] SUCCESS: Patch applied and verified.")
            logger.info("Self-healing applied successfully.", extra={"event": "observability.self_heal", "status": "success"})
            return True
        else:
            print(f"[Self-Healing] FAILED: {result.stderr}")
            logger.error(f"Self-healing failed: {result.stderr}", extra={"event": "observability.self_heal", "status": "failed"})
            return False

    except subprocess.TimeoutExpired:
        print("[Self-Healing] CRITICAL: Healing engine timed out.")
        return False
    except Exception as e:
        print(f"[Self-Healing] CRITICAL ERROR: {e}")
        return False
