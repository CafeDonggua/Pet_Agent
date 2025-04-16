# context.py

class SharedState:
  def __init__(self):
    self.temp = "未知"

# 全域唯一的共享狀態實例
global_state = SharedState()