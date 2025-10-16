"""
API Router for code review endpoints
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import time
from datetime import datetime

from app.database import get_db
from app.models import Review, ReviewStats
from app.services.review_service import ReviewService
from app.config import settings

router = APIRouter(prefix="/api", tags=["reviews"])


@router.post("/review")
async def create_review(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a code file and get a complete review.
    Returns immediately with review results (no queue).
    """
    start_time = time.time()
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1]
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file_ext} not supported. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content
    try:
        content = await file.read()
        file_size = len(content)
        
        # Check file size
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
            )
        
        # Save temporarily
        settings.UPLOAD_DIR.mkdir(exist_ok=True)
        temp_path = settings.UPLOAD_DIR / file.filename
        
        with open(temp_path, 'wb') as f:
            f.write(content)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
    
    # Process review
    try:
        service = ReviewService()
        result = await service.process_review(str(temp_path), file.filename)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Save to database
        review = Review(
            filename=file.filename,
            language=result.get("metadata", {}).get("language", "unknown"),
            file_size=file_size,
            pre_analysis=result.get("pre_analysis"),
            ai_review=result.get("ai_review"),
            final_result=result,
            score=result.get("combined_score", 0),
            total_issues=result.get("statistics", {}).get("total_issues", 0),
            critical_issues=result.get("statistics", {}).get("critical", 0),
            medium_issues=result.get("statistics", {}).get("medium", 0),
            low_issues=result.get("statistics", {}).get("low", 0),
            ai_provider=settings.AI_PROVIDER,
            ai_model=settings.AI_MODEL,
            summary=result.get("summary", ""),
            processing_time=processing_time
        )
        
        db.add(review)
        db.commit()
        db.refresh(review)
        
        # Clean up temp file
        try:
            os.remove(temp_path)
        except:
            pass
        
        return {
            "review_id": review.id,
            "result": result,
            "processing_time": round(processing_time, 2)
        }
    
    except Exception as e:
        # Clean up on error
        try:
            os.remove(temp_path)
        except:
            pass
        
        raise HTTPException(status_code=500, detail=f"Error processing review: {str(e)}")


@router.post("/review/quick")
async def quick_review(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Quick scan without AI review - only static analysis.
    Useful for fast feedback.
    """
    start_time = time.time()
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    file_ext = os.path.splitext(file.filename)[1]
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file_ext} not supported"
        )
    
    try:
        content = await file.read()
        file_size = len(content)
        
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")
        
        # Save temporarily
        settings.UPLOAD_DIR.mkdir(exist_ok=True)
        temp_path = settings.UPLOAD_DIR / file.filename
        
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        # Quick scan
        service = ReviewService()
        result = await service.quick_scan(str(temp_path), file.filename)
        
        processing_time = time.time() - start_time
        
        # Clean up
        os.remove(temp_path)
        
        return {
            "result": result,
            "processing_time": round(processing_time, 2)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/review/{review_id}")
def get_review(review_id: str, db: Session = Depends(get_db)):
    """
    Get a saved review by ID.
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    return review.to_dict_detailed()


@router.get("/reviews")
def list_reviews(
    language: Optional[str] = Query(None),
    min_score: Optional[int] = Query(None),
    max_score: Optional[int] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    """
    List all reviews with optional filters.
    """
    query = db.query(Review)
    
    # Apply filters
    if language:
        query = query.filter(Review.language == language)
    
    if min_score is not None:
        query = query.filter(Review.score >= min_score)
    
    if max_score is not None:
        query = query.filter(Review.score <= max_score)
    
    # Order by most recent
    query = query.order_by(Review.created_at.desc())
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination
    reviews = query.offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "reviews": [review.to_dict() for review in reviews]
    }


@router.delete("/review/{review_id}")
def delete_review(review_id: str, db: Session = Depends(get_db)):
    """
    Delete a review by ID.
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    db.delete(review)
    db.commit()
    
    return {"message": "Review deleted successfully"}


@router.get("/stats")
def get_statistics(db: Session = Depends(get_db)):
    """
    Get overall statistics about all reviews.
    """
    reviews = db.query(Review).all()
    
    if not reviews:
        return {
            "total_reviews": 0,
            "avg_score": 0,
            "total_issues": 0,
            "language_breakdown": {}
        }
    
    # Calculate statistics
    total_reviews = len(reviews)
    avg_score = sum(r.score or 0 for r in reviews) / total_reviews
    total_issues = sum(r.total_issues or 0 for r in reviews)
    total_critical = sum(r.critical_issues or 0 for r in reviews)
    total_medium = sum(r.medium_issues or 0 for r in reviews)
    total_low = sum(r.low_issues or 0 for r in reviews)
    
    # Language breakdown
    language_breakdown = {}
    for review in reviews:
        lang = review.language or "unknown"
        if lang not in language_breakdown:
            language_breakdown[lang] = {
                "count": 0,
                "avg_score": 0,
                "total_issues": 0
            }
        language_breakdown[lang]["count"] += 1
        language_breakdown[lang]["avg_score"] += review.score or 0
        language_breakdown[lang]["total_issues"] += review.total_issues or 0
    
    # Calculate averages for each language
    for lang in language_breakdown:
        count = language_breakdown[lang]["count"]
        language_breakdown[lang]["avg_score"] = round(
            language_breakdown[lang]["avg_score"] / count, 2
        )
    
    return {
        "total_reviews": total_reviews,
        "avg_score": round(avg_score, 2),
        "total_issues": total_issues,
        "critical_issues": total_critical,
        "medium_issues": total_medium,
        "low_issues": total_low,
        "language_breakdown": language_breakdown
    }


@router.get("/health")
def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "ai_provider": settings.AI_PROVIDER,
        "ai_model": settings.AI_MODEL,
        "api_key_configured": settings.validate_api_key()
    }
