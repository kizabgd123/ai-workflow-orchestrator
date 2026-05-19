import asyncio
import os
import sys
from orchestrator.engine import WorkflowOrchestrator
from core.identity import enforce_identity
from core.logging_setup import setup_logging
from observability.self_heal_hook import attempt_self_healing


async def main():
    # 0. Setup Structured Logging (Zero Script QA)
    setup_logging()

    if len(sys.argv) < 2:
        print('Usage: python main.py "your task description"')
        return

    user_request = sys.argv[1]

    # 1. Identity Check (Safety Pattern)
    enforce_identity()

    # 2. Check for API Key
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not found.")
        print("Please set it with: export GOOGLE_API_KEY='your-key-here'")
        return

    print("\n" + "*" * 60)
    print("AI WORKFLOW ORCHESTRATOR")
    print("*" * 60)
    print(f"Request: {user_request}\n")

    orchestrator = WorkflowOrchestrator()

    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            await orchestrator.process_request(user_request)
            print("Workflow completed successfully.")
            return
        except Exception as e:
            print(f"Workflow failed (attempt {attempt + 1}): {str(e)}")

            if attempt < max_retries:
                # Attempt self-healing
                health_check = os.environ.get("HEALTH_CHECK_CMD")
                success = attempt_self_healing(
                    str(e), os.getcwd(), health_check_cmd=health_check
                )
                if success:
                    print("Self-healing triggered. Retrying...")
                    continue
                else:
                    print("Self-healing failed. Escalating...")
                    break
            else:
                print("Max retries exceeded.")
                break


if __name__ == "__main__":
    asyncio.run(main())
