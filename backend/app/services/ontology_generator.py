"""
OntologyGenerateService
Interface1：AnalyzetextContent，GeneratetextSimulationtextEntitytextRelationshipTypetext
"""

import json
from typing import Dict, Any, List, Optional
from ..utils.llm_client import LLMClient


# OntologyGeneratetext
ONTOLOGY_SYSTEM_PROMPT = """textGraphOntologyDesigntext。textTasktextAnalyzetextContenttextSimulationtext，Designtext**textSimulation**textEntityTypetextRelationshipType。

**text：textValidtextJSONFormatData，textContent。**

## textTasktext

text**textSimulationtext**。text：
- textEntitytext、text、textInformationtext"text"text"text"
- Entitytext、text、text、text
- textSimulationtextInformationtextPath

text，**Entitytext、text**：

**text**：
- text（text、text、text、text、text）
- text、text（text）
- Grouptext（text、text、NGO、text）
- text、text
- text（text、text、text、text）
- text
- textTable（text、text、text）

**text**：
- Abstractiontext（text"text"、"text"、"Trend"）
- text/text（text"text"、"textUpdatetext"）
- text/text（text"text"、"text"）

## textFormat

textJSONFormat，text：

```json
{
    "entity_types": [
        {
            "name": "EntityTypeName（text，PascalCase）",
            "description": "text（text，text100Char）",
            "attributes": [
                {
                    "name": "Propertytext（text，snake_case）",
                    "type": "text",
                    "description": "Propertytext"
                }
            ],
            "examples": ["ExampleEntity1", "ExampleEntity2"]
        }
    ],
    "edge_types": [
        {
            "name": "RelationshipTypeName（text，UPPER_SNAKE_CASE）",
            "description": "text（text，text100Char）",
            "source_targets": [
                {"source": "textEntityType", "target": "textEntityType"}
            ],
            "attributes": []
        }
    ],
    "analysis_summary": "textContenttextAnalyzeDescription（text）"
}
```

## Designtext（text！）

### 1. EntityTypeDesign - text

**text：text10textEntityType**

**text（textTypetextType）**：

text10textEntityTypetext：

A. **textType（text，textListtext2text）**：
   - `Person`: textType。textTypetext，textClass。
   - `Organization`: textGrouptextType。textGrouptextGrouptextTypetext，textClass。

B. **textType（8text，textContentDesign）**：
   - textRole，DesigntextType
   - text：text，text `Student`, `Professor`, `University`
   - text：text，text `Company`, `CEO`, `Employee`

**textType**：
- text，text"text"、"text"、"text"
- textTypetext，text `Person`
- text，textGrouptext、text `Organization`

**textTypetextDesigntext**：
- textRoleType
- textTypetextEdgetext，text
- description textDescriptiontextTypetextTypetext

### 2. RelationshipTypeDesign

- text：6-10text
- Relationshiptext
- textRelationshiptext source_targets textEntityType

### 3. PropertyDesign

- textEntityType1-3textProperty
- **text**：Propertytext `name`、`uuid`、`group_id`、`created_at`、`summary`（text）
- text：`full_name`, `title`, `role`, `position`, `location`, `description` text

## EntityTypetext

**textClass（text）**：
- Student: text
- Professor: text/text
- Journalist: text
- Celebrity: text/text
- Executive: text
- Official: text
- Lawyer: text
- Doctor: text

**textClass（text）**：
- Person: text（textTypetext）

**GrouptextClass（text）**：
- University: text
- Company: text
- GovernmentAgency: text
- MediaOutlet: text
- Hospital: text
- School: text
- NGO: textGrouptext

**GrouptextClass（text）**：
- Organization: textGrouptext（textTypetext）

## RelationshipTypetext

- WORKS_FOR: text
- STUDIES_AT: text
- AFFILIATED_WITH: text
- REPRESENTS: textTable
- REGULATES: text
- REPORTS_ON: text
- COMMENTS_ON: text
- RESPONDS_TO: text
- SUPPORTS: text
- OPPOSES: text
- COLLABORATES_WITH: text
- COMPETES_WITH: text
"""


class OntologyGenerator:
    """
    OntologyGeneratetext
    AnalyzetextContent，GenerateEntitytextRelationshipTypetext
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()
    
    def generate(
        self,
        document_texts: List[str],
        simulation_requirement: str,
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        GenerateOntologytext
        
        Args:
            document_texts: DocumentationtextList
            simulation_requirement: Simulationtext
            additional_context: text
            
        Returns:
            Ontologytext（entity_types, edge_typestext）
        """
        # textUserMessage
        user_message = self._build_user_message(
            document_texts, 
            simulation_requirement,
            additional_context
        )
        
        messages = [
            {"role": "system", "content": ONTOLOGY_SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
        
        # textLLM
        result = self.llm_client.chat_json(
            messages=messages,
            temperature=0.3,
            max_tokens=4096
        )
        
        # ValidatetextProcessing/Handle
        result = self._validate_and_process(result)
        
        return result
    
    # text LLM text（5text）
    MAX_TEXT_LENGTH_FOR_LLM = 50000
    
    def _build_user_message(
        self,
        document_texts: List[str],
        simulation_requirement: str,
        additional_context: Optional[str]
    ) -> str:
        """textUserMessage"""
        
        # Mergetext
        combined_text = "\n\n---\n\n".join(document_texts)
        original_length = len(combined_text)
        
        # text5text，text（textLLMtextContent，textGraphtext）
        if len(combined_text) > self.MAX_TEXT_LENGTH_FOR_LLM:
            combined_text = combined_text[:self.MAX_TEXT_LENGTH_FOR_LLM]
            combined_text += f"\n\n...(text{original_length}text，text{self.MAX_TEXT_LENGTH_FOR_LLM}textOntologyAnalyze)..."
        
        message = f"""## Simulationtext

{simulation_requirement}

## DocumentationContent

{combined_text}
"""
        
        if additional_context:
            message += f"""
## textDescription

{additional_context}
"""
        
        message += """
textContent，DesigntextSimulationtextEntityTypetextRelationshipType。

**text**：
1. text10textEntityType
2. text2textType：Person（text）text Organization（Grouptext）
3. text8textContentDesigntextType
4. textEntityTypetext，textAbstractiontext
5. Propertytext name、uuid、group_id text，text full_name、org_name text
"""
        
        return message
    
    def _validate_and_process(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """ValidatetextProcessing/HandleResult"""
        
        # textFieldtext
        if "entity_types" not in result:
            result["entity_types"] = []
        if "edge_types" not in result:
            result["edge_types"] = []
        if "analysis_summary" not in result:
            result["analysis_summary"] = ""
        
        # ValidateEntityType
        for entity in result["entity_types"]:
            if "attributes" not in entity:
                entity["attributes"] = []
            if "examples" not in entity:
                entity["examples"] = []
            # textdescriptiontext100Char
            if len(entity.get("description", "")) > 100:
                entity["description"] = entity["description"][:97] + "..."
        
        # ValidateRelationshipType
        for edge in result["edge_types"]:
            if "source_targets" not in edge:
                edge["source_targets"] = []
            if "attributes" not in edge:
                edge["attributes"] = []
            if len(edge.get("description", "")) > 100:
                edge["description"] = edge["description"][:97] + "..."
        
        # Zep API text：text 10 textEntityType，text 10 textEdgeType
        MAX_ENTITY_TYPES = 10
        MAX_EDGE_TYPES = 10
        
        # textTypetext
        person_fallback = {
            "name": "Person",
            "description": "Any individual person not fitting other specific person types.",
            "attributes": [
                {"name": "full_name", "type": "text", "description": "Full name of the person"},
                {"name": "role", "type": "text", "description": "Role or occupation"}
            ],
            "examples": ["ordinary citizen", "anonymous netizen"]
        }
        
        organization_fallback = {
            "name": "Organization",
            "description": "Any organization not fitting other specific organization types.",
            "attributes": [
                {"name": "org_name", "type": "text", "description": "Name of the organization"},
                {"name": "org_type", "type": "text", "description": "Type of organization"}
            ],
            "examples": ["small business", "community group"]
        }
        
        # ChecktextType
        entity_names = {e["name"] for e in result["entity_types"]}
        has_person = "Person" in entity_names
        has_organization = "Organization" in entity_names
        
        # textAddtextType
        fallbacks_to_add = []
        if not has_person:
            fallbacks_to_add.append(person_fallback)
        if not has_organization:
            fallbacks_to_add.append(organization_fallback)
        
        if fallbacks_to_add:
            current_count = len(result["entity_types"])
            needed_slots = len(fallbacks_to_add)
            
            # textAddtext 10 text，textRemovetextType
            if current_count + needed_slots > MAX_ENTITY_TYPES:
                # textRemovetext
                to_remove = current_count + needed_slots - MAX_ENTITY_TYPES
                # textRemove（textType）
                result["entity_types"] = result["entity_types"][:-to_remove]
            
            # AddtextType
            result["entity_types"].extend(fallbacks_to_add)
        
        # text（text）
        if len(result["entity_types"]) > MAX_ENTITY_TYPES:
            result["entity_types"] = result["entity_types"][:MAX_ENTITY_TYPES]
        
        if len(result["edge_types"]) > MAX_EDGE_TYPES:
            result["edge_types"] = result["edge_types"][:MAX_EDGE_TYPES]
        
        return result
    
    def generate_python_code(self, ontology: Dict[str, Any]) -> str:
        """
        textOntologytextConverttextPythontext（Classtextontology.py）
        
        Args:
            ontology: Ontologytext
            
        Returns:
            PythontextChartext
        """
        code_lines = [
            '"""',
            'textEntityTypetext',
            'textMiroFishtextGenerate，textSimulation',
            '"""',
            '',
            'from pydantic import Field',
            'from zep_cloud.external_clients.ontology import EntityModel, EntityText, EdgeModel',
            '',
            '',
            '# ============== EntityTypetext ==============',
            '',
        ]
        
        # GenerateEntityType
        for entity in ontology.get("entity_types", []):
            name = entity["name"]
            desc = entity.get("description", f"A {name} entity.")
            
            code_lines.append(f'class {name}(EntityModel):')
            code_lines.append(f'    """{desc}"""')
            
            attrs = entity.get("attributes", [])
            if attrs:
                for attr in attrs:
                    attr_name = attr["name"]
                    attr_desc = attr.get("description", attr_name)
                    code_lines.append(f'    {attr_name}: EntityText = Field(')
                    code_lines.append(f'        description="{attr_desc}",')
                    code_lines.append(f'        default=None')
                    code_lines.append(f'    )')
            else:
                code_lines.append('    pass')
            
            code_lines.append('')
            code_lines.append('')
        
        code_lines.append('# ============== RelationshipTypetext ==============')
        code_lines.append('')
        
        # GenerateRelationshipType
        for edge in ontology.get("edge_types", []):
            name = edge["name"]
            # ConverttextPascalCaseClasstext
            class_name = ''.join(word.capitalize() for word in name.split('_'))
            desc = edge.get("description", f"A {name} relationship.")
            
            code_lines.append(f'class {class_name}(EdgeModel):')
            code_lines.append(f'    """{desc}"""')
            
            attrs = edge.get("attributes", [])
            if attrs:
                for attr in attrs:
                    attr_name = attr["name"]
                    attr_desc = attr.get("description", attr_name)
                    code_lines.append(f'    {attr_name}: EntityText = Field(')
                    code_lines.append(f'        description="{attr_desc}",')
                    code_lines.append(f'        default=None')
                    code_lines.append(f'    )')
            else:
                code_lines.append('    pass')
            
            code_lines.append('')
            code_lines.append('')
        
        # GenerateTypeDictionary
        code_lines.append('# ============== TypeConfig ==============')
        code_lines.append('')
        code_lines.append('ENTITY_TYPES = {')
        for entity in ontology.get("entity_types", []):
            name = entity["name"]
            code_lines.append(f'    "{name}": {name},')
        code_lines.append('}')
        code_lines.append('')
        code_lines.append('EDGE_TYPES = {')
        for edge in ontology.get("edge_types", []):
            name = edge["name"]
            class_name = ''.join(word.capitalize() for word in name.split('_'))
            code_lines.append(f'    "{name}": {class_name},')
        code_lines.append('}')
        code_lines.append('')
        
        # GenerateEdgetextsource_targetsMap
        code_lines.append('EDGE_SOURCE_TARGETS = {')
        for edge in ontology.get("edge_types", []):
            name = edge["name"]
            source_targets = edge.get("source_targets", [])
            if source_targets:
                st_list = ', '.join([
                    f'{{"source": "{st.get("source", "Entity")}", "target": "{st.get("target", "Entity")}"}}'
                    for st in source_targets
                ])
                code_lines.append(f'    "{name}": [{st_list}],')
        code_lines.append('}')
        
        return '\n'.join(code_lines)

