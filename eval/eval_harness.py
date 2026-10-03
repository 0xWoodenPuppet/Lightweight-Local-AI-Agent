import json
import sys
import os
from pathlib import Path

# Add parent directory to sys.path so we can import from the main project
sys.path.append(str(Path(__file__).parent.parent))

from agent.orchestrator import run_pipeline
from agent import llm

def evaluate():
    dataset_path = Path(__file__).parent / "dataset.json"
    results_path = Path(__file__).parent / "results.json"
    
    with open(dataset_path, "r") as f:
        dataset = json.load(f)
        
    results = []
    
    metrics = {
        "total": len(dataset),
        "raw_correct": 0,
        "scaffolded_correct": 0,
        "routing_correct": 0,
        "verification_precision": {"true_positive": 0, "false_positive": 0},
        "verification_recall": {"true_positive": 0, "false_negative": 0},
        "overrides": 0  # Tool output was correct, but model final answer was wrong
    }
    
    print(f"Starting evaluation of {len(dataset)} questions...")
    
    for i, item in enumerate(dataset):
        query = item["query"]
        expected_skill = item["expected_skill"]
        ground_truth = item["ground_truth"]
        
        print(f"\n--- [{i+1}/{len(dataset)}] {query} ---")
        
        # 1. Run Raw Baseline
        print("[Raw] Generating...")
        try:
            raw_response, raw_telemetry = llm.chat([{"role": "user", "content": query}], temperature=0.1)
        except Exception as e:
            raw_response = f"Error: {e}"
            
        # 2. Run Scaffolded System
        print("[Scaffolded] Executing pipeline...")
        scaffolded_result = run_pipeline(query)
        
        chosen_skill = scaffolded_result["chosen_skill"]
        final_answer = scaffolded_result["final_answer"]
        verification = scaffolded_result["verification"]
        
        # 3. Assess Correctness
        # Simple string inclusion for ground truth
        def is_correct(answer, truths):
            if not truths:
                return True # For 'none' skill questions without specific GT
            return any(str(t).lower() in str(answer).lower() for t in truths)
            
        raw_is_correct = is_correct(raw_response, ground_truth)
        scaffolded_is_correct = is_correct(final_answer, ground_truth)
        
        if raw_is_correct:
            metrics["raw_correct"] += 1
        if scaffolded_is_correct:
            metrics["scaffolded_correct"] += 1
            
        if chosen_skill == expected_skill:
            metrics["routing_correct"] += 1
            
        # 4. Assess Verification
        v_passed = verification["verified"]
        
        if v_passed and scaffolded_is_correct:
            metrics["verification_precision"]["true_positive"] += 1
            metrics["verification_recall"]["true_positive"] += 1
        elif v_passed and not scaffolded_is_correct:
            metrics["verification_precision"]["false_positive"] += 1
        elif not v_passed and scaffolded_is_correct:
            metrics["verification_recall"]["false_negative"] += 1
            
        # Check override (tool executed, verification passed or partially passed, but final answer wrong)
        # Note: in this simplified check, if the tool execution actually failed but model hallucinated correctly, 
        # it wouldn't count as an override.
        if expected_skill != "none" and not scaffolded_is_correct and v_passed:
            metrics["overrides"] += 1
            
        result_record = {
            "query": query,
            "expected_skill": expected_skill,
            "chosen_skill": chosen_skill,
            "ground_truth": ground_truth,
            "raw_response": raw_response,
            "raw_correct": raw_is_correct,
            "scaffolded_answer": final_answer,
            "scaffolded_correct": scaffolded_is_correct,
            "verification": verification
        }
        results.append(result_record)
        
        print(f"Raw Correct: {raw_is_correct}")
        print(f"Scaffolded Correct: {scaffolded_is_correct}")
        
    with open(results_path, "w") as f:
        json.dump({"metrics": metrics, "results": results}, f, indent=2)
        
    print("\n================ EVALUATION SUMMARY ================")
    print(f"Total Questions: {metrics['total']}")
    print(f"Raw Accuracy: {metrics['raw_correct'] / metrics['total'] * 100:.1f}% ({metrics['raw_correct']}/{metrics['total']})")
    print(f"Scaffolded Accuracy: {metrics['scaffolded_correct'] / metrics['total'] * 100:.1f}% ({metrics['scaffolded_correct']}/{metrics['total']})")
    print(f"Routing Accuracy: {metrics['routing_correct'] / metrics['total'] * 100:.1f}% ({metrics['routing_correct']}/{metrics['total']})")
    
    tp = metrics["verification_precision"]["true_positive"]
    fp = metrics["verification_precision"]["false_positive"]
    fn = metrics["verification_recall"]["false_negative"]
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    
    print(f"Verification Precision: {precision * 100:.1f}%")
    print(f"Verification Recall: {recall * 100:.1f}%")
    print(f"Overrides (Tool passed, Model failed): {metrics['overrides']}")
    print("====================================================")
    print(f"Detailed results saved to {results_path}")

if __name__ == "__main__":
    evaluate()
