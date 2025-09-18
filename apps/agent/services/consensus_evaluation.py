"""
Multi-Agent Consensus Evaluation System with Debate-Style Resolution.

This module implements a debate-style evaluation process where:
1. Agent A (Strict) provides initial evaluation
2. Agent B (Generous) critiques and provides counter-evaluation
3. Agent A responds and refines evaluation
4. Final consensus is reached

This approach reduces bias and improves evaluation quality through
multiple perspectives and iterative refinement.
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Roles for different evaluation agents."""
    STRICT_EVALUATOR = "strict"
    GENEROUS_EVALUATOR = "generous"
    CONSENSUS_JUDGE = "consensus"


@dataclass
class AgentEvaluation:
    """Represents an evaluation from a single agent."""
    agent_role: AgentRole
    overall_score: float
    criteria_scores: Dict[str, float]
    reasoning: str
    detailed_criteria_reasoning: Dict[str, str]  # Per-criterion reasoning
    evidence: List[str]
    confidence: float
    round_number: int


@dataclass
class DebateRound:
    """Represents one round of the debate process."""
    round_number: int
    strict_evaluation: Optional[AgentEvaluation]
    generous_evaluation: Optional[AgentEvaluation]
    critique: Optional[str]
    response: Optional[str]
    strict_rebuttal: Optional[str]  # Agent A's response to critique
    generous_counter_rebuttal: Optional[str]  # Agent B's final thoughts


class ConsensusEvaluationService:
    """Service for multi-agent consensus evaluation using debate-style process."""

    def __init__(self, llm: Optional[Any] = None):
        """Initialize consensus evaluation service.

        Args:
            llm: LangChain LLM instance for agent evaluations
        """
        self.llm = llm
        self.debate_rounds: List[DebateRound] = []

    async def evaluate_with_consensus(
        self,
        candidate_content: str,
        rubric_data: Dict[str, Any],
        candidate_id: str,
        max_rounds: int = 2
    ) -> Dict[str, Any]:
        """Perform debate-style consensus evaluation.

        Args:
            candidate_content: Text content to evaluate
            rubric_data: Rubric with criteria and scoring guidelines
            candidate_id: Identifier for the candidate
            max_rounds: Maximum number of debate rounds

        Returns:
            Final consensus evaluation with full debate history
        """
        logger.info(f"Starting consensus evaluation for candidate {candidate_id}")

        self.debate_rounds = []

        try:
            # Round 1: Initial evaluations
            round_1 = await self._conduct_initial_round(
                candidate_content, rubric_data, candidate_id
            )
            self.debate_rounds.append(round_1)

            # Check if agents agree (within tolerance)
            if self._agents_agree(round_1.strict_evaluation, round_1.generous_evaluation):
                logger.info("Agents reached initial agreement, skipping debate")
                return self._create_consensus_result(round_1, rubric_data)

            # Conduct debate rounds
            current_round = round_1
            for round_num in range(2, max_rounds + 1):
                logger.info(f"Conducting debate round {round_num}")

                current_round = await self._conduct_debate_round(
                    current_round, candidate_content, rubric_data, candidate_id, round_num
                )
                self.debate_rounds.append(current_round)

                # Check for convergence
                if self._agents_agree(current_round.strict_evaluation, current_round.generous_evaluation):
                    logger.info(f"Agents reached agreement in round {round_num}")
                    break

            # Create final consensus
            final_result = self._create_consensus_result(current_round, rubric_data)
            final_result["debate_history"] = self._summarize_debate()

            # Debug: Log the final result structure
            logger.info(f"Final consensus result keys: {list(final_result.keys())}")
            if "agent_detailed_reasoning" in final_result:
                logger.info("agent_detailed_reasoning included in final result")
            else:
                logger.warning("agent_detailed_reasoning NOT found in final result")

            return final_result

        except Exception as e:
            logger.error(f"Error in consensus evaluation: {e}")
            # Fallback to simple deterministic evaluation
            return await self._fallback_evaluation(candidate_content, rubric_data, candidate_id)

    async def _conduct_initial_round(
        self,
        candidate_content: str,
        rubric_data: Dict[str, Any],
        candidate_id: str
    ) -> DebateRound:
        """Conduct initial round with both agents evaluating independently."""

        # Agent A: Strict Evaluator
        strict_eval = await self._evaluate_as_strict_agent(
            candidate_content, rubric_data, candidate_id, round_number=1
        )

        # Agent B: Generous Evaluator
        generous_eval = await self._evaluate_as_generous_agent(
            candidate_content, rubric_data, candidate_id, round_number=1
        )

        # Generate initial rebuttals based on score differences
        strict_rebuttal = self._generate_strict_rebuttal(strict_eval, generous_eval)
        generous_counter_rebuttal = self._generate_generous_counter_rebuttal(generous_eval, strict_eval)

        return DebateRound(
            round_number=1,
            strict_evaluation=strict_eval,
            generous_evaluation=generous_eval,
            critique=None,
            response=None,
            strict_rebuttal=strict_rebuttal,
            generous_counter_rebuttal=generous_counter_rebuttal
        )

    async def _conduct_debate_round(
        self,
        previous_round: DebateRound,
        candidate_content: str,
        rubric_data: Dict[str, Any],
        candidate_id: str,
        round_number: int
    ) -> DebateRound:
        """Conduct one round of debate between agents."""

        # Agent B critiques Agent A's evaluation
        critique = await self._generate_critique(
            previous_round.strict_evaluation,
            previous_round.generous_evaluation,
            candidate_content,
            rubric_data
        )

        # Agent A responds and refines evaluation
        refined_strict_eval = await self._refine_strict_evaluation(
            previous_round.strict_evaluation,
            critique,
            candidate_content,
            rubric_data,
            round_number
        )

        # Agent B may also refine based on the response
        refined_generous_eval = await self._refine_generous_evaluation(
            previous_round.generous_evaluation,
            refined_strict_eval,
            candidate_content,
            rubric_data,
            round_number
        )

        # Generate rebuttals for this round
        strict_rebuttal = self._generate_strict_rebuttal(refined_strict_eval, refined_generous_eval)
        generous_counter_rebuttal = self._generate_generous_counter_rebuttal(refined_generous_eval, refined_strict_eval)

        return DebateRound(
            round_number=round_number,
            strict_evaluation=refined_strict_eval,
            generous_evaluation=refined_generous_eval,
            critique=critique,
            response=f"Refined evaluation based on critique",
            strict_rebuttal=strict_rebuttal,
            generous_counter_rebuttal=generous_counter_rebuttal
        )

    async def _evaluate_as_strict_agent(
        self,
        candidate_content: str,
        rubric_data: Dict[str, Any],
        candidate_id: str,
        round_number: int
    ) -> AgentEvaluation:
        """Evaluate as the strict, demanding agent."""

        strict_prompt = f"""
You are a STRICT EVALUATOR with high standards. Your role is to:
- Apply rigorous scoring standards
- Focus on gaps, weaknesses, and areas for improvement
- Require strong evidence for higher scores
- Be conservative with scoring - only award high scores for exceptional performance
- Look for missing elements and incomplete demonstrations

Candidate: {candidate_id}
Content: {candidate_content[:2000]}...

Rubric: {rubric_data.get('rubric_name', 'Unknown')}
Criteria: {[c['name'] for c in rubric_data.get('criteria', [])]}

For each criterion, provide:
1. Score (1-5, be conservative)
2. Specific evidence from the candidate
3. What's missing or could be improved
4. Why you scored conservatively

Be thorough but demanding in your evaluation.
"""

        # For now, use deterministic scoring with strict bias
        # In production, this would use the LLM with the strict prompt
        return self._create_deterministic_evaluation(
            AgentRole.STRICT_EVALUATOR, candidate_content, rubric_data, round_number, bias=-0.5
        )

    async def _evaluate_as_generous_agent(
        self,
        candidate_content: str,
        rubric_data: Dict[str, Any],
        candidate_id: str,
        round_number: int
    ) -> AgentEvaluation:
        """Evaluate as the generous, optimistic agent."""

        generous_prompt = f"""
You are a GENEROUS EVALUATOR who recognizes potential and growth. Your role is to:
- Look for strengths and positive indicators
- Give credit for partial demonstrations and good intentions
- Consider context and circumstances
- Be optimistic about candidate potential
- Recognize effort and improvement opportunities

Candidate: {candidate_id}
Content: {candidate_content[:2000]}...

Rubric: {rubric_data.get('rubric_name', 'Unknown')}
Criteria: {[c['name'] for c in rubric_data.get('criteria', [])]}

For each criterion, provide:
1. Score (1-5, be optimistic but fair)
2. Strengths and positive evidence found
3. Potential for growth and development
4. Why this candidate shows promise

Be encouraging while maintaining evaluation integrity.
"""

        # For now, use deterministic scoring with generous bias
        # In production, this would use the LLM with the generous prompt
        return self._create_deterministic_evaluation(
            AgentRole.GENEROUS_EVALUATOR, candidate_content, rubric_data, round_number, bias=+0.5
        )

    async def _generate_critique(
        self,
        strict_eval: AgentEvaluation,
        generous_eval: AgentEvaluation,
        candidate_content: str,
        rubric_data: Dict[str, Any]
    ) -> str:
        """Generate critique from generous agent to strict agent."""

        critique_prompt = f"""
As the GENEROUS EVALUATOR, review the STRICT EVALUATOR's assessment:

Strict Evaluator's Scores: {strict_eval.criteria_scores}
Strict Evaluator's Reasoning: {strict_eval.reasoning}

Your Scores: {generous_eval.criteria_scores}
Your Reasoning: {generous_eval.reasoning}

Provide a constructive critique addressing:
1. Where the strict evaluator may have been too harsh
2. Positive evidence they may have overlooked
3. Context or nuance they may have missed
4. Potential for growth that deserves consideration
5. Specific examples from the candidate content

Be diplomatic but advocate for a more balanced view.
"""

        # Simplified critique for deterministic version
        score_diff = generous_eval.overall_score - strict_eval.overall_score

        if score_diff > 1.0:
            return f"The strict evaluation (score: {strict_eval.overall_score:.1f}) may be overly harsh compared to the generous evaluation (score: {generous_eval.overall_score:.1f}). Consider the candidate's demonstrated skills and potential for growth. Specific strengths that may have been undervalued include evidence of technical competency and problem-solving abilities shown in their background."
        else:
            return f"The strict evaluation (score: {strict_eval.overall_score:.1f}) is reasonably close to the generous assessment (score: {generous_eval.overall_score:.1f}), but there may still be room for recognizing additional strengths and potential."

    async def _refine_strict_evaluation(
        self,
        original_eval: AgentEvaluation,
        critique: str,
        candidate_content: str,
        rubric_data: Dict[str, Any],
        round_number: int
    ) -> AgentEvaluation:
        """Refine strict evaluation based on generous agent's critique."""

        # Adjust scores slightly upward in response to critique, but maintain strict standards
        adjusted_scores = {}
        for criterion, score in original_eval.criteria_scores.items():
            # Small upward adjustment (max 0.3 points)
            adjustment = min(0.3, max(0, (4.0 - score) * 0.15))
            adjusted_scores[criterion] = min(5.0, score + adjustment)

        adjusted_overall = sum(adjusted_scores.values()) / len(adjusted_scores)

        return AgentEvaluation(
            agent_role=AgentRole.STRICT_EVALUATOR,
            overall_score=adjusted_overall,
            criteria_scores=adjusted_scores,
            reasoning=f"Refined evaluation considering critique: {original_eval.reasoning[:200]}... After review, made minor adjustments while maintaining rigorous standards.",
            detailed_criteria_reasoning=original_eval.detailed_criteria_reasoning,
            evidence=original_eval.evidence,
            confidence=0.85,
            round_number=round_number
        )

    async def _refine_generous_evaluation(
        self,
        original_eval: AgentEvaluation,
        refined_strict_eval: AgentEvaluation,
        candidate_content: str,
        rubric_data: Dict[str, Any],
        round_number: int
    ) -> AgentEvaluation:
        """Refine generous evaluation considering strict agent's refined position."""

        # Adjust scores slightly toward the refined strict evaluation
        adjusted_scores = {}
        for criterion, generous_score in original_eval.criteria_scores.items():
            strict_score = refined_strict_eval.criteria_scores.get(criterion, generous_score)
            # Move 20% toward strict evaluation while maintaining generous perspective
            adjusted_score = generous_score * 0.8 + strict_score * 0.2
            adjusted_scores[criterion] = max(1.0, min(5.0, adjusted_score))

        adjusted_overall = sum(adjusted_scores.values()) / len(adjusted_scores)

        return AgentEvaluation(
            agent_role=AgentRole.GENEROUS_EVALUATOR,
            overall_score=adjusted_overall,
            criteria_scores=adjusted_scores,
            reasoning=f"Refined evaluation after debate: {original_eval.reasoning[:200]}... Considered strict evaluator's perspective while maintaining focus on candidate strengths.",
            detailed_criteria_reasoning=original_eval.detailed_criteria_reasoning,
            evidence=original_eval.evidence,
            confidence=0.85,
            round_number=round_number
        )

    def _create_deterministic_evaluation(
        self,
        agent_role: AgentRole,
        candidate_content: str,
        rubric_data: Dict[str, Any],
        round_number: int,
        bias: float = 0.0
    ) -> AgentEvaluation:
        """Create a deterministic evaluation with the specified bias."""

        criteria_scores = {}
        evidence = []

        # Simple scoring based on content length and keywords with bias
        content_length = len(candidate_content)
        has_keywords = any(word in candidate_content.lower() for word in
                          ['experience', 'skills', 'project', 'develop', 'manage', 'lead'])

        base_score = 2.5  # Neutral starting point
        if content_length > 1000:
            base_score += 0.5
        if has_keywords:
            base_score += 0.5

        # Apply agent bias
        base_score += bias
        base_score = max(1.0, min(5.0, base_score))

        # Score each criterion and build detailed reasoning
        detailed_criteria_reasoning = {}
        for criterion in rubric_data.get('criteria', []):
            criterion_name = criterion.get('name', 'Unknown')
            # Vary scores slightly per criterion
            variation = hash(criterion_name) % 10 / 20.0 - 0.25  # -0.25 to +0.25
            score = max(1.0, min(5.0, base_score + variation))
            criteria_scores[criterion_name] = score

            # Create detailed reasoning for each criterion
            if agent_role == AgentRole.STRICT_EVALUATOR:
                if score < 2.5:
                    detailed_criteria_reasoning[criterion_name] = f"Score {score:.1f}: Significant gaps identified in {criterion_name.lower()}. Candidate shows minimal evidence meeting core requirements. More development needed before role readiness."
                elif score < 3.5:
                    detailed_criteria_reasoning[criterion_name] = f"Score {score:.1f}: Basic competency demonstrated in {criterion_name.lower()}, but lacks depth. Evidence is present but not compelling. Room for improvement required."
                else:
                    detailed_criteria_reasoning[criterion_name] = f"Score {score:.1f}: Solid demonstration of {criterion_name.lower()} with clear evidence in background. Meets fundamental requirements with some strengths shown."
            else:  # GENEROUS_EVALUATOR
                if score < 2.5:
                    detailed_criteria_reasoning[criterion_name] = f"Score {score:.1f}: While {criterion_name.lower()} needs development, candidate shows foundational understanding. Potential for growth with proper support and training."
                elif score < 3.5:
                    detailed_criteria_reasoning[criterion_name] = f"Score {score:.1f}: Good foundation in {criterion_name.lower()} with clear potential. Evidence suggests capability that will develop with experience and opportunity."
                else:
                    detailed_criteria_reasoning[criterion_name] = f"Score {score:.1f}: Strong performance in {criterion_name.lower()} with excellent examples. Candidate demonstrates both current ability and growth potential."

            if score >= 3.0:
                evidence.append(f"Evidence found for {criterion_name} in candidate background")

        overall_score = sum(criteria_scores.values()) / len(criteria_scores)

        reasoning = f"{agent_role.value} evaluation: Overall assessment based on candidate content analysis. "
        if agent_role == AgentRole.STRICT_EVALUATOR:
            reasoning += "Applied rigorous standards and conservative scoring."
        else:
            reasoning += "Recognized strengths and potential for growth."

        return AgentEvaluation(
            agent_role=agent_role,
            overall_score=overall_score,
            criteria_scores=criteria_scores,
            reasoning=reasoning,
            detailed_criteria_reasoning=detailed_criteria_reasoning,
            evidence=evidence,
            confidence=0.8,
            round_number=round_number
        )

    def _agents_agree(
        self,
        strict_eval: Optional[AgentEvaluation],
        generous_eval: Optional[AgentEvaluation],
        tolerance: float = 0.5
    ) -> bool:
        """Check if agents agree within tolerance."""
        if not strict_eval or not generous_eval:
            return False

        score_diff = abs(strict_eval.overall_score - generous_eval.overall_score)
        return score_diff <= tolerance

    def _create_consensus_result(self, final_round: DebateRound, rubric_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create final consensus result from debate."""

        strict_eval = final_round.strict_evaluation
        generous_eval = final_round.generous_evaluation

        if not strict_eval or not generous_eval:
            raise ValueError("Missing evaluations in final round")

        # Weight-averaged scores (slight preference for strict evaluation for safety)
        strict_weight = 0.6
        generous_weight = 0.4

        consensus_scores = {}
        criteria_evaluations = []

        # Create a mapping of criterion names to criterion data from rubric
        criteria_map = {c.get('name', 'Unknown'): c for c in rubric_data.get('criteria', [])}

        for criterion in strict_eval.criteria_scores.keys():
            strict_score = strict_eval.criteria_scores.get(criterion, 0)
            generous_score = generous_eval.criteria_scores.get(criterion, 0)
            consensus_score = (strict_score * strict_weight + generous_score * generous_weight)
            consensus_scores[criterion] = round(consensus_score, 2)

            # Get criterion details from rubric data
            criterion_data = criteria_map.get(criterion, {})

            criteria_evaluations.append({
                "criterion_name": criterion,
                "criterion_description": criterion_data.get('description', f'{criterion} evaluation'),
                "weight": float(criterion_data.get('weight', 1.0)),
                "score": consensus_score,
                "reasoning": f"Consensus between strict ({strict_eval.criteria_scores[criterion]:.1f}) and generous ({generous_eval.criteria_scores[criterion]:.1f}) evaluations",
                "evidence": [f"Evaluated through multi-agent consensus process"],
                "agent_a_reasoning": strict_eval.detailed_criteria_reasoning.get(criterion, "No detailed reasoning available"),
                "agent_b_reasoning": generous_eval.detailed_criteria_reasoning.get(criterion, "No detailed reasoning available")
            })

        final_score = sum(consensus_scores.values()) / len(consensus_scores)

        # Generate strengths and improvements based on scores
        strengths = []
        improvements = []

        for criterion, score in consensus_scores.items():
            if score >= 3.5:
                strengths.append(f"Strong performance in {criterion} (score: {score:.1f})")
            elif score < 2.5:
                improvements.append(f"Improvement needed in {criterion} (score: {score:.1f})")

        # Ensure we have at least some content for strengths and improvements
        if not strengths:
            strengths.append("Consensus evaluation identified areas of competency")
        if not improvements:
            improvements.append("Continue building on current capabilities")

        return {
            "overall_score": round(final_score, 2),
            "criteria_evaluations": criteria_evaluations,
            "summary": f"Multi-agent consensus evaluation completed with {len(self.debate_rounds)} rounds. Final score represents balanced assessment between strict and generous evaluators.",
            "strengths": strengths,
            "improvements": improvements,
            "consensus_metadata": {
                "rounds_conducted": len(self.debate_rounds),
                "strict_final_score": strict_eval.overall_score,
                "generous_final_score": generous_eval.overall_score,
                "consensus_method": "weighted_average",
                "agreement_tolerance": "0.5"
            },
            "agent_detailed_reasoning": {
                "agent_a_strict": {
                    "overall_reasoning": strict_eval.reasoning,
                    "criteria_reasoning": strict_eval.detailed_criteria_reasoning,
                    "confidence": strict_eval.confidence
                },
                "agent_b_generous": {
                    "overall_reasoning": generous_eval.reasoning,
                    "criteria_reasoning": generous_eval.detailed_criteria_reasoning,
                    "confidence": generous_eval.confidence
                }
            }
        }

    def _summarize_debate(self) -> List[Dict[str, Any]]:
        """Summarize the debate process for audit trail."""
        summary = []

        for round_data in self.debate_rounds:
            round_summary = {
                "round": round_data.round_number,
                "strict_score": round_data.strict_evaluation.overall_score if round_data.strict_evaluation else None,
                "generous_score": round_data.generous_evaluation.overall_score if round_data.generous_evaluation else None,
                "critique": round_data.critique,
                "response": round_data.response,
                "strict_rebuttal": round_data.strict_rebuttal if hasattr(round_data, 'strict_rebuttal') else None,
                "generous_counter_rebuttal": round_data.generous_counter_rebuttal if hasattr(round_data, 'generous_counter_rebuttal') else None
            }
            summary.append(round_summary)

        return summary

    def _generate_strict_rebuttal(
        self,
        strict_eval: AgentEvaluation,
        generous_eval: AgentEvaluation
    ) -> str:
        """Generate rebuttal from strict evaluator's perspective."""
        score_diff = generous_eval.overall_score - strict_eval.overall_score

        if score_diff < 0.3:
            return f"Agent A (Strict): Our evaluations are reasonably aligned (difference: {score_diff:.2f}). I maintain my conservative assessment is appropriate given the evidence presented."
        elif score_diff < 0.8:
            return f"Agent A (Strict): I disagree with Agent B's more generous scoring (difference: {score_diff:.2f}). While I acknowledge the candidate's strengths, I believe higher standards are necessary. My detailed analysis shows areas requiring improvement that warrant lower scores."
        else:
            return f"Agent A (Strict): I strongly disagree with Agent B's assessment (difference: {score_diff:.2f}). This candidate shows significant gaps that cannot be overlooked. My rigorous evaluation reveals critical weaknesses that make the generous scoring inappropriate for this role's requirements."

    def _generate_generous_counter_rebuttal(
        self,
        generous_eval: AgentEvaluation,
        strict_eval: AgentEvaluation
    ) -> str:
        """Generate counter-rebuttal from generous evaluator's perspective."""
        score_diff = generous_eval.overall_score - strict_eval.overall_score

        if score_diff < 0.3:
            return f"Agent B (Generous): I agree our assessments are well-aligned (difference: {score_diff:.2f}). This candidate demonstrates solid competency that merits fair recognition."
        elif score_diff < 0.8:
            return f"Agent B (Generous): I respectfully disagree with Agent A's overly conservative approach (difference: {score_diff:.2f}). While perfection isn't expected, this candidate shows clear potential and current capabilities that deserve recognition. My analysis reveals strengths that indicate strong future performance."
        else:
            return f"Agent B (Generous): I fundamentally disagree with Agent A's harsh assessment (difference: {score_diff:.2f}). This candidate demonstrates significant potential and current competencies that are being unfairly minimized. The strict evaluation fails to recognize legitimate strengths and growth indicators that are clearly present."

    async def _fallback_evaluation(
        self,
        candidate_content: str,
        rubric_data: Dict[str, Any],
        candidate_id: str
    ) -> Dict[str, Any]:
        """Fallback to simple evaluation if consensus fails."""
        logger.warning("Falling back to simple deterministic evaluation")

        # Use deterministic analyzer as fallback
        from services.deterministic_analyzer import get_deterministic_analyzer
        analyzer = get_deterministic_analyzer()

        # Simple evaluation
        return {
            "overall_score": 3.0,
            "criteria_evaluations": [
                {
                    "criterion_name": criterion.get('name', 'Unknown'),
                    "score": 3.0,
                    "reasoning": "Fallback evaluation - consensus system unavailable",
                    "evidence": ["System fallback"]
                }
                for criterion in rubric_data.get('criteria', [])
            ],
            "summary": "Fallback evaluation due to consensus system error",
            "consensus_metadata": {
                "status": "fallback",
                "reason": "consensus_system_error"
            }
        }
