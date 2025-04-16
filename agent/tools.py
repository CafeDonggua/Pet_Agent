# tools.py
from typing import Optional


def switch_status(new_status: str) -> str:
    """
    更改目前的預警狀態。

    Args:
      new_status (str): 目標狀態，應為 '一般'、'觀察' 或 '緊急'。

    Returns:
      str: 狀態更改結果回應。
    """
    return f"已將狀態切換為 {new_status}"


def check_temp(self) -> str:
    """
    確認目前的室內溫度。

    Returns:
      str: 當前室內溫度（例如：'目前室內溫度為 28°C'）。
    """
    return "目前室內溫度為 28°C"


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


def get_toolkit():
    return [
        switch_status,
        check_temp,
        adjust_aircon,
        start_feeder,
        notify_vet,
        notify_owner,
        record_event,
    ]
