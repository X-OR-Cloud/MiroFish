"""
ZepGraphtextUpdateService
textSimulationtextAgentActivetextUpdatetextZepGraphtext
"""

import os
import time
import threading
import json
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from queue import Queue, Empty

from zep_cloud.client import Zep

from ..config import Config
from ..utils.logger import get_logger

logger = get_logger('mirofish.zep_graph_memory_updater')


@dataclass
class AgentActivity:
    """AgentActiveRecord"""
    platform: str           # twitter / reddit
    agent_id: int
    agent_name: str
    action_type: str        # CREATE_POST, LIKE_POST, etc.
    action_args: Dict[str, Any]
    round_num: int
    timestamp: str
    
    def to_episode_text(self) -> str:
        """
        textActiveConverttextSendtextZeptext
        
        textFormat，textZeptextEntitytextRelationship
        textAddSimulationtext，textGraphUpdate
        """
        # textTypeGeneratetext
        action_descriptions = {
            "CREATE_POST": self._describe_create_post,
            "LIKE_POST": self._describe_like_post,
            "DISLIKE_POST": self._describe_dislike_post,
            "REPOST": self._describe_repost,
            "QUOTE_POST": self._describe_quote_post,
            "FOLLOW": self._describe_follow,
            "CREATE_COMMENT": self._describe_create_comment,
            "LIKE_COMMENT": self._describe_like_comment,
            "DISLIKE_COMMENT": self._describe_dislike_comment,
            "SEARCH_POSTS": self._describe_search,
            "SEARCH_USER": self._describe_search_user,
            "MUTE": self._describe_mute,
        }
        
        describe_func = action_descriptions.get(self.action_type, self._describe_generic)
        description = describe_func()
        
        # textReturns "agentName: Activetext" Format，textAddSimulationtext
        return f"{self.agent_name}: {description}"
    
    def _describe_create_post(self) -> str:
        content = self.action_args.get("content", "")
        if content:
            return f"Releasetext：「{content}」"
        return "Releasetext"
    
    def _describe_like_post(self) -> str:
        """text - textAuthorInformation"""
        post_content = self.action_args.get("post_content", "")
        post_author = self.action_args.get("post_author_name", "")
        
        if post_content and post_author:
            return f"text{post_author}text：「{post_content}」"
        elif post_content:
            return f"text：「{post_content}」"
        elif post_author:
            return f"text{post_author}text"
        return "text"
    
    def _describe_dislike_post(self) -> str:
        """text - textAuthorInformation"""
        post_content = self.action_args.get("post_content", "")
        post_author = self.action_args.get("post_author_name", "")
        
        if post_content and post_author:
            return f"text{post_author}text：「{post_content}」"
        elif post_content:
            return f"text：「{post_content}」"
        elif post_author:
            return f"text{post_author}text"
        return "text"
    
    def _describe_repost(self) -> str:
        """text - textContenttextAuthorInformation"""
        original_content = self.action_args.get("original_content", "")
        original_author = self.action_args.get("original_author_name", "")
        
        if original_content and original_author:
            return f"text{original_author}text：「{original_content}」"
        elif original_content:
            return f"text：「{original_content}」"
        elif original_author:
            return f"text{original_author}text"
        return "text"
    
    def _describe_quote_post(self) -> str:
        """text - textContent、AuthorInformationtext"""
        original_content = self.action_args.get("original_content", "")
        original_author = self.action_args.get("original_author_name", "")
        quote_content = self.action_args.get("quote_content", "") or self.action_args.get("content", "")
        
        base = ""
        if original_content and original_author:
            base = f"text{original_author}text「{original_content}」"
        elif original_content:
            base = f"text「{original_content}」"
        elif original_author:
            base = f"text{original_author}text"
        else:
            base = "text"
        
        if quote_content:
            base += f"，text：「{quote_content}」"
        return base
    
    def _describe_follow(self) -> str:
        """textUser - textUsertextName"""
        target_user_name = self.action_args.get("target_user_name", "")
        
        if target_user_name:
            return f"textUser「{target_user_name}」"
        return "textUser"
    
    def _describe_create_comment(self) -> str:
        """textTabletext - textContenttextInformation"""
        content = self.action_args.get("content", "")
        post_content = self.action_args.get("post_content", "")
        post_author = self.action_args.get("post_author_name", "")
        
        if content:
            if post_content and post_author:
                return f"text{post_author}text「{post_content}」text：「{content}」"
            elif post_content:
                return f"text「{post_content}」text：「{content}」"
            elif post_author:
                return f"text{post_author}text：「{content}」"
            return f"text：「{content}」"
        return "textTabletext"
    
    def _describe_like_comment(self) -> str:
        """text - textContenttextAuthorInformation"""
        comment_content = self.action_args.get("comment_content", "")
        comment_author = self.action_args.get("comment_author_name", "")
        
        if comment_content and comment_author:
            return f"text{comment_author}text：「{comment_content}」"
        elif comment_content:
            return f"text：「{comment_content}」"
        elif comment_author:
            return f"text{comment_author}text"
        return "text"
    
    def _describe_dislike_comment(self) -> str:
        """text - textContenttextAuthorInformation"""
        comment_content = self.action_args.get("comment_content", "")
        comment_author = self.action_args.get("comment_author_name", "")
        
        if comment_content and comment_author:
            return f"text{comment_author}text：「{comment_content}」"
        elif comment_content:
            return f"text：「{comment_content}」"
        elif comment_author:
            return f"text{comment_author}text"
        return "text"
    
    def _describe_search(self) -> str:
        """Searchtext - textSearchtext"""
        query = self.action_args.get("query", "") or self.action_args.get("keyword", "")
        return f"Searchtext「{query}」" if query else "textSearch"
    
    def _describe_search_user(self) -> str:
        """SearchUser - textSearchtext"""
        query = self.action_args.get("query", "") or self.action_args.get("username", "")
        return f"SearchtextUser「{query}」" if query else "SearchtextUser"
    
    def _describe_mute(self) -> str:
        """textUser - textUsertextName"""
        target_user_name = self.action_args.get("target_user_name", "")
        
        if target_user_name:
            return f"textUser「{target_user_name}」"
        return "textUser"
    
    def _describe_generic(self) -> str:
        # textType，Generatetext
        return f"Executetext{self.action_type}text"


class ZepGraphMemoryUpdater:
    """
    ZepGraphtextUpdatetext
    
    MonitorSimulationtextactionsLogFile，textagentActivetextUpdatetextZepGraphtext。
    textGroup，textBATCH_SIZEtextActivetextSendtextZep。
    
    textUpdatetextZep，action_argstextInformation：
    - text/text
    - text/text
    - text/textUsertext
    - text/text
    """
    
    # textSendtext（textSend）
    BATCH_SIZE = 5
    
    # textNameMap（textShow）
    PLATFORM_DISPLAY_NAMES = {
        'twitter': 'text1',
        'reddit': 'text2',
    }
    
    # Sendtext（text），textRequesttext
    SEND_INTERVAL = 0.5
    
    # RetryConfiguration
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # text
    
    def __init__(self, graph_id: str, api_key: Optional[str] = None):
        """
        InitializeUpdatetext
        
        Args:
            graph_id: ZepGraphID
            api_key: Zep API Key（text，textConfigurationRead）
        """
        self.graph_id = graph_id
        self.api_key = api_key or Config.ZEP_API_KEY
        
        if not self.api_key:
            raise ValueError("ZEP_API_KEYtextConfiguration")
        
        self.client = Zep(api_key=self.api_key)
        
        # ActiveQueue
        self._activity_queue: Queue = Queue()
        
        # textGrouptextActivetext（textBATCH_SIZEtextSend）
        self._platform_buffers: Dict[str, List[AgentActivity]] = {
            'twitter': [],
            'reddit': [],
        }
        self._buffer_lock = threading.Lock()
        
        # text
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        
        # Statistics
        self._total_activities = 0  # textAddtextQueuetextActivetext
        self._total_sent = 0        # SuccessSendtextZeptext
        self._total_items_sent = 0  # SuccessSendtextZeptextActivetext
        self._failed_count = 0      # SendFailedtext
        self._skipped_count = 0     # textFilterSkiptextActivetext（DO_NOTHING）
        
        logger.info(f"ZepGraphMemoryUpdater InitializeComplete: graph_id={graph_id}, batch_size={self.BATCH_SIZE}")
    
    def _get_platform_display_name(self, platform: str) -> str:
        """GettextShowName"""
        return self.PLATFORM_DISPLAY_NAMES.get(platform.lower(), platform)
    
    def start(self):
        """StarttextThread"""
        if self._running:
            return
        
        self._running = True
        self._worker_thread = threading.Thread(
            target=self._worker_loop,
            daemon=True,
            name=f"ZepMemoryUpdater-{self.graph_id[:8]}"
        )
        self._worker_thread.start()
        logger.info(f"ZepGraphMemoryUpdater textStart: graph_id={self.graph_id}")
    
    def stop(self):
        """StoptextThread"""
        self._running = False
        
        # SendtextActive
        self._flush_remaining()
        
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=10)
        
        logger.info(f"ZepGraphMemoryUpdater textStop: graph_id={self.graph_id}, "
                   f"total_activities={self._total_activities}, "
                   f"batches_sent={self._total_sent}, "
                   f"items_sent={self._total_items_sent}, "
                   f"failed={self._failed_count}, "
                   f"skipped={self._skipped_count}")
    
    def add_activity(self, activity: AgentActivity):
        """
        AddtextagentActivetextQueue
        
        textAddtextQueue，text：
        - CREATE_POST（text）
        - CREATE_COMMENT（text）
        - QUOTE_POST（text）
        - SEARCH_POSTS（Searchtext）
        - SEARCH_USER（SearchUser）
        - LIKE_POST/DISLIKE_POST（text/text）
        - REPOST（text）
        - FOLLOW（text）
        - MUTE（text）
        - LIKE_COMMENT/DISLIKE_COMMENT（text/text）
        
        action_argstextInformation（text、Usertext）。
        
        Args:
            activity: AgentActiveRecord
        """
        # SkipDO_NOTHINGTypetextActive
        if activity.action_type == "DO_NOTHING":
            self._skipped_count += 1
            return
        
        self._activity_queue.put(activity)
        self._total_activities += 1
        logger.debug(f"AddActivetextZepQueue: {activity.agent_name} - {activity.action_type}")
    
    def add_activity_from_dict(self, data: Dict[str, Any], platform: str):
        """
        textDictDataAddActive
        
        Args:
            data: textactions.jsonlParsetextDictData
            platform: textName (twitter/reddit)
        """
        # SkiptextTypetext
        if "event_type" in data:
            return
        
        activity = AgentActivity(
            platform=platform,
            agent_id=data.get("agent_id", 0),
            agent_name=data.get("agent_name", ""),
            action_type=data.get("action_type", ""),
            action_args=data.get("action_args", {}),
            round_num=data.get("round", 0),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
        )
        
        self.add_activity(activity)
    
    def _worker_loop(self):
        """text - textSendActivetextZep"""
        while self._running or not self._activity_queue.empty():
            try:
                # textQueueGetActive（Timeout1text）
                try:
                    activity = self._activity_queue.get(timeout=1)
                    
                    # textActiveAddtext
                    platform = activity.platform.lower()
                    with self._buffer_lock:
                        if platform not in self._platform_buffers:
                            self._platform_buffers[platform] = []
                        self._platform_buffers[platform].append(activity)
                        
                        # Checktext
                        if len(self._platform_buffers[platform]) >= self.BATCH_SIZE:
                            batch = self._platform_buffers[platform][:self.BATCH_SIZE]
                            self._platform_buffers[platform] = self._platform_buffers[platform][self.BATCH_SIZE:]
                            # textLocktextSend
                            self._send_batch_activities(batch, platform)
                            # Sendtext，textRequesttext
                            time.sleep(self.SEND_INTERVAL)
                    
                except Empty:
                    pass
                    
            except Exception as e:
                logger.error(f"textException: {e}")
                time.sleep(1)
    
    def _send_batch_activities(self, activities: List[AgentActivity], platform: str):
        """
        textSendActivetextZepGraph（Mergetext）
        
        Args:
            activities: AgentActiveList
            platform: textName
        """
        if not activities:
            return
        
        # textActiveMergetext，text
        episode_texts = [activity.to_episode_text() for activity in activities]
        combined_text = "\n".join(episode_texts)
        
        # textRetrytextSend
        for attempt in range(self.MAX_RETRIES):
            try:
                self.client.graph.add(
                    graph_id=self.graph_id,
                    type="text",
                    data=combined_text
                )
                
                self._total_sent += 1
                self._total_items_sent += len(activities)
                display_name = self._get_platform_display_name(platform)
                logger.info(f"SuccesstextSend {len(activities)} text{display_name}ActivetextGraph {self.graph_id}")
                logger.debug(f"textContentPreview: {combined_text[:200]}...")
                return
                
            except Exception as e:
                if attempt < self.MAX_RETRIES - 1:
                    logger.warning(f"textSendtextZepFailed (text {attempt + 1}/{self.MAX_RETRIES}): {e}")
                    time.sleep(self.RETRY_DELAY * (attempt + 1))
                else:
                    logger.error(f"textSendtextZepFailed，textRetry{self.MAX_RETRIES}text: {e}")
                    self._failed_count += 1
    
    def _flush_remaining(self):
        """SendQueuetextActive"""
        # textProcessQueuetextActive，Addtext
        while not self._activity_queue.empty():
            try:
                activity = self._activity_queue.get_nowait()
                platform = activity.platform.lower()
                with self._buffer_lock:
                    if platform not in self._platform_buffers:
                        self._platform_buffers[platform] = []
                    self._platform_buffers[platform].append(activity)
            except Empty:
                break
        
        # textSendtextActive（textBATCH_SIZEtext）
        with self._buffer_lock:
            for platform, buffer in self._platform_buffers.items():
                if buffer:
                    display_name = self._get_platform_display_name(platform)
                    logger.info(f"Send{display_name}text {len(buffer)} textActive")
                    self._send_batch_activities(buffer, platform)
            # Cleartext
            for platform in self._platform_buffers:
                self._platform_buffers[platform] = []
    
    def get_stats(self) -> Dict[str, Any]:
        """GetStatisticsInformation"""
        with self._buffer_lock:
            buffer_sizes = {p: len(b) for p, b in self._platform_buffers.items()}
        
        return {
            "graph_id": self.graph_id,
            "batch_size": self.BATCH_SIZE,
            "total_activities": self._total_activities,  # AddtextQueuetextActivetext
            "batches_sent": self._total_sent,            # SuccessSendtext
            "items_sent": self._total_items_sent,        # SuccessSendtextActivetext
            "failed_count": self._failed_count,          # SendFailedtext
            "skipped_count": self._skipped_count,        # textFilterSkiptextActivetext（DO_NOTHING）
            "queue_size": self._activity_queue.qsize(),
            "buffer_sizes": buffer_sizes,                # text
            "running": self._running,
        }


class ZepGraphMemoryManager:
    """
    textSimulationtextZepGraphtextUpdatetext
    
    textSimulationtextUpdatetextInstance
    """
    
    _updaters: Dict[str, ZepGraphMemoryUpdater] = {}
    _lock = threading.Lock()
    
    @classmethod
    def create_updater(cls, simulation_id: str, graph_id: str) -> ZepGraphMemoryUpdater:
        """
        textSimulationCreateGraphtextUpdatetext
        
        Args:
            simulation_id: SimulationID
            graph_id: ZepGraphID
            
        Returns:
            ZepGraphMemoryUpdaterInstance
        """
        with cls._lock:
            # text，textStoptext
            if simulation_id in cls._updaters:
                cls._updaters[simulation_id].stop()
            
            updater = ZepGraphMemoryUpdater(graph_id)
            updater.start()
            cls._updaters[simulation_id] = updater
            
            logger.info(f"CreateGraphtextUpdatetext: simulation_id={simulation_id}, graph_id={graph_id}")
            return updater
    
    @classmethod
    def get_updater(cls, simulation_id: str) -> Optional[ZepGraphMemoryUpdater]:
        """GetSimulationtextUpdatetext"""
        return cls._updaters.get(simulation_id)
    
    @classmethod
    def stop_updater(cls, simulation_id: str):
        """StoptextRemoveSimulationtextUpdatetext"""
        with cls._lock:
            if simulation_id in cls._updaters:
                cls._updaters[simulation_id].stop()
                del cls._updaters[simulation_id]
                logger.info(f"textStopGraphtextUpdatetext: simulation_id={simulation_id}")
    
    # text stop_all text
    _stop_all_done = False
    
    @classmethod
    def stop_all(cls):
        """StoptextUpdatetext"""
        # text
        if cls._stop_all_done:
            return
        cls._stop_all_done = True
        
        with cls._lock:
            if cls._updaters:
                for simulation_id, updater in list(cls._updaters.items()):
                    try:
                        updater.stop()
                    except Exception as e:
                        logger.error(f"StopUpdatetextFailed: simulation_id={simulation_id}, error={e}")
                cls._updaters.clear()
            logger.info("textStoptextGraphtextUpdatetext")
    
    @classmethod
    def get_all_stats(cls) -> Dict[str, Dict[str, Any]]:
        """GettextUpdatetextStatisticsInformation"""
        return {
            sim_id: updater.get_stats() 
            for sim_id, updater in cls._updaters.items()
        }
