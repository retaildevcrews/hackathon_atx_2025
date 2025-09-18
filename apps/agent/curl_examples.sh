#!/bin/bash

# 🎯 Multi-Agent Consensus Evaluation API Examples
# =================================================
# This file contains working examples for testing the enhanced consensus evaluation system
# with detailed agent reasoning and debate capture.

echo "🎯 Multi-Agent Consensus Evaluation API Examples"
echo "================================================="
echo

# Get available test candidates
echo "📋 Step 1: Get Available Test Candidates"
echo "----------------------------------------"
echo "curl -s 'http://localhost:8001/evaluation/test-candidates' | jq ."
echo
echo "# Expected Response: Lists all 37+ available candidates including:"
echo "# - Software Engineer Hiring: Candidate-HIRING-ALICE-RIVERA, Candidate-HIRING-BENJAMIN-CHO, etc."
echo "# - TV Evaluations: Candidate-TV-LG-OLED-C3-55, Candidate-TV-SAMSUNG-QN90C-55, etc."
echo "# - Grant Proposals: Candidate-GRANT-URBAN-AIR-QUALITY-SENSORS, etc."
echo "# - Test Candidates: Candidate-TESTCAND1, Candidate-TESTCAND2, etc."
echo

# Get available rubrics
echo "📖 Step 2: Get Available Rubrics"
echo "--------------------------------"
echo "curl -s 'http://localhost:8001/evaluation/rubrics' | jq '.rubrics[] | {rubric_name, rubric_id}'"
echo
echo "# Key rubrics for testing:"
echo "# - Software Engineer Hiring: 734dcc3f-31e3-4eff-b540-508a4aa271cf"
echo "# - TV Evaluation: b863cadf-894f-4e54-a0ea-811fbcd889ac"
echo "# - Grant Proposal Review: eb91e0cc-5c19-411f-8d24-47780df2c24f"
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
echo

# Single candidate evaluation with consensus
echo "🤝 Step 4: Single Candidate Consensus Evaluation - Software Engineer"
echo "-------------------------------------------------------------------"
echo "curl -X POST 'http://localhost:8001/evaluation/evaluate' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{"
echo "    \"rubric_id\": \"734dcc3f-31e3-4eff-b540-508a4aa271cf\","
echo "    \"candidate_ids\": [\"Candidate-HIRING-ALICE-RIVERA\"]"
echo "  }' | jq ."
echo
echo "# Expected Response:"
echo "# {"
echo "#   \"status\": \"success\","
echo "#   \"is_batch\": false,"
echo "#   \"evaluation_id\": \"uuid-here\""
echo "# }"
echo
echo "# This triggers a multi-agent consensus evaluation with:"
echo "# - Agent A (Strict): Conservative scoring with rigorous standards"
echo "# - Agent B (Generous): Optimistic scoring recognizing potential"
echo "# - 2 rounds of debate to reach consensus"
echo "# - Detailed per-criterion reasoning from both agents"
echo

echo "� Step 5: TV Evaluation Example"
echo "-------------------------------"
echo "curl -X POST 'http://localhost:8001/evaluation/evaluate' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{"
echo "    \"rubric_id\": \"b863cadf-894f-4e54-a0ea-811fbcd889ac\","
echo "    \"candidate_ids\": [\"Candidate-TV-LG-OLED-C3-55\"]"
echo "  }' | jq ."
echo

echo "🎓 Step 6: Grant Proposal Evaluation"
echo "-----------------------------------"
echo "curl -X POST 'http://localhost:8001/evaluation/evaluate' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{"
echo "    \"rubric_id\": \"eb91e0cc-5c19-411f-8d24-47780df2c24f\","
echo "    \"candidate_ids\": [\"Candidate-GRANT-URBAN-AIR-QUALITY-SENSORS\"]"
echo "  }' | jq ."
echo

echo "⚡ Step 7: Simple Evaluation (Returns Only ID)"
echo "---------------------------------------------"
echo "curl -X POST 'http://localhost:8001/evaluation/simple' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{"
echo "    \"rubric_id\": \"734dcc3f-31e3-4eff-b540-508a4aa271cf\","
echo "    \"candidate_ids\": [\"Candidate-HIRING-BENJAMIN-CHO\"]"
echo "  }' | jq ."
echo

echo "📊 Step 8: Retrieve Detailed Evaluation Results"
echo "----------------------------------------------"
echo "# Replace EVALUATION_ID with the ID from previous steps"
echo "curl -s 'http://localhost:8000/candidates/evaluations/EVALUATION_ID' | jq ."
echo
echo "# Example working evaluation ID (replace with your own):"
echo "# curl -s 'http://localhost:8000/candidates/evaluations/36ce8137-edeb-450a-b913-eafd4ecffaaf' | jq ."
echo
echo "# To get just the consensus metadata and overall score:"
echo "curl -s 'http://localhost:8000/candidates/evaluations/EVALUATION_ID' | jq '.individual_results[0] | {overall_score, consensus_metadata}'"
echo
echo "# To get agent detailed reasoning (shows both agents' perspectives):"
echo "curl -s 'http://localhost:8000/candidates/evaluations/EVALUATION_ID' | jq '.individual_results[0].agent_detailed_reasoning'"
echo
echo "# To get debate history (shows how consensus was reached):"
echo "curl -s 'http://localhost:8000/candidates/evaluations/EVALUATION_ID' | jq '.individual_results[0].debate_history'"
echo
echo "# To get per-criterion agent reasoning:"
echo "curl -s 'http://localhost:8000/candidates/evaluations/EVALUATION_ID' | jq '.individual_results[0].criteria_evaluations[] | {criterion_name, score, agent_a_reasoning, agent_b_reasoning}'"
echo

echo "🔧 Working Examples (Copy & Paste Ready)"
echo "========================================"
echo
echo "# Example 1: Software Engineer Evaluation"
echo "curl -X POST 'http://localhost:8001/evaluation/evaluate' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{"
echo "    \"rubric_id\": \"734dcc3f-31e3-4eff-b540-508a4aa271cf\","
echo "    \"candidate_ids\": [\"Candidate-HIRING-ALICE-RIVERA\"]"
echo "  }' | jq ."
echo
echo "# Example 2: Compare 3 Engineer Candidates (Individual Evaluations)"
echo "echo 'Evaluating Alice Rivera...'"
echo "curl -X POST 'http://localhost:8001/evaluation/evaluate' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"rubric_id\": \"734dcc3f-31e3-4eff-b540-508a4aa271cf\", \"candidate_ids\": [\"Candidate-HIRING-ALICE-RIVERA\"]}' | jq '.evaluation_id'"
echo
echo "echo 'Evaluating Benjamin Cho...'"
echo "curl -X POST 'http://localhost:8001/evaluation/evaluate' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"rubric_id\": \"734dcc3f-31e3-4eff-b540-508a4aa271cf\", \"candidate_ids\": [\"Candidate-HIRING-BENJAMIN-CHO\"]}' | jq '.evaluation_id'"
echo
echo "echo 'Evaluating Priya Natarajan...'"
echo "curl -X POST 'http://localhost:8001/evaluation/evaluate' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"rubric_id\": \"734dcc3f-31e3-4eff-b540-508a4aa271cf\", \"candidate_ids\": [\"Candidate-HIRING-PRIYA-NATARAJAN\"]}' | jq '.evaluation_id'"
echo

echo "🏥 Health Checks"
echo "==============="
echo "# Agent service health:"
echo "curl -s 'http://localhost:8001/evaluation/health' | jq ."
echo
echo "# Criteria API health:"
echo "curl -s 'http://localhost:8000/health' | jq ."
echo

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

echo "🎊 Sample Results Analysis"
echo "=========================="
echo "# Based on recent test results, here's what to expect:"
echo "# "
echo "# Alice Rivera: Overall Score 2.49"
echo "#   - Strict Agent: 2.27 (identified significant gaps)"
echo "#   - Generous Agent: 2.83 (recognized potential)"
echo "#   - Consensus reached after 2 rounds of debate"
echo "# "
echo "# Benjamin Cho: Overall Score 2.95"
echo "#   - Strict Agent: 2.70 (more favorable assessment)"
echo "#   - Generous Agent: 3.32 (strong potential)"
echo "#   - Better score difference convergence (0.62 gap)"
echo "# "
echo "# Priya Natarajan: Overall Score 2.49"
echo "#   - Similar pattern to Alice Rivera"
echo "#   - Shows consistency in evaluation methodology"
echo

echo "🚀 Advanced Analysis Commands"
echo "============================"
echo "# Compare final consensus scores:"
echo "curl -s 'http://localhost:8000/candidates/evaluations/EVAL_ID_1' | jq '.individual_results[0].overall_score'"
echo "curl -s 'http://localhost:8000/candidates/evaluations/EVAL_ID_2' | jq '.individual_results[0].overall_score'"
echo "curl -s 'http://localhost:8000/candidates/evaluations/EVAL_ID_3' | jq '.individual_results[0].overall_score'"
echo
echo "# Analyze debate progression:"
echo "curl -s 'http://localhost:8000/candidates/evaluations/EVAL_ID' | jq '.individual_results[0].debate_history | map({round, score_diff: (.generous_score - .strict_score)})'"
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
