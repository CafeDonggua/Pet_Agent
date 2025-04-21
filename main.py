# main.py

import time
from agent.agent_init import init_agent
from agent.tools import get_toolkit
from agent.utils import load_input_json, get_latest_data, store_agent_response
from agent.agent_core import PetCareAgent
from agent.context import global_state


def main():
    # 1. 讀入 JSON 輸入
    output_path = "./output/response.json"
    last_processed_time = "20250000000000"  # 初始時間戳記，設定為最早的時間

    # 初始化 LangChain agent_executor
    agent_executor = init_agent(get_toolkit())

    # 創建 PetCareAgent 實例
    core = PetCareAgent(agent_executor)

    while True:
        input_data = load_input_json("./input/sample.json")
        # 2. 根據時間戳記過濾新資料
        new_data = get_latest_data(input_data, last_processed_time)

        if new_data:
            # 3. 初始化工具與 Agent
            toolkit = get_toolkit()
            agent = init_agent(toolkit)  # LLM Agent：自然語言輸出

            # 4. 執行 Agent 並處理新資料
            for data in new_data:
                if "室溫" in data:
                    global_state.temp = data["室溫"]

                # 使用 AgentCore 處理邏輯決策
                reasoning_result = core.run(data)
                # 使用 LLM Agent 處理自然語言輸出
                response = agent.invoke({"input": data})

                # 整合結果：你可以選擇只儲存 LLM 輸出、reasoning，或兩者並存
                final_output = {
                    "摘要建議": reasoning_result,
                    "模型回應": response
                }
                # 5. 儲存結果或進一步通知
                store_agent_response(final_output, output_path)

                # 更新 last_processed_time 為這筆資料的時間戳記
                last_processed_time = data["時間"]

            # 6. 每 3 秒檢查一次
            time.sleep(3)
            core.memory.vector_memory.save()
            # 在此時進行儲存


if __name__ == "__main__":
    main()
