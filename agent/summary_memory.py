# summary_memory.py
import warnings
#TODO: 以後再處裡 ConversationSummaryBufferMemory版本問題
warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain.memory import ConversationSummaryBufferMemory
from langchain_openai import ChatOpenAI
from agent.singleton_memory import vector_memory_instance
from dotenv import load_dotenv
import os


class SummaryMemory:
    def __init__(self):
        load_dotenv()
        key = os.getenv("OPENAI_CHAT_KEY")
        model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
        self.llm = ChatOpenAI(temperature=0, model=model, api_key=key)
        self.vector_memory = vector_memory_instance  # 初始化向量記憶模組

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
        if not self.memory.chat_memory.messages:
            return ""
        summary = self.memory.load_memory_variables({})["history"]
        messages = self.memory.chat_memory.messages[-2:]
        flat_texts = [msg.content for msg in messages if hasattr(msg, "content")]

        if flat_texts:
            self.vector_memory.add_memory(flat_texts)

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
