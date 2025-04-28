# agent/agent_core.py

from typing import Dict
from agent.memory_manager import memory
from agent.singleton_plan import plan_manager_instance as plan_manager
from agent.goap.world_state_manager import WorldStateManager
from agent.goap.goal_manager import GoalManager
from agent.goap.action_planner import ActionPlanner
from agent.goap.action_registry import action_registry
from agent.goap.goap_cycle import goap_cycle
from agent.goap.state_inference_manager import StateInferenceManager

class PetCareAgent:
    def __init__(self):
        """
        初始化新的 GOAP PetCareAgent。
        """
        self.memory = memory
        self.plan_manager = plan_manager
        self.world_state_manager = WorldStateManager()
        self.goal_manager = GoalManager()
        self.action_planner = ActionPlanner()
        self.inference_manager = StateInferenceManager()

        # 將所有已註冊行動放入 planner
        for action in action_registry.actions:
            self.action_planner.register_action(action)

        self.event_log = []

        # 可以設定初始世界狀態
        self.initialize_world_state()

    def initialize_world_state(self):
        """
        預設世界狀態，可依需要客製化
        """
        default_world_state = {
            "is_awake": False,
            "owner_notified": False,
            "is_hungry": True
        }
        self.world_state_manager.update_states(default_world_state)

    def update_world_state_from_input(self, input_json: Dict):
        """
        根據輸入資料更新世界狀態。
        Args:
            input_json (Dict): 來自感測或外部資料的 JSON 格式
        """
        updates = self.inference_manager.infer_state_from_log(input_json)


        if updates:
            self.world_state_manager.update_states(updates)

    def run(self, input_json: Dict) -> Dict:
        """
        接收一筆輸入資料，更新世界狀態並啟動 GOAP 決策循環。
        Args:
            input_json (Dict): 感測輸入資料
        Returns:
            Dict: 本次行動摘要
        """
        # 更新世界狀態
        self.update_world_state_from_input(input_json)

        # 執行 GOAP 流程
        goap_cycle(
            self.world_state_manager,
            self.goal_manager,
            self.action_planner
        )

        # 可以額外記錄摘要、事件（未來擴充用）
        world_snapshot = self.world_state_manager.get_state()
        return {
            "input": input_json,
            "current_world_state": world_snapshot
        }
