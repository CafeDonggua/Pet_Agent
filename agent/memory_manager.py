# memory_manager.py

import json
import os
from typing import Dict, List, Optional
from agent.summary_memory import SummaryMemory
from agent.singleton_memory import vector_memory_instance


class MemoryManager:
    def __init__(self, memory_path: str = "../memory/memory.json"):
        self.memory_path = memory_path
        self.memory = {
            "current_state": "一般",  # 可為：一般、觀察、緊急
            "events": [],
            "excluded_behaviors": [],
            "abnormal_behavior":[]
        }
        self.load_memory()

        # 新增的記憶系統
        self.summary_memory = SummaryMemory()
        self.vector_memory = vector_memory_instance

    def load_memory(self):
        if os.path.exists(self.memory_path):
            with open(self.memory_path, "r", encoding="utf-8") as f:
                self.memory = json.load(f)

    def save_memory(self):
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        with open(self.memory_path, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)

    def update_state(self, new_state: str):
        self.memory["current_state"] = new_state
        self.save_memory()

    def get_current_state(self) -> str:
        return self.memory.get("current_state", "一般")

    def record_event(self, trigger: Dict, action: str, effectiveness: str):
        event = {
            "trigger": trigger,
            "action": action,
            "effectiveness": effectiveness
        }
        self.memory["events"].append(event)
        self.save_memory()

    def get_similar_events(self, current_input: Dict) -> List[Dict]:
        # 這裡先用簡單的 key 匹配篩選類似事件
        # 可再進化為相似度比對（如 cosine similarity）
        similar = []
        for event in self.memory["events"]:
            if event["trigger"].get("狀態") == current_input.get("狀態"):
                similar.append(event)
        return similar

    def add_excluded_behavior(self, behavior: str):
        if behavior not in self.memory["excluded_behaviors"]:
            self.memory["excluded_behaviors"].append(behavior)
            self.save_memory()

    def is_behavior_excluded(self, behavior: str) -> bool:
        return behavior in self.memory.get("excluded_behaviors", [])

    # 新增對話記憶與摘要同步
    def add_conversation(self, user_input: str, ai_output: str):
        self.summary_memory.add_user_message(user_input)
        self.summary_memory.add_ai_message(ai_output)
        summary = self.summary_memory.get_summary()
        if summary:
            print(f"[摘要更新] 新摘要已寫入向量資料庫：\n{summary[:50]}...")

    def search_similar_memory(self, query: str):
        return self.vector_memory.query_memory(query)


memory = MemoryManager()
