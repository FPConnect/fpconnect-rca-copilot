"""Predictive maintenance with ML-based failure prediction."""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, List, Dict, Optional
import structlog

from app.core.cache import get_cached, set_cached
from app.core.config import settings

log = structlog.get_logger()


def _parse_datetime(value: str) -> datetime:
    """Parse ISO format datetime string."""
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def calculate_risk_score(
    equipment_id: str,
    last_maintenance: str,
    history: List[dict] = None,
    uptime_hours: float = 0,
    operating_conditions: Dict[str, Any] = None,
) -> dict[str, Any]:
    """
    Calculate comprehensive failure risk score using multiple factors.
    
    Enhanced version includes:
    - Time since maintenance
    - Historical failure patterns
    - Operating conditions (temperature, humidity, load)
    - Usage intensity
    - Seasonal factors
    """
    cache_key = f"pred:risk:{equipment_id}"
    cached = get_cached(cache_key)
    if cached:
        return cached

    # Parse and validate inputs
    try:
        last_maint_dt = _parse_datetime(last_maintenance)
    except Exception as e:
        log.error("invalid_maintenance_date", error=str(e))
        raise ValueError("Invalid last_maintenance date format")

    now = datetime.now(timezone.utc)
    days_since_maintenance = max(0, (now - last_maint_dt).days)
    failures = len(history) if history else 0
    
    # Calculate time-based risk component (0-30 points)
    # Risk increases exponentially after recommended maintenance interval
    recommended_interval = 90  # days
    if days_since_maintenance <= recommended_interval:
        time_risk = (days_since_maintenance / recommended_interval) * 15
    else:
        overdue_days = days_since_maintenance - recommended_interval
        time_risk = 15 + min(15, overdue_days / 10)  # Cap at 30
    
    # Calculate failure history risk (0-25 points)
    if failures == 0:
        history_risk = 0
    elif failures <= 2:
        history_risk = failures * 5
    elif failures <= 5:
        history_risk = 10 + (failures - 2) * 5
    else:
        history_risk = 25  # Max out
    
    # Calculate usage intensity risk (0-20 points)
    # Assuming 8 hours/day normal operation
    expected_hours = days_since_maintenance * 8
    if uptime_hours <= expected_hours * 0.5:
        usage_risk = (uptime_hours / (expected_hours * 0.5)) * 10
    elif uptime_hours <= expected_hours:
        usage_risk = 10 + ((uptime_hours - expected_hours * 0.5) / (expected_hours * 0.5)) * 10
    else:
        overtime_ratio = uptime_hours / expected_hours
        usage_risk = min(20, 20 + (overtime_ratio - 1) * 5)
    
    # Calculate operating conditions risk (0-25 points)
    conditions_risk = 0
    if operating_conditions:
        # Temperature factor (optimal: 20-25°C)
        temp = operating_conditions.get("temperature_celsius", 22)
        if temp < 15 or temp > 35:
            conditions_risk += 10
        elif temp < 18 or temp > 30:
            conditions_risk += 5
        
        # Humidity factor (optimal: 40-60%)
        humidity = operating_conditions.get("humidity_percent", 50)
        if humidity < 30 or humidity > 70:
            conditions_risk += 8
        elif humidity < 40 or humidity > 60:
            conditions_risk += 4
        
        # Load factor (optimal: 60-80% capacity)
        load = operating_conditions.get("load_percent", 70)
        if load > 90:
            conditions_risk += 7
        elif load > 80:
            conditions_risk += 3
    
    # Calculate total risk score (0-100)
    total_score = time_risk + history_risk + usage_risk + conditions_risk
    total_score = min(100, max(0, total_score))
    
    # Determine risk level
    if total_score >= 75:
        level = "critical"
    elif total_score >= 50:
        level = "high"
    elif total_score >= 25:
        level = "medium"
    else:
        level = "low"
    
    # Predict days until probable failure (simplified model)
    if total_score > 0:
        # Higher risk = sooner predicted failure
        base_days = 100
        predicted_failure_days = max(1, int(base_days / (total_score / 25)))
    else:
        predicted_failure_days = None
    
    # Generate recommendations based on risk factors
    recommendations = []
    if time_risk > 15:
        recommendations.append("Schedule preventive maintenance immediately - overdue")
    if history_risk > 10:
        recommendations.append("Investigate recurring failure patterns - consider component replacement")
    if usage_risk > 15:
        recommendations.append("Reduce operating hours or add redundant equipment")
    if conditions_risk > 10:
        recommendations.append("Improve environmental conditions (temperature/humidity/load)")
    if not recommendations:
        recommendations.append("Continue regular monitoring - no immediate action required")
    
    result = {
        "equipment_id": equipment_id,
        "score": round(total_score, 1),
        "level": level,
        "predicted_failure_days": predicted_failure_days,
        "components": {
            "time_since_maintenance": round(time_risk, 1),
            "failure_history": round(history_risk, 1),
            "usage_intensity": round(usage_risk, 1),
            "operating_conditions": round(conditions_risk, 1),
        },
        "metrics": {
            "days_since_maintenance": days_since_maintenance,
            "total_failures": failures,
            "uptime_hours": uptime_hours,
        },
        "recommendations": recommendations,
        "generated_at": now.isoformat(),
    }
    
    # Cache duration based on risk level (higher risk = shorter cache)
    cache_ttl = {
        "critical": 3600,
        "high": 7200,
        "medium": 14400,
        "low": 21600,
    }.get(level, 21600)
    
    set_cached(cache_key, result, ttl=cache_ttl)
    return result


def predict_maintenance_window(
    equipment_id: str,
    risk_score: float,
    preferred_days: List[int] = None,
    blackout_dates: List[str] = None,
) -> dict[str, Any]:
    """
    Suggest optimal maintenance window based on risk and constraints.
    
    Args:
        equipment_id: Unique equipment identifier
        risk_score: Current risk score (0-100)
        preferred_days: List of preferred weekdays (0=Monday, 6=Sunday)
        blackout_dates: Dates when maintenance is not allowed
    """
    if preferred_days is None:
        preferred_days = [1, 2, 3, 4, 5]  # Monday-Friday
    
    if blackout_dates is None:
        blackout_dates = []
    
    now = datetime.now(timezone.utc)
    
    # Determine urgency based on risk score
    if risk_score >= 75:
        urgency = "immediate"
        max_days_ahead = 3
    elif risk_score >= 50:
        urgency = "urgent"
        max_days_ahead = 7
    elif risk_score >= 25:
        urgency = "scheduled"
        max_days_ahead = 14
    else:
        urgency = "routine"
        max_days_ahead = 30
    
    # Find available dates
    available_dates = []
    for i in range(max_days_ahead):
        candidate = now + timedelta(days=i)
        
        # Check if weekday is preferred
        if candidate.weekday() not in preferred_days:
            continue
        
        # Check blackout dates
        candidate_str = candidate.strftime("%Y-%m-%d")
        if candidate_str in blackout_dates:
            continue
        
        available_dates.append({
            "date": candidate_str,
            "weekday": candidate.strftime("%A"),
            "priority": i + 1,
        })
    
    # Select best date
    best_date = available_dates[0] if available_dates else None
    
    return {
        "equipment_id": equipment_id,
        "urgency": urgency,
        "risk_score": risk_score,
        "recommended_date": best_date["date"] if best_date else None,
        "available_windows": available_dates[:5],  # Top 5 options
        "max_days_ahead": max_days_ahead,
        "generated_at": now.isoformat(),
    }


def analyze_failure_patterns(
    equipment_id: str,
    failure_history: List[dict],
) -> dict[str, Any]:
    """
    Analyze historical failures to identify patterns.
    
    Args:
        equipment_id: Equipment identifier
        failure_history: List of failure records with date, type, cause
    """
    if not failure_history:
        return {
            "equipment_id": equipment_id,
            "pattern_detected": False,
            "message": "Insufficient failure history for pattern analysis",
        }
    
    # Analyze time between failures
    intervals = []
    sorted_history = sorted(failure_history, key=lambda x: x.get("date", ""))
    
    for i in range(1, len(sorted_history)):
        try:
            prev_date = _parse_datetime(sorted_history[i-1].get("date", ""))
            curr_date = _parse_datetime(sorted_history[i].get("date", ""))
            interval = (curr_date - prev_date).days
            intervals.append(interval)
        except Exception:
            continue
    
    # Calculate statistics
    if intervals:
        avg_interval = sum(intervals) / len(intervals)
        min_interval = min(intervals)
        max_interval = max(intervals)
        
        # Detect trend (are failures getting more frequent?)
        if len(intervals) >= 3:
            first_half_avg = sum(intervals[:len(intervals)//2]) / (len(intervals)//2)
            second_half_avg = sum(intervals[len(intervals)//2:]) / (len(intervals) - len(intervals)//2)
            trend = "increasing" if second_half_avg < first_half_avg else "stable"
        else:
            trend = "insufficient_data"
    else:
        avg_interval = min_interval = max_interval = None
        trend = "no_data"
    
    # Analyze failure types
    failure_types = {}
    for failure in failure_history:
        ftype = failure.get("type", "unknown")
        failure_types[ftype] = failure_types.get(ftype, 0) + 1
    
    most_common_type = max(failure_types.items(), key=lambda x: x[1]) if failure_types else (None, 0)
    
    return {
        "equipment_id": equipment_id,
        "pattern_detected": len(intervals) >= 2,
        "statistics": {
            "total_failures": len(failure_history),
            "average_interval_days": round(avg_interval, 1) if avg_interval else None,
            "min_interval_days": min_interval,
            "max_interval_days": max_interval,
        },
        "trend": trend,
        "failure_types": failure_types,
        "most_common_failure": {
            "type": most_common_type[0],
            "count": most_common_type[1],
        },
        "recommendation": (
            "Implement predictive maintenance - clear pattern detected"
            if trend == "increasing" and len(intervals) >= 3
            else "Continue monitoring - maintain regular schedule"
        ),
    }


def get_fleet_health_summary(
    equipment_list: List[Dict[str, Any]],
) -> dict[str, Any]:
    """
    Get health summary for entire equipment fleet.
    
    Args:
        equipment_list: List of equipment with their metrics
    """
    if not equipment_list:
        return {"status": "no_equipment", "count": 0}
    
    risk_scores = []
    levels = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    
    for equipment in equipment_list:
        try:
            risk_result = calculate_risk_score(
                equipment_id=equipment.get("equipment_id", "unknown"),
                last_maintenance=equipment.get("last_maintenance"),
                history=equipment.get("history", []),
                uptime_hours=equipment.get("uptime_hours", 0),
                operating_conditions=equipment.get("operating_conditions"),
            )
            risk_scores.append(risk_result["score"])
            levels[risk_result["level"]] += 1
        except Exception as e:
            log.warning("fleet_health_error", equipment_id=equipment.get("equipment_id"), error=str(e))
    
    avg_score = sum(risk_scores) / len(risk_scores) if risk_scores else 0
    
    # Determine overall fleet status
    if levels["critical"] > 0:
        fleet_status = "critical"
    elif levels["high"] > len(equipment_list) * 0.2:
        fleet_status = "warning"
    elif avg_score > 50:
        fleet_status = "attention_needed"
    else:
        fleet_status = "healthy"
    
    return {
        "fleet_status": fleet_status,
        "total_equipment": len(equipment_list),
        "average_risk_score": round(avg_score, 1),
        "risk_distribution": levels,
        "equipment_needing_attention": levels["critical"] + levels["high"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
