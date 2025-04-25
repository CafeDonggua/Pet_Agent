# vector_memory.py
import time

import faiss
import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain.schema import Document

from dotenv import load_dotenv
from typing import List, Dict
import traceback

# 載入環境變數
load_dotenv()


class VectorMemory:
    def __init__(self, vector_store_path: str = "./memory/vector_store"):
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
        if os.path.exists(self.vector_store_path) and os.path.isfile(self.vector_store_path):
            # 如果資料庫存在，載入它
            try:
                self.vector_store = FAISS.load_local(self.vector_store_path, self.embeddings,
                                                     allow_dangerous_deserialization=allow_dangerous)
                print("資料庫載入成功")
            except Exception as e:
                print(f"載入資料庫時出錯: {e}")
                # 如果載入失敗，強制初始化
                self.initialize_vector_store()

        else:
            # 如果沒有資料庫，初始化一個新的 FAISS 資料庫
            self.initialize_vector_store()
            # 在此時進行儲存
            self.save()

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
        self.save()
        print(f"[確認] 資料夾 {self.vector_store_path} 目前內容：")
        for f in os.listdir(self.vector_store_path):
            print(" -", f)

        time.sleep(1)  # 保險起見給它一點緩衝

    def add_memory(self, texts: List[str]) -> None:
        """
        儲存新的記憶到 FAISS 向量資料庫。
        Args:
            texts (List[str]): 需要儲存的文本資料
        """
        print("[Debug] 儲存路徑絕對位置：", os.path.abspath(self.vector_store_path))
        print("[AddMemory] 接收到文本：", texts)

        if self.vector_store.index.ntotal == 0:

            existing_texts = set()
            print("[AddMemory] 向量索引為空，無既有內容")
        else:
            # 避免完全重複的記憶內容加入
            existing_docs = self.vector_store.similarity_search("", k=100)
            existing_texts = set(doc.page_content for doc in existing_docs)
            print(f"[AddMemory] 現有記憶數量：{len(existing_texts)}")

        new_texts = [t for t in texts if t not in existing_texts]

        # 將文本轉換為向量並儲存
        if new_texts:
            print(f"[AddMemory] 準備加入 {len(new_texts)} 則新記憶")
            # 包裝成 Document 格式（才能正確儲存到 docstore）
            documents = [Document(page_content=t) for t in new_texts]

            self.vector_store.add_documents(documents)
            self.vector_store.save_local(self.vector_store_path)  # 儲存索引檔案
            # 儲存資料庫
            self.save()
            print(f"[AddMemory] 已儲存 {len(documents)} 則記憶到向量資料庫")
        else:
            print("[AddMemory] 無新文本需儲存，略過。")

        print(f"[確認] 資料夾 {self.vector_store_path} 目前內容：")
        for f in os.listdir(self.vector_store_path):
            print(" -", f)

        self.vector_store.add_texts(new_texts)
        self.vector_store.save_local(self.vector_store_path)

        print(f"[AddMemory] 儲存後 index 數量：{self.vector_store.index.ntotal}")
        print(f"[AddMemory] 資料應儲存在：{os.path.abspath(self.vector_store_path)}")
        print(f"[AddMemory] 資料夾內容：{os.listdir(self.vector_store_path)}")

        time.sleep(1)  # 保險起見給它一點緩衝

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

    def save(self):
        """
        保存資料庫
        """
        if self.vector_store:
            self.vector_store.save_local(self.vector_store_path)
            print("資料庫已儲存")
        else:
            print("未初始化資料庫")


if __name__ == "__main__":
    # 初始化 VectorMemory 實例
    vector_memory = VectorMemory()
    # 儲存記憶
    texts_to_store = ["狗狗看起來有點疲倦", "狗狗正在快速跑步"]
    vector_memory.add_memory(texts_to_store)
    query_result = vector_memory.query_memory("狗狗跑步", top_k=2)
    print(query_result)
