import unittest
import os
from core.identity import IdentityGuard

class TestIdentityGuard(unittest.TestCase):
    def setUp(self):
        self.guard = IdentityGuard()
        self.guard.locked_gcp_project = "test-project"
        self.guard.locked_mongodb_db = "test-db"

    def test_verify_environment_success(self):
        os.environ["GOOGLE_CLOUD_PROJECT"] = "test-project"
        os.environ["MONGODB_DATABASE"] = "test-db"
        self.assertTrue(self.guard.verify_environment())

    def test_verify_environment_mismatch_gcp(self):
        os.environ["GOOGLE_CLOUD_PROJECT"] = "wrong-project"
        os.environ["MONGODB_DATABASE"] = "test-db"
        self.assertFalse(self.guard.verify_environment())

    def test_verify_environment_mismatch_mongo(self):
        os.environ["GOOGLE_CLOUD_PROJECT"] = "test-project"
        os.environ["MONGODB_DATABASE"] = "wrong-db"
        self.assertFalse(self.guard.verify_environment())

    def test_skip_identity_check(self):
        os.environ["SKIP_IDENTITY_CHECK"] = "true"
        os.environ["GOOGLE_CLOUD_PROJECT"] = "anything"
        os.environ["MONGODB_DATABASE"] = "anything"
        self.assertTrue(self.guard.verify_environment())
        # Clean up
        del os.environ["SKIP_IDENTITY_CHECK"]

if __name__ == "__main__":
    unittest.main()
