import sqlite3
import os
from typing import List, Dict, Any, Optional
import datetime

class MemorySystem:
    def __init__(self, db_path: str = "memory/orchestrator_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Debates table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS debates (
                    id TEXT PRIMARY KEY,
                    context TEXT,
                    objective TEXT,
                    consensus_decision TEXT,
                    confidence_score REAL,
                    reasoning_trace TEXT,
                    created_at TIMESTAMP
                )
            ''')

            # Arguments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS arguments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    debate_id TEXT,
                    agent_name TEXT,
                    argument TEXT,
                    is_pro BOOLEAN,
                    confidence_score REAL,
                    created_at TIMESTAMP,
                    FOREIGN KEY(debate_id) REFERENCES debates(id)
                )
            ''')

            # Decision History table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS decision_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id TEXT,
                    debate_id TEXT,
                    decision TEXT,
                    outcome TEXT,
                    timestamp TIMESTAMP,
                    FOREIGN KEY(debate_id) REFERENCES debates(id)
                )
            ''')

            # Agent Opinion History table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_opinion_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_name TEXT,
                    debate_id TEXT,
                    opinion TEXT,
                    was_accepted BOOLEAN,
                    timestamp TIMESTAMP,
                    FOREIGN KEY(debate_id) REFERENCES debates(id)
                )
            ''')

            # Workflows table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workflows (
                    id TEXT PRIMARY KEY,
                    request_type TEXT,
                    plan TEXT,
                    status TEXT,
                    created_at TIMESTAMP
                )
            ''')

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
                    timestamp TIMESTAMP,
                    FOREIGN KEY(workflow_id) REFERENCES workflows(id)
                )
            ''')
            
            conn.commit()

    def store_debate(self, debate_data: Dict[str, Any]):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO debates (id, context, objective, consensus_decision, confidence_score, reasoning_trace, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                debate_id := debate_data['id'],
                debate_data['context'],
                debate_data['objective'],
                debate_data.get('consensus_decision'),
                debate_data.get('confidence_score'),
                debate_data.get('reasoning_trace'),
                datetime.datetime.now().isoformat()
            ))
            
            for arg in debate_data.get('arguments', []):
                cursor.execute('''
                    INSERT INTO arguments (debate_id, agent_name, argument, is_pro, confidence_score, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    debate_id,
                    arg['agent_name'],
                    arg['argument'],
                    arg.get('is_pro', True),
                    arg.get('confidence_score', 1.0),
                    datetime.datetime.now().isoformat()
                ))
            conn.commit()

    def find_similar_debates(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        # Basic implementation - will be expanded with embedding similarity in next phases
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM debates 
                WHERE context LIKE ? OR objective LIKE ? 
                ORDER BY created_at DESC LIMIT ?
            ''', (f'%{query}%', f'%{query}%', limit))
            return [dict(row) for row in cursor.fetchall()]

    def log_execution_step(self, trace_data: Dict[str, Any]):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO execution_traces (workflow_id, step_name, agent_name, input_data, output_data, status, error_msg, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trace_data['workflow_id'],
                trace_data['step_name'],
                trace_data['agent_name'],
                trace_data.get('input_data', ""),
                trace_data.get('output_data', ""),
                trace_data['status'],
                trace_data.get('error_msg', ""),
                datetime.datetime.now().isoformat()
            ))
            conn.commit()
