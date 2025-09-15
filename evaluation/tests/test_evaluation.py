"""Tests for the evaluation framework."""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import os

from evaluation.evaluator import Evaluator, run_evaluation
from evaluation.llm_judge import LLMJudge
from evaluation.metrics import EvaluationMetrics
from evaluation.utils import (
    load_jsonl, save_jsonl, normalize_criterion_id,
    match_criteria, validate_agent_output, validate_judge_output
)


class TestLLMJudge:
    """Tests for LLM Judge functionality."""

    @patch('evaluation.llm_judge.AzureOpenAI')
    def test_judge_initialization(self, mock_azure_openai):
        """Test judge initialization with custom parameters."""
        judge = LLMJudge(model="gpt-3.5-turbo", temperature=0.5)
        assert judge.model == "gpt-3.5-turbo"
        assert judge.temperature == 0.5
        mock_azure_openai.assert_called_once()

    @patch('evaluation.llm_judge.AzureOpenAI')
    def test_evaluate_agent_output_success(self, mock_azure_openai):
        """Test successful agent output evaluation."""
        # Mock Azure OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "judge_id": "gpt-4",
            "overall_judge_score": 85.0,
            "criteria_judgments": [
                {
                    "criterion_id": "test_criterion",
                    "agent_score": 90.0,
                    "judge_score": 85.0,
                    "accuracy": "high",
                    "reasoning_quality": "good",
                    "evidence_relevance": "high",
                    "judge_comments": "Good evaluation"
                }
            ]
        })

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure_openai.return_value = mock_client

        judge = LLMJudge()

        result = judge.evaluate_agent_output(
            document_text="Test document",
            criteria=[{"criterion_id": "test_criterion", "description": "Test criterion"}],
            agent_output={"document_id": "test_doc", "criteria_evaluations": []}
        )

        assert result["overall_judge_score"] == 85.0
        assert len(result["criteria_judgments"]) == 1
        assert result["criteria_judgments"][0]["criterion_id"] == "test_criterion"

    @patch('evaluation.llm_judge.AzureOpenAI')
    def test_evaluate_agent_output_error_handling(self, mock_azure_openai):
        """Test error handling in judge evaluation."""
        # Mock Azure OpenAI client to raise an exception
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_azure_openai.return_value = mock_client

        judge = LLMJudge()

        result = judge.evaluate_agent_output(
            document_text="Test document",
            criteria=[{"criterion_id": "test_criterion", "description": "Test criterion"}],
            agent_output={"document_id": "test_doc"}
        )

        assert result["overall_judge_score"] == 0.0
        assert result["error"] is True
        assert "API Error" in result["judge_overall_comments"]


class TestEvaluator:
    """Tests for main Evaluator class."""

    def test_evaluator_initialization(self):
        """Test evaluator initialization."""
        mock_judge = Mock()
        evaluator = Evaluator(judge=mock_judge, agent_endpoint="http://test.com")

        assert evaluator.judge == mock_judge
        assert evaluator.agent_endpoint == "http://test.com"

    def test_load_dataset_success(self):
        """Test successful dataset loading with embedded criteria."""
        # Create temporary dataset file
        test_data = [
            {
                "document_id": "doc1",
                "document_text": "Test document 1",
                "criteria": [{"criterion_id": "test1", "description": "Test criterion 1"}]
            },
            {
                "document_id": "doc2",
                "document_text": "Test document 2",
                "criteria": [{"criterion_id": "test2", "description": "Test criterion 2"}]
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            for item in test_data:
                f.write(json.dumps(item) + '\n')
            temp_path = f.name

        try:
            evaluator = Evaluator()
            test_cases = list(evaluator._load_dataset(temp_path))

            assert len(test_cases) == 2
            assert test_cases[0]["document_id"] == "doc1"
            assert test_cases[1]["document_id"] == "doc2"
            assert len(test_cases[0]["criteria"]) == 1
            assert test_cases[0]["criteria"][0]["criterion_id"] == "test1"
        finally:
            os.unlink(temp_path)

    def test_load_dataset_with_rubric_file(self):
        """Test dataset loading with rubric file references."""
        # Create temporary rubric file
        rubric_data = {
            "rubric_name": "Test Rubric",
            "domain": "test",
            "version": "1.0",
            "criteria": [
                {
                    "criterion_id": "test_criterion",
                    "description": "Test criterion description",
                    "weight": 1.0
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as rubric_f:
            json.dump(rubric_data, rubric_f)
            rubric_path = rubric_f.name

        # Create temporary dataset file with rubric reference
        test_data = [
            {
                "document_id": "doc1",
                "document_text": "Test document 1",
                "rubric_file": os.path.basename(rubric_path)
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False, dir=os.path.dirname(rubric_path)) as dataset_f:
            for item in test_data:
                dataset_f.write(json.dumps(item) + '\n')
            dataset_path = dataset_f.name

        try:
            evaluator = Evaluator()
            test_cases = list(evaluator._load_dataset(dataset_path))

            assert len(test_cases) == 1
            assert test_cases[0]["document_id"] == "doc1"
            assert "criteria" in test_cases[0]
            assert len(test_cases[0]["criteria"]) == 1
            assert test_cases[0]["criteria"][0]["criterion_id"] == "test_criterion"
        finally:
            os.unlink(rubric_path)
            os.unlink(dataset_path)

    def test_load_dataset_missing_file(self):
        """Test dataset loading with missing file."""
        evaluator = Evaluator()

        with pytest.raises(FileNotFoundError):
            list(evaluator._load_dataset("/nonexistent/file.jsonl"))

    @patch('requests.post')
    def test_call_agent_success(self, mock_post):
        """Test successful agent API call."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "document_id": "test_doc",
            "overall_score": 85.0,
            "criteria_evaluations": []
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        evaluator = Evaluator(agent_endpoint="http://test.com")

        test_case = {
            "document_id": "test_doc",
            "document_text": "Test document",
            "criteria": []
        }

        result = evaluator._call_agent(test_case)

        assert result is not None
        assert result["document_id"] == "test_doc"
        assert result["overall_score"] == 85.0

        # Verify API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]["json"]["document_text"] == "Test document"

    @patch('requests.post')
    def test_call_agent_failure(self, mock_post):
        """Test agent API call failure."""
        # Mock failed response
        mock_post.side_effect = Exception("Connection error")

        evaluator = Evaluator(agent_endpoint="http://test.com")

        test_case = {
            "document_id": "test_doc",
            "document_text": "Test document",
            "criteria": []
        }

        result = evaluator._call_agent(test_case)

        assert result is None


class TestMetrics:
    """Tests for metrics computation."""

    def test_compute_metrics_empty_results(self):
        """Test metrics computation with empty results."""
        metrics = EvaluationMetrics()
        result = metrics.compute_metrics([])

        assert "error" in result
        assert result["error"] == "No results to compute metrics from"

    def test_compute_summary_metrics(self):
        """Test summary metrics computation."""
        metrics = EvaluationMetrics()

        # Mock results
        results = [
            {
                "judge_results": [{"overall_judge_score": 85.0}],
                "agent_output": {"overall_score": 90.0},
                "test_case": {"criteria": [{"criterion_id": "test1"}]}
            },
            {
                "judge_results": [{"overall_judge_score": 75.0}],
                "agent_output": {"overall_score": 80.0},
                "test_case": {"criteria": [{"criterion_id": "test1"}]}
            }
        ]

        result = metrics.compute_metrics(results)

        assert "summary" in result
        summary = result["summary"]
        assert summary["mean_judge_score"] == 80.0
        assert summary["median_judge_score"] == 80.0
        assert "agent_vs_judge_correlation" in summary

    def test_extract_judge_scores(self):
        """Test judge score extraction."""
        metrics = EvaluationMetrics()

        results = [
            {"judge_results": [{"overall_judge_score": 85.0}]},
            {"judge_results": [{"overall_judge_score": 75.0}]},
            {"judge_results": []}  # Missing score
        ]

        scores = metrics._extract_judge_scores(results)

        assert len(scores) == 2
        assert scores == [85.0, 75.0]


class TestUtils:
    """Tests for utility functions."""

    def test_load_save_jsonl(self):
        """Test JSONL loading and saving."""
        test_data = [
            {"id": 1, "text": "Test 1"},
            {"id": 2, "text": "Test 2"}
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            temp_path = f.name

        try:
            # Save data
            save_jsonl(test_data, temp_path)

            # Load data
            loaded_data = load_jsonl(temp_path)

            assert len(loaded_data) == 2
            assert loaded_data[0]["id"] == 1
            assert loaded_data[1]["text"] == "Test 2"
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_normalize_criterion_id(self):
        """Test criterion ID normalization."""
        assert normalize_criterion_id("Security Compliance") == "security_compliance"
        assert normalize_criterion_id("test-criterion") == "test_criterion"
        assert normalize_criterion_id("Test_ID") == "test_id"
        assert normalize_criterion_id("  Mixed Case!  ") == "mixed_case_"

    def test_match_criteria(self):
        """Test criteria matching."""
        agent_criteria = [
            {"criterion_id": "security_compliance"},
            {"criterion_id": "data_protection"}
        ]

        expected_criteria = [
            {"criterion_id": "Security Compliance"},
            {"criterion_id": "data-protection"},
            {"criterion_id": "missing_criterion"}
        ]

        matches = match_criteria(agent_criteria, expected_criteria)

        assert matches["Security Compliance"] == "security_compliance"
        assert matches["data-protection"] == "data_protection"
        assert matches["missing_criterion"] is None

    def test_validate_agent_output_valid(self):
        """Test agent output validation with valid data."""
        valid_output = {
            "document_id": "test_doc",
            "criteria_evaluations": [
                {
                    "criterion_id": "test_criterion",
                    "score": 85.0,
                    "reasoning": "Good evaluation"
                }
            ]
        }

        issues = validate_agent_output(valid_output)
        assert len(issues) == 0

    def test_validate_agent_output_invalid(self):
        """Test agent output validation with invalid data."""
        invalid_output = {
            "document_id": "test_doc",
            "criteria_evaluations": [
                {
                    "criterion_id": "test_criterion",
                    "score": 150.0,  # Invalid score > 100
                    # Missing reasoning
                }
            ]
        }

        issues = validate_agent_output(invalid_output)
        assert len(issues) > 0
        assert any("score must be 0-100" in issue for issue in issues)
        assert any("missing field: reasoning" in issue for issue in issues)

    def test_validate_judge_output_valid(self):
        """Test judge output validation with valid data."""
        valid_output = {
            "overall_judge_score": 85.0,
            "criteria_judgments": [
                {
                    "criterion_id": "test_criterion",
                    "judge_score": 80.0
                }
            ]
        }

        issues = validate_judge_output(valid_output)
        assert len(issues) == 0

    def test_validate_judge_output_invalid(self):
        """Test judge output validation with invalid data."""
        invalid_output = {
            "overall_judge_score": -10.0,  # Invalid negative score
            "criteria_judgments": "not a list"  # Should be list
        }

        issues = validate_judge_output(invalid_output)
        assert len(issues) > 0
        assert any("must be 0-100" in issue for issue in issues)
        assert any("must be a list" in issue for issue in issues)


class TestIntegration:
    """Integration tests for the evaluation framework."""

    @patch('evaluation.evaluator.requests.post')
    @patch('evaluation.llm_judge.AzureOpenAI')
    def test_full_evaluation_pipeline(self, mock_azure_openai, mock_requests):
        """Test the full evaluation pipeline end-to-end."""
        # Mock agent response
        mock_agent_response = Mock()
        mock_agent_response.json.return_value = {
            "document_id": "test_doc",
            "overall_score": 85.0,
            "criteria_evaluations": [
                {
                    "criterion_id": "test_criterion",
                    "score": 85.0,
                    "reasoning": "Good evaluation",
                    "confidence": 0.8
                }
            ]
        }
        mock_agent_response.raise_for_status.return_value = None
        mock_requests.return_value = mock_agent_response

        # Mock judge response
        mock_judge_response = Mock()
        mock_judge_response.choices = [Mock()]
        mock_judge_response.choices[0].message.content = json.dumps({
            "overall_judge_score": 80.0,
            "criteria_judgments": [
                {
                    "criterion_id": "test_criterion",
                    "agent_score": 85.0,
                    "judge_score": 80.0,
                    "accuracy": "high",
                    "reasoning_quality": "good",
                    "evidence_relevance": "high"
                }
            ]
        })

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_judge_response
        mock_azure_openai.return_value = mock_client

        # Create test dataset
        test_data = [{
            "document_id": "test_doc",
            "document_text": "Test document content",
            "criteria": [
                {
                    "criterion_id": "test_criterion",
                    "description": "Test criterion description"
                }
            ]
        }]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            f.write(json.dumps(test_data[0]) + '\n')
            dataset_path = f.name

        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Run evaluation
                evaluator = Evaluator(agent_endpoint="http://test.com")
                results = evaluator.run_evaluation(
                    dataset_path=dataset_path,
                    output_dir=temp_dir,
                    consistency_runs=1
                )

                # Verify results structure
                assert "results" in results
                assert "metrics" in results
                assert results["dataset_size"] == 1

                # Verify metrics
                metrics = results["metrics"]
                assert "summary" in metrics
                assert metrics["summary"]["mean_judge_score"] == 80.0

                # Verify files were created
                reports_dir = Path(temp_dir)
                json_files = list(reports_dir.glob("*.json"))
                md_files = list(reports_dir.glob("*.md"))

                assert len(json_files) >= 2  # results and metrics files
                assert len(md_files) >= 1    # markdown report

            finally:
                os.unlink(dataset_path)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
