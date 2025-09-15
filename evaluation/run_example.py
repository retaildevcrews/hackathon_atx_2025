"""Example script showing how to run the evaluation framework."""

import os
import logging
from evaluation import run_evaluation

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """Run evaluation example."""

    # Set environment variables (in practice, use .env file or config)
    os.environ.setdefault("JUDGE_MODEL", "gpt-4")
    os.environ.setdefault("AGENT_ENDPOINT", "http://localhost:8000/evaluate")
    os.environ.setdefault("MIN_ACCEPTABLE_SCORE", "70.0")

    # Check for required Azure OpenAI environment variables
    required_env_vars = ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("💡 Please set your Azure OpenAI credentials:")
        print("   export AZURE_OPENAI_API_KEY='your-api-key'")
        print("   export AZURE_OPENAI_ENDPOINT='https://your-resource.openai.azure.com/'")
        return

    try:
        # Run evaluation
        print("🔍 Starting evaluation...")
        results = run_evaluation(
            dataset_path="evaluation/dataset/test_cases.jsonl",
            output_dir="evaluation/reports",
            judge_model="gpt-4"  # Override default
        )

        # Print summary
        metrics = results["metrics"]
        summary = metrics.get("summary", {})

        print(f"\n✅ Evaluation complete!")
        print(f"📊 Dataset size: {results['dataset_size']} test cases")
        print(f"🎯 Mean judge score: {summary.get('mean_judge_score', 0):.1f}")
        print(f"📈 Score range: {summary.get('min_judge_score', 0):.1f} - {summary.get('max_judge_score', 0):.1f}")

        # Show performance distribution
        distribution = summary.get("score_distribution", {})
        print(f"\n📈 Performance distribution:")
        for category, count in distribution.items():
            print(f"  {category}: {count} cases")

        # Show recommendations
        recommendations = metrics.get("recommendations", [])
        if recommendations:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")

        # Show low-performing cases
        low_score_cases = [
            r for r in results["results"]
            if r["judge_results"][0].get("overall_judge_score", 0) < 70
        ]

        if low_score_cases:
            print(f"\n⚠️  Cases needing attention ({len(low_score_cases)}):")
            for case in low_score_cases[:3]:  # Show top 3
                doc_id = case["test_case"]["document_id"]
                score = case["judge_results"][0].get("overall_judge_score", 0)
                print(f"  - {doc_id}: {score:.1f}")

        print(f"\n📄 Detailed reports saved to: evaluation/reports/")

    except FileNotFoundError as e:
        print(f"❌ Dataset file not found: {e}")
        print("💡 Make sure the test dataset exists at evaluation/dataset/test_cases.jsonl")
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        logging.exception("Evaluation error")


if __name__ == "__main__":
    main()
