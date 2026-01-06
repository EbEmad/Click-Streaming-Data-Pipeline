from openai import AsyncOpenAI
from .config import get_settings
from ..LLMInterface import LLMProvider
import json

class OpenAIProvider(LLMProvider):
    """OpenAI-based document quality validation."""
    def __init__(self,default_input_max_characters: int=1000):
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        
        self.default_input_max_characters=default_input_max_characters
        self.client=AsyncOpenAI(api_key=settings.OPENAI_API_KEY,base_url=settings.OPENAI_API_URL)
        self.model=settings.OPENAI_MODEL
        logger.info(f"OpenAI provider initialized with model: {self.model}")
    async def validate_document(self, title: str, content: str, document_id: str) -> QualityCheckResult:
        """Validate document using OpenAI API."""

        prompt=self.await self._build_validation_prompt(title,content)

        try:
            response=await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a document quality validator. Analyze documents and return structured quality assessments."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )

            result_text=response.choices[0].message.content
            logger.info(f"OpenAI validation complete for document {document_id}")
            return self._parse_llm_response(result_text,document_id)
        except Exception as e:
            logger.error(f"OpenAI validation failed for {document_id}: {e}")
            return self._create_error_result(document_id, str(e))
    
    def _build_validation_prompt(self,title:str,content:str)->str:
        """Build the validation prompt for the LLM."""
        truncated_content = content[:self.default_input_max_characters]
        prompt=f"""
            Document Title: {title}
            Document Content: {truncated_content}
            Evaluate the following aspects and return JSON with this exact 
            structure:
            {{
                 "completeness": {{
                        "score": 0-100,
                        "passed": true/false,
                        "issues": ["issue1", "issue2"]
                    }},
                    "consistency": {{
                        "score": 0-100,
                        "passed": true/false,
                        "issues": ["issue1"]
                    }},
                    "pii_detection": {{
                        "score": 0-100,
                        "passed": true/false,
                        "has_pii": true/false,
                        "pii_types": ["email", "phone", "ssn"]
                    }},
                    "language_quality": {{
                        "score": 0-100,
                        "passed": true/false,
                        "issues": []
                    }}

            }}

            Completeness: Check if the document has sufficient content, proper structure, and all necessary sections.
            Consistency: Verify title matches content, no contradictions, coherent narrative.
            PII Detection: Identify any personally identifiable information (emails, phone numbers, SSN, addresses).
            Language Quality: Assess grammar, spelling, clarity, and professionalism.
            Return ONLY valid JSON, no additional text.
        
        """

        return prompt
    def _parse_llm_response(self,response_text:str,document_id:str)->QualityCheckResult:
        """Parse LLM JSON response into QualityCheckResult."""
        try:
            data=json.loads(response_text)
            
            # Parse completeness check
            completeness_data = data.get("completeness", {})
            completeness_check = CheckResult(
                passed=completeness_data.get("passed", False),
                score=float(completeness_data.get("score", 0)),
                issues=[
                    ValidationIssue(
                        issue_type="completeness",
                        severity="medium",
                        description=issue,
                        field="content"
                    )
                    for issue in completeness_data.get("issues", [])
                ]
            )
            
            # Parse consistency check
            consistency_data = data.get("consistency", {})
            consistency_check = CheckResult(
                passed=consistency_data.get("passed", False),
                score=float(consistency_data.get("score", 0)),
                issues=[
                    ValidationIssue(
                        issue_type="consistency",
                        severity="medium",
                        description=issue,
                        field="title"
                    )
                    for issue in consistency_data.get("issues", [])
                ]
            )

            # Parse PII detection
            pii_data = data.get("pii_detection", {})
            pii_check = CheckResult(
                passed=not pii_data.get("has_pii", False),
                score=float(pii_data.get("score", 100)),
                issues=[
                    ValidationIssue(
                        issue_type="pii",
                        severity="high",
                        description=f"Detected {pii_type}",
                        field="content"
                    )
                    for pii_type in pii_data.get("pii_types", [])
                ]
            )

            # Parse language quality
            language_data = data.get("language_quality", {})
            language_check = CheckResult(
                passed=language_data.get("passed", False),
                score=float(language_data.get("score", 0)),
                issues=[
                    ValidationIssue(
                        issue_type="language",
                        severity="low",
                        description=issue,
                        field="content"
                    )
                    for issue in language_data.get("issues", [])
                ]
            )


            # Calculate overall score
            overall_score = (
                completeness_check.score * 0.3 +
                consistency_check.score * 0.3 +
                pii_check.score * 0.2 +
                language_check.score * 0.2
            )

            return QualityCheckResult(
                document_id=document_id,
                overall_score=overall_score,
                is_valid=overall_score >= settings.min_quality_score,
                completeness_check=completeness_check,
                consistency_check=consistency_check,
                pii_check=pii_check,
                language_check=language_check,
                llm_provider="openai",
                llm_model=self.model
            )

        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return self._create_error_result(document_id, f"Parse error: {e}")

    def _create_error_result(self,document_id:str,error_msg:str) -> QualityCheckResult:
        """Create a result indicating validation error."""

        error_check = CheckResult(
            passed=False,
            score=0,
            issues=[ValidationIssue(
                issue_type="system",
                severity="high",
                description=f"Validation error: {error_msg}",
                field=None
            )]
        )

        return QualityCheckResult(
            document_id=document_id,
            overall_score=0,
            is_valid=False,
            completeness_check=error_check,
            consistency_check=error_check,
            pii_check=error_check,
            language_check=error_check,
            llm_provider="openai",
            llm_model=self.model
        )



            
    