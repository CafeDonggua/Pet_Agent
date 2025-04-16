from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.agents.agent_types import AgentType
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain.prompts.chat import ChatPromptTemplate, MessagesPlaceholder
from agent.tools import notify_owner, advise_see_doctor, turn_on_ac, feed_pet, analyze_behavior,set_petcare_status

class PetCareAgent:
    def __init__(self, model):
        self.status = "一般"
        self.temp = 28
        self.pet_state = {"時間": "20250326100000", "狀態": "一般", "行為": "坐著"}
        self.behavior_log = []
        self.known_behaviors = {"不進食", "不動", "狂叫"}  # 初始化已知異常行為
        self.abnormal_behaviors = {}
        self.last_feed_time = None
        self.last_review_date = None
        self.log_frequency = {"一般": 5, "觀察": 3, "緊急": 1}
        self.event_queue = []

        self.llm = ChatOpenAI(model=model)

        # 對話 Prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system",
                "你是智慧寵物照護助理，能根據寵物的異常行為呼叫分析工具，並根據建議呼叫其他行動工具。"
                "請依據 analyze_behavior 回傳的 JSON 中的建議模式與 flag 決定下一步行動："
                "緊急 → 通知飼主 + 建議就醫、觀察 → 切換模式並記錄、一般 → 無需動作。"
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
            ("human","{input}"),
        ])
        self.memory = ConversationBufferWindowMemory(k=5, memory_key="chat_history")
        self.tools = [analyze_behavior, set_petcare_status, notify_owner]

        # Agent
        self.agent = create_openai_functions_agent(llm=self.llm, tools=self.tools, prompt=self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, memory=self.memory, verbose=True)


