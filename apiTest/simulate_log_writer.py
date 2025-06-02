# simulate_log_writer.py

import json
import time
from datetime import datetime, timedelta
from pathlib import Path

log_path = "../input/log.json"

# 初始化起始時間
time_cursor = datetime.strptime("20250429120000", "%Y%m%d%H%M%S")

# 確保 log.json 存在
if not Path(log_path).exists():
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

while True:
    # 每次新增一筆 observation
    with open(log_path, "r", encoding="utf-8") as f:
        logs = json.load(f)

    new_entry = {
        "time": time_cursor.strftime("%Y%m%d%H%M%S"),
        "action": "休息",
        "地點": "客廳"
    }
    logs.append(new_entry)

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

    print(f"新增一筆 observation: {new_entry}")

    # 時間往後推5秒
    time_cursor += timedelta(seconds=5)

    time.sleep(0.1)