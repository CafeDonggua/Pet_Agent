# agent/goap/action_registry.py

from typing import Callable, Dict, Any, List

class Action:
    def __init__(self, name: str, preconditions: Dict[str, Any], effects: Dict[str, Any], executor: Callable):
        self.name = name
        self.preconditions = preconditions
        self.effects = effects
        self.executor = executor

    def check_preconditions(self, world_state: Dict[str, Any], goal: Dict[str, Any]) -> bool:
        """
        檢查這個行動是否可以在目前的世界狀態下執行。
        """
        for key, value in self.preconditions.items():
            if world_state.get(key) != value:
                return False
        return True

    def execute(self, world_state: Dict[str, Any]) -> bool:
        """
        執行行動，並套用 effects 更新世界狀態。
        """
        success = self.executor()
        if success:
            world_state.update(self.effects)
        return success

class ActionRegistry:
    def __init__(self):
        self.actions: List[Action] = []

    def register_action(self, name: str, preconditions: Dict[str, Any], effects: Dict[str, Any], executor: Callable):
        action = Action(name, preconditions, effects, executor)
        self.actions.append(action)

    def get_available_actions(self, world_state: Dict[str, Any], goal: Dict[str, Any]) -> List[Action]:
        """
        根據當前世界狀態與目標，回傳可以執行的行動清單。
        """
        available = []
        for action in self.actions:
            if action.check_preconditions(world_state, goal):
                available.append(action)
        return available

    def list_actions(self) -> List[str]:
        return [action.name for action in self.actions]

# --------------------
# 以下是範例行動的定義與登錄
# --------------------

def play_music_executor():
    print("播放輕快音樂喚醒狗狗！")
    return True

def notify_owner_executor():
    print("通知主人：狗狗已醒來，可以互動！")
    return True

def start_feeder_executor():
    print("啟動餵食機，狗狗正在進食！")
    return True

# 初始化 ActionRegistry 並註冊行動
action_registry = ActionRegistry()

action_registry.register_action(
    name="play_music",
    preconditions={"is_awake": False},
    effects={"is_awake": True},
    executor=play_music_executor
)

action_registry.register_action(
    name="notify_owner",
    preconditions={"is_awake": True},
    effects={"owner_notified": True},
    executor=notify_owner_executor
)

action_registry.register_action(
    name="start_feeder",
    preconditions={"is_hungry": True},
    effects={"is_hungry": False},
    executor=start_feeder_executor
)

if __name__ == "__main__":
    print("已註冊的行動:")
    for name in action_registry.list_actions():
        print(f"- {name}")
