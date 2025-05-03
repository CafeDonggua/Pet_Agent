# agent/server.py

import os
import asyncio
from agent.singleton_memory import vector_memory_instance as vm
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from agent.agent_core import PetCareAgent
from agent.memory_manager import memory
from agent.singleton_plan import plan_manager_instance as plan_manager
from agent.utils import load_input_json, store_agent_response
from datetime import datetime, timedelta
from agent.tools import check_daily_plan_conflict, add_plan_item
from langchain_openai import ChatOpenAI
from concurrent.futures import ThreadPoolExecutor

app = FastAPI()

# 初始化 Agent
agent = PetCareAgent()

# WebSocket 連線列表
active_connections = []

executor = ThreadPoolExecutor()


# 讀取 Log 用的紀錄
last_processed_index = 0
LOG_FILE_PATH = "../input/log.json"
INPUT_DIR = "../input"
OUTPUT_DIR = "../output"
latest_sim_time = datetime.strptime("20250429120000", "%Y%m%d%H%M%S")  # 初始模擬時間
# 確保 input/output 目錄存在
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def periodic_log_monitor():
    global latest_sim_time
    while True:
        try:
            log_data = load_input_json("../input/log.json")
            if not log_data:
                await asyncio.sleep(300)
                continue

            next_sim_time = latest_sim_time + timedelta(minutes=5)
            five_min_ago = latest_sim_time.strftime("%Y%m%d%H%M%S")
            current_time = next_sim_time.strftime("%Y%m%d%H%M%S")
            window_logs = [log for log in log_data if five_min_ago <= log["time"] <= current_time]

            if window_logs:
                asyncio.create_task(process_window_logs(window_logs, current_time))
            else:
                print("此時段無資料，跳過但仍推進時間")

            #  每次都推進
            latest_sim_time = next_sim_time

        except Exception as e:
            print(f"[Server Error] {str(e)}")

        await asyncio.sleep(30)

async def process_window_logs(logs, current_time):
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(executor, lambda: asyncio.run(agent.run_with_log_window(logs, current_time)))

    store_agent_response(result, f"{OUTPUT_DIR}/output.json")
    await broadcast(result)

# 啟動背景任務：監控 log.json 並推理
@app.on_event("startup")
async def startup_event():
    # 啟動背景任務
    asyncio.create_task(periodic_log_monitor())


async def broadcast(message: dict):
    """
    推播消息給所有連線中的 WebSocket 客戶端
    """
    disconnected = []
    for conn in active_connections:
        try:
            await conn.send_json(message)
        except:
            disconnected.append(conn)
    for conn in disconnected:
        active_connections.remove(conn)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)


# ------------------- Client API 區域 -------------------

@app.get("/daily_plan")
async def get_daily_plan():
    plans = plan_manager.get_daily_plan()
    return JSONResponse(content=plans)


@app.post("/daily_plan")
async def add_daily_plan(item: dict):
    # 直接寫入到 daily_plan
    if not all(k in item for k in ["time", "action"]):
        return JSONResponse(status_code=400, content={"error": "需要 time 和 action 欄位"})
    conflict_result = check_daily_plan_conflict(item)
    if "衝突" in conflict_result or "注意" in conflict_result or "已有相同" in conflict_result:
        return JSONResponse(status_code=400, content={"error": f"新增失敗：{conflict_result}"})

    add_plan_item(item)
    return {"status": "daily plan 新增成功", "item": item}


@app.get("/current_plan")
async def get_current_plan():
    plans = plan_manager.get_current_plan()
    return JSONResponse(content=plans)


@app.post("/current_plan")
async def add_current_plan(item: dict):
    if not all(k in item for k in ["time", "action"]):
        return JSONResponse(status_code=400, content={"error": "需要 time 和 action 欄位"})
    conflict_result = check_daily_plan_conflict(item)
    if "衝突" in conflict_result or "注意" in conflict_result or "已有相同" in conflict_result:
        return JSONResponse(status_code=400, content={"error": f"新增失敗：{conflict_result}"})

    add_plan_item(item)
    return {"status": "current plan 新增成功", "item": item}


@app.get("/pet_state")
async def get_pet_state():
    return {"current_state": memory.get_current_state()}


@app.get("/recent_records")
async def get_recent_records():
    # 回傳最近 10 筆行為紀錄
    events = memory.memory.get("events", [])
    return JSONResponse(content=events[-10:])


@app.get("/excluded_behaviors")
async def get_excluded_behaviors():
    return JSONResponse(content=memory.memory.get("excluded_behaviors", []))


@app.post("/excluded_behaviors")
async def add_excluded_behaviors(item: dict):
    behavior = item.get("behavior")
    if not behavior:
        return JSONResponse(status_code=400, content={"error": "缺少 'behavior' 欄位"})

    if behavior not in memory.memory["excluded_behaviors"]:
        memory.memory["excluded_behaviors"].append(behavior)
        memory.save_memory()
        return {"status": f"已加入排除行為：{behavior}"}
    else:
        return {"status": f"行為「{behavior}」已經在排除清單中"}


@app.get("/abnormal_behaviors")
async def get_abnormal_behaviors():
    excluded = memory.memory.get("abnormal_behaviors", [])
    return JSONResponse(content=excluded)


@app.delete("/excluded_behaviors")
async def delete_excluded_behaviors(item: dict):
    behavior = item.get("behavior")
    if not behavior:
        return JSONResponse(status_code=400, content={"error": "缺少 'behavior' 欄位"})

    if behavior in memory.memory["excluded_behaviors"]:
        memory.memory["excluded_behaviors"].remove(behavior)
        memory.save_memory()
        return {"status": f"已從排除清單中移除：{behavior}"}

    else:
        return JSONResponse(status_code=404, content={"error": f"行為「{behavior}」不存在於排除清單中"})


@app.delete("/current_plan")
async def delete_current_plan(item: dict):
    time_str = item.get("time")
    action = item.get("action")

    if not time_str or not action:
        return JSONResponse(status_code=400, content={"error": "需要 time 和 action 欄位"})

    original_plan = plan_manager.plan["current_plan"]
    new_plan = [p for p in original_plan if not (p["time"] == time_str and p["action"] == action)]

    if len(original_plan) == len(new_plan):
        return JSONResponse(status_code=404, content={"error": "找不到指定的計畫項目"})

    plan_manager.plan["current_plan"] = new_plan
    plan_manager.save()

    return {"status": f"已刪除 time={time_str}, action={action} 的計畫"}


# ------------------- 向量記憶庫 API -------------------

@app.get("/vector_memory/all")
async def list_vector_memory():
    docs = vm.vector_store.docstore._dict.values()
    contents = [doc.page_content for doc in docs]
    return {"count": len(contents), "data": contents}


@app.post("/vector_memory")
async def add_vector_memory(item: dict):
    text = item.get("text")
    if not text:
        return JSONResponse(status_code=400, content={"error": "缺少 'text' 欄位"})

    vm.add_memory([text])
    return {"status": "已加入向量記憶庫", "text": text}


@app.delete("/vector_memory")
async def delete_vector_memory(item: dict):
    text = item.get("text")
    if not text:
        return JSONResponse(status_code=400, content={"error": "缺少 'text' 欄位"})

    docstore = vm.vector_store.docstore._dict

    to_delete = [k for k, doc in docstore.items() if doc.page_content == text]

    if not to_delete:
        return JSONResponse(status_code=404, content={"error": "找不到完全符合的記憶"})

    for key in to_delete:
        del docstore[key]

    # 移除對應的 index entry
    new_docs = list(docstore.values())
    new_texts = [doc.page_content for doc in new_docs]

    # 重新建立 vector store（簡單暴力但正確）
    vm.initialize_vector_store()
    vm.add_memory(new_texts)

    return {"status": f"已刪除 {len(to_delete)} 筆記憶", "text": text}

import re

def extract_clean_text(raw: str) -> str:
    # 清除 "content='...'" 的 wrapper
    match = re.search(r"content='(.*?)'", raw)
    if match:
        return match.group(1)
    return raw.strip().split(" additional_kwargs")[0]  # 最保險

@app.post("/ask_agent")
async def ask_agent(item: dict):
    text = item.get("text")
    if not text:
        return JSONResponse(status_code=400, content={"error": "缺少 'text'"})

    # 1. 查詢 FAISS 記憶
    results = vm.query_memory(text, top_k=5)
    context = "\n".join([f"- {extract_clean_text(r['text'])}" for r in results]) or "（目前無可參考的記憶）"

    #context = "\n".join([f"- {r['text']}" for r in results]) or "（目前無可參考的記憶）"
    # 2. 組 prompt 給模型
    prompt = f"""你是一個了解狗狗行為的助理。根據以下記憶片段，回答問題：
記憶內容：
{context}

問題：{text}
請根據上面資訊，用中文回答。"""

    # 3. 呼叫 GPT 模型
    chat = ChatOpenAI(model="gpt-4o-mini", temperature=0.5, api_key=os.getenv("OPENAI_CHAT_KEY"))
    answer = chat.invoke(prompt).content

    # 格式化結果
    formatted = f"Agent: {answer}\n\n參考記憶：\n{context}"

    return {"answer": formatted}


# ------------------- End -------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
