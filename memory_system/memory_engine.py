import sqlite3
import json
import logging
from typing import List, Optional, Any, Dict
from core.types import Argument, DebateOutcome

logger = logging.getLogger("MemoryEngine")

class MemoryEngine:
    def __init__(self, db_path: str = "memory.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initializes the database schema for adversarial memory."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Debates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS debates (
                    id TEXT PRIMARY KEY,
                    workflow_id TEXT,
                    status TEXT,
                    final_decision TEXT,
                    confidence_score REAL,
                    rejected_alternatives TEXT, -- JSON
                    conflict_points TEXT, -- JSON
                    reasoning_trace TEXT,
                    metadata TEXT, -- JSON
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Arguments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS arguments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    debate_id TEXT,
                    agent_id TEXT,
                    role TEXT,
                    content TEXT,
                    confidence REAL,
                    round INTEGER,
                    attacked_argument_id INTEGER, -- For adversarial tracing
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(debate_id) REFERENCES debates(id)
                )
            """)
            
            # Historical Decisions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS decision_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    context_hash TEXT,
                    problem_statement TEXT,
                    decision_taken TEXT,
                    outcome_verified BOOLEAN,
                    performance_metrics TEXT, -- JSON
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Agent Performance & Elo
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_performance (
                    agent_id TEXT PRIMARY KEY,
                    elo REAL DEFAULT 1200.0,
                    success_rate REAL DEFAULT 1.0,
                    critique_accuracy REAL DEFAULT 1.0, -- How often their critiques were valid
                    total_debates INTEGER DEFAULT 0
                )
            """)
            
            # Adversarial Conflicts Index
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conflict_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_hash TEXT,
                    description TEXT,
                    resolution_strategy TEXT,
                    frequency INTEGER DEFAULT 1
                )
            """)

            conn.commit()

    def store_debate_artifact(self, outcome: DebateOutcome):
        """Stores a full debate as a decision artifact."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO debates (id, status, final_decision, confidence_score, rejected_alternatives, conflict_points, reasoning_trace)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                str(outcome.debate_id),
                "completed",
                outcome.final_decision,
                outcome.confidence_score,
                json.dumps(outcome.rejected_alternatives),
                json.dumps(outcome.conflict_points),
                outcome.reasoning_trace
            ))
            
            for arg in outcome.arguments:
                cursor.execute("""
                    INSERT INTO arguments (debate_id, agent_id, role, content, confidence, round)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (str(outcome.debate_id), arg.agent_id, arg.role.value, arg.content, arg.confidence, arg.round))
            
            conn.commit()

    def retrieve_similar_adversarial_patterns(self, problem: str) -> List[Dict[str, Any]]:
        """Retrieves similar past conflicts to inform current debate."""
        # Implementation would use FTS5 or simple LIKE for pattern matching
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM conflict_patterns WHERE description LIKE ?", (f"%{problem[:20]}%",))
            return [dict(row) for row in cursor.fetchall()]

    def update_agent_elo_from_debate(self, agent_id: str, score: float):
        """Updates agent Elo based on debate outcome quality."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE agent_performance 
                SET elo = elo + ?, total_debates = total_debates + 1 
                WHERE agent_id = ?
            """, (score, agent_id))
            if cursor.rowcount == 0:
                cursor.execute("INSERT INTO agent_performance (agent_id, elo, total_debates) VALUES (?, ?, 1)", (agent_id, 1200.0 + score))
            conn.commit()

