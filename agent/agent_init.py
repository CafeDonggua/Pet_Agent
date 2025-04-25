# agent_init.py

import os
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv, find_dotenv
from pathlib import Path


def init_agent(tools: list):
    """
    使用 GPT-4o 初始化 ReAct Agent。

    Args:
      tools (list): 已註冊的工具函式列表。

    Returns:
      AgentExecutor: 可執行的代理人物件。
    """
    load_dotenv(Path("..\\.env"))
    load_dotenv(find_dotenv())
    chat_key = os.getenv("OPENAI_CHAT_KEY")
    chat_model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

    # 使用 GPT-4o 模型
    llm = ChatOpenAI(
        model=chat_model,
        temperature=0,
        api_key=chat_key
    )

    # 將工具轉換為 LangChain 的 Tool 實例
    langchain_tools = [
        Tool(
            name=tool.__name__,
            func=tool,
            description=tool.__doc__ or "無描述"
        )
        for tool in tools
    ]

    prompt = ChatPromptTemplate.from_template(
        """Answer the following questions as best you can. You have access to the following tools:{tools}

你是一個寵物照護 AI Agent，輸入是 JSON 格式的狗狗狀態資料。
你的目標是根據當前資料與過往觀察記憶，分析狗狗的健康情況並採取必要行動。

你可以使用工具處理異常行為，或根據歷史記憶給出更智慧的建議。
記憶包含：
- 過去對話與總結摘要
- 類似情境下曾經採取的行動

歷史摘要如下： {memory_summary}

請依據以下邏輯思考：
- 觀察輸入資料（狗狗的狀態、等級、時間與地點）
- 結合記憶系統中儲存的對話與事件，判斷是否需要立即處理或記錄
- 必要時使用工具處理當下狀況
- 最後輸出簡單總結與建議

請務必使用以下格式進行推理與決策（否則將導致錯誤）：
Thought: 你在想什麼？
Action: the action to take, should be one of [{tool_names}]
Action Input: 工具的輸入內容（如果有）
Observation: 工具回傳結果
...(this Thought/Action/Action Input/Observation can repeat N times)
Final Answer: 最後要回傳給使用者的建議內容

請**確保輸出結尾是 Final Answer，不要有多餘敘述。**

Begin!
Question: {input}
Thought:{agent_scratchpad}"""
    )

    agent = create_react_agent(llm=llm, tools=langchain_tools, prompt=prompt)
    # 建立 ReAct Agent
    agent_executor = AgentExecutor(agent=agent, tools=langchain_tools, verbose=True, handle_parsing_errors=True)

    return agent_executor
