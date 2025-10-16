"""
Context Builder - Converts analysis metadata into enriched AI context
This is the key innovation: giving AI structured information to focus on
"""
from typing import Dict, Any, List


class ContextBuilder:
    """
    Builds natural language context from static analysis results.
    This context makes AI reviews smarter and more focused.
    """
    
    def build_context(self, analysis_results: Dict[str, Any], code: str) -> str:
        """
        Convert metadata into a structured natural language prompt.
        
        Args:
            analysis_results: Output from BasicAnalyzer
            code: Original source code
            
        Returns:
            Formatted context string for AI prompt
        """
        structure = analysis_results.get("structure", {})
        complexity = analysis_results.get("complexity", {})
        patterns = analysis_results.get("patterns", [])
        issues = analysis_results.get("issues", [])
        metadata = analysis_results.get("metadata", {})
        
        context = f"""# CODE ANALYSIS CONTEXT

## File Overview
- **Filename**: {metadata.get('filename', 'unknown')}
- **Language**: {metadata.get('language', 'unknown')}
- **Total Lines**: {structure.get('total_lines', 0)}
- **Code Lines**: {structure.get('code_lines', 0)}
- **Comment Lines**: {structure.get('comment_lines', 0)}
- **Blank Lines**: {structure.get('blank_lines', 0)}

## Structure Summary
- **Functions**: {structure.get('functions_count', 0)}
- **Classes**: {structure.get('classes_count', 0)}
- **Imports**: {structure.get('imports_count', 0)}
- **Uses Async**: {'Yes' if structure.get('is_async') else 'No'}

{self._format_functions(structure.get('functions', []))}

{self._format_classes(structure.get('classes', []))}

## Complexity Analysis
- **Average Complexity**: {complexity.get('average', 0)}
- **Maximum Complexity**: {complexity.get('max', 0)}
- **Total Complexity Points**: {complexity.get('total', 0)}

{self._format_complex_functions(complexity.get('complex_functions', []))}

## Code Patterns Detected
{self._format_patterns(patterns)}

## Pre-Identified Issues ({len(issues)} found)
{self._format_issues(issues)}

## Focus Areas for AI Review

Based on the above pre-analysis, please focus your review on:

1. **Issue Validation**: Review the {len(issues)} pre-identified issues above
   - Confirm which are true positives vs false positives
   - Assess the actual severity and impact
   - Provide specific fix recommendations

2. **Logic Analysis**: Examine the code logic for:
   - Business logic errors
   - Edge case handling
   - Potential race conditions or concurrency issues
   - Algorithm correctness

3. **Architecture & Design**:
   - Code organization and structure
   - Design pattern usage
   - Separation of concerns
   - Testability

4. **Security Beyond Basic Patterns**:
   - Authentication/authorization logic
   - Input validation and sanitization
   - Data exposure risks
   - Cryptographic usage

5. **Performance Considerations**:
   - Inefficient algorithms or data structures
   - Unnecessary computations
   - Memory leaks or resource management

6. **Best Practices**:
   - Language-specific idioms
   - Error handling completeness
   - Code maintainability
   - Documentation quality

Please provide a structured review that:
- Validates or dismisses each pre-identified issue
- Identifies NEW issues that static analysis cannot detect
- Prioritizes findings by severity and impact
- Gives specific, actionable recommendations

---
"""
        return context
    
    def _format_functions(self, functions: List[Dict]) -> str:
        """Format function list"""
        if not functions:
            return ""
        
        if len(functions) <= 5:
            func_list = "\n".join([f"  - `{f['name']}` (line {f['line']})" for f in functions])
        else:
            func_list = "\n".join([f"  - `{f['name']}` (line {f['line']})" for f in functions[:5]])
            func_list += f"\n  - ... and {len(functions) - 5} more"
        
        return f"""
### Functions Found
{func_list}
"""
    
    def _format_classes(self, classes: List[Dict]) -> str:
        """Format class list"""
        if not classes:
            return ""
        
        class_list = "\n".join([f"  - `{c['name']}` (line {c['line']})" for c in classes])
        return f"""
### Classes Found
{class_list}
"""
    
    def _format_complex_functions(self, complex_functions: List[Dict]) -> str:
        """Format high-complexity functions"""
        if not complex_functions:
            return "\n✓ No functions with excessive complexity detected."
        
        result = "\n### ⚠️ High Complexity Functions (Complexity > 10)\n"
        for func in complex_functions:
            result += f"  - `{func['name']}` at line {func['line']}: **Complexity {func['complexity']}**\n"
        result += "\n*These functions may need refactoring or extra review.*\n"
        return result
    
    def _format_patterns(self, patterns: List[Dict]) -> str:
        """Format detected code patterns"""
        if not patterns:
            return "No specific patterns detected.\n"
        
        result = ""
        grouped = {}
        
        # Group patterns by category
        for pattern in patterns:
            category = pattern.get('category', 'other')
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(pattern)
        
        # Format by category
        category_labels = {
            'database': '🗄️ Database Operations',
            'api': '🌐 API Endpoints',
            'error_handling': '⚠️ Error Handling',
            'async': '⚡ Async Operations',
            'logging': '📝 Logging',
            'http': '🌍 HTTP Requests',
            'file_io': '📁 File I/O',
            'security': '🔒 Security/Authentication'
        }
        
        for category, category_patterns in grouped.items():
            label = category_labels.get(category, category.title())
            result += f"\n### {label}\n"
            for pattern in category_patterns:
                result += f"- **{pattern['name']}**: {pattern['count']} occurrence(s)\n"
                if pattern.get('occurrences'):
                    result += f"  - First seen at line {pattern['occurrences'][0]['line']}\n"
        
        return result
    
    def _format_issues(self, issues: List[Dict]) -> str:
        """Format pre-identified issues grouped by severity"""
        if not issues:
            return "✓ No basic issues detected in pre-analysis.\n"
        
        # Group by severity
        critical = [i for i in issues if i.get('severity') == 'critical']
        medium = [i for i in issues if i.get('severity') == 'medium']
        low = [i for i in issues if i.get('severity') == 'low']
        
        result = ""
        
        if critical:
            result += "\n### 🔴 Critical Issues\n"
            for issue in critical[:5]:  # Limit to first 5
                result += self._format_single_issue(issue)
        
        if medium:
            result += "\n### 🟡 Medium Issues\n"
            for issue in medium[:5]:
                result += self._format_single_issue(issue)
        
        if low:
            result += f"\n### 🔵 Low Priority Issues ({len(low)} total)\n"
            for issue in low[:3]:
                result += self._format_single_issue(issue)
            if len(low) > 3:
                result += f"  - ... and {len(low) - 3} more low-priority issues\n"
        
        return result
    
    def _format_single_issue(self, issue: Dict) -> str:
        """Format a single issue"""
        return f"""
**Line {issue['line']}**: {issue['type']}
- Message: {issue['message']}
- Code: `{issue.get('code_snippet', 'N/A')}`
"""
    
    def build_summary_context(self, analysis_results: Dict[str, Any]) -> str:
        """
        Build a shorter context for quick summaries.
        """
        structure = analysis_results.get("structure", {})
        issues = analysis_results.get("issues", [])
        
        critical_count = len([i for i in issues if i.get('severity') == 'critical'])
        medium_count = len([i for i in issues if i.get('severity') == 'medium'])
        
        return f"""Quick Summary:
- {structure.get('total_lines', 0)} lines, {structure.get('functions_count', 0)} functions
- {len(issues)} issues found ({critical_count} critical, {medium_count} medium)
"""
