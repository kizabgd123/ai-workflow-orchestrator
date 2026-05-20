from fastapi.testclient import TestClient
from api.health_check import app

client = TestClient(app)

import sqlite3

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"
    assert data["database"] == "healthy"
    assert data["audit_logged"] is True
    
    # Verify the database entry exists
    conn = sqlite3.connect("memory/orchestrator_memory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM health_audit ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    assert row is not None
    assert row[1] == "/health"
    assert row[2] == "healthy"
    conn.close()
