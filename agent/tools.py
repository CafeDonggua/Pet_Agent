# tools.py
from typing import Optional
from agent.context import global_state
from agent.memory_manager import memory
from agent.vector_memory import VectorMemory
from agent.summary_memory import SummaryMemory


def none(self) -> str:
    """
    不用動作
    """


def check_current_state() -> str:
    """
    回傳目前的系統狀態。

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
    memory.update_state(memory.new_state)
    return f"已將狀態切換為 {new_status}"


def check_temp(self) -> str:
    """
    確認目前的室內溫度。

    Returns:
      str: 當前室內溫度（例如：'目前室內溫度為 28°C'）。
    """
    return "目前室內溫度為 {global_state.temp}"


def adjust_aircon(target_temp: int) -> str:
    """
    調整冷氣的溫度。

    Args:
      target_temp (int): 目標冷氣溫度（°C）。

    Returns:
      str: 調整結果。
    """
    return f"已將冷氣調整至 {target_temp}°C"


def start_feeder() -> str:
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
    return f"已記錄異常行為：{event}"

def search_vector_memory(query: str) -> str:
    """
    查詢向量記憶資料庫，找出最相關的記憶內容。

    Args:
        query (str): 查詢的關鍵字或句子

    Returns:
        str: 匹配的記憶內容（文字格式）
    """
    vm = VectorMemory()
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

def get_toolkit():
    return [
        none,
        switch_status,
        check_temp,
        adjust_aircon,
        start_feeder,
        notify_vet,
        notify_owner,
        record_event,
        search_vector_memory,
        search_summary_memory,
    ]
