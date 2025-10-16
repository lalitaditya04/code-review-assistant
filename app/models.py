"""
Database models for Code Review Assistant
Uses SQLAlchemy with SQLite for simplicity
"""
from sqlalchemy import Column, String, Integer, JSON, DateTime, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class Review(Base):
    """
    Model for storing code review results.
    Everything is stored as JSON for flexibility.
    """
    __tablename__ = "reviews"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # File information
    filename = Column(String, nullable=False, index=True)
    language = Column(String, index=True)
    file_size = Column(Integer)  # in bytes
    
    # Analysis results (stored as JSON)
    pre_analysis = Column(JSON)
    ai_review = Column(JSON)
    final_result = Column(JSON)
    
    # Quick access fields
    score = Column(Integer, index=True)  # 0-100
    total_issues = Column(Integer, default=0)
    critical_issues = Column(Integer, default=0)
    medium_issues = Column(Integer, default=0)
    low_issues = Column(Integer, default=0)
    
    # AI provider info
    ai_provider = Column(String)
    ai_model = Column(String)
    
    # Summary
    summary = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    processing_time = Column(Float)  # in seconds
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "filename": self.filename,
            "language": self.language,
            "file_size": self.file_size,
            "score": self.score,
            "total_issues": self.total_issues,
            "critical_issues": self.critical_issues,
            "medium_issues": self.medium_issues,
            "low_issues": self.low_issues,
            "ai_provider": self.ai_provider,
            "ai_model": self.ai_model,
            "summary": self.summary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "processing_time": self.processing_time
        }
    
    def to_dict_detailed(self):
        """Convert to dictionary with full details"""
        base = self.to_dict()
        base.update({
            "pre_analysis": self.pre_analysis,
            "ai_review": self.ai_review,
            "final_result": self.final_result
        })
        return base


class ReviewStats(Base):
    """
    Model for storing aggregated statistics.
    Updated periodically or on-demand.
    """
    __tablename__ = "review_stats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Overall statistics
    total_reviews = Column(Integer, default=0)
    total_files_reviewed = Column(Integer, default=0)
    
    # Average metrics
    avg_score = Column(Float, default=0)
    avg_issues_per_file = Column(Float, default=0)
    
    # Issue counts
    total_critical_issues = Column(Integer, default=0)
    total_medium_issues = Column(Integer, default=0)
    total_low_issues = Column(Integer, default=0)
    
    # Language breakdown (stored as JSON)
    language_breakdown = Column(JSON)
    
    # Last updated
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "total_reviews": self.total_reviews,
            "total_files_reviewed": self.total_files_reviewed,
            "avg_score": round(self.avg_score, 2) if self.avg_score else 0,
            "avg_issues_per_file": round(self.avg_issues_per_file, 2) if self.avg_issues_per_file else 0,
            "total_critical_issues": self.total_critical_issues,
            "total_medium_issues": self.total_medium_issues,
            "total_low_issues": self.total_low_issues,
            "language_breakdown": self.language_breakdown or {},
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
