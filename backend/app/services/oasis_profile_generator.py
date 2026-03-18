"""
OASIS Agent ProfileGeneratetext
textZepGraphtextEntityConverttextOASISSimulationtextAgent ProfileFormat

OptimizeUpdatetext：
1. textZeptextFunctiontextNodeInformation
2. OptimizetextGeneratetext
3. textEntitytextAbstractiontextEntity
"""

import json
import random
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from openai import OpenAI
from zep_cloud.client import Zep

from ..config import Config
from ..utils.logger import get_logger
from .zep_entity_reader import EntityNode, ZepEntityReader

logger = get_logger('mirofish.oasis_profile')


@dataclass
class OasisAgentProfile:
    """OASIS Agent ProfileDatatext"""
    # textField
    user_id: int
    user_name: str
    name: str
    bio: str
    persona: str
    
    # textField - Reddittext
    karma: int = 1000
    
    # textField - Twittertext
    friend_count: int = 100
    follower_count: int = 150
    statuses_count: int = 500
    
    # textInformation
    age: Optional[int] = None
    gender: Optional[str] = None
    mbti: Optional[str] = None
    country: Optional[str] = None
    profession: Optional[str] = None
    interested_topics: List[str] = field(default_factory=list)
    
    # textEntityInformation
    source_entity_uuid: Optional[str] = None
    source_entity_type: Optional[str] = None
    
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    
    def to_reddit_format(self) -> Dict[str, Any]:
        """ConverttextReddittextFormat"""
        profile = {
            "user_id": self.user_id,
            "username": self.user_name,  # OASIS textFieldtext username（text）
            "name": self.name,
            "bio": self.bio,
            "persona": self.persona,
            "karma": self.karma,
            "created_at": self.created_at,
        }
        
        # AddtextInformation（text）
        if self.age:
            profile["age"] = self.age
        if self.gender:
            profile["gender"] = self.gender
        if self.mbti:
            profile["mbti"] = self.mbti
        if self.country:
            profile["country"] = self.country
        if self.profession:
            profile["profession"] = self.profession
        if self.interested_topics:
            profile["interested_topics"] = self.interested_topics
        
        return profile
    
    def to_twitter_format(self) -> Dict[str, Any]:
        """ConverttextTwittertextFormat"""
        profile = {
            "user_id": self.user_id,
            "username": self.user_name,  # OASIS textFieldtext username（text）
            "name": self.name,
            "bio": self.bio,
            "persona": self.persona,
            "friend_count": self.friend_count,
            "follower_count": self.follower_count,
            "statuses_count": self.statuses_count,
            "created_at": self.created_at,
        }
        
        # AddtextInformation
        if self.age:
            profile["age"] = self.age
        if self.gender:
            profile["gender"] = self.gender
        if self.mbti:
            profile["mbti"] = self.mbti
        if self.country:
            profile["country"] = self.country
        if self.profession:
            profile["profession"] = self.profession
        if self.interested_topics:
            profile["interested_topics"] = self.interested_topics
        
        return profile
    
    def to_dict(self) -> Dict[str, Any]:
        """ConverttextDictFormat"""
        return {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "name": self.name,
            "bio": self.bio,
            "persona": self.persona,
            "karma": self.karma,
            "friend_count": self.friend_count,
            "follower_count": self.follower_count,
            "statuses_count": self.statuses_count,
            "age": self.age,
            "gender": self.gender,
            "mbti": self.mbti,
            "country": self.country,
            "profession": self.profession,
            "interested_topics": self.interested_topics,
            "source_entity_uuid": self.source_entity_uuid,
            "source_entity_type": self.source_entity_type,
            "created_at": self.created_at,
        }


class OasisProfileGenerator:
    """
    OASIS ProfileGeneratetext
    
    textZepGraphtextEntityConverttextOASISSimulationtextAgent Profile
    
    Optimizetext：
    1. textZepGraphtextFunctionGettext
    2. Generatetext（textInformation、text、text、text）
    3. textEntitytextAbstractiontextEntity
    """
    
    # MBTITypeList
    MBTI_TYPES = [
        "INTJ", "INTP", "ENTJ", "ENTP",
        "INFJ", "INFP", "ENFJ", "ENFP",
        "ISTJ", "ISFJ", "ESTJ", "ESFJ",
        "ISTP", "ISFP", "ESTP", "ESFP"
    ]
    
    # textList
    COUNTRIES = [
        "China", "US", "UK", "Japan", "Germany", "France", 
        "Canada", "Australia", "Brazil", "India", "South Korea"
    ]
    
    # textTypeEntity（textGeneratetext）
    INDIVIDUAL_ENTITY_TYPES = [
        "student", "alumni", "professor", "person", "publicfigure", 
        "expert", "faculty", "official", "journalist", "activist"
    ]
    
    # text/textTypeEntity（textGeneratetextTabletext）
    GROUP_ENTITY_TYPES = [
        "university", "governmentagency", "organization", "ngo", 
        "mediaoutlet", "company", "institution", "group", "community"
    ]
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        zep_api_key: Optional[str] = None,
        graph_id: Optional[str] = None
    ):
        self.api_key = api_key or Config.LLM_API_KEY
        self.base_url = base_url or Config.LLM_BASE_URL
        self.model_name = model_name or Config.LLM_MODEL_NAME
        
        if not self.api_key:
            raise ValueError("LLM_API_KEY textConfiguration")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        # ZepClienttext
        self.zep_api_key = zep_api_key or Config.ZEP_API_KEY
        self.zep_client = None
        self.graph_id = graph_id
        
        if self.zep_api_key:
            try:
                self.zep_client = Zep(api_key=self.zep_api_key)
            except Exception as e:
                logger.warning(f"ZepClientInitializeFailed: {e}")
    
    def generate_profile_from_entity(
        self, 
        entity: EntityNode, 
        user_id: int,
        use_llm: bool = True
    ) -> OasisAgentProfile:
        """
        textZepEntityGenerateOASIS Agent Profile
        
        Args:
            entity: ZepEntityNode
            user_id: UserID（textOASIS）
            use_llm: textLLMGeneratetext
            
        Returns:
            OasisAgentProfile
        """
        entity_type = entity.get_entity_type() or "Entity"
        
        # textInformation
        name = entity.name
        user_name = self._generate_username(name)
        
        # textInformation
        context = self._build_entity_context(entity)
        
        if use_llm:
            # textLLMGeneratetext
            profile_data = self._generate_profile_with_llm(
                entity_name=name,
                entity_type=entity_type,
                entity_summary=entity.summary,
                entity_attributes=entity.attributes,
                context=context
            )
        else:
            # textGeneratetext
            profile_data = self._generate_profile_rule_based(
                entity_name=name,
                entity_type=entity_type,
                entity_summary=entity.summary,
                entity_attributes=entity.attributes
            )
        
        return OasisAgentProfile(
            user_id=user_id,
            user_name=user_name,
            name=name,
            bio=profile_data.get("bio", f"{entity_type}: {name}"),
            persona=profile_data.get("persona", entity.summary or f"A {entity_type} named {name}."),
            karma=profile_data.get("karma", random.randint(500, 5000)),
            friend_count=profile_data.get("friend_count", random.randint(50, 500)),
            follower_count=profile_data.get("follower_count", random.randint(100, 1000)),
            statuses_count=profile_data.get("statuses_count", random.randint(100, 2000)),
            age=profile_data.get("age"),
            gender=profile_data.get("gender"),
            mbti=profile_data.get("mbti"),
            country=profile_data.get("country"),
            profession=profile_data.get("profession"),
            interested_topics=profile_data.get("interested_topics", []),
            source_entity_uuid=entity.uuid,
            source_entity_type=entity_type,
        )
    
    def _generate_username(self, name: str) -> str:
        """GenerateUsertext"""
        # RemovetextChar，Converttext
        username = name.lower().replace(" ", "_")
        username = ''.join(c for c in username if c.isalnum() or c == '_')
        
        # Addtext
        suffix = random.randint(100, 999)
        return f"{username}_{suffix}"
    
    def _search_zep_for_entity(self, entity: EntityNode) -> Dict[str, Any]:
        """
        textZepGraphtextSearchFunctionGetEntitytextInformation
        
        ZeptextSearchInterface，textSearchedgestextnodestextMergeResult。
        textRequesttextSearch，text。
        
        Args:
            entity: EntityNodeObject
            
        Returns:
            textfacts, node_summaries, contexttextDict
        """
        import concurrent.futures
        
        if not self.zep_client:
            return {"facts": [], "node_summaries": [], "context": ""}
        
        entity_name = entity.name
        
        results = {
            "facts": [],
            "node_summaries": [],
            "context": ""
        }
        
        # textgraph_idtextSearch
        if not self.graph_id:
            logger.debug(f"SkipZeptext：textSetgraph_id")
            return results
        
        comprehensive_query = f"About{entity_name}textInformation、Active、text、Relationshiptext"
        
        def search_edges():
            """SearchEdge（text/Relationship）- textRetrytext"""
            max_retries = 3
            last_exception = None
            delay = 2.0
            
            for attempt in range(max_retries):
                try:
                    return self.zep_client.graph.search(
                        query=comprehensive_query,
                        graph_id=self.graph_id,
                        limit=30,
                        scope="edges",
                        reranker="rrf"
                    )
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.debug(f"ZepEdgeSearchtext {attempt + 1} textFailed: {str(e)[:80]}, Retrytext...")
                        time.sleep(delay)
                        delay *= 2
                    else:
                        logger.debug(f"ZepEdgeSearchtext {max_retries} textFailed: {e}")
            return None
        
        def search_nodes():
            """SearchNode（EntityDigest）- textRetrytext"""
            max_retries = 3
            last_exception = None
            delay = 2.0
            
            for attempt in range(max_retries):
                try:
                    return self.zep_client.graph.search(
                        query=comprehensive_query,
                        graph_id=self.graph_id,
                        limit=20,
                        scope="nodes",
                        reranker="rrf"
                    )
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.debug(f"ZepNodeSearchtext {attempt + 1} textFailed: {str(e)[:80]}, Retrytext...")
                        time.sleep(delay)
                        delay *= 2
                    else:
                        logger.debug(f"ZepNodeSearchtext {max_retries} textFailed: {e}")
            return None
        
        try:
            # textExecuteedgestextnodesSearch
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                edge_future = executor.submit(search_edges)
                node_future = executor.submit(search_nodes)
                
                # GetResult
                edge_result = edge_future.result(timeout=30)
                node_result = node_future.result(timeout=30)
            
            # ProcessEdgeSearchResult
            all_facts = set()
            if edge_result and hasattr(edge_result, 'edges') and edge_result.edges:
                for edge in edge_result.edges:
                    if hasattr(edge, 'fact') and edge.fact:
                        all_facts.add(edge.fact)
            results["facts"] = list(all_facts)
            
            # ProcessNodeSearchResult
            all_summaries = set()
            if node_result and hasattr(node_result, 'nodes') and node_result.nodes:
                for node in node_result.nodes:
                    if hasattr(node, 'summary') and node.summary:
                        all_summaries.add(node.summary)
                    if hasattr(node, 'name') and node.name and node.name != entity_name:
                        all_summaries.add(f"textEntity: {node.name}")
            results["node_summaries"] = list(all_summaries)
            
            # text
            context_parts = []
            if results["facts"]:
                context_parts.append("textInformation:\n" + "\n".join(f"- {f}" for f in results["facts"][:20]))
            if results["node_summaries"]:
                context_parts.append("textEntity:\n" + "\n".join(f"- {s}" for s in results["node_summaries"][:10]))
            results["context"] = "\n\n".join(context_parts)
            
            logger.info(f"ZeptextComplete: {entity_name}, Get {len(results['facts'])} text, {len(results['node_summaries'])} textNode")
            
        except concurrent.futures.TimeoutError:
            logger.warning(f"ZeptextTimeout ({entity_name})")
        except Exception as e:
            logger.warning(f"ZeptextFailed ({entity_name}): {e}")
        
        return results
    
    def _build_entity_context(self, entity: EntityNode) -> str:
        """
        textEntitytextInformation
        
        text：
        1. EntitytextEdgeInformation（text）
        2. textNodetextInformation
        3. ZeptextInformation
        """
        context_parts = []
        
        # 1. AddEntityPropertyInformation
        if entity.attributes:
            attrs = []
            for key, value in entity.attributes.items():
                if value and str(value).strip():
                    attrs.append(f"- {key}: {value}")
            if attrs:
                context_parts.append("### EntityProperty\n" + "\n".join(attrs))
        
        # 2. AddtextEdgeInformation（text/Relationship）
        existing_facts = set()
        if entity.related_edges:
            relationships = []
            for edge in entity.related_edges:  # text
                fact = edge.get("fact", "")
                edge_name = edge.get("edge_name", "")
                direction = edge.get("direction", "")
                
                if fact:
                    relationships.append(f"- {fact}")
                    existing_facts.add(fact)
                elif edge_name:
                    if direction == "outgoing":
                        relationships.append(f"- {entity.name} --[{edge_name}]--> (textEntity)")
                    else:
                        relationships.append(f"- (textEntity) --[{edge_name}]--> {entity.name}")
            
            if relationships:
                context_parts.append("### textRelationship\n" + "\n".join(relationships))
        
        # 3. AddtextNodetextInformation
        if entity.related_nodes:
            related_info = []
            for node in entity.related_nodes:  # text
                node_name = node.get("name", "")
                node_labels = node.get("labels", [])
                node_summary = node.get("summary", "")
                
                # FiltertextTag
                custom_labels = [l for l in node_labels if l not in ["Entity", "Node"]]
                label_str = f" ({', '.join(custom_labels)})" if custom_labels else ""
                
                if node_summary:
                    related_info.append(f"- **{node_name}**{label_str}: {node_summary}")
                else:
                    related_info.append(f"- **{node_name}**{label_str}")
            
            if related_info:
                context_parts.append("### textEntityInformation\n" + "\n".join(related_info))
        
        # 4. textZeptextGettextInformation
        zep_results = self._search_zep_for_entity(entity)
        
        if zep_results.get("facts"):
            # text：text
            new_facts = [f for f in zep_results["facts"] if f not in existing_facts]
            if new_facts:
                context_parts.append("### ZeptextInformation\n" + "\n".join(f"- {f}" for f in new_facts[:15]))
        
        if zep_results.get("node_summaries"):
            context_parts.append("### ZeptextNode\n" + "\n".join(f"- {s}" for s in zep_results["node_summaries"][:10]))
        
        return "\n\n".join(context_parts)
    
    def _is_individual_entity(self, entity_type: str) -> bool:
        """textTypeEntity"""
        return entity_type.lower() in self.INDIVIDUAL_ENTITY_TYPES
    
    def _is_group_entity(self, entity_type: str) -> bool:
        """text/textTypeEntity"""
        return entity_type.lower() in self.GROUP_ENTITY_TYPES
    
    def _generate_profile_with_llm(
        self,
        entity_name: str,
        entity_type: str,
        entity_summary: str,
        entity_attributes: Dict[str, Any],
        context: str
    ) -> Dict[str, Any]:
        """
        textLLMGeneratetext
        
        textEntityTypetext：
        - textEntity：Generatetext
        - text/textEntity：GeneratetextTabletext
        """
        
        is_individual = self._is_individual_entity(entity_type)
        
        if is_individual:
            prompt = self._build_individual_persona_prompt(
                entity_name, entity_type, entity_summary, entity_attributes, context
            )
        else:
            prompt = self._build_group_persona_prompt(
                entity_name, entity_type, entity_summary, entity_attributes, context
            )

        # textGenerate，textSuccesstextRetrytext
        max_attempts = 3
        last_error = None
        
        for attempt in range(max_attempts):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": self._get_system_prompt(is_individual)},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.7 - (attempt * 0.1)  # textRetrytext
                    # textSetmax_tokens，textLLMtext
                )
                
                content = response.choices[0].message.content
                
                # Checktext（finish_reasontext'stop'）
                finish_reason = response.choices[0].finish_reason
                if finish_reason == 'length':
                    logger.warning(f"LLMtext (attempt {attempt+1}), textFix...")
                    content = self._fix_truncated_json(content)
                
                # textParseJSON
                try:
                    result = json.loads(content)
                    
                    # ValidatetextField
                    if "bio" not in result or not result["bio"]:
                        result["bio"] = entity_summary[:200] if entity_summary else f"{entity_type}: {entity_name}"
                    if "persona" not in result or not result["persona"]:
                        result["persona"] = entity_summary or f"{entity_name}text{entity_type}。"
                    
                    return result
                    
                except json.JSONDecodeError as je:
                    logger.warning(f"JSONParseFailed (attempt {attempt+1}): {str(je)[:80]}")
                    
                    # textFixJSON
                    result = self._try_fix_json(content, entity_name, entity_type, entity_summary)
                    if result.get("_fixed"):
                        del result["_fixed"]
                        return result
                    
                    last_error = je
                    
            except Exception as e:
                logger.warning(f"LLMtextFailed (attempt {attempt+1}): {str(e)[:80]}")
                last_error = e
                import time
                time.sleep(1 * (attempt + 1))  # text
        
        logger.warning(f"LLMGeneratetextFailed（{max_attempts}text）: {last_error}, textGenerate")
        return self._generate_profile_rule_based(
            entity_name, entity_type, entity_summary, entity_attributes
        )
    
    def _fix_truncated_json(self, content: str) -> str:
        """FixtextJSON（textmax_tokenstext）"""
        import re
        
        # textJSONtext，text
        content = content.strip()
        
        # text
        open_braces = content.count('{') - content.count('}')
        open_brackets = content.count('[') - content.count(']')
        
        # ChecktextChartext
        # textCheck：text，textChartext
        if content and content[-1] not in '",}]':
            # textChartext
            content += '"'
        
        # text
        content += ']' * open_brackets
        content += '}' * open_braces
        
        return content
    
    def _try_fix_json(self, content: str, entity_name: str, entity_type: str, entity_summary: str = "") -> Dict[str, Any]:
        """textFixtextJSON"""
        import re
        
        # 1. textFixtext
        content = self._fix_truncated_json(content)
        
        # 2. textJSONtext
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            json_str = json_match.group()
            
            # 3. ProcessChartextIssue
            # textChartextReplacetext
            def fix_string_newlines(match):
                s = match.group(0)
                # ReplaceChartext
                s = s.replace('\n', ' ').replace('\r', ' ')
                # Replacetext
                s = re.sub(r'\s+', ' ', s)
                return s
            
            # textJSONChartext
            json_str = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', fix_string_newlines, json_str)
            
            # 4. textParse
            try:
                result = json.loads(json_str)
                result["_fixed"] = True
                return result
            except json.JSONDecodeError as e:
                # 5. textFailed，textFix
                try:
                    # RemovetextChar
                    json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', json_str)
                    # Replacetext
                    json_str = re.sub(r'\s+', ' ', json_str)
                    result = json.loads(json_str)
                    result["_fixed"] = True
                    return result
                except:
                    pass
        
        # 6. textContenttextInformation
        bio_match = re.search(r'"bio"\s*:\s*"([^"]*)"', content)
        persona_match = re.search(r'"persona"\s*:\s*"([^"]*)', content)  # text
        
        bio = bio_match.group(1) if bio_match else (entity_summary[:200] if entity_summary else f"{entity_type}: {entity_name}")
        persona = persona_match.group(1) if persona_match else (entity_summary or f"{entity_name}text{entity_type}。")
        
        # textContent，textFix
        if bio_match or persona_match:
            logger.info(f"textJSONtextInformation")
            return {
                "bio": bio,
                "persona": persona,
                "_fixed": True
            }
        
        # 7. textFailed，Returnstext
        logger.warning(f"JSONFixFailed，Returnstext")
        return {
            "bio": entity_summary[:200] if entity_summary else f"{entity_type}: {entity_name}",
            "persona": entity_summary or f"{entity_name}text{entity_type}。"
        }
    
    def _get_system_prompt(self, is_individual: bool) -> str:
        """Gettext"""
        base_prompt = "textUsertextGeneratetext。Generatetext、textSimulation,textRestoretext。textReturnsValidtextJSONFormat，textChartext。text。"
        return base_prompt
    
    def _build_individual_persona_prompt(
        self,
        entity_name: str,
        entity_type: str,
        entity_summary: str,
        entity_attributes: Dict[str, Any],
        context: str
    ) -> str:
        """textEntitytext"""
        
        attrs_str = json.dumps(entity_attributes, ensure_ascii=False) if entity_attributes else "text"
        context_str = context[:3000] if context else "text"
        
        return f"""textEntityGeneratetextUsertext,textRestoretext。

EntityName: {entity_name}
EntityType: {entity_type}
EntityDigest: {entity_summary}
EntityProperty: {attrs_str}

textInformation:
{context_str}

textGenerateJSON，textField:

1. bio: text，200text
2. persona: text（2000text），text:
   - textInformation（text、text、text、text）
   - text（text、text、textRelationship）
   - text（MBTIType、text、textTabletext）
   - text（text、Contenttext、text、text）
   - text（text、text/textContent）
   - text（text、text、text）
   - text（text，text，text）
3. age: textNumber（text）
4. gender: text，text: "male" text "female"
5. mbti: MBTIType（textINTJ、ENFPtext）
6. country: text（text，text"text"）
7. profession: text
8. interested_topics: textGroup

text:
- textFieldtextChartextNumber，text
- personatext
- text（textgenderFieldtextmale/female）
- ContenttextEntityInformationtext
- agetextValidtext，gendertext"male"text"female"
"""

    def _build_group_persona_prompt(
        self,
        entity_name: str,
        entity_type: str,
        entity_summary: str,
        entity_attributes: Dict[str, Any],
        context: str
    ) -> str:
        """text/textEntitytext"""
        
        attrs_str = json.dumps(entity_attributes, ensure_ascii=False) if entity_attributes else "text"
        context_str = context[:3000] if context else "text"
        
        return f"""text/textEntityGeneratetext,textRestoretext。

EntityName: {entity_name}
EntityType: {entity_type}
EntityDigest: {entity_summary}
EntityProperty: {attrs_str}

textInformation:
{context_str}

textGenerateJSON，textField:

1. bio: text，200text，text
2. persona: text（2000text），text:
   - textInformation（textName、text、text、text）
   - text（textType、text、textFunction）
   - text（text、textTabletext、text）
   - ReleaseContenttext（ContentType、Releasetext、text）
   - text（text、textProcesstext）
   - textDescription（textTabletext、text）
   - text（text，text，text）
3. age: text30（text）
4. gender: text"other"（textotherTabletext）
5. mbti: MBTIType，text，textISTJtextTabletext
6. country: text（text，text"text"）
7. profession: text
8. interested_topics: textDomaintextGroup

text:
- textFieldtextChartextNumber，textAllownulltext
- personatext，text
- text（textgenderFieldtext"other"）
- agetext30，gendertextChartext"other"
- text"""
    
    def _generate_profile_rule_based(
        self,
        entity_name: str,
        entity_type: str,
        entity_summary: str,
        entity_attributes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """textGeneratetext"""
        
        # textEntityTypeGeneratetext
        entity_type_lower = entity_type.lower()
        
        if entity_type_lower in ["student", "alumni"]:
            return {
                "bio": f"{entity_type} with interests in academics and social issues.",
                "persona": f"{entity_name} is a {entity_type.lower()} who is actively engaged in academic and social discussions. They enjoy sharing perspectives and connecting with peers.",
                "age": random.randint(18, 30),
                "gender": random.choice(["male", "female"]),
                "mbti": random.choice(self.MBTI_TYPES),
                "country": random.choice(self.COUNTRIES),
                "profession": "Student",
                "interested_topics": ["Education", "Social Issues", "Technology"],
            }
        
        elif entity_type_lower in ["publicfigure", "expert", "faculty"]:
            return {
                "bio": f"Expert and thought leader in their field.",
                "persona": f"{entity_name} is a recognized {entity_type.lower()} who shares insights and opinions on important matters. They are known for their expertise and influence in public discourse.",
                "age": random.randint(35, 60),
                "gender": random.choice(["male", "female"]),
                "mbti": random.choice(["ENTJ", "INTJ", "ENTP", "INTP"]),
                "country": random.choice(self.COUNTRIES),
                "profession": entity_attributes.get("occupation", "Expert"),
                "interested_topics": ["Politics", "Economics", "Culture & Society"],
            }
        
        elif entity_type_lower in ["mediaoutlet", "socialmediaplatform"]:
            return {
                "bio": f"Official account for {entity_name}. News and updates.",
                "persona": f"{entity_name} is a media entity that reports news and facilitates public discourse. The account shares timely updates and engages with the audience on current events.",
                "age": 30,  # text
                "gender": "other",  # textother
                "mbti": "ISTJ",  # text：text
                "country": "text",
                "profession": "Media",
                "interested_topics": ["General News", "Current Events", "Public Affairs"],
            }
        
        elif entity_type_lower in ["university", "governmentagency", "ngo", "organization"]:
            return {
                "bio": f"Official account of {entity_name}.",
                "persona": f"{entity_name} is an institutional entity that communicates official positions, announcements, and engages with stakeholders on relevant matters.",
                "age": 30,  # text
                "gender": "other",  # textother
                "mbti": "ISTJ",  # text：text
                "country": "text",
                "profession": entity_type,
                "interested_topics": ["Public Policy", "Community", "Official Announcements"],
            }
        
        else:
            # text
            return {
                "bio": entity_summary[:150] if entity_summary else f"{entity_type}: {entity_name}",
                "persona": entity_summary or f"{entity_name} is a {entity_type.lower()} participating in social discussions.",
                "age": random.randint(25, 50),
                "gender": random.choice(["male", "female"]),
                "mbti": random.choice(self.MBTI_TYPES),
                "country": random.choice(self.COUNTRIES),
                "profession": entity_type,
                "interested_topics": ["General", "Social Issues"],
            }
    
    def set_graph_id(self, graph_id: str):
        """SetGraphIDtextZeptext"""
        self.graph_id = graph_id
    
    def generate_profiles_from_entities(
        self,
        entities: List[EntityNode],
        use_llm: bool = True,
        progress_callback: Optional[callable] = None,
        graph_id: Optional[str] = None,
        parallel_count: int = 5,
        realtime_output_path: Optional[str] = None,
        output_platform: str = "reddit"
    ) -> List[OasisAgentProfile]:
        """
        textEntityGenerateAgent Profile（textGenerate）
        
        Args:
            entities: EntityList
            use_llm: textLLMGeneratetext
            progress_callback: textFunction (current, total, message)
            graph_id: GraphID，textZeptextGettext
            parallel_count: textGeneratetext，text5
            realtime_output_path: textWritetextFilePath（text，textGeneratetextWritetext）
            output_platform: textFormat ("reddit" text "twitter")
            
        Returns:
            Agent ProfileList
        """
        import concurrent.futures
        from threading import Lock
        
        # Setgraph_idtextZeptext
        if graph_id:
            self.graph_id = graph_id
        
        total = len(entities)
        profiles = [None] * total  # textListtext
        completed_count = [0]  # textListtextUpdate
        lock = Lock()
        
        # textWriteFiletextFunction
        def save_profiles_realtime():
            """textSavetextGeneratetext profiles textFile"""
            if not realtime_output_path:
                return
            
            with lock:
                # FiltertextGeneratetext profiles
                existing_profiles = [p for p in profiles if p is not None]
                if not existing_profiles:
                    return
                
                try:
                    if output_platform == "reddit":
                        # Reddit JSON Format
                        profiles_data = [p.to_reddit_format() for p in existing_profiles]
                        with open(realtime_output_path, 'w', encoding='utf-8') as f:
                            json.dump(profiles_data, f, ensure_ascii=False, indent=2)
                    else:
                        # Twitter CSV Format
                        import csv
                        profiles_data = [p.to_twitter_format() for p in existing_profiles]
                        if profiles_data:
                            fieldnames = list(profiles_data[0].keys())
                            with open(realtime_output_path, 'w', encoding='utf-8', newline='') as f:
                                writer = csv.DictWriter(f, fieldnames=fieldnames)
                                writer.writeheader()
                                writer.writerows(profiles_data)
                except Exception as e:
                    logger.warning(f"textSave profiles Failed: {e}")
        
        def generate_single_profile(idx: int, entity: EntityNode) -> tuple:
            """GeneratetextprofiletextFunction"""
            entity_type = entity.get_entity_type() or "Entity"
            
            try:
                profile = self.generate_profile_from_entity(
                    entity=entity,
                    user_id=idx,
                    use_llm=use_llm
                )
                
                # textGeneratetextLog
                self._print_generated_profile(entity.name, entity_type, profile)
                
                return idx, profile, None
                
            except Exception as e:
                logger.error(f"GenerateEntity {entity.name} textFailed: {str(e)}")
                # Createtextprofile
                fallback_profile = OasisAgentProfile(
                    user_id=idx,
                    user_name=self._generate_username(entity.name),
                    name=entity.name,
                    bio=f"{entity_type}: {entity.name}",
                    persona=entity.summary or f"A participant in social discussions.",
                    source_entity_uuid=entity.uuid,
                    source_entity_type=entity_type,
                )
                return idx, fallback_profile, str(e)
        
        logger.info(f"textGenerate {total} textAgenttext（text: {parallel_count}）...")
        print(f"\n{'='*60}")
        print(f"textGenerateAgenttext - text {total} textEntity，text: {parallel_count}")
        print(f"{'='*60}\n")
        
        # textThreadtextExecute
        with concurrent.futures.ThreadPoolExecutor(max_workers=parallel_count) as executor:
            # CommittextTask
            future_to_entity = {
                executor.submit(generate_single_profile, idx, entity): (idx, entity)
                for idx, entity in enumerate(entities)
            }
            
            # textResult
            for future in concurrent.futures.as_completed(future_to_entity):
                idx, entity = future_to_entity[future]
                entity_type = entity.get_entity_type() or "Entity"
                
                try:
                    result_idx, profile, error = future.result()
                    profiles[result_idx] = profile
                    
                    with lock:
                        completed_count[0] += 1
                        current = completed_count[0]
                    
                    # textWriteFile
                    save_profiles_realtime()
                    
                    if progress_callback:
                        progress_callback(
                            current, 
                            total, 
                            f"textComplete {current}/{total}: {entity.name}（{entity_type}）"
                        )
                    
                    if error:
                        logger.warning(f"[{current}/{total}] {entity.name} text: {error}")
                    else:
                        logger.info(f"[{current}/{total}] SuccessGeneratetext: {entity.name} ({entity_type})")
                        
                except Exception as e:
                    logger.error(f"ProcessEntity {entity.name} textException: {str(e)}")
                    with lock:
                        completed_count[0] += 1
                    profiles[idx] = OasisAgentProfile(
                        user_id=idx,
                        user_name=self._generate_username(entity.name),
                        name=entity.name,
                        bio=f"{entity_type}: {entity.name}",
                        persona=entity.summary or "A participant in social discussions.",
                        source_entity_uuid=entity.uuid,
                        source_entity_type=entity_type,
                    )
                    # textWriteFile（text）
                    save_profiles_realtime()
        
        print(f"\n{'='*60}")
        print(f"textGenerateComplete！textGenerate {len([p for p in profiles if p])} textAgent")
        print(f"{'='*60}\n")
        
        return profiles
    
    def _print_generated_profile(self, entity_name: str, entity_type: str, profile: OasisAgentProfile):
        """textGeneratetext（textContent，text）"""
        separator = "-" * 70
        
        # textContent（text）
        topics_str = ', '.join(profile.interested_topics) if profile.interested_topics else 'text'
        
        output_lines = [
            f"\n{separator}",
            f"[textGenerate] {entity_name} ({entity_type})",
            f"{separator}",
            f"Usertext: {profile.user_name}",
            f"",
            f"【text】",
            f"{profile.bio}",
            f"",
            f"【text】",
            f"{profile.persona}",
            f"",
            f"【textProperty】",
            f"text: {profile.age} | text: {profile.gender} | MBTI: {profile.mbti}",
            f"text: {profile.profession} | text: {profile.country}",
            f"text: {topics_str}",
            separator
        ]
        
        output = "\n".join(output_lines)
        
        # text（text，loggertextContent）
        print(output)
    
    def save_profiles(
        self,
        profiles: List[OasisAgentProfile],
        file_path: str,
        platform: str = "reddit"
    ):
        """
        SaveProfiletextFile（textSelecttextFormat）
        
        OASIStextFormattext：
        - Twitter: CSVFormat
        - Reddit: JSONFormat
        
        Args:
            profiles: ProfileList
            file_path: FilePath
            platform: textType ("reddit" text "twitter")
        """
        if platform == "twitter":
            self._save_twitter_csv(profiles, file_path)
        else:
            self._save_reddit_json(profiles, file_path)
    
    def _save_twitter_csv(self, profiles: List[OasisAgentProfile], file_path: str):
        """
        SaveTwitter ProfiletextCSVFormat（textOASIStext）
        
        OASIS TwittertextCSVField：
        - user_id: UserID（textCSVtext0text）
        - name: Usertext
        - username: textUsertext
        - user_char: text（textLLMtext，textAgenttext）
        - description: text（ShowtextUsertext）
        
        user_char vs description text：
        - user_char: text，LLMtext，textAgenttext
        - description: textShow，textUsertext
        """
        import csv
        
        # textFiletext.csv
        if not file_path.endswith('.csv'):
            file_path = file_path.replace('.json', '.csv')
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # WriteOASIStextTabletext
            headers = ['user_id', 'name', 'username', 'user_char', 'description']
            writer.writerow(headers)
            
            # WriteDatatext
            for idx, profile in enumerate(profiles):
                # user_char: text（bio + persona），textLLMtext
                user_char = profile.bio
                if profile.persona and profile.persona != profile.bio:
                    user_char = f"{profile.bio} {profile.persona}"
                # Processtext（CSVtext）
                user_char = user_char.replace('\n', ' ').replace('\r', ' ')
                
                # description: text，textShow
                description = profile.bio.replace('\n', ' ').replace('\r', ' ')
                
                row = [
                    idx,                    # user_id: text0textID
                    profile.name,           # name: text
                    profile.user_name,      # username: Usertext
                    user_char,              # user_char: text（textLLMtext）
                    description             # description: text（textShow）
                ]
                writer.writerow(row)
        
        logger.info(f"textSave {len(profiles)} textTwitter Profiletext {file_path} (OASIS CSVFormat)")
    
    def _normalize_gender(self, gender: Optional[str]) -> str:
        """
        textgenderFieldtextOASIStextFormat
        
        OASIStext: male, female, other
        """
        if not gender:
            return "other"
        
        gender_lower = gender.lower().strip()
        
        # textMap
        gender_map = {
            "text": "male",
            "text": "female",
            "text": "other",
            "text": "other",
            # text
            "male": "male",
            "female": "female",
            "other": "other",
        }
        
        return gender_map.get(gender_lower, "other")
    
    def _save_reddit_json(self, profiles: List[OasisAgentProfile], file_path: str):
        """
        SaveReddit ProfiletextJSONFormat
        
        text to_reddit_format() textFormat，text OASIS textRead。
        text user_id Field，text OASIS agent_graph.get_agent() text！
        
        textField：
        - user_id: UserID（text，text initial_posts text poster_agent_id）
        - username: Usertext
        - name: ShowName
        - bio: text
        - persona: text
        - age: text（text）
        - gender: "male", "female", text "other"
        - mbti: MBTIType
        - country: text
        """
        data = []
        for idx, profile in enumerate(profiles):
            # text to_reddit_format() textFormat
            item = {
                "user_id": profile.user_id if profile.user_id is not None else idx,  # text：text user_id
                "username": profile.user_name,
                "name": profile.name,
                "bio": profile.bio[:150] if profile.bio else f"{profile.name}",
                "persona": profile.persona or f"{profile.name} is a participant in social discussions.",
                "karma": profile.karma if profile.karma else 1000,
                "created_at": profile.created_at,
                # OASIStextField - text
                "age": profile.age if profile.age else 30,
                "gender": self._normalize_gender(profile.gender),
                "mbti": profile.mbti if profile.mbti else "ISTJ",
                "country": profile.country if profile.country else "text",
            }
            
            # textField
            if profile.profession:
                item["profession"] = profile.profession
            if profile.interested_topics:
                item["interested_topics"] = profile.interested_topics
            
            data.append(item)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"textSave {len(profiles)} textReddit Profiletext {file_path} (JSONFormat，textuser_idField)")
    
    # textMethodtext，text
    def save_profiles_to_json(
        self,
        profiles: List[OasisAgentProfile],
        file_path: str,
        platform: str = "reddit"
    ):
        """[text] text save_profiles() Method"""
        logger.warning("save_profiles_to_jsontext，textsave_profilesMethod")
        self.save_profiles(profiles, file_path, platform)

