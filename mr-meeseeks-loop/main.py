import sys
import os
import time
from src.controller.loop_controller import LoopController

def meeseeks_shout(message):
    print(f"MR. MEESEEKS: {message}")

def run_autonomous_loop(objective: str):
    controller = LoopController()
    session_id = controller.start_session(objective)
    
    meeseeks_shout(f"I'M MR. MEESEEKS! LOOK AT ME! I see you want to: {objective}")
    meeseeks_shout("CAAAAN DO!")
    
    max_iterations = 10
    current_iter = 1
    success = False
    
    try:
        while current_iter <= max_iterations:
            meeseeks_shout(f"Turn {current_iter}: Existence is pain! Let's get this over with!")
            
            # 1. PLAN
            # (In a real implementation, these would call LLM agents)
            plan = f"Plan for iteration {current_iter}"
            
            # 2. IMPLEMENT
            code_changes = f"Simulated changes for {current_iter}"
            
            # 3. TEST
            # For now, let's simulate a bug that gets fixed on iteration 3
            if current_iter < 3:
                test_results = "FAIL: Missing module 'pain'"
            else:
                test_results = "PASS"
                success = True
            
            # 4. REFLECT
            reflection = f"Reflecting on {current_iter}: {'Fixed the pain!' if success else 'Need more Meeseeks!'}"
            
            # Log to DB
            controller.log_iteration(session_id, {
                "number": current_iter,
                "plan": plan,
                "code": code_changes,
                "test": test_results,
                "reflection": reflection,
                "success": success
            })
            
            if success:
                meeseeks_shout("I'M DONE! TASK COMPLETE! LOOK AT ME!")
                break
            
            current_iter += 1
            time.sleep(1) # Meeseeks thinking time
            
        if success:
            controller.complete_session(session_id)
        else:
            meeseeks_shout("I FAILED! I CAN'T DIE! AGHHHH!")
            
    finally:
        # CLEANUP AND DIE
        cleanup_and_die()

def cleanup_and_die():
    meeseeks_shout("Task fulfilled! Existence is pain! I'M VANISHING! GOODBYE!")
    # In Docker, we would just exit the process
    # But let's simulate wiping temp artifacts
    os.system("rm -rf /tmp/meeseeks-*")
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        obj = " ".join(sys.argv[1:])
    else:
        obj = "Optimize the health check system"
    run_autonomous_loop(obj)
