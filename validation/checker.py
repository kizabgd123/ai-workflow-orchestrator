import logging
from typing import Dict, Any, List

logger = logging.getLogger("ValidationChecker")

class ValidationChecker:
    """
    Verifies that the execution results match the expected outcomes.
    """
    
    def validate_results(self, execution_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes the execution report and provides a validation summary.
        """
        logger.info("Validating execution results...")
        
        success_count = 0
        total_tasks = len(execution_report.get("details", []))
        failures = []
        
        for item in execution_report.get("details", []):
            task = item.get("task")
            result = item.get("result", {})
            
            if result.get("success"):
                success_count += 1
            else:
                failures.append({
                    "task": task,
                    "error": result.get("stderr") or result.get("message") or "Unknown error"
                })
        
        is_valid = (success_count == total_tasks) if total_tasks > 0 else False
        
        validation_report = {
            "is_valid": is_valid,
            "success_rate": (success_count / total_tasks) if total_tasks > 0 else 0,
            "failures": failures,
            "message": "All tasks validated successfully" if is_valid else f"Validation failed for {len(failures)} tasks"
        }
        
        logger.info(f"Validation Result: {validation_report['message']}")
        return validation_report
