# vector_memory.py
import faiss
import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from dotenv import load_dotenv
from typing import List, Dict

# 載入環境變數
load_dotenv()


class VectorMemory:
    def __init__(self, vector_store_path: str = "../memory/vector_store"):
        """
        初始化向量記憶系統。
        Args:
            vector_store_path (str): FAISS 向量資料庫的存儲路徑
        """

        embedding_key = os.getenv("OPENAI_EMBEDDING_KEY")
        embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        self.embeddings = OpenAIEmbeddings(model=embedding_model, api_key=embedding_key)

        # 嘗試載入現有的 FAISS 資料庫
        self.vector_store_path = vector_store_path
        self.vector_store = None
        allow_dangerous = os.getenv("ALLOW_DANGEROUS_DESERIALIZATION", "False").lower() == "true"
        if os.path.exists(self.vector_store_path):
            # 如果資料庫存在，載入它
            self.vector_store = FAISS.load_local(self.vector_store_path, self.embeddings,
                                                 allow_dangerous_deserialization=allow_dangerous)
        else:
            # 如果沒有資料庫，初始化一個新的 FAISS 資料庫
            self.initialize_vector_store()

    def initialize_vector_store(self):
        """
        初始化一個新的 FAISS 向量資料庫。
        """
        dim = 1536
        index = faiss.IndexFlatL2(dim)  # L2 距離度量
        # 創建一個空的文檔存儲
        docstore = InMemoryDocstore()
        # 創建索引到文檔 ID 的映射
        index_to_docstore_id = {}

        # 使用 LangChain 內部的 FAISS 來創建向量資料庫
        self.vector_store = FAISS(
            embedding_function=self.embeddings,
            index=index,
            docstore=docstore,
            index_to_docstore_id=index_to_docstore_id
        )

    def add_memory(self, texts: List[str]) -> None:
        """
        儲存新的記憶到 FAISS 向量資料庫。
        Args:
            texts (List[str]): 需要儲存的文本資料
        """
        # 避免完全重複的記憶內容加入
        existing_docs = self.vector_store.similarity_search("")
        existing_texts = set(doc.page_content for doc in existing_docs)
        texts = [t for t in texts if t not in existing_texts]

        # 將文本轉換為向量並儲存
        if texts:
            self.vector_store.add_texts(texts)
            self.vector_store.save_local(self.vector_store_path)  # 儲存索引檔案

    def query_memory(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        根據查詢文本來查找最相似的記憶。
        Args:
            query (str): 查詢的文本
            top_k (int): 需要返回的最相似的記憶數量
        Returns:
            List[Dict]: 返回的最相似記憶，格式為字典列表
        """
        # 查詢最相似的文本
        result = self.vector_store.similarity_search_with_score(query, top_k=top_k)

        # 組裝查詢結果
        results = [{"distance": score, "text": doc.page_content} for doc, score in result]
        return results

# ===== 封裝成 Tool 用的函式 =====

vector_memory_instance = VectorMemory()

def search_vector_memory(query: str) -> str:
    """
    查詢向量記憶庫中與輸入最相關的記憶內容。
    Args:
        query (str): 使用者的查詢。
    Returns:
        str: 與查詢最相似的記憶內容（文字形式）。
    """
    results = vector_memory_instance.query_memory(query)
    if not results:
        return "查無相關記憶。"
    return "\n".join([f"相似度: {round(1 - r['distance'], 3)} | 內容: {r['text']}" for r in results])