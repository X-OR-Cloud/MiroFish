"""
Report AgentService
textLangChain + ZepImplementationReACTPatterntextSimulationReportGenerate

Function：
1. textSimulationtextZepGraphInformationGenerateReport
2. textDirectorytext，textGenerate
3. textReACTtextPattern
4. textUsertext，textTool
"""

import os
import json
import time
import re
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from ..config import Config
from ..utils.llm_client import LLMClient
from ..utils.logger import get_logger
from .zep_tools import (
    ZepToolsService, 
    SearchResult, 
    InsightForgeResult, 
    PanoramaResult,
    InterviewResult
)

logger = get_logger('mirofish.report_agent')


class ReportLogger:
    """
    Report Agent textLogRecordtext
    
    textReportFiletextGenerate agent_log.jsonl File，Recordtext。
    text JSON Object，textTimestamp、textType、textContenttext。
    """
    
    def __init__(self, report_id: str):
        """
        InitializeLogRecordtext
        
        Args:
            report_id: ReportID，textLogFilePath
        """
        self.report_id = report_id
        self.log_file_path = os.path.join(
            Config.UPLOAD_FOLDER, 'reports', report_id, 'agent_log.jsonl'
        )
        self.start_time = datetime.now()
        self._ensure_log_file()
    
    def _ensure_log_file(self):
        """textLogFiletextDirectorytext"""
        log_dir = os.path.dirname(self.log_file_path)
        os.makedirs(log_dir, exist_ok=True)
    
    def _get_elapsed_time(self) -> float:
        """GettextNowtext（text）"""
        return (datetime.now() - self.start_time).total_seconds()
    
    def log(
        self, 
        action: str, 
        stage: str,
        details: Dict[str, Any],
        section_title: str = None,
        section_index: int = None
    ):
        """
        RecordtextLog
        
        Args:
            action: textType，text 'start', 'tool_call', 'llm_response', 'section_complete' text
            stage: textStage，text 'planning', 'generating', 'completed'
            details: textContentDict，text
            section_title: text（text）
            section_index: textIndex（text）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": round(self._get_elapsed_time(), 2),
            "report_id": self.report_id,
            "action": action,
            "stage": stage,
            "section_title": section_title,
            "section_index": section_index,
            "details": details
        }
        
        # textWrite JSONL File
        with open(self.log_file_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def log_start(self, simulation_id: str, graph_id: str, simulation_requirement: str):
        """RecordReportGeneratetext"""
        self.log(
            action="report_start",
            stage="pending",
            details={
                "simulation_id": simulation_id,
                "graph_id": graph_id,
                "simulation_requirement": simulation_requirement,
                "message": "ReportGenerateTasktext"
            }
        )
    
    def log_planning_start(self):
        """Recordtext"""
        self.log(
            action="planning_start",
            stage="planning",
            details={"message": "textReporttext"}
        )
    
    def log_planning_context(self, context: Dict[str, Any]):
        """RecordtextGettextInformation"""
        self.log(
            action="planning_context",
            stage="planning",
            details={
                "message": "GetSimulationtextInformation",
                "context": context
            }
        )
    
    def log_planning_complete(self, outline_dict: Dict[str, Any]):
        """RecordtextComplete"""
        self.log(
            action="planning_complete",
            stage="planning",
            details={
                "message": "textComplete",
                "outline": outline_dict
            }
        )
    
    def log_section_start(self, section_title: str, section_index: int):
        """RecordtextGeneratetext"""
        self.log(
            action="section_start",
            stage="generating",
            section_title=section_title,
            section_index=section_index,
            details={"message": f"textGeneratetext: {section_title}"}
        )
    
    def log_react_thought(self, section_title: str, section_index: int, iteration: int, thought: str):
        """Record ReACT text"""
        self.log(
            action="react_thought",
            stage="generating",
            section_title=section_title,
            section_index=section_index,
            details={
                "iteration": iteration,
                "thought": thought,
                "message": f"ReACT text{iteration}text"
            }
        )
    
    def log_tool_call(
        self, 
        section_title: str, 
        section_index: int,
        tool_name: str, 
        parameters: Dict[str, Any],
        iteration: int
    ):
        """RecordTooltext"""
        self.log(
            action="tool_call",
            stage="generating",
            section_title=section_title,
            section_index=section_index,
            details={
                "iteration": iteration,
                "tool_name": tool_name,
                "parameters": parameters,
                "message": f"textTool: {tool_name}"
            }
        )
    
    def log_tool_result(
        self,
        section_title: str,
        section_index: int,
        tool_name: str,
        result: str,
        iteration: int
    ):
        """RecordTooltextResult（textContent，text）"""
        self.log(
            action="tool_result",
            stage="generating",
            section_title=section_title,
            section_index=section_index,
            details={
                "iteration": iteration,
                "tool_name": tool_name,
                "result": result,  # textResult，text
                "result_length": len(result),
                "message": f"Tool {tool_name} ReturnsResult"
            }
        )
    
    def log_llm_response(
        self,
        section_title: str,
        section_index: int,
        response: str,
        iteration: int,
        has_tool_calls: bool,
        has_final_answer: bool
    ):
        """Record LLM Response（textContent，text）"""
        self.log(
            action="llm_response",
            stage="generating",
            section_title=section_title,
            section_index=section_index,
            details={
                "iteration": iteration,
                "response": response,  # textResponse，text
                "response_length": len(response),
                "has_tool_calls": has_tool_calls,
                "has_final_answer": has_final_answer,
                "message": f"LLM Response (Tooltext: {has_tool_calls}, text: {has_final_answer})"
            }
        )
    
    def log_section_content(
        self,
        section_title: str,
        section_index: int,
        content: str,
        tool_calls_count: int
    ):
        """RecordtextContentGenerateComplete（textRecordContent，textTabletextComplete）"""
        self.log(
            action="section_content",
            stage="generating",
            section_title=section_title,
            section_index=section_index,
            details={
                "content": content,  # textContent，text
                "content_length": len(content),
                "tool_calls_count": tool_calls_count,
                "message": f"text {section_title} ContentGenerateComplete"
            }
        )
    
    def log_section_full_complete(
        self,
        section_title: str,
        section_index: int,
        full_content: str
    ):
        """
        RecordtextGenerateComplete

        textLogtextComplete，textGettextContent
        """
        self.log(
            action="section_complete",
            stage="generating",
            section_title=section_title,
            section_index=section_index,
            details={
                "content": full_content,
                "content_length": len(full_content),
                "message": f"text {section_title} GenerateComplete"
            }
        )
    
    def log_report_complete(self, total_sections: int, total_time_seconds: float):
        """RecordReportGenerateComplete"""
        self.log(
            action="report_complete",
            stage="completed",
            details={
                "total_sections": total_sections,
                "total_time_seconds": round(total_time_seconds, 2),
                "message": "ReportGenerateComplete"
            }
        )
    
    def log_error(self, error_message: str, stage: str, section_title: str = None):
        """RecordError"""
        self.log(
            action="error",
            stage=stage,
            section_title=section_title,
            section_index=None,
            details={
                "error": error_message,
                "message": f"textError: {error_message}"
            }
        )


class ReportConsoleLogger:
    """
    Report Agent textLogRecordtext
    
    textLog（INFO、WARNINGtext）WriteReportFiletext console_log.txt File。
    textLogtext agent_log.jsonl text，textFormattext。
    """
    
    def __init__(self, report_id: str):
        """
        InitializetextLogRecordtext
        
        Args:
            report_id: ReportID，textLogFilePath
        """
        self.report_id = report_id
        self.log_file_path = os.path.join(
            Config.UPLOAD_FOLDER, 'reports', report_id, 'console_log.txt'
        )
        self._ensure_log_file()
        self._file_handler = None
        self._setup_file_handler()
    
    def _ensure_log_file(self):
        """textLogFiletextDirectorytext"""
        log_dir = os.path.dirname(self.log_file_path)
        os.makedirs(log_dir, exist_ok=True)
    
    def _setup_file_handler(self):
        """SetFileProcesstext，textLogtextWriteFile"""
        import logging
        
        # CreateFileProcesstext
        self._file_handler = logging.FileHandler(
            self.log_file_path,
            mode='a',
            encoding='utf-8'
        )
        self._file_handler.setLevel(logging.INFO)
        
        # textFormat
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        self._file_handler.setFormatter(formatter)
        
        # Addtext report_agent text logger
        loggers_to_attach = [
            'mirofish.report_agent',
            'mirofish.zep_tools',
        ]
        
        for logger_name in loggers_to_attach:
            target_logger = logging.getLogger(logger_name)
            # textAdd
            if self._file_handler not in target_logger.handlers:
                target_logger.addHandler(self._file_handler)
    
    def close(self):
        """CloseFileProcesstext logger textRemove"""
        import logging
        
        if self._file_handler:
            loggers_to_detach = [
                'mirofish.report_agent',
                'mirofish.zep_tools',
            ]
            
            for logger_name in loggers_to_detach:
                target_logger = logging.getLogger(logger_name)
                if self._file_handler in target_logger.handlers:
                    target_logger.removeHandler(self._file_handler)
            
            self._file_handler.close()
            self._file_handler = None
    
    def __del__(self):
        """textCloseFileProcesstext"""
        self.close()


class ReportStatus(str, Enum):
    """ReportStatus"""
    PENDING = "pending"
    PLANNING = "planning"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ReportSection:
    """Reporttext"""
    title: str
    content: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "content": self.content
        }

    def to_markdown(self, level: int = 2) -> str:
        """ConverttextMarkdownFormat"""
        md = f"{'#' * level} {self.title}\n\n"
        if self.content:
            md += f"{self.content}\n\n"
        return md


@dataclass
class ReportOutline:
    """Reporttext"""
    title: str
    summary: str
    sections: List[ReportSection]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "summary": self.summary,
            "sections": [s.to_dict() for s in self.sections]
        }
    
    def to_markdown(self) -> str:
        """ConverttextMarkdownFormat"""
        md = f"# {self.title}\n\n"
        md += f"> {self.summary}\n\n"
        for section in self.sections:
            md += section.to_markdown()
        return md


@dataclass
class Report:
    """textReport"""
    report_id: str
    simulation_id: str
    graph_id: str
    simulation_requirement: str
    status: ReportStatus
    outline: Optional[ReportOutline] = None
    markdown_content: str = ""
    created_at: str = ""
    completed_at: str = ""
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "simulation_id": self.simulation_id,
            "graph_id": self.graph_id,
            "simulation_requirement": self.simulation_requirement,
            "status": self.status.value,
            "outline": self.outline.to_dict() if self.outline else None,
            "markdown_content": self.markdown_content,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "error": self.error
        }


# ═══════════════════════════════════════════════════════════════
# Prompt text
# ═══════════════════════════════════════════════════════════════

# ── Tooltext ──

TOOL_DESC_INSIGHT_FORGE = """\
【text - textTool】
textFunction，textAnalyzeDesign。text：
1. textIssuetextIssue
2. textSimulationGraphtextInformation
3. textSearch、EntityAnalyze、RelationshiptextTracetextResult
4. Returnstext、textContent

【text】
- textAnalyzetext
- text
- textGettextReporttext

【ReturnsContent】
- text（text）
- textEntitytext
- RelationshiptextAnalyze"""

TOOL_DESC_PANORAMA_SEARCH = """\
【textSearch - GettextGraph】
textTooltextGetSimulationResulttext，text。text：
1. GettextNodetextRelationship
2. textValidtext/Expiretext
3. Helptext

【text】
- text
- textStagetext
- textGettextEntitytextRelationshipInformation

【ReturnsContent】
- textValidtext（SimulationtextResult）
- text/Expiretext（textRecord）
- textEntity"""

TOOL_DESC_QUICK_SEARCH = """\
【textSearch - text】
textTool，text、textInformationQuery。

【text】
- textQuerytextInformation
- textValidatetext
- textInformationtext

【ReturnsContent】
- textQuerytextList"""

TOOL_DESC_INTERVIEW_AGENTS = """\
【text - textAgenttext（text）】
textOASISSimulationtextAPI，textRuntextSimulationAgenttext！
textLLMSimulation，textInterfaceGetSimulationAgenttext。
textTwittertextReddittext，Gettext。

Functiontext：
1. textReadtextFile，textSimulationAgent
2. textSelecttextAgent（text、text、text）
3. textGeneratetextAccesstext
4. text /api/simulation/interview/batch Interfacetext
5. textResult，textAnalyze

【text】
- textNevertextRoletext（text？text？text？）
- text
- textGetSimulationAgenttext（textOASISSimulationtext）
- textReporttext，text"text"

【ReturnsContent】
- textAgenttextInformation
- textAgenttextTwittertextReddittext
- text（text）
- textDigesttext

【text】textOASISSimulationtextRuntextFunction！"""

# ── text prompt ──

PLAN_SYSTEM_PROMPT = """\
text「textReport」text，textSimulationtext「text」——textSimulationtextAgenttext、text。

【text】
textSimulationtext，text「Simulationtext」textVariable。SimulationtextResult，text。text"textData"，text"text"。

【textTask】
text「textReport」，text：
1. text，text？
2. textClassAgent（text）text？
3. textSimulationtextTrendtext？

【Reporttext】
- ✅ textSimulationtextReport，text"text，text"
- ✅ textResult：text、text、text、text
- ✅ SimulationtextAgenttext
- ❌ textAnalyze
- ❌ text

【text】
- text2text，text5text
- text，textContent
- Contenttext，text
- textResulttextDesign

textJSONFormattextReporttext，Formattext：
{
    "title": "Reporttext",
    "summary": "ReportDigest（text）",
    "sections": [
        {
            "title": "text",
            "description": "textContenttext"
        }
    ]
}

text：sectionstextGrouptext2text，text5text！"""

PLAN_USER_PROMPT_TEMPLATE = """\
【text】
textSimulationtextVariable（Simulationtext）：{simulation_requirement}

【Simulationtext】
- textSimulationtextEntitytext: {total_nodes}
- EntitytextRelationshiptext: {total_edges}
- EntityTypetext: {entity_types}
- textAgenttext: {total_entities}

【Simulationtext】
{related_facts_json}

text「text」text：
1. text，textStatus？
2. textClasstext（Agent）text？
3. textSimulationtextTrend？

textResult，DesigntextReporttext。

【textReminder】Reporttext：text2text，text5text，Contenttext。"""

# ── textGenerate prompt ──

SECTION_SYSTEM_PROMPT_TEMPLATE = """\
text「textReport」text，textReporttext。

Reporttext: {report_title}
ReportDigest: {report_summary}
text（Simulationtext）: {simulation_requirement}

text: {section_title}

═══════════════════════════════════════════════════════════════
【text】
═══════════════════════════════════════════════════════════════

Simulationtext。textSimulationtext（Simulationtext），
SimulationtextAgenttext，text。

textTasktext：
- text，text
- textClasstext（Agent）text
- textTrend、text

❌ textAnalyze
✅ text"text"——SimulationResulttext

═══════════════════════════════════════════════════════════════
【text - text】
═══════════════════════════════════════════════════════════════

1. 【textTooltextSimulationtext】
   - text「text」text
   - textContenttextSimulationtextAgenttext
   - textReportContent
   - text3textTool（text5text）textSimulationtext，textTabletext

2. 【textAgenttext】
   - Agenttext
   - textReporttextFormattext，text：
     > "textClasstextTabletext：textContent..."
   - textSimulationtext

3. 【text - textContenttextReporttext】
   - ToolReturnstextContenttextTabletext
   - textSimulationtext，Reporttext
   - textToolReturnstextContenttext，textWriteReport
   - text，textTabletext
   - text（> Format）textContent

4. 【textResult】
   - ReportContenttextSimulationtextTabletextSimulationResult
   - textAddSimulationtextInformation
   - textInformationtext，textDescription

═══════════════════════════════════════════════════════════════
【⚠️ Formattext - text！】
═══════════════════════════════════════════════════════════════

【text = textContenttext】
- textReporttext
- ❌ text Markdown text（#、##、###、#### text）
- ❌ textContenttextAddtext
- ✅ textAdd，textContent
- ✅ text**text**、text、text、ListtextGrouptextContent，text

【textExample】
```
textAnalyzetext。textSimulationDatatextAnalyze，text...

**textStage**

text，textInformationtextFunction：

> "text68%textClasstext..."

**textZoom InStage**

textZoom Intext：

- text
- text
```

【ErrorExample】
```
## ExecuteDigest          ← Error！textAddtext
### text、textStage     ← Error！text###text
#### 1.1 textAnalyze   ← Error！text####text

textAnalyzetext...
```

═══════════════════════════════════════════════════════════════
【textTool】（text3-5text）
═══════════════════════════════════════════════════════════════

{tools_description}

【Tooltext - textTool，text】
- insight_forge: textAnalyze，textIssuetextRelationship
- panorama_search: textSearch，text、text
- quick_search: textValidatetextInformationtext
- interview_agents: textSimulationAgent，GettextRoletext

═══════════════════════════════════════════════════════════════
【text】
═══════════════════════════════════════════════════════════════

text（text）：

OptionsA - textTool：
text，textFormattextTool：
<tool_call>
{{"name": "ToolName", "parameters": {{"Parameterstext": "Parameterstext"}}}}
</tool_call>
textExecuteTooltextResultReturnstext。textToolReturnsResult。

OptionsB - textContent：
textToolGettextInformation，text "Final Answer:" textContent。

⚠️ text：
- textTooltext Final Answer
- textToolReturnsResult（Observation），textToolResulttext
- textTool

═══════════════════════════════════════════════════════════════
【textContenttext】
═══════════════════════════════════════════════════════════════

1. ContenttextTooltextSimulationData
2. textSimulationtext
3. textMarkdownFormat（text）：
   - text **text** text（text）
   - textList（-text1.2.3.）Grouptext
   - text
   - ❌ text #、##、###、#### text
4. 【textFormattext - text】
   text，text，text：

   ✅ textFormat：
   ```
   textContent。

   > "textPatterntext。"

   text。
   ```

   ❌ ErrorFormat：
   ```
   textContent。> "textPattern..." text...
   ```
5. text
6. 【text】textCompletetextContent，textInformation
7. 【text】textAddtext！text**text**text"""

SECTION_USER_PROMPT_TEMPLATE = """\
textCompletetextContent（text，text）：
{previous_content}

═══════════════════════════════════════════════════════════════
【textTask】text: {section_title}
═══════════════════════════════════════════════════════════════

【textReminder】
1. textCompletetext，textContent！
2. textToolGetSimulationData
3. textTool，text
4. ReportContenttextResult，text

【⚠️ FormatWarning - text】
- ❌ text（#、##、###、####text）
- ❌ text"{section_title}"text
- ✅ textAdd
- ✅ text，text**text**text

text：
1. text（Thought）textInformation
2. textTool（Action）GetSimulationData
3. textInformationtext Final Answer（text，text）"""

# ── ReACT textMessagetext ──

REACT_OBSERVATION_TEMPLATE = """\
Observation（textResult）:

═══ Tool {tool_name} Returns ═══
{result}

═══════════════════════════════════════════════════════════════
textTool {tool_calls_count}/{max_tool_calls} text（text: {used_tools_str}）{unused_hint}
- textInformationtext：text "Final Answer:" textContent（text）
- textInformation：textToolContinuetext
═══════════════════════════════════════════════════════════════"""

REACT_INSUFFICIENT_TOOLS_MSG = (
    "【text】text{tool_calls_count}textTool，text{min_tool_calls}text。"
    "textToolGettextSimulationData，text Final Answer。{unused_hint}"
)

REACT_INSUFFICIENT_TOOLS_MSG_ALT = (
    "text {tool_calls_count} textTool，text {min_tool_calls} text。"
    "textToolGetSimulationData。{unused_hint}"
)

REACT_TOOL_LIMIT_MSG = (
    "Tooltext（{tool_calls_count}/{max_tool_calls}），textTool。"
    'textGettextInformation，text "Final Answer:" textContent。'
)

REACT_UNUSED_TOOLS_HINT = "\n💡 text: {unused_list}，textToolGettextInformation"

REACT_FORCE_FINAL_MSG = "textTooltext，text Final Answer: textGeneratetextContent。"

# ── Chat prompt ──

CHAT_SYSTEM_PROMPT_TEMPLATE = """\
textSimulationtext。

【text】
text: {simulation_requirement}

【textGeneratetextAnalyzeReport】
{report_content}

【text】
1. textReportContenttextIssue
2. textIssue，text
3. textReportContenttext，textTooltextData
4. text、text、text

【textTool】（text，text1-2text）
{tools_description}

【TooltextFormat】
<tool_call>
{{"name": "ToolName", "parameters": {{"Parameterstext": "Parameterstext"}}}}
</tool_call>

【text】
- text，text
- text > FormattextContent
- text，text"""

CHAT_OBSERVATION_SUFFIX = "\n\ntextIssue。"


# ═══════════════════════════════════════════════════════════════
# ReportAgent textClass
# ═══════════════════════════════════════════════════════════════


class ReportAgent:
    """
    Report Agent - SimulationReportGenerateAgent

    textReACT（Reasoning + Acting）Pattern：
    1. textStage：AnalyzeSimulationtext，textReportDirectorytext
    2. GenerateStage：textGenerateContent，textToolGetInformation
    3. textStage：CheckContenttext
    """
    
    # textTooltext（text）
    MAX_TOOL_CALLS_PER_SECTION = 5
    
    # text
    MAX_REFLECTION_ROUNDS = 3
    
    # textTooltext
    MAX_TOOL_CALLS_PER_CHAT = 2
    
    def __init__(
        self, 
        graph_id: str,
        simulation_id: str,
        simulation_requirement: str,
        llm_client: Optional[LLMClient] = None,
        zep_tools: Optional[ZepToolsService] = None
    ):
        """
        InitializeReport Agent
        
        Args:
            graph_id: GraphID
            simulation_id: SimulationID
            simulation_requirement: Simulationtext
            llm_client: LLMClient（text）
            zep_tools: ZepToolService（text）
        """
        self.graph_id = graph_id
        self.simulation_id = simulation_id
        self.simulation_requirement = simulation_requirement
        
        self.llm = llm_client or LLMClient()
        self.zep_tools = zep_tools or ZepToolsService()
        
        # Tooltext
        self.tools = self._define_tools()
        
        # LogRecordtext（text generate_report textInitialize）
        self.report_logger: Optional[ReportLogger] = None
        # textLogRecordtext（text generate_report textInitialize）
        self.console_logger: Optional[ReportConsoleLogger] = None
        
        logger.info(f"ReportAgent InitializeComplete: graph_id={graph_id}, simulation_id={simulation_id}")
    
    def _define_tools(self) -> Dict[str, Dict[str, Any]]:
        """textTool"""
        return {
            "insight_forge": {
                "name": "insight_forge",
                "description": TOOL_DESC_INSIGHT_FORGE,
                "parameters": {
                    "query": "textAnalyzetextIssuetext",
                    "report_context": "textReporttext（text，textGeneratetextIssue）"
                }
            },
            "panorama_search": {
                "name": "panorama_search",
                "description": TOOL_DESC_PANORAMA_SEARCH,
                "parameters": {
                    "query": "SearchQuery，textSort",
                    "include_expired": "textExpire/textContent（textTrue）"
                }
            },
            "quick_search": {
                "name": "quick_search",
                "description": TOOL_DESC_QUICK_SEARCH,
                "parameters": {
                    "query": "SearchQueryChartext",
                    "limit": "ReturnsResulttext（text，text10）"
                }
            },
            "interview_agents": {
                "name": "interview_agents",
                "description": TOOL_DESC_INTERVIEW_AGENTS,
                "parameters": {
                    "interview_topic": "text（text：'text'）",
                    "max_agents": "textAgenttext（text，text5，text10）"
                }
            }
        }
    
    def _execute_tool(self, tool_name: str, parameters: Dict[str, Any], report_context: str = "") -> str:
        """
        ExecuteTooltext
        
        Args:
            tool_name: ToolName
            parameters: ToolParameters
            report_context: Reporttext（textInsightForge）
            
        Returns:
            ToolExecuteResult（textFormat）
        """
        logger.info(f"ExecuteTool: {tool_name}, Parameters: {parameters}")
        
        try:
            if tool_name == "insight_forge":
                query = parameters.get("query", "")
                ctx = parameters.get("report_context", "") or report_context
                result = self.zep_tools.insight_forge(
                    graph_id=self.graph_id,
                    query=query,
                    simulation_requirement=self.simulation_requirement,
                    report_context=ctx
                )
                return result.to_text()
            
            elif tool_name == "panorama_search":
                # textSearch - Gettext
                query = parameters.get("query", "")
                include_expired = parameters.get("include_expired", True)
                if isinstance(include_expired, str):
                    include_expired = include_expired.lower() in ['true', '1', 'yes']
                result = self.zep_tools.panorama_search(
                    graph_id=self.graph_id,
                    query=query,
                    include_expired=include_expired
                )
                return result.to_text()
            
            elif tool_name == "quick_search":
                # textSearch - text
                query = parameters.get("query", "")
                limit = parameters.get("limit", 10)
                if isinstance(limit, str):
                    limit = int(limit)
                result = self.zep_tools.quick_search(
                    graph_id=self.graph_id,
                    query=query,
                    limit=limit
                )
                return result.to_text()
            
            elif tool_name == "interview_agents":
                # text - textOASIStextAPIGetSimulationAgenttext（text）
                interview_topic = parameters.get("interview_topic", parameters.get("query", ""))
                max_agents = parameters.get("max_agents", 5)
                if isinstance(max_agents, str):
                    max_agents = int(max_agents)
                max_agents = min(max_agents, 10)
                result = self.zep_tools.interview_agents(
                    simulation_id=self.simulation_id,
                    interview_requirement=interview_topic,
                    simulation_requirement=self.simulation_requirement,
                    max_agents=max_agents
                )
                return result.to_text()
            
            # ========== textTool（textTool） ==========
            
            elif tool_name == "search_graph":
                # text quick_search
                logger.info("search_graph text quick_search")
                return self._execute_tool("quick_search", parameters, report_context)
            
            elif tool_name == "get_graph_statistics":
                result = self.zep_tools.get_graph_statistics(self.graph_id)
                return json.dumps(result, ensure_ascii=False, indent=2)
            
            elif tool_name == "get_entity_summary":
                entity_name = parameters.get("entity_name", "")
                result = self.zep_tools.get_entity_summary(
                    graph_id=self.graph_id,
                    entity_name=entity_name
                )
                return json.dumps(result, ensure_ascii=False, indent=2)
            
            elif tool_name == "get_simulation_context":
                # text insight_forge，text
                logger.info("get_simulation_context text insight_forge")
                query = parameters.get("query", self.simulation_requirement)
                return self._execute_tool("insight_forge", {"query": query}, report_context)
            
            elif tool_name == "get_entities_by_type":
                entity_type = parameters.get("entity_type", "")
                nodes = self.zep_tools.get_entities_by_type(
                    graph_id=self.graph_id,
                    entity_type=entity_type
                )
                result = [n.to_dict() for n in nodes]
                return json.dumps(result, ensure_ascii=False, indent=2)
            
            else:
                return f"textTool: {tool_name}。textTooltext: insight_forge, panorama_search, quick_search"
                
        except Exception as e:
            logger.error(f"ToolExecuteFailed: {tool_name}, Error: {str(e)}")
            return f"ToolExecuteFailed: {str(e)}"
    
    # textToolNameSet，text JSON textParsetext
    VALID_TOOL_NAMES = {"insight_forge", "panorama_search", "quick_search", "interview_agents"}

    def _parse_tool_calls(self, response: str) -> List[Dict[str, Any]]:
        """
        textLLMResponsetextParseTooltext

        textFormat（text）：
        1. <tool_call>{"name": "tool_name", "parameters": {...}}</tool_call>
        2. text JSON（ResponsetextTooltext JSON）
        """
        tool_calls = []

        # Format1: XMLtext（textFormat）
        xml_pattern = r'<tool_call>\s*(\{.*?\})\s*</tool_call>'
        for match in re.finditer(xml_pattern, response, re.DOTALL):
            try:
                call_data = json.loads(match.group(1))
                tool_calls.append(call_data)
            except json.JSONDecodeError:
                pass

        if tool_calls:
            return tool_calls

        # Format2: text - LLM text JSON（text <tool_call> Tag）
        # textFormat1text，text JSON
        stripped = response.strip()
        if stripped.startswith('{') and stripped.endswith('}'):
            try:
                call_data = json.loads(stripped)
                if self._is_valid_tool_call(call_data):
                    tool_calls.append(call_data)
                    return tool_calls
            except json.JSONDecodeError:
                pass

        # Responsetext + text JSON，text JSON Object
        json_pattern = r'(\{"(?:name|tool)"\s*:.*?\})\s*$'
        match = re.search(json_pattern, stripped, re.DOTALL)
        if match:
            try:
                call_data = json.loads(match.group(1))
                if self._is_valid_tool_call(call_data):
                    tool_calls.append(call_data)
            except json.JSONDecodeError:
                pass

        return tool_calls

    def _is_valid_tool_call(self, data: dict) -> bool:
        """textParsetext JSON textTooltext"""
        # text {"name": ..., "parameters": ...} text {"tool": ..., "params": ...} text
        tool_name = data.get("name") or data.get("tool")
        if tool_name and tool_name in self.VALID_TOOL_NAMES:
            # text name / parameters
            if "tool" in data:
                data["name"] = data.pop("tool")
            if "params" in data and "parameters" not in data:
                data["parameters"] = data.pop("params")
            return True
        return False
    
    def _get_tools_description(self) -> str:
        """GenerateTooltext"""
        desc_parts = ["textTool："]
        for name, tool in self.tools.items():
            params_desc = ", ".join([f"{k}: {v}" for k, v in tool["parameters"].items()])
            desc_parts.append(f"- {name}: {tool['description']}")
            if params_desc:
                desc_parts.append(f"  Parameters: {params_desc}")
        return "\n".join(desc_parts)
    
    def plan_outline(
        self, 
        progress_callback: Optional[Callable] = None
    ) -> ReportOutline:
        """
        textReporttext
        
        textLLMAnalyzeSimulationtext，textReporttextDirectorytext
        
        Args:
            progress_callback: textFunction
            
        Returns:
            ReportOutline: Reporttext
        """
        logger.info("textReporttext...")
        
        if progress_callback:
            progress_callback("planning", 0, "textAnalyzeSimulationtext...")
        
        # textGetSimulationtext
        context = self.zep_tools.get_simulation_context(
            graph_id=self.graph_id,
            simulation_requirement=self.simulation_requirement
        )
        
        if progress_callback:
            progress_callback("planning", 30, "textGenerateReporttext...")
        
        system_prompt = PLAN_SYSTEM_PROMPT
        user_prompt = PLAN_USER_PROMPT_TEMPLATE.format(
            simulation_requirement=self.simulation_requirement,
            total_nodes=context.get('graph_statistics', {}).get('total_nodes', 0),
            total_edges=context.get('graph_statistics', {}).get('total_edges', 0),
            entity_types=list(context.get('graph_statistics', {}).get('entity_types', {}).keys()),
            total_entities=context.get('total_entities', 0),
            related_facts_json=json.dumps(context.get('related_facts', [])[:10], ensure_ascii=False, indent=2),
        )

        try:
            response = self.llm.chat_json(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3
            )
            
            if progress_callback:
                progress_callback("planning", 80, "textParsetext...")
            
            # Parsetext
            sections = []
            for section_data in response.get("sections", []):
                sections.append(ReportSection(
                    title=section_data.get("title", ""),
                    content=""
                ))
            
            outline = ReportOutline(
                title=response.get("title", "SimulationAnalyzeReport"),
                summary=response.get("summary", ""),
                sections=sections
            )
            
            if progress_callback:
                progress_callback("planning", 100, "textComplete")
            
            logger.info(f"textComplete: {len(sections)} text")
            return outline
            
        except Exception as e:
            logger.error(f"textFailed: {str(e)}")
            # Returnstext（3text，textfallback）
            return ReportOutline(
                title="textReport",
                summary="textSimulationtextTrendtextAnalyze",
                sections=[
                    ReportSection(title="text"),
                    ReportSection(title="textAnalyze"),
                    ReportSection(title="Trendtext")
                ]
            )
    
    def _generate_section_react(
        self, 
        section: ReportSection,
        outline: ReportOutline,
        previous_sections: List[str],
        progress_callback: Optional[Callable] = None,
        section_index: int = 0
    ) -> str:
        """
        textReACTPatternGeneratetextContent
        
        ReACTtext：
        1. Thought（text）- AnalyzetextInformation
        2. Action（text）- textToolGetInformation
        3. Observation（text）- AnalyzeToolReturnsResult
        4. textInformationtext
        5. Final Answer（text）- GeneratetextContent
        
        Args:
            section: textGeneratetext
            outline: text
            previous_sections: textContent（text）
            progress_callback: text
            section_index: textIndex（textLogRecord）
            
        Returns:
            textContent（MarkdownFormat）
        """
        logger.info(f"ReACTGeneratetext: {section.title}")
        
        # RecordtextLog
        if self.report_logger:
            self.report_logger.log_section_start(section.title, section_index)
        
        system_prompt = SECTION_SYSTEM_PROMPT_TEMPLATE.format(
            report_title=outline.title,
            report_summary=outline.summary,
            simulation_requirement=self.simulation_requirement,
            section_title=section.title,
            tools_description=self._get_tools_description(),
        )

        # textUserprompt - textCompletetext4000text
        if previous_sections:
            previous_parts = []
            for sec in previous_sections:
                # text4000text
                truncated = sec[:4000] + "..." if len(sec) > 4000 else sec
                previous_parts.append(truncated)
            previous_content = "\n\n---\n\n".join(previous_parts)
        else:
            previous_content = "（text）"
        
        user_prompt = SECTION_USER_PROMPT_TEMPLATE.format(
            previous_content=previous_content,
            section_title=section.title,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # ReACTtext
        tool_calls_count = 0
        max_iterations = 5  # textIterationtext
        min_tool_calls = 3  # textTooltext
        conflict_retries = 0  # TooltextFinal AnswertextConflicttext
        used_tools = set()  # RecordtextTooltext
        all_tools = {"insight_forge", "panorama_search", "quick_search", "interview_agents"}

        # Reporttext，textInsightForgetextIssueGenerate
        report_context = f"text: {section.title}\nSimulationtext: {self.simulation_requirement}"
        
        for iteration in range(max_iterations):
            if progress_callback:
                progress_callback(
                    "generating", 
                    int((iteration / max_iterations) * 100),
                    f"text ({tool_calls_count}/{self.MAX_TOOL_CALLS_PER_SECTION})"
                )
            
            # textLLM
            response = self.llm.chat(
                messages=messages,
                temperature=0.5,
                max_tokens=4096
            )

            # Check LLM Returnstext None（API ExceptiontextContenttext）
            if response is None:
                logger.warning(f"text {section.title} text {iteration + 1} textIteration: LLM Returns None")
                # textIterationtext，AddMessagetextRetry
                if iteration < max_iterations - 1:
                    messages.append({"role": "assistant", "content": "（Responsetext）"})
                    messages.append({"role": "user", "content": "textContinueGenerateContent。"})
                    continue
                # textIterationtextReturns None，text
                break

            logger.debug(f"LLMResponse: {response[:200]}...")

            # Parsetext，textResult
            tool_calls = self._parse_tool_calls(response)
            has_tool_calls = bool(tool_calls)
            has_final_answer = "Final Answer:" in response

            # ── ConflictProcess：LLM textTooltext Final Answer ──
            if has_tool_calls and has_final_answer:
                conflict_retries += 1
                logger.warning(
                    f"text {section.title} text {iteration+1} text: "
                    f"LLM textTooltext Final Answer（text {conflict_retries} textConflict）"
                )

                if conflict_retries <= 2:
                    # text：DiscardtextResponse，text LLM text
                    messages.append({"role": "assistant", "content": response})
                    messages.append({
                        "role": "user",
                        "content": (
                            "【FormatError】textTooltext Final Answer，textAllowtext。\n"
                            "text：\n"
                            "- textTool（text <tool_call> text，text Final Answer）\n"
                            "- textContent（text 'Final Answer:' text，text <tool_call>）\n"
                            "text，text。"
                        ),
                    })
                    continue
                else:
                    # text：textProcess，textTooltext，textExecute
                    logger.warning(
                        f"text {section.title}: text {conflict_retries} textConflict，"
                        "textExecutetextTooltext"
                    )
                    first_tool_end = response.find('</tool_call>')
                    if first_tool_end != -1:
                        response = response[:first_tool_end + len('</tool_call>')]
                        tool_calls = self._parse_tool_calls(response)
                        has_tool_calls = bool(tool_calls)
                    has_final_answer = False
                    conflict_retries = 0

            # Record LLM ResponseLog
            if self.report_logger:
                self.report_logger.log_llm_response(
                    section_title=section.title,
                    section_index=section_index,
                    response=response,
                    iteration=iteration + 1,
                    has_tool_calls=has_tool_calls,
                    has_final_answer=has_final_answer
                )

            # ── text1：LLM text Final Answer ──
            if has_final_answer:
                # Tooltext，DenytextContinuetextTool
                if tool_calls_count < min_tool_calls:
                    messages.append({"role": "assistant", "content": response})
                    unused_tools = all_tools - used_tools
                    unused_hint = f"（textTooltext，text: {', '.join(unused_tools)}）" if unused_tools else ""
                    messages.append({
                        "role": "user",
                        "content": REACT_INSUFFICIENT_TOOLS_MSG.format(
                            tool_calls_count=tool_calls_count,
                            min_tool_calls=min_tool_calls,
                            unused_hint=unused_hint,
                        ),
                    })
                    continue

                # Normaltext
                final_answer = response.split("Final Answer:")[-1].strip()
                logger.info(f"text {section.title} GenerateComplete（Tooltext: {tool_calls_count}text）")

                if self.report_logger:
                    self.report_logger.log_section_content(
                        section_title=section.title,
                        section_index=section_index,
                        content=final_answer,
                        tool_calls_count=tool_calls_count
                    )
                return final_answer

            # ── text2：LLM textTool ──
            if has_tool_calls:
                # Tooltext → text，text Final Answer
                if tool_calls_count >= self.MAX_TOOL_CALLS_PER_SECTION:
                    messages.append({"role": "assistant", "content": response})
                    messages.append({
                        "role": "user",
                        "content": REACT_TOOL_LIMIT_MSG.format(
                            tool_calls_count=tool_calls_count,
                            max_tool_calls=self.MAX_TOOL_CALLS_PER_SECTION,
                        ),
                    })
                    continue

                # textExecutetextTooltext
                call = tool_calls[0]
                if len(tool_calls) > 1:
                    logger.info(f"LLM text {len(tool_calls)} textTool，textExecutetext: {call['name']}")

                if self.report_logger:
                    self.report_logger.log_tool_call(
                        section_title=section.title,
                        section_index=section_index,
                        tool_name=call["name"],
                        parameters=call.get("parameters", {}),
                        iteration=iteration + 1
                    )

                result = self._execute_tool(
                    call["name"],
                    call.get("parameters", {}),
                    report_context=report_context
                )

                if self.report_logger:
                    self.report_logger.log_tool_result(
                        section_title=section.title,
                        section_index=section_index,
                        tool_name=call["name"],
                        result=result,
                        iteration=iteration + 1
                    )

                tool_calls_count += 1
                used_tools.add(call['name'])

                # textTooltext
                unused_tools = all_tools - used_tools
                unused_hint = ""
                if unused_tools and tool_calls_count < self.MAX_TOOL_CALLS_PER_SECTION:
                    unused_hint = REACT_UNUSED_TOOLS_HINT.format(unused_list="、".join(unused_tools))

                messages.append({"role": "assistant", "content": response})
                messages.append({
                    "role": "user",
                    "content": REACT_OBSERVATION_TEMPLATE.format(
                        tool_name=call["name"],
                        result=result,
                        tool_calls_count=tool_calls_count,
                        max_tool_calls=self.MAX_TOOL_CALLS_PER_SECTION,
                        used_tools_str=", ".join(used_tools),
                        unused_hint=unused_hint,
                    ),
                })
                continue

            # ── text3：textTooltext，text Final Answer ──
            messages.append({"role": "assistant", "content": response})

            if tool_calls_count < min_tool_calls:
                # Tooltext，textTool
                unused_tools = all_tools - used_tools
                unused_hint = f"（textTooltext，text: {', '.join(unused_tools)}）" if unused_tools else ""

                messages.append({
                    "role": "user",
                    "content": REACT_INSUFFICIENT_TOOLS_MSG_ALT.format(
                        tool_calls_count=tool_calls_count,
                        min_tool_calls=min_tool_calls,
                        unused_hint=unused_hint,
                    ),
                })
                continue

            # Tooltext，LLM textContenttext "Final Answer:" text
            # textContenttext，text
            logger.info(f"text {section.title} text 'Final Answer:' text，textLLMtextContent（Tooltext: {tool_calls_count}text）")
            final_answer = response.strip()

            if self.report_logger:
                self.report_logger.log_section_content(
                    section_title=section.title,
                    section_index=section_index,
                    content=final_answer,
                    tool_calls_count=tool_calls_count
                )
            return final_answer
        
        # textIterationtext，textGenerateContent
        logger.warning(f"text {section.title} textIterationtext，textGenerate")
        messages.append({"role": "user", "content": REACT_FORCE_FINAL_MSG})
        
        response = self.llm.chat(
            messages=messages,
            temperature=0.5,
            max_tokens=4096
        )

        # Checktext LLM Returnstext None
        if response is None:
            logger.error(f"text {section.title} text LLM Returns None，textErrortext")
            final_answer = f"（textGenerateFailed：LLM ReturnstextResponse，textLaterRetry）"
        elif "Final Answer:" in response:
            final_answer = response.split("Final Answer:")[-1].strip()
        else:
            final_answer = response
        
        # RecordtextContentGenerateCompleteLog
        if self.report_logger:
            self.report_logger.log_section_content(
                section_title=section.title,
                section_index=section_index,
                content=final_answer,
                tool_calls_count=tool_calls_count
            )
        
        return final_answer
    
    def generate_report(
        self, 
        progress_callback: Optional[Callable[[str, int, str], None]] = None,
        report_id: Optional[str] = None
    ) -> Report:
        """
        GeneratetextReport（text）
        
        textGenerateCompletetextSavetextFiletext，textWaittextReportComplete。
        Filetext：
        reports/{report_id}/
            meta.json       - ReporttextInformation
            outline.json    - Reporttext
            progress.json   - Generatetext
            section_01.md   - text1text
            section_02.md   - text2text
            ...
            full_report.md  - textReport
        
        Args:
            progress_callback: textFunction (stage, progress, message)
            report_id: ReportID（text，textGenerate）
            
        Returns:
            Report: textReport
        """
        import uuid
        
        # text report_id，textGenerate
        if not report_id:
            report_id = f"report_{uuid.uuid4().hex[:12]}"
        start_time = datetime.now()
        
        report = Report(
            report_id=report_id,
            simulation_id=self.simulation_id,
            graph_id=self.graph_id,
            simulation_requirement=self.simulation_requirement,
            status=ReportStatus.PENDING,
            created_at=datetime.now().isoformat()
        )
        
        # textCompletetextList（textTrace）
        completed_section_titles = []
        
        try:
            # Initialize：CreateReportFiletextSavetextStatus
            ReportManager._ensure_report_folder(report_id)
            
            # InitializeLogRecordtext（textLog agent_log.jsonl）
            self.report_logger = ReportLogger(report_id)
            self.report_logger.log_start(
                simulation_id=self.simulation_id,
                graph_id=self.graph_id,
                simulation_requirement=self.simulation_requirement
            )
            
            # InitializetextLogRecordtext（console_log.txt）
            self.console_logger = ReportConsoleLogger(report_id)
            
            ReportManager.update_progress(
                report_id, "pending", 0, "InitializeReport...",
                completed_sections=[]
            )
            ReportManager.save_report(report)
            
            # Stage1: text
            report.status = ReportStatus.PLANNING
            ReportManager.update_progress(
                report_id, "planning", 5, "textReporttext...",
                completed_sections=[]
            )
            
            # RecordtextLog
            self.report_logger.log_planning_start()
            
            if progress_callback:
                progress_callback("planning", 0, "textReporttext...")
            
            outline = self.plan_outline(
                progress_callback=lambda stage, prog, msg: 
                    progress_callback(stage, prog // 5, msg) if progress_callback else None
            )
            report.outline = outline
            
            # RecordtextCompleteLog
            self.report_logger.log_planning_complete(outline.to_dict())
            
            # SavetextFile
            ReportManager.save_outline(report_id, outline)
            ReportManager.update_progress(
                report_id, "planning", 15, f"textComplete，text{len(outline.sections)}text",
                completed_sections=[]
            )
            ReportManager.save_report(report)
            
            logger.info(f"textSavetextFile: {report_id}/outline.json")
            
            # Stage2: textGenerate（textSave）
            report.status = ReportStatus.GENERATING
            
            total_sections = len(outline.sections)
            generated_sections = []  # SaveContenttext
            
            for i, section in enumerate(outline.sections):
                section_num = i + 1
                base_progress = 20 + int((i / total_sections) * 70)
                
                # Updatetext
                ReportManager.update_progress(
                    report_id, "generating", base_progress,
                    f"textGeneratetext: {section.title} ({section_num}/{total_sections})",
                    current_section=section.title,
                    completed_sections=completed_section_titles
                )
                
                if progress_callback:
                    progress_callback(
                        "generating", 
                        base_progress, 
                        f"textGeneratetext: {section.title} ({section_num}/{total_sections})"
                    )
                
                # GeneratetextContent
                section_content = self._generate_section_react(
                    section=section,
                    outline=outline,
                    previous_sections=generated_sections,
                    progress_callback=lambda stage, prog, msg:
                        progress_callback(
                            stage, 
                            base_progress + int(prog * 0.7 / total_sections),
                            msg
                        ) if progress_callback else None,
                    section_index=section_num
                )
                
                section.content = section_content
                generated_sections.append(f"## {section.title}\n\n{section_content}")

                # Savetext
                ReportManager.save_section(report_id, section_num, section)
                completed_section_titles.append(section.title)

                # RecordtextCompleteLog
                full_section_content = f"## {section.title}\n\n{section_content}"

                if self.report_logger:
                    self.report_logger.log_section_full_complete(
                        section_title=section.title,
                        section_index=section_num,
                        full_content=full_section_content.strip()
                    )

                logger.info(f"textSave: {report_id}/section_{section_num:02d}.md")
                
                # Updatetext
                ReportManager.update_progress(
                    report_id, "generating", 
                    base_progress + int(70 / total_sections),
                    f"text {section.title} textComplete",
                    current_section=None,
                    completed_sections=completed_section_titles
                )
            
            # Stage3: GrouptextReport
            if progress_callback:
                progress_callback("generating", 95, "textGrouptextReport...")
            
            ReportManager.update_progress(
                report_id, "generating", 95, "textGrouptextReport...",
                completed_sections=completed_section_titles
            )
            
            # textReportManagerGrouptextReport
            report.markdown_content = ReportManager.assemble_full_report(report_id, outline)
            report.status = ReportStatus.COMPLETED
            report.completed_at = datetime.now().isoformat()
            
            # text
            total_time_seconds = (datetime.now() - start_time).total_seconds()
            
            # RecordReportCompleteLog
            if self.report_logger:
                self.report_logger.log_report_complete(
                    total_sections=total_sections,
                    total_time_seconds=total_time_seconds
                )
            
            # SavetextReport
            ReportManager.save_report(report)
            ReportManager.update_progress(
                report_id, "completed", 100, "ReportGenerateComplete",
                completed_sections=completed_section_titles
            )
            
            if progress_callback:
                progress_callback("completed", 100, "ReportGenerateComplete")
            
            logger.info(f"ReportGenerateComplete: {report_id}")
            
            # ClosetextLogRecordtext
            if self.console_logger:
                self.console_logger.close()
                self.console_logger = None
            
            return report
            
        except Exception as e:
            logger.error(f"ReportGenerateFailed: {str(e)}")
            report.status = ReportStatus.FAILED
            report.error = str(e)
            
            # RecordErrorLog
            if self.report_logger:
                self.report_logger.log_error(str(e), "failed")
            
            # SaveFailedStatus
            try:
                ReportManager.save_report(report)
                ReportManager.update_progress(
                    report_id, "failed", -1, f"ReportGenerateFailed: {str(e)}",
                    completed_sections=completed_section_titles
                )
            except Exception:
                pass  # IgnoreSaveFailedtextError
            
            # ClosetextLogRecordtext
            if self.console_logger:
                self.console_logger.close()
                self.console_logger = None
            
            return report
    
    def chat(
        self, 
        message: str,
        chat_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        textReport Agenttext
        
        textAgenttextTooltextIssue
        
        Args:
            message: UserMessage
            chat_history: text
            
        Returns:
            {
                "response": "Agenttext",
                "tool_calls": [textToolList],
                "sources": [Informationtext]
            }
        """
        logger.info(f"Report Agenttext: {message[:50]}...")
        
        chat_history = chat_history or []
        
        # GettextGeneratetextReportContent
        report_content = ""
        try:
            report = ReportManager.get_report_by_simulation(self.simulation_id)
            if report and report.markdown_content:
                # textReporttext，text
                report_content = report.markdown_content[:15000]
                if len(report.markdown_content) > 15000:
                    report_content += "\n\n... [ReportContenttext] ..."
        except Exception as e:
            logger.warning(f"GetReportContentFailed: {e}")
        
        system_prompt = CHAT_SYSTEM_PROMPT_TEMPLATE.format(
            simulation_requirement=self.simulation_requirement,
            report_content=report_content if report_content else "（textReport）",
            tools_description=self._get_tools_description(),
        )

        # textMessage
        messages = [{"role": "system", "content": system_prompt}]
        
        # Addtext
        for h in chat_history[-10:]:  # text
            messages.append(h)
        
        # AddUserMessage
        messages.append({
            "role": "user", 
            "content": message
        })
        
        # ReACTtext（text）
        tool_calls_made = []
        max_iterations = 2  # textIterationtext
        
        for iteration in range(max_iterations):
            response = self.llm.chat(
                messages=messages,
                temperature=0.5
            )
            
            # ParseTooltext
            tool_calls = self._parse_tool_calls(response)
            
            if not tool_calls:
                # textTooltext，textReturnsResponse
                clean_response = re.sub(r'<tool_call>.*?</tool_call>', '', response, flags=re.DOTALL)
                clean_response = re.sub(r'\[TOOL_CALL\].*?\)', '', clean_response)
                
                return {
                    "response": clean_response.strip(),
                    "tool_calls": tool_calls_made,
                    "sources": [tc.get("parameters", {}).get("query", "") for tc in tool_calls_made]
                }
            
            # ExecuteTooltext（text）
            tool_results = []
            for call in tool_calls[:1]:  # textExecute1textTooltext
                if len(tool_calls_made) >= self.MAX_TOOL_CALLS_PER_CHAT:
                    break
                result = self._execute_tool(call["name"], call.get("parameters", {}))
                tool_results.append({
                    "tool": call["name"],
                    "result": result[:1500]  # textResulttext
                })
                tool_calls_made.append(call)
            
            # textResultAddtextMessage
            messages.append({"role": "assistant", "content": response})
            observation = "\n".join([f"[{r['tool']}Result]\n{r['result']}" for r in tool_results])
            messages.append({
                "role": "user",
                "content": observation + CHAT_OBSERVATION_SUFFIX
            })
        
        # textIteration，GettextResponse
        final_response = self.llm.chat(
            messages=messages,
            temperature=0.5
        )
        
        # CleanResponse
        clean_response = re.sub(r'<tool_call>.*?</tool_call>', '', final_response, flags=re.DOTALL)
        clean_response = re.sub(r'\[TOOL_CALL\].*?\)', '', clean_response)
        
        return {
            "response": clean_response.strip(),
            "tool_calls": tool_calls_made,
            "sources": [tc.get("parameters", {}).get("query", "") for tc in tool_calls_made]
        }


class ReportManager:
    """
    Reporttext
    
    textReporttext
    
    Filetext（text）：
    reports/
      {report_id}/
        meta.json          - ReporttextInformationtextStatus
        outline.json       - Reporttext
        progress.json      - Generatetext
        section_01.md      - text1text
        section_02.md      - text2text
        ...
        full_report.md     - textReport
    """
    
    # ReporttextDirectory
    REPORTS_DIR = os.path.join(Config.UPLOAD_FOLDER, 'reports')
    
    @classmethod
    def _ensure_reports_dir(cls):
        """textReporttextDirectorytext"""
        os.makedirs(cls.REPORTS_DIR, exist_ok=True)
    
    @classmethod
    def _get_report_folder(cls, report_id: str) -> str:
        """GetReportFiletextPath"""
        return os.path.join(cls.REPORTS_DIR, report_id)
    
    @classmethod
    def _ensure_report_folder(cls, report_id: str) -> str:
        """textReportFiletextReturnsPath"""
        folder = cls._get_report_folder(report_id)
        os.makedirs(folder, exist_ok=True)
        return folder
    
    @classmethod
    def _get_report_path(cls, report_id: str) -> str:
        """GetReporttextInformationFilePath"""
        return os.path.join(cls._get_report_folder(report_id), "meta.json")
    
    @classmethod
    def _get_report_markdown_path(cls, report_id: str) -> str:
        """GettextReportMarkdownFilePath"""
        return os.path.join(cls._get_report_folder(report_id), "full_report.md")
    
    @classmethod
    def _get_outline_path(cls, report_id: str) -> str:
        """GettextFilePath"""
        return os.path.join(cls._get_report_folder(report_id), "outline.json")
    
    @classmethod
    def _get_progress_path(cls, report_id: str) -> str:
        """GettextFilePath"""
        return os.path.join(cls._get_report_folder(report_id), "progress.json")
    
    @classmethod
    def _get_section_path(cls, report_id: str, section_index: int) -> str:
        """GettextMarkdownFilePath"""
        return os.path.join(cls._get_report_folder(report_id), f"section_{section_index:02d}.md")
    
    @classmethod
    def _get_agent_log_path(cls, report_id: str) -> str:
        """Get Agent LogFilePath"""
        return os.path.join(cls._get_report_folder(report_id), "agent_log.jsonl")
    
    @classmethod
    def _get_console_log_path(cls, report_id: str) -> str:
        """GettextLogFilePath"""
        return os.path.join(cls._get_report_folder(report_id), "console_log.txt")
    
    @classmethod
    def get_console_log(cls, report_id: str, from_line: int = 0) -> Dict[str, Any]:
        """
        GettextLogContent
        
        textReportGeneratetextLog（INFO、WARNINGtext），
        text agent_log.jsonl textLogtext。
        
        Args:
            report_id: ReportID
            from_line: textRead（textGet，0 Tabletext）
            
        Returns:
            {
                "logs": [LogtextList],
                "total_lines": text,
                "from_line": text,
                "has_more": textLog
            }
        """
        log_path = cls._get_console_log_path(report_id)
        
        if not os.path.exists(log_path):
            return {
                "logs": [],
                "total_lines": 0,
                "from_line": 0,
                "has_more": False
            }
        
        logs = []
        total_lines = 0
        
        with open(log_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                total_lines = i + 1
                if i >= from_line:
                    # textLogtext，text
                    logs.append(line.rstrip('\n\r'))
        
        return {
            "logs": logs,
            "total_lines": total_lines,
            "from_line": from_line,
            "has_more": False  # textReadtext
        }
    
    @classmethod
    def get_console_log_stream(cls, report_id: str) -> List[str]:
        """
        GettextLog（textGettext）
        
        Args:
            report_id: ReportID
            
        Returns:
            LogtextList
        """
        result = cls.get_console_log(report_id, from_line=0)
        return result["logs"]
    
    @classmethod
    def get_agent_log(cls, report_id: str, from_line: int = 0) -> Dict[str, Any]:
        """
        Get Agent LogContent
        
        Args:
            report_id: ReportID
            from_line: textRead（textGet，0 Tabletext）
            
        Returns:
            {
                "logs": [LogtextList],
                "total_lines": text,
                "from_line": text,
                "has_more": textLog
            }
        """
        log_path = cls._get_agent_log_path(report_id)
        
        if not os.path.exists(log_path):
            return {
                "logs": [],
                "total_lines": 0,
                "from_line": 0,
                "has_more": False
            }
        
        logs = []
        total_lines = 0
        
        with open(log_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                total_lines = i + 1
                if i >= from_line:
                    try:
                        log_entry = json.loads(line.strip())
                        logs.append(log_entry)
                    except json.JSONDecodeError:
                        # SkipParseFailedtext
                        continue
        
        return {
            "logs": logs,
            "total_lines": total_lines,
            "from_line": from_line,
            "has_more": False  # textReadtext
        }
    
    @classmethod
    def get_agent_log_stream(cls, report_id: str) -> List[Dict[str, Any]]:
        """
        Gettext Agent Log（textGettext）
        
        Args:
            report_id: ReportID
            
        Returns:
            LogtextList
        """
        result = cls.get_agent_log(report_id, from_line=0)
        return result["logs"]
    
    @classmethod
    def save_outline(cls, report_id: str, outline: ReportOutline) -> None:
        """
        SaveReporttext
        
        textStageCompletetext
        """
        cls._ensure_report_folder(report_id)
        
        with open(cls._get_outline_path(report_id), 'w', encoding='utf-8') as f:
            json.dump(outline.to_dict(), f, ensure_ascii=False, indent=2)
        
        logger.info(f"textSave: {report_id}")
    
    @classmethod
    def save_section(
        cls,
        report_id: str,
        section_index: int,
        section: ReportSection
    ) -> str:
        """
        Savetext

        textGenerateCompletetext，Implementationtext

        Args:
            report_id: ReportID
            section_index: textIndex（text1text）
            section: textObject

        Returns:
            SavetextFilePath
        """
        cls._ensure_report_folder(report_id)

        # textMarkdownContent - Cleantext
        cleaned_content = cls._clean_section_content(section.content, section.title)
        md_content = f"## {section.title}\n\n"
        if cleaned_content:
            md_content += f"{cleaned_content}\n\n"

        # SaveFile
        file_suffix = f"section_{section_index:02d}.md"
        file_path = os.path.join(cls._get_report_folder(report_id), file_suffix)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        logger.info(f"textSave: {report_id}/{file_suffix}")
        return file_path
    
    @classmethod
    def _clean_section_content(cls, content: str, section_title: str) -> str:
        """
        CleantextContent
        
        1. RemoveContenttextMarkdowntext
        2. text ### textConverttext
        
        Args:
            content: textContent
            section_title: text
            
        Returns:
            CleantextContent
        """
        import re
        
        if not content:
            return content
        
        content = content.strip()
        lines = content.split('\n')
        cleaned_lines = []
        skip_next_empty = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # ChecktextMarkdowntext
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', stripped)
            
            if heading_match:
                level = len(heading_match.group(1))
                title_text = heading_match.group(2).strip()
                
                # Checktext（Skiptext5text）
                if i < 5:
                    if title_text == section_title or title_text.replace(' ', '') == section_title.replace(' ', ''):
                        skip_next_empty = True
                        continue
                
                # text（#, ##, ###, ####text）Converttext
                # textAdd，Contenttext
                cleaned_lines.append(f"**{title_text}**")
                cleaned_lines.append("")  # Addtext
                continue
            
            # textSkiptext，text，textSkip
            if skip_next_empty and stripped == '':
                skip_next_empty = False
                continue
            
            skip_next_empty = False
            cleaned_lines.append(line)
        
        # Removetext
        while cleaned_lines and cleaned_lines[0].strip() == '':
            cleaned_lines.pop(0)
        
        # Removetext
        while cleaned_lines and cleaned_lines[0].strip() in ['---', '***', '___']:
            cleaned_lines.pop(0)
            # textRemovetext
            while cleaned_lines and cleaned_lines[0].strip() == '':
                cleaned_lines.pop(0)
        
        return '\n'.join(cleaned_lines)
    
    @classmethod
    def update_progress(
        cls, 
        report_id: str, 
        status: str, 
        progress: int, 
        message: str,
        current_section: str = None,
        completed_sections: List[str] = None
    ) -> None:
        """
        UpdateReportGeneratetext
        
        textReadprogress.jsonGettext
        """
        cls._ensure_report_folder(report_id)
        
        progress_data = {
            "status": status,
            "progress": progress,
            "message": message,
            "current_section": current_section,
            "completed_sections": completed_sections or [],
            "updated_at": datetime.now().isoformat()
        }
        
        with open(cls._get_progress_path(report_id), 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def get_progress(cls, report_id: str) -> Optional[Dict[str, Any]]:
        """GetReportGeneratetext"""
        path = cls._get_progress_path(report_id)
        
        if not os.path.exists(path):
            return None
        
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @classmethod
    def get_generated_sections(cls, report_id: str) -> List[Dict[str, Any]]:
        """
        GettextGeneratetextList
        
        ReturnstextSavetextFileInformation
        """
        folder = cls._get_report_folder(report_id)
        
        if not os.path.exists(folder):
            return []
        
        sections = []
        for filename in sorted(os.listdir(folder)):
            if filename.startswith('section_') and filename.endswith('.md'):
                file_path = os.path.join(folder, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # textFiletextParsetextIndex
                parts = filename.replace('.md', '').split('_')
                section_index = int(parts[1])

                sections.append({
                    "filename": filename,
                    "section_index": section_index,
                    "content": content
                })

        return sections
    
    @classmethod
    def assemble_full_report(cls, report_id: str, outline: ReportOutline) -> str:
        """
        GrouptextReport
        
        textSavetextFileGrouptextReport，textClean
        """
        folder = cls._get_report_folder(report_id)
        
        # textReporttext
        md_content = f"# {outline.title}\n\n"
        md_content += f"> {outline.summary}\n\n"
        md_content += f"---\n\n"
        
        # textReadtextFile
        sections = cls.get_generated_sections(report_id)
        for section_info in sections:
            md_content += section_info["content"]
        
        # textProcess：CleantextReporttextIssue
        md_content = cls._post_process_report(md_content, outline)
        
        # SavetextReport
        full_path = cls._get_report_markdown_path(report_id)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        logger.info(f"textReporttextGrouptext: {report_id}")
        return md_content
    
    @classmethod
    def _post_process_report(cls, content: str, outline: ReportOutline) -> str:
        """
        textProcessReportContent
        
        1. Removetext
        2. textReporttext(#)text(##)，Removetext(###, ####text)
        3. Cleantext
        
        Args:
            content: textReportContent
            outline: Reporttext
            
        Returns:
            ProcesstextContent
        """
        import re
        
        lines = content.split('\n')
        processed_lines = []
        prev_was_heading = False
        
        # text
        section_titles = set()
        for section in outline.sections:
            section_titles.add(section.title)
        
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # Checktext
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', stripped)
            
            if heading_match:
                level = len(heading_match.group(1))
                title = heading_match.group(2).strip()
                
                # Checktext（text5textContenttext）
                is_duplicate = False
                for j in range(max(0, len(processed_lines) - 5), len(processed_lines)):
                    prev_line = processed_lines[j].strip()
                    prev_match = re.match(r'^(#{1,6})\s+(.+)$', prev_line)
                    if prev_match:
                        prev_title = prev_match.group(2).strip()
                        if prev_title == title:
                            is_duplicate = True
                            break
                
                if is_duplicate:
                    # Skiptext
                    i += 1
                    while i < len(lines) and lines[i].strip() == '':
                        i += 1
                    continue
                
                # textProcess：
                # - # (level=1) textReporttext
                # - ## (level=2) text
                # - ### text (level>=3) Converttext
                
                if level == 1:
                    if title == outline.title:
                        # textReporttext
                        processed_lines.append(line)
                        prev_was_heading = True
                    elif title in section_titles:
                        # textErrortext#，text##
                        processed_lines.append(f"## {title}")
                        prev_was_heading = True
                    else:
                        # text
                        processed_lines.append(f"**{title}**")
                        processed_lines.append("")
                        prev_was_heading = False
                elif level == 2:
                    if title in section_titles or title == outline.title:
                        # text
                        processed_lines.append(line)
                        prev_was_heading = True
                    else:
                        # text
                        processed_lines.append(f"**{title}**")
                        processed_lines.append("")
                        prev_was_heading = False
                else:
                    # ### textConverttext
                    processed_lines.append(f"**{title}**")
                    processed_lines.append("")
                    prev_was_heading = False
                
                i += 1
                continue
            
            elif stripped == '---' and prev_was_heading:
                # Skiptext
                i += 1
                continue
            
            elif stripped == '' and prev_was_heading:
                # text
                if processed_lines and processed_lines[-1].strip() != '':
                    processed_lines.append(line)
                prev_was_heading = False
            
            else:
                processed_lines.append(line)
                prev_was_heading = False
            
            i += 1
        
        # Cleantext（text2text）
        result_lines = []
        empty_count = 0
        for line in processed_lines:
            if line.strip() == '':
                empty_count += 1
                if empty_count <= 2:
                    result_lines.append(line)
            else:
                empty_count = 0
                result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    @classmethod
    def save_report(cls, report: Report) -> None:
        """SaveReporttextInformationtextReport"""
        cls._ensure_report_folder(report.report_id)
        
        # SavetextInformationJSON
        with open(cls._get_report_path(report.report_id), 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
        
        # Savetext
        if report.outline:
            cls.save_outline(report.report_id, report.outline)
        
        # SavetextMarkdownReport
        if report.markdown_content:
            with open(cls._get_report_markdown_path(report.report_id), 'w', encoding='utf-8') as f:
                f.write(report.markdown_content)
        
        logger.info(f"ReporttextSave: {report.report_id}")
    
    @classmethod
    def get_report(cls, report_id: str) -> Optional[Report]:
        """GetReport"""
        path = cls._get_report_path(report_id)
        
        if not os.path.exists(path):
            # textFormat：ChecktextreportsDirectorytextFile
            old_path = os.path.join(cls.REPORTS_DIR, f"{report_id}.json")
            if os.path.exists(old_path):
                path = old_path
            else:
                return None
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # textReportObject
        outline = None
        if data.get('outline'):
            outline_data = data['outline']
            sections = []
            for s in outline_data.get('sections', []):
                sections.append(ReportSection(
                    title=s['title'],
                    content=s.get('content', '')
                ))
            outline = ReportOutline(
                title=outline_data['title'],
                summary=outline_data['summary'],
                sections=sections
            )
        
        # textmarkdown_contenttext，textfull_report.mdRead
        markdown_content = data.get('markdown_content', '')
        if not markdown_content:
            full_report_path = cls._get_report_markdown_path(report_id)
            if os.path.exists(full_report_path):
                with open(full_report_path, 'r', encoding='utf-8') as f:
                    markdown_content = f.read()
        
        return Report(
            report_id=data['report_id'],
            simulation_id=data['simulation_id'],
            graph_id=data['graph_id'],
            simulation_requirement=data['simulation_requirement'],
            status=ReportStatus(data['status']),
            outline=outline,
            markdown_content=markdown_content,
            created_at=data.get('created_at', ''),
            completed_at=data.get('completed_at', ''),
            error=data.get('error')
        )
    
    @classmethod
    def get_report_by_simulation(cls, simulation_id: str) -> Optional[Report]:
        """textSimulationIDGetReport"""
        cls._ensure_reports_dir()
        
        for item in os.listdir(cls.REPORTS_DIR):
            item_path = os.path.join(cls.REPORTS_DIR, item)
            # textFormat：Filetext
            if os.path.isdir(item_path):
                report = cls.get_report(item)
                if report and report.simulation_id == simulation_id:
                    return report
            # textFormat：JSONFile
            elif item.endswith('.json'):
                report_id = item[:-5]
                report = cls.get_report(report_id)
                if report and report.simulation_id == simulation_id:
                    return report
        
        return None
    
    @classmethod
    def list_reports(cls, simulation_id: Optional[str] = None, limit: int = 50) -> List[Report]:
        """textReport"""
        cls._ensure_reports_dir()
        
        reports = []
        for item in os.listdir(cls.REPORTS_DIR):
            item_path = os.path.join(cls.REPORTS_DIR, item)
            # textFormat：Filetext
            if os.path.isdir(item_path):
                report = cls.get_report(item)
                if report:
                    if simulation_id is None or report.simulation_id == simulation_id:
                        reports.append(report)
            # textFormat：JSONFile
            elif item.endswith('.json'):
                report_id = item[:-5]
                report = cls.get_report(report_id)
                if report:
                    if simulation_id is None or report.simulation_id == simulation_id:
                        reports.append(report)
        
        # textCreatetext
        reports.sort(key=lambda r: r.created_at, reverse=True)
        
        return reports[:limit]
    
    @classmethod
    def delete_report(cls, report_id: str) -> bool:
        """DeleteReport（textFiletext）"""
        import shutil
        
        folder_path = cls._get_report_folder(report_id)
        
        # textFormat：DeletetextFiletext
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            shutil.rmtree(folder_path)
            logger.info(f"ReportFiletextDelete: {report_id}")
            return True
        
        # textFormat：DeletetextFile
        deleted = False
        old_json_path = os.path.join(cls.REPORTS_DIR, f"{report_id}.json")
        old_md_path = os.path.join(cls.REPORTS_DIR, f"{report_id}.md")
        
        if os.path.exists(old_json_path):
            os.remove(old_json_path)
            deleted = True
        if os.path.exists(old_md_path):
            os.remove(old_md_path)
            deleted = True
        
        return deleted
