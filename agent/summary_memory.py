from langchain.memory import ConversationSummaryBufferMemory
from langchain.chat_models import ChatOpenAI
from agent.vector_memory import VectorMemory
from dotenv import load_dotenv
import os

class SummaryMemory:
    def __init__(self):
        load_dotenv()
        self.llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo", openai_api_key=os.getenv("OPENAI_API_KEY"))
        self.memory = ConversationSummaryBufferMemory(llm=self.llm, max_token_limit=500)
        self.vector_memory = VectorMemory()  # 初始化向量記憶模組

        self.memory = ConversationSummaryBufferMemory(
            llm=self.llm,
            max_token_limit=1000,
            return_messages=True
        )

    def add_user_message(self, message: str):
        """
        添加使用者訊息到記憶。
        Args:
            message (str): 使用者發送的訊息
        """
        self.memory.chat_memory.add_user_message(message)

    def add_ai_message(self, message: str):
        """
        添加 AI 回應訊息到記憶。
        Args:
            message (str): AI 發送的回應訊息
        """
        self.memory.chat_memory.add_ai_message(message)

    def get_summary(self) -> str:
        """
        取得摘要並儲存到向量記憶。
        Returns:
            str: 當前對話的摘要內容
        """
        summary = self.memory.load_memory_variables({})["history"]
        if summary:
            # 儲存摘要到向量記憶
            self.vector_memory.add_memory([summary])
        return summary

    def query_summaries(self, query: str, top_k: int = 5):
        """
        查詢與對話摘要相關的記憶。
        Args:
            query (str): 查詢的文本
            top_k (int): 返回的最相似摘要數量
        Returns:
            List[Dict]: 返回最相似摘要的列表
        """
        return self.vector_memory.query_memory(query, top_k=top_k)

# ===== 封裝成 Tool 用的函式 =====

def search_summary_memory(query: str) -> str:
    """
    根據查詢關鍵字，從摘要記憶中找出最相關的內容。
    Args:
        query (str): 查詢的問題或關鍵字
    Returns:
        str: 匹配的摘要資訊（文字格式）
    """
    summary_memory = SummaryMemory()
    results = summary_memory.query_summaries(query)
    if not results:
        return "找不到相關摘要記憶。"

    output = "\n".join([f"[距離: {r['distance']:.4f}] {r['text']}" for r in results])
    return output