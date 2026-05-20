import uuid
from typing import Dict, Any, Optional
from datetime import datetime

class JobManager:
    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}

    def create_job(self) -> str:
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = {"status": "pending", "result": None, "events": []}
        return job_id

    def update_job(self, job_id: str, status: str, result: Any = None):
        if job_id in self.jobs:
            self.jobs[job_id]["status"] = status
            if result is not None:
                self.jobs[job_id]["result"] = result

    def add_event(self, job_id: str, event_type: str, data: Any = None):
        if job_id in self.jobs:
            event = {
                "type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data or {}
            }
            self.jobs[job_id]["events"].append(event)

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self.jobs.get(job_id)

job_manager = JobManager()
