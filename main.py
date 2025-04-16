#pip install langchain langchain-community
#pip install -U langchain-community
#pip install openai

import os
import time
import json
from datetime import datetime
from dotenv import load_dotenv
from agent.agent_init import PetCareAgent
from agent.agent_core import read_log, handle_abnormal_behavior, daily_review, _execute_response
from agent.tools import notify_owner, advise_see_doctor, turn_on_ac, feed_pet



# 取得 API Key
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")


pet_ai = PetCareAgent( model="gpt-4o-mini")

# 手動把方法綁上 instance（或 refactor 成 class method）
pet_ai.read_log = read_log.__get__(pet_ai)
pet_ai.handle_abnormal_behavior = handle_abnormal_behavior.__get__(pet_ai)
pet_ai._execute_response = _execute_response.__get__(pet_ai)
pet_ai.daily_review = daily_review.__get__(pet_ai)

tools = [
    notify_owner,
    advise_see_doctor,
    turn_on_ac,
    feed_pet
]

# 進入主迴圈
while True:
  user_input = input("請輸入 LOG（JSON）：")
  #user_input = '{"時間": "20250326100000", "狀態": "一般", "行為": "坐著", "位置": "沙發上"}'

  print(type(user_input))
  try:
    simulated_log = json.loads(user_input)
    pet_ai.read_log(log=simulated_log, tools=tools)
  except json.JSONDecodeError as e:
    print("JSON 格式錯誤：", e)
  except Exception as e:
    print("格式錯誤，請重新輸入。", e)


  if datetime.now().strftime("%H:%M:%S") >= "20:00:00":
    pet_ai.daily_review()

  time.sleep(pet_ai.log_frequency[pet_ai.status])
