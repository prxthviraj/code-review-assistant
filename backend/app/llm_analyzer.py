import os
from groq import Groq
from dotenv import load_dotenv
import json
import re

# Load environment variables
load_dotenv()

class CodeAnalyzer:
    def __init__(self):
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError("❌ GROQ_API_KEY not found in environment variables!")
        
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"  # Latest Llama model!
    
    def analyze_code(self, code_content, filename):
        """Analyze code using Groq LLM"""
        
        prompt = f"""You are an expert code reviewer. Analyze the following code and provide a detailed review.

Filename: {filename}

Code:
{code_content}
Provide your review in the following JSON format:
{{
    "overall_quality_score": <number 0-100>,
    "summary": "<brief summary of code quality>",
    "errors": [
        {{"type": "<error type>", "line": <line number or null>, "description": "<description>", "severity": "high|medium|low"}}
    ],
    "warnings": [
        {{"type": "<warning type>", "line": <line number or null>, "description": "<description>"}}
    ],
    "suggestions": [
        {{"category": "<category>", "description": "<suggestion>", "priority": "high|medium|low"}}
    ],
    "strengths": ["<strength 1>", "<strength 2>"],
    "readability_score": <number 0-100>,
    "modularity_score": <number 0-100>,
    "best_practices_score": <number 0-100>,
    "security_concerns": ["<concern 1>", "<concern 2>"],
    "performance_notes": ["<note 1>", "<note 2>"]
}}

Be thorough and specific in your analysis. Focus on:
1. Code structure and organization
2. Readability and naming conventions
3. Potential bugs or errors
4. Security vulnerabilities
5. Performance improvements
6. Best practices adherence
7. Documentation quality
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert code reviewer who provides detailed, actionable feedback."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            result = response.choices[0].message.content
            
            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                analysis = json.loads(result)
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error during analysis: {str(e)}")
            return {
                "overall_quality_score": 0,
                "summary": f"Error during analysis: {str(e)}",
                "errors": [],
                "warnings": [],
                "suggestions": [],
                "strengths": [],
                "readability_score": 0,
                "modularity_score": 0,
                "best_practices_score": 0,
                "security_concerns": [],
                "performance_notes": []
            }
    
    def generate_report(self, analysis, filename):
        """Generate a formatted report from analysis"""
        report = {
            "filename": filename,
            "overall_score": analysis.get("overall_quality_score", 0),
            "summary": analysis.get("summary", ""),
            "detailed_scores": {
                "readability": analysis.get("readability_score", 0),
                "modularity": analysis.get("modularity_score", 0),
                "best_practices": analysis.get("best_practices_score", 0)
            },
            "errors": analysis.get("errors", []),
            "warnings": analysis.get("warnings", []),
            "suggestions": analysis.get("suggestions", []),
            "strengths": analysis.get("strengths", []),
            "security_concerns": analysis.get("security_concerns", []),
            "performance_notes": analysis.get("performance_notes", []),
            "metrics": {
                "total_errors": len(analysis.get("errors", [])),
                "total_warnings": len(analysis.get("warnings", [])),
                "total_suggestions": len(analysis.get("suggestions", []))
            }
        }
        
        return report