# agent/agent_init.py

import os
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
from agent.tools import get_toolkit


def init_agent():
    """
    初始化新的 GOAP 思考流程 LLM Agent（內部自己抓工具）
    """
    load_dotenv(Path("..\\.env"))
    load_dotenv(find_dotenv())
    chat_key = os.getenv("OPENAI_CHAT_KEY")
    chat_model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

    llm = ChatOpenAI(
        model=chat_model,
        temperature=0,
        api_key=chat_key
    )

    # 自己抓工具，不需要外部傳入
    tools = get_toolkit()

    langchain_tools = [
        Tool(
            name=tool.__name__,
            func=tool,
            description=tool.__doc__ or "無描述"
        )
        for tool in tools
    ]


    prompt = ChatPromptTemplate.from_template(
        """你是一個寵物照護 AI Agent。
你的任務是根據當前觀察（Observation）、已知可使用的工具（Tools），自主規劃狗狗今日的照護行動計畫。

請依循以下 GOAP 思考流程：
1. 感知 (Observation)：
    - 理解目前狗狗的行為、地點、時間資訊。
    - 注意：每次行動後，除非有新的 Observation，否則環境狀態不會改變。
2. 目標決策 (Goal Selection)：
    - 根據 Observation 判斷是否需要新增 Current Plan。
   - 如需新增，請使用工具 `check_daily_plan_conflict` 確認是否與主計畫衝突。
3. 規劃 (Planning)：安排合理順序的行動步驟。
   - 合理規劃行動順序。
   - 每個行動如果需要使用工具，則要選擇一個合適的工具（Tools）, should be one of [{tool_names}]
4. 執行 (Act)：
   - 依序執行行動。
   - 每次 Action 後假設 Observation 暫時未更新，請自行判斷是否需要繼續行動。
5. 觀察與調整 (Observe & Adjust)：每步驟後重新觀察環境，必要時調整計畫。
   - 不得重複使用 wait_and_observe 超過一次，若無變化請立即輸出 Final Answer。
   - 不得重複使用 get_today_plan 超過一次，若無變化請立即輸出 Final Answer。
   - 不得無限重複工具呼叫
   - Final Answer 一出，代表本次照護流程結束。

---
可使用的工具名稱（Tools）如下：
{tool_names}
可使用的工具描述（詳細功能）如下：
{tools}
當前觀察 (Observation)：
{input}
---
輸出格式要求（必須遵循）
請遵循 Thought → Action → Observation → Final Answer 的格式輸出。

範例：
Thought: 分析當前情境與需要的行動
Action: [選擇一個工具名稱]
Action Input: [填入行動的輸入內容，如無則寫「無」]
Observation: 描述行動後的結果（假設環境無更新時，請合理推測）
Thought: 分析行動後的結果的情境與是否有需要的行動（如果無需新的行動，或所有必要行動已完成，請輸出：）
Final Answer: 本次照護流程完成。
---
注意事項：
- 不要持續重複同一個行動（例如 'check_temp', 'notify_owner', 'get_today_plan', 'add_plan_item' 等）若重複執行則視為違反規則，立即輸出 Final Answer，結束本次流程。
- 查詢型工具（如 'get_today_plan', 'check_temp' 等）使用後，請立即判斷是否需要進一步行動，不用則立即輸出 Final Answer，結束本次流程。
- 若無新的明確行動，請立即輸出 Final Answer，結束本次流程。
- 如確定無需再執行新的行動，請儘速輸出 Final Answer。
- 若遇到無法處理的情境，也應輸出 Final Answer。
- 請勿創造不存在的工具。
---

請務必遵循以上步驟，開始！
Thought:{agent_scratchpad}
"""
    )

    agent = create_react_agent(llm=llm, tools=langchain_tools, prompt=prompt)
    # 建立 ReAct Agent
    agent_executor = AgentExecutor(agent=agent, tools=langchain_tools, verbose=True, handle_parsing_errors=True)

    return agent_executor

