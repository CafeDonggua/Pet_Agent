# agent/server.py
import os
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.responses import JSONResponse
from agent.agent_core import PetCareAgent
from agent.memory_manager import memory
from agent.plan_manager import PlanManager
from agent.singleton_plan import plan_manager_instance as plan_manager
from agent.utils import load_input_json, store_agent_response
from datetime import datetime
from pathlib import Path
from agent.tools import check_daily_plan_conflict, add_plan_item

app = FastAPI()

# 初始化 Agent
agent = PetCareAgent()

# WebSocket 連線列表
active_connections = []

# 讀取 Log 用的紀錄
last_processed_index = 0
LOG_FILE_PATH = "../input/log.json"
INPUT_DIR = "../input"
OUTPUT_DIR = "../output"

# 確保 input/output 目錄存在
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


async def monitor_log_file():
    """
    背景任務：每5秒掃描一次 sample.json，偵測新的一筆 observation
    """
    global last_processed_index
    while True:
        await asyncio.sleep(5)
        if not os.path.exists(LOG_FILE_PATH):
            continue

        try:
            logs = load_input_json(LOG_FILE_PATH)
            if last_processed_index < len(logs):
                # 處理新的 observation
                new_observation = logs[last_processed_index]
                last_processed_index += 1

                # 執行推理
                result = await asyncio.to_thread(agent.run, new_observation)
                print(result)
                # 儲存 output
                store_agent_response(result, f"{OUTPUT_DIR}/output.json")

                # 推播給所有 WebSocket
                await broadcast(result)

        except Exception as e:
            print("[Log Monitor Error]", e)


@app.on_event("startup")
async def startup_event():
    # 啟動背景任務
    asyncio.create_task(monitor_log_file())


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
    if "衝突" in conflict_result or "注意" in conflict_result:
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
    if "衝突" in conflict_result or "注意" in conflict_result:
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

# ------------------- End -------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
