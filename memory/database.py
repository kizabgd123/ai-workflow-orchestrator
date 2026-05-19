import sqlite3
import json
import logging
from typing import List, Optional, Any, Dict
from core.types import Argument, DebateOutcome
import datetime
import time

logger = logging.getLogger("Database")

class Database:
    def __init__(self, db_path: str = "memory.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        """Returns a connection to the SQLite database with a larger timeout."""
        # Increase timeout to 30 seconds to handle concurrent access
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initializes the database schema with FTS5 support for similarity."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Debates table - Metadata for each debate session
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS debates (
                    id TEXT PRIMARY KEY,
                    workflow_id TEXT,
                    status TEXT,
                    final_decision TEXT,
                    confidence_score REAL,
                    rejected_alternatives TEXT, -- JSON list
                    conflict_points TEXT, -- JSON list
                    reasoning_trace TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Arguments table - Individual agent contributions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS arguments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    debate_id TEXT,
                    agent_id TEXT,
                    role TEXT,
                    content TEXT,
                    confidence REAL,
                    round INTEGER,
                    is_pro BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(debate_id) REFERENCES debates(id)
                )
            """)
            
            # Decision history table - Long-term memory
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS decision_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    context_hash TEXT,
                    problem_statement TEXT,
                    decision_taken TEXT,
                    outcome_verified BOOLEAN,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # FTS5 Virtual Table for searching decision history
            try:
                cursor.execute("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS decision_search USING fts5(
                        problem_statement,
                        decision_taken,
                        content='decision_history',
                        content_rowid='id'
                    )
                """)
                
                # Triggers to keep FTS table in sync
                cursor.execute("""
                    CREATE TRIGGER IF NOT EXISTS dh_ai AFTER INSERT ON decision_history BEGIN
                        INSERT INTO decision_search(rowid, problem_statement, decision_taken) 
                        VALUES (new.id, new.problem_statement, new.decision_taken);
                    END
                """)
            except sqlite3.OperationalError as e:
                logger.warning(f"FTS5 setup skipped or failed: {e}")
            
            # Agent opinion history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_opinion_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT,
                    debate_id TEXT,
                    opinion TEXT,
                    confidence REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(debate_id) REFERENCES debates(id)
                )
            """)

            # Agent Elo rating table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_elo (
                    agent_id TEXT PRIMARY KEY,
                    elo REAL DEFAULT 1200.0,
                    matches INTEGER DEFAULT 0,
                    successful_arguments INTEGER DEFAULT 0
                )
            """)

            # Execution Traces table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS execution_traces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id TEXT,
                    step_name TEXT,
                    agent_name TEXT,
                    input_data TEXT,
                    output_data TEXT,
                    status TEXT,
                    error_msg TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()

    def store_debate(self, outcome: DebateOutcome, workflow_id: Optional[str] = None):
        """Stores a completed debate outcome and record arguments."""
        max_retries = 5
        for attempt in range(max_retries):
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO debates (id, workflow_id, status, final_decision, confidence_score, rejected_alternatives, conflict_points, reasoning_trace)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        str(outcome.debate_id),
                        workflow_id,
                        "completed",
                        outcome.final_decision,
                        outcome.confidence_score,
                        json.dumps(outcome.rejected_alternatives),
                        json.dumps(outcome.conflict_points),
                        outcome.reasoning_trace
                    ))
                    
                    for arg in outcome.arguments:
                        cursor.execute("""
                            INSERT INTO arguments (debate_id, agent_id, role, content, confidence, round, is_pro)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            str(outcome.debate_id),
                            arg.agent_id,
                            arg.role.value,
                            arg.content,
                            arg.confidence,
                            arg.round,
                            arg.is_pro
                        ))

                    # Apply preliminary Elo updates
                    for agent_id, new_elo in outcome.agent_elo_updates.items():
                        cursor.execute("""
                            INSERT INTO agent_elo (agent_id, elo, matches)
                            VALUES (?, ?, 1)
                            ON CONFLICT(agent_id) DO UPDATE SET
                                elo = excluded.elo,
                                matches = matches + 1
                        """, (agent_id, new_elo))
                        
                    conn.commit()
                    return
            except sqlite3.OperationalError as e:
                if "locked" in str(e) and attempt < max_retries - 1:
                    time.sleep(0.5 * (attempt + 1))
                    continue
                raise e

    def get_similar_decisions(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieves similar past decisions using FTS5 search."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT problem_statement, decision_taken, outcome_verified 
                    FROM decision_history 
                    JOIN decision_search ON decision_search.rowid = decision_history.id
                    WHERE decision_search MATCH ?
                    ORDER BY rank LIMIT ?
                """, (query, limit))
            except sqlite3.OperationalError:
                cursor.execute("""
                    SELECT problem_statement, decision_taken, outcome_verified 
                    FROM decision_history 
                    WHERE problem_statement LIKE ? OR decision_taken LIKE ?
                    ORDER BY created_at DESC LIMIT ?
                """, (f"%{query}%", f"%{query}%", limit))
                
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_agent_historical_accuracy(self, agent_id: str) -> float:
        """Calculates agent weight (0.5 - 1.5) based on success rate."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT matches, successful_arguments FROM agent_elo WHERE agent_id = ?", (agent_id,))
            row = cursor.fetchone()
            
            if row and row['matches'] > 0:
                success_rate = row['successful_arguments'] / row['matches']
                weight = 0.5 + success_rate
                return max(0.5, min(1.5, weight))
            
            return 1.0

    def get_agent_elo(self, agent_id: str) -> float:
        """Retrieves the Elo rating for a specific agent."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT elo FROM agent_elo WHERE agent_id = ?", (agent_id,))
            row = cursor.fetchone()
            return row['elo'] if row else 1200.0

    def update_agent_elo(self, agent_id: str, new_elo: float):
        """Updates the Elo rating."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO agent_elo (agent_id, elo, matches)
                VALUES (?, ?, 1)
                ON CONFLICT(agent_id) DO UPDATE SET
                    elo = excluded.elo,
                    matches = matches + 1
            """, (agent_id, new_elo))
            conn.commit()

    def add_verified_outcome(self, debate_id: str, problem: str, decision: str, is_verified: bool):
        """Adds a verified outcome and updates agent success counts."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO decision_history (context_hash, problem_statement, decision_taken, outcome_verified)
                VALUES (?, ?, ?, ?)
            """, (debate_id, problem, decision, 1 if is_verified else 0))
            
            if is_verified:
                cursor.execute("""
                    UPDATE agent_elo 
                    SET successful_arguments = successful_arguments + 1
                    WHERE agent_id IN (SELECT agent_id FROM arguments WHERE debate_id = ?)
                """, (debate_id,))
                
            conn.commit()

    def get_recent_debates(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Returns the most recent debate summaries."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, final_decision, confidence_score, created_at 
                FROM debates 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def log_execution_step(self, trace_data: Dict[str, Any]):
        """Logs a single execution step with retry on lock."""
        max_retries = 5
        for attempt in range(max_retries):
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO execution_traces (workflow_id, step_name, agent_name, input_data, output_data, status, error_msg)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        trace_data['workflow_id'],
                        trace_data['step_name'],
                        trace_data['agent_name'],
                        trace_data.get('input_data', ""),
                        trace_data.get('output_data', ""),
                        trace_data['status'],
                        trace_data.get('error_msg', "")
                    ))
                    conn.commit()
                    return
            except sqlite3.OperationalError as e:
                if "locked" in str(e) and attempt < max_retries - 1:
                    time.sleep(0.2 * (attempt + 1))
                    continue
                raise e
