"""
Core logic for strategy_agent.
Prepares structure for LangGraph nodes.
"""

class StrategyAgent:
    """Agent definition."""
    
    def __init__(self, llm_provider) -> None:
        """
        Initialize with an injected LLM provider.
        """
        self.llm_provider = llm_provider
