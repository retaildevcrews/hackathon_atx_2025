"""
Test script for batch document evaluation feature.
Tests the new batch evaluation endpoint with multiple documents.
"""

import asyncio
import httpx
import json


async def test_batch_evaluation():
    """Test the batch evaluation functionality."""

    print("🧪 Testing Batch Document Evaluation\n")

    # Sample documents for testing
    sample_documents = [
        {
            "document_id": "samsung_65_qled",
            "document_text": """
            Samsung 65" Neo QLED 8K TV Review

            Picture Quality: Exceptional 8K resolution with Quantum Dot technology delivers
            stunning color accuracy and brightness. HDR10+ and Dolby Vision support provide
            excellent contrast ratios. Peak brightness reaches 4000 nits.

            Sound Quality: Object Tracking Sound+ with Dolby Atmos creates immersive audio
            experience. 60W speakers with dedicated subwoofer deliver rich bass and clear dialogue.

            Smart Platform: Tizen OS runs smoothly with comprehensive app selection including
            Netflix, Disney+, Prime Video, and gaming apps. Interface is responsive and intuitive.

            Build Quality: Premium materials with slim profile design. Excellent build quality
            with minimal bezels and sturdy stand.
            """,
            "metadata": {"brand": "Samsung", "type": "TV"}
        },
        {
            "document_id": "lg_55_oled",
            "document_text": """
            LG 55" OLED C3 TV Review

            Picture Quality: Perfect blacks and infinite contrast ratio thanks to OLED technology.
            Excellent color reproduction with wide color gamut. Good peak brightness for HDR content.

            Sound Quality: Built-in speakers are adequate but lack bass depth. Audio quality is
            clear for dialogue but benefits from external sound system for movies.

            Smart Platform: webOS interface is user-friendly with quick access to popular apps.
            Magic remote makes navigation intuitive. Good app support but some streaming services
            load slowly.

            Build Quality: Ultra-thin design looks premium. Sturdy construction with minimal
            flex. Wall mounting options are excellent.
            """,
            "metadata": {"brand": "LG", "type": "TV"}
        },
        {
            "document_id": "sony_75_led",
            "document_text": """
            Sony 75" X90L LED TV Review

            Picture Quality: Good LED performance with local dimming zones. Colors are accurate
            but not as vibrant as QLED. HDR performance is solid with good detail preservation.

            Sound Quality: Acoustic Multi-Audio provides decent sound positioning. Bass response
            is average. Clear dialogue reproduction. Overall audio quality is good for a TV.

            Smart Platform: Google TV platform offers excellent app selection and integration.
            Voice control works well. Interface can be somewhat slow during navigation.

            Build Quality: Solid construction with premium materials. Bezel design is clean and
            modern. Stand provides good stability for the large screen size.
            """,
            "metadata": {"brand": "Sony", "type": "TV"}
        }
    ]

    # Test different comparison modes and ranking strategies
    test_scenarios = [
        {
            "name": "Overall Score Ranking (Deterministic)",
            "comparison_mode": "deterministic",
            "ranking_strategy": "overall_score"
        },
        {
            "name": "Consistency Ranking (Deterministic)",
            "comparison_mode": "deterministic",
            "ranking_strategy": "consistency"
        },
        {
            "name": "Peak Performance Ranking (Deterministic)",
            "comparison_mode": "deterministic",
            "ranking_strategy": "peak_performance"
        },
        {
            "name": "Balanced Performance Ranking (Deterministic)",
            "comparison_mode": "deterministic",
            "ranking_strategy": "balanced"
        }
    ]

    # First, get available rubrics
    print("1️⃣ Getting available rubrics...")
    try:
        async with httpx.AsyncClient() as client:
            rubrics_response = await client.get("http://localhost:8001/evaluation/rubrics")

            if rubrics_response.status_code != 200:
                print(f"   ❌ Failed to get rubrics: {rubrics_response.status_code}")
                return

            rubrics_data = rubrics_response.json()
            if rubrics_data["status"] != "success" or not rubrics_data["rubrics"]:
                print("   ❌ No rubrics available for testing")
                return

            # Use first available rubric
            test_rubric = rubrics_data["rubrics"][0]
            rubric_name = test_rubric["rubric_id"]
            print(f"   ✅ Using rubric: {test_rubric['rubric_name']} (ID: {rubric_name})")

    except Exception as e:
        print(f"   ❌ Error getting rubrics: {e}")
        return

    # Test each scenario
    for i, scenario in enumerate(test_scenarios, 2):
        print(f"\n{i}️⃣ Testing: {scenario['name']}")

        batch_request = {
            "documents": sample_documents,
            "rubric_name": rubric_name,
            "comparison_mode": scenario["comparison_mode"],
            "ranking_strategy": scenario["ranking_strategy"]
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                print(f"   📤 Sending batch evaluation request...")
                response = await client.post(
                    "http://localhost:8001/evaluation/evaluate-batch",
                    json=batch_request
                )

                print(f"   📊 Response Status: {response.status_code}")

                if response.status_code != 200:
                    print(f"   ❌ Request failed: {response.text}")
                    continue

                try:
                    result = response.json()
                except Exception as json_error:
                    print(f"   ❌ Failed to parse JSON: {json_error}")
                    continue

                if result["status"] != "success":
                    print(f"   ❌ Evaluation failed: {result.get('error', 'Unknown error')}")
                    continue

                # Display results
                batch_result = result["batch_result"]
                comparison = batch_result["comparison_summary"]

                print(f"   ✅ Batch evaluation completed!")
                print(f"      Documents Processed: {batch_result['total_documents']}")
                print(f"      Analysis Method: {comparison['analysis_method']}")

                # Show rankings
                print(f"      📊 Document Rankings:")
                for ranking in comparison["rankings"]:
                    doc_id = ranking["document_id"]
                    rank = ranking["rank"]
                    score = ranking["overall_score"]
                    print(f"         {rank}. {doc_id}: {score:.2f}/5.0")

                # Show best document details
                best_doc = comparison["best_document"]
                print(f"      🏆 Recommended: {best_doc['document_id']} ({best_doc['overall_score']:.2f}/5.0)")

                if best_doc["key_strengths"]:
                    print(f"         Strengths: {', '.join(best_doc['key_strengths'][:2])}")

                # Show insights
                insights = comparison["cross_document_insights"]
                print(f"      💡 Insights: {insights}")

                # Show recommendation rationale
                rationale = comparison["recommendation_rationale"]
                print(f"      🎯 Rationale: {rationale}")

                # Show statistical summary
                stats = comparison["statistical_summary"]
                print(f"      📈 Statistics: Mean={stats['mean_score']:.2f}, StdDev={stats['std_deviation']:.2f}")

        except httpx.TimeoutException:
            print(f"   ❌ Request timed out")
        except Exception as e:
            print(f"   ❌ Test failed: {e}")

    print(f"\n🎉 Batch evaluation testing completed!")
    print(f"\n📝 What was tested:")
    print(f"   ✅ Parallel document evaluation")
    print(f"   ✅ Deterministic comparison analysis")
    print(f"   ✅ Multiple ranking strategies")
    print(f"   ✅ Statistical analysis across documents")
    print(f"   ✅ Cross-document insights generation")
    print(f"   ✅ Recommendation rationale")


if __name__ == "__main__":
    asyncio.run(test_batch_evaluation())
