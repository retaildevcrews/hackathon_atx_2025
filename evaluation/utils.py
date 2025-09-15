"""Utility functions for evaluation framework."""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def load_jsonl(file_path: str) -> List[Dict[str, Any]]:
    """Load data from a JSONL file.
    
    Args:
        file_path: Path to the JSONL file
        
    Returns:
        List of dictionaries, one per line
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If JSON parsing fails
    """
    data = []
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON on line {line_num}: {e}")
                raise ValueError(f"Invalid JSON on line {line_num}: {e}")
    
    return data


def save_jsonl(data: List[Dict[str, Any]], file_path: str) -> None:
    """Save data to a JSONL file.
    
    Args:
        data: List of dictionaries to save
        file_path: Output file path
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')


def normalize_criterion_id(criterion_id: str) -> str:
    """Normalize criterion ID for consistent matching.
    
    Args:
        criterion_id: Raw criterion ID
        
    Returns:
        Normalized criterion ID (lowercase, underscores)
    """
    return re.sub(r'[^\w]', '_', criterion_id.lower().strip())


def match_criteria(
    agent_criteria: List[Dict[str, Any]], 
    expected_criteria: List[Dict[str, Any]]
) -> Dict[str, Optional[str]]:
    """Match agent criteria evaluations to expected criteria.
    
    Args:
        agent_criteria: Agent's criteria evaluations
        expected_criteria: Expected criteria from test case
        
    Returns:
        Mapping from expected criterion_id to matched agent criterion_id (or None)
    """
    # Normalize criterion IDs
    agent_map = {
        normalize_criterion_id(c.get("criterion_id", "")): c.get("criterion_id", "")
        for c in agent_criteria
    }
    
    expected_map = {
        normalize_criterion_id(c.get("criterion_id", "")): c.get("criterion_id", "")
        for c in expected_criteria
    }
    
    # Direct matching
    matches = {}
    for norm_expected, orig_expected in expected_map.items():
        if norm_expected in agent_map:
            matches[orig_expected] = agent_map[norm_expected]
        else:
            matches[orig_expected] = None
    
    return matches


def extract_text_spans(
    text: str, 
    supporting_evidence: List[Dict[str, Any]]
) -> List[Tuple[str, int, int]]:
    """Extract text spans from supporting evidence.
    
    Args:
        text: Full document text
        supporting_evidence: List of evidence dictionaries with text/positions
        
    Returns:
        List of (extracted_text, start_pos, end_pos) tuples
    """
    spans = []
    
    for evidence in supporting_evidence:
        if isinstance(evidence, dict):
            # Try different evidence formats
            if "text" in evidence and "start_char" in evidence and "end_char" in evidence:
                spans.append((
                    evidence["text"],
                    evidence["start_char"],
                    evidence["end_char"]
                ))
            elif "text" in evidence:
                # Search for text in document if positions not provided
                evidence_text = evidence["text"]
                start_pos = text.find(evidence_text)
                if start_pos != -1:
                    spans.append((
                        evidence_text,
                        start_pos,
                        start_pos + len(evidence_text)
                    ))
    
    return spans


def compute_text_overlap(
    spans1: List[Tuple[str, int, int]], 
    spans2: List[Tuple[str, int, int]]
) -> float:
    """Compute overlap between two sets of text spans.
    
    Args:
        spans1: First set of spans
        spans2: Second set of spans
        
    Returns:
        Overlap ratio (0.0 to 1.0)
    """
    if not spans1 or not spans2:
        return 0.0
    
    # Convert spans to character ranges
    ranges1 = set()
    for _, start, end in spans1:
        ranges1.update(range(start, end))
    
    ranges2 = set()
    for _, start, end in spans2:
        ranges2.update(range(start, end))
    
    if not ranges1 or not ranges2:
        return 0.0
    
    intersection = len(ranges1 & ranges2)
    union = len(ranges1 | ranges2)
    
    return intersection / union if union > 0 else 0.0


def validate_agent_output(agent_output: Dict[str, Any]) -> List[str]:
    """Validate agent output format and return list of issues.
    
    Args:
        agent_output: Agent's evaluation output
        
    Returns:
        List of validation error messages (empty if valid)
    """
    issues = []
    
    # Check required top-level fields
    required_fields = ["document_id", "criteria_evaluations"]
    for field in required_fields:
        if field not in agent_output:
            issues.append(f"Missing required field: {field}")
    
    # Check criteria evaluations structure
    criteria_evals = agent_output.get("criteria_evaluations", [])
    if not isinstance(criteria_evals, list):
        issues.append("criteria_evaluations must be a list")
    else:
        for i, evaluation in enumerate(criteria_evals):
            if not isinstance(evaluation, dict):
                issues.append(f"criteria_evaluations[{i}] must be a dictionary")
                continue
            
            # Check required fields in each evaluation
            required_eval_fields = ["criterion_id", "score", "reasoning"]
            for field in required_eval_fields:
                if field not in evaluation:
                    issues.append(f"criteria_evaluations[{i}] missing field: {field}")
            
            # Validate score range
            score = evaluation.get("score")
            if score is not None:
                try:
                    score_float = float(score)
                    if not (0 <= score_float <= 100):
                        issues.append(f"criteria_evaluations[{i}] score must be 0-100, got {score}")
                except (ValueError, TypeError):
                    issues.append(f"criteria_evaluations[{i}] score must be numeric, got {type(score)}")
    
    return issues


def validate_judge_output(judge_output: Dict[str, Any]) -> List[str]:
    """Validate judge output format and return list of issues.
    
    Args:
        judge_output: Judge's evaluation output
        
    Returns:
        List of validation error messages (empty if valid)
    """
    issues = []
    
    # Check required top-level fields
    required_fields = ["overall_judge_score", "criteria_judgments"]
    for field in required_fields:
        if field not in judge_output:
            issues.append(f"Missing required field: {field}")
    
    # Validate overall score
    overall_score = judge_output.get("overall_judge_score")
    if overall_score is not None:
        try:
            score_float = float(overall_score)
            if not (0 <= score_float <= 100):
                issues.append(f"overall_judge_score must be 0-100, got {overall_score}")
        except (ValueError, TypeError):
            issues.append(f"overall_judge_score must be numeric, got {type(overall_score)}")
    
    # Check criteria judgments
    judgments = judge_output.get("criteria_judgments", [])
    if not isinstance(judgments, list):
        issues.append("criteria_judgments must be a list")
    else:
        for i, judgment in enumerate(judgments):
            if not isinstance(judgment, dict):
                issues.append(f"criteria_judgments[{i}] must be a dictionary")
                continue
            
            # Check required fields
            required_judgment_fields = ["criterion_id", "judge_score"]
            for field in required_judgment_fields:
                if field not in judgment:
                    issues.append(f"criteria_judgments[{i}] missing field: {field}")
            
            # Validate judge score
            judge_score = judgment.get("judge_score")
            if judge_score is not None:
                try:
                    score_float = float(judge_score)
                    if not (0 <= score_float <= 100):
                        issues.append(f"criteria_judgments[{i}] judge_score must be 0-100, got {judge_score}")
                except (ValueError, TypeError):
                    issues.append(f"criteria_judgments[{i}] judge_score must be numeric, got {type(judge_score)}")
    
    return issues


def create_summary_stats(scores: List[float]) -> Dict[str, float]:
    """Create summary statistics for a list of scores.
    
    Args:
        scores: List of numeric scores
        
    Returns:
        Dictionary with mean, median, std, min, max
    """
    if not scores:
        return {"count": 0}
    
    import statistics
    
    return {
        "count": len(scores),
        "mean": statistics.mean(scores),
        "median": statistics.median(scores),
        "std": statistics.stdev(scores) if len(scores) > 1 else 0.0,
        "min": min(scores),
        "max": max(scores)
    }


def format_score(score: float) -> str:
    """Format a score for display.
    
    Args:
        score: Numeric score
        
    Returns:
        Formatted score string
    """
    return f"{score:.1f}"


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to maximum length with ellipsis.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."


def get_evaluation_summary(evaluation_results: Dict[str, Any]) -> str:
    """Generate a brief summary of evaluation results.
    
    Args:
        evaluation_results: Results from evaluator
        
    Returns:
        Summary string
    """
    metrics = evaluation_results.get("metrics", {})
    summary = metrics.get("summary", {})
    
    mean_score = summary.get("mean_judge_score", 0)
    dataset_size = evaluation_results.get("dataset_size", 0)
    
    performance_level = "excellent" if mean_score >= 90 else \
                       "good" if mean_score >= 80 else \
                       "fair" if mean_score >= 70 else \
                       "poor"
    
    return f"Evaluated {dataset_size} test cases. Mean judge score: {format_score(mean_score)} ({performance_level})"