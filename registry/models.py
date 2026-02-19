from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AgentCard(BaseModel):
    name: str
    url: str
    version: str = "1.0.0"
    description: str = ""
    capabilities: List[str]
    mcp_tools: List[str] = Field(default_factory=list)
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)
    query_endpoint: str = "/query"
    health_endpoint: str = "/health"
    collaborates_with: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentRegistration(BaseModel):
    name: str
    url: str
    capabilities: List[str]
    mcp_tools: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    agent_card: Optional[AgentCard] = None


class AgentDeregistration(BaseModel):
    name: str


class AgentInfo(BaseModel):
    name: str
    url: str
    capabilities: List[str]
    mcp_tools: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    status: str = "alive"
    agent_card: Optional[AgentCard] = None


class DiscoverResponse(BaseModel):
    agents: List[AgentInfo]


class CardDiscoverResponse(BaseModel):
    cards: List[AgentCard]
