# agent/goap/world_state_manager.py

from typing import Dict, Any, Optional

class WorldStateManager:
    def __init__(self):
        self.state: Dict[str, Any] = {}

    def set_state(self, key: str, value: Any):
        """
        設定一個單獨的世界事實。
        """
        self.state[key] = value

    def get_state(self) -> Dict[str, Any]:
        """
        取得完整的世界狀態。
        """
        return self.state

    def get_fact(self, key: str) -> Optional[Any]:
        """
        查詢單一事實。
        """
        return self.state.get(key)

    def update_states(self, updates: Dict[str, Any]):
        """
        批量更新多個事實。
        """
        self.state.update(updates)

    def reset(self):
        """
        清空世界狀態。
        """
        self.state.clear()

if __name__ == "__main__":
    world = WorldStateManager()

    world.set_state("狗狗狀態", "睡覺中")
    world.set_state("室溫", 26)

    print(world.get_state())
    # {'狗狗狀態': '睡覺中', '室溫': 26}

    world.update_states({"狗狗狀態": "醒來", "餵食時間": True})

    print(world.get_fact("狗狗狀態"))
    # 醒來