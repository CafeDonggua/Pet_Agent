from typing import Optional, Dict

from agent.context import global_state
from agent.memory_manager import memory
from agent.singleton_memory import vector_memory_instance
from agent.summary_memory import SummaryMemory
from agent.singleton_plan import plan_manager_instance as plan_manager
import json

def check_current_state(_: Optional[str] = None) -> str:
    """
    回傳目前系統狀態（模式）。

    Returns:
      str: 狀態描述（例如：'目前狀態為觀察模式'）。
    """
    return f"目前狀態為 {memory.get_current_state()} 模式"


def switch_status(new_status: str) -> str:
    """
    更改目前的預警狀態。

    Args:
      new_status (str): 目標狀態，應為 '一般'、'觀察' 或 '緊急'。

    Returns:
      str: 狀態更改結果回應。
    """
    memory.update_state(new_status)
    return f"已將狀態切換為 {new_status}"


def check_temp(self) -> str:
    """
    確認目前的室內溫度。

    Returns:
      str: 當前室內溫度（例如：'目前室內溫度為 28°C'）。
    """
    return f"目前室內溫度為 {global_state.temp}°C"


def adjust_aircon(target_temp: int) -> str:
    """
    調整冷氣溫度。

    Args:
      target_temp (int): 目標冷氣溫度（°C）。

    Returns:
      str: 調整結果。
    """
    global_state.temp=target_temp
    return f"已將冷氣調整至 {target_temp}°C"


def start_feeder(_: Optional[str] = None) -> str:
    """
    啟動餵食機器，讓狗狗進食。

    Returns:
      str: 執行結果說明。
    """
    return "已啟動餵食機器"


def notify_vet(message: Optional[str] = None) -> str:
    """
    通知獸醫狗狗可能出現緊急狀況。

    Args:
      message (Optional[str]): 傳送給獸醫的附加訊息。

    Returns:
      str: 通知回應。
    """
    return f"已通知獸醫：{message or '狗狗出現異常狀況，請盡快確認'}"


def notify_owner(message: Optional[str] = None) -> str:
    """
    通知主人目前狗狗的異常或處理狀況。

    Args:
      message (Optional[str]): 傳送給主人的訊息。

    Returns:
      str: 通知回應。
    """
    return f"已通知主人：{message or '狗狗可能需要關注'}"


def record_event(event: str) -> str:
    """
    記錄新的異常行為。

    Args:
      event (str): 描述要記錄的異常行為。

    Returns:
      str: 記錄結果。
    """

    if event not in memory.memory["abnormal_behavior"]:
        memory.memory["abnormal_behavior"].append(event)
        memory.save_memory()
    return f"已記錄異常行為：{event}"

def search_vector_memory(query: str) -> str:
    """
    查詢向量記憶資料庫，找出最相關的記憶內容。

    Args:
        query (str): 查詢的關鍵字或句子

    Returns:
        str: 匹配的記憶內容（文字格式）
    """
    vm = vector_memory_instance
    results = vm.query_memory(query)
    if not results:
        return "找不到相關記憶。"
    return "\n".join([f"[距離: {r['distance']:.4f}] {r['text']}" for r in results])

def search_summary_memory(query: str) -> str:
    """
    查詢摘要記憶資料庫，找出與摘要最相關的內容。

    Args:
        query (str): 查詢的關鍵字或句子

    Returns:
        str: 匹配的摘要內容（文字格式）
    """
    sm = SummaryMemory()
    results = sm.query_summaries(query)
    if not results:
        return "找不到相關摘要記憶。"
    return "\n".join([f"[距離: {r['distance']:.4f}] {r['text']}" for r in results])

def add_plan_item(input) -> str:
    """
    新增一個行為到當前計畫中。

    Args:
        input (str or dict): JSON 格式字串或字典
        {"time": "時間", "action": "預期行動"}
    Returns:
        str: 新增結果說明。
    """
    try:
        # 如果是 str，先嘗試轉成 dict
        if isinstance(input, str):
            input_dict = json.loads(input)
        else:
            input_dict = input
    except Exception as e:
        return f"解析輸入失敗：{str(e)}"

    # 如果 input_dict 是 list，取第一個元素
    if isinstance(input_dict, list):
        if len(input_dict) == 0:
            return "新增計畫失敗，輸入為空列表。"
        input_dict = input_dict[0]

    time_str = input_dict.get("time")
    action = input_dict.get("action")

    if not time_str or not action:
        return "輸入錯誤，請提供正確的時間 (time) 和行為 (action)。"

    plan_manager.add_to_current_plan(time_str, action, source="agent")
    return f"已新增 {time_str} 的行為「{action}」到計畫中。"

def check_daily_plan_conflict(input) -> str:
    """
        檢查某個指定時間的行為是否與每日固定計畫 (daily_plan) 衝突。

        Args:
            input (str or dict): JSON 格式字串或字典

        Returns:
            str: 衝突檢查的結果說明。
        """
    try:
        # 如果是 str，先嘗試轉成 dict
        if isinstance(input, str):
            input_dict = json.loads(input)
        else:
            input_dict = input
    except Exception as e:
        return f"解析輸入失敗：{str(e)}"

    time_str = input_dict.get("time")
    action = input_dict.get("action")

    if not time_str or not action:
        return "輸入錯誤，請提供正確的時間 (time) 和行為 (action)。"

    daily_plan = plan_manager.get_daily_plan()

    for plan in daily_plan:
        if plan["time"] == time_str:
            if plan["action"] != action:
                return (
                    f"注意：在 {time_str} 已存在計畫「{plan['action']}」，"
                    f"而你要新增的是「{action}」。這將會產生衝突！\n"
                    f"請確認是否要覆蓋原有計畫。"
                )
            else:
                return (
                    f"在 {time_str} 已有相同的行為「{action}」，"
                    "無需再次新增。"
                )

    get_current_plan = plan_manager.get_current_plan()

    for plan in get_current_plan:
        if plan["time"] == time_str:
            if plan["action"] != action:
                return (
                    f"注意：在 {time_str} 已存在計畫「{plan['action']}」，"
                    f"而你要新增的是「{action}」。這將會產生衝突！\n"
                    f"請確認是否要覆蓋原有計畫。"
                )
            else:
                return (
                    f"在 {time_str} 已有相同的行為「{action}」，"
                    "無需再次新增。"
                )

    return f"目前在 {time_str} 沒有任何固定計畫，可以安全新增「{action}」。"

def get_today_plan(_: Optional[str] = None) -> str:
    """
    取得今天的主計畫列表。

    Returns:
        str: 今日計畫描述。
    """
    plans = plan_manager.get_daily_plan()
    if not plans:
        return "今日尚無任何計畫項目。"
    return "\n".join([f"{p['time']} - {p['action']} ({'衝突' if p.get('衝突') else '✔'})" for p in plans])

def wait_and_observe(input_data: str = "無") -> str:
    """
    當前不需要立即行動，進入觀察等待狀態。
    """
    return "目前進入觀察等待狀態，無需立即行動。"

def get_toolkit():
    return [
        switch_status,
        check_temp,
        adjust_aircon,
        start_feeder,
        notify_vet,
        notify_owner,
        record_event,
        search_vector_memory,
        search_summary_memory,
        add_plan_item,
        check_daily_plan_conflict,
        get_today_plan,
        wait_and_observe
    ]
