# main.py
from agent.agent_init import init_agent
from agent.tools import get_toolkit
from agent.utils import load_input_json,get_latest_data, store_agent_response
import time
from agent.context import global_state


def main():
    # 1. 讀入 JSON 輸入
    output_path = "./output/response.json"
    last_processed_time = "20250000000000"  # 初始時間戳記，設定為最早的時間

    while(True):
        input_data = load_input_json("./input/sample.json")
        # 2. 根據時間戳記過濾新資料
        new_data = get_latest_data(input_data, last_processed_time)

        if new_data:
            # 3. 初始化工具與 Agent
            toolkit = get_toolkit()
            agent = init_agent(toolkit)

            # 4. 執行 Agent 並處理新資料
            for data in new_data:
                if "室溫" in data:
                    global_state.temp = data["室溫"]
                response = agent.invoke({"input": data})

                # 5. 儲存結果或進一步通知
                store_agent_response(response, output_path)

                # 更新 last_processed_time 為這筆資料的時間戳記
                last_processed_time = data["時間"]

            # 6. 每 3 秒檢查一次
            time.sleep(3)


if __name__ == "__main__":
    main()
