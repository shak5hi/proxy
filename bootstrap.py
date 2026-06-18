import os
from pathlib import Path

BASE_DIR = Path("C:/Users/shaks/OneDrive/Desktop/Projects/proxy/proxy")
BACKEND_DIR = BASE_DIR / "proxy_backend"
FRONTEND_DIR = BASE_DIR / "proxy_frontend"

directories = [
    FRONTEND_DIR,
    BACKEND_DIR,
    BACKEND_DIR / "core",
    BACKEND_DIR / "api",
    BACKEND_DIR / "domains",
    BACKEND_DIR / "agents",
    BACKEND_DIR / "providers",
    BACKEND_DIR / "events",
    BACKEND_DIR / "events" / "contracts",
    BACKEND_DIR / "workers",
    BACKEND_DIR / "memory",
    BACKEND_DIR / "prompts",
    BACKEND_DIR / "db",
    BACKEND_DIR / "middlewares",
    BACKEND_DIR / "exceptions",
    BACKEND_DIR / "shared",
    BACKEND_DIR / "utils",
    BACKEND_DIR / "tests",
    BACKEND_DIR / "tests" / "unit",
    BACKEND_DIR / "tests" / "integration",
    BACKEND_DIR / "tests" / "fixtures",
    BACKEND_DIR / "tests" / "mocks",
    BACKEND_DIR / "scripts",
    BACKEND_DIR / "migrations",
    BACKEND_DIR / "docs",
]

domains = [
    "user", "profile", "jobs", "companies", 
    "emails", "analytics", "gmail", "strategy"
]

domain_files = [
    "__init__.py", "models.py", "schemas.py", "repositories.py", 
    "services.py", "validators.py", "exceptions.py"
]

for domain in domains:
    d_path = BACKEND_DIR / "domains" / domain
    directories.append(d_path)

agents = [
    "profile_agent", "job_agent", "research_agent", 
    "email_agent", "inbox_agent", "strategy_agent"
]

agent_files = [
    "__init__.py", "agent.py", "schemas.py", 
    "prompts.py", "tools.py", "memory.py"
]

for agent in agents:
    a_path = BACKEND_DIR / "agents" / agent
    directories.append(a_path)

providers = [
    "llm", "embeddings", "vectorstore", "storage", "email"
]

for provider in providers:
    directories.append(BACKEND_DIR / "providers" / provider)

# Create all directories
for d in directories:
    d.mkdir(parents=True, exist_ok=True)

# Helper to write file safely
def write_file(path: Path, content: str):
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# 1. Base Domain Files
for domain in domains:
    d_path = BACKEND_DIR / "domains" / domain
    for df in domain_files:
        if df == "schemas.py":
            content = f'''"""
Pydantic V2 schemas for the {domain} domain.
"""
from pydantic import BaseModel, ConfigDict

class {domain.capitalize()}Base(BaseModel):
    """Base schema for {domain}."""
    model_config = ConfigDict(from_attributes=True)
'''
            write_file(d_path / df, content)
        elif df == "services.py":
            content = f'''"""
Service layer for the {domain} domain.
Contains pure business logic.
"""

class {domain.capitalize()}Service:
    """Orchestrates business use cases for {domain}."""
    
    def __init__(self, repository) -> None:
        """
        Initialize {domain} service with repository injection.
        
        Args:
            repository: The {domain} repository.
        """
        self.repository = repository
'''
            write_file(d_path / df, content)
        elif df == "__init__.py":
            write_file(d_path / df, "")
        else:
            write_file(d_path / df, f'"""\nPlaceholder for {domain} {df.split(".")[0]}.\n"""\n')

# 2. Base Agent Files
for agent in agents:
    a_path = BACKEND_DIR / "agents" / agent
    for af in agent_files:
        if af == "agent.py":
            content = f'''"""
Core logic for {agent}.
Prepares structure for LangGraph nodes.
"""

class {agent.replace("_agent", "").capitalize()}Agent:
    """Agent definition."""
    
    def __init__(self, llm_provider) -> None:
        """
        Initialize with an injected LLM provider.
        """
        self.llm_provider = llm_provider
'''
            write_file(a_path / af, content)
        elif af == "__init__.py":
            write_file(a_path / af, "")
        else:
            write_file(a_path / af, f'"""\nPlaceholder for {agent} {af.split(".")[0]}.\n"""\n')

# 3. Core Dependencies
dep_content = '''"""
Centralized FastAPI dependencies.
No external DI containers; native FastAPI Depends() only.
"""
from typing import Generator
from fastapi import Request

# TODO: Add specific provider return types

def get_settings():
    """Dependency to retrieve application settings."""
    pass

def get_logger():
    """Dependency to retrieve the structured logger."""
    pass

def get_llm_provider():
    """Dependency to inject the LLM Provider."""
    pass

def get_embedding_provider():
    """Dependency to inject the Embedding Provider."""
    pass

def get_vector_store():
    """Dependency to inject the Vector Store Provider."""
    pass

def get_email_provider():
    """Dependency to inject the Email Provider."""
    pass
'''
write_file(BACKEND_DIR / "core" / "dependencies.py", dep_content)

# 4. Providers
llm_interface = '''"""
LLM Provider Abstractions.
"""
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    """Abstract Base Class for LLM providers."""
    
    @abstractmethod
    async def generate_text(self, prompt: str) -> str:
        """Generate text from a prompt."""
        pass
'''
write_file(BACKEND_DIR / "providers" / "llm" / "interfaces.py", llm_interface)

gemini_provider = '''"""
Concrete implementation for Gemini LLM.
"""
from .interfaces import LLMProvider

class GeminiProvider(LLMProvider):
    """Gemini Provider implementation."""
    
    async def generate_text(self, prompt: str) -> str:
        """Generate text using Google's Gemini."""
        return "Generated text from Gemini."
'''
write_file(BACKEND_DIR / "providers" / "llm" / "gemini_provider.py", gemini_provider)

embedding_interface = '''"""
Embedding Provider Abstractions.
"""
from abc import ABC, abstractmethod
from typing import List

class EmbeddingProvider(ABC):
    """Abstract Base Class for Embedding providers."""
    
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Convert text into vector embeddings."""
        pass
'''
write_file(BACKEND_DIR / "providers" / "embeddings" / "interfaces.py", embedding_interface)

sentence_transformer = '''"""
Concrete implementation for Sentence Transformers.
"""
from typing import List
from .interfaces import EmbeddingProvider

class SentenceTransformerProvider(EmbeddingProvider):
    """Sentence Transformer Provider implementation."""
    
    async def embed_text(self, text: str) -> List[float]:
        """Embed text using sentence-transformers."""
        return [0.0] * 768
'''
write_file(BACKEND_DIR / "providers" / "embeddings" / "sentence_transformer_provider.py", sentence_transformer)

vectorstore_interface = '''"""
Vector Store Provider Abstractions.
"""
from abc import ABC, abstractmethod
from typing import List, Any

class VectorStoreProvider(ABC):
    """Abstract Base Class for Vector Store providers."""
    
    @abstractmethod
    async def search(self, embedding: List[float], limit: int = 5) -> List[Any]:
        """Search vector database."""
        pass
'''
write_file(BACKEND_DIR / "providers" / "vectorstore" / "interfaces.py", vectorstore_interface)

supabase_vector = '''"""
Concrete implementation for Supabase pgvector.
"""
from typing import List, Any
from .interfaces import VectorStoreProvider

class SupabaseVectorProvider(VectorStoreProvider):
    """Supabase Vector Store Provider implementation."""
    
    async def search(self, embedding: List[float], limit: int = 5) -> List[Any]:
        """Search pgvector in Supabase."""
        return []
'''
write_file(BACKEND_DIR / "providers" / "vectorstore" / "supabase_vector_provider.py", supabase_vector)

storage_interface = '''"""
Storage Provider Abstractions.
"""
from abc import ABC, abstractmethod

class StorageProvider(ABC):
    """Abstract Base Class for Storage providers."""
    
    @abstractmethod
    async def upload_file(self, file_path: str, destination: str) -> str:
        """Upload file to storage."""
        pass
'''
write_file(BACKEND_DIR / "providers" / "storage" / "interfaces.py", storage_interface)

email_interface = '''"""
Email Provider Abstractions.
"""
from abc import ABC, abstractmethod

class EmailProvider(ABC):
    """Abstract Base Class for Email providers."""
    
    @abstractmethod
    async def send_email(self, to_address: str, subject: str, body: str) -> bool:
        """Send an email."""
        pass
'''
write_file(BACKEND_DIR / "providers" / "email" / "interfaces.py", email_interface)

# 5. Events
event_bus = '''"""
Event Bus Abstraction.
Prepares for future Redis pub/sub migration.
"""
from abc import ABC, abstractmethod
from typing import Any

class EventBus(ABC):
    """Abstract Base Class for Event Bus."""
    
    @abstractmethod
    async def publish(self, topic: str, event: Any) -> None:
        """Publish an event to a topic."""
        pass
        
    @abstractmethod
    async def subscribe(self, topic: str, handler: Any) -> None:
        """Subscribe to a topic with a handler."""
        pass
'''
write_file(BACKEND_DIR / "events" / "event_bus.py", event_bus)

base_event = '''"""
Base Event definitions.
"""
from pydantic import BaseModel
from datetime import datetime

class BaseEvent(BaseModel):
    """Base schema for all events in the system."""
    event_id: str
    timestamp: datetime
'''
write_file(BACKEND_DIR / "events" / "base_event.py", base_event)

event_contracts = [
    "resume_uploaded.py", "profile_created.py", "jobs_discovered.py",
    "company_researched.py", "emails_generated.py", "reply_received.py",
    "weekly_analysis_generated.py"
]

for contract in event_contracts:
    write_file(BACKEND_DIR / "events" / "contracts" / contract, f'"""\nContract schema for {contract.split(".")[0]}.\n"""\n')

# 6. Memory
memories = [
    "conversation_memory.py", "vector_memory.py", 
    "email_history_memory.py", "success_pattern_memory.py"
]

for memory in memories:
    write_file(BACKEND_DIR / "memory" / memory, f'"""\nImplementation of {memory.split(".")[0]}.\n"""\n')

# 7. Core observability
write_file(BACKEND_DIR / "core" / "logging.py", '"""\nStructured logging configuration.\n"""\n')
write_file(BACKEND_DIR / "middlewares" / "request_logging.py", '"""\nMiddleware for logging requests and correlation IDs.\n"""\n')
write_file(BACKEND_DIR / "middlewares" / "error_handler.py", '"""\nMiddleware for global error handling.\n"""\n')

print("Bootstrap completed successfully. Created 70+ structural files and directories.")
