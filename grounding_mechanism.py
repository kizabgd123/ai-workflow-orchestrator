"""
Grounding Mechanism for AI Agent Systems
Verifies agent outputs against reliable sources to ensure accuracy and trustworthiness.
"""

import hashlib
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class VerificationStatus(Enum):
    """Status of claim verification"""
    VERIFIED = "verified"
    PARTIALLY_VERIFIED = "partially_verified"
    UNVERIFIED = "unverified"
    CONTRADICTED = "contradicted"
    ERROR = "error"


class SourceReliability(Enum):
    """Reliability levels for information sources"""
    AUTHORITATIVE = "authoritative"  # Peer-reviewed journals, official documentation
    HIGH = "high"  # Established news outlets, verified databases
    MEDIUM = "medium"  # Community-maintained resources, technical blogs
    LOW = "low"  # User-generated content, unverified sources
    UNKNOWN = "unknown"


@dataclass
class Claim:
    """Represents a factual claim made by an agent"""
    text: str
    source_agent: str
    timestamp: datetime = field(default_factory=datetime.now)
    claim_id: str = field(default_factory=lambda: "")
    confidence: float = field(default=0.0)
    
    def __post_init__(self):
        if not self.claim_id:
            self.claim_id = hashlib.sha256(
                f"{self.text}{self.timestamp.isoformat()}".encode()
            ).hexdigest()[:16]


@dataclass
class Source:
    """Represents a reliable information source"""
    name: str
    url: str
    reliability: SourceReliability
    source_type: str  # e.g., "documentation", "database", "api", "knowledge_base"
    last_updated: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VerificationResult:
    """Result of grounding verification"""
    claim: Claim
    status: VerificationStatus
    confidence_score: float
    supporting_sources: List[Source] = field(default_factory=list)
    contradictory_sources: List[Source] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    verification_timestamp: datetime = field(default_factory=datetime.now)
    notes: str = ""


class SourceConnector(ABC):
    """Abstract base class for connecting to different types of sources"""
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the source"""
        pass
    
    @abstractmethod
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search for information relevant to the query"""
        pass
    
    @abstractmethod
    def verify_claim(self, claim: str) -> Tuple[bool, List[str]]:
        """Verify a specific claim against the source"""
        pass


class DocumentationConnector(SourceConnector):
    """Connector for official documentation sources"""
    
    def __init__(self, docs_index: Dict[str, str]):
        """
        Initialize with a pre-built index of documentation.
        docs_index: {section_name: content}
        """
        self.docs_index = docs_index
        self.connected = False
    
    def connect(self) -> bool:
        self.connected = True
        logger.info("Documentation connector connected")
        return True
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        if not self.connected:
            raise ConnectionError("Not connected to documentation source")
        
        results = []
        query_lower = query.lower()
        
        for section, content in self.docs_index.items():
            if query_lower in content.lower():
                results.append({
                    "section": section,
                    "content": content,
                    "relevance": self._calculate_relevance(query, content)
                })
        
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results[:max_results]
    
    def verify_claim(self, claim: str) -> Tuple[bool, List[str]]:
        results = self.search(claim, max_results=3)
        if not results:
            return False, []
        
        evidence = [r["content"] for r in results if r["relevance"] > 0.7]
        return len(evidence) > 0, evidence
    
    def _calculate_relevance(self, query: str, content: str) -> float:
        """Simple relevance scoring based on keyword overlap"""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        intersection = query_words & content_words
        return len(intersection) / max(len(query_words), 1)


class DatabaseConnector(SourceConnector):
    """Connector for structured database sources"""
    
    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self.connection = None
        self.connected = False
    
    def connect(self) -> bool:
        # Placeholder for actual database connection logic
        # In production, this would use appropriate DB driver
        self.connected = True
        logger.info(f"Database connector connected to {self.db_config.get('name', 'unknown')}")
        return True
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        if not self.connected:
            raise ConnectionError("Not connected to database")
        
        # Placeholder implementation
        # In production, this would execute parameterized queries
        logger.warning("Database search not fully implemented - using mock data")
        return []
    
    def verify_claim(self, claim: str) -> Tuple[bool, List[str]]:
        # Placeholder for actual verification logic
        return False, []


class APIConnector(SourceConnector):
    """Connector for external API sources"""
    
    def __init__(self, api_config: Dict[str, Any]):
        self.api_config = api_config
        self.session = None
        self.connected = False
    
    def connect(self) -> bool:
        # Placeholder for API authentication and session setup
        self.connected = True
        logger.info(f"API connector connected to {self.api_config.get('endpoint', 'unknown')}")
        return True
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        if not self.connected:
            raise ConnectionError("Not connected to API")
        
        # Placeholder implementation
        # In production, this would make authenticated API calls
        return []
    
    def verify_claim(self, claim: str) -> Tuple[bool, List[str]]:
        # Placeholder for actual verification via API
        return False, []


class GroundingEngine:
    """
    Main engine for grounding and verifying agent outputs.
    Coordinates multiple source connectors and aggregates verification results.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.connectors: Dict[str, SourceConnector] = {}
        self.sources: Dict[str, Source] = {}
        self.verification_cache: Dict[str, VerificationResult] = {}
        self.min_confidence_threshold = self.config.get("min_confidence_threshold", 0.7)
        
    def register_source(self, source: Source, connector: SourceConnector) -> bool:
        """Register a new information source with its connector"""
        try:
            if connector.connect():
                self.sources[source.name] = source
                self.connectors[source.name] = connector
                logger.info(f"Registered source: {source.name} ({source.reliability.value})")
                return True
            else:
                logger.error(f"Failed to connect to source: {source.name}")
                return False
        except Exception as e:
            logger.error(f"Error registering source {source.name}: {str(e)}")
            return False
    
    def extract_claims(self, agent_output: str, agent_name: str) -> List[Claim]:
        """
        Extract factual claims from agent output.
        In production, this would use NLP techniques or a dedicated claim extraction model.
        """
        # Simplified claim extraction - in production, use more sophisticated methods
        claims = []
        
        # Split into sentences (simplified)
        sentences = [s.strip() for s in agent_output.replace('\n', ' ').split('.') if s.strip()]
        
        for sentence in sentences:
            # Filter for potentially factual statements
            if len(sentence) > 20 and not sentence.startswith(('What', 'How', 'Why', 'Can', 'Could')):
                claims.append(Claim(
                    text=sentence + ".",
                    source_agent=agent_name
                ))
        
        return claims
    
    def verify_claim(self, claim: Claim) -> VerificationResult:
        """Verify a single claim against all registered sources"""
        
        # Check cache first
        if claim.claim_id in self.verification_cache:
            cached_result = self.verification_cache[claim.claim_id]
            # Cache valid for 1 hour
            if (datetime.now() - cached_result.verification_timestamp).total_seconds() < 3600:
                return cached_result
        
        supporting_sources = []
        contradictory_sources = []
        all_evidence = []
        verification_scores = []
        
        for source_name, connector in self.connectors.items():
            try:
                is_supported, evidence = connector.verify_claim(claim.text)
                source = self.sources[source_name]
                
                if is_supported:
                    supporting_sources.append(source)
                    all_evidence.extend(evidence)
                    # Weight by source reliability
                    reliability_weight = self._get_reliability_weight(source.reliability)
                    verification_scores.append(reliability_weight)
                else:
                    # Check for contradictions (simplified - in production use NLI models)
                    if self._check_contradiction(claim.text, source_name):
                        contradictory_sources.append(source)
                        
            except Exception as e:
                logger.error(f"Error verifying claim against {source_name}: {str(e)}")
        
        # Calculate overall confidence score
        if verification_scores:
            confidence_score = sum(verification_scores) / len(verification_scores)
        else:
            confidence_score = 0.0
        
        # Determine verification status
        status = self._determine_status(
            supporting_sources, 
            contradictory_sources, 
            confidence_score
        )
        
        result = VerificationResult(
            claim=claim,
            status=status,
            confidence_score=confidence_score,
            supporting_sources=supporting_sources,
            contradictory_sources=contradictory_sources,
            evidence=all_evidence,
            notes=f"Verified against {len(self.connectors)} sources"
        )
        
        # Cache the result
        self.verification_cache[claim.claim_id] = result
        
        return result
    
    def verify_agent_output(self, agent_output: str, agent_name: str) -> Dict[str, Any]:
        """
        Complete verification pipeline for agent output.
        Returns structured verification report.
        """
        claims = self.extract_claims(agent_output, agent_name)
        
        if not claims:
            return {
                "status": "no_claims_to_verify",
                "message": "No factual claims detected in output",
                "overall_confidence": 1.0,
                "claims_verified": 0,
                "timestamp": datetime.now().isoformat()
            }
        
        results = []
        for claim in claims:
            result = self.verify_claim(claim)
            results.append(result)
        
        # Aggregate results
        verified_count = sum(1 for r in results if r.status == VerificationStatus.VERIFIED)
        partially_verified_count = sum(1 for r in results if r.status == VerificationStatus.PARTIALLY_VERIFIED)
        contradicted_count = sum(1 for r in results if r.status == VerificationStatus.CONTRADICTED)
        
        overall_confidence = sum(r.confidence_score for r in results) / len(results) if results else 0.0
        
        # Determine overall status
        if contradicted_count > 0:
            overall_status = "contains_contradictions"
        elif verified_count == len(results):
            overall_status = "fully_verified"
        elif verified_count + partially_verified_count == len(results):
            overall_status = "partially_verified"
        elif verified_count > 0:
            overall_status = "some_verified"
        else:
            overall_status = "unverified"
        
        return {
            "status": overall_status,
            "overall_confidence": overall_confidence,
            "claims_total": len(results),
            "claims_verified": verified_count,
            "claims_partially_verified": partially_verified_count,
            "claims_contradicted": contradicted_count,
            "claims_unverified": len(results) - verified_count - partially_verified_count - contradicted_count,
            "detailed_results": [
                {
                    "claim": r.claim.text,
                    "status": r.status.value,
                    "confidence": r.confidence_score,
                    "evidence_count": len(r.evidence)
                }
                for r in results
            ],
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_reliability_weight(self, reliability: SourceReliability) -> float:
        """Convert source reliability to numerical weight"""
        weights = {
            SourceReliability.AUTHORITATIVE: 1.0,
            SourceReliability.HIGH: 0.85,
            SourceReliability.MEDIUM: 0.7,
            SourceReliability.LOW: 0.5,
            SourceReliability.UNKNOWN: 0.3
        }
        return weights.get(reliability, 0.3)
    
    def _determine_status(
        self, 
        supporting: List[Source], 
        contradictory: List[Source], 
        confidence: float
    ) -> VerificationStatus:
        """Determine verification status based on evidence"""
        if contradictory:
            return VerificationStatus.CONTRADICTED
        elif supporting and confidence >= self.min_confidence_threshold:
            return VerificationStatus.VERIFIED
        elif supporting:
            return VerificationStatus.PARTIALLY_VERIFIED
        else:
            return VerificationStatus.UNVERIFIED
    
    def _check_contradiction(self, claim: str, source_name: str) -> bool:
        """
        Check if claim contradicts information in source.
        Simplified implementation - in production use NLI (Natural Language Inference) models.
        """
        # Placeholder - would use models like RoBERTa-MNLI or similar
        return False


class GroundingGuardrail:
    """
    Guardrail that uses grounding engine to validate agent outputs before delivery.
    Can block, flag, or modify outputs based on verification results.
    """
    
    def __init__(self, grounding_engine: GroundingEngine, config: Optional[Dict[str, Any]] = None):
        self.engine = grounding_engine
        self.config = config or {}
        self.action_thresholds = self.config.get("action_thresholds", {
            "block": 0.3,      # Block if confidence below this
            "flag": 0.6,       # Flag for review if confidence below this
            "warn": 0.8        # Show warning if confidence below this
        })
    
    def validate_output(self, agent_output: str, agent_name: str) -> Dict[str, Any]:
        """
        Validate agent output and determine appropriate action.
        Returns validation result with recommended action.
        """
        verification_report = self.engine.verify_agent_output(agent_output, agent_name)
        
        confidence = verification_report.get("overall_confidence", 0.0)
        status = verification_report.get("status", "unknown")
        
        # Determine action based on confidence thresholds
        if confidence < self.action_thresholds["block"]:
            action = "block"
            reason = f"Confidence score ({confidence:.2f}) below blocking threshold"
        elif confidence < self.action_thresholds["flag"]:
            action = "flag_for_review"
            reason = f"Confidence score ({confidence:.2f}) requires human review"
        elif confidence < self.action_thresholds["warn"]:
            action = "warn"
            reason = f"Confidence score ({confidence:.2f}) - user should be informed"
        else:
            action = "allow"
            reason = "Output passed grounding verification"
        
        # Special handling for contradictions
        if status == "contains_contradictions":
            action = "block"
            reason = "Output contains contradicted claims"
        
        return {
            "action": action,
            "reason": reason,
            "confidence": confidence,
            "status": status,
            "verification_report": verification_report,
            "timestamp": datetime.now().isoformat()
        }
    
    def apply_action(self, validation_result: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
        """
        Apply the recommended action.
        Returns: (allowed, message, modified_output)
        """
        action = validation_result["action"]
        
        if action == "block":
            return False, f"Output blocked: {validation_result['reason']}", None
        
        elif action == "flag_for_review":
            # In production, this would queue for human review
            return False, f"Output flagged for review: {validation_result['reason']}", None
        
        elif action == "warn":
            # Add warning to output but allow it through
            warning_message = f"⚠️ Note: This information has moderate verification confidence ({validation_result['confidence']:.0%}). Please verify critical claims."
            return True, warning_message, validation_result.get("original_output")
        
        else:  # allow
            return True, "Output verified successfully", None


# Example usage and demonstration
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create grounding engine
    engine = GroundingEngine()
    
    # Register some example sources
    docs_source = Source(
        name="Python_Docs",
        url="https://docs.python.org/3/",
        reliability=SourceReliability.AUTHORITATIVE,
        source_type="documentation"
    )
    
    # Create mock documentation index
    mock_docs = {
        "functions": "Python functions are defined using the def keyword followed by the function name and parentheses.",
        "lists": "Python lists are mutable sequences that can contain elements of different types.",
        "decorators": "Decorators in Python are functions that modify the behavior of other functions or classes."
    }
    
    docs_connector = DocumentationConnector(mock_docs)
    engine.register_source(docs_source, docs_connector)
    
    # Test claim extraction and verification
    test_output = """
    Python functions are defined using the def keyword. 
    Lists in Python can store multiple values.
    The sky is green and grass is blue.
    """
    
    print("\n=== Testing Grounding Engine ===\n")
    result = engine.verify_agent_output(test_output, "TestAgent")
    
    print(f"Overall Status: {result['status']}")
    print(f"Overall Confidence: {result['overall_confidence']:.2f}")
    print(f"Claims Verified: {result['claims_verified']}/{result['claims_total']}")
    print(f"Claims Contradicted: {result['claims_contradicted']}")
    
    print("\nDetailed Results:")
    for claim_result in result.get("detailed_results", []):
        print(f"\n  Claim: {claim_result['claim'][:60]}...")
        print(f"  Status: {claim_result['status']}")
        print(f"  Confidence: {claim_result['confidence']:.2f}")
    
    # Test guardrail
    print("\n=== Testing Grounding Guardrail ===\n")
    guardrail = GroundingGuardrail(engine)
    validation = guardrail.validate_output(test_output, "TestAgent")
    
    print(f"Action: {validation['action']}")
    print(f"Reason: {validation['reason']}")
    print(f"Confidence: {validation['confidence']:.2f}")
    
    allowed, message, _ = guardrail.apply_action(validation)
    print(f"\nFinal Decision: {'ALLOWED' if allowed else 'BLOCKED'}")
    print(f"Message: {message}")
