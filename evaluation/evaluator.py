"""Main evaluation orchestrator."""

import json
import logging
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Iterator
from .llm_judge import LLMJudge
from .config import Config
from .metrics import EvaluationMetrics

logger = logging.getLogger(__name__)


class Evaluator:
    """Main evaluation orchestrator."""

    def __init__(
        self,
        judge: Optional[LLMJudge] = None,
        agent_endpoint: Optional[str] = None
    ):
        """Initialize the evaluator.

        Args:
            judge: LLM judge instance (creates default if None)
            agent_endpoint: Agent API endpoint (uses config if None)
        """
        self.judge = judge or LLMJudge()
        self.agent_endpoint = agent_endpoint or Config.get_agent_config()["endpoint"]
        self.agent_timeout = Config.get_agent_config()["timeout"]
        self.metrics = EvaluationMetrics()

    def run_evaluation(
        self,
        dataset_path: str,
        output_dir: str = "evaluation/reports",
        consistency_runs: int = 1
    ) -> Dict[str, Any]:
        """Run evaluation on a dataset.

        Args:
            dataset_path: Path to JSONL dataset file
            output_dir: Directory to save reports
            consistency_runs: Number of runs for consistency testing

        Returns:
            Evaluation results dictionary
        """
        logger.info(f"Starting evaluation on {dataset_path}")

        # Load dataset
        test_cases = list(self._load_dataset(dataset_path))
        logger.info(f"Loaded {len(test_cases)} test cases")

        # Run evaluations
        results = []
        for i, test_case in enumerate(test_cases):
            logger.info(f"Evaluating case {i+1}/{len(test_cases)}: {test_case['document_id']}")

            # Get agent output
            agent_output = self._call_agent(test_case)
            if agent_output is None:
                logger.error(f"Failed to get agent output for {test_case['document_id']}")
                continue

            # Run judge evaluation(s)
            judge_results = []
            for run in range(consistency_runs):
                judge_output = self.judge.evaluate_agent_output(
                    document_text=test_case["document_text"],
                    criteria=test_case["criteria"],
                    agent_output=agent_output,
                    document_metadata=test_case.get("document_metadata")
                )
                judge_results.append(judge_output)

            results.append({
                "test_case": test_case,
                "agent_output": agent_output,
                "judge_results": judge_results,
                "timestamp": datetime.now().isoformat()
            })

        # Compute metrics
        metrics = self.metrics.compute_metrics(results)

        # Save results
        self._save_results(results, metrics, output_dir)

        logger.info(f"Evaluation complete. Results saved to {output_dir}")
        return {
            "results": results,
            "metrics": metrics,
            "dataset_size": len(test_cases),
            "timestamp": datetime.now().isoformat()
        }

    def _load_dataset(self, dataset_path: str) -> Iterator[Dict[str, Any]]:
        """Load test cases from JSONL file."""
        dataset_file = Path(dataset_path)
        if not dataset_file.exists():
            raise FileNotFoundError(f"Dataset file not found: {dataset_path}")

        with open(dataset_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    test_case = json.loads(line)
                    # Validate required fields
                    required_fields = ["document_id", "document_text"]
                    for field in required_fields:
                        if field not in test_case:
                            raise ValueError(f"Missing required field: {field}")

                    # Load criteria from rubric file if specified
                    if "rubric_file" in test_case:
                        test_case["criteria"] = self._load_rubric(test_case["rubric_file"], dataset_path)
                    elif "criteria" not in test_case:
                        raise ValueError("Either 'criteria' or 'rubric_file' must be specified")

                    yield test_case
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON on line {line_num}: {e}")
                except ValueError as e:
                    logger.error(f"Invalid test case on line {line_num}: {e}")

    def _load_rubric(self, rubric_file: str, dataset_path: str) -> List[Dict[str, Any]]:
        """Load criteria from a rubric file.

        Args:
            rubric_file: Name of the rubric file (e.g., 'tv_rubric.json')
            dataset_path: Path to the dataset file (used to find rubric directory)

        Returns:
            List of criteria dictionaries
        """
        # Find rubric file in the same directory as the dataset
        dataset_dir = Path(dataset_path).parent
        rubric_path = dataset_dir / rubric_file

        if not rubric_path.exists():
            raise FileNotFoundError(f"Rubric file not found: {rubric_path}")

        try:
            with open(rubric_path, 'r', encoding='utf-8') as f:
                rubric_data = json.load(f)

            # Convert rubric format to criteria format expected by judge
            if "criteria" in rubric_data:
                criteria = []
                for criterion in rubric_data["criteria"]:
                    # Convert weight from percentage or keep as float
                    weight = criterion.get("weight", 1.0)
                    if isinstance(weight, str) and weight.endswith("%"):
                        weight = float(weight.rstrip("%")) / 100.0

                    criteria.append({
                        "criterion_id": criterion.get("criterion_id", criterion.get("name", "")),
                        "description": criterion.get("description", ""),
                        "weight": weight
                    })
                return criteria
            else:
                raise ValueError(f"Invalid rubric format in {rubric_file}: missing 'criteria' field")

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in rubric file {rubric_file}: {e}")
        except Exception as e:
            raise ValueError(f"Error loading rubric file {rubric_file}: {e}")

    def _call_agent(self, test_case: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call the agent API to get evaluation output."""
        try:
            payload = {
                "document_text": test_case["document_text"],
                "criteria": test_case["criteria"],
                "document_metadata": test_case.get("document_metadata", {})
            }

            response = requests.post(
                self.agent_endpoint,
                json=payload,
                timeout=self.agent_timeout,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()

            agent_output = response.json()

            # Add document_id if not present
            if "document_id" not in agent_output:
                agent_output["document_id"] = test_case["document_id"]

            # Simulate input chunks if not provided by agent (for testing)
            if "input_chunks" not in agent_output:
                logger.warning(f"Agent output missing input_chunks for {test_case['document_id']}")
                agent_output["input_chunks"] = []

            return agent_output

        except requests.RequestException as e:
            logger.error(f"Agent API call failed for {test_case['document_id']}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from agent for {test_case['document_id']}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error calling agent for {test_case['document_id']}: {e}")
            return None

    def _save_results(
        self,
        results: List[Dict[str, Any]],
        metrics: Dict[str, Any],
        output_dir: str
    ) -> None:
        """Save evaluation results and metrics."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save detailed results as JSON
        results_file = output_path / f"evaluation_results_{timestamp}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                "results": results,
                "metrics": metrics,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)

        # Save metrics summary as JSON
        metrics_file = output_path / f"metrics_summary_{timestamp}.json"
        with open(metrics_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)

        # Generate Markdown report
        self._generate_markdown_report(results, metrics, output_path / f"report_{timestamp}.md")

        logger.info(f"Results saved to {results_file}")
        logger.info(f"Metrics saved to {metrics_file}")

    def _generate_markdown_report(
        self,
        results: List[Dict[str, Any]],
        metrics: Dict[str, Any],
        report_path: Path
    ) -> None:
        """Generate a human-readable Markdown report."""
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# Evaluation Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Dataset Size:** {len(results)} test cases\n\n")

            # Summary metrics
            f.write("## Summary\n\n")
            summary = metrics.get("summary", {})
            f.write(f"- **Mean Judge Score:** {summary.get('mean_judge_score', 0):.1f}\n")
            f.write(f"- **Median Judge Score:** {summary.get('median_judge_score', 0):.1f}\n")
            f.write(f"- **Standard Deviation:** {summary.get('std_judge_score', 0):.1f}\n")
            f.write(f"- **Agent vs Judge Correlation:** {summary.get('agent_vs_judge_correlation', 0):.2f}\n\n")

            # Per-criterion breakdown
            f.write("## Per-Criterion Performance\n\n")
            per_criterion = metrics.get("per_criterion", {})
            for criterion_id, criterion_metrics in per_criterion.items():
                f.write(f"### {criterion_id}\n")
                f.write(f"- Mean Judge Score: {criterion_metrics.get('mean_judge_score', 0):.1f}\n")
                f.write(f"- Agreement Rate: {criterion_metrics.get('agreement_rate', 0):.2f}\n")

                issues = criterion_metrics.get('common_issues', [])
                if issues:
                    f.write(f"- Common Issues: {', '.join(issues)}\n")
                f.write("\n")

            # Recommendations
            recommendations = metrics.get("recommendations", [])
            if recommendations:
                f.write("## Recommendations\n\n")
                for rec in recommendations:
                    f.write(f"- {rec}\n")
                f.write("\n")

            # Low-scoring cases
            f.write("## Cases Requiring Attention\n\n")
            low_score_threshold = 70.0
            low_scoring_cases = [
                r for r in results
                if r["judge_results"][0].get("overall_judge_score", 0) < low_score_threshold
            ]

            if low_scoring_cases:
                for case in low_scoring_cases[:5]:  # Show top 5
                    judge_result = case["judge_results"][0]
                    score = judge_result.get("overall_judge_score", 0)
                    doc_id = case["test_case"]["document_id"]
                    comments = judge_result.get("judge_overall_comments", "No comments")

                    f.write(f"### {doc_id} (Score: {score:.1f})\n")
                    f.write(f"{comments}\n\n")
            else:
                f.write("No cases below threshold found.\n\n")


def run_evaluation(
    dataset_path: str = None,
    agent_endpoint: str = None,
    judge_model: str = None,
    output_dir: str = "evaluation/reports"
) -> Dict[str, Any]:
    """Convenience function to run evaluation with default settings."""
    dataset_path = dataset_path or Config.DATASET_PATH

    judge = LLMJudge(model=judge_model) if judge_model else LLMJudge()
    evaluator = Evaluator(judge=judge, agent_endpoint=agent_endpoint)

    return evaluator.run_evaluation(
        dataset_path=dataset_path,
        output_dir=output_dir,
        consistency_runs=Config.CONSISTENCY_RUNS
    )
