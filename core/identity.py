import os
import sys
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class IdentityGuard:
    """
    Implements the cm-identity-guard pattern from CodyMaster.
    Prevents operations on unauthorized projects or databases.
    """

    def __init__(self):
        # Definitions of what is "LOCKED" for this workspace
        self.allowed_gcp_projects = ["sixth-hawk-492717-m1", "portfolio-hub-prod"]
        self.locked_mongodb_db = "ai_workflow_orchestrator"

    def verify_environment(self) -> bool:
        """
        Verifies that current ENV matches the locked project identity.
        """
        # Allow skipping check for non-GCP environments (like Hugging Face)
        if os.environ.get("SKIP_IDENTITY_CHECK") == "true":
            logger.info("⚠️  Identity check skipped via SKIP_IDENTITY_CHECK.", extra={"event": "security.identity_check", "status": "skipped"})
            return True

        current_gcp = os.environ.get("GOOGLE_CLOUD_PROJECT")
        current_mongo_db = os.environ.get("MONGODB_DATABASE")

        if current_gcp not in self.allowed_gcp_projects:
            logger.critical(
                f"IDENTITY MISMATCH: Expected one of {self.allowed_gcp_projects}, got {current_gcp}",
                extra={"event": "security.identity_check", "status": "failed", "error": "gcp_mismatch"}
            )
            return False

        if current_mongo_db != self.locked_mongodb_db:
            logger.critical(
                f"IDENTITY MISMATCH: Expected MongoDB DB {self.locked_mongodb_db}, got {current_mongo_db}",
                extra={"event": "security.identity_check", "status": "failed", "error": "mongo_mismatch"}
            )
            return False

        logger.info(
            f"✅ Identity Verified: {current_gcp} | {self.locked_mongodb_db}",
            extra={"event": "security.identity_check", "status": "success", "gcp_project": current_gcp}
        )
        return True


def enforce_identity():
    """Entrypoint to be called in main.py before starting server."""
    guard = IdentityGuard()
    if not guard.verify_environment():
        print("\n[!] SECURITY ALERT: Project identity mismatch detected.")
        print("[!] Stopping to prevent cross-project data contamination.")
        sys.exit(1)
