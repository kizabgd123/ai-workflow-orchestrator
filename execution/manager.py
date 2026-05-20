import logging
from typing import Dict, Any, List
from .runner import ExecutionRunner

logger = logging.getLogger("ExecutionManager")

class ExecutionManager:
    """
    Coordinates the execution of plans approved by the debate system.
    Implements state tracking and rollback (Mandate 9).
    """
    
    def __init__(self):
        self.runner = ExecutionRunner()
        self.history: List[Dict[str, Any]] = []
        self.rollback_stack: List[Dict[str, Any]] = []

    async def execute_plan(self, final_decision: str) -> Dict[str, Any]:
        """
        Takes the final decision from the debate and executes the implied actions.
        """
        logger.info(f"Executing plan: {final_decision}")
        
        tasks = []
        if "PROCEED:" in final_decision:
            core_part = final_decision.split("PROCEED:")[1].split("WITH OPTIMIZATIONS:")[0]
            tasks = [t.strip() for t in core_part.split(",") if t.strip()]
            
        results = []
        for task in tasks:
            logger.info(f"Running task: {task}")
            try:
                result = await self.runner.execute_task(task)
                results.append({
                    "task": task,
                    "result": result
                })
                
                if result.get("success"):
                    # Record rollback action if provided by the runner
                    if "rollback_action" in result:
                        self.rollback_stack.append({
                            "task": task,
                            "rollback": result["rollback_action"]
                        })
                else:
                    logger.error(f"Task {task} failed. Triggering rollback...")
                    await self.rollback()
                    break
            except Exception as e:
                logger.error(f"Execution error on {task}: {e}")
                await self.rollback()
                break
            
        execution_report = {
            "overall_success": all(r["result"].get("success", False) for r in results) if results else False,
            "details": results,
            "rollback_triggered": not all(r["result"].get("success", False) for r in results) if results else True
        }
        
        self.history.append(execution_report)
        return execution_report

    async def rollback(self):
        """Rolls back the executed actions in reverse order."""
        logger.warning("Initiating Rollback sequence...")
        while self.rollback_stack:
            action = self.rollback_stack.pop()
            logger.info(f"Undoing: {action['task']}")
            try:
                # Assuming runner can execute rollback commands
                await self.runner.execute_task(action['rollback'])
            except Exception as e:
                logger.error(f"Rollback failed for {action['task']}: {e}")
        logger.info("Rollback complete.")
