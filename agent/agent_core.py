# agent_core.py

import json
from typing import Dict
from agent.memory_manager import memory

class PetCareAgent:
    def __init__(self, agent_executor):
        """
        初始化 PetCareAgent。

        Args:
          agent_executor: 由 LangChain 建立的可執行 agent。
        """
        self.agent = agent_executor
        self.memory = memory  # 使用 Singleton 的 memory 管理
        self.state = memory.get_current_state()  # 初始時讀取當前狀態
        self.event_log = []  # 這裡是用來記錄事件的，可以根據需求擴展

    def process_input(self, input_data: dict) -> str:
        """
        根據輸入資料進行推理與決策。

        Args:
          input_data (dict): 包含時間、等級、狗狗狀態與地點的 JSON 物件。

        Returns:
          str: 處理結果的摘要建議。
        """
        # 擷取關鍵欄位
        time = input_data.get("時間")
        level = input_data.get("等級")
        status = input_data.get("狀態")
        location = input_data.get("地點")

        # 設定 action 和 effectiveness
        action = ""
        effectiveness = "有效"

        # 檢查是否為排除行為
        if memory.is_behavior_excluded(status):
            return f"忽略排除的行為：{status}"

        # 建立事件記錄
        event = {
            "時間": time,
            "等級": level,
            "狀態": status,
            "地點": location,
            "應對": "尚未決策"
        }
        self.memory.record_event(event, action, effectiveness)

        # 根據目前模式決定行動
        current_state = self.memory.get_current_state()

        if level == "緊急":
            response = "偵測到緊急狀況，請立即通知主人或聯絡獸醫。"
        elif level == "觀察":
            response = "建議進一步觀察狀況，視情況調整空調或切換狀態。"
        else:
            response = "目前為一般狀況，無需特殊處理。"

        return f"[{current_state}] {response}"

    def run(self, input_json: Dict) -> Dict:
        """
        執行一次推論與工具使用，根據輸入做出建議並回傳行動摘要。

        Args:
          input_json (Dict): 包含時間、狀態、狗狗行為與地點。

        Returns:
          Dict: Agent 執行後的應對建議與工具操作紀錄。
        """
        prompt = self._build_prompt(input_json)
        result = self.agent.run(prompt)

        # 更新記憶
        self.memory.append({
            "input": input_json,
            "response": result
        })

        return {
            "input": input_json,
            "agent_response": result
        }

    def _build_prompt(self, input_json: Dict) -> str:
        """
        建構給 Agent 的描述性任務指令。

        Args:
          input_json (Dict): 來源輸入資料。

        Returns:
          str: 完整的語意描述提示。
        """
        time = input_json.get("時間", "未知")
        level = input_json.get("狀態", "一般")
        status = input_json.get("狗狗狀態", "未知")
        location = input_json.get("地點", "未知")

        return (
            f"現在是 {time}，狗狗目前在 {location}。"
            f"狀態等級為「{level}」，牠現在的樣子是「{status}」。"
            f"請根據目前狀況評估並使用必要的工具（如通知主人、記錄異常等）。"
            f"請輸出你的處理建議與採取的工具行動。"
        )
