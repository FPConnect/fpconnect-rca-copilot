"""Enhanced RCA service with multi-method analysis and ensemble scoring."""

from __future__ import annotations

import hashlib
import json
from typing import Any, List, Dict
from datetime import datetime, timezone

from openai import OpenAI, OpenAIError
import structlog

from app.core.cache import get_cached, set_cached
from app.core.config import settings

log = structlog.get_logger()

# Enhanced RCA methods with more sophisticated approaches
METHODS = [
    "5whys",
    "fishbone", 
    "fault_tree",
    "fmea",  # Failure Mode and Effects Analysis
    "barrier",  # Barrier Analysis
    "change",  # Change Analysis
    "taproot",  # TapRooT methodology
]

_client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None


def _cache_key(problem: str, context: str, method: str) -> str:
    """Generate cache key for RCA results."""
    digest = hashlib.sha256(f"{problem}|{context}|{method}".encode("utf-8")).hexdigest()
    return f"rca:enhanced:{digest}"


def _get_method_prompt(method: str, problem: str, context: str) -> str:
    """Get specialized prompt for each RCA method."""
    prompts = {
        "5whys": (
            f"Perform a 5 Whys root cause analysis.\n"
            f"Problem: {problem}\n"
            f"Context: {context}\n\n"
            "Ask 'why' iteratively 5 times to drill down to the root cause. "
            "Return JSON: {\"analysis\": {{\"method\": \"5whys\", \"why_chain\": [\"why1\", \"why2\", ...], \"summary\": \"...\"}}, "
            "\"root_cause\": \"...\", \"confidence\": 0.0, \"actions\": [\"...\"]}"
        ),
        "fishbone": (
            f"Perform a Fishbone (Ishikawa) diagram analysis.\n"
            f"Problem: {problem}\n"
            f"Context: {context}\n\n"
            "Analyze causes across categories: Methods, Machines, Materials, Manpower, Measurement, Environment. "
            "Return JSON: {\"analysis\": {{\"method\": \"fishbone\", \"categories\": {{\"Methods\": [...], \"Machines\": [...], ...}}}}, "
            "\"root_cause\": \"...\", \"confidence\": 0.0, \"actions\": [\"...\"]}"
        ),
        "fault_tree": (
            f"Perform a Fault Tree Analysis.\n"
            f"Problem: {problem}\n"
            f"Context: {context}\n\n"
            "Build a top-down deductive failure analysis with logical gates. "
            "Return JSON: {\"analysis\": {{\"method\": \"fault_tree\", \"top_event\": \"...\", \"intermediate_events\": [...], \"basic_events\": [...]}}, "
            "\"root_cause\": \"...\", \"confidence\": 0.0, \"actions\": [\"...\"]}"
        ),
        "fmea": (
            f"Perform a Failure Mode and Effects Analysis (FMEA).\n"
            f"Problem: {problem}\n"
            f"Context: {context}\n\n"
            "Identify failure modes, their effects, severity, occurrence, and detection. Calculate RPN (Risk Priority Number). "
            "Return JSON: {\"analysis\": {{\"method\": \"fmea\", \"failure_modes\": [{{\"mode\": \"...\", \"severity\": 1-10, \"occurrence\": 1-10, \"detection\": 1-10, \"rpn\": 0-1000}}]}}, "
            "\"root_cause\": \"...\", \"confidence\": 0.0, \"actions\": [\"...\"]}"
        ),
        "barrier": (
            f"Perform a Barrier Analysis.\n"
            f"Problem: {problem}\n"
            f"Context: {context}\n\n"
            "Identify barriers that failed or were missing that allowed the problem to occur. "
            "Return JSON: {\"analysis\": {{\"method\": \"barrier\", \"failed_barriers\": [...], \"missing_barriers\": [...], \"barrier_recommendations\": [...]}}, "
            "\"root_cause\": \"...\", \"confidence\": 0.0, \"actions\": [\"...\"]}"
        ),
        "change": (
            f"Perform a Change Analysis.\n"
            f"Problem: {problem}\n"
            f"Context: {context}\n\n"
            "Identify changes that occurred before the problem. Compare current state vs. baseline. "
            "Return JSON: {\"analysis\": {{\"method\": \"change\", \"changes_identified\": [...], \"relevant_changes\": [...], \"timeline\": [...]}}, "
            "\"root_cause\": \"...\", \"confidence\": 0.0, \"actions\": [\"...\"]}"
        ),
        "taproot": (
            f"Perform TapRooT Root Cause Analysis.\n"
            f"Problem: {problem}\n"
            f"Context: {context}\n\n"
            "Use TapRooT methodology: SnapCharT, Root Cause Tree, Corrective Actions. "
            "Return JSON: {\"analysis\": {{\"method\": \"taproot\", \"snapchart_events\": [...], \"root_causes_tree\": [...], \"human_performance_factors\": [...]}}, "
            "\"root_cause\": \"...\", \"confidence\": 0.0, \"actions\": [\"...\"]}"
        ),
    }
    return prompts.get(method, prompts["5whys"])


def _fallback_rca(problem: str, method: str) -> dict[str, Any]:
    """Generate fallback RCA using rule-based approach when AI is unavailable."""
    return {
        "analysis": {
            "method": method,
            "summary": f"RCA generated from local rule-based fallback because the AI provider was unavailable.",
            "problem": problem,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "root_cause": "Insufficient evidence for a definitive root cause; escalate to engineering N2.",
        "confidence": 0.35,
        "actions": [
            "Collect equipment logs and maintenance history.",
            "Validate calibration status and environmental conditions.",
            "Update the knowledge base after corrective action confirmation.",
            "Review similar incidents in the ticket system.",
            "Conduct interviews with operators and technicians.",
        ],
        "metadata": {
            "fallback": True,
            "method_used": method,
        }
    }


def generate_single_rca(
    problem: str, 
    context: str = "", 
    method: str = "5whys",
    use_cache: bool = True
) -> dict[str, Any]:
    """Generate a single RCA using specified methodology."""
    if method not in METHODS:
        log.warning("unsupported_method", method=method, available=METHODS)
        method = "5whys"
    
    cache_key = _cache_key(problem, context, method)
    
    if use_cache:
        cached = get_cached(cache_key)
        if cached:
            log.debug("rca_cache_hit", method=method, cache_key=cache_key)
            return cached

    prompt = _get_method_prompt(method, problem, context)

    try:
        if not _client:
            raise OpenAIError("OpenAI client not initialized")
            
        response = _client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,  # Lower temperature for more consistent analysis
            max_tokens=2000,
        )
        content = response.choices[0].message.content or "{}"
        result = json.loads(content)
        
        # Add metadata
        result["metadata"] = {
            "method": method,
            "model": "gpt-4o",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "fallback": False,
        }
        
    except (OpenAIError, json.JSONDecodeError, IndexError, AttributeError) as e:
        log.warning("rca_ai_failed", method=method, error=str(e))
        result = _fallback_rca(problem, method)

    if use_cache:
        set_cached(cache_key, result, ttl=86400 * 7)  # Cache for 7 days
    
    return result


def generate_ensemble_rca(
    problem: str,
    context: str = "",
    methods: List[str] = None,
    use_cache: bool = True,
) -> dict[str, Any]:
    """
    Generate RCA using multiple methods and ensemble the results for higher confidence.
    
    This is the premium analysis mode that provides the most comprehensive insights.
    """
    if methods is None:
        methods = ["5whys", "fishbone", "fmea"]  # Default ensemble
    
    # Filter to valid methods
    methods = [m for m in methods if m in METHODS]
    if not methods:
        methods = ["5whys"]
    
    log.info("ensemble_rca_started", methods=methods, problem_length=len(problem))
    
    # Collect results from all methods
    results = []
    for method in methods:
        try:
            result = generate_single_rca(problem, context, method, use_cache)
            results.append(result)
        except Exception as e:
            log.error("ensemble_method_failed", method=method, error=str(e))
            results.append(_fallback_rca(problem, method))
    
    # Ensemble the results
    ensemble_result = _ensemble_results(results, problem, context)
    
    # Add ensemble metadata
    ensemble_result["ensemble"] = {
        "methods_used": methods,
        "individual_results_count": len(results),
        "consensus_score": ensemble_result.get("confidence", 0.0),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    
    return ensemble_result


def _ensemble_results(results: List[dict], problem: str, context: str) -> dict[str, Any]:
    """Combine multiple RCA results into a consensus analysis."""
    if not results:
        return _fallback_rca(problem, "ensemble")
    
    # Extract root causes and confidence scores
    root_causes = [(r.get("root_cause", ""), r.get("confidence", 0.0)) for r in results]
    
    # Find most common root cause themes (simple approach)
    cause_counts: Dict[str, float] = {}
    for cause, confidence in root_causes:
        cause_lower = cause.lower()
        if cause_lower in cause_counts:
            cause_counts[cause_lower] += confidence
        else:
            cause_counts[cause_lower] = confidence
    
    # Select highest scoring root cause
    best_cause = max(cause_counts.items(), key=lambda x: x[1]) if cause_counts else ("", 0.0)
    
    # Aggregate actions from all methods
    all_actions = []
    for r in results:
        all_actions.extend(r.get("actions", []))
    
    # Remove duplicates while preserving order
    unique_actions = list(dict.fromkeys(all_actions))
    
    # Calculate ensemble confidence (average + bonus for agreement)
    avg_confidence = sum(c for _, c in root_causes) / len(root_causes) if root_causes else 0.0
    agreement_bonus = 0.1 * (len([c for c, _ in root_causes if c.lower() == best_cause[0]]) / len(root_causes))
    ensemble_confidence = min(0.95, avg_confidence + agreement_bonus)
    
    # Combine analysis from all methods
    combined_analysis = {
        "method": "ensemble",
        "methods_analyzed": [r.get("analysis", {}).get("method", "unknown") for r in results],
        "summary": f"Ensemble analysis combining {len(results)} RCA methodologies for comprehensive insights.",
        "problem": problem,
        "context": context,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    
    return {
        "analysis": combined_analysis,
        "root_cause": best_cause[0] if best_cause[0] else "Unable to determine root cause with high confidence.",
        "confidence": round(ensemble_confidence, 2),
        "actions": unique_actions[:10],  # Limit to top 10 actions
        "supporting_evidence": [r.get("analysis", {}) for r in results],
        "metadata": {
            "ensemble": True,
            "methods_count": len(results),
            "fallback": any(r.get("metadata", {}).get("fallback", False) for r in results),
        }
    }


def generate_smart_rca(
    problem: str,
    context: str = "",
    priority: str = "medium",
    use_cache: bool = True,
) -> dict[str, Any]:
    """
    Intelligently select RCA method(s) based on problem complexity and priority.
    
    - Low priority: Single quick method (5whys)
    - Medium priority: Dual method (5whys + fishbone)
    - High/Critical priority: Full ensemble analysis
    """
    if priority in ["high", "critical"]:
        return generate_ensemble_rca(
            problem, 
            context, 
            methods=["5whys", "fishbone", "fmea", "barrier"],
            use_cache=use_cache
        )
    elif priority == "medium":
        return generate_ensemble_rca(
            problem,
            context,
            methods=["5whys", "fishbone"],
            use_cache=use_cache
        )
    else:
        return generate_single_rca(problem, context, "5whys", use_cache)
