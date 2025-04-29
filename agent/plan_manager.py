import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class PlanManager:
    PLAN_PATH = "./memory/plan.json"

    def __init__(self, path: str = "./memory/plan.json"):
        self.path = path
        self.plan = {
            "daily_plan": [],
            "current_plan": [],
            "最後更新時間": ""
        }
        self.load()

    def load(self):
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                self.plan = json.load(f)
        else:
            self.save()

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.plan, f, ensure_ascii=False, indent=2)

    def initialize_today_plan(self):
        """
        根據每日計畫，依據今天是星期幾，自動初始化 current_plan。
        """
        today = datetime.now().strftime("%A")  # 例如 'Monday'

        filtered = []

        for item in self.plan.get("daily_plan", []):
            frequency = item.get("頻率", "每日")

            if frequency == "每日":
                filtered.append(item)
            elif frequency == "週一到週五" and today in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
                filtered.append(item)
            elif frequency == "週末" and today in ["Saturday", "Sunday"]:
                filtered.append(item)
            elif frequency == today:  # 允許直接寫頻率為 'Monday' 等
                filtered.append(item)

        # 將符合的項目放入 current_plan
        self.plan["current_plan"] = filtered
        self.plan["最後更新時間"] = datetime.now().isoformat(timespec='seconds')
        self.save()

        print(f"[PlanInit] 今日 ({today}) 已載入 {len(filtered)} 則計畫項目至 current_plan")

    def get_daily_plan(self) -> List[Dict]: #取得每日固定計畫
        return self.plan.get("daily_plan", [])

    def get_current_plan(self) -> List[Dict]:   #取得目前應執行的行為序列
        return self.plan.get("current_plan", [])

    def add_to_current_plan(self, time_str: str, action: str, source: str = "自動新增") -> None:    #新增新任務並標註是否與 daily plan 衝突
        conflict = any(p["time"] == time_str and p["action"] != action for p in self.plan["daily_plan"])
        self.plan["current_plan"].append({
            "time": time_str,
            "action": action,
            "來源": source,
            "衝突": conflict
        })
        self.plan["最後更新時間"] = datetime.now().isoformat(timespec='seconds')
        self.save()

    def check_conflict(self, time_str: str, action: str) -> bool:   #主動檢查特定行為是否衝突
        return any(p["time"] == time_str and p["action"] != action for p in self.plan["daily_plan"])

    def clear_current_plan(self):   #清空目前計畫
        self.plan["current_plan"] = []
        self.save()

    def check_plan_conflict(self, new_task: Dict) -> bool:
        """
        檢查新任務是否與目前計畫衝突。
        Args:
            new_task (Dict): 包含 "time" 與 "action" 的新任務。
        Returns:
            bool: 是否衝突。
        """
        for task in self.get_current_plan():
            if task["time"] == new_task["time"] and task["action"] != new_task["action"]:
                return True
        return False

    def insert_plan_item(self, new_task: Dict, source: str = "動態新增") -> str:
        """
        插入新任務到 current_plan，會自動標記是否與既有計畫衝突。
        Args:
            new_task (Dict): 含時間與行為等資訊的任務
            source (str): 任務來源註記
        Returns:
            str: 結果說明
        """
        conflict = self.check_plan_conflict(new_task)
        new_task_entry = {
            "time": new_task["time"],
            "action": new_task["action"],
            "來源": source,
            "衝突": conflict
        }
        self.plan["current_plan"].append(new_task_entry)
        self.plan["最後更新時間"] = datetime.now().isoformat(timespec='seconds')
        self.save()
        return "已新增任務，並標記衝突" if conflict else "已新增任務"

# Debug 測試
if __name__ == "__main__":
    pm = PlanManager()
    pm.add_to_current_plan("16:00", "播放音樂")
    print(json.dumps(pm.plan, ensure_ascii=False, indent=2))
