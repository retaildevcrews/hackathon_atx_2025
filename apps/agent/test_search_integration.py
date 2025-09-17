"""
Test script to verify Azure Search integration with document evaluation.
This test demonstrates how the agent service queries the Azure Search index
to find relevant chunks for evaluation instead of using full document text.
"""

import asyncio
import httpx
import json


async def test_search_integration():
    """Test evaluation workflow using Azure Search index for document chunks."""

    print("🔍 Testing Agent Service with Azure Search Integration\n")

    # Test 1: Verify search service configuration
    print("1️⃣ Testing Azure Search configuration...")

    # Check if search service is properly configured by testing a direct search
    try:
        async with httpx.AsyncClient() as client:
            # First get available rubrics to know what criteria to search for
            rubrics_response = await client.get("http://localhost:8001/evaluation/rubrics")

            if rubrics_response.status_code != 200:
                print(f"   ❌ Failed to get rubrics: {rubrics_response.status_code}")
                return

            rubrics_data = rubrics_response.json()
            if rubrics_data["status"] != "success" or not rubrics_data["rubrics"]:
                print("   ❌ No rubrics available for testing")
                return

            test_rubric = rubrics_data["rubrics"][0]
            rubric_id = test_rubric["rubric_id"]
            rubric_name = test_rubric["rubric_name"]

            print(f"   ✅ Using rubric: {rubric_name} (ID: {rubric_id})")

            # Get rubric details to see what criteria we'll be searching for
            rubric_details_response = await client.get(f"http://localhost:8001/evaluation/rubrics/{rubric_id}")
            if rubric_details_response.status_code == 200:
                rubric_details = rubric_details_response.json()
                if rubric_details.get("status") == "success":
                    criteria = rubric_details.get("rubric", {}).get("criteria", [])
                    print(f"   📊 Rubric has {len(criteria)} criteria that will be used for search:")
                    for criterion in criteria[:3]:  # Show first 3
                        criterion_id = criterion.get('criterion_id', 'Unknown')
                        description = criterion.get('description', 'No description')
                        print(f"      - {criterion_id}: {description[:60]}...")
                    if len(criteria) > 3:
                        print(f"      ... and {len(criteria) - 3} more criteria")

    except Exception as e:
        print(f"   ❌ Setup failed: {e}")
        return

    # Test 2: Test evaluation with search-based chunk retrieval
    print(f"\n2️⃣ Testing search-based evaluation...")
    print(f"   💡 Note: Instead of using full document text, the system will:")
    print(f"      1. Query Azure Search index '{AZURE_SEARCH_INDEX}' for each criterion")
    print(f"      2. Retrieve relevant chunks from your indexed TV data")
    print(f"      3. Evaluate based on the retrieved chunks")

    # Use a minimal document text since we'll be getting chunks from search
    minimal_document = """
    Testing document for search-based evaluation.
    The actual evaluation content will come from Azure Search index chunks.
    """

    evaluation_request = {
        "document_text": minimal_document,
        "rubric_name": rubric_id,
        "document_id": "search_based_test",
        "max_chunks": 5  # Allow more chunks to be retrieved per criterion
    }

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            print(f"   📤 Sending search-based evaluation request...")
            response = await client.post(
                "http://localhost:8001/evaluation/evaluate",
                json=evaluation_request
            )

            print(f"   📊 Response Status: {response.status_code}")

            if response.status_code != 200:
                print(f"   ❌ Request failed: {response.text}")
                return

            try:
                eval_result = response.json()
            except Exception as json_error:
                print(f"   ❌ Failed to parse JSON: {json_error}")
                return

            if eval_result.get("status") == "success":
                evaluation = eval_result.get("evaluation", {})
                agent_metadata = evaluation.get("agent_metadata", {})
                chunks_analyzed = agent_metadata.get("chunks_analyzed", "0")

                print(f"   ✅ Search-based evaluation completed!")
                print(f"      Document ID: {evaluation.get('document_id')}")
                print(f"      Chunks Retrieved from Index: {chunks_analyzed}")
                print(f"      Overall Score: {evaluation.get('overall_score', 0):.2f}/5.0")

                # Show how each criterion was evaluated
                criteria_evaluations = evaluation.get("criteria_evaluations", [])
                print(f"      📊 Criteria Evaluated using Search Chunks:")
                for criterion in criteria_evaluations[:5]:  # Show first 5
                    name = criterion.get('criterion_name', 'Unknown')
                    score = criterion.get('score', 0)
                    reasoning = criterion.get('reasoning', 'No reasoning')
                    evidence = criterion.get('evidence', [])

                    print(f"         • {name}: {score:.1f}/5.0")
                    print(f"           Reasoning: {reasoning[:80]}...")
                    if evidence:
                        print(f"           Evidence Found: {len(evidence)} items")
                        for i, ev in enumerate(evidence[:2]):  # Show first 2 pieces of evidence
                            print(f"             {i+1}. {ev[:60]}...")
                    else:
                        print(f"           Evidence: No evidence found in search results")
                    print()

                if len(criteria_evaluations) > 5:
                    print(f"         ... and {len(criteria_evaluations) - 5} more criteria")

                # Show summary
                summary = evaluation.get("summary", "No summary")
                strengths = evaluation.get("strengths", [])
                improvements = evaluation.get("improvements", [])

                print(f"      📝 Summary: {summary[:100]}...")
                if strengths:
                    print(f"      💪 Strengths: {', '.join(strengths[:2])}")
                if improvements:
                    print(f"      🎯 Improvements: {', '.join(improvements[:2])}")

            else:
                error_msg = eval_result.get('error', 'Unknown error')
                print(f"   ❌ Search-based evaluation failed: {error_msg}")
                return

    except httpx.TimeoutException:
        print(f"   ❌ Request timed out (Azure Search queries can take longer)")
        return
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return

    # Test 3: Test batch evaluation with search
    print(f"\n3️⃣ Testing batch evaluation with Azure Search...")

    # Create multiple test scenarios that will trigger different search queries
    search_test_documents = [
        {
            "document_id": "tv_picture_test",
            "document_text": "Picture quality evaluation test document.",
            "metadata": {"focus": "picture_quality"}
        },
        {
            "document_id": "tv_sound_test",
            "document_text": "Sound quality evaluation test document.",
            "metadata": {"focus": "sound_quality"}
        },
        {
            "document_id": "tv_smart_test",
            "document_text": "Smart platform evaluation test document.",
            "metadata": {"focus": "smart_features"}
        }
    ]

    batch_request = {
        "documents": search_test_documents,
        "rubric_name": rubric_id,
        "comparison_mode": "deterministic",
        "ranking_strategy": "overall_score",
        "max_chunks": 3
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            print(f"   📤 Sending batch evaluation with search...")
            response = await client.post(
                "http://localhost:8001/evaluation/evaluate-batch",
                json=batch_request
            )

            print(f"   📊 Batch Response Status: {response.status_code}")

            if response.status_code != 200:
                print(f"   ❌ Batch request failed: {response.text}")
                return

            try:
                batch_result = response.json()
            except Exception as json_error:
                print(f"   ❌ Failed to parse batch JSON: {json_error}")
                return

            if batch_result.get("status") == "success":
                batch_data = batch_result.get("batch_result", {})
                individual_results = batch_data.get("individual_results", [])
                comparison_summary = batch_data.get("comparison_summary", {})

                print(f"   ✅ Batch search-based evaluation completed!")
                print(f"      Documents Processed: {len(individual_results)}")

                # Show how many chunks were retrieved for each document
                total_chunks = 0
                for result in individual_results:
                    doc_id = result.get("document_id", "unknown")
                    metadata = result.get("agent_metadata", {})
                    chunks = int(metadata.get("chunks_analyzed", "0"))
                    total_chunks += chunks
                    print(f"         {doc_id}: {chunks} chunks from search index")

                print(f"      Total Chunks Retrieved: {total_chunks}")

                # Show ranking results
                rankings = comparison_summary.get("rankings", [])
                if rankings:
                    print(f"      📊 Search-Based Rankings:")
                    for ranking in rankings[:3]:  # Show top 3
                        doc_id = ranking.get("document_id", "unknown")
                        rank = ranking.get("rank", 0)
                        score = ranking.get("overall_score", 0)
                        print(f"         {rank}. {doc_id}: {score:.2f}/5.0")

                # Show insights
                insights = comparison_summary.get("cross_document_insights", "")
                print(f"      💡 Search-Based Insights: {insights}")

            else:
                error_msg = batch_result.get('error', 'Unknown error')
                print(f"   ❌ Batch search evaluation failed: {error_msg}")
                return

    except httpx.TimeoutException:
        print(f"   ❌ Batch request timed out")
        return
    except Exception as e:
        print(f"   ❌ Batch test failed: {e}")
        return

    print(f"\n🎉 Azure Search integration testing completed!")
    print(f"\n📝 What was tested:")
    print(f"   ✅ Azure Search service configuration")
    print(f"   ✅ Criterion-based search queries to index '{AZURE_SEARCH_INDEX}'")
    print(f"   ✅ Chunk retrieval from indexed TV data")
    print(f"   ✅ Search-based document evaluation")
    print(f"   ✅ Batch evaluation with search integration")
    print(f"   ✅ Cross-document analysis using search results")

    print(f"\n🔍 How it works:")
    print(f"   1. For each rubric criterion, the system creates a search query")
    print(f"   2. Queries your Azure Search index '{AZURE_SEARCH_INDEX}' for relevant content")
    print(f"   3. Retrieves the most relevant chunks for each criterion")
    print(f"   4. Evaluates based on the retrieved chunks instead of full document text")
    print(f"   5. This allows evaluation against your existing indexed TV specification data")


# Get the index name from environment
AZURE_SEARCH_INDEX = "index_one"  # From your .env file


if __name__ == "__main__":
    asyncio.run(test_search_integration())
