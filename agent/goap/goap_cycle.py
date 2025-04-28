# agent/goap/goap_cycle.py

from typing import Dict, Any
from agent.goap.action_registry import action_registry
from agent.goap.goal_manager import GoalManager
from agent.goap.world_state_manager import WorldStateManager
from agent.goap.action_planner import ActionPlanner

# 這邊預設 goals，可以之後改成從外部讀入
default_goals = [
    {
        "name": "喚醒狗狗並通知主人",
        "desired_state": {
            "is_awake": True,
            "owner_notified": True
        },
        "priority": 1
    },
    {
        "name": "讓狗狗吃飽",
        "desired_state": {
            "is_hungry": False
        },
        "priority": 2
    }
]

def is_goal_completed(world_state: Dict[str, Any], desired_state: Dict[str, Any]) -> bool:
    for key, value in desired_state.items():
        if world_state.get(key) != value:
            return False
    return True

def goap_cycle(
    world_state_manager: WorldStateManager,
    goal_manager: GoalManager,
    action_planner: ActionPlanner,
):
    """
    GOAP 主循環：感知 -> 決策 -> 規劃 -> 執行 -> 更新
    """
    world_state = world_state_manager.get_state()

    if not goal_manager.has_active_goal():
        for goal in sorted(default_goals, key=lambda g: g["priority"]):
            if not is_goal_completed(world_state, goal["desired_state"]):
                goal_manager.add_goal(goal)
                goal_name = goal.get("name", "未知目標")
                print(f"[GOAP] 設定新目標: {goal_name}")
                break
        else:
            print("[GOAP] 沒有需要完成的目標，結束 cycle。")
            return

    current_goal = goal_manager.get_current_goal()
    if not current_goal:
        print("[GOAP] 找不到活躍目標。")
        return

    action = action_planner.plan(world_state, current_goal)
    if not action:
        goal_name = current_goal.get("name", "未知目標")
        print(f"[GOAP] 無可執行行動以達成目標: {goal_name}")
        return

    print(f"[GOAP] 執行行動: {action.name}")
    success = action.execute(world_state)

    if success:
        world_state_manager.update_states(action.effects)
        print(f"[GOAP] 行動成功，已更新世界狀態: {action.effects}")
    else:
        print(f"[GOAP] 行動執行失敗。")

    if goal_manager.update_goal(world_state_manager.get_state()):
        goal_name = current_goal.get("name", "未知目標")
        print(f"[GOAP] 目標已完成: {goal_name}")
        goal_manager.remove_goal()