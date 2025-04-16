from langchain_community.tools import tool
from datetime import datetime

temp = 28
last_feed_time = None

@tool
def notify_owner() -> str:
  """通知寵物的飼主"""
  print("已通知主人0")
  return "已通知主人"

@tool
def advise_see_doctor() -> str:
  """建議飼主帶寵物就醫"""
  return "建議就醫，請盡快安排看診"

@tool
def turn_on_ac() -> str:
  """開冷氣並降低溫度"""
  global temp
  temp -= 2
  return f"開冷氣 → 降低溫度，目前溫度：{temp}"

@tool
def feed_pet() -> str:
  """餵食寵物並記錄時間"""
  global last_feed_time
  last_feed_time = datetime.now()
  return f"餵食 → 記錄餵食時間：{last_feed_time.strftime('%Y-%m-%d %H:%M:%S')}"

@tool
def set_petcare_status(status: str) -> str:
  """根據建議模式切換寵物照護狀態：一般 / 觀察 / 緊急"""
  if status == "緊急":
    return "已切換至緊急模式，請立即通知飼主並建議就醫。"
  elif status == "觀察":
    return "已切換至觀察模式，請定期記錄並提醒飼主注意。"
  elif status == "一般":
    return "已切換至一般模式，持續進行日常監控。"
  else:
    return f"無效的模式：{status}"

@tool
def analyze_behavior(task: str) -> dict:
    """
    分析異常行為，返回可能原因和建議。
    """
    # 模擬分析過程
    analysis = {
        "task": task,
        "建議模式": "觀察",  # 可根據行為設定「一般」/「觀察」/「緊急」
        "可能原因": "耳朵發炎或過敏",
        "應對方案": "觀察並避免過度抓撓",
        "是否需通知飼主": True,
        "是否建議就醫": False
    }
    return analysis