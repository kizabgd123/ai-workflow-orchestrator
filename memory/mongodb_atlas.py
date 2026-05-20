"""
MongoDB Atlas MCP Integration for AI Workflow Orchestrator
Google Cloud Rapid Agent Hackathon - MongoDB Track

This module provides the MongoDB Atlas backend for the persistent
memory layer, replacing/extending the local SQLite implementation.
Uses MongoDB Atlas Vector Search for semantic similarity lookup
and Atlas App Services as the MCP server endpoint.
"""

import os
import json
import hashlib
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime

try:
    from pymongo import MongoClient
    from pymongo.collection import Collection
    from pymongo.errors import ConnectionFailure, OperationFailure
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

try:
    from core.types import Argument, DebateOutcome
except ImportError:
    # Fallback dataclasses if running standalone
    from dataclasses import dataclass, field
    
    @dataclass
    class Argument:
        agent_id: str
        role: Any
        content: str
        confidence: float
        round: int
    
    @dataclass
    class DebateOutcome:
        debate_id: str
        final_decision: str
        confidence_score: float
        rejected_alternatives: List[str] = field(default_factory=list)
        arguments: List[Any] = field(default_factory=list)
        conflict_points: List[str] = field(default_factory=list)
        reasoning_trace: str = ""


class MongoDBMemory:
    """
    MongoDB Atlas-backed persistent memory for the AI Workflow Orchestrator.
    
    Collections:
        - debates: Metadata for each debate session
        - arguments: Individual agent contributions per round
        - decision_history: Historical decisions with verified outcomes
        - agent_opinions: Per-agent opinion tracking for reliability scoring
        - workflows: Full workflow execution traces
    
    MCP Integration:
        Uses MongoDB Atlas MCP Server for agent tool access to:
        - find() — semantic similarity search via Vector Search
        - insertOne() — store debate outcomes
        - aggregate() — agent reliability scoring
    """
    
    COLLECTION_DEBATES = "debates"
    COLLECTION_ARGUMENTS = "arguments"
    COLLECTION_DECISIONS = "decision_history"
    COLLECTION_OPINIONS = "agent_opinions"
    COLLECTION_WORKFLOWS = "workflows"
    COLLECTION_AGENT_ELO = "agent_elo"

    def __init__(
        self,
        uri: Optional[str] = None,
        database_name: str = "ai_workflow_orchestrator",
        fallback_to_sqlite: bool = True
    ):
        self.uri = uri or os.environ.get("MONGODB_URI")
        self.database_name = database_name
        self.fallback_to_sqlite = fallback_to_sqlite
        self.client: Optional[MongoClient] = None
        self.db = None
        self._sqlite_fallback = None
        
        self._connect()
    
    def _connect(self):
        """Establishes connection to MongoDB Atlas."""
        if not MONGODB_AVAILABLE:
            print("[MEMORY] pymongo not installed. Run: pip install pymongo")
            self._init_sqlite_fallback()
            return
            
        if not self.uri:
            print("[MEMORY] MONGODB_URI not set. Falling back to SQLite.")
            self._init_sqlite_fallback()
            return
        
        try:
            self.client = MongoClient(
                self.uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            # Verify connection
            self.client.admin.command("ping")
            self.db = self.client[self.database_name]
            self._ensure_indexes()
            print(f"[MEMORY] ✅ Connected to MongoDB Atlas: {self.database_name}")
        except (ConnectionFailure, Exception) as e:
            print(f"[MEMORY] ⚠️  MongoDB connection failed: {e}")
            if self.fallback_to_sqlite:
                print("[MEMORY] Falling back to SQLite local memory.")
                self._init_sqlite_fallback()

    def _init_sqlite_fallback(self):
        """Initializes SQLite as a fallback memory backend."""
        if not self.fallback_to_sqlite:
            return
        try:
            from memory.database import Database
            self._sqlite_fallback = Database("storage/memory.db")
            print("[MEMORY] SQLite fallback active at storage/memory.db")
        except ImportError:
            print("[MEMORY] ⚠️  No memory backend available.")

    def _ensure_indexes(self):
        """Creates necessary indexes and search configurations."""
        if self.db is None:
            return
        try:
            # Index for fast debate lookups
            self.db[self.COLLECTION_DEBATES].create_index("workflow_id")
            self.db[self.COLLECTION_DEBATES].create_index("created_at")
            
            # Index for argument retrieval by debate
            self.db[self.COLLECTION_ARGUMENTS].create_index("debate_id")
            self.db[self.COLLECTION_ARGUMENTS].create_index("agent_id")
            
            # Index for decision history similarity lookup
            self.db[self.COLLECTION_DECISIONS].create_index("context_hash")
            self.db[self.COLLECTION_DECISIONS].create_index("created_at")
            
            # Index for agent performance tracking
            self.db[self.COLLECTION_OPINIONS].create_index("agent_id")
            
            print("[MEMORY] Indexes ensured.")
        except OperationFailure as e:
            print(f"[MEMORY] Index creation warning: {e}")

    @property
    def is_connected(self) -> bool:
        """Returns True if MongoDB Atlas is connected."""
        return self.db is not None

    # ─────────────────────────────────────────────────────────────
    # DEBATE STORAGE (MCP: insertOne on debates collection)
    # ─────────────────────────────────────────────────────────────

    def store_debate(self, outcome: DebateOutcome, workflow_id: Optional[str] = None):
        """
        Stores a completed debate outcome.
        MCP Tool: mongodb.insertOne({ collection: 'debates', ... })
        """
        debate_doc = {
            "debate_id": str(outcome.debate_id),
            "workflow_id": workflow_id,
            "status": "completed",
            "final_decision": outcome.final_decision,
            "confidence_score": outcome.confidence_score,
            "rejected_alternatives": outcome.rejected_alternatives,
            "conflict_points": getattr(outcome, 'conflict_points', []),
            "reasoning_trace": getattr(outcome, 'reasoning_trace', ''),
            "created_at": datetime.utcnow(),
        }
        
        if self.is_connected:
            try:
                self.db[self.COLLECTION_DEBATES].insert_one(debate_doc)
                
                # Apply Elo updates
                for agent_id, new_elo in getattr(outcome, 'agent_elo_updates', {}).items():
                    self.update_agent_elo(agent_id, new_elo)
                    
                print(f"[MEMORY] Debate {outcome.debate_id} stored in MongoDB Atlas.")
                return
            except Exception as e:
                print(f"[MEMORY] MongoDB write error: {e}")
        
        # Fallback
        if self._sqlite_fallback:
            self._sqlite_fallback.store_debate(outcome, workflow_id)

    def add_argument(self, debate_id: str, arg: Argument):
        """
        Stores an individual agent argument.
        MCP Tool: mongodb.insertOne({ collection: 'arguments', ... })
        """
        arg_doc = {
            "debate_id": debate_id,
            "agent_id": arg.agent_id,
            "role": arg.role.value if hasattr(arg.role, 'value') else str(arg.role),
            "content": arg.content,
            "confidence": arg.confidence,
            "round": arg.round,
            "created_at": datetime.utcnow(),
        }
        
        if self.is_connected:
            try:
                self.db[self.COLLECTION_ARGUMENTS].insert_one(arg_doc)
                return
            except Exception as e:
                print(f"[MEMORY] Argument write error: {e}")
        
        if self._sqlite_fallback:
            self._sqlite_fallback.add_argument(debate_id, arg)

    # ─────────────────────────────────────────────────────────────
    # SIMILARITY SEARCH (MCP: mongodb.find with vector search)
    # ─────────────────────────────────────────────────────────────

    def get_similar_decisions(self, problem_statement: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieves similar past decisions using context hash matching.
        For Atlas Vector Search, embed the problem_statement and use
        $vectorSearch aggregation stage.
        
        MCP Tool: mongodb.aggregate({ 
            collection: 'decision_history',
            pipeline: [{ $vectorSearch: { queryVector: [...], ... } }]
        })
        """
        # If the input is already a hex hash (e.g. from engine.py), use it directly
        is_hex = False
        if len(problem_statement) in (32, 64):
            try:
                int(problem_statement, 16)
                is_hex = True
            except ValueError:
                pass
                
        context_hash = problem_statement if is_hex else hashlib.md5(problem_statement.encode()).hexdigest()
        
        if self.is_connected:
            try:
                # First try exact hash match
                results = list(
                    self.db[self.COLLECTION_DECISIONS].find(
                        {"context_hash": context_hash},
                        {"_id": 0, "problem_statement": 1, "decision_taken": 1, "outcome_verified": 1}
                    ).limit(limit)
                )
                
                if results:
                    return results
                
                # If no exact match, return recent decisions as context
                results = list(
                    self.db[self.COLLECTION_DECISIONS].find(
                        {},
                        {"_id": 0, "problem_statement": 1, "decision_taken": 1, "outcome_verified": 1}
                    ).sort("created_at", -1).limit(limit)
                )
                return results
                
            except Exception as e:
                print(f"[MEMORY] Similarity search error: {e}")
        
        if self._sqlite_fallback:
            return self._sqlite_fallback.get_similar_decisions(context_hash)
        
        return []

    # ─────────────────────────────────────────────────────────────
    # AGENT RELIABILITY (MCP: mongodb.aggregate)
    # ─────────────────────────────────────────────────────────────

    def get_agent_historical_accuracy(self, agent_id: str) -> float:
        """
        Calculates agent reliability weight from historical debate performance.
        Uses MongoDB aggregation pipeline for efficient computation.
        
        MCP Tool: mongodb.aggregate({
            collection: 'arguments',
            pipeline: [
                { $match: { agent_id: agent_id } },
                { $group: { _id: "$agent_id", avg_confidence: { $avg: "$confidence" } } }
            ]
        })
        Returns weight between 0.5 and 1.5.
        """
        if self.is_connected:
            try:
                pipeline = [
                    {"$match": {"agent_id": agent_id}},
                    {"$group": {
                        "_id": "$agent_id",
                        "avg_confidence": {"$avg": "$confidence"},
                        "total_arguments": {"$sum": 1}
                    }}
                ]
                result = list(self.db[self.COLLECTION_ARGUMENTS].aggregate(pipeline))
                
                if result:
                    avg_conf = result[0].get("avg_confidence", 0.5)
                    # Map 0.0-1.0 confidence to 0.5-1.5 weight
                    weight = 0.5 + avg_conf
                    return max(0.5, min(1.5, weight))
                    
            except Exception as e:
                print(f"[MEMORY] Reliability query error: {e}")
        
        if self._sqlite_fallback:
            return self._sqlite_fallback.get_agent_historical_accuracy(agent_id)
        
        return 1.0  # Default neutral weight

    def get_agent_elo(self, agent_id: str) -> float:
        """Retrieves the Elo rating for a specific agent from MongoDB."""
        if self.is_connected:
            try:
                doc = self.db[self.COLLECTION_AGENT_ELO].find_one({"agent_id": agent_id})
                if doc and "elo" in doc:
                    return doc["elo"]
            except Exception as e:
                print(f"[MEMORY] Get Elo error: {e}")
        
        if self._sqlite_fallback:
            return self._sqlite_fallback.get_agent_elo(agent_id)
            
        return 1200.0

    def update_agent_elo(self, agent_id: str, new_elo: float):
        """Updates the Elo rating for a specific agent in MongoDB."""
        if self.is_connected:
            try:
                self.db[self.COLLECTION_AGENT_ELO].update_one(
                    {"agent_id": agent_id},
                    {"$set": {"elo": new_elo}, "$inc": {"matches": 1}},
                    upsert=True
                )
                return
            except Exception as e:
                print(f"[MEMORY] Update Elo error: {e}")
                
        if self._sqlite_fallback:
            self._sqlite_fallback.update_agent_elo(agent_id, new_elo)

    # ─────────────────────────────────────────────────────────────
    # VERIFIED OUTCOME STORAGE
    # ─────────────────────────────────────────────────────────────

    def add_verified_outcome(
        self,
        problem_statement: Optional[str] = None,
        decision: Optional[str] = None,
        is_verified: Optional[bool] = None,
        context_hash: Optional[str] = None,
        problem: Optional[str] = None
    ):
        """
        Records a verified outcome to improve future agent weighting.
        MCP Tool: mongodb.insertOne({ collection: 'decision_history', ... })
        Supports both keyword parameter sets (context_hash, problem, decision, is_verified)
        and positional parameter sets (problem_statement, decision, is_verified).
        """
        # Map parameters from either signature style
        p_statement = problem_statement or problem or ""
        dec = decision or ""
        verified = is_verified if is_verified is not None else False
        
        # Calculate context hash if not provided
        c_hash = context_hash
        if not c_hash:
            c_hash = hashlib.md5(p_statement.encode()).hexdigest() if p_statement else ""
            
        outcome_doc = {
            "context_hash": c_hash,
            "problem_statement": p_statement,
            "decision_taken": dec,
            "outcome_verified": verified,
            "created_at": datetime.utcnow(),
        }
        
        if self.is_connected:
            try:
                self.db[self.COLLECTION_DECISIONS].insert_one(outcome_doc)
                return
            except Exception as e:
                print(f"[MEMORY] Outcome write error: {e}")
        
        if self._sqlite_fallback:
            # Call SQLite fallback with the signature it expects
            self._sqlite_fallback.add_verified_outcome(
                context_hash=c_hash,
                problem=p_statement,
                decision=dec,
                is_verified=verified
            )

    # ─────────────────────────────────────────────────────────────
    # WORKFLOW TRACING
    # ─────────────────────────────────────────────────────────────

    def store_workflow_trace(self, trace_id: str, workflow_id: str, steps: List[Dict]):
        """
        Stores the full execution trace of a workflow.
        MCP Tool: mongodb.insertOne({ collection: 'workflows', ... })
        """
        trace_doc = {
            "trace_id": trace_id,
            "workflow_id": workflow_id,
            "steps": steps,
            "created_at": datetime.utcnow(),
        }
        
        if self.is_connected:
            try:
                self.db[self.COLLECTION_WORKFLOWS].insert_one(trace_doc)
                return
            except Exception as e:
                print(f"[MEMORY] Workflow trace write error: {e}")

    def get_recent_debates(self, limit: int = 5) -> List[Dict]:
        """Returns the most recent debate summaries for context loading."""
        if self.is_connected:
            try:
                results = list(
                    self.db[self.COLLECTION_DEBATES].find(
                        {},
                        {"_id": 0, "debate_id": 1, "final_decision": 1, 
                         "confidence_score": 1, "created_at": 1}
                    ).sort("created_at", -1).limit(limit)
                )
                return results
            except Exception as e:
                print(f"[MEMORY] Recent debates query error: {e}")
        return []

    def health_check(self) -> Dict[str, Any]:
        """Returns connection health status."""
        if self.is_connected:
            try:
                counts = {
                    "debates": self.db[self.COLLECTION_DEBATES].count_documents({}),
                    "arguments": self.db[self.COLLECTION_ARGUMENTS].count_documents({}),
                    "decisions": self.db[self.COLLECTION_DECISIONS].count_documents({}),
                }
                return {
                    "status": "connected",
                    "backend": "MongoDB Atlas",
                    "database": self.database_name,
                    "collections": counts,
                }
            except Exception as e:
                return {"status": "error", "backend": "MongoDB Atlas", "error": str(e)}
        
        if self._sqlite_fallback:
            return {"status": "connected", "backend": "SQLite (fallback)", "database": "storage/memory.db"}
        
        return {"status": "disconnected", "backend": "none"}

    def close(self):
        """Closes the MongoDB connection."""
        if self.client:
            self.client.close()
            print("[MEMORY] MongoDB connection closed.")


# ─────────────────────────────────────────────────────────────────────────────
# MCP SERVER TOOL DEFINITIONS
# Used by Google Cloud Agent Builder to define MCP tool capabilities
# ─────────────────────────────────────────────────────────────────────────────

MCP_TOOL_DEFINITIONS = [
    {
        "name": "store_debate_outcome",
        "description": "Stores a completed multi-agent debate outcome in MongoDB Atlas for future reference and learning.",
        "parameters": {
            "type": "object",
            "properties": {
                "debate_id": {"type": "string", "description": "Unique debate identifier"},
                "final_decision": {"type": "string", "description": "The consensus decision reached"},
                "confidence_score": {"type": "number", "description": "Overall confidence 0.0-1.0"},
                "rejected_alternatives": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["debate_id", "final_decision", "confidence_score"]
        }
    },
    {
        "name": "search_similar_decisions",
        "description": "Searches MongoDB Atlas for historically similar debates and decisions to inform current reasoning.",
        "parameters": {
            "type": "object",
            "properties": {
                "problem_statement": {"type": "string", "description": "Description of the current problem"},
                "limit": {"type": "integer", "description": "Maximum results to return", "default": 3}
            },
            "required": ["problem_statement"]
        }
    },
    {
        "name": "get_agent_reliability",
        "description": "Retrieves historical reliability score for a specific agent to weight their debate contributions.",
        "parameters": {
            "type": "object",
            "properties": {
                "agent_id": {"type": "string", "description": "The agent identifier"}
            },
            "required": ["agent_id"]
        }
    },
    {
        "name": "get_agent_elo",
        "description": "Retrieves historical Elo rating for a specific agent to weight their debate contributions dynamically.",
        "parameters": {
            "type": "object",
            "properties": {
                "agent_id": {"type": "string", "description": "The agent identifier"}
            },
            "required": ["agent_id"]
        }
    },
    {
        "name": "memory_health_check",
        "description": "Returns the current status of the MongoDB Atlas memory backend.",
        "parameters": {"type": "object", "properties": {}}
    }
]


if __name__ == "__main__":
    # Quick integration test
    print("Testing MongoDB Atlas Memory Integration...")
    memory = MongoDBMemory()
    health = memory.health_check()
    print(f"Health: {json.dumps(health, indent=2, default=str)}")
    memory.close()
