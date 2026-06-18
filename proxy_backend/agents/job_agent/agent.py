"""
Core logic for job_agent.
Prepares structure for LangGraph nodes.
"""

class JobAgent:
    """Agent definition."""
    
    def __init__(self, llm_provider) -> None:
        """
        Initialize with an injected LLM provider.
        """
        self.llm_provider = llm_provider
