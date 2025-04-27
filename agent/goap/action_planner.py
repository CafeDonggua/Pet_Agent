# agent/goap/action_planner.py

from typing import List, Dict, Any, Callable

class ActionPlanner:
    def __init__(self):
        self.actions: List[Callable] = []

    def register_action(self, action_fn: Callable):
        """
        註冊一個可以執行的行動（Function）。
        Args:
            action_fn: 需要有 .check_preconditions(world_state) 和 .execute(world_state) 方法
        """
        self.actions.append(action_fn)

    def plan(self, world_state: Dict[str, Any], goal: Dict[str, Any]) -> Callable:
        """
        根據目標與目前世界狀態，決定下一個可以執行的行動。
        Args:
            world_state: 世界的目前狀態
            goal: 目標描述
        Returns:
            Callable: 符合條件的行動 function，或者 None
        """
        # 依序檢查每個行動的前置條件
        for action in self.actions:
            if action.check_preconditions(world_state, goal):
                return action

        return None  # 找不到符合條件的行動

    def list_actions(self) -> List[str]:
        """
        列出目前註冊的所有行動名字。
        """
        return [action.__name__ for action in self.actions]