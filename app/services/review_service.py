"""
Review Service - Main pipeline that orchestrates the review process
Combines static analysis with AI review
"""
import os
from typing import Dict, Any
from app.analyzers.basic_analyzer import BasicAnalyzer
from app.analyzers.context_builder import ContextBuilder
from app.services.llm_service import LLMService


class ReviewService:
    """
    Main service that orchestrates the complete code review pipeline:
    1. Static pre-analysis
    2. Context building
    3. AI review with enriched context
    4. Results merging
    """
    
    def __init__(self):
        self.analyzer = BasicAnalyzer()
        self.context_builder = ContextBuilder()
        self.llm = LLMService()
    
    async def process_review(self, file_path: str, filename: str) -> Dict[str, Any]:
        """
        Execute the complete review pipeline.
        
        Args:
            file_path: Path to the code file
            filename: Name of the file
            
        Returns:
            Complete review results with merged analysis
        """
        try:
            # Step 1: Read code
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Step 2: Pre-analyze with static tools
            print(f"🔍 Analyzing {filename}...")
            pre_analysis = self.analyzer.analyze_file(code, filename)
            
            # Step 3: Build enriched context
            print(f"📝 Building context...")
            context = self.context_builder.build_context(pre_analysis, code)
            
            # Step 4: AI review with context
            print(f"🤖 Running AI review with {self.llm.provider}...")
            language = self._detect_language(filename)
            ai_review = await self.llm.review_with_context(code, context, language)
            
            # Step 5: Merge results
            print(f"✅ Merging results...")
            final_result = self._merge_results(pre_analysis, ai_review)
            
            return final_result
        
        except Exception as e:
            return {
                "error": str(e),
                "pre_analysis": {},
                "ai_review": {},
                "combined_score": 0,
                "all_issues": [],
                "summary": f"Error processing review: {str(e)}"
            }
    
    def _merge_results(
        self, 
        pre_analysis: Dict[str, Any], 
        ai_review: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge pre-analysis and AI review results.
        Remove false positives and combine all validated issues.
        """
        # Extract pre-analysis issues
        pre_issues = pre_analysis.get("issues", [])
        
        # Extract AI review components
        validated_issues = ai_review.get("validated_issues", [])
        false_positives = ai_review.get("false_positives", [])
        new_findings = ai_review.get("new_findings", [])
        
        # Build false positive line numbers set for quick lookup
        false_positive_lines = {fp.get("line") for fp in false_positives}
        
        # Combine all valid issues
        all_issues = []
        
        # Add validated pre-analysis issues (excluding false positives)
        for issue in pre_issues:
            if issue.get("line") not in false_positive_lines:
                # Mark as validated by AI
                issue["source"] = "pre-analysis"
                issue["ai_validated"] = issue.get("line") in [
                    v.get("line") for v in validated_issues
                ]
                all_issues.append(issue)
        
        # Add new AI findings
        for finding in new_findings:
            finding["source"] = "ai"
            finding["ai_validated"] = True
            all_issues.append(finding)
        
        # Sort by severity
        severity_order = {"critical": 0, "medium": 1, "low": 2}
        all_issues.sort(key=lambda x: severity_order.get(x.get("severity", "low"), 3))
        
        # Calculate combined score
        combined_score = self._calculate_score(pre_analysis, ai_review, all_issues)
        
        # Build comprehensive result
        return {
            "pre_analysis": pre_analysis,
            "ai_review": ai_review,
            "all_issues": all_issues,
            "combined_score": combined_score,
            "statistics": {
                "total_issues": len(all_issues),
                "critical": len([i for i in all_issues if i.get("severity") == "critical"]),
                "medium": len([i for i in all_issues if i.get("severity") == "medium"]),
                "low": len([i for i in all_issues if i.get("severity") == "low"]),
                "pre_analysis_found": len(pre_issues),
                "ai_found": len(new_findings),
                "false_positives": len(false_positives),
                "validated_by_ai": len(validated_issues)
            },
            "summary": ai_review.get("summary", "Review completed"),
            "strengths": ai_review.get("strengths", []),
            "key_improvements": ai_review.get("key_improvements", []),
            "metadata": pre_analysis.get("metadata", {})
        }
    
    def _calculate_score(
        self, 
        pre_analysis: Dict[str, Any], 
        ai_review: Dict[str, Any],
        all_issues: list
    ) -> int:
        """
        Calculate a code quality score (0-100).
        Higher score = better code quality.
        """
        # Start with AI's score if available
        base_score = ai_review.get("score", 70)
        
        # Deduct points for issues
        critical_count = len([i for i in all_issues if i.get("severity") == "critical"])
        medium_count = len([i for i in all_issues if i.get("severity") == "medium"])
        low_count = len([i for i in all_issues if i.get("severity") == "low"])
        
        # Penalty system
        penalty = (critical_count * 15) + (medium_count * 5) + (low_count * 1)
        
        # Calculate final score
        final_score = max(0, min(100, base_score - penalty))
        
        return final_score
    
    def _detect_language(self, filename: str) -> str:
        """Detect programming language from filename"""
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rb': 'ruby',
            '.php': 'php',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.swift': 'swift',
        }
        
        for ext, lang in extension_map.items():
            if filename.endswith(ext):
                return lang
        
        return 'unknown'
    
    async def quick_scan(self, file_path: str, filename: str) -> Dict[str, Any]:
        """
        Quick scan without AI review (for fast feedback).
        Only runs static analysis.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            pre_analysis = self.analyzer.analyze_file(code, filename)
            
            issues = pre_analysis.get("issues", [])
            critical_count = len([i for i in issues if i.get("severity") == "critical"])
            
            return {
                "pre_analysis": pre_analysis,
                "quick_score": max(0, 100 - (critical_count * 20)),
                "summary": f"Quick scan found {len(issues)} potential issues",
                "metadata": pre_analysis.get("metadata", {})
            }
        
        except Exception as e:
            return {
                "error": str(e),
                "summary": f"Error during quick scan: {str(e)}"
            }
