# agent/goap/goal_manager.py
from typing import Optional, Dict

class GoalManager:
    def __init__(self):
        self.current_goal = None  # 目前只有一個活躍目標（未來可以擴展多目標）

    def add_goal(self, goal: Dict):
        """
        設定一個新的目標。
        Args:
          goal (dict): 包含目標資訊，例如 {'目標': '叫醒狗狗', '條件': {...}}
        """
        self.current_goal = goal

    def get_current_goal(self) -> Optional[Dict]:
        """取得目前的目標（如果有的話）"""
        return self.current_goal

    def has_active_goal(self) -> bool:
        """是否有活躍目標"""
        return self.current_goal is not None

    def update_goal(self, world_state: Dict) -> bool:
        """
        更新目標狀態，判斷是否達成。
        Args:
          world_state (dict): 當前世界狀態資料
        Returns:
          bool: 是否已完成目標
        """
        if not self.current_goal:
            return False

        # 這裡假設每個目標都有一組"完成條件"，只要符合條件就算達成
        conditions = self.current_goal.get("條件", {})
        for key, value in conditions.items():
            if world_state.get(key) != value:
                return False  # 尚未達成

        return True  # 條件都符合，目標完成

    def remove_goal(self):
        """移除已完成或取消的目標"""
        self.current_goal = None