import json
from datetime import datetime
from agent.utils import parse_llm_response

def read_log(self, log, tools):
  self.pet_state = log
  self.behavior_log.append(log)
  behavior = log.get("行為")

  if behavior in self.known_behaviors:
    self.handle_abnormal_behavior(behavior)
  else:
    result = self.agent_executor.invoke({"task": behavior},tools=tools,)

    try:
      # 解析 LLM 回應
      action_data = parse_llm_response(result)
      # 執行 LLM 回應的動作
      self._execute_response(action_data)
    except Exception as e:
      print("⚠️ LLM 回應解析失敗：", e)
      print("原始回應：", result)

def handle_abnormal_behavior(self, behavior):
  result = self.chain.invoke({"task": behavior})
  try:
    data = json.loads(result)
  except json.JSONDecodeError:
    print("解析失敗：", result)
    return

  self._execute_response(data)
  self.status = data.get("建議模式", self.status)
  self.abnormal_behaviors[datetime.now().strftime("%H:%M:%S")] = data

def _execute_response(self, action_data):
  if action_data.get("是否需通知飼主"):
    print("已通知主人")

  if action_data.get("是否建議就醫"):
    print("建議就醫，請盡快安排看診")

  response = action_data.get("應對方案", "")

  if "開冷氣" in response:
    self.temp -= 2
    print(f"執行動作：開冷氣 → 降低溫度，目前溫度：{self.temp}")

  if "餵食" in response:
    self.last_feed_time = datetime.now()
    print(f"執行動作：餵食 → 記錄餵食時間：{self.last_feed_time.strftime('%Y-%m-%d %H:%M:%S')}")

def daily_review(self):
  if self.last_review_date == datetime.now().date():
    return  # 當天已經回顧過

  print("\n🐾 每日總結（異常行為）")
  for time, log in self.abnormal_behaviors.items():
    print(f"{time} → {log['task']}（模式：{log['建議模式']}）")

  self.abnormal_behaviors.clear()
  self.last_review_date = datetime.now().date()
