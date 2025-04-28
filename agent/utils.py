# utils.py

import json
from typing import Dict
from pathlib import Path


def load_input_json(path: str) -> Dict:
    """
    從指定路徑讀取 JSON 格式的輸入資料。

    Args:
      path (str): 檔案路徑。

    Returns:
      Dict: 解析後的 JSON 資料。
    """
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_latest_data(input_data: list, last_processed_time: str):
    """從資料列表中篩選出新的資料"""
    # 按照時間過濾出新資料
    new_data = [entry for entry in input_data if entry["time"] > last_processed_time]
    new_data.sort(key=lambda x: x["time"])
    return new_data

def store_agent_response(response: Dict, output_path: str) -> None:
    """
    將 Agent 的回應儲存為 JSON 檔。

    Args:
      response (Dict): Agent 回傳的字典資料。
      output_path (str): 儲存檔案的路徑。
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(response, f, ensure_ascii=False, indent=2)
