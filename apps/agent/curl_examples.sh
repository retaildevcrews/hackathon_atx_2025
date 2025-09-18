#!/bin/bash

# 🎯 Multi-Agent Consensus Evaluation API Examples
# =================================================
# This file contains working examples for testing the enhanced consensus evaluation system

echo "🎯 Multi-Agent Consensus Evaluation API Examples"
echo "================================================="
echo

# Get available test candidates
echo "📋 Step 1: Get Available Test Candidates"
echo "----------------------------------------"
echo "curl -s 'http://localhost:8001/evaluation/test-candidates' | jq ."
echo
echo "# Expected Response:"
echo "# {"
echo "#   \"mode\": \"Local Search (Test Mode)\","
echo "#   \"available_candidates\": ["
echo "#     \"Candidate-LMAOGUID\","
echo "#     \"Candidate-TESTCAND1\","
echo "#     \"Candidate-TESTCAND2\""
echo "#   ],"
echo "#   \"total\": 3"
echo "# }"
echo

# Get available rubrics
echo "📖 Step 2: Get Available Rubrics"
echo "--------------------------------"
echo "curl -s 'http://localhost:8001/evaluation/rubrics' | jq '.rubrics[] | {rubric_name, rubric_id}'"
echo
echo "# Expected Response (sample):"
echo "# {"
echo "#   \"rubric_name\": \"Software Engineer Hiring\","
echo "#   \"rubric_id\": \"734dcc3f-31e3-4eff-b540-508a4aa271cf\""
echo "# }"
echo

# Check evaluation mode
echo "⚙️  Step 3: Check Evaluation Configuration"
echo "-----------------------------------------"
echo "curl -s 'http://localhost:8001/evaluation/evaluation-mode' | jq ."
echo
echo "# Expected Response:"
echo "# {"
echo "#   \"evaluation_mode\": \"consensus\","
echo "#   \"search_mode\": \"local\","
echo "#   \"features\": {\"consensus_evaluation\": true, \"local_search\": true}"
echo "# }"
echo

# Single candidate evaluation with consensus
echo "🤝 Step 4: Single Candidate Consensus Evaluation"
echo "------------------------------------------------"
echo "curl -X POST 'http://localhost:8001/evaluation/evaluate' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{"
echo "    \"rubric_id\": \"734dcc3f-31e3-4eff-b540-508a4aa271cf\","
echo "    \"candidate_ids\": [\"Candidate-TESTCAND1\"]"
echo "  }' | jq ."
echo
echo "# Expected Response:"
echo "# {"
echo "#   \"status\": \"success\","
echo "#   \"is_batch\": false,"
echo "#   \"evaluation_id\": \"uuid-here\","
echo "#   \"evaluation\": null,"
echo "#   \"batch_result\": null,"
echo "#   \"error\": null"
echo "# }"
echo

# Multiple candidates evaluation
echo "👥 Step 5: Multiple Candidates Batch Evaluation"
echo "-----------------------------------------------"
echo "curl -X POST 'http://localhost:8001/evaluation/evaluate' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{"
echo "    \"rubric_id\": \"734dcc3f-31e3-4eff-b540-508a4aa271cf\","
echo "    \"candidate_ids\": [\"Candidate-TESTCAND1\", \"Candidate-TESTCAND2\"],"
echo "    \"comparison_mode\": \"deterministic\","
echo "    \"ranking_strategy\": \"overall_score\""
echo "  }' | jq ."
echo

# Simple evaluation endpoint
echo "⚡ Step 6: Simple Evaluation (Returns Only ID)"
echo "---------------------------------------------"
echo "curl -X POST 'http://localhost:8001/evaluation/simple' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{"
echo "    \"rubric_id\": \"734dcc3f-31e3-4eff-b540-508a4aa271cf\","
echo "    \"candidate_ids\": [\"Candidate-TESTCAND2\"]"
echo "  }' | jq ."
echo

# Retrieve detailed evaluation results
echo "📊 Step 7: Retrieve Detailed Evaluation Results"
echo "----------------------------------------------"
echo "# Replace EVALUATION_ID with the ID from previous steps"
echo "curl -s 'http://localhost:8000/candidates/evaluations/EVALUATION_ID' | jq ."
echo
echo "# To get just the consensus metadata:"
echo "curl -s 'http://localhost:8000/candidates/evaluations/EVALUATION_ID' | jq '.individual_results[0].consensus_metadata'"
echo
echo "# To get agent detailed reasoning:"
echo "curl -s 'http://localhost:8000/candidates/evaluations/EVALUATION_ID' | jq '.individual_results[0].agent_detailed_reasoning'"
echo
echo "# To get debate history:"
echo "curl -s 'http://localhost:8000/candidates/evaluations/EVALUATION_ID' | jq '.individual_results[0].debate_history'"
echo

# Working example with actual IDs
echo "🔧 Working Example (Copy & Paste Ready)"
echo "======================================="
echo "# 1. Run a consensus evaluation:"
echo "curl -X POST 'http://localhost:8001/evaluation/evaluate' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{"
echo "    \"rubric_id\": \"734dcc3f-31e3-4eff-b540-508a4aa271cf\","
echo "    \"candidate_ids\": [\"Candidate-TESTCAND1\"]"
echo "  }'"
echo
echo "# 2. Extract evaluation_id from response, then:"
echo "# curl -s 'http://localhost:8000/candidates/evaluations/YOUR_EVALUATION_ID' | jq '.individual_results[0] | {overall_score, consensus_metadata, agent_detailed_reasoning}'"
echo

# Health checks
echo "🏥 Health Checks"
echo "==============="
echo "# Agent service health:"
echo "curl -s 'http://localhost:8001/evaluation/health' | jq ."
echo
echo "# Criteria API health:"
echo "curl -s 'http://localhost:8000/health' | jq ."
echo

# Error examples
echo "❌ Common Errors & Troubleshooting"
echo "=================================="
echo "# Invalid rubric ID:"
echo "curl -X POST 'http://localhost:8001/evaluation/evaluate' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"rubric_id\": \"invalid-id\", \"candidate_ids\": [\"test\"]}'"
echo
echo "# Invalid candidate ID:"
echo "curl -X POST 'http://localhost:8001/evaluation/evaluate' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"rubric_id\": \"734dcc3f-31e3-4eff-b540-508a4aa271cf\", \"candidate_ids\": [\"invalid-candidate\"]}'"
echo

echo "🎉 Multi-Agent Consensus Features Demonstrated:"
echo "==============================================="
echo "✅ Detailed per-criterion reasoning from both agents"
echo "✅ Complete debate transcript with rebuttals"
echo "✅ Consensus metadata showing agreement process"
echo "✅ Weighted scoring between strict and generous evaluators"
echo "✅ Full audit trail of evaluation rounds"
echo "✅ Agent confidence levels and reasoning capture"
echo
