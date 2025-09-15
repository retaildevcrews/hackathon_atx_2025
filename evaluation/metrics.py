"""Metrics computation for evaluation results."""

import statistics
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class EvaluationMetrics:
    """Computes metrics from evaluation results."""
    
    def compute_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compute comprehensive metrics from evaluation results.
        
        Args:
            results: List of evaluation results, each containing:
                - test_case: Original test case
                - agent_output: Agent's evaluation
                - judge_results: List of judge evaluations (for consistency)
                
        Returns:
            Dictionary with computed metrics
        """
        if not results:
            return {"error": "No results to compute metrics from"}
        
        # Extract scores and compute basic statistics
        judge_scores = self._extract_judge_scores(results)
        agent_scores = self._extract_agent_scores(results)
        
        # Compute summary metrics
        summary = self._compute_summary_metrics(judge_scores, agent_scores)
        
        # Compute per-criterion metrics
        per_criterion = self._compute_per_criterion_metrics(results)
        
        # Compute consistency metrics (if multiple judge runs)
        consistency = self._compute_consistency_metrics(results)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(summary, per_criterion, consistency)
        
        return {
            "summary": summary,
            "per_criterion": per_criterion,
            "consistency": consistency,
            "recommendations": recommendations,
            "metadata": {
                "total_cases": len(results),
                "failed_cases": len([r for r in results if self._is_failed_case(r)]),
                "average_criteria_per_case": self._compute_avg_criteria_per_case(results)
            }
        }
    
    def _extract_judge_scores(self, results: List[Dict[str, Any]]) -> List[float]:
        """Extract overall judge scores from results."""
        scores = []
        for result in results:
            if result["judge_results"]:
                # Use first judge result for primary metrics
                score = result["judge_results"][0].get("overall_judge_score", 0.0)
                scores.append(score)
        return scores
    
    def _extract_agent_scores(self, results: List[Dict[str, Any]]) -> List[float]:
        """Extract overall agent scores from results."""
        scores = []
        for result in results:
            agent_output = result.get("agent_output", {})
            score = agent_output.get("overall_score", 0.0)
            scores.append(score)
        return scores
    
    def _compute_summary_metrics(
        self, 
        judge_scores: List[float], 
        agent_scores: List[float]
    ) -> Dict[str, Any]:
        """Compute summary-level metrics."""
        if not judge_scores:
            return {"error": "No judge scores available"}
        
        summary = {
            "mean_judge_score": statistics.mean(judge_scores),
            "median_judge_score": statistics.median(judge_scores),
            "std_judge_score": statistics.stdev(judge_scores) if len(judge_scores) > 1 else 0.0,
            "min_judge_score": min(judge_scores),
            "max_judge_score": max(judge_scores),
            "score_distribution": self._compute_score_distribution(judge_scores)
        }
        
        # Correlation between agent and judge scores
        if agent_scores and len(agent_scores) == len(judge_scores):
            summary["agent_vs_judge_correlation"] = self._compute_correlation(agent_scores, judge_scores)
            summary["mean_agent_score"] = statistics.mean(agent_scores)
            summary["score_difference_mean"] = statistics.mean([
                abs(a - j) for a, j in zip(agent_scores, judge_scores)
            ])
        
        return summary
    
    def _compute_per_criterion_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compute metrics per evaluation criterion."""
        criterion_data = {}
        
        for result in results:
            if not result["judge_results"]:
                continue
                
            judge_result = result["judge_results"][0]
            criteria_judgments = judge_result.get("criteria_judgments", [])
            
            for judgment in criteria_judgments:
                criterion_id = judgment.get("criterion_id")
                if not criterion_id:
                    continue
                
                if criterion_id not in criterion_data:
                    criterion_data[criterion_id] = {
                        "judge_scores": [],
                        "agent_scores": [],
                        "accuracy_ratings": [],
                        "reasoning_quality": [],
                        "evidence_relevance": [],
                        "issues": []
                    }
                
                # Collect data for this criterion
                data = criterion_data[criterion_id]
                data["judge_scores"].append(judgment.get("judge_score", 0.0))
                data["agent_scores"].append(judgment.get("agent_score", 0.0))
                data["accuracy_ratings"].append(judgment.get("accuracy", "unknown"))
                data["reasoning_quality"].append(judgment.get("reasoning_quality", "unknown"))
                data["evidence_relevance"].append(judgment.get("evidence_relevance", "unknown"))
                
                # Extract issues from comments
                comments = judgment.get("judge_comments", "")
                if any(keyword in comments.lower() for keyword in ["missing", "incorrect", "weak", "poor"]):
                    data["issues"].append(comments)
        
        # Compute metrics for each criterion
        per_criterion_metrics = {}
        for criterion_id, data in criterion_data.items():
            if not data["judge_scores"]:
                continue
                
            metrics = {
                "mean_judge_score": statistics.mean(data["judge_scores"]),
                "std_judge_score": statistics.stdev(data["judge_scores"]) if len(data["judge_scores"]) > 1 else 0.0,
                "agreement_rate": self._compute_agreement_rate(data["accuracy_ratings"]),
                "quality_distribution": self._compute_quality_distribution(data["reasoning_quality"]),
                "common_issues": self._extract_common_issues(data["issues"])
            }
            
            if data["agent_scores"]:
                metrics["agent_judge_correlation"] = self._compute_correlation(
                    data["agent_scores"], data["judge_scores"]
                )
            
            per_criterion_metrics[criterion_id] = metrics
        
        return per_criterion_metrics
    
    def _compute_consistency_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compute consistency metrics across multiple judge runs."""
        consistency_scores = []
        
        for result in results:
            judge_results = result["judge_results"]
            if len(judge_results) > 1:
                # Compute variance in judge scores for this case
                scores = [jr.get("overall_judge_score", 0.0) for jr in judge_results]
                if len(scores) > 1:
                    consistency_scores.append(statistics.stdev(scores))
        
        if consistency_scores:
            return {
                "mean_consistency_std": statistics.mean(consistency_scores),
                "max_consistency_std": max(consistency_scores),
                "cases_with_high_variance": len([s for s in consistency_scores if s > 10.0]),
                "judge_reliability": "high" if statistics.mean(consistency_scores) < 5.0 else "medium" if statistics.mean(consistency_scores) < 10.0 else "low"
            }
        else:
            return {"note": "Consistency metrics require multiple judge runs per case"}
    
    def _compute_score_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Compute distribution of scores into ranges."""
        ranges = {
            "excellent (90-100)": 0,
            "good (80-89)": 0,
            "fair (70-79)": 0,
            "poor (60-69)": 0,
            "very_poor (0-59)": 0
        }
        
        for score in scores:
            if score >= 90:
                ranges["excellent (90-100)"] += 1
            elif score >= 80:
                ranges["good (80-89)"] += 1
            elif score >= 70:
                ranges["fair (70-79)"] += 1
            elif score >= 60:
                ranges["poor (60-69)"] += 1
            else:
                ranges["very_poor (0-59)"] += 1
        
        return ranges
    
    def _compute_correlation(self, x: List[float], y: List[float]) -> float:
        """Compute Pearson correlation coefficient."""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        try:
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(xi * yi for xi, yi in zip(x, y))
            sum_x2 = sum(xi * xi for xi in x)
            sum_y2 = sum(yi * yi for yi in y)
            
            numerator = n * sum_xy - sum_x * sum_y
            denominator = ((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2)) ** 0.5
            
            return numerator / denominator if denominator != 0 else 0.0
        except:
            return 0.0
    
    def _compute_agreement_rate(self, ratings: List[str]) -> float:
        """Compute rate of high-quality ratings."""
        if not ratings:
            return 0.0
        
        high_quality = sum(1 for r in ratings if r in ["high", "excellent", "good"])
        return high_quality / len(ratings)
    
    def _compute_quality_distribution(self, quality_ratings: List[str]) -> Dict[str, int]:
        """Compute distribution of quality ratings."""
        distribution = {}
        for rating in quality_ratings:
            distribution[rating] = distribution.get(rating, 0) + 1
        return distribution
    
    def _extract_common_issues(self, issues: List[str], top_n: int = 3) -> List[str]:
        """Extract most common issues from judge comments."""
        if not issues:
            return []
        
        # Simple keyword-based issue extraction
        issue_keywords = {
            "missing evidence": ["missing", "lack", "insufficient evidence"],
            "over-scoring": ["too high", "optimistic", "overestimate"],
            "under-scoring": ["too low", "pessimistic", "underestimate"],
            "irrelevant evidence": ["irrelevant", "not relevant", "off-topic"],
            "weak reasoning": ["weak", "poor reasoning", "unclear"],
            "incomplete analysis": ["incomplete", "partial", "missed"]
        }
        
        issue_counts = {}
        for issue_text in issues:
            issue_lower = issue_text.lower()
            for issue_type, keywords in issue_keywords.items():
                if any(keyword in issue_lower for keyword in keywords):
                    issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        # Return top issues
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        return [issue for issue, count in sorted_issues[:top_n]]
    
    def _generate_recommendations(
        self, 
        summary: Dict[str, Any], 
        per_criterion: Dict[str, Any],
        consistency: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations based on metrics."""
        recommendations = []
        
        # Overall score recommendations
        mean_score = summary.get("mean_judge_score", 0)
        if mean_score < 70:
            recommendations.append("Overall performance is below acceptable threshold (70). Focus on improving core evaluation capabilities.")
        elif mean_score < 85:
            recommendations.append("Performance is acceptable but has room for improvement. Focus on edge cases and nuanced evaluations.")
        
        # Correlation recommendations
        correlation = summary.get("agent_vs_judge_correlation", 0)
        if correlation < 0.7:
            recommendations.append("Low correlation between agent and judge scores suggests calibration issues. Review scoring methodology.")
        
        # Per-criterion recommendations
        low_performing_criteria = []
        for criterion_id, metrics in per_criterion.items():
            if metrics.get("mean_judge_score", 0) < 75:
                low_performing_criteria.append(criterion_id)
        
        if low_performing_criteria:
            recommendations.append(f"Focus on improving evaluation for: {', '.join(low_performing_criteria)}")
        
        # Consistency recommendations
        reliability = consistency.get("judge_reliability", "unknown")
        if reliability == "low":
            recommendations.append("Judge consistency is low. Consider refining judge prompts or using multiple judges.")
        
        # Issue-based recommendations
        all_issues = []
        for criterion_metrics in per_criterion.values():
            all_issues.extend(criterion_metrics.get("common_issues", []))
        
        if "missing evidence" in all_issues:
            recommendations.append("Improve evidence retrieval and selection mechanisms.")
        if "over-scoring" in all_issues:
            recommendations.append("Calibrate scoring to be more conservative and realistic.")
        if "weak reasoning" in all_issues:
            recommendations.append("Enhance reasoning chain generation and validation.")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _is_failed_case(self, result: Dict[str, Any]) -> bool:
        """Check if a case failed evaluation."""
        return (
            not result.get("agent_output") or 
            not result.get("judge_results") or
            result["judge_results"][0].get("error", False)
        )
    
    def _compute_avg_criteria_per_case(self, results: List[Dict[str, Any]]) -> float:
        """Compute average number of criteria per test case."""
        if not results:
            return 0.0
        
        total_criteria = sum(
            len(result["test_case"].get("criteria", [])) 
            for result in results
        )
        return total_criteria / len(results)