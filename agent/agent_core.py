# agent/agent_core.py

from typing import Dict
from agent.agent_init import init_agent
from agent.memory_manager import memory
from agent.singleton_plan import plan_manager_instance as plan_manager
from agent.context import global_state
from agent.tools import get_toolkit


class PetCareAgent:
    def __init__(self):
        """
        初始化 PetCareAgent，內部自動 init_agent()
        """
        self.agent = init_agent()
        self.memory = memory
        self.summary_memory = memory.summary_memory
        self.plan_manager = plan_manager
        self.state = self.memory.get_current_state()
        self.event_log = []

    def run(self, input_json: Dict) -> Dict:
        """
        處理一筆 observation log，讓 LLM Agent 依據 GOAP 流程自主決策並執行行動。
        """
        observation = input_json

        # 檢查是否為非異常行為
        behavior = observation.get("action")
        if self.memory.is_behavior_excluded(behavior):
            response = f"行為「{behavior}」已標記為非異常，無需處理。"
            self.summary_memory.add_user_message(str(observation))
            self.summary_memory.add_ai_message(response)
            self.memory.record_event(observation, action="略過（非異常行為）", effectiveness="無需處理")
            self.summary_memory.get_summary()
            return {
                "input": input_json,
                "agent_response": response
            }

        completed = False
        full_steps = []

        while not completed:
            related_memory = self.memory.search_similar_memory(str(observation))
            print(related_memory)
            prompt_input = {
                "input": f"觀察: {observation}\n相關記憶: {related_memory}",
                "tools": "\n".join([f"- {tool.__name__}: {tool.__doc__}" for tool in get_toolkit()])
            }

            steps = list(self.agent.stream(prompt_input))
            full_steps.extend(steps)

            # 檢查是否完成
            for block in steps:
                if 'output' in block:
                    output_text = block['output']
                    if "完成" in output_text or "無需進一步行動" in output_text:
                        completed = True
                        break

            if not completed:
                # 如果還沒完成，模擬新的 observation
                observation = self._simulate_new_observation(steps)

            # 最後一次 memory更新
        final_output = self._extract_final_output_from_steps(full_steps)
        actions_taken = self._extract_actions_from_steps(full_steps)

        # 儲存摘要/事件的工作丟到副線程做，不阻塞主流程
        asyncio.create_task(self._async_memory_save(observation, final_output, actions_taken))

        return {
            "input": input_json,
            "agent_response": final_output
        }

    def _extract_final_output_from_steps(self, steps) -> str:
        for block in reversed(steps):
            if 'output' in block:
                return block['output']
        return "無最終回覆"

    def _extract_actions_from_steps(self, steps) -> str:
        actions = []
        for block in steps:
            if 'steps' in block:
                for s in block['steps']:
                    if hasattr(s, "action") and s.action is not None:
                        actions.append(f"{s.action.tool}({s.action.tool_input})")
            if 'actions' in block:
                for a in block['actions']:
                    if hasattr(a, "tool") and a.tool is not None:
                        actions.append(f"{a.tool}({a.tool_input})")
        return " -> ".join(actions) if actions else "無行動"

    def _simulate_new_observation(self, steps) -> Dict:
        """
        根據最近的行動模擬一個更合理的新的 Observation。
        """
        last_action = None

        for block in reversed(steps):
            if 'actions' in block:
                for a in block['actions']:
                    if hasattr(a, "tool") and a.tool:
                        last_action = a.tool
                        break
            if 'steps' in block:
                for s in block['steps']:
                    if hasattr(s, "action") and s.action:
                        last_action = s.action.tool
                        break
            if last_action:
                break

        # 改成更合理的模擬行為
        if last_action == "play_music":
            return {
                "time": "模擬時間",
                "action": "步行",
                "地點": "客廳"
            }
        elif last_action == "start_feeder":
            return {
                "time": "模擬時間",
                "action": "完成餵食，狗狗正在安靜休息",
                "地點": "餐廳"
            }
        elif last_action == "notify_owner" or last_action == "record_event":
            return {
                "time": "模擬時間",
                "action": "靜止休息",
                "地點": "客廳"
            }
        elif last_action == "adjust_aircon":
            return {
                "time": "模擬時間",
                "action": "靜止",
                "地點": "原地"
            }
        else:
            # Default fallback
            return {
                "time": "模擬時間",
                "action": "步行",
                "地點": "原地"
            }
