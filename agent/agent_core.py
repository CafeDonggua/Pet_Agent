# agent_core.py

import json
from typing import Dict
from agent.memory_manager import memory
from agent.singleton_plan import plan_manager_instance as plan_manager

class PetCareAgent:
    def __init__(self, agent_executor):
        """
        初始化 PetCareAgent。

        Args:
          agent_executor: 由 LangChain 建立的可執行 agent。
        """
        self.agent = agent_executor
        self.memory = memory  # 使用 Singleton 的 memory 管理
        self.summary_memory = memory.summary_memory  # 專責對話摘要與向量儲存
        self.state = self.memory.get_current_state()  # 初始時讀取當前狀態
        self.event_log = []  # 這裡是用來記錄事件的，可以根據需求擴展
        self.plan_manager = plan_manager   # 負責計畫功能

    def run(self, input_json: Dict) -> Dict:
        """
        執行一次推論與工具使用，根據輸入做出建議並回傳行動摘要。

        Args:
          input_json (Dict): 包含時間、狀態、狗狗行為與地點。

        Returns:
          Dict: Agent 執行後的應對建議與工具操作紀錄。
        """
        # 擷取關鍵欄位
        time = input_json.get("時間")
        level = input_json.get("等級")
        status = input_json.get("狀態")
        location = input_json.get("地點")

        if self.memory.is_behavior_excluded(status):
            return {
                "input": input_json,
                "agent_response": f"忽略排除的行為：{status}"
            }

        prompt = self._build_prompt(input_json)  # 生成prompt的描述
        summary = self.summary_memory.get_summary() # get目前累積的摘要：背景知識

        self.summary_memory.add_user_message(prompt)  # 更新摘要記憶：加入 user 輸入
        steps  =list(self.agent.stream({"input": input_json, "memory_summary": summary}))
        action_taken  = self._extract_actions_from_stream_steps(steps)
        # 最後一個步驟的 Final Answer
        final_output = self._extract_final_output_from_stream_steps(steps)

        self.summary_memory.add_ai_message(final_output)  # 更新摘要記憶：加入 agent 回應

        event = {
            "時間": time,
            "等級": level,
            "狀態": status,
            "地點": location,
            "應對": action_taken or "無特定行動"
        }
        self.memory.record_event(event, action_taken, effectiveness="待觀察")
        self.summary_memory.get_summary()  # 更新摘要（並寫入 vector DB）
        self.memory.vector_memory.save()

        # 儲存當下模式狀態（方便推論結果附加提示用）
        current_state = self.memory.get_current_state()
        return {
            "input": input_json,
            "agent_response": f"[{current_state}] {final_output}"
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

    def _extract_actions_from_stream_steps(self, steps) -> str:
        """
        從 Agent stream() 流中的步驟提取所有的 action 使用紀錄。
        """
        actions = []
        for block in steps:
            # 先看 'steps' 裡有沒有
            if 'steps' in block:
                for s in block['steps']:
                    if hasattr(s, "action") and s.action is not None:
                        tool_name = s.action.tool
                        tool_input = s.action.tool_input
                        actions.append(f"{tool_name}({tool_input})")
            # 再看 'actions' 裡有沒有
            if 'actions' in block:
                for a in block['actions']:
                    if hasattr(a, "tool") and a.tool is not None:
                        tool_name = a.tool
                        tool_input = a.tool_input
                        actions.append(f"{tool_name}({tool_input})")

        return " -> ".join(actions) if actions else "無行動"

    def _extract_final_output_from_stream_steps(self, steps) -> str:
        for block in reversed(steps):
            if 'output' in block:
                return block['output']
        return "無最終回覆"