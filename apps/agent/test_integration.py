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
            criteria_health = await client.get("http://localhost:8001/healthz")
            print(f"   ✅ Criteria API: {criteria_health.status_code}")
            
            # Check agent service
            agent_health = await client.get("http://localhost:8000/healthz")
            print(f"   ✅ Agent Service: {agent_health.status_code}")
            
    except Exception as e:
        print(f"   ❌ Service health check failed: {e}")
        return
    
    # Test 2: List available rubrics from agent service
    print("\n2️⃣ Testing rubric listing...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/evaluation/rubrics")
            rubrics_data = response.json()
            
            if rubrics_data["status"] == "success":
                rubrics = rubrics_data["rubrics"]
                print(f"   ✅ Found {len(rubrics)} rubrics:")
                for rubric in rubrics:
                    print(f"      - {rubric['rubric_name']} (ID: {rubric['rubric_id']})")
                    
                # Use first rubric for evaluation test
                if rubrics:
                    test_rubric_id = rubrics[0]["rubric_id"]
                    test_rubric_name = rubrics[0]["rubric_name"]
                else:
                    print("   ⚠️ No rubrics found")
                    return
            else:
                print(f"   ❌ Failed to list rubrics: {rubrics_data}")
                return
                
    except Exception as e:
        print(f"   ❌ Rubric listing failed: {e}")
        return
    
    # Test 3: Get rubric details
    print(f"\n3️⃣ Testing rubric details for '{test_rubric_name}'...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://localhost:8000/evaluation/rubrics/{test_rubric_id}")
            rubric_details = response.json()
            
            if rubric_details["status"] == "success":
                criteria_count = len(rubric_details["rubric"]["criteria"])
                print(f"   ✅ Rubric has {criteria_count} criteria")
                for criterion in rubric_details["rubric"]["criteria"]:
                    print(f"      - {criterion['description'][:50]}... (weight: {criterion['weight']})")
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
        "document_id": "samsung_qled_test",
        "max_chunks": 5
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "http://localhost:8000/evaluation/evaluate",
                json=evaluation_request
            )
            
            eval_result = response.json()
            
            if eval_result["status"] == "success":
                evaluation = eval_result["evaluation"]
                overall_score = evaluation["overall_score"]
                criteria_count = len(evaluation["criteria_evaluations"])
                
                print(f"   ✅ Evaluation completed!")
                print(f"      Overall Score: {overall_score:.2f}/5.0")
                print(f"      Criteria Evaluated: {criteria_count}")
                print(f"      Summary: {evaluation['summary'][:100]}...")
                
                # Show individual criterion scores
                print(f"      Individual Scores:")
                for criterion in evaluation["criteria_evaluations"]:
                    print(f"        - {criterion['criterion_id']}: {criterion['score']:.1f}/5.0")
                    
            else:
                print(f"   ❌ Evaluation failed: {eval_result.get('error', 'Unknown error')}")
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