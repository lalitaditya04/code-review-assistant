"""
LLM Insight Quality Evaluation Module
Measures accuracy, relevance, and usefulness of AI findings
"""

from typing import Dict, List, Optional
import json
import os
from pathlib import Path


class InsightQualityEvaluator:
    """
    Evaluates the quality of LLM-generated insights by comparing them
    against benchmark test cases with known issues.
    """
    
    def __init__(self):
        """Initialize the evaluator and load benchmark tests"""
        self.benchmark_tests = self._load_benchmarks()
    
    def _load_benchmarks(self) -> List[Dict]:
        """
        Load benchmark test cases with known issues
        
        Returns:
            List of benchmark test dictionaries
        """
        return [
            {
                "file": "hardcoded_secret.py",
                "language": "python",
                "known_issues": [
                    {
                        "line": 5,
                        "type": "security",
                        "severity": "critical",
                        "description": "Hardcoded API key"
                    }
                ]
            },
            {
                "file": "sql_injection.py",
                "language": "python",
                "known_issues": [
                    {
                        "line": 12,
                        "type": "security",
                        "severity": "critical",
                        "description": "SQL injection vulnerability"
                    }
                ]
            },
            {
                "file": "high_complexity.py",
                "language": "python",
                "known_issues": [
                    {
                        "line": 1,
                        "type": "complexity",
                        "severity": "medium",
                        "description": "High cyclomatic complexity"
                    }
                ]
            },
            {
                "file": "race_condition.py",
                "language": "python",
                "known_issues": [
                    {
                        "line": 8,
                        "type": "concurrency",
                        "severity": "critical",
                        "description": "Race condition in counter increment"
                    }
                ]
            }
        ]
    
    def calculate_precision_recall(self, 
                                   found_issues: List[Dict], 
                                   known_issues: List[Dict]) -> Dict:
        """
        Calculate precision, recall, and F1 score metrics
        
        Precision = True Positives / (True Positives + False Positives)
        Recall = True Positives / (True Positives + False Negatives)
        F1 Score = 2 * (Precision * Recall) / (Precision + Recall)
        
        Args:
            found_issues: Issues detected by the system
            known_issues: Ground truth issues from benchmark
            
        Returns:
            Dictionary with precision, recall, F1 score, and counts
        """
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        matched_issues = []
        
        # Match found issues with known issues
        for known in known_issues:
            found_match = False
            for found in found_issues:
                if self._issues_match(found, known):
                    true_positives += 1
                    matched_issues.append({
                        "known": known,
                        "found": found,
                        "match": "true_positive"
                    })
                    found_match = True
                    break
            
            if not found_match:
                false_negatives += 1
                matched_issues.append({
                    "known": known,
                    "found": None,
                    "match": "false_negative"
                })
        
        # Count false positives (found but not in known issues)
        for found in found_issues:
            if not any(self._issues_match(found, k) for k in known_issues):
                false_positives += 1
                matched_issues.append({
                    "known": None,
                    "found": found,
                    "match": "false_positive"
                })
        
        # Calculate metrics
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1_score": round(f1_score, 3),
            "true_positives": true_positives,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
            "total_found": len(found_issues),
            "total_known": len(known_issues),
            "matched_details": matched_issues
        }
    
    def _issues_match(self, issue1: Dict, issue2: Dict) -> bool:
        """
        Check if two issues refer to the same problem
        
        Issues match if:
        - They are within 2 lines of each other
        - They have the same type or severity
        
        Args:
            issue1: First issue to compare
            issue2: Second issue to compare
            
        Returns:
            True if issues match, False otherwise
        """
        # Extract line numbers
        line1 = issue1.get("line", 0)
        line2 = issue2.get("line", 0)
        
        # Check if lines are close (within 2 lines)
        if abs(line1 - line2) > 2:
            return False
        
        # Check if type or severity matches
        type_match = issue1.get("type", "").lower() == issue2.get("type", "").lower()
        severity_match = issue1.get("severity", "").lower() == issue2.get("severity", "").lower()
        
        return type_match or severity_match
    
    def evaluate_recommendation_quality(self, recommendations: List[str]) -> Dict:
        """
        Evaluate the quality of recommendations provided by the LLM
        
        Quality dimensions:
        - Specificity: Does it mention specific lines/functions?
        - Actionability: Does it provide concrete steps?
        - Clarity: Is it understandable and well-structured?
        
        Args:
            recommendations: List of recommendation strings
            
        Returns:
            Dictionary with quality scores
        """
        if not recommendations:
            return {
                "specificity_score": 0.0,
                "actionability_score": 0.0,
                "clarity_score": 0.0,
                "overall_quality": 0.0,
                "total_recommendations": 0
            }
        
        scores = {
            "specificity": 0,
            "actionability": 0,
            "clarity": 0
        }
        
        for rec in recommendations:
            if not rec or not isinstance(rec, str):
                continue
            
            rec_lower = rec.lower()
            
            # Check specificity (mentions line numbers/function names/code elements)
            specificity_keywords = ["line", "function", "class", "variable", "method", "parameter"]
            if any(keyword in rec_lower for keyword in specificity_keywords):
                scores["specificity"] += 1
            
            # Check actionability (contains action verbs and concrete steps)
            action_verbs = ["replace", "refactor", "add", "remove", "change", "use", 
                          "move", "extract", "rename", "implement", "fix"]
            if any(verb in rec_lower for verb in action_verbs):
                scores["actionability"] += 1
            
            # Check clarity (has reasonable length and structure)
            word_count = len(rec.split())
            if 10 < word_count < 150:  # Not too short, not too long
                scores["clarity"] += 1
        
        total = len(recommendations)
        
        return {
            "specificity_score": round(scores["specificity"] / total, 3),
            "actionability_score": round(scores["actionability"] / total, 3),
            "clarity_score": round(scores["clarity"] / total, 3),
            "overall_quality": round(sum(scores.values()) / (3 * total), 3),
            "total_recommendations": total
        }
    
    def run_benchmark_suite(self, review_service) -> Dict:
        """
        Run all benchmark tests and aggregate results
        
        Args:
            review_service: ReviewService instance to perform reviews
            
        Returns:
            Dictionary with individual and aggregate results
        """
        results = []
        benchmark_dir = Path("tests/benchmark_files")
        
        for test in self.benchmark_tests:
            file_path = benchmark_dir / test['file']
            
            # Skip if file doesn't exist
            if not file_path.exists():
                results.append({
                    "file": test["file"],
                    "status": "skipped",
                    "reason": "Benchmark file not found"
                })
                continue
            
            try:
                # Read benchmark file
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                # Run review
                review = review_service.perform_full_review(
                    filename=test['file'],
                    language=test['language'],
                    code_content=code
                )
                
                # Extract found issues from both pre-analysis and AI review
                pre_issues = review.get("pre_analysis", {}).get("issues", [])
                ai_validated = review.get("ai_review", {}).get("validated_issues", [])
                ai_new = review.get("ai_review", {}).get("new_findings", [])
                
                # Combine all found issues
                found_issues = pre_issues + ai_validated + ai_new
                
                # Calculate metrics
                metrics = self.calculate_precision_recall(
                    found_issues, 
                    test["known_issues"]
                )
                
                # Evaluate recommendations
                recommendations = []
                for issue in ai_validated + ai_new:
                    if issue.get("recommendation"):
                        recommendations.append(issue["recommendation"])
                
                rec_quality = self.evaluate_recommendation_quality(recommendations)
                
                results.append({
                    "file": test["file"],
                    "status": "completed",
                    "metrics": metrics,
                    "recommendation_quality": rec_quality,
                    "score": review.get("combined_score", 0)
                })
                
            except Exception as e:
                results.append({
                    "file": test["file"],
                    "status": "failed",
                    "error": str(e)
                })
        
        # Aggregate results (only from completed tests)
        completed_results = [r for r in results if r.get("status") == "completed"]
        
        if completed_results:
            avg_precision = sum(r["metrics"]["precision"] for r in completed_results) / len(completed_results)
            avg_recall = sum(r["metrics"]["recall"] for r in completed_results) / len(completed_results)
            avg_f1 = sum(r["metrics"]["f1_score"] for r in completed_results) / len(completed_results)
            avg_rec_quality = sum(r["recommendation_quality"]["overall_quality"] for r in completed_results) / len(completed_results)
        else:
            avg_precision = avg_recall = avg_f1 = avg_rec_quality = 0
        
        return {
            "total_tests": len(self.benchmark_tests),
            "completed": len(completed_results),
            "failed": len([r for r in results if r.get("status") == "failed"]),
            "skipped": len([r for r in results if r.get("status") == "skipped"]),
            "individual_results": results,
            "aggregate_metrics": {
                "average_precision": round(avg_precision, 3),
                "average_recall": round(avg_recall, 3),
                "average_f1_score": round(avg_f1, 3),
                "average_recommendation_quality": round(avg_rec_quality, 3)
            }
        }
    
    def generate_evaluation_report(self, benchmark_results: Dict) -> str:
        """
        Generate a human-readable evaluation report
        
        Args:
            benchmark_results: Results from run_benchmark_suite()
            
        Returns:
            Formatted string report
        """
        report = []
        report.append("=" * 60)
        report.append("LLM INSIGHT QUALITY EVALUATION REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Summary
        report.append("SUMMARY")
        report.append("-" * 60)
        report.append(f"Total Tests: {benchmark_results['total_tests']}")
        report.append(f"Completed: {benchmark_results['completed']}")
        report.append(f"Failed: {benchmark_results['failed']}")
        report.append(f"Skipped: {benchmark_results['skipped']}")
        report.append("")
        
        # Aggregate Metrics
        metrics = benchmark_results['aggregate_metrics']
        report.append("AGGREGATE METRICS")
        report.append("-" * 60)
        report.append(f"Precision: {metrics['average_precision']:.1%}")
        report.append(f"Recall: {metrics['average_recall']:.1%}")
        report.append(f"F1 Score: {metrics['average_f1_score']:.1%}")
        report.append(f"Recommendation Quality: {metrics['average_recommendation_quality']:.1%}")
        report.append("")
        
        # Individual Results
        report.append("INDIVIDUAL TEST RESULTS")
        report.append("-" * 60)
        for result in benchmark_results['individual_results']:
            report.append(f"\nFile: {result['file']}")
            report.append(f"Status: {result['status']}")
            
            if result['status'] == 'completed':
                m = result['metrics']
                report.append(f"  Precision: {m['precision']:.1%}")
                report.append(f"  Recall: {m['recall']:.1%}")
                report.append(f"  F1 Score: {m['f1_score']:.1%}")
                report.append(f"  True Positives: {m['true_positives']}")
                report.append(f"  False Positives: {m['false_positives']}")
                report.append(f"  False Negatives: {m['false_negatives']}")
            elif result['status'] == 'failed':
                report.append(f"  Error: {result.get('error', 'Unknown error')}")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
