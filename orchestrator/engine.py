import asyncio
import hashlib
import json
import logging
import os
import uuid
from typing import Dict, List, Optional, Any

from core.types import AgentRole, AgentMode, DebateOutcome, Argument
from core.key_manager import KeyManager
from orchestrator.router import ModelRouter
from agents.factory import AgentFactory
from memory.database import Database
from debate.rounds import DebateManager
from execution.manager import ExecutionManager
from validation.checker import ValidationChecker

# Set up logging
logger = logging.getLogger("WorkflowOrchestrator")


class WorkflowOrchestrator:
    def __init__(self):
        self.key_manager = KeyManager.from_env()
        self.model_router = ModelRouter()
        self.db = Database()
        self.debate_manager = DebateManager(db=self.db)
        self.execution_manager = ExecutionManager()
        self.validation_checker = ValidationChecker()

    def _generate_hash(self, text: str) -> str:
        """Generates a SHA-256 hash of the input text."""
        return hashlib.sha256(text.encode()).hexdigest()

    def _log_step(self, workflow_id: str, step: int, name: str, agent_name: str, status: str = "success", input_data: Any = None, output_data: Any = None, error_msg: Optional[str] = None):
        """Helper to log execution traces for auditability."""
        self.db.log_execution_step({
            "workflow_id": workflow_id,
            "step_name": f"Step {step}: {name}",
            "agent_name": agent_name,
            "input_data": str(input_data) if input_data else "",
            "output_data": str(output_data) if output_data else "",
            "status": status,
            "error_msg": error_msg or ""
        })

    async def process_request(self, user_request: str, job_id: Optional[str] = None):
        """Processes a user request through the full 11-step production-grade AI workflow."""
        workflow_id = str(uuid.uuid4())
        request_hash = self._generate_hash(user_request)
        
        logger.info(f"Starting 11-step workflow [{workflow_id}] for request: {user_request}")

        # 1. load_memory_context()
        logger.info("Step 1: Loading Memory Context...")
        memory_context = self.db.get_recent_debates(limit=5)
        self._log_step(workflow_id, 1, "load_memory_context", "System", output_data=memory_context)

        # Initialize Analyst Agent
        analyst = AgentFactory.create_agent(
            AgentRole.ANALYST, "analyst-001", self.key_manager, self.model_router
        )

        # 2. classify_request()
        logger.info("Step 2: Classifying Request...")
        request_type = await analyst.think(
            prompt=f"Classify this request into a category: {user_request}"
        )
        self._log_step(workflow_id, 2, "classify_request", "analyst-001", input_data=user_request, output_data=request_type)

        # 3. retrieve_similar_workflows()
        logger.info("Step 3: Retrieving Similar Workflows...")
        similar_decisions = self.db.get_similar_decisions(user_request) # Using FTS5 search
        self._log_step(workflow_id, 3, "retrieve_similar_workflows", "System", output_data=similar_decisions)

        # 4. build_initial_plan()
        logger.info("Step 4: Building Initial Plan...")
        initial_plan = await analyst.think(
            prompt=f"Create a high-level execution plan for this {request_type} request: {user_request}",
            context=str(similar_decisions),
        )
        self._log_step(workflow_id, 4, "build_initial_plan", "analyst-001", output_data=initial_plan)

        # 5. EXECUTE DEBATE ENGINE
        logger.info("Step 5: Executing Multi-Agent Debate Engine...")
        agents = {
            AgentRole.ANALYST: analyst,
            AgentRole.SOLUTION: AgentFactory.create_agent(AgentRole.SOLUTION, "solution-001", self.key_manager, self.model_router),
            AgentRole.CRITIC: AgentFactory.create_agent(AgentRole.CRITIC, "critic-001", self.key_manager, self.model_router),
            AgentRole.SECURITY: AgentFactory.create_agent(AgentRole.SECURITY, "security-001", self.key_manager, self.model_router),
            AgentRole.OPTIMIZER: AgentFactory.create_agent(AgentRole.OPTIMIZER, "optimizer-001", self.key_manager, self.model_router),
            AgentRole.AGGREGATOR: AgentFactory.create_agent(AgentRole.AGGREGATOR, "aggregator-001", self.key_manager, self.model_router),
        }
        
        outcome = await self.debate_manager.run_debate(
            user_request, agents, memory_context=str(initial_plan), job_id=job_id
        )
        self._log_step(workflow_id, 5, "EXECUTE DEBATE ENGINE", "DebateManager", output_data=outcome.model_dump())

        # 6. resolve_final_decision_from_debate()
        logger.info("Step 6: Resolving Final Decision...")
        final_decision = outcome.final_decision
        self._log_step(workflow_id, 6, "resolve_final_decision", "Aggregator", output_data=final_decision)

        # 7. assign_execution_agents()
        logger.info("Step 7: Assigning Execution Agents...")
        # Selection logic based on outcome and role
        execution_agents = ["solution-001", "cli-agent-001"] if final_decision.startswith("PROCEED") else []
        self._log_step(workflow_id, 7, "assign_execution_agents", "System", output_data=execution_agents)

        # 8. execute_plan()
        execution_report = None
        if execution_agents:
            logger.info("Step 8: Executing Plan...")
            try:
                execution_report = await self.execution_manager.execute_plan(final_decision)
                self._log_step(workflow_id, 8, "execute_plan", "ExecutionManager", input_data=final_decision, output_data=execution_report)
            except Exception as e:
                self._log_step(workflow_id, 8, "execute_plan", "ExecutionManager", status="failed", error_msg=str(e))
                raise e

        # 9. validate_results()
        validation_report = None
        if execution_report:
            logger.info("Step 9: Validating Results...")
            validation_report = self.validation_checker.validate_results(execution_report)
            self._log_step(workflow_id, 9, "validate_results", "ValidationChecker", input_data=execution_report, output_data=validation_report)

        # 10. store_all_in_memory()
        logger.info("Step 10: Storing all artifacts in Memory...")
        # Store debate with arguments and update Elos
        self.db.store_debate(outcome, workflow_id=workflow_id)
        
        # Add to long-term decision history if verified
        if validation_report:
            self.db.add_verified_outcome(
                debate_id=str(outcome.debate_id),
                problem=user_request,
                decision=final_decision,
                is_verified=validation_report.get("is_valid", False)
            )
        self._log_step(workflow_id, 10, "store_all_in_memory", "System")

        # 11. audit log final decision
        logger.info("Step 11: Generating Audit Log...")
        self._print_reasoning_trace(outcome)
        self._save_trace_to_artifact(outcome)
        self._log_step(workflow_id, 11, "audit_log_final_decision", "System")

        return outcome

    def _save_trace_to_artifact(self, outcome: DebateOutcome):
        """Saves the reasoning trace to a JSON artifact for long-term audit."""
        os.makedirs("storage/traces", exist_ok=True)
        file_path = f"storage/traces/{outcome.debate_id}.json"
        with open(file_path, "w") as f:
            json.dump(outcome.model_dump(mode="json"), f, indent=2)
        logger.info(f"Trace saved to {file_path}")

    def _print_reasoning_trace(self, outcome: DebateOutcome):
        """Prints a structured reasoning trace for auditability."""
        print("\n" + "REASONING TRACE (Audit Log)")
        print("-" * 30)
        print(f"Trace ID: {outcome.debate_id}")
        print(f"Final Decision: {outcome.final_decision}")
        print(f"Overall Confidence Score: {outcome.confidence_score:.2f}")
        print("\nAgent Contributions & Confidence:")

        for arg in outcome.arguments:
            support = "PRO" if arg.is_pro else "CON"
            print(f"- {arg.role.value} ({arg.agent_id}) [{support}]:")
            print(f"  Confidence: {arg.confidence:.2f}")
            print(f"  Argument: {arg.content[:150]}...")

        if outcome.conflict_points:
            print("\nKey Conflict Points:")
            for conflict in outcome.conflict_points:
                print(f"- {conflict}")
        print("-" * 30 + "\n")
