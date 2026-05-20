import sqlite3
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    audit_logged: bool

def init_audit_table():
    """Ensures the health_audit table exists."""
    conn = sqlite3.connect("memory/orchestrator_memory.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS health_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            endpoint TEXT,
            status TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

@app.get("/health", response_model=HealthResponse)
async def health_check():
    db_status = "unhealthy"
    audit_logged = False
    
    try:
        init_audit_table()
        conn = sqlite3.connect("memory/orchestrator_memory.db")
        
        # Check connectivity
        conn.execute("SELECT 1")
        db_status = "healthy"
        
        # Log the audit entry
        conn.execute(
            "INSERT INTO health_audit (endpoint, status) VALUES (?, ?)",
            ("/health", db_status)
        )
        conn.commit()
        conn.close()
        audit_logged = True
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy", 
        "version": "1.0.0",
        "database": db_status,
        "audit_logged": audit_logged
    }
