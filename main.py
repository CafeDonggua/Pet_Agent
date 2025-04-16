# main.py
from agent.agent_init import init_agent
from agent.tools import get_toolkit
from agent.utils import load_input_json, store_agent_response


def main():
    # 1. 讀入 JSON 輸入
    input_data = load_input_json("./input/sample.json")

    # 2. 初始化工具與 Agent
    toolkit = get_toolkit()
    agent = init_agent(toolkit)

    # 3. 執行 Agent
    response = agent.invoke({"input": input_data})

    # 4. 儲存結果或進一步通知
    store_agent_response(response)


if __name__ == "__main__":
    main()
