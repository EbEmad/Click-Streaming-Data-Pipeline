from abc import ABC, abstractmethod
from ..schemas import QualityCheckResult
class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def validate_document(self,title:str,content:str,document_id :str) -> QualityCheckResult:
        """Validate a document using the LLM."""

        pass