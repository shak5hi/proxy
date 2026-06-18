"""
Core logic for research_agent.
Prepares structure for LangGraph nodes.
"""

class ResearchAgent:
    """Agent definition."""
    
    def __init__(self, llm_provider) -> None:
        """
        Initialize with an injected LLM provider.
        """
        self.llm_provider = llm_provider
