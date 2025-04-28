# agent/goap/state_inference_manager.py

from typing import Dict, Any
from datetime import datetime

class StateInferenceManager:
    def __init__(self):
        """
        初始化推理模組，可以根據時間、行為、地點推測內部狀態。
        """
        # 簡易作息設定（可以未來外部配置）
        self.wake_up_time = 7  # 早上7點
        self.breakfast_time = 8  # 早上8點
        self.lunch_time = 12   # 中午12點
        self.dinner_time = 18  # 晚上6點

    def infer_state_from_log(self, log: Dict[str, Any]) -> Dict[str, Any]:
        """
        根據輸入 log 推測內部狀態。
        Args:
            log (dict): 包含時間、狀態、行為、地點等資訊
        Returns:
            dict: 推論後的 WorldState 更新
        """
        updates = {}

        # --- 解析時間
        time_str = log.get("時間", "")
        try:
            log_time = datetime.strptime(time_str, "%Y%m%d%H%M%S")
            hour = log_time.hour
        except Exception:
            hour = None

        # --- 解析行為
        behavior = log.get("行為", "")

        # --- 依據行為推理
        if "趴" in behavior or "躺" in behavior:
            # 如果是趴著/躺著
            if hour is not None and hour >= self.wake_up_time:
                updates["is_awake"] = False  # 早上應該醒來，如果還趴著，視為尚未醒來
        elif "走" in behavior or "玩" in behavior:
            updates["is_awake"] = True  # 有活動則視為醒著

        # --- 依據時間推理餓不餓
        if hour is not None:
            if (self.breakfast_time <= hour < self.breakfast_time + 1) or \
               (self.lunch_time <= hour < self.lunch_time + 1) or \
               (self.dinner_time <= hour < self.dinner_time + 1):
                updates["is_hungry"] = True  # 餐前時段推定為餓
            else:
                updates["is_hungry"] = False

        return updates
