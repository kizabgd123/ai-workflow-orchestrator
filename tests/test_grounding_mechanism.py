"""
Unit tests for grounding_mechanism.py

Covers: Claim/Source/VerificationResult dataclasses, SourceConnector
implementations (DocumentationConnector, DatabaseConnector, APIConnector),
GroundingEngine, and GroundingGuardrail.
"""

from datetime import datetime, timedelta

import pytest

from grounding_mechanism import (
    APIConnector,
    Claim,
    DatabaseConnector,
    DocumentationConnector,
    GroundingEngine,
    GroundingGuardrail,
    Source,
    SourceConnector,
    SourceReliability,
    VerificationResult,
    VerificationStatus,
)


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


class FakeConnector(SourceConnector):
    """Configurable fake connector used to drive GroundingEngine tests
    without depending on the behavior of the concrete connector classes."""

    def __init__(
        self,
        connect_result=True,
        raise_on_connect=False,
        verify_results=None,
        raise_on_verify=False,
    ):
        self.connect_result = connect_result
        self.raise_on_connect = raise_on_connect
        # verify_results: list of (bool, list[str]) tuples returned in order,
        # one per call to verify_claim. If a single tuple is given, it is
        # returned for every call.
        self._verify_results = verify_results if verify_results is not None else (False, [])
        self.raise_on_verify = raise_on_verify
        self.verify_calls = []

    def connect(self) -> bool:
        if self.raise_on_connect:
            raise RuntimeError("simulated connect failure")
        return self.connect_result

    def search(self, query, max_results=5):
        return []

    def verify_claim(self, claim):
        self.verify_calls.append(claim)
        if self.raise_on_verify:
            raise RuntimeError("simulated verify failure")
        if isinstance(self._verify_results, list):
            index = len(self.verify_calls) - 1
            return self._verify_results[index]
        return self._verify_results


def make_source(name="TestSource", reliability=SourceReliability.HIGH):
    return Source(
        name=name,
        url="https://example.com",
        reliability=reliability,
        source_type="test",
    )


# ---------------------------------------------------------------------------
# Claim
# ---------------------------------------------------------------------------


def test_claim_auto_generates_claim_id():
    claim = Claim(text="The sky is blue.", source_agent="agent-1")
    assert claim.claim_id != ""
    assert len(claim.claim_id) == 16
    # hex digest characters only
    int(claim.claim_id, 16)


def test_claim_id_deterministic_for_same_text_and_timestamp():
    ts = datetime(2024, 1, 1, 12, 0, 0)
    claim1 = Claim(text="Water boils at 100C.", source_agent="a", timestamp=ts)
    claim2 = Claim(text="Water boils at 100C.", source_agent="b", timestamp=ts)
    assert claim1.claim_id == claim2.claim_id


def test_claim_id_differs_for_different_text():
    ts = datetime(2024, 1, 1, 12, 0, 0)
    claim1 = Claim(text="Claim A.", source_agent="a", timestamp=ts)
    claim2 = Claim(text="Claim B.", source_agent="a", timestamp=ts)
    assert claim1.claim_id != claim2.claim_id


def test_claim_explicit_claim_id_is_preserved():
    claim = Claim(text="Some text.", source_agent="a", claim_id="custom-id-123")
    assert claim.claim_id == "custom-id-123"


def test_claim_default_confidence_is_zero():
    claim = Claim(text="Some text.", source_agent="a")
    assert claim.confidence == 0.0


# ---------------------------------------------------------------------------
# Source
# ---------------------------------------------------------------------------


def test_source_defaults():
    source = Source(
        name="Docs",
        url="https://docs.example.com",
        reliability=SourceReliability.AUTHORITATIVE,
        source_type="documentation",
    )
    assert source.last_updated is None
    assert source.metadata == {}


def test_source_metadata_default_not_shared_between_instances():
    source1 = make_source(name="S1")
    source2 = make_source(name="S2")
    source1.metadata["key"] = "value"
    assert source2.metadata == {}


# ---------------------------------------------------------------------------
# VerificationResult
# ---------------------------------------------------------------------------


def test_verification_result_defaults():
    claim = Claim(text="Some text that is long enough.", source_agent="a")
    result = VerificationResult(
        claim=claim,
        status=VerificationStatus.UNVERIFIED,
        confidence_score=0.0,
    )
    assert result.supporting_sources == []
    assert result.contradictory_sources == []
    assert result.evidence == []
    assert result.notes == ""
    assert isinstance(result.verification_timestamp, datetime)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


def test_verification_status_values():
    assert VerificationStatus.VERIFIED.value == "verified"
    assert VerificationStatus.PARTIALLY_VERIFIED.value == "partially_verified"
    assert VerificationStatus.UNVERIFIED.value == "unverified"
    assert VerificationStatus.CONTRADICTED.value == "contradicted"
    assert VerificationStatus.ERROR.value == "error"


def test_source_reliability_values():
    assert SourceReliability.AUTHORITATIVE.value == "authoritative"
    assert SourceReliability.HIGH.value == "high"
    assert SourceReliability.MEDIUM.value == "medium"
    assert SourceReliability.LOW.value == "low"
    assert SourceReliability.UNKNOWN.value == "unknown"


# ---------------------------------------------------------------------------
# SourceConnector (abstract base)
# ---------------------------------------------------------------------------


def test_source_connector_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        SourceConnector()


# ---------------------------------------------------------------------------
# DocumentationConnector
# ---------------------------------------------------------------------------


@pytest.fixture
def docs_index():
    return {
        "functions": "Python functions are defined using the def keyword and parentheses.",
        "lists": "Python lists are mutable sequences that can contain elements of different types.",
        "unrelated": "The weather today is sunny with a chance of rain.",
    }


def test_documentation_connector_connect_sets_connected(docs_index):
    connector = DocumentationConnector(docs_index)
    assert connector.connected is False
    assert connector.connect() is True
    assert connector.connected is True


def test_documentation_connector_search_requires_connection(docs_index):
    connector = DocumentationConnector(docs_index)
    with pytest.raises(ConnectionError):
        connector.search("functions")


def test_documentation_connector_search_finds_matching_section(docs_index):
    connector = DocumentationConnector(docs_index)
    connector.connect()
    results = connector.search("def keyword")
    assert len(results) >= 1
    assert results[0]["section"] == "functions"
    assert "relevance" in results[0]


def test_documentation_connector_search_no_match_returns_empty(docs_index):
    connector = DocumentationConnector(docs_index)
    connector.connect()
    results = connector.search("nonexistent phrase xyz")
    assert results == []


def test_documentation_connector_search_respects_max_results():
    docs_index = {
        "a": "python code example one",
        "b": "python code example two",
        "c": "python code example three",
        "d": "python code example four",
    }
    connector = DocumentationConnector(docs_index)
    connector.connect()
    results = connector.search("python code example", max_results=2)
    assert len(results) == 2


def test_documentation_connector_search_sorted_by_relevance_descending():
    # Both docs contain the query as a literal substring (required for a
    # search match), but "low" has an extra suffix glued onto the final
    # word ("exampleX"), which lowers its word-overlap relevance score
    # relative to "high" where the query's words match exactly.
    docs_index = {
        "low": "python code exampleX and something else entirely",
        "high": "python code example is clear and simple",
    }
    connector = DocumentationConnector(docs_index)
    connector.connect()
    results = connector.search("python code example")
    assert [r["section"] for r in results] == ["high", "low"]
    relevances = [r["relevance"] for r in results]
    assert relevances == sorted(relevances, reverse=True)
    assert relevances[0] > relevances[1]


def test_documentation_connector_verify_claim_supported(docs_index):
    connector = DocumentationConnector(docs_index)
    connector.connect()
    supported, evidence = connector.verify_claim(
        "Python functions are defined using the def keyword and parentheses"
    )
    assert supported is True
    assert len(evidence) > 0


def test_documentation_connector_verify_claim_unsupported(docs_index):
    connector = DocumentationConnector(docs_index)
    connector.connect()
    supported, evidence = connector.verify_claim("Bananas are a type of fruit")
    assert supported is False
    assert evidence == []


def test_documentation_connector_calculate_relevance_full_overlap():
    connector = DocumentationConnector({})
    relevance = connector._calculate_relevance("python code", "python code example")
    assert relevance == 1.0


def test_documentation_connector_calculate_relevance_no_overlap():
    connector = DocumentationConnector({})
    relevance = connector._calculate_relevance("java", "python code example")
    assert relevance == 0.0


def test_documentation_connector_calculate_relevance_empty_query_no_error():
    connector = DocumentationConnector({})
    relevance = connector._calculate_relevance("", "python code example")
    assert relevance == 0.0


# ---------------------------------------------------------------------------
# DatabaseConnector
# ---------------------------------------------------------------------------


def test_database_connector_connect_returns_true():
    connector = DatabaseConnector({"name": "test_db"})
    assert connector.connect() is True
    assert connector.connected is True


def test_database_connector_search_requires_connection():
    connector = DatabaseConnector({"name": "test_db"})
    with pytest.raises(ConnectionError):
        connector.search("query")


def test_database_connector_search_returns_empty_placeholder():
    connector = DatabaseConnector({"name": "test_db"})
    connector.connect()
    assert connector.search("query") == []


def test_database_connector_verify_claim_returns_false_placeholder():
    connector = DatabaseConnector({"name": "test_db"})
    connector.connect()
    supported, evidence = connector.verify_claim("any claim")
    assert supported is False
    assert evidence == []


# ---------------------------------------------------------------------------
# APIConnector
# ---------------------------------------------------------------------------


def test_api_connector_connect_returns_true():
    connector = APIConnector({"endpoint": "https://api.example.com"})
    assert connector.connect() is True
    assert connector.connected is True


def test_api_connector_search_requires_connection():
    connector = APIConnector({"endpoint": "https://api.example.com"})
    with pytest.raises(ConnectionError):
        connector.search("query")


def test_api_connector_search_returns_empty_placeholder():
    connector = APIConnector({"endpoint": "https://api.example.com"})
    connector.connect()
    assert connector.search("query") == []


def test_api_connector_verify_claim_returns_false_placeholder():
    connector = APIConnector({"endpoint": "https://api.example.com"})
    connector.connect()
    supported, evidence = connector.verify_claim("any claim")
    assert supported is False
    assert evidence == []


# ---------------------------------------------------------------------------
# GroundingEngine - construction & registration
# ---------------------------------------------------------------------------


def test_engine_default_config():
    engine = GroundingEngine()
    assert engine.config == {}
    assert engine.min_confidence_threshold == 0.7
    assert engine.connectors == {}
    assert engine.sources == {}
    assert engine.verification_cache == {}


def test_engine_custom_min_confidence_threshold():
    engine = GroundingEngine({"min_confidence_threshold": 0.9})
    assert engine.min_confidence_threshold == 0.9


def test_register_source_success():
    engine = GroundingEngine()
    source = make_source()
    connector = FakeConnector(connect_result=True)
    assert engine.register_source(source, connector) is True
    assert engine.sources[source.name] is source
    assert engine.connectors[source.name] is connector


def test_register_source_connect_failure_returns_false():
    engine = GroundingEngine()
    source = make_source()
    connector = FakeConnector(connect_result=False)
    assert engine.register_source(source, connector) is False
    assert source.name not in engine.sources
    assert source.name not in engine.connectors


def test_register_source_connect_raises_exception_is_handled():
    engine = GroundingEngine()
    source = make_source()
    connector = FakeConnector(raise_on_connect=True)
    assert engine.register_source(source, connector) is False
    assert source.name not in engine.sources


# ---------------------------------------------------------------------------
# GroundingEngine - extract_claims
# ---------------------------------------------------------------------------


def test_extract_claims_filters_short_and_question_sentences():
    engine = GroundingEngine()
    text = (
        "Python functions are defined using the def keyword. "
        "What is happening here. "
        "Short. "
        "How does this work in practice. "
        "Can you explain this in detail please. "
        "Could this possibly be true in every case. "
        "This is a sufficiently long factual statement about something."
    )
    claims = engine.extract_claims(text, "agent-1")
    texts = [c.text for c in claims]

    assert any("def keyword" in t for t in texts)
    assert any("sufficiently long factual statement" in t for t in texts)
    assert not any(t.startswith("What") for t in texts)
    assert not any(t.startswith("How") for t in texts)
    assert not any(t.startswith("Can") for t in texts)
    assert not any(t.startswith("Could") for t in texts)
    assert not any(t.strip(".") == "Short" for t in texts)


def test_extract_claims_appends_period_and_sets_agent():
    engine = GroundingEngine()
    text = "This is a sufficiently long factual statement about something"
    claims = engine.extract_claims(text, "agent-xyz")
    assert len(claims) == 1
    assert claims[0].text.endswith(".")
    assert claims[0].source_agent == "agent-xyz"


def test_extract_claims_empty_output_returns_no_claims():
    engine = GroundingEngine()
    claims = engine.extract_claims("What. How. Can.", "agent-1")
    assert claims == []


# ---------------------------------------------------------------------------
# GroundingEngine - verify_claim
# ---------------------------------------------------------------------------


def test_verify_claim_no_connectors_is_unverified():
    engine = GroundingEngine()
    claim = Claim(text="A claim with no registered sources.", source_agent="a")
    result = engine.verify_claim(claim)
    assert result.status == VerificationStatus.UNVERIFIED
    assert result.confidence_score == 0.0
    assert result.supporting_sources == []
    assert result.contradictory_sources == []


def test_verify_claim_supported_high_reliability_is_verified():
    engine = GroundingEngine()
    source = make_source("HighSource", SourceReliability.AUTHORITATIVE)
    connector = FakeConnector(verify_results=(True, ["supporting evidence"]))
    engine.register_source(source, connector)

    claim = Claim(text="A well supported claim.", source_agent="a")
    result = engine.verify_claim(claim)

    assert result.status == VerificationStatus.VERIFIED
    assert result.confidence_score == pytest.approx(1.0)
    assert source in result.supporting_sources
    assert "supporting evidence" in result.evidence


def test_verify_claim_supported_low_reliability_is_partially_verified():
    engine = GroundingEngine()
    source = make_source("LowSource", SourceReliability.LOW)
    connector = FakeConnector(verify_results=(True, ["weak evidence"]))
    engine.register_source(source, connector)

    claim = Claim(text="A weakly supported claim.", source_agent="a")
    result = engine.verify_claim(claim)

    assert result.status == VerificationStatus.PARTIALLY_VERIFIED
    assert result.confidence_score == pytest.approx(0.5)


def test_verify_claim_unsupported_is_unverified():
    engine = GroundingEngine()
    source = make_source("SomeSource", SourceReliability.HIGH)
    connector = FakeConnector(verify_results=(False, []))
    engine.register_source(source, connector)

    claim = Claim(text="An unsupported claim.", source_agent="a")
    result = engine.verify_claim(claim)

    assert result.status == VerificationStatus.UNVERIFIED
    assert result.confidence_score == 0.0


def test_verify_claim_contradiction_takes_precedence(monkeypatch):
    engine = GroundingEngine()
    source = make_source("ContradictSource", SourceReliability.HIGH)
    connector = FakeConnector(verify_results=(False, []))
    engine.register_source(source, connector)

    monkeypatch.setattr(engine, "_check_contradiction", lambda claim, name: True)

    claim = Claim(text="A contradicted claim.", source_agent="a")
    result = engine.verify_claim(claim)

    assert result.status == VerificationStatus.CONTRADICTED
    assert source in result.contradictory_sources


def test_verify_claim_connector_exception_is_handled_gracefully():
    engine = GroundingEngine()
    source = make_source("FailingSource", SourceReliability.HIGH)
    connector = FakeConnector(raise_on_verify=True)
    engine.register_source(source, connector)

    claim = Claim(text="A claim that triggers a connector error.", source_agent="a")
    result = engine.verify_claim(claim)

    assert result.status == VerificationStatus.UNVERIFIED
    assert result.supporting_sources == []
    assert result.contradictory_sources == []


def test_verify_claim_uses_cache_for_repeated_claim():
    engine = GroundingEngine()
    source = make_source("CacheSource", SourceReliability.HIGH)
    connector = FakeConnector(verify_results=(True, ["evidence"]))
    engine.register_source(source, connector)

    claim = Claim(text="A cached claim.", source_agent="a")
    result1 = engine.verify_claim(claim)
    result2 = engine.verify_claim(claim)

    assert result1 is result2
    assert len(connector.verify_calls) == 1


def test_verify_claim_cache_expires_after_one_hour():
    engine = GroundingEngine()
    source = make_source("ExpiringSource", SourceReliability.HIGH)
    connector = FakeConnector(verify_results=(True, ["evidence"]))
    engine.register_source(source, connector)

    claim = Claim(text="A claim whose cache expires.", source_agent="a")
    engine.verify_claim(claim)

    # Force the cached result to look stale.
    cached_result = engine.verification_cache[claim.claim_id]
    cached_result.verification_timestamp = datetime.now() - timedelta(seconds=4000)

    engine.verify_claim(claim)
    assert len(connector.verify_calls) == 2


# ---------------------------------------------------------------------------
# GroundingEngine - verify_agent_output
# ---------------------------------------------------------------------------


def test_verify_agent_output_no_claims():
    engine = GroundingEngine()
    result = engine.verify_agent_output("What is this. How about that.", "agent-1")
    assert result["status"] == "no_claims_to_verify"
    assert result["overall_confidence"] == 1.0
    assert result["claims_verified"] == 0


def test_verify_agent_output_fully_verified():
    engine = GroundingEngine()
    source = make_source("GoodSource", SourceReliability.AUTHORITATIVE)
    connector = FakeConnector(verify_results=(True, ["evidence"]))
    engine.register_source(source, connector)

    text = "This is a fully verifiable factual statement about the world."
    result = engine.verify_agent_output(text, "agent-1")

    assert result["status"] == "fully_verified"
    assert result["claims_verified"] == result["claims_total"]
    assert result["overall_confidence"] == pytest.approx(1.0)


def test_verify_agent_output_unverified():
    engine = GroundingEngine()
    source = make_source("BadSource", SourceReliability.HIGH)
    connector = FakeConnector(verify_results=(False, []))
    engine.register_source(source, connector)

    text = "This is a completely unverifiable factual statement about nothing."
    result = engine.verify_agent_output(text, "agent-1")

    assert result["status"] == "unverified"
    assert result["claims_verified"] == 0
    assert result["claims_contradicted"] == 0


def test_verify_agent_output_partially_verified():
    engine = GroundingEngine()
    source = make_source("WeakSource", SourceReliability.LOW)
    connector = FakeConnector(verify_results=(True, ["weak evidence"]))
    engine.register_source(source, connector)

    text = "This is a weakly supported factual statement about something."
    result = engine.verify_agent_output(text, "agent-1")

    assert result["status"] == "partially_verified"
    assert result["claims_partially_verified"] == result["claims_total"]


def test_verify_agent_output_contains_contradictions(monkeypatch):
    engine = GroundingEngine()
    source = make_source("ContradictSource", SourceReliability.HIGH)
    connector = FakeConnector(verify_results=(False, []))
    engine.register_source(source, connector)
    monkeypatch.setattr(engine, "_check_contradiction", lambda claim, name: True)

    text = "This is a contradicted factual statement about something."
    result = engine.verify_agent_output(text, "agent-1")

    assert result["status"] == "contains_contradictions"
    assert result["claims_contradicted"] == result["claims_total"]


def test_verify_agent_output_some_verified():
    engine = GroundingEngine()
    source = make_source("MixedSource", SourceReliability.AUTHORITATIVE)
    # First claim verified, second not.
    connector = FakeConnector(verify_results=[(True, ["evidence"]), (False, [])])
    engine.register_source(source, connector)

    text = (
        "This is the first fully verifiable factual statement here. "
        "This is the second entirely unverifiable factual statement here."
    )
    result = engine.verify_agent_output(text, "agent-1")

    assert result["claims_total"] == 2
    assert result["status"] == "some_verified"
    assert result["claims_verified"] == 1


def test_verify_agent_output_detailed_results_structure():
    engine = GroundingEngine()
    source = make_source("Source1", SourceReliability.AUTHORITATIVE)
    connector = FakeConnector(verify_results=(True, ["evidence"]))
    engine.register_source(source, connector)

    text = "This is a fully verifiable factual statement about the world."
    result = engine.verify_agent_output(text, "agent-1")

    assert "detailed_results" in result
    detail = result["detailed_results"][0]
    assert set(detail.keys()) == {"claim", "status", "confidence", "evidence_count"}
    assert detail["status"] == VerificationStatus.VERIFIED.value


# ---------------------------------------------------------------------------
# GroundingEngine - internal helper methods
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "reliability,expected_weight",
    [
        (SourceReliability.AUTHORITATIVE, 1.0),
        (SourceReliability.HIGH, 0.85),
        (SourceReliability.MEDIUM, 0.7),
        (SourceReliability.LOW, 0.5),
        (SourceReliability.UNKNOWN, 0.3),
    ],
)
def test_get_reliability_weight(reliability, expected_weight):
    engine = GroundingEngine()
    assert engine._get_reliability_weight(reliability) == expected_weight


def test_determine_status_contradicted_overrides_supporting():
    engine = GroundingEngine()
    source = make_source()
    status = engine._determine_status([source], [source], confidence=1.0)
    assert status == VerificationStatus.CONTRADICTED


def test_determine_status_verified_when_confidence_meets_threshold():
    engine = GroundingEngine()
    source = make_source()
    status = engine._determine_status([source], [], confidence=0.7)
    assert status == VerificationStatus.VERIFIED


def test_determine_status_partially_verified_when_confidence_below_threshold():
    engine = GroundingEngine()
    source = make_source()
    status = engine._determine_status([source], [], confidence=0.69)
    assert status == VerificationStatus.PARTIALLY_VERIFIED


def test_determine_status_unverified_when_no_support():
    engine = GroundingEngine()
    status = engine._determine_status([], [], confidence=0.0)
    assert status == VerificationStatus.UNVERIFIED


def test_check_contradiction_placeholder_always_false():
    engine = GroundingEngine()
    assert engine._check_contradiction("any claim", "any source") is False


# ---------------------------------------------------------------------------
# GroundingGuardrail
# ---------------------------------------------------------------------------


def _make_report(confidence, status="some_status"):
    return {
        "status": status,
        "overall_confidence": confidence,
        "claims_total": 1,
        "claims_verified": 0,
        "claims_partially_verified": 0,
        "claims_contradicted": 0,
        "claims_unverified": 1,
        "detailed_results": [],
        "timestamp": datetime.now().isoformat(),
    }


def test_guardrail_default_thresholds():
    guardrail = GroundingGuardrail(GroundingEngine())
    assert guardrail.action_thresholds == {"block": 0.3, "flag": 0.6, "warn": 0.8}


def test_guardrail_custom_thresholds():
    guardrail = GroundingGuardrail(
        GroundingEngine(),
        config={"action_thresholds": {"block": 0.1, "flag": 0.4, "warn": 0.6}},
    )
    assert guardrail.action_thresholds == {"block": 0.1, "flag": 0.4, "warn": 0.6}


def test_validate_output_blocks_low_confidence(monkeypatch):
    engine = GroundingEngine()
    guardrail = GroundingGuardrail(engine)
    monkeypatch.setattr(engine, "verify_agent_output", lambda *a, **kw: _make_report(0.1))

    result = guardrail.validate_output("some output", "agent-1")
    assert result["action"] == "block"
    assert "blocking threshold" in result["reason"]


def test_validate_output_flags_medium_low_confidence(monkeypatch):
    engine = GroundingEngine()
    guardrail = GroundingGuardrail(engine)
    monkeypatch.setattr(engine, "verify_agent_output", lambda *a, **kw: _make_report(0.5))

    result = guardrail.validate_output("some output", "agent-1")
    assert result["action"] == "flag_for_review"
    assert "human review" in result["reason"]


def test_validate_output_warns_medium_high_confidence(monkeypatch):
    engine = GroundingEngine()
    guardrail = GroundingGuardrail(engine)
    monkeypatch.setattr(engine, "verify_agent_output", lambda *a, **kw: _make_report(0.75))

    result = guardrail.validate_output("some output", "agent-1")
    assert result["action"] == "warn"


def test_validate_output_allows_high_confidence(monkeypatch):
    engine = GroundingEngine()
    guardrail = GroundingGuardrail(engine)
    monkeypatch.setattr(engine, "verify_agent_output", lambda *a, **kw: _make_report(0.95))

    result = guardrail.validate_output("some output", "agent-1")
    assert result["action"] == "allow"
    assert result["reason"] == "Output passed grounding verification"


def test_validate_output_forces_block_on_contradictions_regardless_of_confidence(monkeypatch):
    engine = GroundingEngine()
    guardrail = GroundingGuardrail(engine)
    monkeypatch.setattr(
        engine,
        "verify_agent_output",
        lambda *a, **kw: _make_report(0.99, status="contains_contradictions"),
    )

    result = guardrail.validate_output("some output", "agent-1")
    assert result["action"] == "block"
    assert result["reason"] == "Output contains contradicted claims"


def test_apply_action_block():
    guardrail = GroundingGuardrail(GroundingEngine())
    validation_result = {"action": "block", "reason": "Confidence score (0.10) below blocking threshold"}
    allowed, message, modified = guardrail.apply_action(validation_result)
    assert allowed is False
    assert "Output blocked" in message
    assert modified is None


def test_apply_action_flag_for_review():
    guardrail = GroundingGuardrail(GroundingEngine())
    validation_result = {"action": "flag_for_review", "reason": "Confidence score (0.50) requires human review"}
    allowed, message, modified = guardrail.apply_action(validation_result)
    assert allowed is False
    assert "flagged for review" in message
    assert modified is None


def test_apply_action_warn_includes_percentage():
    guardrail = GroundingGuardrail(GroundingEngine())
    validation_result = {
        "action": "warn",
        "reason": "Confidence score (0.75) - user should be informed",
        "confidence": 0.75,
    }
    allowed, message, modified = guardrail.apply_action(validation_result)
    assert allowed is True
    assert "75%" in message
    assert modified is None


def test_apply_action_allow():
    guardrail = GroundingGuardrail(GroundingEngine())
    validation_result = {"action": "allow", "reason": "Output passed grounding verification"}
    allowed, message, modified = guardrail.apply_action(validation_result)
    assert allowed is True
    assert message == "Output verified successfully"
    assert modified is None


# ---------------------------------------------------------------------------
# End-to-end integration (mirrors the module's __main__ demonstration)
# ---------------------------------------------------------------------------


def test_end_to_end_documentation_backed_verification():
    # DocumentationConnector.search requires the whole claim text to appear
    # verbatim (as a substring) inside the doc content, so the doc content
    # below is crafted to literally contain the first sentence extracted
    # from test_output (including the trailing period re-appended by
    # extract_claims), while the second sentence has no match anywhere.
    engine = GroundingEngine()
    docs_source = Source(
        name="Python_Docs",
        url="https://docs.python.org/3/",
        reliability=SourceReliability.AUTHORITATIVE,
        source_type="documentation",
    )
    mock_docs = {
        "lists": "Python lists are mutable sequences. They can also be modified in place.",
    }
    docs_connector = DocumentationConnector(mock_docs)
    assert engine.register_source(docs_source, docs_connector) is True

    test_output = (
        "Python lists are mutable sequences. "
        "The moon is made of green cheese and cats can fly to Mars."
    )

    report = engine.verify_agent_output(test_output, "TestAgent")

    assert report["claims_total"] == 2
    assert report["status"] == "some_verified"
    assert report["claims_verified"] == 1

    verified_results = [
        r for r in report["detailed_results"] if "mutable sequences" in r["claim"]
    ]
    unrelated_results = [
        r for r in report["detailed_results"] if "moon is made of green cheese" in r["claim"]
    ]
    assert verified_results[0]["status"] == VerificationStatus.VERIFIED.value
    assert unrelated_results[0]["status"] == VerificationStatus.UNVERIFIED.value

    guardrail = GroundingGuardrail(engine)
    validation = guardrail.validate_output(test_output, "TestAgent")
    allowed, message, _ = guardrail.apply_action(validation)
    assert isinstance(allowed, bool)
    assert isinstance(message, str)