# main.py

import time
from agent.agent_core import PetCareAgent
from agent.utils import load_input_json, get_latest_data, store_agent_response

def main():
    input_path = "./input/sample.json"
    output_path = "./output/response.json"
    last_processed_time = "20250000000000"

    agent = PetCareAgent()

    while True:
        input_data = load_input_json(input_path)
        new_data = get_latest_data(input_data, last_processed_time)

        if new_data:
            for data in new_data:
                result = agent.run(data)
                store_agent_response(result, output_path)
                last_processed_time = data["time"]
            time.sleep(3)
        else:
            print("[Main] 暫無新資料，等待中...")
            time.sleep(3)

if __name__ == "__main__":
    main()
