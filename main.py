# main.py

import time
from agent.agent_core import PetCareAgent
from agent.utils import load_input_json, get_latest_data, store_agent_response

def main():
    input_path = "./input/sample.json"
    output_path = "./output/response.json"
    last_processed_time = "20250000000000"  # 初始時間戳記

    # 初始化新版 GOAP Agent
    agent = PetCareAgent()

    while True:
        try:
            # 讀取輸入資料
            input_data = load_input_json(input_path)
            new_data = get_latest_data(input_data, last_processed_time)

            if new_data:
                for data in new_data:
                    # 1. 更新世界狀態並執行 GOAP 決策
                    result = agent.run(data)

                    # 2. 儲存處理結果
                    store_agent_response(result, output_path)

                    # 3. 更新最後處理時間
                    last_processed_time = data["時間"]

                print(f"[Main] 本次處理 {len(new_data)} 筆新資料。")

            else:
                print("[Main] 暫無新資料，等待中...")

            # 每 3 秒檢查一次
            time.sleep(3)

        except Exception as e:
            print(f"[Main] 發生錯誤：{e}")
            time.sleep(3)  # 出錯也休息一下再試

if __name__ == "__main__":
    main()
