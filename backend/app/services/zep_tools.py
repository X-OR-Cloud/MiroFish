"""
ZeptextToolService
EncapsulationGraphSearch、NodeRead、EdgeQuerytextTool，textReport Agenttext

textTool（Optimizetext）：
1. InsightForge（text）- text，textGeneratetextIssuetext
2. PanoramaSearch（textSearch）- Gettext，textExpireContent
3. QuickSearch（textSearch）- text
"""

import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from zep_cloud.client import Zep

from ..config import Config
from ..utils.logger import get_logger
from ..utils.llm_client import LLMClient
from ..utils.zep_paging import fetch_all_nodes, fetch_all_edges

logger = get_logger('mirofish.zep_tools')


@dataclass
class SearchResult:
    """SearchResult"""
    facts: List[str]
    edges: List[Dict[str, Any]]
    nodes: List[Dict[str, Any]]
    query: str
    total_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "facts": self.facts,
            "edges": self.edges,
            "nodes": self.nodes,
            "query": self.query,
            "total_count": self.total_count
        }
    
    def to_text(self) -> str:
        """ConverttextFormat，textLLMtext"""
        text_parts = [f"SearchQuery: {self.query}", f"text {self.total_count} textInformation"]
        
        if self.facts:
            text_parts.append("\n### text:")
            for i, fact in enumerate(self.facts, 1):
                text_parts.append(f"{i}. {fact}")
        
        return "\n".join(text_parts)


@dataclass
class NodeInfo:
    """NodeInformation"""
    uuid: str
    name: str
    labels: List[str]
    summary: str
    attributes: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "uuid": self.uuid,
            "name": self.name,
            "labels": self.labels,
            "summary": self.summary,
            "attributes": self.attributes
        }
    
    def to_text(self) -> str:
        """ConverttextFormat"""
        entity_type = next((l for l in self.labels if l not in ["Entity", "Node"]), "textType")
        return f"Entity: {self.name} (Type: {entity_type})\nDigest: {self.summary}"


@dataclass
class EdgeInfo:
    """EdgeInformation"""
    uuid: str
    name: str
    fact: str
    source_node_uuid: str
    target_node_uuid: str
    source_node_name: Optional[str] = None
    target_node_name: Optional[str] = None
    # textInformation
    created_at: Optional[str] = None
    valid_at: Optional[str] = None
    invalid_at: Optional[str] = None
    expired_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "uuid": self.uuid,
            "name": self.name,
            "fact": self.fact,
            "source_node_uuid": self.source_node_uuid,
            "target_node_uuid": self.target_node_uuid,
            "source_node_name": self.source_node_name,
            "target_node_name": self.target_node_name,
            "created_at": self.created_at,
            "valid_at": self.valid_at,
            "invalid_at": self.invalid_at,
            "expired_at": self.expired_at
        }
    
    def to_text(self, include_temporal: bool = False) -> str:
        """ConverttextFormat"""
        source = self.source_node_name or self.source_node_uuid[:8]
        target = self.target_node_name or self.target_node_uuid[:8]
        base_text = f"Relationship: {source} --[{self.name}]--> {target}\ntext: {self.fact}"
        
        if include_temporal:
            valid_at = self.valid_at or "text"
            invalid_at = self.invalid_at or "text"
            base_text += f"\ntext: {valid_at} - {invalid_at}"
            if self.expired_at:
                base_text += f" (textExpire: {self.expired_at})"
        
        return base_text
    
    @property
    def is_expired(self) -> bool:
        """textExpire"""
        return self.expired_at is not None
    
    @property
    def is_invalid(self) -> bool:
        """textInvalid"""
        return self.invalid_at is not None


@dataclass
class InsightForgeResult:
    """
    textResult (InsightForge)
    textIssuetextResult，textAnalyze
    """
    query: str
    simulation_requirement: str
    sub_queries: List[str]
    
    # textResult
    semantic_facts: List[str] = field(default_factory=list)  # textSearchResult
    entity_insights: List[Dict[str, Any]] = field(default_factory=list)  # Entitytext
    relationship_chains: List[str] = field(default_factory=list)  # Relationshiptext
    
    # StatisticsInformation
    total_facts: int = 0
    total_entities: int = 0
    total_relationships: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "simulation_requirement": self.simulation_requirement,
            "sub_queries": self.sub_queries,
            "semantic_facts": self.semantic_facts,
            "entity_insights": self.entity_insights,
            "relationship_chains": self.relationship_chains,
            "total_facts": self.total_facts,
            "total_entities": self.total_entities,
            "total_relationships": self.total_relationships
        }
    
    def to_text(self) -> str:
        """ConverttextFormat，textLLMtext"""
        text_parts = [
            f"## textAnalyze",
            f"AnalyzeIssue: {self.query}",
            f"text: {self.simulation_requirement}",
            f"\n### textDataStatistics",
            f"- text: {self.total_facts}text",
            f"- textEntity: {self.total_entities}text",
            f"- Relationshiptext: {self.total_relationships}text"
        ]
        
        # textIssue
        if self.sub_queries:
            text_parts.append(f"\n### AnalyzetextIssue")
            for i, sq in enumerate(self.sub_queries, 1):
                text_parts.append(f"{i}. {sq}")
        
        # textSearchResult
        if self.semantic_facts:
            text_parts.append(f"\n### 【text】(textReporttext)")
            for i, fact in enumerate(self.semantic_facts, 1):
                text_parts.append(f"{i}. \"{fact}\"")
        
        # Entitytext
        if self.entity_insights:
            text_parts.append(f"\n### 【textEntity】")
            for entity in self.entity_insights:
                text_parts.append(f"- **{entity.get('name', 'text')}** ({entity.get('type', 'Entity')})")
                if entity.get('summary'):
                    text_parts.append(f"  Digest: \"{entity.get('summary')}\"")
                if entity.get('related_facts'):
                    text_parts.append(f"  text: {len(entity.get('related_facts', []))}text")
        
        # Relationshiptext
        if self.relationship_chains:
            text_parts.append(f"\n### 【Relationshiptext】")
            for chain in self.relationship_chains:
                text_parts.append(f"- {chain}")
        
        return "\n".join(text_parts)


@dataclass
class PanoramaResult:
    """
    textSearchResult (Panorama)
    textInformation，textExpireContent
    """
    query: str
    
    # textNode
    all_nodes: List[NodeInfo] = field(default_factory=list)
    # textEdge（textExpiretext）
    all_edges: List[EdgeInfo] = field(default_factory=list)
    # textValidtext
    active_facts: List[str] = field(default_factory=list)
    # textExpire/Invalidtext（textRecord）
    historical_facts: List[str] = field(default_factory=list)
    
    # Statistics
    total_nodes: int = 0
    total_edges: int = 0
    active_count: int = 0
    historical_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "all_nodes": [n.to_dict() for n in self.all_nodes],
            "all_edges": [e.to_dict() for e in self.all_edges],
            "active_facts": self.active_facts,
            "historical_facts": self.historical_facts,
            "total_nodes": self.total_nodes,
            "total_edges": self.total_edges,
            "active_count": self.active_count,
            "historical_count": self.historical_count
        }
    
    def to_text(self) -> str:
        """ConverttextFormat（textVersion，text）"""
        text_parts = [
            f"## textSearchResult（textGraph）",
            f"Query: {self.query}",
            f"\n### StatisticsInformation",
            f"- textNodetext: {self.total_nodes}",
            f"- textEdgetext: {self.total_edges}",
            f"- textValidtext: {self.active_count}text",
            f"- text/Expiretext: {self.historical_count}text"
        ]
        
        # textValidtext（text，text）
        if self.active_facts:
            text_parts.append(f"\n### 【textValidtext】(SimulationResulttext)")
            for i, fact in enumerate(self.active_facts, 1):
                text_parts.append(f"{i}. \"{fact}\"")
        
        # text/Expiretext（text，text）
        if self.historical_facts:
            text_parts.append(f"\n### 【text/Expiretext】(textRecord)")
            for i, fact in enumerate(self.historical_facts, 1):
                text_parts.append(f"{i}. \"{fact}\"")
        
        # textEntity（text，text）
        if self.all_nodes:
            text_parts.append(f"\n### 【textEntity】")
            for node in self.all_nodes:
                entity_type = next((l for l in node.labels if l not in ["Entity", "Node"]), "Entity")
                text_parts.append(f"- **{node.name}** ({entity_type})")
        
        return "\n".join(text_parts)


@dataclass
class AgentInterview:
    """textAgenttextResult"""
    agent_name: str
    agent_role: str  # RoleType（text：text、text、text）
    agent_bio: str  # text
    question: str  # textAccesstext
    response: str  # text
    key_quotes: List[str] = field(default_factory=list)  # text
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "agent_role": self.agent_role,
            "agent_bio": self.agent_bio,
            "question": self.question,
            "response": self.response,
            "key_quotes": self.key_quotes
        }
    
    def to_text(self) -> str:
        text = f"**{self.agent_name}** ({self.agent_role})\n"
        # Showtextagent_bio，text
        text += f"_text: {self.agent_bio}_\n\n"
        text += f"**Q:** {self.question}\n\n"
        text += f"**A:** {self.response}\n"
        if self.key_quotes:
            text += "\n**text:**\n"
            for quote in self.key_quotes:
                # Cleantext
                clean_quote = quote.replace('\u201c', '').replace('\u201d', '').replace('"', '')
                clean_quote = clean_quote.replace('\u300c', '').replace('\u300d', '')
                clean_quote = clean_quote.strip()
                # text
                while clean_quote and clean_quote[0] in '，,；;：:、。！？\n\r\t ':
                    clean_quote = clean_quote[1:]
                # FiltertextIssuetextContent（Issue1-9）
                skip = False
                for d in '123456789':
                    if f'\u95ee\u9898{d}' in clean_quote:
                        skip = True
                        break
                if skip:
                    continue
                # textContent（text，text）
                if len(clean_quote) > 150:
                    dot_pos = clean_quote.find('\u3002', 80)
                    if dot_pos > 0:
                        clean_quote = clean_quote[:dot_pos + 1]
                    else:
                        clean_quote = clean_quote[:147] + "..."
                if clean_quote and len(clean_quote) >= 10:
                    text += f'> "{clean_quote}"\n'
        return text


@dataclass
class InterviewResult:
    """
    textResult (Interview)
    textSimulationAgenttext
    """
    interview_topic: str  # text
    interview_questions: List[str]  # textAccesstextList
    
    # textSelecttextAgent
    selected_agents: List[Dict[str, Any]] = field(default_factory=list)
    # textAgenttext
    interviews: List[AgentInterview] = field(default_factory=list)
    
    # SelectAgenttext
    selection_reasoning: str = ""
    # textDigest
    summary: str = ""
    
    # Statistics
    total_agents: int = 0
    interviewed_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "interview_topic": self.interview_topic,
            "interview_questions": self.interview_questions,
            "selected_agents": self.selected_agents,
            "interviews": [i.to_dict() for i in self.interviews],
            "selection_reasoning": self.selection_reasoning,
            "summary": self.summary,
            "total_agents": self.total_agents,
            "interviewed_count": self.interviewed_count
        }
    
    def to_text(self) -> str:
        """ConverttextFormat，textLLMtextReporttext"""
        text_parts = [
            "## textReport",
            f"**text:** {self.interview_topic}",
            f"**text:** {self.interviewed_count} / {self.total_agents} textSimulationAgent",
            "\n### textObjectSelecttext",
            self.selection_reasoning or "（textSelect）",
            "\n---",
            "\n### text",
        ]

        if self.interviews:
            for i, interview in enumerate(self.interviews, 1):
                text_parts.append(f"\n#### text #{i}: {interview.agent_name}")
                text_parts.append(interview.to_text())
                text_parts.append("\n---")
        else:
            text_parts.append("（textRecord）\n\n---")

        text_parts.append("\n### textDigesttext")
        text_parts.append(self.summary or "（textDigest）")

        return "\n".join(text_parts)


class ZepToolsService:
    """
    ZeptextToolService
    
    【textTool - Optimizetext】
    1. insight_forge - text（text，textGeneratetextIssue，text）
    2. panorama_search - textSearch（Gettext，textExpireContent）
    3. quick_search - textSearch（text）
    4. interview_agents - text（textSimulationAgent，Gettext）
    
    【textTool】
    - search_graph - GraphtextSearch
    - get_all_nodes - GetGraphtextNode
    - get_all_edges - GetGraphtextEdge（textInformation）
    - get_node_detail - GetNodetextInformation
    - get_node_edges - GetNodetextEdge
    - get_entities_by_type - textTypeGetEntity
    - get_entity_summary - GetEntitytextRelationshipDigest
    """
    
    # RetryConfiguration
    MAX_RETRIES = 3
    RETRY_DELAY = 2.0
    
    def __init__(self, api_key: Optional[str] = None, llm_client: Optional[LLMClient] = None):
        self.api_key = api_key or Config.ZEP_API_KEY
        if not self.api_key:
            raise ValueError("ZEP_API_KEY textConfiguration")
        
        self.client = Zep(api_key=self.api_key)
        # LLMClienttextInsightForgeGeneratetextIssue
        self._llm_client = llm_client
        logger.info("ZepToolsService InitializeComplete")
    
    @property
    def llm(self) -> LLMClient:
        """textInitializeLLMClient"""
        if self._llm_client is None:
            self._llm_client = LLMClient()
        return self._llm_client
    
    def _call_with_retry(self, func, operation_name: str, max_retries: int = None):
        """textRetrytextAPItext"""
        max_retries = max_retries or self.MAX_RETRIES
        last_exception = None
        delay = self.RETRY_DELAY
        
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Zep {operation_name} text {attempt + 1} textFailed: {str(e)[:100]}, "
                        f"{delay:.1f}textRetry..."
                    )
                    time.sleep(delay)
                    delay *= 2
                else:
                    logger.error(f"Zep {operation_name} text {max_retries} textFailed: {str(e)}")
        
        raise last_exception
    
    def search_graph(
        self, 
        graph_id: str, 
        query: str, 
        limit: int = 10,
        scope: str = "edges"
    ) -> SearchResult:
        """
        GraphtextSearch
        
        textSearch（text+BM25）textGraphtextSearchtextInformation。
        textZep Cloudtextsearch APItext，text。
        
        Args:
            graph_id: GraphID (Standalone Graph)
            query: SearchQuery
            limit: ReturnsResulttext
            scope: Searchtext，"edges" text "nodes"
            
        Returns:
            SearchResult: SearchResult
        """
        logger.info(f"GraphSearch: graph_id={graph_id}, query={query[:50]}...")
        
        # textZep Cloud Search API
        try:
            search_results = self._call_with_retry(
                func=lambda: self.client.graph.search(
                    graph_id=graph_id,
                    query=query,
                    limit=limit,
                    scope=scope,
                    reranker="cross_encoder"
                ),
                operation_name=f"GraphSearch(graph={graph_id})"
            )
            
            facts = []
            edges = []
            nodes = []
            
            # ParseEdgeSearchResult
            if hasattr(search_results, 'edges') and search_results.edges:
                for edge in search_results.edges:
                    if hasattr(edge, 'fact') and edge.fact:
                        facts.append(edge.fact)
                    edges.append({
                        "uuid": getattr(edge, 'uuid_', None) or getattr(edge, 'uuid', ''),
                        "name": getattr(edge, 'name', ''),
                        "fact": getattr(edge, 'fact', ''),
                        "source_node_uuid": getattr(edge, 'source_node_uuid', ''),
                        "target_node_uuid": getattr(edge, 'target_node_uuid', ''),
                    })
            
            # ParseNodeSearchResult
            if hasattr(search_results, 'nodes') and search_results.nodes:
                for node in search_results.nodes:
                    nodes.append({
                        "uuid": getattr(node, 'uuid_', None) or getattr(node, 'uuid', ''),
                        "name": getattr(node, 'name', ''),
                        "labels": getattr(node, 'labels', []),
                        "summary": getattr(node, 'summary', ''),
                    })
                    # NodeDigesttext
                    if hasattr(node, 'summary') and node.summary:
                        facts.append(f"[{node.name}]: {node.summary}")
            
            logger.info(f"SearchComplete: text {len(facts)} text")
            
            return SearchResult(
                facts=facts,
                edges=edges,
                nodes=nodes,
                query=query,
                total_count=len(facts)
            )
            
        except Exception as e:
            logger.warning(f"Zep Search APIFailed，textSearch: {str(e)}")
            # text：textSearch
            return self._local_search(graph_id, query, limit, scope)
    
    def _local_search(
        self, 
        graph_id: str, 
        query: str, 
        limit: int = 10,
        scope: str = "edges"
    ) -> SearchResult:
        """
        textSearch（textZep Search APItext）
        
        GettextEdge/Node，text
        
        Args:
            graph_id: GraphID
            query: SearchQuery
            limit: ReturnsResulttext
            scope: Searchtext
            
        Returns:
            SearchResult: SearchResult
        """
        logger.info(f"textSearch: query={query[:30]}...")
        
        facts = []
        edges_result = []
        nodes_result = []
        
        # textQuerytext（text）
        query_lower = query.lower()
        keywords = [w.strip() for w in query_lower.replace(',', ' ').replace('，', ' ').split() if len(w.strip()) > 1]
        
        def match_score(text: str) -> int:
            """textQuerytext"""
            if not text:
                return 0
            text_lower = text.lower()
            # textQuery
            if query_lower in text_lower:
                return 100
            # text
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 10
            return score
        
        try:
            if scope in ["edges", "both"]:
                # GettextEdgetext
                all_edges = self.get_all_edges(graph_id)
                scored_edges = []
                for edge in all_edges:
                    score = match_score(edge.fact) + match_score(edge.name)
                    if score > 0:
                        scored_edges.append((score, edge))
                
                # textSort
                scored_edges.sort(key=lambda x: x[0], reverse=True)
                
                for score, edge in scored_edges[:limit]:
                    if edge.fact:
                        facts.append(edge.fact)
                    edges_result.append({
                        "uuid": edge.uuid,
                        "name": edge.name,
                        "fact": edge.fact,
                        "source_node_uuid": edge.source_node_uuid,
                        "target_node_uuid": edge.target_node_uuid,
                    })
            
            if scope in ["nodes", "both"]:
                # GettextNodetext
                all_nodes = self.get_all_nodes(graph_id)
                scored_nodes = []
                for node in all_nodes:
                    score = match_score(node.name) + match_score(node.summary)
                    if score > 0:
                        scored_nodes.append((score, node))
                
                scored_nodes.sort(key=lambda x: x[0], reverse=True)
                
                for score, node in scored_nodes[:limit]:
                    nodes_result.append({
                        "uuid": node.uuid,
                        "name": node.name,
                        "labels": node.labels,
                        "summary": node.summary,
                    })
                    if node.summary:
                        facts.append(f"[{node.name}]: {node.summary}")
            
            logger.info(f"textSearchComplete: text {len(facts)} text")
            
        except Exception as e:
            logger.error(f"textSearchFailed: {str(e)}")
        
        return SearchResult(
            facts=facts,
            edges=edges_result,
            nodes=nodes_result,
            query=query,
            total_count=len(facts)
        )
    
    def get_all_nodes(self, graph_id: str) -> List[NodeInfo]:
        """
        GetGraphtextNode（textGet）

        Args:
            graph_id: GraphID

        Returns:
            NodeList
        """
        logger.info(f"GetGraph {graph_id} textNode...")

        nodes = fetch_all_nodes(self.client, graph_id)

        result = []
        for node in nodes:
            node_uuid = getattr(node, 'uuid_', None) or getattr(node, 'uuid', None) or ""
            result.append(NodeInfo(
                uuid=str(node_uuid) if node_uuid else "",
                name=node.name or "",
                labels=node.labels or [],
                summary=node.summary or "",
                attributes=node.attributes or {}
            ))

        logger.info(f"Gettext {len(result)} textNode")
        return result

    def get_all_edges(self, graph_id: str, include_temporal: bool = True) -> List[EdgeInfo]:
        """
        GetGraphtextEdge（textGet，textInformation）

        Args:
            graph_id: GraphID
            include_temporal: textInformation（textTrue）

        Returns:
            EdgeList（textcreated_at, valid_at, invalid_at, expired_at）
        """
        logger.info(f"GetGraph {graph_id} textEdge...")

        edges = fetch_all_edges(self.client, graph_id)

        result = []
        for edge in edges:
            edge_uuid = getattr(edge, 'uuid_', None) or getattr(edge, 'uuid', None) or ""
            edge_info = EdgeInfo(
                uuid=str(edge_uuid) if edge_uuid else "",
                name=edge.name or "",
                fact=edge.fact or "",
                source_node_uuid=edge.source_node_uuid or "",
                target_node_uuid=edge.target_node_uuid or ""
            )

            # AddtextInformation
            if include_temporal:
                edge_info.created_at = getattr(edge, 'created_at', None)
                edge_info.valid_at = getattr(edge, 'valid_at', None)
                edge_info.invalid_at = getattr(edge, 'invalid_at', None)
                edge_info.expired_at = getattr(edge, 'expired_at', None)

            result.append(edge_info)

        logger.info(f"Gettext {len(result)} textEdge")
        return result
    
    def get_node_detail(self, node_uuid: str) -> Optional[NodeInfo]:
        """
        GettextNodetextInformation
        
        Args:
            node_uuid: NodeUUID
            
        Returns:
            NodeInformationtextNone
        """
        logger.info(f"GetNodetext: {node_uuid[:8]}...")
        
        try:
            node = self._call_with_retry(
                func=lambda: self.client.graph.node.get(uuid_=node_uuid),
                operation_name=f"GetNodetext(uuid={node_uuid[:8]}...)"
            )
            
            if not node:
                return None
            
            return NodeInfo(
                uuid=getattr(node, 'uuid_', None) or getattr(node, 'uuid', ''),
                name=node.name or "",
                labels=node.labels or [],
                summary=node.summary or "",
                attributes=node.attributes or {}
            )
        except Exception as e:
            logger.error(f"GetNodetextFailed: {str(e)}")
            return None
    
    def get_node_edges(self, graph_id: str, node_uuid: str) -> List[EdgeInfo]:
        """
        GetNodetextEdge
        
        textGetGraphtextEdge，textFiltertextNodetextEdge
        
        Args:
            graph_id: GraphID
            node_uuid: NodeUUID
            
        Returns:
            EdgeList
        """
        logger.info(f"GetNode {node_uuid[:8]}... textEdge")
        
        try:
            # GetGraphtextEdge，textFilter
            all_edges = self.get_all_edges(graph_id)
            
            result = []
            for edge in all_edges:
                # CheckEdgetextNodetext（text）
                if edge.source_node_uuid == node_uuid or edge.target_node_uuid == node_uuid:
                    result.append(edge)
            
            logger.info(f"text {len(result)} textNodetextEdge")
            return result
            
        except Exception as e:
            logger.warning(f"GetNodeEdgeFailed: {str(e)}")
            return []
    
    def get_entities_by_type(
        self, 
        graph_id: str, 
        entity_type: str
    ) -> List[NodeInfo]:
        """
        textTypeGetEntity
        
        Args:
            graph_id: GraphID
            entity_type: EntityType（text Student, PublicFigure text）
            
        Returns:
            textTypetextEntityList
        """
        logger.info(f"GetTypetext {entity_type} textEntity...")
        
        all_nodes = self.get_all_nodes(graph_id)
        
        filtered = []
        for node in all_nodes:
            # ChecklabelstextType
            if entity_type in node.labels:
                filtered.append(node)
        
        logger.info(f"text {len(filtered)} text {entity_type} TypetextEntity")
        return filtered
    
    def get_entity_summary(
        self, 
        graph_id: str, 
        entity_name: str
    ) -> Dict[str, Any]:
        """
        GettextEntitytextRelationshipDigest
        
        SearchtextEntitytextInformation，textGenerateDigest
        
        Args:
            graph_id: GraphID
            entity_name: EntityName
            
        Returns:
            EntityDigestInformation
        """
        logger.info(f"GetEntity {entity_name} textRelationshipDigest...")
        
        # textSearchtextEntitytextInformation
        search_result = self.search_graph(
            graph_id=graph_id,
            query=entity_name,
            limit=20
        )
        
        # textNodetextEntity
        all_nodes = self.get_all_nodes(graph_id)
        entity_node = None
        for node in all_nodes:
            if node.name.lower() == entity_name.lower():
                entity_node = node
                break
        
        related_edges = []
        if entity_node:
            # textgraph_idParameters
            related_edges = self.get_node_edges(graph_id, entity_node.uuid)
        
        return {
            "entity_name": entity_name,
            "entity_info": entity_node.to_dict() if entity_node else None,
            "related_facts": search_result.facts,
            "related_edges": [e.to_dict() for e in related_edges],
            "total_relations": len(related_edges)
        }
    
    def get_graph_statistics(self, graph_id: str) -> Dict[str, Any]:
        """
        GetGraphtextStatisticsInformation
        
        Args:
            graph_id: GraphID
            
        Returns:
            StatisticsInformation
        """
        logger.info(f"GetGraph {graph_id} textStatisticsInformation...")
        
        nodes = self.get_all_nodes(graph_id)
        edges = self.get_all_edges(graph_id)
        
        # StatisticsEntityTypetext
        entity_types = {}
        for node in nodes:
            for label in node.labels:
                if label not in ["Entity", "Node"]:
                    entity_types[label] = entity_types.get(label, 0) + 1
        
        # StatisticsRelationshipTypetext
        relation_types = {}
        for edge in edges:
            relation_types[edge.name] = relation_types.get(edge.name, 0) + 1
        
        return {
            "graph_id": graph_id,
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "entity_types": entity_types,
            "relation_types": relation_types
        }
    
    def get_simulation_context(
        self, 
        graph_id: str,
        simulation_requirement: str,
        limit: int = 30
    ) -> Dict[str, Any]:
        """
        GetSimulationtextInformation
        
        textSearchtextSimulationtextInformation
        
        Args:
            graph_id: GraphID
            simulation_requirement: Simulationtext
            limit: textClassInformationtext
            
        Returns:
            SimulationtextInformation
        """
        logger.info(f"GetSimulationtext: {simulation_requirement[:50]}...")
        
        # SearchtextSimulationtextInformation
        search_result = self.search_graph(
            graph_id=graph_id,
            query=simulation_requirement,
            limit=limit
        )
        
        # GetGraphStatistics
        stats = self.get_graph_statistics(graph_id)
        
        # GettextEntityNode
        all_nodes = self.get_all_nodes(graph_id)
        
        # textTypetextEntity（textEntityNode）
        entities = []
        for node in all_nodes:
            custom_labels = [l for l in node.labels if l not in ["Entity", "Node"]]
            if custom_labels:
                entities.append({
                    "name": node.name,
                    "type": custom_labels[0],
                    "summary": node.summary
                })
        
        return {
            "simulation_requirement": simulation_requirement,
            "related_facts": search_result.facts,
            "graph_statistics": stats,
            "entities": entities[:limit],  # text
            "total_entities": len(entities)
        }
    
    # ========== textTool（Optimizetext） ==========
    
    def insight_forge(
        self,
        graph_id: str,
        query: str,
        simulation_requirement: str,
        report_context: str = "",
        max_sub_queries: int = 5
    ) -> InsightForgeResult:
        """
        【InsightForge - text】
        
        textFunction，textIssuetext：
        1. textLLMtextIssuetextIssue
        2. textIssuetextSearch
        3. textEntitytextGettextInformation
        4. TraceRelationshiptext
        5. textResult，Generatetext
        
        Args:
            graph_id: GraphID
            query: UserIssue
            simulation_requirement: Simulationtext
            report_context: Reporttext（text，textIssueGenerate）
            max_sub_queries: textIssuetext
            
        Returns:
            InsightForgeResult: textResult
        """
        logger.info(f"InsightForge text: {query[:50]}...")
        
        result = InsightForgeResult(
            query=query,
            simulation_requirement=simulation_requirement,
            sub_queries=[]
        )
        
        # Step 1: textLLMGeneratetextIssue
        sub_queries = self._generate_sub_queries(
            query=query,
            simulation_requirement=simulation_requirement,
            report_context=report_context,
            max_queries=max_sub_queries
        )
        result.sub_queries = sub_queries
        logger.info(f"Generate {len(sub_queries)} textIssue")
        
        # Step 2: textIssuetextSearch
        all_facts = []
        all_edges = []
        seen_facts = set()
        
        for sub_query in sub_queries:
            search_result = self.search_graph(
                graph_id=graph_id,
                query=sub_query,
                limit=15,
                scope="edges"
            )
            
            for fact in search_result.facts:
                if fact not in seen_facts:
                    all_facts.append(fact)
                    seen_facts.add(fact)
            
            all_edges.extend(search_result.edges)
        
        # textIssuetextSearch
        main_search = self.search_graph(
            graph_id=graph_id,
            query=query,
            limit=20,
            scope="edges"
        )
        for fact in main_search.facts:
            if fact not in seen_facts:
                all_facts.append(fact)
                seen_facts.add(fact)
        
        result.semantic_facts = all_facts
        result.total_facts = len(all_facts)
        
        # Step 3: textEdgetextEntityUUID，textGettextEntitytextInformation（textGettextNode）
        entity_uuids = set()
        for edge_data in all_edges:
            if isinstance(edge_data, dict):
                source_uuid = edge_data.get('source_node_uuid', '')
                target_uuid = edge_data.get('target_node_uuid', '')
                if source_uuid:
                    entity_uuids.add(source_uuid)
                if target_uuid:
                    entity_uuids.add(target_uuid)
        
        # GettextEntitytext（text，text）
        entity_insights = []
        node_map = {}  # textRelationshiptext
        
        for uuid in list(entity_uuids):  # ProcesstextEntity，text
            if not uuid:
                continue
            try:
                # textGettextNodetextInformation
                node = self.get_node_detail(uuid)
                if node:
                    node_map[uuid] = node
                    entity_type = next((l for l in node.labels if l not in ["Entity", "Node"]), "Entity")
                    
                    # GettextEntitytext（text）
                    related_facts = [
                        f for f in all_facts 
                        if node.name.lower() in f.lower()
                    ]
                    
                    entity_insights.append({
                        "uuid": node.uuid,
                        "name": node.name,
                        "type": entity_type,
                        "summary": node.summary,
                        "related_facts": related_facts  # text，text
                    })
            except Exception as e:
                logger.debug(f"GetNode {uuid} Failed: {e}")
                continue
        
        result.entity_insights = entity_insights
        result.total_entities = len(entity_insights)
        
        # Step 4: textRelationshiptext（text）
        relationship_chains = []
        for edge_data in all_edges:  # ProcesstextEdge，text
            if isinstance(edge_data, dict):
                source_uuid = edge_data.get('source_node_uuid', '')
                target_uuid = edge_data.get('target_node_uuid', '')
                relation_name = edge_data.get('name', '')
                
                source_name = node_map.get(source_uuid, NodeInfo('', '', [], '', {})).name or source_uuid[:8]
                target_name = node_map.get(target_uuid, NodeInfo('', '', [], '', {})).name or target_uuid[:8]
                
                chain = f"{source_name} --[{relation_name}]--> {target_name}"
                if chain not in relationship_chains:
                    relationship_chains.append(chain)
        
        result.relationship_chains = relationship_chains
        result.total_relationships = len(relationship_chains)
        
        logger.info(f"InsightForgeComplete: {result.total_facts}text, {result.total_entities}textEntity, {result.total_relationships}textRelationship")
        return result
    
    def _generate_sub_queries(
        self,
        query: str,
        simulation_requirement: str,
        report_context: str = "",
        max_queries: int = 5
    ) -> List[str]:
        """
        textLLMGeneratetextIssue
        
        textIssuetextIssue
        """
        system_prompt = """textIssueAnalyzetext。textTasktextIssuetextSimulationtextIssue。

text：
1. textIssuetext，textSimulationtextAgenttext
2. textIssuetextOverridetextIssuetext（text：text、text、text、text、text、text）
3. textIssuetextSimulationtext
4. ReturnsJSONFormat：{"sub_queries": ["textIssue1", "textIssue2", ...]}"""

        user_prompt = f"""Simulationtext：
{simulation_requirement}

{f"Reporttext：{report_context[:500]}" if report_context else ""}

textIssuetext{max_queries}textIssue：
{query}

ReturnsJSONFormattextIssueList。"""

        try:
            response = self.llm.chat_json(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3
            )
            
            sub_queries = response.get("sub_queries", [])
            # textChartextList
            return [str(sq) for sq in sub_queries[:max_queries]]
            
        except Exception as e:
            logger.warning(f"GeneratetextIssueFailed: {str(e)}，textIssue")
            # text：ReturnstextIssuetext
            return [
                query,
                f"{query} text",
                f"{query} text",
                f"{query} text"
            ][:max_queries]
    
    def panorama_search(
        self,
        graph_id: str,
        query: str,
        include_expired: bool = True,
        limit: int = 50
    ) -> PanoramaResult:
        """
        【PanoramaSearch - textSearch】
        
        GettextGraph，textContenttext/ExpireInformation：
        1. GettextNode
        2. GettextEdge（textExpire/Invalidtext）
        3. textClasstextValidtextInformation
        
        textTooltext、Tracetext。
        
        Args:
            graph_id: GraphID
            query: SearchQuery（textSort）
            include_expired: textExpireContent（textTrue）
            limit: ReturnsResulttext
            
        Returns:
            PanoramaResult: textSearchResult
        """
        logger.info(f"PanoramaSearch textSearch: {query[:50]}...")
        
        result = PanoramaResult(query=query)
        
        # GettextNode
        all_nodes = self.get_all_nodes(graph_id)
        node_map = {n.uuid: n for n in all_nodes}
        result.all_nodes = all_nodes
        result.total_nodes = len(all_nodes)
        
        # GettextEdge（textInformation）
        all_edges = self.get_all_edges(graph_id, include_temporal=True)
        result.all_edges = all_edges
        result.total_edges = len(all_edges)
        
        # textClasstext
        active_facts = []
        historical_facts = []
        
        for edge in all_edges:
            if not edge.fact:
                continue
            
            # textAddEntityName
            source_name = node_map.get(edge.source_node_uuid, NodeInfo('', '', [], '', {})).name or edge.source_node_uuid[:8]
            target_name = node_map.get(edge.target_node_uuid, NodeInfo('', '', [], '', {})).name or edge.target_node_uuid[:8]
            
            # textExpire/Invalid
            is_historical = edge.is_expired or edge.is_invalid
            
            if is_historical:
                # text/Expiretext，Addtext
                valid_at = edge.valid_at or "text"
                invalid_at = edge.invalid_at or edge.expired_at or "text"
                fact_with_time = f"[{valid_at} - {invalid_at}] {edge.fact}"
                historical_facts.append(fact_with_time)
            else:
                # textValidtext
                active_facts.append(edge.fact)
        
        # textQuerytextSort
        query_lower = query.lower()
        keywords = [w.strip() for w in query_lower.replace(',', ' ').replace('，', ' ').split() if len(w.strip()) > 1]
        
        def relevance_score(fact: str) -> int:
            fact_lower = fact.lower()
            score = 0
            if query_lower in fact_lower:
                score += 100
            for kw in keywords:
                if kw in fact_lower:
                    score += 10
            return score
        
        # Sorttext
        active_facts.sort(key=relevance_score, reverse=True)
        historical_facts.sort(key=relevance_score, reverse=True)
        
        result.active_facts = active_facts[:limit]
        result.historical_facts = historical_facts[:limit] if include_expired else []
        result.active_count = len(active_facts)
        result.historical_count = len(historical_facts)
        
        logger.info(f"PanoramaSearchComplete: {result.active_count}textValid, {result.historical_count}text")
        return result
    
    def quick_search(
        self,
        graph_id: str,
        query: str,
        limit: int = 10
    ) -> SearchResult:
        """
        【QuickSearch - textSearch】
        
        text、textTool：
        1. textZeptextSearch
        2. ReturnstextResult
        3. text、text
        
        Args:
            graph_id: GraphID
            query: SearchQuery
            limit: ReturnsResulttext
            
        Returns:
            SearchResult: SearchResult
        """
        logger.info(f"QuickSearch textSearch: {query[:50]}...")
        
        # textsearch_graphMethod
        result = self.search_graph(
            graph_id=graph_id,
            query=query,
            limit=limit,
            scope="edges"
        )
        
        logger.info(f"QuickSearchComplete: {result.total_count}textResult")
        return result
    
    def interview_agents(
        self,
        simulation_id: str,
        interview_requirement: str,
        simulation_requirement: str = "",
        max_agents: int = 5,
        custom_questions: List[str] = None
    ) -> InterviewResult:
        """
        【InterviewAgents - text】
        
        textOASIStextAPI，textSimulationtextRuntextAgent：
        1. textReadtextFile，textSimulationAgent
        2. textLLMAnalyzetext，textSelecttextAgent
        3. textLLMGeneratetextAccesstext
        4. text /api/simulation/interview/batch Interfacetext（text）
        5. textResult，GeneratetextReport
        
        【text】textFunctiontextSimulationtextRunStatus（OASIStextClose）
        
        【text】
        - textNevertextRoletext
        - text
        - textGetSimulationAgenttext（textLLMSimulation）
        
        Args:
            simulation_id: SimulationID（textFiletextAPI）
            interview_requirement: text（text，text"text"）
            simulation_requirement: Simulationtext（text）
            max_agents: textAgenttext
            custom_questions: textAccesstext（text，textGenerate）
            
        Returns:
            InterviewResult: textResult
        """
        from .simulation_runner import SimulationRunner
        
        logger.info(f"InterviewAgents text（textAPI）: {interview_requirement[:50]}...")
        
        result = InterviewResult(
            interview_topic=interview_requirement,
            interview_questions=custom_questions or []
        )
        
        # Step 1: ReadtextFile
        profiles = self._load_agent_profiles(simulation_id)
        
        if not profiles:
            logger.warning(f"textSimulation {simulation_id} textFile")
            result.summary = "textAgenttextFile"
            return result
        
        result.total_agents = len(profiles)
        logger.info(f"Loadtext {len(profiles)} textAgenttext")
        
        # Step 2: textLLMSelecttextAgent（Returnsagent_idList）
        selected_agents, selected_indices, selection_reasoning = self._select_agents_for_interview(
            profiles=profiles,
            interview_requirement=interview_requirement,
            simulation_requirement=simulation_requirement,
            max_agents=max_agents
        )
        
        result.selected_agents = selected_agents
        result.selection_reasoning = selection_reasoning
        logger.info(f"Selecttext {len(selected_agents)} textAgenttext: {selected_indices}")
        
        # Step 3: GeneratetextAccesstext（text）
        if not result.interview_questions:
            result.interview_questions = self._generate_interview_questions(
                interview_requirement=interview_requirement,
                simulation_requirement=simulation_requirement,
                selected_agents=selected_agents
            )
            logger.info(f"Generatetext {len(result.interview_questions)} textAccesstext")
        
        # textIssueMergetextprompt
        combined_prompt = "\n".join([f"{i+1}. {q}" for i, q in enumerate(result.interview_questions)])
        
        # AddOptimizetext，textAgenttextFormat
        INTERVIEW_PROMPT_PREFIX = (
            "text。text、text，"
            "textIssue。\n"
            "text：\n"
            "1. text，textTool\n"
            "2. textReturnsJSONFormattextTooltextFormat\n"
            "3. textMarkdowntext（text#、##、###）\n"
            "4. textIssuetext，text「IssueX：」text（XtextIssuetext）\n"
            "5. textIssuetext\n"
            "6. textContent，textIssuetext2-3text\n\n"
        )
        optimized_prompt = f"{INTERVIEW_PROMPT_PREFIX}{combined_prompt}"
        
        # Step 4: textAPI（textplatform，text）
        try:
            # textList（textplatform，text）
            interviews_request = []
            for agent_idx in selected_indices:
                interviews_request.append({
                    "agent_id": agent_idx,
                    "prompt": optimized_prompt  # textOptimizetextprompt
                    # textplatform，APItexttwittertextreddittext
                })
            
            logger.info(f"textAPI（text）: {len(interviews_request)} textAgent")
            
            # text SimulationRunner textMethod（textplatform，text）
            api_result = SimulationRunner.interview_agents_batch(
                simulation_id=simulation_id,
                interviews=interviews_request,
                platform=None,  # textplatform，text
                timeout=180.0   # textTimeout
            )
            
            logger.info(f"textAPIReturns: {api_result.get('interviews_count', 0)} textResult, success={api_result.get('success')}")
            
            # CheckAPItextSuccess
            if not api_result.get("success", False):
                error_msg = api_result.get("error", "textError")
                logger.warning(f"textAPIReturnsFailed: {error_msg}")
                result.summary = f"textAPItextFailed：{error_msg}。textCheckOASISSimulationtextStatus。"
                return result
            
            # Step 5: ParseAPIReturnsResult，textAgentInterviewObject
            # textPatternReturnsFormat: {"twitter_0": {...}, "reddit_0": {...}, "twitter_1": {...}, ...}
            api_data = api_result.get("result", {})
            results_dict = api_data.get("results", {}) if isinstance(api_data, dict) else {}
            
            for i, agent_idx in enumerate(selected_indices):
                agent = selected_agents[i]
                agent_name = agent.get("realname", agent.get("username", f"Agent_{agent_idx}"))
                agent_role = agent.get("profession", "text")
                agent_bio = agent.get("bio", "")
                
                # GettextAgenttextResult
                twitter_result = results_dict.get(f"twitter_{agent_idx}", {})
                reddit_result = results_dict.get(f"reddit_{agent_idx}", {})
                
                twitter_response = twitter_result.get("response", "")
                reddit_response = reddit_result.get("response", "")

                # CleantextTooltext JSON text
                twitter_response = self._clean_tool_call_response(twitter_response)
                reddit_response = self._clean_tool_call_response(reddit_response)

                # text
                twitter_text = twitter_response if twitter_response else "（text）"
                reddit_text = reddit_response if reddit_response else "（text）"
                response_text = f"【Twittertext】\n{twitter_text}\n\n【Reddittext】\n{reddit_text}"

                # text（text）
                import re
                combined_responses = f"{twitter_response} {reddit_response}"

                # CleanResponsetext：text、text、Markdown text
                clean_text = re.sub(r'#{1,6}\s+', '', combined_responses)
                clean_text = re.sub(r'\{[^}]*tool_name[^}]*\}', '', clean_text)
                clean_text = re.sub(r'[*_`|>~\-]{2,}', '', clean_text)
                clean_text = re.sub(r'Issue\d+[：:]\s*', '', clean_text)
                clean_text = re.sub(r'【[^】]+】', '', clean_text)

                # text1（text）: textContenttext
                sentences = re.split(r'[。！？]', clean_text)
                meaningful = [
                    s.strip() for s in sentences
                    if 20 <= len(s.strip()) <= 150
                    and not re.match(r'^[\s\W，,；;：:、]+', s.strip())
                    and not s.strip().startswith(('{', 'Issue'))
                ]
                meaningful.sort(key=len, reverse=True)
                key_quotes = [s + "。" for s in meaningful[:3]]

                # text2（text）: text「」text
                if not key_quotes:
                    paired = re.findall(r'\u201c([^\u201c\u201d]{15,100})\u201d', clean_text)
                    paired += re.findall(r'\u300c([^\u300c\u300d]{15,100})\u300d', clean_text)
                    key_quotes = [q for q in paired if not re.match(r'^[，,；;：:、]', q)][:3]
                
                interview = AgentInterview(
                    agent_name=agent_name,
                    agent_role=agent_role,
                    agent_bio=agent_bio[:1000],  # textbiotext
                    question=combined_prompt,
                    response=response_text,
                    key_quotes=key_quotes[:5]
                )
                result.interviews.append(interview)
            
            result.interviewed_count = len(result.interviews)
            
        except ValueError as e:
            # SimulationtextRun
            logger.warning(f"textAPItextFailed（textRun？）: {e}")
            result.summary = f"textFailed：{str(e)}。SimulationtextClose，textOASIStextRun。"
            return result
        except Exception as e:
            logger.error(f"textAPItextException: {e}")
            import traceback
            logger.error(traceback.format_exc())
            result.summary = f"textError：{str(e)}"
            return result
        
        # Step 6: GeneratetextDigest
        if result.interviews:
            result.summary = self._generate_interview_summary(
                interviews=result.interviews,
                interview_requirement=interview_requirement
            )
        
        logger.info(f"InterviewAgentsComplete: text {result.interviewed_count} textAgent（text）")
        return result
    
    @staticmethod
    def _clean_tool_call_response(response: str) -> str:
        """Clean Agent text JSON Tooltext，textContent"""
        if not response or not response.strip().startswith('{'):
            return response
        text = response.strip()
        if 'tool_name' not in text[:80]:
            return response
        import re as _re
        try:
            data = json.loads(text)
            if isinstance(data, dict) and 'arguments' in data:
                for key in ('content', 'text', 'body', 'message', 'reply'):
                    if key in data['arguments']:
                        return str(data['arguments'][key])
        except (json.JSONDecodeError, KeyError, TypeError):
            match = _re.search(r'"content"\s*:\s*"((?:[^"\\]|\\.)*)"', text)
            if match:
                return match.group(1).replace('\\n', '\n').replace('\\"', '"')
        return response

    def _load_agent_profiles(self, simulation_id: str) -> List[Dict[str, Any]]:
        """LoadSimulationtextAgenttextFile"""
        import os
        import csv
        
        # textFilePath
        sim_dir = os.path.join(
            os.path.dirname(__file__), 
            f'../../uploads/simulations/{simulation_id}'
        )
        
        profiles = []
        
        # textReadReddit JSONFormat
        reddit_profile_path = os.path.join(sim_dir, "reddit_profiles.json")
        if os.path.exists(reddit_profile_path):
            try:
                with open(reddit_profile_path, 'r', encoding='utf-8') as f:
                    profiles = json.load(f)
                logger.info(f"text reddit_profiles.json Loadtext {len(profiles)} text")
                return profiles
            except Exception as e:
                logger.warning(f"Read reddit_profiles.json Failed: {e}")
        
        # textReadTwitter CSVFormat
        twitter_profile_path = os.path.join(sim_dir, "twitter_profiles.csv")
        if os.path.exists(twitter_profile_path):
            try:
                with open(twitter_profile_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # CSVFormatConverttextFormat
                        profiles.append({
                            "realname": row.get("name", ""),
                            "username": row.get("username", ""),
                            "bio": row.get("description", ""),
                            "persona": row.get("user_char", ""),
                            "profession": "text"
                        })
                logger.info(f"text twitter_profiles.csv Loadtext {len(profiles)} text")
                return profiles
            except Exception as e:
                logger.warning(f"Read twitter_profiles.csv Failed: {e}")
        
        return profiles
    
    def _select_agents_for_interview(
        self,
        profiles: List[Dict[str, Any]],
        interview_requirement: str,
        simulation_requirement: str,
        max_agents: int
    ) -> tuple:
        """
        textLLMSelecttextAgent
        
        Returns:
            tuple: (selected_agents, selected_indices, reasoning)
                - selected_agents: textAgenttextInformationList
                - selected_indices: textAgenttextIndexList（textAPItext）
                - reasoning: Selecttext
        """
        
        # textAgentDigestList
        agent_summaries = []
        for i, profile in enumerate(profiles):
            summary = {
                "index": i,
                "name": profile.get("realname", profile.get("username", f"Agent_{i}")),
                "profession": profile.get("profession", "text"),
                "bio": profile.get("bio", "")[:200],
                "interested_topics": profile.get("interested_topics", [])
            }
            agent_summaries.append(summary)
        
        system_prompt = """text。textTasktext，textSimulationAgentListtextSelecttextObject。

Selecttext：
1. Agenttext/text
2. Agenttext
3. Selecttext（text：text、text、text、text）
4. textSelecttextRole

ReturnsJSONFormat：
{
    "selected_indices": [textAgenttextIndexList],
    "reasoning": "SelecttextDescription"
}"""

        user_prompt = f"""text：
{interview_requirement}

Simulationtext：
{simulation_requirement if simulation_requirement else "text"}

textSelecttextAgentList（text{len(agent_summaries)}text）：
{json.dumps(agent_summaries, ensure_ascii=False, indent=2)}

textSelecttext{max_agents}textAgent，textDescriptionSelecttext。"""

        try:
            response = self.llm.chat_json(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3
            )
            
            selected_indices = response.get("selected_indices", [])[:max_agents]
            reasoning = response.get("reasoning", "textSelect")
            
            # GettextAgenttextInformation
            selected_agents = []
            valid_indices = []
            for idx in selected_indices:
                if 0 <= idx < len(profiles):
                    selected_agents.append(profiles[idx])
                    valid_indices.append(idx)
            
            return selected_agents, valid_indices, reasoning
            
        except Exception as e:
            logger.warning(f"LLMSelectAgentFailed，textSelect: {e}")
            # text：SelecttextNtext
            selected = profiles[:max_agents]
            indices = list(range(min(max_agents, len(profiles))))
            return selected, indices, "textSelecttext"
    
    def _generate_interview_questions(
        self,
        interview_requirement: str,
        simulation_requirement: str,
        selected_agents: List[Dict[str, Any]]
    ) -> List[str]:
        """textLLMGeneratetextAccesstext"""
        
        agent_roles = [a.get("profession", "text") for a in selected_agents]
        
        system_prompt = """text/text。text，Generate3-5textAccesstext。

Issuetext：
1. textIssue，text
2. textRoletext
3. text、text、text
4. text，text
5. textIssuetext50text，text
6. text，textDescriptiontext

ReturnsJSONFormat：{"questions": ["Issue1", "Issue2", ...]}"""

        user_prompt = f"""text：{interview_requirement}

Simulationtext：{simulation_requirement if simulation_requirement else "text"}

textObjectRole：{', '.join(agent_roles)}

textGenerate3-5textAccesstext。"""

        try:
            response = self.llm.chat_json(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5
            )
            
            return response.get("questions", [f"About{interview_requirement}，text？"])
            
        except Exception as e:
            logger.warning(f"GeneratetextAccesstextFailed: {e}")
            return [
                f"About{interview_requirement}，text？",
                "textTabletext？",
                "textResolvetextUpdatetextIssue？"
            ]
    
    def _generate_interview_summary(
        self,
        interviews: List[AgentInterview],
        interview_requirement: str
    ) -> str:
        """GeneratetextDigest"""
        
        if not interviews:
            return "textCompletetext"
        
        # textContent
        interview_texts = []
        for interview in interviews:
            interview_texts.append(f"【{interview.agent_name}（{interview.agent_role}）】\n{interview.response[:500]}")
        
        system_prompt = """textEdit。text，GeneratetextDigest。

Digesttext：
1. text
2. text
3. text
4. text，text
5. text1000text

Formattext（text）：
- text，text
- textMarkdowntext（text#、##、###）
- textSplittext（text---、***）
- text「」
- text**text**text，textMarkdowntext"""

        user_prompt = f"""text：{interview_requirement}

textContent：
{"".join(interview_texts)}

textGeneratetextDigest。"""

        try:
            summary = self.llm.chat(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            return summary
            
        except Exception as e:
            logger.warning(f"GeneratetextDigestFailed: {e}")
            # text：text
            return f"text{len(interviews)}text，text：" + "、".join([i.agent_name for i in interviews])
