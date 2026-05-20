import uuid
import datetime
from typing import Dict, Any, List
from core.base import Orchestrator, AgentMode
from debate.engine import DebateEngine
from memory.system import MemorySystem

class WorkflowOrchestrator(Orchestrator):
    def __init__(self, memory_system: MemorySystem):
        super().__init__(memory_system)
        self.debate_engine = DebateEngine(memory_system)

    async def execute_workflow(self, request: str):
        workflow_id = str(uuid.uuid4())
        print(f"[*] Starting workflow: {workflow_id} for request: {request}")

        # 1. load_memory_context()
        similar_debates = self.memory.find_similar_debates(request)
        context = {"similar_history": similar_debates, "request": request}

        # 2. classify_request() & 3. retrieve_similar_workflows()
        # (Simplified for now)
        request_type = "COMPLEX_TASK"
        
        # 4. build_initial_plan()
        plan = f"Execute multi-agent debate for: {request}"
        
        # Store workflow start
        with self.memory._get_connection() as conn:
            conn.execute('''
                INSERT INTO workflows (id, request_type, plan, status, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (workflow_id, request_type, plan, "DEBATING", datetime.datetime.now().isoformat()))

        # 5. EXECUTE DEBATE ENGINE
        participants = list(self.agents.values())
        debate_result = await self.debate_engine.run_debate(request, participants, context)
        
        print(f"[*] Debate finished. Consensus: {debate_result['consensus_decision']} (Score: {debate_result['confidence_score']:.2f})")

        # 6. resolve_final_decision_from_debate()
        if debate_result['consensus_decision'] == "APPROVED":
            # 7. assign_execution_agents() & 8. execute_plan()
            execution_status = "SUCCESS"
            
            # Example execution step logging
            self.memory.log_execution_step({
                "workflow_id": workflow_id,
                "step_name": "Main Execution",
                "agent_name": "Solution",
                "input_data": request,
                "output_data": "Execution complete based on debate consensus",
                "status": "COMPLETED"
            })
        else:
            execution_status = "REJECTED_BY_DEBATE"

        # 9. validate_results()
        validation_status = "VALIDATED" if execution_status == "SUCCESS" else "SKIPPED"

        # 10. store_all_in_memory() & 11. audit log final decision
        with self.memory._get_connection() as conn:
            conn.execute('''
                UPDATE workflows SET status = ? WHERE id = ?
            ''', (f"COMPLETED_{execution_status}", workflow_id))
            
            conn.execute('''
                INSERT INTO decision_history (workflow_id, debate_id, decision, outcome, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (workflow_id, debate_result['id'], debate_result['consensus_decision'], execution_status, datetime.datetime.now().isoformat()))

        print(f"[*] Workflow {workflow_id} finished with status: {execution_status}")
        return {
            "workflow_id": workflow_id,
            "debate_id": debate_result['id'],
            "status": execution_status,
            "decision": debate_result['consensus_decision']
        }
