# agent_core.py

import json
from typing import Dict


class PetCareAgent:
    def __init__(self, agent_executor):
        """
        初始化 PetCareAgent。

        Args:
          agent_executor: 由 LangChain 建立的可執行 agent。
        """
        self.agent = agent_executor
        self.memory = []  # 簡易記憶模擬（可改為向量記憶等）

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
