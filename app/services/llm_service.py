"""
LLM Service - Universal AI provider integration
Supports Anthropic Claude, OpenAI GPT, and extensible for other providers
"""
import json
import os
from typing import Dict, Any, Optional
from app.config import settings


class LLMService:
    """
    Universal LLM service that supports multiple AI providers.
    Provider is selected via environment configuration.
    """
    
    def __init__(self):
        self.provider = settings.AI_PROVIDER
        self.model = settings.AI_MODEL
        self.max_tokens = settings.MAX_TOKENS
        self.api_key = settings.get_api_key()
        
        # Validate API key
        if not settings.validate_api_key():
            raise ValueError(
                f"No valid API key found for provider '{self.provider}'. "
                "Please set the appropriate API key in your .env file."
            )
        
        # Initialize the appropriate client
        self.client = self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the AI client based on provider"""
        if self.provider == "anthropic":
            try:
                from anthropic import Anthropic
                return Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "anthropic package not installed. Run: pip install anthropic"
                )
        
        elif self.provider == "openai":
            try:
                from openai import OpenAI
                return OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "openai package not installed. Run: pip install openai"
                )
        
        elif self.provider == "gemini":
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                return genai
            except ImportError:
                raise ImportError(
                    "google-generativeai package not installed. Run: pip install google-generativeai"
                )
        
        elif self.provider == "ollama":
            # Local LLM - no client initialization needed
            return None
        
        else:
            raise ValueError(
                f"Unsupported AI provider: {self.provider}. "
                "Supported providers: 'anthropic', 'openai', 'gemini', 'ollama'"
            )
    
    async def review_with_context(
        self, 
        code: str, 
        context: str,
        language: str
    ) -> Dict[str, Any]:
        """
        Send code to AI with enriched context for review.
        
        Args:
            code: Source code to review
            context: Pre-analyzed context from ContextBuilder
            language: Programming language
            
        Returns:
            Dictionary with review results
        """
        prompt = self._build_review_prompt(code, context, language)
        
        try:
            if self.provider == "anthropic":
                response = await self._call_anthropic(prompt)
            elif self.provider == "openai":
                response = await self._call_openai(prompt)
            elif self.provider == "gemini":
                response = await self._call_gemini(prompt)
            elif self.provider == "ollama":
                response = await self._call_ollama(prompt)
            else:
                raise ValueError(f"Provider {self.provider} not implemented")
            
            return self._parse_response(response)
        
        except Exception as e:
            return {
                "error": str(e),
                "validated_issues": [],
                "false_positives": [],
                "new_findings": [],
                "summary": f"Error during AI review: {str(e)}",
                "score": 0
            }
    
    def _build_review_prompt(self, code: str, context: str, language: str) -> str:
        """Build the complete prompt with context"""
        return f"""You are an expert code reviewer with deep knowledge of software engineering best practices, security, and architecture.

You have been provided with pre-analysis metadata below. This metadata was gathered through static analysis and gives you a head start on understanding the code structure and potential issues.

{context}

---

Now, please review the actual code below. Your task is to:

1. **Validate Pre-Identified Issues**: 
   - Confirm which flagged issues are true positives
   - Identify false positives (issues that aren't actually problems)
   - Assess the real severity and impact of each issue

2. **Find New Issues**: Look for problems that static analysis cannot detect:
   - Logic errors and business logic bugs
   - Race conditions or concurrency issues
   - Security vulnerabilities beyond simple patterns
   - Architectural problems
   - Performance issues
   - Incorrect algorithm implementations

3. **Provide Recommendations**:
   - Specific, actionable fixes for each issue
   - Code improvement suggestions
   - Best practice recommendations

**CODE TO REVIEW:**
```{language}
{code}
```

**IMPORTANT: Please respond with a COMPLETE, VALID JSON object. Do not truncate the response.**

**Response Format (JSON only, no additional text):**

{{
  "validated_issues": [
    {{
      "line": <line_number>,
      "severity": "critical|medium|low",
      "type": "<issue_type>",
      "message": "<explanation>",
      "recommendation": "<how_to_fix>"
    }}
  ],
  "false_positives": [
    {{
      "line": <line_number>,
      "reason": "<why_this_is_not_actually_a_problem>"
    }}
  ],
  "new_findings": [
    {{
      "line": <line_number>,
      "severity": "critical|medium|low",
      "type": "<issue_type>",
      "message": "<explanation>",
      "recommendation": "<how_to_fix>"
    }}
  ],
  "summary": "<overall_assessment_of_code_quality>",
  "score": <0-100>,
  "strengths": ["<what_the_code_does_well>"],
  "key_improvements": ["<prioritized_improvements>"]
}}

**CRITICAL**: 
1. Return ONLY valid JSON (you can wrap in ```json if needed)
2. Ensure ALL brackets and braces are properly closed
3. Prioritize the most important issues if response space is limited
4. Keep messages concise but actionable

Focus on being precise, actionable, and helpful. Prioritize issues by severity and impact.
"""
    
    async def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic Claude API"""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            return message.content[0].text
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")
    
    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI GPT API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert code reviewer. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=0.3  # Lower temperature for more consistent output
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    async def _call_gemini(self, prompt: str) -> str:
        """Call Google Gemini API"""
        try:
            model = self.client.GenerativeModel(
                model_name=self.model,
                generation_config={
                    'temperature': 0.3,
                    'max_output_tokens': self.max_tokens,
                    'top_p': 0.95,
                    'top_k': 40,
                }
            )
            
            response = model.generate_content(prompt)
            
            # Check if response was blocked or incomplete
            if not response.text:
                raise Exception("Gemini returned empty response. Check your API key and model name.")
            
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    async def _call_ollama(self, prompt: str) -> str:
        """Call Local Ollama LLM"""
        try:
            import httpx
            from app.config import settings
            
            async with httpx.AsyncClient(timeout=settings.API_TIMEOUT) as client:
                response = await client.post(
                    f"{settings.OLLAMA_BASE_URL}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,
                            "num_predict": self.max_tokens,
                        }
                    }
                )
                
                if response.status_code != 200:
                    raise Exception(f"Ollama returned status {response.status_code}: {response.text}")
                
                result = response.json()
                return result.get("response", "")
                
        except httpx.ConnectError:
            raise Exception(
                "Cannot connect to Ollama. Make sure Ollama is running at "
                f"{settings.OLLAMA_BASE_URL}. Install from: https://ollama.ai"
            )
        except Exception as e:
            raise Exception(f"Ollama API error: {str(e)}")
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse AI response into structured format.
        Handles both JSON and plain text responses, including truncated responses.
        """
        try:
            # Try to extract JSON from response
            # Sometimes AI wraps JSON in markdown code blocks
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                if json_end == -1:  # No closing backticks (truncated)
                    json_str = response[json_start:].strip()
                else:
                    json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                if json_end == -1:  # No closing backticks (truncated)
                    json_str = response[json_start:].strip()
                else:
                    json_str = response[json_start:json_end].strip()
            else:
                json_str = response.strip()
            
            # Try to fix truncated JSON by completing brackets
            if json_str and not json_str.endswith('}'):
                # Count opening and closing braces
                open_braces = json_str.count('{')
                close_braces = json_str.count('}')
                
                # Add missing closing braces
                if open_braces > close_braces:
                    # Close any open arrays first
                    if json_str.rstrip().endswith(','):
                        json_str = json_str.rstrip().rstrip(',')
                    
                    open_brackets = json_str.count('[')
                    close_brackets = json_str.count(']')
                    
                    # Close arrays
                    json_str += ']' * (open_brackets - close_brackets)
                    # Close objects
                    json_str += '}' * (open_braces - close_braces)
            
            # Parse JSON
            parsed = json.loads(json_str)
            
            # Ensure all required fields exist
            result = {
                "validated_issues": parsed.get("validated_issues", []),
                "false_positives": parsed.get("false_positives", []),
                "new_findings": parsed.get("new_findings", []),
                "summary": parsed.get("summary", "No summary provided"),
                "score": parsed.get("score", 50),
                "strengths": parsed.get("strengths", []),
                "key_improvements": parsed.get("key_improvements", [])
            }
            
            return result
        
        except json.JSONDecodeError as e:
            # If JSON parsing fails, return a structured error response
            print(f"JSON Parse Error: {str(e)}")
            print(f"Failed JSON string (first 500 chars): {json_str[:500] if 'json_str' in locals() else response[:500]}")
            
            return {
                "validated_issues": [],
                "false_positives": [],
                "new_findings": [],
                "summary": f"⚠️ AI response was truncated or malformed. Please increase MAX_TOKENS in .env file. Error: {str(e)}",
                "score": 0,
                "strengths": [],
                "key_improvements": ["Increase MAX_TOKENS to at least 4000 in .env file"],
                "raw_response": response[:1000],
                "parse_error": str(e)
            }
    
    def get_provider_info(self) -> Dict[str, str]:
        """Get information about the current AI provider"""
        return {
            "provider": self.provider,
            "model": self.model,
            "max_tokens": self.max_tokens,
            "api_key_configured": bool(self.api_key and len(self.api_key) > 0)
        }
