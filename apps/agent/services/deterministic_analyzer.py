"""
Deterministic comparison analyzer for batch document evaluation.
Provides rule-based, explainable analysis without LLM dependencies.
"""

import logging
import statistics
from typing import Dict, List, Tuple, Any

from models.invoke import (
    CriterionEvaluation,
    EvaluationResult,
    CandidateInput,
    ComparisonSummary,
    CandidateRanking,
    StatisticalSummary,
    CriteriaAnalysis,
    RankingStrategy
)

logger = logging.getLogger(__name__)


class DeterministicComparison:
    """Provides deterministic, rule-based comparison of document evaluations."""

    def analyze(
        self,
        results: List[EvaluationResult],
        ranking_strategy: RankingStrategy = RankingStrategy.OVERALL_SCORE
    ) -> ComparisonSummary:
        """
        Perform complete deterministic analysis of evaluation results.

        Args:
            results: List of individual document evaluation results
            ranking_strategy: Strategy to use for ranking documents

        Returns:
            Complete comparison summary with rankings and insights
        """
        logger.info(f"Starting deterministic analysis of {len(results)} documents")

        # Step 1: Calculate statistical summary
        statistical_summary = self._calculate_statistical_summary(results)

        # Step 2: Analyze performance by criteria
        criteria_analysis = self._analyze_criteria_performance(results)

        # Step 3: Rank documents based on strategy
        rankings = self._rank_documents(results, ranking_strategy)

        # Step 4: Generate insights and recommendations
        insights = self._generate_cross_document_insights(results, criteria_analysis, statistical_summary)
        recommendation_rationale = self._generate_recommendation_rationale(rankings[0], criteria_analysis)

        return ComparisonSummary(
            best_document=rankings[0],
            rankings=rankings,
            statistical_summary=statistical_summary,
            criteria_analysis=criteria_analysis,
            cross_document_insights=insights,
            recommendation_rationale=recommendation_rationale,
            analysis_method=ComparisonMode.DETERMINISTIC
        )

    def _calculate_statistical_summary(self, results: List[EvaluationResult]) -> StatisticalSummary:
        """Calculate statistical measures across all document scores."""
        scores = [result.overall_score for result in results]

        mean_score = statistics.mean(scores)
        median_score = statistics.median(scores)
        std_dev = statistics.stdev(scores) if len(scores) > 1 else 0.0
        score_range = (min(scores), max(scores))

        # Identify outliers (more than 1 std dev from mean)
        outliers = []
        if std_dev > 0:
            for result in results:
                if abs(result.overall_score - mean_score) > std_dev:
                    outliers.append(result.document_id or "unknown")

        return StatisticalSummary(
            mean_score=mean_score,
            median_score=median_score,
            std_deviation=std_dev,
            score_range=score_range,
            outliers=outliers
        )

    def _analyze_criteria_performance(self, results: List[EvaluationResult]) -> List[CriteriaAnalysis]:
        """Analyze performance for each criterion across all documents."""
        if not results or not results[0].criteria_evaluations:
            return []

        # Group scores by criterion
        criteria_scores: Dict[str, List[Tuple[str, float]]] = {}

        for result in results:
            for criterion in result.criteria_evaluations:
                criterion_name = criterion.criterion_name
                document_id = result.document_id or "unknown"

                if criterion_name not in criteria_scores:
                    criteria_scores[criterion_name] = []

                criteria_scores[criterion_name].append((document_id, criterion.score))

        # Analyze each criterion
        analyses = []
        for criterion_name, scores_data in criteria_scores.items():
            scores = [score for _, score in scores_data]

            # Find best and worst performers
            best_doc = max(scores_data, key=lambda x: x[1])
            worst_doc = min(scores_data, key=lambda x: x[1])

            # Calculate metrics
            score_spread = max(scores) - min(scores)
            average_score = statistics.mean(scores)
            std_dev = statistics.stdev(scores) if len(scores) > 1 else 0.0

            # Determine performance trend
            if std_dev < 0.3:
                trend = "consistent"
            elif std_dev > 1.0:
                trend = "polarized"
            else:
                trend = "varied"

            analysis = CriteriaAnalysis(
                criterion_name=criterion_name,
                best_document_id=best_doc[0],
                worst_document_id=worst_doc[0],
                score_spread=score_spread,
                average_score=average_score,
                performance_trend=trend
            )
            analyses.append(analysis)

        return analyses

    def _rank_documents(self, results: List[EvaluationResult], strategy: RankingStrategy) -> List[CandidateRanking]:
        """Rank documents based on the specified strategy."""
        if strategy == RankingStrategy.OVERALL_SCORE:
            return self._rank_by_overall_score(results)
        elif strategy == RankingStrategy.CONSISTENCY:
            return self._rank_by_consistency(results)
        elif strategy == RankingStrategy.PEAK_PERFORMANCE:
            return self._rank_by_peak_performance(results)
        elif strategy == RankingStrategy.BALANCED:
            return self._rank_by_balanced_performance(results)
        else:
            # Default to overall score
            return self._rank_by_overall_score(results)

    def _rank_by_overall_score(self, results: List[EvaluationResult]) -> List[CandidateRanking]:
        """Rank documents by weighted overall score."""
        sorted_results = sorted(results, key=lambda x: x.overall_score, reverse=True)

        rankings = []
        for rank, result in enumerate(sorted_results, 1):
            # Analyze strengths and weaknesses
            criterion_scores = [(c.criterion_name, c.score) for c in result.criteria_evaluations]
            criterion_scores.sort(key=lambda x: x[1], reverse=True)

            strengths = [f"{name} ({score:.1f})" for name, score in criterion_scores[:3] if score >= 4.0]
            weaknesses = [f"{name} ({score:.1f})" for name, score in criterion_scores[-3:] if score <= 2.5]

            score_breakdown = {name: score for name, score in criterion_scores}

            ranking = DocumentRanking(
                document_id=result.document_id or f"document_{rank}",
                rank=rank,
                overall_score=result.overall_score,
                key_strengths=strengths,
                key_weaknesses=weaknesses,
                score_breakdown=score_breakdown
            )
            rankings.append(ranking)

        return rankings

    def _rank_by_consistency(self, results: List[EvaluationResult]) -> List[CandidateRanking]:
        """Rank documents by consistency (lowest standard deviation in criterion scores)."""
        consistency_scores = []

        for result in results:
            scores = [c.score for c in result.criteria_evaluations]
            std_dev = statistics.stdev(scores) if len(scores) > 1 else 0.0
            # Lower std dev = higher consistency = better rank
            consistency_score = 5.0 - std_dev  # Invert so lower std dev gets higher score
            consistency_scores.append((result, consistency_score, std_dev))

        # Sort by consistency score (higher is better)
        sorted_results = sorted(consistency_scores, key=lambda x: x[1], reverse=True)

        rankings = []
        for rank, (result, consistency_score, std_dev) in enumerate(sorted_results, 1):
            criterion_scores = [(c.criterion_name, c.score) for c in result.criteria_evaluations]

            strengths = [f"Consistent performance (σ={std_dev:.2f})"]
            if consistency_score > 4.0:
                strengths.append("Very stable across criteria")

            weaknesses = []
            if std_dev > 1.0:
                weaknesses.append("High variability across criteria")

            score_breakdown = {name: score for name, score in criterion_scores}

            ranking = DocumentRanking(
                document_id=result.document_id or f"document_{rank}",
                rank=rank,
                overall_score=result.overall_score,
                key_strengths=strengths,
                key_weaknesses=weaknesses,
                score_breakdown=score_breakdown
            )
            rankings.append(ranking)

        return rankings

    def _rank_by_peak_performance(self, results: List[EvaluationResult]) -> List[CandidateRanking]:
        """Rank documents by peak performance (highest individual criterion scores)."""
        peak_scores = []

        for result in results:
            scores = [c.score for c in result.criteria_evaluations]
            max_score = max(scores) if scores else 0.0
            high_scores_count = len([s for s in scores if s >= 4.0])
            peak_metric = max_score + (high_scores_count * 0.1)  # Bonus for multiple high scores
            peak_scores.append((result, peak_metric, max_score, high_scores_count))

        sorted_results = sorted(peak_scores, key=lambda x: x[1], reverse=True)

        rankings = []
        for rank, (result, peak_metric, max_score, high_count) in enumerate(sorted_results, 1):
            criterion_scores = [(c.criterion_name, c.score) for c in result.criteria_evaluations]
            criterion_scores.sort(key=lambda x: x[1], reverse=True)

            strengths = [f"Peak score: {max_score:.1f}"]
            if high_count > 1:
                strengths.append(f"{high_count} criteria above 4.0")

            # Show top performing criteria
            top_criteria = [f"{name} ({score:.1f})" for name, score in criterion_scores[:2] if score >= 4.0]
            strengths.extend(top_criteria)

            weaknesses = [f"{name} ({score:.1f})" for name, score in criterion_scores[-2:] if score <= 2.5]

            score_breakdown = {name: score for name, score in criterion_scores}

            ranking = DocumentRanking(
                document_id=result.document_id or f"document_{rank}",
                rank=rank,
                overall_score=result.overall_score,
                key_strengths=strengths,
                key_weaknesses=weaknesses,
                score_breakdown=score_breakdown
            )
            rankings.append(ranking)

        return rankings

    def _rank_by_balanced_performance(self, results: List[EvaluationResult]) -> List[CandidateRanking]:
        """Rank documents by balanced performance across all criteria."""
        balance_scores = []

        for result in results:
            scores = [c.score for c in result.criteria_evaluations]
            if not scores:
                balance_scores.append((result, 0.0, 0.0, 0))
                continue

            mean_score = statistics.mean(scores)
            std_dev = statistics.stdev(scores) if len(scores) > 1 else 0.0
            min_score = min(scores)

            # Balance metric: good average, low std dev, no very low scores
            balance_metric = mean_score - (std_dev * 0.5) - max(0, 2.0 - min_score)

            below_threshold = len([s for s in scores if s < 3.0])
            balance_scores.append((result, balance_metric, std_dev, below_threshold))

        sorted_results = sorted(balance_scores, key=lambda x: x[1], reverse=True)

        rankings = []
        for rank, (result, balance_metric, std_dev, below_count) in enumerate(sorted_results, 1):
            criterion_scores = [(c.criterion_name, c.score) for c in result.criteria_evaluations]

            strengths = []
            if std_dev < 0.5:
                strengths.append("Very balanced performance")
            elif std_dev < 1.0:
                strengths.append("Balanced performance")

            if below_count == 0:
                strengths.append("No weak criteria")

            weaknesses = []
            if below_count > 0:
                weaknesses.append(f"{below_count} criteria below 3.0")
            if std_dev > 1.0:
                weaknesses.append("Uneven performance")

            score_breakdown = {name: score for name, score in criterion_scores}

            ranking = DocumentRanking(
                document_id=result.document_id or f"document_{rank}",
                rank=rank,
                overall_score=result.overall_score,
                key_strengths=strengths,
                key_weaknesses=weaknesses,
                score_breakdown=score_breakdown
            )
            rankings.append(ranking)

        return rankings

    def _generate_cross_document_insights(
        self,
        results: List[EvaluationResult],
        criteria_analysis: List[CriteriaAnalysis],
        statistical_summary: StatisticalSummary
    ) -> str:
        """Generate insights by analyzing patterns across all documents."""
        insights = []

        # Overall performance insights
        if statistical_summary.std_deviation < 0.3:
            insights.append("Documents show very similar performance levels")
        elif statistical_summary.std_deviation > 1.0:
            insights.append("Significant performance variation between documents")

        # Criteria-specific insights
        weak_criteria = [c for c in criteria_analysis if c.average_score < 2.5]
        strong_criteria = [c for c in criteria_analysis if c.average_score > 4.0]
        varied_criteria = [c for c in criteria_analysis if c.score_spread > 1.5]

        if weak_criteria:
            criteria_names = ", ".join([c.criterion_name for c in weak_criteria])
            insights.append(f"All documents struggle with: {criteria_names}")

        if strong_criteria:
            criteria_names = ", ".join([c.criterion_name for c in strong_criteria])
            insights.append(f"All documents excel at: {criteria_names}")

        if varied_criteria:
            criteria_names = ", ".join([c.criterion_name for c in varied_criteria])
            insights.append(f"High variation in: {criteria_names}")

        # Performance distribution insights
        scores = [r.overall_score for r in results]
        high_performers = len([s for s in scores if s >= 4.0])
        low_performers = len([s for s in scores if s <= 2.5])

        if high_performers > len(results) * 0.6:
            insights.append("Most documents meet high quality standards")
        elif low_performers > len(results) * 0.4:
            insights.append("Many documents need significant improvement")

        if not insights:
            insights.append("Documents show typical performance distribution")

        return "; ".join(insights)

    def _generate_recommendation_rationale(
        self,
        winner: CandidateRanking,
        criteria_analysis: List[CriteriaAnalysis]
    ) -> str:
        """Generate explanation for why the top document was recommended."""
        reasons = []

        # Overall score performance
        if winner.overall_score >= 4.5:
            reasons.append(f"Exceptional overall performance ({winner.overall_score:.1f}/5.0)")
        elif winner.overall_score >= 4.0:
            reasons.append(f"Strong overall performance ({winner.overall_score:.1f}/5.0)")
        elif winner.overall_score >= 3.5:
            reasons.append(f"Good overall performance ({winner.overall_score:.1f}/5.0)")
        else:
            reasons.append(f"Best available option ({winner.overall_score:.1f}/5.0)")

        # Criteria leadership
        winning_criteria = [c for c in criteria_analysis if c.best_document_id == winner.document_id]
        if winning_criteria:
            if len(winning_criteria) >= len(criteria_analysis) * 0.6:
                reasons.append(f"Leading in {len(winning_criteria)}/{len(criteria_analysis)} criteria")
            else:
                criteria_names = ", ".join([c.criterion_name for c in winning_criteria[:2]])
                reasons.append(f"Excels in: {criteria_names}")

        # Strength analysis
        if winner.key_strengths:
            if len(winner.key_strengths) >= 3:
                reasons.append("Multiple key strengths identified")

        # Weakness analysis
        if not winner.key_weaknesses:
            reasons.append("No significant weaknesses detected")
        elif len(winner.key_weaknesses) <= 1:
            reasons.append("Minimal weaknesses")

        if not reasons:
            reasons.append("Selected as best available option based on evaluation criteria")

        return f"Recommended because: {'; '.join(reasons)}"


def get_deterministic_analyzer() -> DeterministicComparison:
    """Get singleton deterministic analyzer instance."""
    return DeterministicComparison()
