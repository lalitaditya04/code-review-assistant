"""
Evaluation API Endpoints
Provides endpoints for testing and evaluating LLM insight quality
"""

from fastapi import APIRouter, HTTPException
from typing import Dict
from app.evaluation.insight_quality import InsightQualityEvaluator
from app.services.review_service import ReviewService
from app.database import SessionLocal

router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])


@router.get("/benchmark")
async def run_benchmark_evaluation() -> Dict:
    """
    Run the complete benchmark suite to evaluate LLM insight quality
    
    This endpoint:
    1. Loads benchmark test files with known issues
    2. Runs code reviews on each file
    3. Compares detected issues against known issues
    4. Calculates precision, recall, and F1 scores
    5. Evaluates recommendation quality
    
    Returns:
        Dictionary containing:
        - total_tests: Number of benchmark tests
        - completed: Successfully completed tests
        - failed: Failed tests
        - individual_results: Results for each test file
        - aggregate_metrics: Overall performance metrics
    """
    try:
        # Initialize evaluator and review service
        evaluator = InsightQualityEvaluator()
        db = SessionLocal()
        review_service = ReviewService(db)
        
        # Run benchmark suite
        results = evaluator.run_benchmark_suite(review_service)
        
        # Close database session
        db.close()
        
        return {
            "status": "success",
            "message": "Benchmark evaluation completed",
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Benchmark evaluation failed: {str(e)}"
        )


@router.get("/benchmark/report")
async def get_benchmark_report() -> Dict:
    """
    Run benchmark evaluation and return a formatted text report
    
    Returns:
        Dictionary with formatted report string
    """
    try:
        # Initialize evaluator and review service
        evaluator = InsightQualityEvaluator()
        db = SessionLocal()
        review_service = ReviewService(db)
        
        # Run benchmark suite
        results = evaluator.run_benchmark_suite(review_service)
        
        # Generate report
        report = evaluator.generate_evaluation_report(results)
        
        # Close database session
        db.close()
        
        return {
            "status": "success",
            "report": report,
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Report generation failed: {str(e)}"
        )


@router.get("/metrics")
async def get_evaluation_metrics() -> Dict:
    """
    Get quick overview of evaluation metrics
    
    Returns:
        Summary of key performance indicators
    """
    try:
        evaluator = InsightQualityEvaluator()
        db = SessionLocal()
        review_service = ReviewService(db)
        
        results = evaluator.run_benchmark_suite(review_service)
        db.close()
        
        metrics = results.get("aggregate_metrics", {})
        
        return {
            "status": "success",
            "metrics": {
                "precision": f"{metrics.get('average_precision', 0):.1%}",
                "recall": f"{metrics.get('average_recall', 0):.1%}",
                "f1_score": f"{metrics.get('average_f1_score', 0):.1%}",
                "recommendation_quality": f"{metrics.get('average_recommendation_quality', 0):.1%}",
                "tests_completed": results.get("completed", 0),
                "tests_total": results.get("total_tests", 0)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Metrics calculation failed: {str(e)}"
        )


@router.get("/health")
async def evaluation_health_check() -> Dict:
    """
    Check if evaluation system is ready
    
    Returns:
        Status of evaluation system components
    """
    import os
    from pathlib import Path
    
    benchmark_dir = Path("tests/benchmark_files")
    benchmark_files_exist = benchmark_dir.exists()
    
    if benchmark_files_exist:
        benchmark_count = len(list(benchmark_dir.glob("*.py")))
    else:
        benchmark_count = 0
    
    return {
        "status": "healthy",
        "benchmark_directory_exists": benchmark_files_exist,
        "benchmark_files_count": benchmark_count,
        "evaluator_ready": True
    }
