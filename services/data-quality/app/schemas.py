from datetime import datetime
from pydantic import BaseModel,Field


class ValidationIssue(BaseModel):
    """Represents a specific quality issue found in a document."""
    
    issue_type: str  # "completeness", "consistency", "pii", "language"
    severity: str  # "low", "medium", "high"
    description: str
    field: str | None = None  # Which field has the issue
    

class CheckResult(BaseModel):
    """Result of a specific quality check."""
    
    passed: bool
    score: float  # 0-100
    issues: list[ValidationIssue] = []
    details: str | None = None


class QualityCheckResult(BaseModel):
    """Complete quality validation result for a document."""
    
    document_id: str
    overall_score: float = Field(..., ge=0, le=100)
    is_valid: bool
    
    # Individual check results
    completeness_check: CheckResult
    consistency_check: CheckResult
    pii_check: CheckResult
    language_check: CheckResult


    # Metadata
    checked_at: datetime = Field(default_factory=datetime.utcnow)
    llm_provider: str
    llm_model: str

    @property
    def all_issues(self) -> list[ValidationIssue]:
        """Get all issues from all checks."""
        issues = []
        issues.extend(self.completeness_check.issues)
        issues.extend(self.consistency_check.issues)
        issues.extend(self.pii_check.issues)
        issues.extend(self.language_check.issues)
        return issues
    
    @property
    def has_pii(self) -> bool:
        """Check if PII was detected."""
        return not self.pii_check.passed
    