"""
Basic Analyzer - All-in-one static code analysis
Performs structure, complexity, pattern, and issue detection
"""
import re
from typing import Dict, List, Any
from dataclasses import dataclass
from radon.complexity import cc_visit
from radon.raw import analyze


@dataclass
class Issue:
    """Represents a code issue"""
    line: int
    severity: str  # critical, medium, low
    type: str
    message: str
    code_snippet: str = ""


class BasicAnalyzer:
    """
    Unified analyzer that performs all static analysis in one place.
    This is the core innovation - gathering metadata BEFORE AI analysis.
    """
    
    def __init__(self):
        self.code = ""
        self.lines = []
        self.filename = ""
    
    def analyze_file(self, code: str, filename: str) -> Dict[str, Any]:
        """
        Main entry point - analyzes code and returns all metadata.
        
        Args:
            code: Source code as string
            filename: Name of the file being analyzed
            
        Returns:
            Dictionary with structure, complexity, patterns, and issues
        """
        self.code = code
        self.lines = code.split('\n')
        self.filename = filename
        
        return {
            "structure": self._analyze_structure(),
            "complexity": self._analyze_complexity(),
            "patterns": self._find_patterns(),
            "issues": self._find_basic_issues(),
            "metadata": {
                "filename": filename,
                "language": self._detect_language(filename),
                "total_lines": len(self.lines)
            }
        }
    
    def _analyze_structure(self) -> Dict[str, Any]:
        """
        Extract basic structural information using regex patterns.
        Works across multiple languages.
        """
        structure = {
            "total_lines": len(self.lines),
            "blank_lines": 0,
            "comment_lines": 0,
            "code_lines": 0,
            "functions_count": 0,
            "classes_count": 0,
            "imports_count": 0,
            "is_async": False,
            "functions": [],
            "classes": []
        }
        
        # Count line types
        for line in self.lines:
            stripped = line.strip()
            if not stripped:
                structure["blank_lines"] += 1
            elif stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('/*'):
                structure["comment_lines"] += 1
            else:
                structure["code_lines"] += 1
        
        # Find functions (Python, JavaScript, Java patterns)
        function_patterns = [
            r'def\s+(\w+)\s*\(',  # Python
            r'function\s+(\w+)\s*\(',  # JavaScript
            r'(?:public|private|protected)?\s*\w+\s+(\w+)\s*\(',  # Java/C#
        ]
        
        for pattern in function_patterns:
            for i, line in enumerate(self.lines, 1):
                matches = re.finditer(pattern, line)
                for match in matches:
                    structure["functions_count"] += 1
                    structure["functions"].append({
                        "name": match.group(1),
                        "line": i
                    })
        
        # Find classes
        class_pattern = r'class\s+(\w+)'
        for i, line in enumerate(self.lines, 1):
            matches = re.finditer(class_pattern, line)
            for match in matches:
                structure["classes_count"] += 1
                structure["classes"].append({
                    "name": match.group(1),
                    "line": i
                })
        
        # Count imports
        import_patterns = [
            r'^import\s+',
            r'^from\s+\w+\s+import',
            r'^#include\s+',
        ]
        for line in self.lines:
            if any(re.match(pattern, line.strip()) for pattern in import_patterns):
                structure["imports_count"] += 1
        
        # Check for async code
        if re.search(r'\basync\s+def\b|\basync\s+function\b|\basync\b.*\bawait\b', self.code):
            structure["is_async"] = True
        
        return structure
    
    def _analyze_complexity(self) -> Dict[str, Any]:
        """
        Calculate cyclomatic complexity.
        Uses radon for Python, simple heuristics for other languages.
        """
        complexity = {
            "average": 0,
            "max": 0,
            "total": 0,
            "complex_functions": []
        }
        
        language = self._detect_language(self.filename)
        
        if language == "python":
            try:
                # Use radon for Python
                results = cc_visit(self.code)
                if results:
                    complexities = [r.complexity for r in results]
                    complexity["total"] = sum(complexities)
                    complexity["average"] = round(complexity["total"] / len(complexities), 2)
                    complexity["max"] = max(complexities)
                    
                    # Flag complex functions (complexity > 10)
                    for result in results:
                        if result.complexity > 10:
                            complexity["complex_functions"].append({
                                "name": result.name,
                                "complexity": result.complexity,
                                "line": result.lineno
                            })
            except Exception as e:
                # Fallback to simple counting
                complexity = self._simple_complexity_count()
        else:
            # For non-Python, use simple heuristics
            complexity = self._simple_complexity_count()
        
        return complexity
    
    def _simple_complexity_count(self) -> Dict[str, Any]:
        """
        Simple complexity estimation based on control flow keywords.
        Used for non-Python languages or when radon fails.
        """
        control_keywords = [
            r'\bif\b', r'\belse\b', r'\belif\b', r'\bfor\b', 
            r'\bwhile\b', r'\bswitch\b', r'\bcase\b', r'\bcatch\b',
            r'\b\?\s*.*\s*:\b'  # Ternary operator
        ]
        
        total_complexity = 0
        for line in self.lines:
            for keyword in control_keywords:
                if re.search(keyword, line):
                    total_complexity += 1
        
        return {
            "average": round(total_complexity / max(len(self.lines), 1), 2),
            "max": total_complexity,
            "total": total_complexity,
            "complex_functions": [],
            "note": "Estimated using control flow count"
        }
    
    def _find_patterns(self) -> List[Dict[str, Any]]:
        """
        Detect common code patterns using regex.
        Helps AI understand what the code is doing.
        """
        patterns = []
        
        pattern_definitions = [
            {
                "name": "Database Query",
                "regex": r'(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP)\s+',
                "category": "database"
            },
            {
                "name": "API Endpoint",
                "regex": r'@(app\.|router\.)(get|post|put|delete|patch)',
                "category": "api"
            },
            {
                "name": "Error Handling",
                "regex": r'\btry\s*:|\bcatch\s*\(',
                "category": "error_handling"
            },
            {
                "name": "Async Pattern",
                "regex": r'\basync\b|\bawait\b',
                "category": "async"
            },
            {
                "name": "Logging",
                "regex": r'(logging\.|logger\.|console\.log|print\()',
                "category": "logging"
            },
            {
                "name": "HTTP Request",
                "regex": r'(requests\.|axios\.|fetch\(|http\.)',
                "category": "http"
            },
            {
                "name": "File I/O",
                "regex": r'(open\(|fs\.|File\(|readFile|writeFile)',
                "category": "file_io"
            },
            {
                "name": "Authentication",
                "regex": r'(authenticate|login|password|token|jwt|auth)',
                "category": "security"
            }
        ]
        
        for pattern_def in pattern_definitions:
            matches = []
            for i, line in enumerate(self.lines, 1):
                if re.search(pattern_def["regex"], line, re.IGNORECASE):
                    matches.append({
                        "line": i,
                        "code": line.strip()
                    })
            
            if matches:
                patterns.append({
                    "name": pattern_def["name"],
                    "category": pattern_def["category"],
                    "count": len(matches),
                    "occurrences": matches[:3]  # Limit to first 3 occurrences
                })
        
        return patterns
    
    def _find_basic_issues(self) -> List[Dict[str, Any]]:
        """
        Detect common code issues using simple patterns.
        These are pre-flagged for AI to validate.
        """
        issues = []
        
        # Issue detection rules
        rules = [
            {
                "name": "Hardcoded Secret",
                "regex": r'(api_key|password|secret|token)\s*=\s*["\'][^"\']{8,}["\']',
                "severity": "critical",
                "message": "Possible hardcoded credential detected"
            },
            {
                "name": "SQL String",
                "regex": r'["\'].*?(SELECT|INSERT|UPDATE|DELETE).*?FROM.*?["\']',
                "severity": "medium",
                "message": "Raw SQL string detected - potential SQL injection risk"
            },
            {
                "name": "Print Statement",
                "regex": r'\bprint\s*\(|console\.log\(',
                "severity": "low",
                "message": "Print/console.log found - consider using proper logging"
            },
            {
                "name": "TODO Comment",
                "regex": r'#\s*(TODO|FIXME|XXX|HACK)',
                "severity": "low",
                "message": "Unfinished work flagged in comment"
            },
            {
                "name": "Bare Except",
                "regex": r'except\s*:',
                "severity": "medium",
                "message": "Bare except clause - should catch specific exceptions"
            },
            {
                "name": "Missing Error Handling",
                "regex": r'(requests\.|http\.|fetch\()(?!.*try)',
                "severity": "medium",
                "message": "Network call without apparent error handling"
            }
        ]
        
        for rule in rules:
            for i, line in enumerate(self.lines, 1):
                if re.search(rule["regex"], line, re.IGNORECASE):
                    issues.append({
                        "line": i,
                        "severity": rule["severity"],
                        "type": rule["name"],
                        "message": rule["message"],
                        "code_snippet": line.strip()
                    })
        
        # Check for long lines
        for i, line in enumerate(self.lines, 1):
            if len(line) > 120:
                issues.append({
                    "line": i,
                    "severity": "low",
                    "type": "Long Line",
                    "message": f"Line exceeds 120 characters ({len(line)} chars)",
                    "code_snippet": line[:100] + "..."
                })
        
        # Check for long functions (simple heuristic)
        in_function = False
        function_start = 0
        function_name = ""
        
        for i, line in enumerate(self.lines, 1):
            if re.search(r'def\s+(\w+)|function\s+(\w+)', line):
                if in_function and (i - function_start) > 50:
                    issues.append({
                        "line": function_start,
                        "severity": "medium",
                        "type": "Long Function",
                        "message": f"Function '{function_name}' is {i - function_start} lines long (>50)",
                        "code_snippet": self.lines[function_start - 1].strip()
                    })
                
                in_function = True
                function_start = i
                match = re.search(r'(def|function)\s+(\w+)', line)
                function_name = match.group(2) if match else "unknown"
        
        return issues
    
    def _detect_language(self, filename: str) -> str:
        """Detect programming language from file extension"""
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
