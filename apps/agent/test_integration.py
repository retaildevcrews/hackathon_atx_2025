"""
Test script to verify agent service integration with criteria_api.
Run this after starting both services to test the evaluation workflow.
"""

import asyncio
import httpx
import json


async def test_integration():
    """Test the complete evaluation workflow."""

    print("🧪 Testing Agent Service Integration with Criteria API\n")

    # Test 1: Check if both services are running
    print("1️⃣ Testing service health...")

    try:
        async with httpx.AsyncClient() as client:
            # Check criteria_api
            try:
                criteria_health = await client.get("http://localhost:8000/healthz")
                print(f"   ✅ Criteria API: {criteria_health.status_code}")
            except Exception as e:
                print(f"   ❌ Criteria API not reachable: {e}")
                print("   💡 Make sure criteria_api is running on port 8000")
                return

            # Check agent service
            try:
                agent_health = await client.get("http://localhost:8001/")
                print(f"   ✅ Agent Service: {agent_health.status_code}")
            except Exception as e:
                print(f"   ❌ Agent Service not reachable: {e}")
                print("   💡 Make sure agent service is running on port 8001")
                return

    except Exception as e:
        print(f"   ❌ Service health check failed: {e}")
        return

    # Test 2: List available rubrics from agent service
    print("\n2️⃣ Testing rubric listing...")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8001/evaluation/rubrics")

            print(f"   📊 Response Status: {response.status_code}")
            print(f"   📊 Response Headers: {dict(response.headers)}")

            try:
                rubrics_data = response.json()
                print(f"   📊 Response Body: {json.dumps(rubrics_data, indent=2)}")
            except Exception as json_error:
                print(f"   ❌ Failed to parse JSON response: {json_error}")
                print(f"   📊 Raw Response Text: {response.text}")
                return

            # Check if response has expected structure
            if not isinstance(rubrics_data, dict):
                print(f"   ❌ Expected dict response, got {type(rubrics_data)}")
                return

            if "status" not in rubrics_data:
                print(f"   ❌ Response missing 'status' field")
                print(f"   📊 Available fields: {list(rubrics_data.keys())}")
                return

            if rubrics_data["status"] == "success":
                rubrics = rubrics_data.get("rubrics", [])
                print(f"   ✅ Found {len(rubrics)} rubrics:")
                for rubric in rubrics:
                    print(f"      - {rubric.get('rubric_name', 'N/A')} (ID: {rubric.get('rubric_id', 'N/A')})")

                # Use first rubric for evaluation test
                if rubrics:
                    test_rubric_id = rubrics[0].get("rubric_id")
                    test_rubric_name = rubrics[0].get("rubric_name")
                    if not test_rubric_id:
                        print("   ⚠️ First rubric missing rubric_id field")
                        return
                else:
                    print("   ⚠️ No rubrics found - check if criteria_api has sample data")
                    return
            else:
                print(f"   ❌ API returned error status: {rubrics_data}")
                return

    except httpx.RequestError as e:
        print(f"   ❌ HTTP request failed: {e}")
        return
    except Exception as e:
        print(f"   ❌ Rubric listing failed: {e}")
        print(f"   📊 Exception type: {type(e).__name__}")
        return

    # Test 3: Get rubric details
    print(f"\n3️⃣ Testing rubric details for '{test_rubric_name}'...")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://localhost:8001/evaluation/rubrics/{test_rubric_id}")

            print(f"   📊 Response Status: {response.status_code}")

            try:
                rubric_details = response.json()
            except Exception as json_error:
                print(f"   ❌ Failed to parse JSON: {json_error}")
                print(f"   📊 Raw Response: {response.text}")
                return

            if rubric_details.get("status") == "success":
                rubric = rubric_details.get("rubric", {})
                criteria = rubric.get("criteria", [])
                criteria_count = len(criteria)
                print(f"   ✅ Rubric has {criteria_count} criteria")
                for criterion in criteria[:3]:  # Show first 3
                    desc = criterion.get('description', 'No description')
                    weight = criterion.get('weight', 'No weight')
                    print(f"      - {desc[:50]}... (weight: {weight})")
                if len(criteria) > 3:
                    print(f"      ... and {len(criteria) - 3} more criteria")
            else:
                print(f"   ❌ Failed to get rubric details: {rubric_details}")
                return

    except Exception as e:
        print(f"   ❌ Rubric details failed: {e}")
        return

    # Test 4: Evaluate a sample document
    print(f"\n4️⃣ Testing document evaluation...")

    sample_document = """
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
    """

    evaluation_request = {
        "document_text": sample_document,
        "rubric_name": test_rubric_id,
        "document_id": "samsung_qled_test"
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            print(f"   📤 Sending evaluation request...")
            response = await client.post(
                "http://localhost:8001/evaluation/evaluate",
                json=evaluation_request
            )

            print(f"   📊 Evaluation Response Status: {response.status_code}")

            try:
                eval_result = response.json()
            except Exception as json_error:
                print(f"   ❌ Failed to parse evaluation JSON: {json_error}")
                print(f"   📊 Raw Response: {response.text}")
                return

            if eval_result.get("status") == "success":
                evaluation = eval_result.get("evaluation", {})
                overall_score = evaluation.get("overall_score", 0)
                criteria_evaluations = evaluation.get("criteria_evaluations", [])
                summary = evaluation.get("summary", "No summary")

                print(f"   ✅ Evaluation completed!")
                print(f"      Overall Score: {overall_score:.2f}/5.0")
                print(f"      Criteria Evaluated: {len(criteria_evaluations)}")
                print(f"      Summary: {summary[:100]}...")

                # Show individual criterion scores
                if criteria_evaluations:
                    print(f"      Individual Scores:")
                    for criterion in criteria_evaluations[:5]:  # Show first 5
                        name = criterion.get('criterion_name', 'Unknown')
                        score = criterion.get('score', 0)
                        print(f"        - {name}: {score:.1f}/5.0")
                    if len(criteria_evaluations) > 5:
                        print(f"        ... and {len(criteria_evaluations) - 5} more")

            else:
                error_msg = eval_result.get('error', eval_result.get('message', 'Unknown error'))
                print(f"   ❌ Evaluation failed: {error_msg}")
                print(f"   📊 Full response: {json.dumps(eval_result, indent=2)}")
                return

    except httpx.TimeoutException:
        print(f"   ❌ Evaluation request timed out (>60s)")
        return
    except Exception as e:
        print(f"   ❌ Document evaluation failed: {e}")
        return

    print(f"\n🎉 All tests passed! Integration is working correctly.")
    print(f"\n📝 Next steps:")
    print(f"   - Create custom rubrics via criteria_api endpoints")
    print(f"   - Evaluate your own documents using the agent service")
    print(f"   - Integrate with your document management system")


if __name__ == "__main__":
    asyncio.run(test_integration())
